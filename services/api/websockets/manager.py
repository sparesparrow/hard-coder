from typing import Dict, Set, Optional, List
import json
import logging
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from ..models.metrics import Metric

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        # Store active connections with their subscribed metric types
        self.active_connections: Dict[WebSocket, Set[str]] = {}
        # Track last heartbeat for each connection
        self.last_heartbeat: Dict[WebSocket, datetime] = {}
    
    async def connect(self, websocket: WebSocket, metric_types: Optional[List[str]] = None) -> None:
        """Accept a new WebSocket connection and store subscription preferences."""
        try:
            await websocket.accept()
            self.active_connections[websocket] = set(metric_types) if metric_types else set()
            self.last_heartbeat[websocket] = datetime.utcnow()
            logger.info(f"New WebSocket connection established. Subscribed to: {metric_types}")
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {str(e)}")
            raise
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        try:
            self.active_connections.pop(websocket, None)
            self.last_heartbeat.pop(websocket, None)
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {str(e)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Send a message to a specific client."""
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast(self, metric: Metric) -> None:
        """Broadcast a metric to all subscribed clients."""
        try:
            # Convert metric to JSON-serializable format
            metric_data = {
                "type": metric.__class__.__name__.lower().replace("metric", ""),
                "timestamp": metric.timestamp.isoformat(),
                "data": metric.to_dict()
            }
            
            message = json.dumps(metric_data)
            
            # Send to all connected clients that are subscribed to this metric type
            disconnected = []
            for websocket, subscriptions in self.active_connections.items():
                if not subscriptions or metric_data["type"] in subscriptions:
                    try:
                        await websocket.send_text(message)
                    except WebSocketDisconnect:
                        disconnected.append(websocket)
                    except Exception as e:
                        logger.error(f"Error broadcasting to client: {str(e)}")
                        disconnected.append(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.disconnect(websocket)
                
        except Exception as e:
            logger.error(f"Error broadcasting metric: {str(e)}")
    
    async def update_subscriptions(self, websocket: WebSocket, metric_types: List[str]) -> None:
        """Update subscription preferences for a connection."""
        try:
            if websocket in self.active_connections:
                self.active_connections[websocket] = set(metric_types)
                await self.send_personal_message(
                    json.dumps({
                        "type": "subscription_update",
                        "subscriptions": list(metric_types)
                    }),
                    websocket
                )
                logger.info(f"Updated subscriptions for client: {metric_types}")
        except Exception as e:
            logger.error(f"Error updating subscriptions: {str(e)}")
            self.disconnect(websocket)
    
    async def handle_heartbeat(self, websocket: WebSocket) -> None:
        """Update last heartbeat time for a connection."""
        try:
            if websocket in self.active_connections:
                self.last_heartbeat[websocket] = datetime.utcnow()
                await self.send_personal_message(
                    json.dumps({
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    websocket
                )
        except Exception as e:
            logger.error(f"Error handling heartbeat: {str(e)}")
            self.disconnect(websocket)
    
    def cleanup_stale_connections(self, max_heartbeat_age_seconds: int = 30) -> None:
        """Remove connections that haven't sent a heartbeat recently."""
        try:
            current_time = datetime.utcnow()
            stale_connections = [
                ws for ws, last_hb in self.last_heartbeat.items()
                if (current_time - last_hb).total_seconds() > max_heartbeat_age_seconds
            ]
            
            for websocket in stale_connections:
                logger.warning(f"Removing stale connection (last heartbeat: {self.last_heartbeat[websocket]})")
                self.disconnect(websocket)
                
        except Exception as e:
            logger.error(f"Error cleaning up stale connections: {str(e)}")
    
    async def broadcast_error(self, error_message: str, websocket: Optional[WebSocket] = None) -> None:
        """Broadcast an error message to one or all clients."""
        try:
            error_data = json.dumps({
                "type": "error",
                "message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if websocket:
                await self.send_personal_message(error_data, websocket)
            else:
                disconnected = []
                for ws in self.active_connections:
                    try:
                        await ws.send_text(error_data)
                    except Exception:
                        disconnected.append(ws)
                
                for ws in disconnected:
                    self.disconnect(ws)
                    
        except Exception as e:
            logger.error(f"Error broadcasting error message: {str(e)}")
            if websocket:
                self.disconnect(websocket) 