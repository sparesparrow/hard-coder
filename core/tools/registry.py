from typing import Dict, Any, Optional, List, Type
import logging
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field

from ..validation.schema import SchemaValidator, ValidationResult
from .calculator import Calculator, CalculationError

logger = logging.getLogger(__name__)

class ToolMetadata(BaseModel):
    """Metadata for registered tools."""
    name: str
    description: str
    implementation: Any
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    enabled: bool = True
    error_count: int = 0
    average_execution_time: float = 0.0
    total_executions: int = 0

class ToolRegistry:
    """Registry for managing dynamic tools."""
    
    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}
        self._validator = SchemaValidator()
        self._lock = asyncio.Lock()
        self._initialize_default_tools()
    
    def _initialize_default_tools(self) -> None:
        """Initialize default tools."""
        try:
            calculator = Calculator()
            self.register_tool(calculator)
        except Exception as e:
            logger.error(f"Error initializing default tools: {str(e)}")
    
    async def register_tool(self, implementation: Any) -> None:
        """Register a new tool."""
        try:
            # Get tool definition
            if not hasattr(implementation, "get_tool_definition"):
                raise ValueError("Tool implementation must provide get_tool_definition method")
                
            definition = implementation.get_tool_definition()
            
            # Validate tool definition
            validation_result = self._validator.validate_tool_definition(definition)
            if not validation_result.is_valid:
                raise ValueError(
                    f"Invalid tool definition: {', '.join(validation_result.errors)}"
                )
            
            tool_name = definition["name"]
            
            async with self._lock:
                if tool_name in self._tools:
                    # Update existing tool
                    metadata = self._tools[tool_name]
                    metadata.implementation = implementation
                    metadata.description = definition["description"]
                    metadata.last_updated = datetime.utcnow()
                    logger.info(f"Updated existing tool: {tool_name}")
                else:
                    # Register new tool
                    self._tools[tool_name] = ToolMetadata(
                        name=tool_name,
                        description=definition["description"],
                        implementation=implementation
                    )
                    logger.info(f"Registered new tool: {tool_name}")
                
                # Register tool schema
                self._validator.register_tool_schema(
                    tool_name,
                    definition["parameters"]
                )
                
        except Exception as e:
            logger.error(f"Error registering tool: {str(e)}")
            raise
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a registered tool."""
        start_time = datetime.utcnow()
        
        try:
            # Get tool metadata
            metadata = self._tools.get(tool_name)
            if not metadata:
                raise ValueError(f"Tool not found: {tool_name}")
            
            if not metadata.enabled:
                raise ValueError(f"Tool is disabled: {tool_name}")
            
            # Validate arguments
            validation_result = self._validator.validate_tool_arguments(
                tool_name,
                arguments
            )
            if not validation_result.is_valid:
                raise ValueError(
                    f"Invalid arguments for {tool_name}: {', '.join(validation_result.errors)}"
                )
            
            # Execute tool
            implementation = metadata.implementation
            if not hasattr(implementation, tool_name):
                raise ValueError(f"Tool implementation missing method: {tool_name}")
                
            result = await getattr(implementation, tool_name)(arguments)
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(metadata, execution_time, success=True)
            
            return result
            
        except Exception as e:
            if tool_name in self._tools:
                await self._update_metrics(
                    self._tools[tool_name],
                    (datetime.utcnow() - start_time).total_seconds(),
                    success=False
                )
            logger.error(
                f"Error executing tool {tool_name}",
                exc_info=True,
                extra={"arguments": arguments}
            )
            raise
    
    async def _update_metrics(
        self,
        metadata: ToolMetadata,
        execution_time: float,
        success: bool
    ) -> None:
        """Update tool execution metrics."""
        async with self._lock:
            if not success:
                metadata.error_count += 1
            
            # Update average execution time
            total_time = (metadata.average_execution_time * metadata.total_executions)
            metadata.total_executions += 1
            metadata.average_execution_time = (
                total_time + execution_time
            ) / metadata.total_executions
    
    async def disable_tool(self, tool_name: str) -> None:
        """Disable a tool."""
        async with self._lock:
            if tool_name in self._tools:
                self._tools[tool_name].enabled = False
                logger.info(f"Disabled tool: {tool_name}")
            else:
                raise ValueError(f"Tool not found: {tool_name}")
    
    async def enable_tool(self, tool_name: str) -> None:
        """Enable a tool."""
        async with self._lock:
            if tool_name in self._tools:
                self._tools[tool_name].enabled = True
                logger.info(f"Enabled tool: {tool_name}")
            else:
                raise ValueError(f"Tool not found: {tool_name}")
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self._tools.get(tool_name)
    
    def list_tools(self, include_disabled: bool = False) -> List[ToolMetadata]:
        """List all registered tools."""
        if include_disabled:
            return list(self._tools.values())
        return [
            metadata for metadata in self._tools.values()
            if metadata.enabled
        ]
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a specific tool."""
        return self._validator.get_tool_schema(tool_name) 