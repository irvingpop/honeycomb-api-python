# DeepEval Parallelization Strategy

## Current State

**Test Architecture:**
- ~53 test cases across 12 resources
- 4 test methods per test case (tool_selection_basic, tool_selection_llm_eval, argument_basic, argument_llm_eval)
- Total: ~212 test executions if running all modes

**API Call Pattern per Test:**
1. `call_claude_with_tools()` - Claude API call for tool invocation
2. LLM metrics (if enabled) - Additional Claude API call for evaluation

**Current Bottleneck:** Sequential test execution makes ~2 API calls per test case, limited by Anthropic rate limits.

## Anthropic Rate Limits by Tier

| Tier | RPM (Claude Sonnet 4.x) | ITPM | OTPM |
|------|-------------------------|------|------|
| 1 | 50 | 30,000 | 8,000 |
| 2 | 1,000 | 450,000 | 90,000 |
| 3 | 2,000 | 800,000 | 160,000 |
| 4 | 4,000 | 2,000,000 | 400,000 |

**Key Insight:** Rate limits use token bucket algorithm with continuous replenishment.

## Parallelization Strategies

### Strategy 1: pytest-xdist with Rate-Limited Workers

**Approach:** Use pytest-xdist for process-based parallelization with careful worker count.

**Configuration:**
```bash
# Add to pyproject.toml dev dependencies
pytest-xdist = ">=3.0"
```

**Safe Worker Counts by Tier:**

| Tier | Safe Workers | Reasoning |
|------|--------------|-----------|
| 1 | 2-3 | 50 RPM / ~20 requests per test = 2-3 concurrent tests |
| 2 | 10-15 | 1000 RPM allows more parallelism |
| 3 | 20-30 | 2000 RPM, balance with token limits |
| 4 | 50+ | High limits allow aggressive parallelism |

**Usage:**
```bash
# Tier 1 (conservative)
poetry run pytest tests/integration/test_claude_tools_eval.py -n 3

# Tier 4 (aggressive)
poetry run pytest tests/integration/test_claude_tools_eval.py -n auto
```

**Pros:**
- Simple to implement
- Works with existing test structure
- No code changes needed beyond adding xdist

**Cons:**
- No fine-grained rate control
- Potential for burst rate limit errors
- Each worker creates separate API client

### Strategy 2: DeepEval's Built-in AsyncConfig

**Approach:** Use DeepEval's `evaluate()` function with `AsyncConfig` instead of pytest parameterization.

**Implementation:**
```python
from deepeval import evaluate
from deepeval.evaluate import AsyncConfig, CacheConfig

# Configure rate limiting
async_config = AsyncConfig(
    run_async=True,
    max_concurrent=10,      # Limit parallel test cases
    throttle_value=1,       # 1 second between test starts
)

# Enable caching for re-runs
cache_config = CacheConfig(
    use_cache=True,
    write_cache=True,
)

# Run evaluation
evaluate(
    test_cases=all_test_cases,
    metrics=[ToolCorrectnessMetric(), ArgumentCorrectnessMetric()],
    async_config=async_config,
    cache_config=cache_config,
)
```

**Recommended Settings by Tier:**

| Tier | max_concurrent | throttle_value |
|------|----------------|----------------|
| 1 | 5 | 2 |
| 2 | 15 | 0.5 |
| 3 | 25 | 0.3 |
| 4 | 50 | 0.1 |

**Pros:**
- Built-in rate limiting
- Caching prevents redundant evaluations
- DeepEval handles retry logic

**Cons:**
- Requires rewriting tests to use `evaluate()` instead of pytest parameterization
- Less integration with pytest ecosystem

### Strategy 3: Hybrid Approach (Recommended)

**Approach:** Combine pytest-xdist for test distribution with custom rate limiting wrapper.

**Implementation:**

```python
# tests/integration/conftest.py
import asyncio
import time
from functools import wraps

import pytest

# Rate limiter shared across workers via file lock or semaphore
class RateLimiter:
    def __init__(self, requests_per_minute: int = 40):
        self.min_interval = 60.0 / requests_per_minute
        self.last_request = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            wait_time = self.last_request + self.min_interval - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_request = time.monotonic()

# Per-process rate limiter
_rate_limiter = None

@pytest.fixture(scope="session")
def rate_limiter():
    global _rate_limiter
    if _rate_limiter is None:
        # Tier 1: ~40 RPM safe, Tier 4: ~3000 RPM safe
        rpm = int(os.environ.get("ANTHROPIC_RPM_LIMIT", "40"))
        _rate_limiter = RateLimiter(rpm)
    return _rate_limiter

# Modified call function with rate limiting
async def call_claude_with_tools_rate_limited(client, prompt: str, rate_limiter) -> dict:
    await rate_limiter.acquire()
    # ... existing implementation
```

**Usage:**
```bash
# Tier 1: 3 workers, 15 RPM each = 45 total RPM (under 50 limit)
ANTHROPIC_RPM_LIMIT=15 poetry run pytest tests/integration/test_claude_tools_eval.py -n 3

# Tier 4: 8 workers, 400 RPM each = 3200 total RPM (under 4000 limit)
ANTHROPIC_RPM_LIMIT=400 poetry run pytest tests/integration/test_claude_tools_eval.py -n 8
```

**Pros:**
- Fine-grained control over rate limiting
- Works with existing pytest structure
- Configurable per tier via environment variable

**Cons:**
- More complex implementation
- Per-process rate limiters don't coordinate across workers

### Strategy 4: Batch API (Best for Large Scale)

**Approach:** Use Anthropic's Message Batches API for non-interactive evaluation.

**When to Use:**
- Running 100+ test cases
- Not time-sensitive (batches can take hours)
- Want lowest cost per evaluation

**Implementation Concept:**
```python
from anthropic import Anthropic

def create_eval_batch(test_cases: list[dict]) -> str:
    """Submit all test cases as a batch job."""
    client = Anthropic()

    requests = [
        {
            "custom_id": tc["id"],
            "params": {
                "model": "claude-sonnet-4-5-20250929",
                "max_tokens": 1024,
                "tools": HONEYCOMB_TOOLS,
                "messages": [{"role": "user", "content": tc["prompt"]}],
            }
        }
        for tc in test_cases
    ]

    batch = client.messages.batches.create(requests=requests)
    return batch.id

def poll_batch_results(batch_id: str) -> list[dict]:
    """Poll for batch completion and return results."""
    # ... polling logic
```

**Batch API Limits:**

| Tier | Max Batch Requests | Max in Queue |
|------|-------------------|--------------|
| 1 | 100,000 | 100,000 |
| 4 | 100,000 | 500,000 |

**Pros:**
- No rate limiting concerns
- Most cost-effective for large test suites
- Can run 53 test cases in single batch

**Cons:**
- Asynchronous (not real-time results)
- Requires separate polling logic
- Not suitable for CI/CD pipelines requiring fast feedback

## Implemented Solution: Simple Caching

**Status:** Implemented and tested

### Architecture

Simple file-based caching for Claude API responses:

- Tool call results cached to `tests/integration/.tool_call_cache/`
- Cache key = SHA256 hash of full prompt text
- First run populates cache, subsequent runs are instant
- No DeepEval LLM evaluation overhead (removed for simplicity)

### Environment Variables

```bash
EVAL_USE_CACHE=true      # Enable caching (default: true)
```

### Measured Performance

| Scenario | Time | Notes |
|----------|------|-------|
| First run (empty cache) | ~5-6 min | 53 API calls @ ~6s each |
| Cached run | ~5 sec | All cache hits |

### Usage

```bash
# Run all tests (uses cache)
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v

# Run specific resource
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k triggers

# Clear cache for fresh run
rm -rf tests/integration/.tool_call_cache/

# Disable cache temporarily
EVAL_USE_CACHE=false poetry run pytest ...
```

### Test Structure

- `TestToolSelection` - Verifies correct tool is selected (53 tests)
- `TestArgumentCorrectness` - Verifies parameters match expectations (53 tests)
- `TestToolSchemas` - Schema validation (2 tests)
- **Total: 108 tests**

---

## Alternative Strategies (Not Implemented)

### Phase 1: Quick Win (pytest-xdist)

Add pytest-xdist to dev dependencies and use conservative parallelization:

```toml
# pyproject.toml
[tool.poetry.group.dev.dependencies]
pytest-xdist = ">=3.0"
```

```bash
# Run with 4 workers (safe for Tier 1+)
make eval-parallel  # poetry run pytest tests/integration/test_claude_tools_eval.py -n 4 -k basic
```

### Phase 2: DeepEval Caching

Enable DeepEval's caching to skip re-evaluation of unchanged test cases:

```bash
deepeval test run tests/integration/test_claude_tools_eval.py -c -n 4
```

### Phase 3: Rate-Limited Wrapper

Implement a rate limiter that respects Anthropic limits:

```python
# tests/integration/rate_limiter.py
import os
import time
import threading

class TokenBucketRateLimiter:
    """Thread-safe token bucket rate limiter."""

    def __init__(self, rpm: int = None):
        self.rpm = rpm or int(os.environ.get("ANTHROPIC_RPM_LIMIT", "40"))
        self.tokens = self.rpm
        self.max_tokens = self.rpm
        self.refill_rate = self.rpm / 60.0  # tokens per second
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            # Refill tokens
            elapsed = now - self.last_refill
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            # Wait if needed
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.refill_rate
                time.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1
```

### Phase 4: CI Configuration

Create tiered CI workflows:

```yaml
# .github/workflows/evals.yml
jobs:
  eval-fast:
    # Basic assertions only (no LLM eval)
    runs-on: ubuntu-latest
    steps:
      - run: poetry run pytest tests/integration/test_claude_tools_eval.py -v -k basic -n 4

  eval-full:
    # Full LLM evaluation (slower, scheduled)
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - run: poetry run pytest tests/integration/test_claude_tools_eval.py -v -n 2
```

## Performance Projections

### Current (Sequential)

| Test Mode | Per Test | 53 Tests | Total |
|-----------|----------|----------|-------|
| Basic only | ~3s | 159s | ~3 min |
| LLM eval | ~10s | 530s | ~9 min |
| Both | ~13s | 689s | ~12 min |

### With pytest-xdist (4 workers)

| Test Mode | 53 Tests | Speedup |
|-----------|----------|---------|
| Basic only | ~45s | 3.5x |
| LLM eval | ~150s | 3.5x |
| Both | ~180s | 3.8x |

### With Batch API

| Test Mode | 53 Tests | Notes |
|-----------|----------|-------|
| All tests | ~60s* | *Plus batch processing time |

## Configuration Reference

### Environment Variables

```bash
# Rate limiting
ANTHROPIC_RPM_LIMIT=40          # Requests per minute (adjust per tier)
ANTHROPIC_API_KEY=sk-...        # Required

# DeepEval
DEEPEVAL_RESULTS_FOLDER=.deepeval  # Cache location
```

### Makefile Targets

```makefile
.PHONY: eval eval-fast eval-parallel

eval:
	poetry run pytest tests/integration/test_claude_tools_eval.py -v

eval-fast:
	poetry run pytest tests/integration/test_claude_tools_eval.py -v -k basic

eval-parallel:
	poetry run pytest tests/integration/test_claude_tools_eval.py -v -n 4 -k basic
```

## Sources

- [DeepEval Flags and Configs](https://deepeval.com/docs/evaluation-flags-and-configs)
- [Anthropic Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/)
- [DeepEval Parallel Execution Issue #259](https://github.com/confident-ai/deepeval/issues/259)
