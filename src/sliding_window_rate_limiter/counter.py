"""Sliding window counter rate limiter.

Approximates a sliding window by keeping a request count for the current
fixed window and the previous one, then weighting the previous window's
count by how much it still overlaps the trailing window. O(1) memory per
key, at the cost of assuming a roughly uniform request rate within each
window.
"""

from __future__ import annotations

import math
import threading
import time
from typing import Callable, Dict, Tuple


class SlidingWindowCounterLimiter:
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
        # key -> (window_index, current_count, previous_count)
        self._state: Dict[str, Tuple[int, int, int]] = {}

    def allow(self, key: str = "default") -> bool:
        now = self._clock()
        window_index = math.floor(now / self.window_seconds)
        offset = now - window_index * self.window_seconds

        with self._lock:
            prev_index, current, previous = self._state.get(key, (window_index, 0, 0))

            if window_index == prev_index:
                pass
            elif window_index == prev_index + 1:
                previous = current
                current = 0
            else:
                previous = 0
                current = 0

            weight = max(0.0, (self.window_seconds - offset) / self.window_seconds)
            estimated = previous * weight + current

            if estimated < self.limit:
                current += 1
                self._state[key] = (window_index, current, previous)
                return True

            self._state[key] = (window_index, current, previous)
            return False
