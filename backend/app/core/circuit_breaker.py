"""プロバイダー用 Circuit Breaker。

- 直近 window 秒のエラー率が閾値超 → OPEN（一時遮断）
- cooldown 経過で HALF_OPEN → 1リクエスト成功で CLOSED 復帰

本PoCではインメモリ簡易版。将来 Redis 共有に差し替え。
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock

from .config import get_settings


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class _ProviderBreaker:
    name: str
    state: BreakerState = BreakerState.CLOSED
    events: deque[tuple[float, bool]] = field(default_factory=deque)  # (ts, success)
    opened_at: float | None = None
    lock: Lock = field(default_factory=Lock)

    def _prune(self, now: float, window: int) -> None:
        cutoff = now - window
        while self.events and self.events[0][0] < cutoff:
            self.events.popleft()

    def record(self, success: bool) -> None:
        settings = get_settings()
        now = time.time()
        with self.lock:
            self.events.append((now, success))
            self._prune(now, settings.cb_window_seconds)

            # 現状態に応じた遷移判定
            if self.state == BreakerState.HALF_OPEN:
                if success:
                    self.state = BreakerState.CLOSED
                    self.opened_at = None
                else:
                    self.state = BreakerState.OPEN
                    self.opened_at = now
                return

            total = len(self.events)
            if total < 5:
                return  # サンプル数不足
            failures = sum(1 for _, ok in self.events if not ok)
            error_rate = failures / total
            if error_rate >= settings.cb_error_rate_threshold:
                self.state = BreakerState.OPEN
                self.opened_at = now

    def allow(self) -> bool:
        """リクエストを通してよいか。OPEN 中でも cooldown 経過で HALF_OPEN へ。"""
        settings = get_settings()
        now = time.time()
        with self.lock:
            if self.state == BreakerState.OPEN:
                if (
                    self.opened_at is not None
                    and now - self.opened_at >= settings.cb_cooldown_seconds
                ):
                    self.state = BreakerState.HALF_OPEN
                    return True
                return False
            return True

    def snapshot(self) -> dict:
        with self.lock:
            total = len(self.events)
            failures = sum(1 for _, ok in self.events if not ok)
            return {
                "name": self.name,
                "state": self.state.value,
                "events_in_window": total,
                "failures_in_window": failures,
                "error_rate": (failures / total) if total else 0.0,
                "opened_at": self.opened_at,
            }


class CircuitBreakerRegistry:
    """プロバイダー別 Breaker のレジストリ。"""

    def __init__(self) -> None:
        self._breakers: dict[str, _ProviderBreaker] = {}
        self._lock = Lock()

    def get(self, provider: str) -> _ProviderBreaker:
        with self._lock:
            if provider not in self._breakers:
                self._breakers[provider] = _ProviderBreaker(name=provider)
            return self._breakers[provider]

    def allow(self, provider: str) -> bool:
        return self.get(provider).allow()

    def record(self, provider: str, success: bool) -> None:
        self.get(provider).record(success)

    def snapshot_all(self) -> dict[str, dict]:
        with self._lock:
            return {name: b.snapshot() for name, b in self._breakers.items()}


registry = CircuitBreakerRegistry()
