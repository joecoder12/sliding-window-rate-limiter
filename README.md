# sliding-window-rate-limiter

A small, dependency-free Python implementation of rate limiting using the
sliding window algorithm. Includes two variants:

- **`SlidingWindowLogLimiter`** — keeps an exact timestamp log per key and
  evicts entries once they fall outside the trailing window. Precise (no
  boundary burst issue), at the cost of O(limit) memory per key.
- **`SlidingWindowCounterLimiter`** — keeps two fixed-window counters
  (current + previous) per key and estimates the sliding count by weighting
  the previous window's contribution by how much it still overlaps the
  trailing window. O(1) memory per key, assumes a roughly uniform request
  rate within each window.

Both are thread-safe and support per-key limiting (e.g. per user or per IP).

## Install

```bash
pip install -e .
```

Requires Python 3.8+ and has no runtime dependencies.

## Usage

```python
from sliding_window_rate_limiter import SlidingWindowLogLimiter

limiter = SlidingWindowLogLimiter(limit=100, window_seconds=60)

if limiter.allow(key="user-123"):
    handle_request()
else:
    reject_request()
```

Or the counter-based variant, which trades a small amount of precision for
constant memory usage regardless of the limit:

```python
from sliding_window_rate_limiter import SlidingWindowCounterLimiter

limiter = SlidingWindowCounterLimiter(limit=100, window_seconds=60)
allowed = limiter.allow(key="user-123")
```

Run the runnable demo:

```bash
python examples/basic_usage.py
```

## How the sliding window algorithm works

A naive **fixed window** limiter (e.g. "100 requests per minute, reset every
minute") lets a client burst up to `2x` the limit around a window boundary —
100 requests in the last second of one window plus 100 in the first second
of the next. The sliding window algorithm avoids this by always looking at
the trailing `window_seconds` from *now*, not from a fixed clock boundary.

**Sliding window log** does this exactly: store every request timestamp for
a key, drop timestamps older than `now - window_seconds` on each check, and
allow the request if what's left is under the limit.

**Sliding window counter** approximates the same thing without storing every
timestamp. It tracks a count for the current fixed window and the previous
one, then computes:

```
estimated_count = previous_window_count * overlap_fraction + current_window_count
```

where `overlap_fraction` is how much of the previous window still falls
within the trailing `window_seconds`. This is O(1) memory per key instead of
O(limit), at the cost of assuming requests are spread evenly through each
window.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Project layout

```
src/sliding_window_rate_limiter/
  log.py       # SlidingWindowLogLimiter
  counter.py   # SlidingWindowCounterLimiter
tests/         # unit tests for both limiters
examples/      # runnable usage demo
```

## License

MIT — see [LICENSE](LICENSE).
