from typing import List, Optional, Dict, Any
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..websockets.manager import ConnectionManager
from ..services.monitoring import MonitoringService
from ..dependencies import get_api_key
from ..database import get_session

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    api_key: str = Depends(get_api_key)
):
    """WebSocket endpoint for real-time metric updates."""
    try:
        # Accept the connection
        await manager.connect(websocket)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message["type"] == "subscribe":
                    # Update metric type subscriptions
                    await manager.update_subscriptions(
                        websocket,
                        message.get("metric_types", [])
                    )
                    
                elif message["type"] == "heartbeat":
                    # Update last heartbeat time
                    await manager.handle_heartbeat(websocket)
                    
                elif message["type"] == "get_metrics":
                    # Handle request for historical metrics
                    async with get_session() as session:
                        monitoring_service = MonitoringService(session)
                        metrics = await monitoring_service.get_metrics(
                            metric_type=message.get("metric_type"),
                            start_time=message.get("start_time"),
                            end_time=message.get("end_time"),
                            limit=message.get("limit", 100),
                            offset=message.get("offset", 0)
                        )
                        
                        # Send metrics to client
                        for metric in metrics:
                            metric_data = {
                                "type": metric.__class__.__name__.lower().replace("metric", ""),
                                "timestamp": metric.timestamp.isoformat(),
                                "data": metric.to_dict()
                            }
                            await websocket.send_text(json.dumps(metric_data))
                
                else:
                    # Handle unknown message type
                    await manager.broadcast_error(
                        f"Unknown message type: {message.get('type')}",
                        websocket
                    )
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info("WebSocket client disconnected")
            
        except json.JSONDecodeError as e:
            await manager.broadcast_error(
                f"Invalid JSON message: {str(e)}",
                websocket
            )
            manager.disconnect(websocket)
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await manager.broadcast_error(
                "Internal server error",
                websocket
            )
            manager.disconnect(websocket)
            
    except Exception as e:
        logger.error(f"Error establishing WebSocket connection: {str(e)}")
        try:
            await websocket.close()
        except Exception:
            pass

@router.websocket("/ws/metrics/{metric_type}")
async def metric_type_websocket(
    websocket: WebSocket,
    metric_type: str,
    api_key: str = Depends(get_api_key)
):
    """WebSocket endpoint for specific metric type updates."""
    try:
        # Accept the connection with specific metric type subscription
        await manager.connect(websocket, [metric_type])
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["type"] == "heartbeat":
                    # Update last heartbeat time
                    await manager.handle_heartbeat(websocket)
                    
                elif message["type"] == "get_metrics":
                    # Handle request for historical metrics of specific type
                    async with get_session() as session:
                        monitoring_service = MonitoringService(session)
                        metrics = await monitoring_service.get_metrics(
                            metric_type=metric_type,
                            start_time=message.get("start_time"),
                            end_time=message.get("end_time"),
                            limit=message.get("limit", 100),
                            offset=message.get("offset", 0)
                        )
                        
                        # Send metrics to client
                        for metric in metrics:
                            metric_data = {
                                "type": metric_type,
                                "timestamp": metric.timestamp.isoformat(),
                                "data": metric.to_dict()
                            }
                            await websocket.send_text(json.dumps(metric_data))
                            
                else:
                    # Handle unknown message type
                    await manager.broadcast_error(
                        f"Unknown message type: {message.get('type')}",
                        websocket
                    )
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info(f"WebSocket client disconnected from {metric_type} feed")
            
        except json.JSONDecodeError as e:
            await manager.broadcast_error(
                f"Invalid JSON message: {str(e)}",
                websocket
            )
            manager.disconnect(websocket)
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await manager.broadcast_error(
                "Internal server error",
                websocket
            )
            manager.disconnect(websocket)
            
    except Exception as e:
        logger.error(f"Error establishing WebSocket connection: {str(e)}")
        try:
            await websocket.close()
        except Exception:
            pass

# Background task to clean up stale connections
@router.on_event("startup")
async def startup_event():
    """Initialize WebSocket cleanup task."""
    import asyncio
    
    async def cleanup_task():
        while True:
            try:
                manager.cleanup_stale_connections()
                await asyncio.sleep(15)  # Check every 15 seconds
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    asyncio.create_task(cleanup_task()) 