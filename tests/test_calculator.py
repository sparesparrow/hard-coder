import pytest
from core.tools.calculator import Calculator, CalculationError

@pytest.fixture
def calculator():
    """Create a calculator instance for testing."""
    return Calculator()

@pytest.mark.asyncio
async def test_calculate_sum_valid(calculator):
    """Test calculate_sum with valid arguments."""
    # Test integers
    result = await calculator.calculate_sum({"numbers": [1, 2, 3, 4, 5]})
    assert result["result"] == 15
    assert result["count"] == 5
    assert result["status"] == "success"
    
    # Test floats
    result = await calculator.calculate_sum({"numbers": [1.5, 2.5, 3.5]})
    assert result["result"] == 7.5
    assert result["count"] == 3
    assert result["status"] == "success"
    
    # Test mixed numbers
    result = await calculator.calculate_sum({"numbers": [1, 2.5, 3, 4.5]})
    assert result["result"] == 11.0
    assert result["count"] == 4
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_calculate_sum_invalid_arguments(calculator):
    """Test calculate_sum with invalid arguments."""
    # Empty array
    with pytest.raises(CalculationError) as exc_info:
        await calculator.calculate_sum({"numbers": []})
    assert "Invalid arguments" in str(exc_info.value)
    
    # Missing required field
    with pytest.raises(CalculationError) as exc_info:
        await calculator.calculate_sum({})
    assert "Invalid arguments" in str(exc_info.value)
    
    # Wrong type (strings instead of numbers)
    with pytest.raises(CalculationError) as exc_info:
        await calculator.calculate_sum({"numbers": ["1", "2", "3"]})
    assert "Invalid arguments" in str(exc_info.value)
    
    # Mixed valid and invalid types
    with pytest.raises(CalculationError) as exc_info:
        await calculator.calculate_sum({"numbers": [1, "2", 3]})
    assert "All elements must be numbers" in str(exc_info.value)

def test_tool_definition(calculator):
    """Test the tool definition is valid."""
    definition = calculator.get_tool_definition()
    
    assert definition["name"] == "calculate_sum"
    assert "description" in definition
    assert "parameters" in definition
    
    parameters = definition["parameters"]
    assert parameters["type"] == "object"
    assert "numbers" in parameters["properties"]
    assert parameters["required"] == ["numbers"]
    
    numbers_prop = parameters["properties"]["numbers"]
    assert numbers_prop["type"] == "array"
    assert numbers_prop["items"]["type"] == "number"
    assert numbers_prop["minItems"] == 1 