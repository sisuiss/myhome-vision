"""Over-generation 計算ロジック。

03_機能仕様書 §7.4 / §13.3 / §14.2 参照。
- 顧客提示本数（displayed_patterns）× overgen_multiplier の本数を並列生成
- Quality-gate 通過本から先頭 displayed_patterns 本を選出して表示
- 数量は顧客に非開示（F-06）
"""
from __future__ import annotations

import math

from ..core.config import get_settings


def calculate_total_attempts(
    displayed_patterns: int | None = None,
    overgen_multiplier: float | None = None,
) -> int:
    settings = get_settings()
    displayed = displayed_patterns or settings.displayed_patterns
    mult = overgen_multiplier or settings.overgen_multiplier
    return max(displayed, math.ceil(displayed * mult))


def plan_overgen_indices(
    displayed_patterns: int | None = None,
    overgen_multiplier: float | None = None,
) -> list[int]:
    total = calculate_total_attempts(displayed_patterns, overgen_multiplier)
    return list(range(total))
