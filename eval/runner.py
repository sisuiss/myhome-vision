"""評価ランナー：生成動画 1本に対して ArcFace / Pose / Uncanny を計算し、
Quality-gate に渡せる形にまとめる。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .arcface import ArcFaceScorer
from .pose import PoseScorer
from .uncanny import UncannyScorer


@dataclass
class Evaluation:
    arcface_score: float
    pose_score: float
    uncanny_score: float

    def as_dict(self) -> dict:
        return asdict(self)


class EvaluationRunner:
    def __init__(self) -> None:
        self.arcface = ArcFaceScorer()
        self.pose = PoseScorer()
        self.uncanny = UncannyScorer()

    def evaluate(
        self,
        reference_photo: str | Path,
        video_path: str | Path,
        frames_dir: str | Path | None = None,
    ) -> Evaluation:
        arc = self.arcface.video_mean_similarity(reference_photo, frames_dir or video_path)
        pose = self.pose.similarity(reference_photo, video_path).similarity
        un = self.uncanny.score(video_path).score
        return Evaluation(arcface_score=arc, pose_score=pose, uncanny_score=un)
