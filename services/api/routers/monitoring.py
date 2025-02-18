from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status, BackgroundTasks
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import json

from ..dependencies import get_api_key
from ..services.monitoring import MonitoringService
from ..database import get_session
from ..models.metrics import (
    Metric,
    ScreenshotMetric,
    NetworkMetric,
    ClipboardMetric
)
from ..websockets.manager import ConnectionManager

logger = logging.getLogger(__name__)

# Enhanced Models with Validation
class MetricBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metric_type: str
    value: Any
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('metric_type')
    def validate_metric_type(cls, v):
        allowed_types = {'screenshot', 'network', 'clipboard', 'system', 'custom'}
        if v not in allowed_types:
            raise ValueError(f'Invalid metric type. Must be one of: {allowed_types}')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScreenshotMetric(MetricBase):
    file_path: str
    dimensions: Dict[str, int]
    file_size: int

    @validator('dimensions')
    def validate_dimensions(cls, v):
        required_keys = {'width', 'height'}
        if not all(key in v for key in required_keys):
            raise ValueError(f'Dimensions must contain keys: {required_keys}')
        if any(value <= 0 for value in v.values()):
            raise ValueError('Dimensions must be positive integers')
        return v

class NetworkMetric(MetricBase):
    connections: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    io_counters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    active_interfaces: List[Dict[str, Any]] = Field(default_factory=list)
    bandwidth_usage: Optional[float] = Field(default=0.0, ge=0)

    @validator('bandwidth_usage')
    def validate_bandwidth(cls, v):
        if v < 0:
            raise ValueError('Bandwidth usage must be non-negative')
        return v

class ClipboardMetric(MetricBase):
    content_hash: str
    content_type: str
    content_length: int
    is_filtered: bool = False
    sensitive_content_detected: bool = False

    @validator('content_length')
    def validate_content_length(cls, v):
        if v < 0:
            raise ValueError('Content length must be non-negative')
        return v

# Router
router = APIRouter()
ws_manager = ConnectionManager()

# Enhanced WebSocket Manager
class MonitoringWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_subscriptions: Dict[str, set] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        await self.send_welcome_message(websocket, client_id)

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        self.client_subscriptions.pop(client_id, None)

    async def subscribe(self, client_id: str, metric_types: List[str]):
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].update(metric_types)

    async def unsubscribe(self, client_id: str, metric_types: List[str]):
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].difference_update(metric_types)

    async def broadcast(self, message: Dict[str, Any], metric_type: Optional[str] = None):
        for client_id, websocket in self.active_connections.items():
            try:
                if not metric_type or metric_type in self.client_subscriptions[client_id]:
                    await websocket.send_json(message)
            except WebSocketDisconnect:
                await self.handle_disconnect(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                await self.handle_disconnect(client_id)

    async def send_welcome_message(self, websocket: WebSocket, client_id: str):
        welcome_msg = {
            "type": "welcome",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to monitoring WebSocket"
        }
        await websocket.send_json(welcome_msg)

    async def handle_disconnect(self, client_id: str):
        self.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

ws_monitoring_manager = MonitoringWebSocketManager()

# Enhanced Endpoints
@router.post("/metrics/{metric_type}", status_code=status.HTTP_201_CREATED)
async def create_metric(
    metric_type: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Create a new metric with background processing."""
    try:
        monitoring_service = MonitoringService(session)
        metric = await monitoring_service.create_metric(metric_type, data)
        
        # Add background task for WebSocket broadcast
        background_tasks.add_task(
            ws_monitoring_manager.broadcast,
            message={"type": "metric_created", "data": metric.to_dict()},
            metric_type=metric_type
        )
        
        return {
            "status": "success",
            "message": f"Created {metric_type} metric",
            "data": metric.to_dict()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating metric: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/metrics")
async def get_metrics(
    metric_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    sort_by: Optional[str] = Query(None, regex="^(timestamp|metric_type|value)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get metrics with enhanced filtering and sorting."""
    try:
        monitoring_service = MonitoringService(session)
        metrics = await monitoring_service.get_metrics(
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "status": "success",
            "count": len(metrics),
            "data": [metric.to_dict() for metric in metrics],
            "pagination": {
                "offset": offset,
                "limit": limit,
                "has_more": len(metrics) == limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/metrics")
async def cleanup_metrics(
    retention_hours: int = Query(default=24, ge=1),
    metric_type: Optional[str] = None,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Clean up old metrics with optional type filtering."""
    try:
        monitoring_service = MonitoringService(session)
        cleanup_results = await monitoring_service.cleanup_old_metrics(
            retention_hours,
            metric_type=metric_type
        )
        
        # Notify WebSocket clients about cleanup
        background_tasks.add_task(
            ws_monitoring_manager.broadcast,
            message={
                "type": "metrics_cleanup",
                "data": {
                    "retention_hours": retention_hours,
                    "metric_type": metric_type,
                    "deleted_counts": cleanup_results
                }
            }
        )
        
        return {
            "status": "success",
            "message": "Cleaned up old metrics",
            "deleted_counts": cleanup_results
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/metrics/summary")
async def get_metrics_summary(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get a summary of metrics by type."""
    try:
        monitoring_service = MonitoringService(session)
        summary = await monitoring_service.get_metrics_summary(
            start_time=start_time,
            end_time=end_time
        )
        
        return {
            "status": "success",
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Enhanced WebSocket endpoint with subscription support."""
    try:
        await ws_monitoring_manager.connect(websocket, client_id)
        
        while True:
            try:
                data = await websocket.receive_json()
                
                if data.get("action") == "subscribe":
                    metric_types = data.get("metric_types", [])
                    await ws_monitoring_manager.subscribe(client_id, metric_types)
                    await websocket.send_json({
                        "type": "subscription_update",
                        "status": "success",
                        "subscribed_types": list(ws_monitoring_manager.client_subscriptions[client_id])
                    })
                
                elif data.get("action") == "unsubscribe":
                    metric_types = data.get("metric_types", [])
                    await ws_monitoring_manager.unsubscribe(client_id, metric_types)
                    await websocket.send_json({
                        "type": "subscription_update",
                        "status": "success",
                        "subscribed_types": list(ws_monitoring_manager.client_subscriptions[client_id])
                    })
                
            except WebSocketDisconnect:
                await ws_monitoring_manager.handle_disconnect(client_id)
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"WebSocket error for client {client_id}: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Internal server error"
                })
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        if websocket.client_state.connected:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR) 