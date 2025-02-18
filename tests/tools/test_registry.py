import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio

from core.tools.registry import ToolRegistry, ToolMetadata
from core.tools.calculator import Calculator, CalculationError

@pytest.fixture
async def registry():
    """Create a tool registry instance for testing."""
    return ToolRegistry()

@pytest.fixture
def calculator():
    """Create a calculator instance for testing."""
    return Calculator()

@pytest.mark.asyncio
async def test_register_tool(registry, calculator):
    """Test registering a new tool."""
    # Register calculator tool
    await registry.register_tool(calculator)
    
    # Verify tool is registered
    tools = registry.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "calculate_sum"
    assert tools[0].enabled is True
    assert isinstance(tools[0].registered_at, datetime)
    assert isinstance(tools[0].last_updated, datetime)

@pytest.mark.asyncio
async def test_execute_tool(registry, calculator):
    """Test executing a registered tool."""
    # Register calculator tool
    await registry.register_tool(calculator)
    
    # Execute tool with valid arguments
    result = await registry.execute_tool(
        "calculate_sum",
        {"numbers": [1, 2, 3, 4, 5]}
    )
    assert result == {"sum": 15}
    
    # Verify metrics are updated
    metadata = registry.get_tool_metadata("calculate_sum")
    assert metadata.total_executions == 1
    assert metadata.error_count == 0
    assert metadata.average_execution_time > 0

@pytest.mark.asyncio
async def test_execute_invalid_arguments(registry, calculator):
    """Test executing a tool with invalid arguments."""
    # Register calculator tool
    await registry.register_tool(calculator)
    
    # Execute tool with invalid arguments
    with pytest.raises(ValueError) as exc_info:
        await registry.execute_tool(
            "calculate_sum",
            {"numbers": ["not", "numbers"]}
        )
    assert "Invalid arguments" in str(exc_info.value)
    
    # Verify error metrics are updated
    metadata = registry.get_tool_metadata("calculate_sum")
    assert metadata.error_count == 1

@pytest.mark.asyncio
async def test_execute_unknown_tool(registry):
    """Test executing an unknown tool."""
    with pytest.raises(ValueError) as exc_info:
        await registry.execute_tool(
            "unknown_tool",
            {"arg": "value"}
        )
    assert "Tool not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_disable_enable_tool(registry, calculator):
    """Test disabling and enabling a tool."""
    # Register calculator tool
    await registry.register_tool(calculator)
    
    # Disable tool
    await registry.disable_tool("calculate_sum")
    assert not registry.get_tool_metadata("calculate_sum").enabled
    
    # Verify tool is not listed when disabled
    assert len(registry.list_tools()) == 0
    assert len(registry.list_tools(include_disabled=True)) == 1
    
    # Try to execute disabled tool
    with pytest.raises(ValueError) as exc_info:
        await registry.execute_tool(
            "calculate_sum",
            {"numbers": [1, 2, 3]}
        )
    assert "Tool is disabled" in str(exc_info.value)
    
    # Enable tool
    await registry.enable_tool("calculate_sum")
    assert registry.get_tool_metadata("calculate_sum").enabled
    
    # Verify tool can be executed after enabling
    result = await registry.execute_tool(
        "calculate_sum",
        {"numbers": [1, 2, 3]}
    )
    assert result == {"sum": 6}

@pytest.mark.asyncio
async def test_update_existing_tool(registry, calculator):
    """Test updating an existing tool."""
    # Register calculator tool
    await registry.register_tool(calculator)
    original_registered_at = registry.get_tool_metadata("calculate_sum").registered_at
    
    # Update tool
    await registry.register_tool(calculator)
    metadata = registry.get_tool_metadata("calculate_sum")
    
    # Verify registration time is preserved but update time changes
    assert metadata.registered_at == original_registered_at
    assert metadata.last_updated > original_registered_at

@pytest.mark.asyncio
async def test_tool_schema(registry, calculator):
    """Test retrieving tool schema."""
    # Register calculator tool
    await registry.register_tool(calculator)
    
    # Get tool schema
    schema = registry.get_tool_schema("calculate_sum")
    assert schema is not None
    assert "properties" in schema
    assert "numbers" in schema["properties"]
    
    # Verify schema for unknown tool
    assert registry.get_tool_schema("unknown_tool") is None

@pytest.mark.asyncio
async def test_metrics_tracking(registry, calculator):
    """Test tracking of tool execution metrics."""
    # Register calculator tool
    await registry.register_tool(calculator)
    
    # Execute tool multiple times
    for numbers in [[1, 2], [3, 4], [5, 6]]:
        await registry.execute_tool(
            "calculate_sum",
            {"numbers": numbers}
        )
    
    # Execute with invalid arguments
    with pytest.raises(ValueError):
        await registry.execute_tool(
            "calculate_sum",
            {"numbers": ["invalid"]}
        )
    
    # Verify metrics
    metadata = registry.get_tool_metadata("calculate_sum")
    assert metadata.total_executions == 4
    assert metadata.error_count == 1
    assert metadata.average_execution_time > 0

@pytest.mark.asyncio
async def test_invalid_tool_registration(registry):
    """Test registering an invalid tool."""
    class InvalidTool:
        def get_tool_definition(self):
            return {
                "name": "invalid_tool",
                # Missing required description
                "parameters": {}
            }
    
    # Try to register invalid tool
    with pytest.raises(ValueError) as exc_info:
        await registry.register_tool(InvalidTool())
    assert "Invalid tool definition" in str(exc_info.value)
    
    # Verify tool was not registered
    assert len(registry.list_tools()) == 0

@pytest.mark.asyncio
async def test_concurrent_tool_execution(registry, calculator):
    """Test concurrent execution of tools."""
    # Register calculator tool
    await registry.register_tool(calculator)
    
    # Create multiple execution tasks
    tasks = []
    for i in range(5):
        tasks.append(
            registry.execute_tool(
                "calculate_sum",
                {"numbers": list(range(i, i+5))}
            )
        )
    
    # Execute concurrently
    results = await asyncio.gather(*tasks)
    
    # Verify results
    expected_sums = [sum(range(i, i+5)) for i in range(5)]
    for result, expected in zip(results, expected_sums):
        assert result["sum"] == expected
    
    # Verify metrics
    metadata = registry.get_tool_metadata("calculate_sum")
    assert metadata.total_executions == 5
    assert metadata.error_count == 0

@pytest.mark.asyncio
async def test_error_recovery(registry, calculator):
    """Test error recovery and metrics tracking."""
    await registry.register_tool(calculator)
    
    # Mix of valid and invalid executions
    tasks = [
        registry.execute_tool("calculate_sum", {"numbers": [1, 2, 3]}),
        registry.execute_tool("calculate_sum", {"numbers": ["invalid"]}),
        registry.execute_tool("calculate_sum", {"numbers": [4, 5, 6]})
    ]
    
    results = []
    for task in tasks:
        try:
            result = await task
            results.append(("success", result))
        except Exception as e:
            results.append(("error", str(e)))
    
    # Verify results
    assert len(results) == 3
    assert results[0][0] == "success"
    assert results[1][0] == "error"
    assert results[2][0] == "success"
    
    # Verify metrics
    metadata = registry.get_tool_metadata("calculate_sum")
    assert metadata.total_executions == 3
    assert metadata.error_count == 1

@pytest.mark.asyncio
async def test_tool_lifecycle(registry, calculator):
    """Test complete tool lifecycle including registration, update, and removal."""
    # Initial registration
    await registry.register_tool(calculator)
    
    # Execute tool
    result = await registry.execute_tool(
        "calculate_sum",
        {"numbers": [1, 2, 3]}
    )
    assert result["sum"] == 6
    
    # Disable tool
    await registry.disable_tool("calculate_sum")
    with pytest.raises(ValueError) as exc_info:
        await registry.execute_tool(
            "calculate_sum",
            {"numbers": [1, 2, 3]}
        )
    assert "Tool is disabled" in str(exc_info.value)
    
    # Enable tool
    await registry.enable_tool("calculate_sum")
    result = await registry.execute_tool(
        "calculate_sum",
        {"numbers": [4, 5, 6]}
    )
    assert result["sum"] == 15
    
    # Update tool (re-register)
    original_metadata = registry.get_tool_metadata("calculate_sum")
    await registry.register_tool(calculator)
    updated_metadata = registry.get_tool_metadata("calculate_sum")
    
    assert updated_metadata.registered_at == original_metadata.registered_at
    assert updated_metadata.last_updated > original_metadata.last_updated

@pytest.mark.asyncio
async def test_tool_validation(registry):
    """Test tool validation during registration and execution."""
    class InvalidTool:
        def get_tool_definition(self):
            return {
                "name": "invalid_tool",
                "description": "Invalid tool",
                "parameters": {
                    "type": "invalid"  # Invalid schema
                }
            }
    
    # Try to register invalid tool
    with pytest.raises(ValueError) as exc_info:
        await registry.register_tool(InvalidTool())
    assert "Invalid tool definition" in str(exc_info.value)
    
    # Try to register tool without required method
    class IncompleteImplementation:
        pass
    
    with pytest.raises(ValueError) as exc_info:
        await registry.register_tool(IncompleteImplementation())
    assert "must provide get_tool_definition method" in str(exc_info.value)

@pytest.mark.asyncio
async def test_metrics_accuracy(registry, calculator):
    """Test accuracy of tool execution metrics."""
    await registry.register_tool(calculator)
    
    # Execute tool multiple times with varying delays
    execution_times = []
    
    for i in range(3):
        start_time = datetime.utcnow()
        await registry.execute_tool(
            "calculate_sum",
            {"numbers": list(range(i*1000))}  # Increase workload
        )
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        execution_times.append(execution_time)
    
    # Verify metrics
    metadata = registry.get_tool_metadata("calculate_sum")
    assert metadata.total_executions == 3
    assert metadata.error_count == 0
    
    # Verify average execution time is within reasonable range
    expected_average = sum(execution_times) / len(execution_times)
    assert abs(metadata.average_execution_time - expected_average) < 0.1

@pytest.mark.asyncio
async def test_concurrent_registration(registry):
    """Test concurrent tool registration and updates."""
    class TestTool:
        def __init__(self, name: str):
            self.name = name
        
        def get_tool_definition(self):
            return {
                "name": self.name,
                "description": f"Test tool {self.name}",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
    
    # Create multiple registration tasks
    tools = [TestTool(f"tool_{i}") for i in range(5)]
    registration_tasks = [
        registry.register_tool(tool)
        for tool in tools
    ]
    
    # Register tools concurrently
    await asyncio.gather(*registration_tasks)
    
    # Verify all tools are registered
    registered_tools = registry.list_tools()
    assert len(registered_tools) == 5
    assert all(
        any(t.name == f"tool_{i}" for t in registered_tools)
        for i in range(5)
    )

@pytest.mark.asyncio
async def test_tool_listing_and_filtering(registry, calculator):
    """Test tool listing with various filters."""
    # Register calculator
    await registry.register_tool(calculator)
    
    # Register additional test tools
    class TestTool:
        def __init__(self, name: str, enabled: bool = True):
            self.name = name
            self._enabled = enabled
        
        def get_tool_definition(self):
            return {
                "name": self.name,
                "description": f"Test tool {self.name}",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
    
    await registry.register_tool(TestTool("test_tool_1"))
    await registry.register_tool(TestTool("test_tool_2"))
    
    # Disable one tool
    await registry.disable_tool("test_tool_1")
    
    # Test listing all tools
    all_tools = registry.list_tools(include_disabled=True)
    assert len(all_tools) == 3
    
    # Test listing only enabled tools
    enabled_tools = registry.list_tools(include_disabled=False)
    assert len(enabled_tools) == 2
    assert all(tool.enabled for tool in enabled_tools)
    
    # Verify tool metadata
    for tool in all_tools:
        assert isinstance(tool.registered_at, datetime)
        assert isinstance(tool.last_updated, datetime)
        assert isinstance(tool.error_count, int)
        assert isinstance(tool.average_execution_time, float) 