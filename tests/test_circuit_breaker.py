"""Circuit Breaker のユニットテスト。"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.circuit_breaker import BreakerState, _ProviderBreaker  # noqa: E402


def test_closed_on_success() -> None:
    b = _ProviderBreaker(name="test")
    for _ in range(5):
        b.record(success=True)
    assert b.state == BreakerState.CLOSED
    assert b.allow() is True


def test_opens_on_failures() -> None:
    b = _ProviderBreaker(name="test")
    for _ in range(10):
        b.record(success=False)
    assert b.state == BreakerState.OPEN
    assert b.allow() is False


def test_half_open_after_cooldown() -> None:
    b = _ProviderBreaker(name="test")
    for _ in range(10):
        b.record(success=False)
    assert b.state == BreakerState.OPEN

    # cooldown を短絡（本来は 600秒だが、テストでは強制前倒し）
    b.opened_at = time.time() - 9999
    assert b.allow() is True
    assert b.state == BreakerState.HALF_OPEN

    b.record(success=True)
    assert b.state == BreakerState.CLOSED
