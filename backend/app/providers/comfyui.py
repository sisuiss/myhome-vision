"""ComfyUI 主軸プロバイダー（Level 1/2/3 対応）。

Phase 0 では HTTP スタブ実装。
- POST  {endpoint}/prompt           → ワークフロー投入
- GET   {endpoint}/history/{prompt} → 進捗・結果
- GET   {endpoint}/view             → 生成物ダウンロード

実接続は Runpod Serverless / SaladCloud / RunComfy / 自社GPU のいずれかに
切替可能。本クラスは ComfyUI API 互換のエンドポイントを前提とする。
"""
from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

import httpx

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.schemas import ConsentLevel
from .base import (
    AIVideoProvider,
    FetchResult,
    GenerateParams,
    GenerateResult,
    JobPhase,
    PollResult,
    ProviderError,
)

logger = get_logger(__name__)


class ComfyUIProvider(AIVideoProvider):
    name = "comfyui"

    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint = settings.comfyui_endpoint.rstrip("/")
        self._api_key = settings.comfyui_api_key
        # Phase 0 PoC: インメモリでジョブ状態を管理（本実装では Redis/DB に移行）
        self._jobs: dict[str, dict[str, Any]] = {}

    def supports_consent_level(self, level: ConsentLevel) -> bool:
        # 国内完結（自社GPU or 国内リージョンの管理GPU）想定のため全レベル可
        return True

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    def _build_workflow(self, params: GenerateParams) -> dict[str, Any]:
        """パラメトリック ComfyUI ワークフローを構築する。

        本実装では comfyui/workflows/*.json をロードしてパラメータ置換する想定。
        PoC 段階ではモック。
        """
        return {
            "scene": params.scene,
            "subjects": [s.model_dump() for s in params.subjects],
            "base_video": params.base_video_path,
            "motion_ref": params.motion_ref_path,
            "overgen_index": params.overgen_index,
            "extra": params.extra,
        }

    async def generate(self, params: GenerateParams) -> GenerateResult:
        workflow = self._build_workflow(params)
        job_id = f"cf-{uuid.uuid4().hex[:12]}"

        # PoC スタブ: 実接続がない場合はモックで 3〜8 秒後に完了扱い
        try:
            if self._is_stubbed():
                self._jobs[job_id] = {
                    "phase": JobPhase.QUEUED,
                    "started_at": time.time(),
                    "workflow": workflow,
                }
                return GenerateResult(
                    job_id=job_id,
                    provider=self.name,
                    overgen_index=params.overgen_index,
                    submitted_at=time.time(),
                )

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self._endpoint}/prompt",
                    headers=self._headers(),
                    json={"prompt": workflow, "client_id": job_id},
                )
                resp.raise_for_status()
            self._jobs[job_id] = {
                "phase": JobPhase.RUNNING,
                "started_at": time.time(),
            }
            return GenerateResult(
                job_id=job_id,
                provider=self.name,
                overgen_index=params.overgen_index,
                submitted_at=time.time(),
            )
        except httpx.HTTPError as e:
            logger.warning("comfyui.generate.error", error=str(e), job_id=job_id)
            raise ProviderError(f"ComfyUI generate failed: {e}") from e

    def _is_stubbed(self) -> bool:
        """endpoint が localhost のまま or api_key 空なら Phase 0 スタブとして動作。"""
        return "localhost" in self._endpoint or "127.0.0.1" in self._endpoint

    async def poll(self, job_id: str) -> PollResult:
        job = self._jobs.get(job_id)
        if not job:
            return PollResult(job_id=job_id, phase=JobPhase.FAILED, message="unknown job")

        if self._is_stubbed():
            elapsed = time.time() - job["started_at"]
            if elapsed < 3:
                return PollResult(job_id=job_id, phase=JobPhase.RUNNING, progress=elapsed / 8.0)
            if elapsed < 8:
                return PollResult(job_id=job_id, phase=JobPhase.RUNNING, progress=elapsed / 8.0)
            job["phase"] = JobPhase.SUCCEEDED
            return PollResult(job_id=job_id, phase=JobPhase.SUCCEEDED, progress=1.0)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self._endpoint}/history/{job_id}", headers=self._headers()
                )
                resp.raise_for_status()
                data = resp.json()
            # ComfyUI の API レスポンスに応じて解釈（PoC ではダミー）
            phase = JobPhase.SUCCEEDED if data else JobPhase.RUNNING
            return PollResult(job_id=job_id, phase=phase)
        except httpx.HTTPError as e:
            logger.warning("comfyui.poll.error", error=str(e), job_id=job_id)
            return PollResult(job_id=job_id, phase=JobPhase.FAILED, message=str(e))

    async def fetch(self, job_id: str) -> FetchResult:
        # PoC スタブ: 空の mp4 を返す
        if self._is_stubbed():
            await asyncio.sleep(0.01)
            return FetchResult(job_id=job_id, video_bytes=b"", duration_sec=10.0)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(
                    f"{self._endpoint}/view",
                    params={"filename": f"{job_id}.mp4"},
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return FetchResult(job_id=job_id, video_bytes=resp.content)
        except httpx.HTTPError as e:
            raise ProviderError(f"ComfyUI fetch failed: {e}") from e

    async def cancel(self, job_id: str) -> bool:
        job = self._jobs.pop(job_id, None)
        return job is not None
