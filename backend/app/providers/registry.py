"""プロバイダー登録・フォールバック順序を管理するレジストリ。"""
from __future__ import annotations

from functools import lru_cache

from ..core.config import get_settings
from ..models.schemas import ConsentLevel
from .base import AIVideoProvider
from .comfyui import ComfyUIProvider
from .kling import KlingProvider
from .runway import RunwayActOneProvider
from .viggle import ViggleProvider

# 既定のフォールバック優先順位（03_機能仕様書 §13.10）
DEFAULT_PRIORITY = ["comfyui", "viggle", "runway_act_one", "kling"]


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, AIVideoProvider] = {
            p.name: p
            for p in (
                ComfyUIProvider(),
                ViggleProvider(),
                RunwayActOneProvider(),
                KlingProvider(),
            )
        }

    def get(self, name: str) -> AIVideoProvider:
        return self._providers[name]

    def all(self) -> dict[str, AIVideoProvider]:
        return dict(self._providers)

    def eligible_for_level(self, level: ConsentLevel) -> list[AIVideoProvider]:
        """同意レベルで許容されるプロバイダーを優先順位で返す。"""
        eligible: list[AIVideoProvider] = []
        for name in DEFAULT_PRIORITY:
            p = self._providers.get(name)
            if p and p.supports_consent_level(level):
                eligible.append(p)
        return eligible

    def status(self) -> dict[str, str]:
        """health エンドポイント用の簡易状態表示。"""
        settings = get_settings()
        return {
            "comfyui": "stub" if "localhost" in settings.comfyui_endpoint else "live",
            "viggle": "stub" if not settings.viggle_api_key else "live",
            "runway_act_one": "stub" if not settings.runway_api_key else "live",
            "kling": "disabled" if not settings.kling_enabled else "live",
        }


@lru_cache
def get_registry() -> ProviderRegistry:
    return ProviderRegistry()
