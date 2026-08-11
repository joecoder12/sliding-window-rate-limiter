import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sliding_window_rate_limiter import SlidingWindowCounterLimiter


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class SlidingWindowCounterLimiterTest(unittest.TestCase):
    def test_allows_up_to_limit_within_window(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowCounterLimiter(limit=3, window_seconds=10, clock=clock)

        self.assertTrue(limiter.allow())
        clock.advance(1)
        self.assertTrue(limiter.allow())
        clock.advance(1)
        self.assertTrue(limiter.allow())
        clock.advance(1)
        self.assertFalse(limiter.allow())

    def test_previous_window_weight_decays_over_time(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowCounterLimiter(limit=3, window_seconds=10, clock=clock)

        for _ in range(3):
            self.assertTrue(limiter.allow())

        # Right at the next window boundary the previous window still
        # weighs at full strength, so the estimate matches the limit and
        # is rejected. clock is at t=2, advance to t=10 (window 1, offset 0).
        clock.advance(8)
        self.assertFalse(limiter.allow())

        # Later in the next window the previous window's contribution has
        # decayed enough to allow more requests through. t=10 -> t=15.
        clock.advance(5)
        self.assertTrue(limiter.allow())

    def test_far_future_request_resets_state(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowCounterLimiter(limit=1, window_seconds=10, clock=clock)

        self.assertTrue(limiter.allow())
        self.assertFalse(limiter.allow())

        clock.advance(1000)  # many windows later, previous window is irrelevant
        self.assertTrue(limiter.allow())

    def test_keys_are_independent(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowCounterLimiter(limit=1, window_seconds=10, clock=clock)

        self.assertTrue(limiter.allow("a"))
        self.assertFalse(limiter.allow("a"))
        self.assertTrue(limiter.allow("b"))

    def test_rejects_invalid_configuration(self) -> None:
        with self.assertRaises(ValueError):
            SlidingWindowCounterLimiter(limit=0, window_seconds=10)
        with self.assertRaises(ValueError):
            SlidingWindowCounterLimiter(limit=10, window_seconds=0)


if __name__ == "__main__":
    unittest.main()
