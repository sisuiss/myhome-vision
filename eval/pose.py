"""OpenPose / MediaPipe 骨格類似度スコアラー（骨格）。

体型（骨格比率）の一貫性を測る。実装では mediapipe / openpose を使う。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PoseScore:
    similarity: float  # 0.0 - 1.0
    reference_keypoints: int
    target_keypoints: int


class PoseScorer:
    def __init__(self, backend: str = "mediapipe") -> None:
        self.backend = backend

    def similarity(self, reference: str | Path, target: str | Path) -> PoseScore:
        """Phase 0 スタブ: 0.75 固定。"""
        return PoseScore(similarity=0.75, reference_keypoints=17, target_keypoints=17)
