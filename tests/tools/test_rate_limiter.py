import pytest
import asyncio
from datetime import datetime, timedelta

from core.tools.rate_limiter import RateLimiter, RateLimitConfig

@pytest.fixture
async def rate_limiter():
    """Create a rate limiter instance for testing."""
    config = RateLimitConfig(
        max_requests=5,
        window_seconds=1,
        max_concurrent=2,
        burst_limit=3,
        cooldown_seconds=1
    )
    limiter = RateLimiter(config)
    await limiter.start()
    yield limiter
    await limiter.stop()

@pytest.mark.asyncio
async def test_request_limit(rate_limiter):
    """Test request rate limiting."""
    tool_id = "test_tool"
    
    # Make requests up to limit
    for _ in range(rate_limiter._config.max_requests):
        assert await rate_limiter.check_rate_limit(tool_id)
    
    # Next request should be denied
    assert not await rate_limiter.check_rate_limit(tool_id)
    
    # Wait for window to reset
    await asyncio.sleep(rate_limiter._config.window_seconds + 0.1)
    
    # Should allow requests again
    assert await rate_limiter.check_rate_limit(tool_id)

@pytest.mark.asyncio
async def test_concurrent_limit(rate_limiter):
    """Test concurrent execution limiting."""
    tool_id = "test_tool"
    
    # Start concurrent executions up to limit
    for _ in range(rate_limiter._config.max_concurrent):
        assert await rate_limiter.check_rate_limit(tool_id)
    
    # Next execution should be denied
    assert not await rate_limiter.check_rate_limit(tool_id)
    
    # Release one slot
    await rate_limiter.release(tool_id)
    
    # Should allow another execution
    assert await rate_limiter.check_rate_limit(tool_id)

@pytest.mark.asyncio
async def test_burst_limit(rate_limiter):
    """Test burst rate limiting."""
    tool_id = "test_tool"
    
    # Make burst requests up to limit
    for _ in range(rate_limiter._config.burst_limit):
        assert await rate_limiter.check_rate_limit(tool_id)
    
    # Next request should be denied
    assert not await rate_limiter.check_rate_limit(tool_id)
    
    # Wait for cooldown
    await asyncio.sleep(rate_limiter._config.cooldown_seconds + 0.1)
    
    # Should allow requests again
    assert await rate_limiter.check_rate_limit(tool_id)

@pytest.mark.asyncio
async def test_multiple_tools(rate_limiter):
    """Test rate limiting for multiple tools."""
    tool_1 = "tool_1"
    tool_2 = "tool_2"
    
    # Max out first tool
    for _ in range(rate_limiter._config.max_requests):
        assert await rate_limiter.check_rate_limit(tool_1)
    
    # Second tool should still work
    assert await rate_limiter.check_rate_limit(tool_2)
    
    # First tool should be denied
    assert not await rate_limiter.check_rate_limit(tool_1)

@pytest.mark.asyncio
async def test_cleanup(rate_limiter):
    """Test cleanup of old rate limit data."""
    tool_id = "test_tool"
    
    # Make some requests
    for _ in range(3):
        assert await rate_limiter.check_rate_limit(tool_id)
    
    # Wait for cleanup
    await asyncio.sleep(rate_limiter._config.window_seconds + 0.1)
    await rate_limiter._cleanup()
    
    # Verify data is cleaned up
    assert tool_id not in rate_limiter._requests
    assert tool_id not in rate_limiter._concurrent

@pytest.mark.asyncio
async def test_get_limits(rate_limiter):
    """Test getting current rate limit counters."""
    tool_id = "test_tool"
    
    # Make some requests
    for _ in range(2):
        await rate_limiter.check_rate_limit(tool_id)
    
    # Get limits
    limits = rate_limiter.get_limits(tool_id)
    
    assert limits["requests"] == 2
    assert limits["concurrent"] == 2
    assert limits["burst"] == 2

@pytest.mark.asyncio
async def test_concurrent_requests(rate_limiter):
    """Test concurrent rate limit checks."""
    tool_id = "test_tool"
    
    # Create concurrent requests
    tasks = [
        rate_limiter.check_rate_limit(tool_id)
        for _ in range(10)
    ]
    
    # Execute concurrently
    results = await asyncio.gather(*tasks)
    
    # Verify only max_concurrent requests were allowed
    assert sum(results) == rate_limiter._config.max_concurrent 