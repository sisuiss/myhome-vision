"""failed_generations 用の匿名化ユーティリティ。

本人識別不能になるよう、セッションID・物件IDをソルト付き SHA256 でハッシュ化し、
時刻を月粒度に丸める。写真・動画本体は保存しない前提（メタ情報のみ）。
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from .config import get_settings


def anonymize_id(raw: str) -> str:
    """セッションID等の一方向ハッシュ化。"""
    salt = get_settings().anon_salt.encode("utf-8")
    h = hashlib.sha256()
    h.update(salt)
    h.update(b"|")
    h.update(raw.encode("utf-8"))
    return h.hexdigest()


def anonymize_timestamp(ts: datetime | None = None) -> str:
    """タイムスタンプを YYYY-MM に丸める。"""
    t = ts or datetime.now(timezone.utc)
    return f"{t.year:04d}-{t.month:02d}"


def build_failure_record(
    *,
    session_id: str,
    property_id: str | None,
    provider: str,
    stage: str,
    reason_code: str,
    arcface_score: float | None = None,
    pose_score: float | None = None,
    overgen_index: int | None = None,
    occurred_at: datetime | None = None,
) -> dict:
    """failed_generations に保存する匿名化済みレコードを組み立てる。"""
    return {
        "session_hash": anonymize_id(session_id),
        "property_hash": anonymize_id(property_id) if property_id else None,
        "provider": provider,
        "stage": stage,
        "reason_code": reason_code,
        "arcface_score": arcface_score,
        "pose_score": pose_score,
        "overgen_index": overgen_index,
        "occurred_month": anonymize_timestamp(occurred_at),
    }
