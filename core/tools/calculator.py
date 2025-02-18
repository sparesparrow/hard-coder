from typing import List, Dict, Any
import logging
from ..validation.schema import SchemaValidator, ValidationResult

logger = logging.getLogger(__name__)

class CalculationError(Exception):
    """Exception raised for calculation errors."""
    pass

class Calculator:
    """Implements calculator tools."""
    
    def __init__(self):
        self._validator = SchemaValidator()
    
    async def calculate_sum(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the sum of a list of numbers."""
        try:
            # Validate arguments
            validation_result = self._validator.validate_tool_arguments(
                "calculate_sum",
                arguments
            )
            
            if not validation_result.is_valid:
                logger.error(
                    "Invalid arguments for calculate_sum",
                    extra={
                        "errors": validation_result.errors,
                        "context": validation_result.context
                    }
                )
                raise CalculationError(
                    f"Invalid arguments: {', '.join(validation_result.errors)}"
                )
            
            numbers = arguments["numbers"]
            
            # Additional runtime validation
            if not all(isinstance(n, (int, float)) for n in numbers):
                raise CalculationError("All elements must be numbers")
            
            # Perform calculation
            total = sum(numbers)
            
            # Log success
            logger.info(
                "Sum calculated successfully",
                extra={
                    "total": total,
                    "count": len(numbers)
                }
            )
            
            return {
                "result": total,
                "count": len(numbers),
                "status": "success"
            }
            
        except CalculationError:
            raise
        except Exception as e:
            logger.error(
                "Unexpected error in calculate_sum",
                exc_info=True,
                extra={"arguments": arguments}
            )
            raise CalculationError(f"Calculation failed: {str(e)}")
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for calculate_sum."""
        return {
            "name": "calculate_sum",
            "description": "Calculate the sum of a list of numbers",
            "parameters": {
                "type": "object",
                "required": ["numbers"],
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 1,
                        "description": "List of numbers to sum"
                    }
                }
            }
        } 