import pytest
from core.validation.schema import SchemaValidator, ValidationResult

@pytest.fixture
def validator():
    """Create a schema validator instance for testing."""
    return SchemaValidator()

def test_base_tool_schema_validation(validator):
    """Test validation of tool definitions against base schema."""
    # Valid tool definition
    valid_tool = {
        "name": "test_tool",
        "description": "A test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            }
        }
    }
    result = validator.validate_tool_definition(valid_tool)
    assert result.is_valid
    assert not result.errors
    
    # Invalid tool definition (missing required field)
    invalid_tool = {
        "name": "test_tool",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
    result = validator.validate_tool_definition(invalid_tool)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert "description" in result.errors[0]

def test_calculate_sum_validation(validator):
    """Test validation of calculate_sum tool arguments."""
    # Valid arguments
    valid_args = {
        "numbers": [1, 2, 3, 4, 5]
    }
    result = validator.validate_tool_arguments("calculate_sum", valid_args)
    assert result.is_valid
    assert not result.errors
    
    # Invalid arguments (empty array)
    invalid_args = {
        "numbers": []
    }
    result = validator.validate_tool_arguments("calculate_sum", invalid_args)
    assert not result.is_valid
    assert len(result.errors) > 0
    
    # Invalid arguments (wrong type)
    invalid_args = {
        "numbers": ["1", "2", "3"]
    }
    result = validator.validate_tool_arguments("calculate_sum", invalid_args)
    assert not result.is_valid
    assert len(result.errors) > 0

def test_schema_registration(validator):
    """Test registration of new tool schemas."""
    # Valid schema
    new_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"}
        }
    }
    validator.register_tool_schema("test_tool", new_schema)
    assert "test_tool" in validator.list_registered_tools()
    
    # Invalid schema
    invalid_schema = {
        "type": "invalid_type",
        "properties": {}
    }
    with pytest.raises(ValueError):
        validator.register_tool_schema("invalid_tool", invalid_schema)

def test_tool_listing(validator):
    """Test listing of registered tools."""
    tools = validator.list_registered_tools()
    assert "calculate_sum" in tools
    assert "base_tool" not in tools

def test_unknown_tool_validation(validator):
    """Test validation of arguments for unknown tool."""
    result = validator.validate_tool_arguments(
        "unknown_tool",
        {"some": "args"}
    )
    assert not result.is_valid
    assert "No schema registered" in result.errors[0]

def test_validation_result_model():
    """Test ValidationResult model functionality."""
    result = ValidationResult(
        is_valid=False,
        errors=["Test error"],
        context={"test": "context"}
    )
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.context["test"] == "context"
    assert result.timestamp is not None 