import pytest

from app.limits import LIMITER


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    # Each test starts with empty counters, so tests cannot push each other over a limit.
    LIMITER.reset()
    yield
    LIMITER.reset()
