# client.py
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol
from urllib.parse import urljoin
import os

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseTransport(ABC):
    def __init__(self):
        self.connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        pass
    
    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        pass
    
    def _check_connection(self):
        if not self.connected:
            raise RuntimeError("Transport not connected")

class StdioTransport(BaseTransport):
    def __init__(self, server_command: str, server_args: Optional[List[str]] = None):
        super().__init__()
        self.server_command = server_command
        self.server_args = server_args or []
        self.session: Optional[ClientSession] = None
    
    async def connect(self) -> None:
        try:
            params = StdioServerParameters(
                command=self.server_command,
                args=self.server_args,
                env=None
            )
            
            streams = await stdio_client(params).__aenter__()
            self.session = await ClientSession(streams[0], streams[1]).__aenter__()
            await self.session.initialize()
            self.connected = True
            logger.info("Connected via stdio transport")
            
        except Exception as e:
            logger.error(f"Failed to connect via stdio: {e}")
            raise
    
    async def disconnect(self) -> None:
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
                self.connected = False
                logger.info("Disconnected stdio transport")
            except Exception as e:
                logger.error(f"Error disconnecting stdio transport: {e}")
                raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        self._check_connection()
        try:
            response = await self.session.list_tools()
            return [tool.dict() for tool in response.tools]
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        self._check_connection()
        try:
            result = await self.session.call_tool(tool_name, arguments or {})
            return result
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise

class HTTPTransport(BaseTransport):
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def connect(self) -> None:
        try:
            await self.list_tools()  # Test connection
            self.connected = True
            logger.info(f"Connected to HTTP transport at {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to HTTP transport: {e}")
            raise

    async def disconnect(self) -> None:
        await self.http_client.aclose()
        self.connected = False
        logger.info("Disconnected HTTP transport")

    async def list_tools(self) -> List[Dict[str, Any]]:
        self._check_connection()
        try:
            response = await self.http_client.get(urljoin(self.base_url, "/tools"))
            response.raise_for_status()
            return response.json()["tools"]
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise

    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        self._check_connection()
        try:
            response = await self.http_client.post(
                urljoin(self.base_url, f"/tools/call/{tool_name}"),
                json=arguments or {}
            )
            response.raise_for_status()
            return response.json()["result"]
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise

class MCPClient:
    def __init__(self, transport: BaseTransport):
        self.transport = transport

    async def connect(self) -> None:
        await self.transport.connect()

    async def disconnect(self) -> None:
        await self.transport.disconnect()

    async def list_tools(self) -> List[Dict[str, Any]]: