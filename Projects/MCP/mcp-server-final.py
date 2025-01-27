# server.py
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
import mcp.types as types

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ToolExecutionError(Exception):
    """Custom exception for tool execution failures"""
    pass

class MCPToolServer(Server):
    def __init__(self, tools_path: Union[str, Path] = "tools.json"):
        super().__init__("tool-server")
        self.tools_path = Path(tools_path)
        self.tools: List[Dict[str, Any]] = []
        self.capabilities = {
            "tools": {
                "listChanged": True  
            },
            "logging": {},  
            "resources": {
                "subscribe": True,
                "listChanged": True
            }
        }
        self.load_tools()

    def load_tools(self) -> None:
        try:
            if not self.tools_path.exists():
                logger.error(f"Tools file not found: {self.tools_path}")
                return

            with open(self.tools_path) as f:
                tools = json.load(f)

            validated_tools = []
            for tool in tools:
                try:
                    self._validate_tool_definition(tool)
                    validated_tools.append(tool)
                except ValueError as e:
                    logger.warning(f"Invalid tool definition: {e}")

            self.tools = validated_tools
            logger.info(f"Successfully loaded {len(self.tools)} tools")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tools.json: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading tools: {e}")

    def _validate_tool_definition(self, tool: Dict[str, Any]) -> None:
        required_fields = {"name", "description", "input_schema"}
        missing_fields = required_fields - set(tool.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        if not isinstance(tool["input_schema"], dict):
            raise ValueError("input_schema must be a dictionary")
        if tool["input_schema"].get("type") != "object":
            raise ValueError("input_schema.type must be 'object'")

    async def handle_list_tools(self) -> List[types.Tool]:
        try:
            return [
                types.Tool(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    inputSchema=tool["input_schema"]
                )
                for tool in self.tools
            ]
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            raise

    async def handle_call_tool(
        self, 
        name: str, 
        arguments: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None
    ) -> List[types.TextContent]:
        try:
            tool = next((t for t in self.tools if t["name"] == name), None)
            if not tool:
                raise ValueError(f"Tool not found: {name}")

            self._validate_tool_arguments(tool, arguments or {})

            if progress_callback:
                await progress_callback(0, 100)

            result = await self._execute_tool(tool, arguments or {}, progress_callback)

            if progress_callback:
                await progress_callback(100, 100)

            return [types.TextContent(type="text", text=result)]

        except ValueError as e:
            logger.warning(f"Invalid tool call: {e}")
            raise
        except ToolExecutionError as e:
            logger.error(f"Tool execution failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error executing tool: {str(e)}"
            )]
        except Exception as e:
            logger.error(f"Unexpected error in tool execution: {e}")
            raise

    def _validate_tool_arguments(self, tool: Dict[str, Any], arguments: Dict[str, Any]) -> None:
        schema = tool["input_schema"]
        required_props = schema.get("required", [])
        missing_args = set(required_props) - set(arguments.keys())
        if missing_args:
            raise ValueError(f"Missing required arguments: {missing_args}")

    async def _execute_tool(
        self, 
        tool: Dict[str, Any], 
        arguments: Dict[str, Any],
        progress_callback: Optional[callable]
    ) -> str:
        try:
            if tool["name"] == "execute_command":
                return await self._execute_shell_command(
                    arguments["command"], 
                    arguments.get("args", [])
                )
            elif tool["name"] == "analyze_csv":
                return await self._analyze_csv(
                    arguments["filepath"],
                    arguments.get("operations", [])
                )
            
            raise NotImplementedError(f"Tool {tool['name']} not implemented")
            
        except Exception as e:
            raise ToolExecutionError(str(e))

    async def _execute_shell_command(self, command: str, args: List[str]) -> str:
        try:
            proc = await asyncio.create_subprocess_exec(
                command,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                raise ToolExecutionError(f"Command failed: {stderr.decode()}")
                
            return stdout.decode()
            
        except Exception as e:
            raise ToolExecutionError(f"Failed to execute command: {e}")

    async def _analyze_csv(self, filepath: str, operations: List[str]) -> str:
        # Implement CSV analysis logic here
        return f"Analyzing CSV {filepath} with operations: {operations}"

class TransportManager:
    def __init__(self, server: MCPToolServer):
        self.server = server
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/sse")
        async def sse_endpoint(request: Request):
            transport = SseServerTransport("/message")
            return EventSourceResponse(self.handle_sse(transport, request))

        @self.app.post("/message")
        async def message_endpoint(request: Request):
            message = await request.json()
            return JSONResponse({"status": "ok"})

        @self.app.post("/tools/call/{tool_name}")
        async def call_tool(tool_name: str, request: Request):
            try:
                arguments = await request.json()
                result = await self.server.handle_call_tool(tool_name, arguments)
                return JSONResponse({"result": result})
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/tools")
        async def list_tools():
            try:
                tools = await self.server.handle_list_tools()
                return JSONResponse({"tools": [t.dict() for t in tools]})
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def handle_sse(self, transport, request):
        async with transport.connect_sse(request.scope, request.receive, request.send) as streams:
            await self.server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="tool-server",
                    server_version="1.0.0",
                    capabilities=self.server.capabilities
                )
            )

    async def run_stdio(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="tool-server",
                    server_version="1.0.0",
                    capabilities=self.server.capabilities
                )
            )

async def main():
    server = MCPToolServer()
    transport_mgr = TransportManager(server)
    
    transport_type = os.environ.get("MCP_TRANSPORT", "stdio")
    port = int(os.environ.get("MCP_PORT", 8000))
    
    try:
        if transport_type == "stdio":
            await transport_mgr.run_stdio()
        else:
            config = uvicorn.Config(transport_mgr.app, host="0.0.0.0", port=port)
            server = uvicorn.Server(config)
            await server.serve()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
