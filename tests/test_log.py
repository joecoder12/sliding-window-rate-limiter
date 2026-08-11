import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sliding_window_rate_limiter import SlidingWindowLogLimiter


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class SlidingWindowLogLimiterTest(unittest.TestCase):
    def test_allows_up_to_limit(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowLogLimiter(limit=3, window_seconds=10, clock=clock)

        self.assertTrue(limiter.allow())
        self.assertTrue(limiter.allow())
        self.assertTrue(limiter.allow())
        self.assertFalse(limiter.allow())

    def test_old_requests_expire_out_of_window(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowLogLimiter(limit=2, window_seconds=10, clock=clock)

        self.assertTrue(limiter.allow())
        clock.advance(5)
        self.assertTrue(limiter.allow())
        self.assertFalse(limiter.allow())

        clock.advance(5.01)  # first request is now outside the window
        self.assertTrue(limiter.allow())

    def test_keys_are_independent(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowLogLimiter(limit=1, window_seconds=10, clock=clock)

        self.assertTrue(limiter.allow("a"))
        self.assertFalse(limiter.allow("a"))
        self.assertTrue(limiter.allow("b"))

    def test_remaining(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowLogLimiter(limit=2, window_seconds=10, clock=clock)

        self.assertEqual(limiter.remaining(), 2)
        limiter.allow()
        self.assertEqual(limiter.remaining(), 1)
        limiter.allow()
        self.assertEqual(limiter.remaining(), 0)

    def test_rejects_invalid_configuration(self) -> None:
        with self.assertRaises(ValueError):
            SlidingWindowLogLimiter(limit=0, window_seconds=10)
        with self.assertRaises(ValueError):
            SlidingWindowLogLimiter(limit=10, window_seconds=0)


if __name__ == "__main__":
    unittest.main()
