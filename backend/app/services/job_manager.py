"""生成ジョブのインメモリ管理（Phase 0 PoC）。

本実装では Redis / Postgres に差し替える。Over-generation・Quality-gate・プロバイダー
フォールバック（R1→R2）を束ねる薄いオーケストレーター。
"""
from __future__ import annotations

import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from ..core.circuit_breaker import registry as cb_registry
from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.schemas import (
    ConsentLevel,
    GenerationAttempt,
    JobCreateRequest,
    JobResponse,
    JobStatus,
    RetentionMode,
    Scene,
)
from ..providers import get_registry
from ..providers.base import GenerateParams, JobPhase, ProviderError, ProviderUnavailable
from .over_generation import plan_overgen_indices

logger = get_logger(__name__)


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    async def submit(self, req: JobCreateRequest) -> JobResponse:
        settings = get_settings()
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        session_id = req.session_id or f"sess-{uuid.uuid4().hex[:10]}"

        providers = get_registry().eligible_for_level(req.consent_level)
        if not providers:
            raise RuntimeError(
                f"No eligible providers for consent_level={req.consent_level}"
            )

        overgen_indices = plan_overgen_indices(settings.displayed_patterns)
        attempts: list[GenerationAttempt] = []

        # PoC では逐次実行。本実装は asyncio.gather 並列＋ Redis キュー。
        for idx in overgen_indices:
            primary = providers[0]
            attempt = await self._try_providers(
                providers=providers,
                params=GenerateParams(
                    base_video_path=f"/assets/base/{req.scene.value}.mp4",
                    subjects=req.subjects,
                    motion_ref_path=f"/assets/motion/{req.scene.value}_default.mp4",
                    scene=req.scene.value,
                    consent_level=req.consent_level,
                    overgen_index=idx,
                ),
            )
            attempts.append(attempt)

        status = (
            JobStatus.SUCCEEDED
            if any(a.status == JobStatus.SUCCEEDED for a in attempts)
            else JobStatus.FAILED
        )

        job = {
            "job_id": job_id,
            "session_id": session_id,
            "property_id": req.property_id,
            "scene": req.scene,
            "consent_level": req.consent_level,
            "retention_mode": req.retention_mode,
            "status": status,
            "attempts": attempts,
            "displayed_video_ids": [
                a.attempt_id
                for a in attempts
                if a.status == JobStatus.SUCCEEDED
            ][: settings.displayed_patterns],
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        self._jobs[job_id] = job
        return self._to_response(job)

    async def _try_providers(
        self,
        *,
        providers: list,
        params: GenerateParams,
    ) -> GenerationAttempt:
        """R1 リトライ1回 → R2 プロバイダー切替、の単層ラッパー。"""
        last_error: str | None = None
        started = self._now()
        for provider in providers:
            if not cb_registry.allow(provider.name):
                last_error = f"{provider.name}:circuit_open"
                continue
            try:
                res = await provider.generate(params)
                # PoC スタブ: ポーリング短縮
                phase = JobPhase.RUNNING
                for _ in range(60):
                    status = await provider.poll(res.job_id)
                    phase = status.phase
                    if phase in (JobPhase.SUCCEEDED, JobPhase.FAILED):
                        break
                    await asyncio.sleep(0.2)
                cb_registry.record(provider.name, success=(phase == JobPhase.SUCCEEDED))
                if phase == JobPhase.SUCCEEDED:
                    return GenerationAttempt(
                        attempt_id=res.job_id,
                        provider=provider.name,
                        status=JobStatus.SUCCEEDED,
                        overgen_index=params.overgen_index,
                        started_at=started,
                        finished_at=self._now(),
                    )
                last_error = f"{provider.name}:{status.message or 'failed'}"
            except ProviderUnavailable as e:
                last_error = f"{provider.name}:unavailable:{e}"
                cb_registry.record(provider.name, success=False)
            except ProviderError as e:
                last_error = f"{provider.name}:error:{e}"
                cb_registry.record(provider.name, success=False)

        return GenerationAttempt(
            attempt_id=f"failed-{uuid.uuid4().hex[:8]}",
            provider="none",
            status=JobStatus.FAILED,
            overgen_index=params.overgen_index,
            failure_reason=last_error,
            started_at=started,
            finished_at=self._now(),
        )

    def get(self, job_id: str) -> JobResponse | None:
        job = self._jobs.get(job_id)
        return self._to_response(job) if job else None

    def _to_response(self, job: dict[str, Any]) -> JobResponse:
        return JobResponse(
            job_id=job["job_id"],
            session_id=job["session_id"],
            scene=job["scene"] if isinstance(job["scene"], Scene) else Scene(job["scene"]),
            consent_level=job["consent_level"]
            if isinstance(job["consent_level"], ConsentLevel)
            else ConsentLevel(job["consent_level"]),
            retention_mode=job["retention_mode"]
            if isinstance(job["retention_mode"], RetentionMode)
            else RetentionMode(job["retention_mode"]),
            status=job["status"],
            attempts=job["attempts"],
            displayed_video_ids=job["displayed_video_ids"],
            created_at=job["created_at"],
            updated_at=job["updated_at"],
        )


_manager: JobManager | None = None


def get_manager() -> JobManager:
    global _manager
    if _manager is None:
        _manager = JobManager()
    return _manager
