import logging
from typing import Dict, Any, Optional, List, Set
import asyncio
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from ..interfaces.service_interfaces import WebSocketManagerInterface

logger = logging.getLogger(__name__)

class WebSocketManager(WebSocketManagerInterface):
    """WebSocket connection manager implementation."""
    
    def __init__(self):
        self._active_connections: Dict[str, WebSocket] = {}
        self._connection_metadata: Dict[str, Dict[str, Any]] = {}
        self._connection_heartbeats: Dict[str, datetime] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._heartbeat_interval = 30  # seconds
        logger.info("Initializing WebSocket manager")

    async def initialize(self) -> None:
        """Initialize the WebSocket manager."""
        try:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            logger.info("WebSocket manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket manager: {str(e)}")
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
            self._connection_heartbeats.clear()
            logger.info("WebSocket manager cleaned up")
        except Exception as e:
            logger.error(f"Error during WebSocket manager cleanup: {str(e)}")
            raise

    async def register_connection(self,
        client_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register new WebSocket connection."""
        if client_id in self._active_connections:
            logger.warning(f"Client {client_id} already registered")
            return

        try:
            websocket = metadata.pop("websocket", None) if metadata else None
            if not isinstance(websocket, WebSocket):
                raise ValueError("WebSocket instance required in metadata")

            self._active_connections[client_id] = websocket
            self._connection_metadata[client_id] = metadata or {}
            self._connection_heartbeats[client_id] = datetime.utcnow()
            
            logger.info(f"Registered new connection for client {client_id}")
            
            # Start connection handler
            asyncio.create_task(self._handle_connection(client_id, websocket))
            
        except Exception as e:
            logger.error(f"Failed to register connection for client {client_id}: {str(e)}")
            raise

    async def broadcast_message(self,
        message: Dict[str, Any],
        client_ids: Optional[List[str]] = None
    ) -> None:
        """Broadcast message to connected clients."""
        target_clients = set(client_ids) if client_ids else set(self._active_connections.keys())
        failed_clients: Set[str] = set()

        for client_id in target_clients:
            if client_id not in self._active_connections:
                logger.warning(f"Client {client_id} not found")
                continue

            try:
                websocket = self._active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to client {client_id}: {str(e)}")
                failed_clients.add(client_id)

        # Clean up failed connections
        for client_id in failed_clients:
            await self._remove_connection(client_id)

    async def get_active_connections(self) -> List[Dict[str, Any]]:
        """Get list of active connections."""
        return [{
            "client_id": client_id,
            "metadata": self._connection_metadata.get(client_id, {}),
            "connected_since": self._connection_heartbeats.get(client_id)
        } for client_id in self._active_connections.keys()]

    async def _handle_connection(self, client_id: str, websocket: WebSocket) -> None:
        """Handle individual WebSocket connection."""
        try:
            while True:
                try:
                    # Wait for messages or heartbeat
                    message = await websocket.receive_json()
                    self._connection_heartbeats[client_id] = datetime.utcnow()
                    
                    # Process message if needed
                    if message.get("type") == "heartbeat":
                        await websocket.send_json({"type": "heartbeat_ack"})
                        
                except WebSocketDisconnect:
                    logger.info(f"Client {client_id} disconnected")
                    break
                except Exception as e:
                    logger.error(f"Error handling message from client {client_id}: {str(e)}")
                    break
                    
        finally:
            await self._remove_connection(client_id)

    async def _heartbeat_monitor(self) -> None:
        """Monitor connection heartbeats."""
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                current_time = datetime.utcnow()
                
                expired_clients = [
                    client_id for client_id, last_heartbeat in self._connection_heartbeats.items()
                    if (current_time - last_heartbeat).total_seconds() > self._heartbeat_interval * 2
                ]
                
                for client_id in expired_clients:
                    logger.warning(f"Client {client_id} heartbeat expired")
                    await self._remove_connection(client_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {str(e)}")

    async def _remove_connection(self, client_id: str) -> None:
        """Remove a client connection."""
        try:
            if websocket := self._active_connections.pop(client_id, None):
                await websocket.close()
            self._connection_metadata.pop(client_id, None)
            self._connection_heartbeats.pop(client_id, None)
            logger.info(f"Removed connection for client {client_id}")
        except Exception as e:
            logger.error(f"Error removing connection for client {client_id}: {str(e)}") 