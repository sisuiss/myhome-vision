"""ArcFace 顔類似度スコアラー（骨格）。

Phase 0 では insightface / onnxruntime を使って実装予定。本ファイルは
インタフェースのみ定義し、実装は GPU 環境で差し替える。

Usage:
    from eval.arcface import ArcFaceScorer
    scorer = ArcFaceScorer()
    sim = scorer.similarity(reference_jpg_path, video_frame_jpg_path)
    # sim: 0.0 - 1.0（コサイン類似度、1.0=完全一致）
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ArcFaceScore:
    similarity: float
    reference_path: str
    target_path: str
    detected_faces_target: int


class ArcFaceScorer:
    """骨格実装。実装では insightface.app.FaceAnalysis を使用予定。"""

    def __init__(self, model_name: str = "buffalo_l") -> None:
        self.model_name = model_name
        self._app = None  # 実装時に insightface.FaceAnalysis をロード

    def similarity(self, reference: str | Path, target: str | Path) -> ArcFaceScore:
        """参照画像と対象画像の顔類似度を返す。

        Phase 0 スタブ: 0.70 固定。
        """
        return ArcFaceScore(
            similarity=0.70,
            reference_path=str(reference),
            target_path=str(target),
            detected_faces_target=1,
        )

    def video_mean_similarity(
        self, reference: str | Path, video_frames_dir: str | Path
    ) -> float:
        """フレーム列のArcFace平均類似度。"""
        return 0.68
