"""匿名化ユーティリティのユニットテスト。"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.anonymization import (  # noqa: E402
    anonymize_id,
    anonymize_timestamp,
    build_failure_record,
)


def test_anonymize_id_deterministic() -> None:
    assert anonymize_id("sess-1") == anonymize_id("sess-1")


def test_anonymize_id_differs() -> None:
    assert anonymize_id("sess-1") != anonymize_id("sess-2")


def test_anonymize_timestamp_month_precision() -> None:
    ts = datetime(2026, 5, 17, 12, 34, 56, tzinfo=timezone.utc)
    assert anonymize_timestamp(ts) == "2026-05"


def test_build_failure_record_no_photos() -> None:
    rec = build_failure_record(
        session_id="sess-xyz",
        property_id="prop-a",
        provider="comfyui",
        stage="stage1",
        reason_code="quality_reject",
        arcface_score=0.55,
        pose_score=0.80,
        overgen_index=3,
    )
    assert "session_hash" in rec
    assert rec["provider"] == "comfyui"
    # Personally identifiable fields must NOT be present
    assert "photo_path" not in rec
    assert "session_id" not in rec
