import pytest
import asyncio
from datetime import datetime

from core.tools.timeout import TimeoutManager, TimeoutError

@pytest.fixture
async def timeout_manager():
    """Create a timeout manager instance for testing."""
    manager = TimeoutManager(default_timeout=1.0)
    await manager.start()
    yield manager
    await manager.stop()

async def slow_function(delay: float):
    """Test function that takes time to complete."""
    await asyncio.sleep(delay)
    return "completed"

@pytest.mark.asyncio
async def test_successful_execution(timeout_manager):
    """Test successful execution within timeout."""
    result = await timeout_manager.execute_with_timeout(
        "test_tool",
        slow_function,
        timeout=2.0,
        delay=0.1
    )
    assert result == "completed"

@pytest.mark.asyncio
async def test_timeout_execution(timeout_manager):
    """Test execution that exceeds timeout."""
    with pytest.raises(TimeoutError) as exc_info:
        await timeout_manager.execute_with_timeout(
            "test_tool",
            slow_function,
            timeout=0.1,
            delay=1.0
        )
    
    assert "test_tool" in str(exc_info.value)
    assert "0.1 seconds" in str(exc_info.value)

@pytest.mark.asyncio
async def test_default_timeout(timeout_manager):
    """Test execution with default timeout."""
    # Should succeed (delay < default timeout)
    result = await timeout_manager.execute_with_timeout(
        "test_tool",
        slow_function,
        delay=0.1
    )
    assert result == "completed"
    
    # Should timeout (delay > default timeout)
    with pytest.raises(TimeoutError):
        await timeout_manager.execute_with_timeout(
            "test_tool",
            slow_function,
            delay=2.0
        )

@pytest.mark.asyncio
async def test_timeout_decorator(timeout_manager):
    """Test timeout decorator functionality."""
    @timeout_manager.timeout_decorator("test_tool", timeout=0.5)
    async def decorated_function(delay: float):
        return await slow_function(delay)
    
    # Should succeed
    result = await decorated_function(0.1)
    assert result == "completed"
    
    # Should timeout
    with pytest.raises(TimeoutError):
        await decorated_function(1.0)

@pytest.mark.asyncio
async def test_multiple_executions(timeout_manager):
    """Test handling multiple executions."""
    # Create multiple execution tasks
    tasks = []
    for i in range(5):
        tasks.append(
            timeout_manager.execute_with_timeout(
                f"tool_{i}",
                slow_function,
                timeout=0.5,
                delay=0.1 if i < 3 else 1.0
            )
        )
    
    # Execute concurrently
    results = []
    for task in asyncio.as_completed(tasks):
        try:
            result = await task
            results.append(("success", result))
        except TimeoutError:
            results.append(("timeout", None))
    
    # Verify results
    assert len(results) == 5
    assert sum(1 for r in results if r[0] == "success") == 3
    assert sum(1 for r in results if r[0] == "timeout") == 2

@pytest.mark.asyncio
async def test_cleanup(timeout_manager):
    """Test cleanup of completed and timed out executions."""
    # Start some executions
    tasks = [
        timeout_manager.execute_with_timeout(
            "test_tool",
            slow_function,
            timeout=0.1,
            delay=0.5
        )
        for _ in range(3)
    ]
    
    # Wait for timeouts
    for task in tasks:
        with pytest.raises(TimeoutError):
            await task
    
    # Wait for cleanup
    await asyncio.sleep(0.2)
    await timeout_manager._cleanup()
    
    # Verify all executions are cleaned up
    assert len(timeout_manager._active_executions) == 0

@pytest.mark.asyncio
async def test_active_executions(timeout_manager):
    """Test getting information about active executions."""
    # Start an execution
    task = asyncio.create_task(
        timeout_manager.execute_with_timeout(
            "test_tool",
            slow_function,
            timeout=1.0,
            delay=0.5
        )
    )
    
    # Get active executions
    await asyncio.sleep(0.1)
    executions = timeout_manager.get_active_executions()
    
    assert len(executions) == 1
    execution = list(executions.values())[0]
    assert execution["elapsed"] > 0
    assert execution["timeout"] == 1.0
    assert not execution["is_done"]
    
    # Wait for completion
    await task
    
    # Verify execution is removed
    executions = timeout_manager.get_active_executions()
    assert len(executions) == 0

@pytest.mark.asyncio
async def test_cancel_on_timeout(timeout_manager):
    """Test that tasks are properly cancelled on timeout."""
    cancel_flag = False
    
    async def cancellable_function():
        nonlocal cancel_flag
        try:
            await asyncio.sleep(2.0)
        except asyncio.CancelledError:
            cancel_flag = True
            raise
    
    with pytest.raises(TimeoutError):
        await timeout_manager.execute_with_timeout(
            "test_tool",
            cancellable_function,
            timeout=0.1
        )
    
    # Verify function was cancelled
    assert cancel_flag 