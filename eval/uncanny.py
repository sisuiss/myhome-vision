"""不気味の谷（uncanny）検出スコアラー（骨格）。

実装方針:
- 顔の対称性／解剖学的破綻の検知
- Latent-space anomaly（VAE再構成誤差）
- 時系列ID分散（ArcFace 連続フレームばらつき）
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class UncannyScore:
    score: float  # 0.0 = natural, 1.0 = clearly uncanny
    reasons: list[str]


class UncannyScorer:
    def score(self, video_path: str | Path) -> UncannyScore:
        """Phase 0 スタブ: 0.15 固定（ほぼ自然）。"""
        return UncannyScore(score=0.15, reasons=[])
