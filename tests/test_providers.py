"""プロバイダー抽象・Level 適合性のユニットテスト。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

# Kling を OFF のままテストするため環境変数を上書き
os.environ.setdefault("KLING_ENABLED", "false")

from app.models.schemas import ConsentLevel  # noqa: E402
from app.providers import get_registry  # noqa: E402


def test_comfyui_supports_all_levels() -> None:
    comfy = get_registry().get("comfyui")
    assert comfy.supports_consent_level(ConsentLevel.L1_DOMESTIC)
    assert comfy.supports_consent_level(ConsentLevel.L2_US)
    assert comfy.supports_consent_level(ConsentLevel.L3_ALL)


def test_viggle_blocks_level1() -> None:
    viggle = get_registry().get("viggle")
    assert not viggle.supports_consent_level(ConsentLevel.L1_DOMESTIC)
    assert viggle.supports_consent_level(ConsentLevel.L2_US)
    assert viggle.supports_consent_level(ConsentLevel.L3_ALL)


def test_kling_disabled_by_flag() -> None:
    kling = get_registry().get("kling")
    assert not kling.supports_consent_level(ConsentLevel.L1_DOMESTIC)
    assert not kling.supports_consent_level(ConsentLevel.L2_US)
    # Level 3 でも flag OFF なので不可
    assert not kling.supports_consent_level(ConsentLevel.L3_ALL)


def test_priority_order_for_level1() -> None:
    eligible = get_registry().eligible_for_level(ConsentLevel.L1_DOMESTIC)
    names = [p.name for p in eligible]
    # Level 1 は ComfyUI のみ
    assert names == ["comfyui"]


def test_priority_order_for_level2() -> None:
    eligible = get_registry().eligible_for_level(ConsentLevel.L2_US)
    names = [p.name for p in eligible]
    assert names == ["comfyui", "viggle", "runway_act_one"]
