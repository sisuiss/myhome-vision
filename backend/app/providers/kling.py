"""Kling AI プロバイダー（Dark Launch・Level 3 のみ）。

feature_flag `KLING_ENABLED=false` が既定。本採用時に true に切替。
"""
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
    ProviderUnavailable,
)


class KlingProvider(AIVideoProvider):
    name = "kling"

    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint = settings.kling_endpoint
        self._api_key = settings.kling_api_key
        self._enabled = settings.kling_enabled

    def supports_consent_level(self, level: ConsentLevel) -> bool:
        if not self._enabled:
            return False
        return level == ConsentLevel.L3_ALL

    async def generate(self, params: GenerateParams) -> GenerateResult:
        if not self._enabled:
            raise ProviderUnavailable("Kling AI is disabled (Dark Launch flag OFF)")
        return GenerateResult(
            job_id=f"kl-{uuid.uuid4().hex[:12]}",
            provider=self.name,
            overgen_index=params.overgen_index,
            submitted_at=time.time(),
        )

    async def poll(self, job_id: str) -> PollResult:
        if not self._enabled:
            raise ProviderUnavailable("Kling AI is disabled (Dark Launch flag OFF)")
        return PollResult(job_id=job_id, phase=JobPhase.SUCCEEDED, progress=1.0)

    async def fetch(self, job_id: str) -> FetchResult:
        if not self._enabled:
            raise ProviderUnavailable("Kling AI is disabled (Dark Launch flag OFF)")
        return FetchResult(job_id=job_id, video_bytes=b"", duration_sec=10.0)

    async def cancel(self, job_id: str) -> bool:
        return True
