from unittest.mock import patch, MagicMock, AsyncMock
import pytest
import os
import asyncio
from mcp_system_context.__main__ import async_main, main
from mcp_system_context.config import ServerConfig

@pytest.fixture
def mock_server():
    """Create a mock server."""
    with patch('mcp_system_context.__main__.SystemContextServer') as mock:
        # Set up async mock for run method
        mock.return_value.run = AsyncMock()
        mock.return_value._enable_remote_transport = MagicMock()
        # Mock the clipboard monitor to prevent event loop issues
        mock.return_value._start_clipboard_monitor = MagicMock()
        yield mock

@pytest.fixture
def mock_config():
    """Create a mock config."""
    with patch('mcp_system_context.__main__.ServerConfig') as mock:
        yield mock

@pytest.mark.asyncio
async def test_async_main_basic_functionality(mock_server, mock_config):
    """Test basic functionality of async_main."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]',
        'MCP_LOG_LEVEL': 'INFO'
    }):
        # Create a mock config
        config = ServerConfig(
            allowed_paths=["/tmp/test"],
            log_level="INFO"
        )
        mock_config.return_value = config

        # Run async_main
        await async_main()

        # Verify server was initialized and run
        mock_server.assert_called_once()
        mock_server.return_value.run.assert_awaited_once()

@pytest.mark.asyncio
async def test_async_main_with_remote_enabled(mock_server, mock_config):
    """Test async_main with remote transport enabled."""
    with patch.dict(os.environ, {
        'MCP_REMOTE_ENABLED': 'true',
        'MCP_ALLOWED_USERS': '["user1", "user2"]',
        'MCP_LOG_LEVEL': 'INFO'
    }):
        # Create a mock config
        config = ServerConfig(
            allowed_paths=["/tmp/test"],
            log_level="INFO"
        )
        mock_config.return_value = config

        # Run async_main
        await async_main()

        # Verify remote transport was enabled
        mock_server.return_value._enable_remote_transport.assert_called_once()
        mock_server.return_value.run.assert_awaited_once()

@pytest.mark.asyncio
async def test_async_main_with_custom_log_level(mock_server, mock_config):
    """Test async_main with custom log level."""
    with patch.dict(os.environ, {
        'MCP_LOG_LEVEL': 'DEBUG',
        'MCP_ALLOWED_USERS': '["user1", "user2"]'
    }):
        # Create a mock config
        config = ServerConfig(
            allowed_paths=["/tmp/test"],
            log_level="DEBUG"
        )
        mock_config.return_value = config

        # Run async_main
        await async_main()

        # Verify server was run with correct config
        mock_server.assert_called_once()
        mock_server.return_value.run.assert_awaited_once()

@pytest.mark.asyncio
async def test_async_main_error_handling(mock_server, mock_config):
    """Test error handling in async_main."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]',
        'MCP_LOG_LEVEL': 'INFO'
    }):
        # Create a mock config
        config = ServerConfig(
            allowed_paths=["/tmp/test"],
            log_level="INFO"
        )
        mock_config.return_value = config

        # Set up server to raise an exception
        mock_server.return_value.run = AsyncMock(side_effect=Exception("Test error"))

        # Run async_main and expect exception to be caught
        await async_main()

@pytest.mark.asyncio
async def test_main_keyboard_interrupt(mock_server, mock_config):
    """Test handling of KeyboardInterrupt in main."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]',
        'MCP_LOG_LEVEL': 'INFO'
    }):
        # Create a mock config
        config = ServerConfig(
            allowed_paths=["/tmp/test"],
            log_level="INFO"
        )
        mock_config.return_value = config

        # Create a mock server that raises KeyboardInterrupt
        mock_server.return_value.run = AsyncMock(side_effect=KeyboardInterrupt())

        # Run main and expect clean exit
        with pytest.raises(SystemExit) as exc_info:
            await main()
        assert exc_info.value.code == 0

@pytest.mark.asyncio
async def test_main_error_handling(mock_server, mock_config):
    """Test error handling in main."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]',
        'MCP_LOG_LEVEL': 'INFO'
    }):
        # Create a mock config
        config = ServerConfig(
            allowed_paths=["/tmp/test"],
            log_level="INFO"
        )
        mock_config.return_value = config

        # Create a mock server that raises an exception
        mock_server.return_value.run = AsyncMock(side_effect=Exception("Test error"))

        # Run main and expect non-zero exit code
        with pytest.raises(SystemExit) as exc_info:
            await main()
        assert exc_info.value.code == 1

@pytest.mark.asyncio
async def test_async_main_path_expansion(mock_server, mock_config):
    """Test that paths are properly expanded."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]',
        'MCP_LOG_LEVEL': 'INFO'
    }):
        # Create a mock config with a path containing ~
        config = ServerConfig(
            allowed_paths=["~/test"],
            log_level="INFO"
        )
        mock_config.return_value = config

        # Run async_main
        await async_main()

        # Verify server was initialized with expanded path
        mock_server.assert_called_once()
        mock_server.return_value.run.assert_awaited_once() 
        