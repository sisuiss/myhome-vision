"""Quality-gate 判定のユニットテスト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.quality_gate import QualityDecision, judge  # noqa: E402


def test_accept() -> None:
    v = judge(arcface_score=0.80, pose_score=0.80, uncanny_score=0.10)
    assert v.decision == QualityDecision.ACCEPT


def test_reject_all_fail() -> None:
    v = judge(arcface_score=0.40, pose_score=0.40, uncanny_score=0.80)
    assert v.decision == QualityDecision.REJECT


def test_borderline_two_of_three() -> None:
    # ArcFace 通過、Pose 通過、Uncanny 失敗 → borderline（L4 送り）
    v = judge(arcface_score=0.80, pose_score=0.80, uncanny_score=0.90)
    assert v.decision == QualityDecision.BORDERLINE
    assert any("uncanny" in r for r in v.reasons)
