import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from mcp_system_context.server import SystemContextServer
from mcp_system_context.config import ServerConfig

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
async def server(temp_dir):
    """Create a server instance for testing."""
    with patch.dict(os.environ, {
        'MCP_ALLOWED_USERS': '["user1", "user2"]'
    }):
        # Mock the clipboard monitor to prevent event loop issues
        with patch('mcp_system_context.server.SystemContextServer._start_clipboard_monitor', MagicMock()):
            # Mock the run method to prevent event loop issues
            with patch('mcp_system_context.server.SystemContextServer.run', AsyncMock()):
                server = SystemContextServer([str(temp_dir)])
                yield server
                # Clean up
                await server.cleanup()

@pytest.mark.asyncio
async def test_server_initialization(server):
    """Test server initialization."""
    assert server.allowed_paths == [str(server.allowed_paths[0])]
    assert server.auth_manager is not None
    assert server.file_manager is not None
    assert server.history_manager is not None
    assert server.clipboard_manager is not None
    assert server.system_monitor is not None
    assert server.vector_manager is not None

@pytest.mark.asyncio
async def test_server_resources(server):
    """Test server resource initialization."""
    # Test auth manager
    assert server.auth_manager.validate_path("/tmp/test") is True
    assert server.auth_manager.validate_path("/root/test") is False

    # Test file manager
    test_file = Path(server.allowed_paths[0]) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test content")
    
    entries = server.file_manager.list_directory(server.allowed_paths[0])
    assert "test.txt" in entries

    # Test history manager
    history = server.history_manager.get_shell_history()
    assert isinstance(history, list)

    # Test clipboard manager
    assert server.clipboard_manager is not None

    # Test system monitor
    system_info = server.system_monitor.get_system_info()
    assert isinstance(system_info, dict)
    assert "cpu_percent" in system_info
    assert "memory_percent" in system_info

    # Test vector manager
    assert server.vector_manager is not None

@pytest.fixture
def vector_manager(server):
    """Create a vector manager instance for testing."""
    return server.vector_manager

@pytest.mark.asyncio
async def test_vector_manager(vector_manager):
    """Test vector manager operations."""
    # Test adding and searching documents
    docs = ["Hello world", "Testing vector search", "Another document"]
    metadata = [{"source": "test", "type": "document", "id": str(i)} for i, _ in enumerate(docs)]
    collection_metadata = {"description": "Test collection", "version": "1.0"}
    
    # Create collection with metadata
    collection = vector_manager.get_or_create_collection("test", metadata=collection_metadata)
    
    # Add documents with metadata
    vector_manager.add_documents("test", docs, metadata)

    # Test searching
    results = vector_manager.search("test", "world", limit=1)
    assert len(results) == 1
    assert "Hello world" in results[0]

    # Test getting all documents
    all_docs = vector_manager.get_documents("test")
    assert len(all_docs) == 3 
    