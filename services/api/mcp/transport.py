import logging
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import json
from fastapi import WebSocket, WebSocketDisconnect
import uuid

from .server import MCPServer, Message, MCPError
from ..managers.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)

class MCPTransport:
    """WebSocket transport for MCP communication."""
    
    def __init__(self, server: MCPServer, metrics: MetricsCollector):
        self.server = server
        self.metrics = metrics
        self._active_connections: Dict[str, WebSocket] = {}
        self._connection_metadata: Dict[str, Dict[str, Any]] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._heartbeat_interval = 30  # seconds
        logger.info("Initialized MCP transport")

    async def initialize(self) -> None:
        """Initialize the transport."""
        try:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            logger.info("MCP transport initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP transport: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
                self._heartbeat_task = None

            # Close all active connections
            for client_id, websocket in self._active_connections.items():
                try:
                    await websocket.close()
                except Exception as e:
                    logger.error(f"Error closing connection {client_id}: {str(e)}")

            self._active_connections.clear()
            self._connection_metadata.clear()
            logger.info("MCP transport cleaned up")
        except Exception as e:
            logger.error(f"Error during MCP transport cleanup: {str(e)}")
            raise

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Handle new WebSocket connection."""
        client_id = str(uuid.uuid4())
        
        try:
            await websocket.accept()
            self._active_connections[client_id] = websocket
            self._connection_metadata[client_id] = {
                "connected_at": datetime.utcnow().isoformat(),
                "client_info": websocket.client,
                "last_heartbeat": datetime.utcnow().isoformat()
            }
            
            # Send welcome message
            await self._send_message(websocket, {
                "type": "welcome",
                "client_id": client_id,
                "server_time": datetime.utcnow().isoformat()
            })
            
            logger.info(f"New MCP connection established: {client_id}")
            
            # Handle messages
            while True:
                try:
                    raw_message = await websocket.receive_text()
                    start_time = datetime.utcnow()
                    
                    # Parse and validate message
                    try:
                        data = json.loads(raw_message)
                        message = Message(**data)
                    except json.JSONDecodeError:
                        await self._send_error(websocket, "invalid_json", "Invalid JSON format")
                        continue
                    except Exception as e:
                        await self._send_error(websocket, "invalid_message", str(e))
                        continue

                    # Handle message
                    try:
                        response = await self.server.handle_message(message)
                        await self._send_message(websocket, {
                            "id": message.id,
                            **response
                        })
                    except MCPError as e:
                        await self._send_error(
                            websocket,
                            e.code,
                            e.message,
                            message_id=message.id
                        )
                    except Exception as e:
                        logger.error(f"Error handling message: {str(e)}")
                        await self._send_error(
                            websocket,
                            "internal_error",
                            "Internal server error",
                            message_id=message.id
                        )
                    
                    # Record metrics
                    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                    await self.metrics.record_latency(
                        operation=f"mcp.{message.method}",
                        duration_ms=duration,
                        metadata={
                            "client_id": client_id,
                            "message_id": message.id
                        }
                    )
                    
                except WebSocketDisconnect:
                    logger.info(f"MCP client disconnected: {client_id}")
                    break
                except Exception as e:
                    logger.error(f"Error in message loop for {client_id}: {str(e)}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling MCP connection {client_id}: {str(e)}")
        finally:
            # Clean up connection
            self._active_connections.pop(client_id, None)
            self._connection_metadata.pop(client_id, None)
            logger.info(f"MCP connection cleaned up: {client_id}")

    async def _send_message(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """Send message to client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    async def _send_error(self,
        websocket: WebSocket,
        code: str,
        message: str,
        message_id: Optional[str] = None
    ) -> None:
        """Send error message to client."""
        error_message = {
            "error": {
                "code": code,
                "message": message
            }
        }
        if message_id:
            error_message["id"] = message_id
            
        await self._send_message(websocket, error_message)

    async def _heartbeat_monitor(self) -> None:
        """Monitor connection heartbeats."""
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                current_time = datetime.utcnow()
                
                # Check all connections
                for client_id, websocket in list(self._active_connections.items()):
                    try:
                        # Send heartbeat
                        await self._send_message(websocket, {
                            "type": "heartbeat",
                            "server_time": current_time.isoformat()
                        })
                        
                        # Update metadata
                        if client_id in self._connection_metadata:
                            self._connection_metadata[client_id]["last_heartbeat"] = current_time.isoformat()
                            
                    except Exception as e:
                        logger.error(f"Heartbeat failed for {client_id}: {str(e)}")
                        # Remove failed connection
                        self._active_connections.pop(client_id, None)
                        self._connection_metadata.pop(client_id, None)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {str(e)}")

    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about active connections."""
        return {
            "active_connections": len(self._active_connections),
            "connections": [
                {
                    "client_id": client_id,
                    **metadata
                }
                for client_id, metadata in self._connection_metadata.items()
            ]
        } 