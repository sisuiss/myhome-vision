"""Quality-gate (L3 自動品質判定)。

03_機能仕様書 §13.11 の閾値に従い、生成結果を採用 / 差戻し / 境界値（L4 送り）に
分類する。ArcFace / OpenPose の実装は eval/ パッケージに委譲し、本モジュールは
判定ポリシーのみを担当する。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..core.config import get_settings


class QualityDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    BORDERLINE = "borderline"  # L4 人間レビューへ


@dataclass
class QualityVerdict:
    decision: QualityDecision
    quality_score: float
    arcface_score: float
    pose_score: float
    uncanny_score: float
    reasons: list[str]


def judge(
    *,
    arcface_score: float,
    pose_score: float,
    uncanny_score: float,
) -> QualityVerdict:
    settings = get_settings()
    reasons: list[str] = []

    arcface_ok = arcface_score >= settings.quality_arcface_min
    pose_ok = pose_score >= settings.quality_pose_min
    uncanny_ok = uncanny_score <= settings.quality_uncanny_max

    if not arcface_ok:
        reasons.append(f"arcface<{settings.quality_arcface_min:.2f}")
    if not pose_ok:
        reasons.append(f"pose<{settings.quality_pose_min:.2f}")
    if not uncanny_ok:
        reasons.append(f"uncanny>{settings.quality_uncanny_max:.2f}")

    quality_score = (
        max(0.0, arcface_score)
        + max(0.0, pose_score)
        + max(0.0, 1.0 - uncanny_score)
    ) / 3.0

    if arcface_ok and pose_ok and uncanny_ok:
        decision = QualityDecision.ACCEPT
    elif sum([arcface_ok, pose_ok, uncanny_ok]) >= 2:
        # 3項目中2項目クリア → L4 人間レビューへ
        decision = QualityDecision.BORDERLINE
    else:
        decision = QualityDecision.REJECT

    return QualityVerdict(
        decision=decision,
        quality_score=quality_score,
        arcface_score=arcface_score,
        pose_score=pose_score,
        uncanny_score=uncanny_score,
        reasons=reasons,
    )
