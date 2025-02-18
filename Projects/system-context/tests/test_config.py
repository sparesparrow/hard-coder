"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from mcp_system_context.config import (
    ServerConfig,
    ClipboardConfig,
    SystemMonitorConfig,
    VectorDBConfig
)


def test_clipboard_config():
    """Test clipboard configuration."""
    # Test defaults
    config = ClipboardConfig()
    assert config.max_history == 100
    assert config.monitor_interval == 1.0
    assert config.save_on_change is True
    
    # Test custom values
    config = ClipboardConfig(
        max_history=50,
        monitor_interval=0.5,
        save_on_change=False
    )
    assert config.max_history == 50
    assert config.monitor_interval == 0.5
    assert config.save_on_change is False
    
    # Test validation
    with pytest.raises(ValidationError):
        ClipboardConfig(max_history=0)  # Must be > 0
    with pytest.raises(ValidationError):
        ClipboardConfig(monitor_interval=0)  # Must be > 0


def test_system_monitor_config():
    """Test system monitor configuration."""
    config = SystemMonitorConfig()
    assert config.max_command_history == 1000
    assert config.default_log_lines == 100
    assert config.command_timeout == 5.0
    assert "journalctl" in config.allowed_commands
    
    # Test custom values
    config = SystemMonitorConfig(
        max_command_history=500,
        allowed_commands=["ls", "pwd"]
    )
    assert config.max_command_history == 500
    assert config.allowed_commands == ["ls", "pwd"]


def test_vector_db_config():
    """Test vector database configuration."""
    config = VectorDBConfig()
    assert config.collection_name == "files"
    assert config.embedding_model == "all-MiniLM-L6-v2"
    assert config.anonymized_telemetry is False
    
    # Test custom values
    config = VectorDBConfig(
        collection_name="test",
        embedding_model="custom-model"
    )
    assert config.collection_name == "test"
    assert config.embedding_model == "custom-model"


def test_server_config():
    """Test server configuration."""
    # Test defaults
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]'
    }):
        config = ServerConfig()
        assert len(config.allowed_paths) == 1
        assert config.remote_enabled is False
        assert config.log_level == "INFO"
        
        # Test environment variables
        os.environ["MCP_REMOTE_ENABLED"] = "true"
        config = ServerConfig()
        assert config.allowed_users == ["user1", "user2"]
        assert config.remote_enabled is True
        
        # Test nested config
        os.environ["MCP_CLIPBOARD__MAX_HISTORY"] = "200"
        config = ServerConfig()
        assert config.clipboard.max_history == 200


def test_config_file_operations():
    """Test configuration file operations."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]'
    }):
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
            # Create config
            config = ServerConfig(
                allowed_paths=[Path("/tmp")],
                allowed_users=["testuser"],
                clipboard=ClipboardConfig(max_history=50)
            )
            
            # Save to file
            config.save_to_file(tmp.name)
            
            # Load from file
            loaded = ServerConfig.load_from_file(tmp.name)
            assert loaded.allowed_paths == config.allowed_paths
            assert loaded.allowed_users == config.allowed_users
            assert loaded.clipboard.max_history == 50


def test_config_directory_creation():
    """Test directory creation."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]'
    }):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ServerConfig(
                clipboard=ClipboardConfig(
                    history_file=Path(tmpdir) / "clipboard/history.json"
                ),
                vector_db=VectorDBConfig(
                    persist_directory=Path(tmpdir) / "vector_db"
                )
            )
            
            # Create directories
            config.create_directories()
            
            # Verify directories were created
            assert (Path(tmpdir) / "clipboard").exists()
            assert (Path(tmpdir) / "vector_db").exists() 