"""Run with: python examples/basic_usage.py"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sliding_window_rate_limiter import SlidingWindowCounterLimiter, SlidingWindowLogLimiter


def demo(name: str, limiter) -> None:
    print(f"\n{name}: limit={limiter.limit}, window={limiter.window_seconds}s")
    for i in range(6):
        allowed = limiter.allow(key="user-123")
        print(f"  request {i + 1}: {'allowed' if allowed else 'rejected'}")
        time.sleep(0.2)


if __name__ == "__main__":
    demo("Sliding window log", SlidingWindowLogLimiter(limit=3, window_seconds=1))
    demo("Sliding window counter", SlidingWindowCounterLimiter(limit=3, window_seconds=1))
