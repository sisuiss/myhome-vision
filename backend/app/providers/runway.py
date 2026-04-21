"""Runway Act One プロバイダー（米国・Level 2/3）。Phase 0 スタブ実装。"""
from __future__ import annotations

import time
import uuid

from ..core.config import get_settings
from ..models.schemas import ConsentLevel
from .base import (
    AIVideoProvider,
    FetchResult,
    GenerateParams,
    GenerateResult,
    JobPhase,
    PollResult,
)


class RunwayActOneProvider(AIVideoProvider):
    name = "runway_act_one"

    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint = settings.runway_endpoint
        self._api_key = settings.runway_api_key

    def supports_consent_level(self, level: ConsentLevel) -> bool:
        return level in (ConsentLevel.L2_US, ConsentLevel.L3_ALL)

    async def generate(self, params: GenerateParams) -> GenerateResult:
        return GenerateResult(
            job_id=f"rw-{uuid.uuid4().hex[:12]}",
            provider=self.name,
            overgen_index=params.overgen_index,
            submitted_at=time.time(),
        )

    async def poll(self, job_id: str) -> PollResult:
        return PollResult(job_id=job_id, phase=JobPhase.SUCCEEDED, progress=1.0)

    async def fetch(self, job_id: str) -> FetchResult:
        return FetchResult(job_id=job_id, video_bytes=b"", duration_sec=10.0)

    async def cancel(self, job_id: str) -> bool:
        return True
