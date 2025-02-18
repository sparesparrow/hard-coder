import pytest
import asyncio
import os
from typing import Dict, Any
from datetime import datetime

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def base_monitoring_config() -> Dict[str, Any]:
    """Provide base monitoring configuration for testing."""
    return {
        "screenshot": {
            "interval_seconds": 0.1,  # Fast intervals for testing
            "max_samples": 5,
            "retention_hours": 1,
            "output_dir": "test_screenshots",
            "max_dimension": 800,
            "compression_quality": 85
        },
        "network": {
            "interval_seconds": 0.1,
            "max_samples": 5,
            "retention_hours": 1,
            "capture_connections": True,
            "capture_io_counters": True,
            "excluded_ports": [0]
        },
        "clipboard": {
            "interval_seconds": 0.1,
            "max_samples": 5,
            "retention_hours": 1,
            "max_content_length": 1000,
            "hash_content": True
        }
    }

@pytest.fixture
def test_context() -> Dict[str, Any]:
    """Create a test context with valid configuration."""
    return {
        "monitoring_config": {
            "screenshot": {
                "interval_seconds": 60,
                "max_samples": 5,
                "retention_hours": 1,
                "output_dir": "test_screenshots",
                "max_dimension": 800,
                "compression_quality": 85,
                "resource_limits": {
                    "memory_mb": 100,
                    "cpu_percent": 10
                }
            },
            "network": {
                "interval_seconds": 5,
                "max_samples": 5,
                "retention_hours": 1,
                "capture_connections": True,
                "capture_io_counters": True,
                "excluded_ports": [0],
                "resource_limits": {
                    "memory_mb": 300,
                    "cpu_percent": 15
                }
            },
            "clipboard": {
                "interval_seconds": 5,
                "max_samples": 5,
                "retention_hours": 1,
                "max_content_length": 1000,
                "hash_content": True,
                "resource_limits": {
                    "memory_mb": 200,
                    "cpu_percent": 10
                }
            }
        },
        "enabled_services": ["screenshot", "network", "clipboard"]
    }

@pytest.fixture(autouse=True)
async def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    # Clean up test directories
    test_dirs = ["test_screenshots"]
    for dir_path in test_dirs:
        if os.path.exists(dir_path):
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            try:
                os.rmdir(dir_path)
            except Exception:
                pass

@pytest.fixture
def mock_metrics(mocker):
    """Mock Prometheus metrics for testing."""
    return {
        "counter": mocker.Mock(),
        "histogram": mocker.Mock(),
        "gauge": mocker.Mock()
    } 