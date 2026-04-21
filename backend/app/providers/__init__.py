"""AIVideoProvider 抽象レイヤー。

03_機能仕様書 §9.1 の仕様に準拠。
- ComfyUI（主軸・Level 1/2/3）
- Viggle（副・Level 2/3）
- Runway Act One（副・Level 2/3）
- Kling AI（Dark Launch・Level 3 かつ feature_flag ON 時のみ）
"""
from .base import (
    AIVideoProvider,
    GenerateParams,
    GenerateResult,
    PollResult,
    ProviderError,
    ProviderUnavailable,
)
from .registry import ProviderRegistry, get_registry

__all__ = [
    "AIVideoProvider",
    "GenerateParams",
    "GenerateResult",
    "PollResult",
    "ProviderError",
    "ProviderUnavailable",
    "ProviderRegistry",
    "get_registry",
]
