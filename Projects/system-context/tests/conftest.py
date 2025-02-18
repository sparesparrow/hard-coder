"""Configure pytest for async tests."""

import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def set_asyncio_fixture_loop_scope():
    """Set the default fixture loop scope to function."""
    pytest.asyncio_fixture_loop_scope = "function" 