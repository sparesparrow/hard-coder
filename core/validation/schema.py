from typing import Dict, Any, Optional, List
import jsonschema
from jsonschema import validate, ValidationError
import logging
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    """Model for validation results."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[Dict[str, Any]] = None

class SchemaValidator:
    """Handles JSON schema validation for tools and their arguments."""
    
    def __init__(self):
        self._tool_schemas: Dict[str, Dict[str, Any]] = {}
        self._initialize_base_schemas()
    
    def _initialize_base_schemas(self) -> None:
        """Initialize base schemas for common tool patterns."""
        self._tool_schemas["base_tool"] = {
            "type": "object",
            "required": ["name", "description", "parameters"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "required": {"type": "array", "items": {"type": "string"}},
                        "properties": {"type": "object"}
                    },
                    "required": ["type", "properties"]
                }
            }
        }
        
        # Add schema for calculate_sum tool
        self._tool_schemas["calculate_sum"] = {
            "type": "object",
            "required": ["numbers"],
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 1
                }
            }
        }
    
    def register_tool_schema(self, tool_name: str, schema: Dict[str, Any]) -> None:
        """Register a new tool schema."""
        try:
            # Validate the schema itself
            jsonschema.Draft7Validator.check_schema(schema)
            self._tool_schemas[tool_name] = schema
            logger.info(f"Registered schema for tool: {tool_name}")
        except Exception as e:
            logger.error(f"Error registering schema for {tool_name}: {str(e)}")
            raise ValueError(f"Invalid schema for tool {tool_name}: {str(e)}")
    
    def validate_tool_definition(self, tool_def: Dict[str, Any]) -> ValidationResult:
        """Validate a tool definition against the base tool schema."""
        try:
            validate(instance=tool_def, schema=self._tool_schemas["base_tool"])
            return ValidationResult(
                is_valid=True,
                context={"tool_name": tool_def.get("name")}
            )
        except ValidationError as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(e)],
                context={
                    "tool_name": tool_def.get("name"),
                    "validation_path": list(e.path)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error validating tool definition: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Unexpected validation error: {str(e)}"],
                context={"tool_name": tool_def.get("name")}
            )
    
    def validate_tool_arguments(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ValidationResult:
        """Validate tool arguments against the tool's schema."""
        if tool_name not in self._tool_schemas:
            return ValidationResult(
                is_valid=False,
                errors=[f"No schema registered for tool: {tool_name}"],
                context={"tool_name": tool_name}
            )
            
        try:
            validate(instance=arguments, schema=self._tool_schemas[tool_name])
            return ValidationResult(
                is_valid=True,
                context={"tool_name": tool_name}
            )
        except ValidationError as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(e)],
                context={
                    "tool_name": tool_name,
                    "validation_path": list(e.path)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error validating {tool_name} arguments: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Unexpected validation error: {str(e)}"],
                context={"tool_name": tool_name}
            )
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a specific tool."""
        return self._tool_schemas.get(tool_name)
    
    def list_registered_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return [name for name in self._tool_schemas.keys() if name != "base_tool"] 