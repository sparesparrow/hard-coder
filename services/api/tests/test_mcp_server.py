import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from ..mcp.server import (
    MCPServer,
    Message,
    Tool,
    MCPError,
    ToolError,
    ValidationError
)
from ..core.container import ServiceContainer
from ..interfaces.service_interfaces import (
    AIServiceInterface,
    AudioServiceInterface,
    StateManagerInterface,
    MetricsCollectorInterface
)

@pytest.fixture
def mock_container():
    container = Mock(spec=ServiceContainer)
    container.get = AsyncMock()
    return container

@pytest.fixture
async def mcp_server(mock_container):
    server = MCPServer(mock_container)
    yield server

@pytest.mark.asyncio
async def test_register_tool(mcp_server):
    """Test tool registration."""
    tool = Tool(
        name="test/tool",
        description="Test tool",
        input_schema={
            "type": "object",
            "properties": {
                "test": {"type": "string"}
            }
        }
    )
    
    mcp_server.register_tool(tool)
    assert "test/tool" in mcp_server.tools
    assert mcp_server.tools["test/tool"] == tool

@pytest.mark.asyncio
async def test_handle_tools_list(mcp_server):
    """Test tools/list request handling."""
    message = Message(
        id="test-id",
        method="tools/list",
        params={}
    )
    
    response = await mcp_server.handle_message(message)
    assert "tools" in response
    assert isinstance(response["tools"], list)
    assert len(response["tools"]) > 0  # Default tools should be registered

@pytest.mark.asyncio
async def test_handle_invalid_method(mcp_server):
    """Test handling of invalid method."""
    message = Message(
        id="test-id",
        method="invalid/method",
        params={}
    )
    
    response = await mcp_server.handle_message(message)
    assert "error" in response
    assert response["error"]["code"] == "invalid_method"

@pytest.mark.asyncio
async def test_handle_ai_tool(mcp_server, mock_container):
    """Test AI tool execution."""
    # Mock AI service
    mock_ai_service = AsyncMock()
    mock_ai_service.stream_response = AsyncMock(return_value="AI response")
    mock_container.get.return_value = mock_ai_service
    
    message = Message(
        id="test-id",
        method="tools/call",
        params={
            "name": "ai/generate",
            "arguments": {
                "prompt": "Test prompt",
                "context": {}
            }
        }
    )
    
    response = await mcp_server.handle_message(message)
    assert "result" in response
    assert response["result"] == "AI response"
    mock_container.get.assert_called_once_with(AIServiceInterface)

@pytest.mark.asyncio
async def test_handle_audio_tool(mcp_server, mock_container):
    """Test audio tool execution."""
    # Mock audio service
    mock_audio_service = AsyncMock()
    mock_audio_service.stream_audio = AsyncMock(return_value=b"audio data")
    mock_container.get.return_value = mock_audio_service
    
    message = Message(
        id="test-id",
        method="tools/call",
        params={
            "name": "audio/synthesize",
            "arguments": {
                "text": "Test text",
                "voice_id": "test-voice"
            }
        }
    )
    
    response = await mcp_server.handle_message(message)
    assert "result" in response
    assert response["result"] == b"audio data"
    mock_container.get.assert_called_once_with(AudioServiceInterface)

@pytest.mark.asyncio
async def test_handle_system_metrics(mcp_server):
    """Test system metrics tool."""
    with patch("psutil.cpu_percent") as mock_cpu, \
         patch("psutil.virtual_memory") as mock_memory:
        
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(
            total=16000000000,
            available=8000000000,
            percent=50.0
        )
        
        message = Message(
            id="test-id",
            method="tools/call",
            params={
                "name": "system/metrics",
                "arguments": {
                    "metrics": ["cpu", "memory"]
                }
            }
        )
        
        response = await mcp_server.handle_message(message)
        assert "result" in response
        assert "cpu" in response["result"]
        assert "memory" in response["result"]
        assert response["result"]["cpu"]["percent"] == 50.0
        assert response["result"]["memory"]["percent"] == 50.0

@pytest.mark.asyncio
async def test_handle_system_processes(mcp_server):
    """Test system processes tool."""
    mock_process = Mock(
        info={
            "pid": 1,
            "name": "test-process",
            "cpu_percent": 10.0,
            "memory_percent": 5.0
        }
    )
    
    with patch("psutil.process_iter", return_value=[mock_process]):
        message = Message(
            id="test-id",
            method="tools/call",
            params={
                "name": "system/processes",
                "arguments": {
                    "filters": {
                        "cpu_percent": 5.0
                    }
                }
            }
        )
        
        response = await mcp_server.handle_message(message)
        assert "result" in response
        assert isinstance(response["result"], list)
        assert len(response["result"]) == 1
        assert response["result"][0]["name"] == "test-process"

@pytest.mark.asyncio
async def test_handle_state_management(mcp_server, mock_container):
    """Test state management tools."""
    # Mock state manager
    mock_state_manager = AsyncMock()
    mock_state_manager.get_state = AsyncMock(return_value={"test": "value"})
    mock_state_manager.set_state = AsyncMock()
    mock_container.get.return_value = mock_state_manager
    
    # Test get state
    get_message = Message(
        id="test-id",
        method="tools/call",
        params={
            "name": "state/get",
            "arguments": {
                "key": "test-key"
            }
        }
    )
    
    response = await mcp_server.handle_message(get_message)
    assert "result" in response
    assert response["result"] == {"test": "value"}
    
    # Test set state
    set_message = Message(
        id="test-id",
        method="tools/call",
        params={
            "name": "state/set",
            "arguments": {
                "key": "test-key",
                "value": {"test": "new-value"},
                "ttl": 3600
            }
        }
    )
    
    response = await mcp_server.handle_message(set_message)
    assert "result" in response
    mock_state_manager.set_state.assert_called_once()

@pytest.mark.asyncio
async def test_handle_metrics_collection(mcp_server, mock_container):
    """Test metrics collection tool."""
    # Mock metrics collector
    mock_metrics = AsyncMock()
    mock_metrics.get_metrics = AsyncMock(return_value={
        "latency": {
            "p50": 100,
            "p95": 200,
            "p99": 300
        },
        "errors": {
            "count": 5,
            "types": {"validation": 3, "timeout": 2}
        }
    })
    mock_container.get.return_value = mock_metrics
    
    message = Message(
        id="test-id",
        method="tools/call",
        params={
            "name": "metrics/get",
            "arguments": {
                "start_time": "2024-03-01T00:00:00Z",
                "end_time": "2024-03-02T00:00:00Z",
                "metric_types": ["latency", "errors"]
            }
        }
    )
    
    response = await mcp_server.handle_message(message)
    assert "result" in response
    assert "latency" in response["result"]
    assert "errors" in response["result"]
    mock_container.get.assert_called_once_with(MetricsCollectorInterface)

@pytest.mark.asyncio
async def test_handle_streaming_response(mcp_server, mock_container):
    """Test handling of streaming responses."""
    # Mock streaming service
    async def mock_stream():
        for chunk in ["chunk1", "chunk2", "chunk3"]:
            yield chunk
    
    mock_service = AsyncMock()
    mock_service.stream_response = mock_stream
    mock_container.get.return_value = mock_service
    
    message = Message(
        id="test-id",
        method="tools/call",
        params={
            "name": "ai/generate",
            "arguments": {
                "prompt": "Test prompt",
                "context": {}
            }
        }
    )
    
    response = await mcp_server.handle_message(message)
    assert "result" in response
    assert response["result"] == ["chunk1", "chunk2", "chunk3"]

@pytest.mark.asyncio
async def test_handle_tool_error(mcp_server, mock_container):
    """Test tool error handling."""
    # Mock failing service
    mock_service = AsyncMock()
    mock_service.stream_response = AsyncMock(side_effect=Exception("Test error"))
    mock_container.get.return_value = mock_service
    
    message = Message(
        id="test-id",
        method="tools/call",
        params={
            "name": "ai/generate",
            "arguments": {
                "prompt": "Test prompt",
                "context": {}
            }
        }
    )
    
    response = await mcp_server.handle_message(message)
    assert "error" in response
    assert response["error"]["code"] == "execution_failed"
    assert "Test error" in response["error"]["message"]

@pytest.mark.asyncio
async def test_handle_system_tools_enhanced(mcp_server):
    """Test enhanced system tools with SystemMonitor integration."""
    # Mock SystemMonitor methods
    with patch.object(mcp_server.system_monitor, "get_process_list") as mock_process_list, \
         patch.object(mcp_server.system_monitor, "get_network_connections") as mock_connections, \
         patch.object(mcp_server.system_monitor, "get_network_routes") as mock_routes, \
         patch.object(mcp_server.system_monitor, "get_systemd_logs") as mock_logs, \
         patch.object(mcp_server.system_monitor, "get_system_info") as mock_info, \
         patch.object(mcp_server.system_monitor, "get_command_history") as mock_history:
        
        # Setup mock returns
        mock_process_list.return_value = AsyncMock(
            dict=lambda: {"command": "ps", "output": "process data"}
        )()
        mock_connections.return_value = [
            NetworkConnection(
                protocol="tcp",
                local_address="127.0.0.1:80",
                remote_address="",
                state="LISTEN"
            )
        ]
        mock_routes.return_value = [
            NetworkRoute(
                destination="default",
                gateway="192.168.1.1",
                interface="eth0"
            )
        ]
        mock_logs.return_value = AsyncMock(
            dict=lambda: {"command": "journalctl", "output": "log data"}
        )()
        mock_info.return_value = {
            "hostname": "test-host",
            "kernel": "test-kernel"
        }
        mock_history.return_value = [
            SystemCommand(
                command="test",
                output="test output",
                timestamp=datetime.now(),
                exit_code=0
            )
        ]
        
        # Test raw process list
        message = Message(
            id="test-id",
            method="tools/call",
            params={
                "name": "system/processes",
                "arguments": {"raw": True}
            }
        )
        response = await mcp_server.handle_message(message)
        assert "result" in response
        assert response["result"]["command"] == "ps"
        
        # Test network info
        message.params["name"] = "system/network"
        response = await mcp_server.handle_message(message)
        assert "result" in response
        assert "connections" in response["result"]
        assert "routes" in response["result"]
        assert "history" in response["result"]
        assert len(response["result"]["connections"]) == 1
        assert response["result"]["connections"][0]["protocol"] == "tcp"
        
        # Test system logs
        message.params.update({
            "name": "system/logs",
            "arguments": {"unit": "test.service", "since": "1h"}
        })
        response = await mcp_server.handle_message(message)
        assert "result" in response
        assert response["result"]["command"] == "journalctl"
        
        # Test system info
        message.params["name"] = "system/info"
        response = await mcp_server.handle_message(message)
        assert "result" in response
        assert "hostname" in response["result"]
        assert "metrics" in response["result"]
        assert "command_history" in response["result"]

@pytest.mark.asyncio
async def test_handle_system_tool_error(mcp_server):
    """Test system tool error handling."""
    with patch.object(mcp_server.system_monitor, "get_process_list") as mock_process:
        mock_process.side_effect = Exception("Command failed")
        
        message = Message(
            id="test-id",
            method="tools/call",
            params={
                "name": "system/processes",
                "arguments": {"raw": True}
            }
        )
        
        response = await mcp_server.handle_message(message)
        assert "error" in response
        assert response["error"]["code"] == "system_tool_error"
        assert "Command failed" in response["error"]["message"] 