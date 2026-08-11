"""Sliding window log rate limiter.

Keeps an exact timestamp log per key and evicts entries that have fallen
out of the trailing window on every check. Precise (no boundary burst
issue) at the cost of O(limit) memory per key.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict


class SlidingWindowLogLimiter:
    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if limit <= 0:
            raise ValueError("limit must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._logs: Dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, key: str = "default") -> bool:
        now = self._clock()
        with self._lock:
            log = self._logs[key]
            self._evict(log, now)
            if len(log) < self.limit:
                log.append(now)
                return True
            return False

    def remaining(self, key: str = "default") -> int:
        now = self._clock()
        with self._lock:
            log = self._logs[key]
            self._evict(log, now)
            return max(0, self.limit - len(log))

    def _evict(self, log: Deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while log and log[0] <= cutoff:
            log.popleft()
