"""Over-generation 計算のユニットテスト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.over_generation import calculate_total_attempts, plan_overgen_indices  # noqa: E402


def test_calculate_total_attempts_default() -> None:
    assert calculate_total_attempts(displayed_patterns=4, overgen_multiplier=2.0) == 8


def test_calculate_total_attempts_min_displayed() -> None:
    assert calculate_total_attempts(displayed_patterns=4, overgen_multiplier=0.5) == 4


def test_plan_overgen_indices() -> None:
    assert plan_overgen_indices(displayed_patterns=4, overgen_multiplier=2.0) == [
        0, 1, 2, 3, 4, 5, 6, 7,
    ]
