"""AIVideoProvider 抽象インタフェース。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..models.schemas import ConsentLevel, Subject


class ProviderError(RuntimeError):
    """プロバイダー側の失敗を表す例外。"""


class ProviderUnavailable(ProviderError):
    """Circuit Breaker OPEN / フラグOFF 等で呼び出せない状態。"""


class JobPhase(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class GenerateParams:
    """AIVideoProvider.generate() の入力。"""

    base_video_path: str
    subjects: list[Subject]
    motion_ref_path: str
    scene: str
    consent_level: ConsentLevel
    overgen_index: int = 0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerateResult:
    job_id: str
    provider: str
    overgen_index: int
    submitted_at: float  # epoch seconds


@dataclass
class PollResult:
    job_id: str
    phase: JobPhase
    progress: float = 0.0  # 0.0 - 1.0
    quality_score: float | None = None
    message: str | None = None


@dataclass
class FetchResult:
    job_id: str
    video_bytes: bytes
    content_type: str = "video/mp4"
    duration_sec: float | None = None


class AIVideoProvider(ABC):
    """抽象プロバイダー。実装者はすべて実装する。"""

    name: str = "abstract"

    @abstractmethod
    def supports_consent_level(self, level: ConsentLevel) -> bool:
        """同意レベルがこのプロバイダーを許容しているか。"""

    @abstractmethod
    async def generate(self, params: GenerateParams) -> GenerateResult:
        """生成ジョブを投入する。"""

    @abstractmethod
    async def poll(self, job_id: str) -> PollResult:
        """進捗を取得する。"""

    @abstractmethod
    async def fetch(self, job_id: str) -> FetchResult:
        """完成した動画を取得する。"""

    @abstractmethod
    async def cancel(self, job_id: str) -> bool:
        """ジョブをキャンセルする。"""
