import logging
from typing import Dict, Any, Optional, List, Type
import asyncio
from datetime import datetime
import psutil
import json
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

from ..core.container import ServiceContainer, get_container
from ..interfaces.service_interfaces import (
    AIServiceInterface,
    AudioServiceInterface,
    WorkflowServiceInterface,
    MetricsCollectorInterface,
    StateManagerInterface
)

# Import the SystemMonitor
import sys
sys.path.append("/home/sparrow/projects/hard-coder/Projects/system-context")
from mcp_system_context.system.monitor import SystemMonitor, SystemCommand, NetworkConnection, NetworkRoute

logger = logging.getLogger(__name__)

class MCPError(Exception):
    """Base class for MCP-related errors."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

class ToolError(MCPError):
    """Raised when tool execution fails."""
    pass

class ValidationError(MCPError):
    """Raised when message validation fails."""
    pass

class Message(BaseModel):
    """MCP message model."""
    id: str = Field(..., description="Unique message identifier")
    method: str = Field(..., description="Message method/type")
    params: Dict[str, Any] = Field(default_factory=dict, description="Message parameters")

class Tool(BaseModel):
    """MCP tool definition."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for tool input")
    service_interface: Optional[Type] = Field(None, description="Service interface this tool uses")
    method_name: Optional[str] = Field(None, description="Service method to call")

class MCPServer:
    """Model Context Protocol server implementation."""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
        self.tools: Dict[str, Tool] = {}
        self.system_monitor = SystemMonitor()
        self._register_default_tools()
        logger.info("Initialized MCP server")

    def _register_default_tools(self) -> None:
        """Register default tools from our services."""
        # AI Service tools
        self.register_tool(Tool(
            name="ai/generate",
            description="Generate AI response with optional tools",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "context": {"type": "object"},
                    "tools": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["prompt", "context"]
            },
            service_interface=AIServiceInterface,
            method_name="stream_response"
        ))

        # Audio Service tools
        self.register_tool(Tool(
            name="audio/synthesize",
            description="Convert text to speech",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "voice_id": {"type": "string"},
                    "settings": {"type": "object"}
                },
                "required": ["text", "voice_id"]
            },
            service_interface=AudioServiceInterface,
            method_name="stream_audio"
        ))

        # System Monitoring tools
        self.register_tool(Tool(
            name="system/metrics",
            description="Get system performance metrics",
            input_schema={
                "type": "object",
                "properties": {
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of metrics to collect (cpu, memory, disk, network)"
                    }
                }
            }
        ))

        self.register_tool(Tool(
            name="system/processes",
            description="List system processes with optional filters",
            input_schema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "cpu_percent": {"type": "number"},
                            "memory_percent": {"type": "number"}
                        }
                    }
                }
            }
        ))

        # State Management tools
        self.register_tool(Tool(
            name="state/get",
            description="Get state value by key",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"}
                },
                "required": ["key"]
            },
            service_interface=StateManagerInterface,
            method_name="get_state"
        ))

        self.register_tool(Tool(
            name="state/set",
            description="Set state value with optional TTL",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "object"},
                    "ttl": {"type": "number"}
                },
                "required": ["key", "value"]
            },
            service_interface=StateManagerInterface,
            method_name="set_state"
        ))

        # Metrics Collection tools
        self.register_tool(Tool(
            name="metrics/get",
            description="Get collected metrics for specified time period",
            input_schema={
                "type": "object",
                "properties": {
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "metric_types": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["start_time", "end_time"]
            },
            service_interface=MetricsCollectorInterface,
            method_name="get_metrics"
        ))

        # Enhanced system monitoring tools
        self.register_tool(Tool(
            name="system/network",
            description="Get detailed network information including connections and routes",
            input_schema={
                "type": "object",
                "properties": {}
            }
        ))

        self.register_tool(Tool(
            name="system/logs",
            description="Get system logs with optional unit filter",
            input_schema={
                "type": "object",
                "properties": {
                    "unit": {"type": "string"},
                    "since": {"type": "string", "default": "1h"}
                }
            }
        ))

        self.register_tool(Tool(
            name="system/info",
            description="Get comprehensive system information",
            input_schema={
                "type": "object",
                "properties": {}
            }
        ))

    def register_tool(self, tool: Tool) -> None:
        """Register a new tool."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    async def handle_message(self, message: Message) -> Dict[str, Any]:
        """Handle incoming MCP message."""
        try:
            if message.method == "tools/list":
                return await self._handle_tools_list(message)
            elif message.method == "tools/call":
                return await self._handle_tool_call(message)
            else:
                raise ValidationError(
                    "invalid_method",
                    f"Unsupported method: {message.method}"
                )
        except MCPError as e:
            return {
                "error": {
                    "code": e.code,
                    "message": e.message
                }
            }
        except Exception as e:
            logger.error(f"Internal error handling message: {str(e)}")
            return {
                "error": {
                    "code": "internal_error",
                    "message": str(e)
                }
            }

    async def _handle_tools_list(self, message: Message) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema
                }
                for tool in self.tools.values()
            ]
        }

    async def _handle_tool_call(self, message: Message) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = message.params.get("name")
        if not tool_name:
            raise ValidationError("missing_tool_name", "Tool name is required")

        tool = self.tools.get(tool_name)
        if not tool:
            raise ValidationError("unknown_tool", f"Unknown tool: {tool_name}")

        try:
            if tool.service_interface and tool.method_name:
                # Handle service-based tools
                service = await self.container.get(tool.service_interface)
                method = getattr(service, tool.method_name)
                result = await method(**message.params.get("arguments", {}))
            else:
                # Handle system tools
                result = await self._handle_system_tool(tool_name, message.params.get("arguments", {}))

            # Handle streaming results
            if hasattr(result, "__aiter__"):
                chunks = []
                async for chunk in result:
                    chunks.append(chunk)
                result = chunks

            return {"result": result}

        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            raise ToolError("execution_failed", str(e))

    async def _handle_system_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Handle system-specific tools."""
        try:
            if tool_name == "system/metrics":
                return await self._collect_system_metrics(arguments.get("metrics", ["cpu", "memory"]))
            elif tool_name == "system/processes":
                if arguments.get("raw", False):
                    result = await self.system_monitor.get_process_list()
                    return result.dict()
                return await self._list_system_processes(arguments.get("filters", {}))
            elif tool_name == "system/network":
                connections = await self.system_monitor.get_network_connections()
                routes = await self.system_monitor.get_network_routes()
                return {
                    "connections": [conn.dict() for conn in connections],
                    "routes": [route.dict() for route in routes],
                    "history": [cmd.dict() for cmd in self.system_monitor.get_command_history(5)]
                }
            elif tool_name == "system/logs":
                result = await self.system_monitor.get_systemd_logs(
                    unit=arguments.get("unit"),
                    since=arguments.get("since", "1h")
                )
                return result.dict()
            elif tool_name == "system/info":
                info = await self.system_monitor.get_system_info()
                metrics = await self._collect_system_metrics(["cpu", "memory", "disk", "network"])
                return {
                    **info,
                    "metrics": metrics,
                    "command_history": [
                        cmd.dict() for cmd in self.system_monitor.get_command_history(3)
                    ]
                }
            else:
                raise ValidationError("unknown_system_tool", f"Unknown system tool: {tool_name}")
        except Exception as e:
            logger.error(f"Error executing system tool {tool_name}: {str(e)}")
            raise ToolError("system_tool_error", str(e))

    async def _collect_system_metrics(self, metrics: List[str]) -> Dict[str, Any]:
        """Collect system metrics."""
        result = {}
        
        for metric in metrics:
            if metric == "cpu":
                result["cpu"] = {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                }
            elif metric == "memory":
                memory = psutil.virtual_memory()
                result["memory"] = {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                }
            elif metric == "disk":
                disk = psutil.disk_usage('/')
                result["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                }
            elif metric == "network":
                result["network"] = psutil.net_io_counters()._asdict()

        return result

    async def _list_system_processes(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List system processes with optional filters."""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                
                # Apply filters
                if filters:
                    if "name" in filters and filters["name"] not in pinfo["name"].lower():
                        continue
                    if "cpu_percent" in filters and pinfo["cpu_percent"] < filters["cpu_percent"]:
                        continue
                    if "memory_percent" in filters and pinfo["memory_percent"] < filters["memory_percent"]:
                        continue
                
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

@asynccontextmanager
async def get_mcp_server():
    """Get MCP server instance."""
    container = get_container()
    server = MCPServer(container)
    try:
        yield server
    finally:
        # Cleanup if needed
        pass 