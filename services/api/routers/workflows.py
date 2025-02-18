from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status, BackgroundTasks
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid

from ..dependencies import get_api_key
from ..services.workflows import WorkflowService
from ..database import get_session
from ..websockets.manager import ConnectionManager

logger = logging.getLogger(__name__)

# Models
class WorkflowStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    timeout_seconds: Optional[int] = Field(default=300, ge=1)
    retry_config: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('type')
    def validate_step_type(cls, v):
        allowed_types = {'processing', 'analysis', 'decision', 'action', 'notification'}
        if v not in allowed_types:
            raise ValueError(f'Invalid step type. Must be one of: {allowed_types}')
        return v

class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "created"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = {'created', 'running', 'paused', 'completed', 'failed'}
        if v not in allowed_statuses:
            raise ValueError(f'Invalid status. Must be one of: {allowed_statuses}')
        return v

class WorkflowExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "running"
    current_step: Optional[str] = None
    results: Dict[str, Any] = Field(default_factory=dict)
    error_details: Optional[Dict[str, Any]] = None

    @validator('status')
    def validate_execution_status(cls, v):
        allowed_statuses = {'running', 'paused', 'completed', 'failed'}
        if v not in allowed_statuses:
            raise ValueError(f'Invalid status. Must be one of: {allowed_statuses}')
        return v

# Router
router = APIRouter()
ws_manager = ConnectionManager()

# WebSocket Manager for Workflows
class WorkflowWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.workflow_subscriptions: Dict[str, set] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.workflow_subscriptions[client_id] = set()
        await self.send_welcome_message(websocket, client_id)

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        self.workflow_subscriptions.pop(client_id, None)

    async def subscribe_to_workflow(self, client_id: str, workflow_id: str):
        if client_id in self.workflow_subscriptions:
            self.workflow_subscriptions[client_id].add(workflow_id)

    async def unsubscribe_from_workflow(self, client_id: str, workflow_id: str):
        if client_id in self.workflow_subscriptions:
            self.workflow_subscriptions[client_id].discard(workflow_id)

    async def broadcast_workflow_update(self, workflow_id: str, update: Dict[str, Any]):
        for client_id, websocket in self.active_connections.items():
            try:
                if workflow_id in self.workflow_subscriptions[client_id]:
                    await websocket.send_json({
                        "type": "workflow_update",
                        "workflow_id": workflow_id,
                        "data": update,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                await self.handle_disconnect(client_id)

    async def send_welcome_message(self, websocket: WebSocket, client_id: str):
        welcome_msg = {
            "type": "welcome",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to workflow WebSocket"
        }
        await websocket.send_json(welcome_msg)

    async def handle_disconnect(self, client_id: str):
        self.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected from workflow WebSocket")

ws_workflow_manager = WorkflowWebSocketManager()

# Endpoints
@router.post("/workflows", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: Workflow,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Create a new workflow."""
    try:
        workflow_service = WorkflowService(session)
        created_workflow = await workflow_service.create_workflow(workflow)
        
        # Broadcast creation event
        background_tasks.add_task(
            ws_workflow_manager.broadcast_workflow_update,
            workflow_id=created_workflow.id,
            update={"action": "created", "workflow": created_workflow.dict()}
        )
        
        return {
            "status": "success",
            "message": "Workflow created successfully",
            "data": created_workflow.dict()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/workflows")
async def get_workflows(
    status: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get workflows with optional filtering."""
    try:
        workflow_service = WorkflowService(session)
        workflows = await workflow_service.get_workflows(
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "status": "success",
            "count": len(workflows),
            "data": [w.dict() for w in workflows],
            "pagination": {
                "offset": offset,
                "limit": limit,
                "has_more": len(workflows) == limit
            }
        }
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get workflow by ID."""
    try:
        workflow_service = WorkflowService(session)
        workflow = await workflow_service.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        
        return {
            "status": "success",
            "data": workflow.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Execute a workflow."""
    try:
        workflow_service = WorkflowService(session)
        execution = await workflow_service.execute_workflow(workflow_id)
        
        # Add background task for execution
        background_tasks.add_task(
            workflow_service.process_workflow_execution,
            execution.id,
            ws_workflow_manager
        )
        
        return {
            "status": "success",
            "message": "Workflow execution started",
            "data": execution.dict()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/workflows/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Pause a running workflow."""
    try:
        workflow_service = WorkflowService(session)
        updated_workflow = await workflow_service.pause_workflow(workflow_id)
        
        # Broadcast pause event
        background_tasks.add_task(
            ws_workflow_manager.broadcast_workflow_update,
            workflow_id=workflow_id,
            update={"action": "paused", "workflow": updated_workflow.dict()}
        )
        
        return {
            "status": "success",
            "message": "Workflow paused successfully",
            "data": updated_workflow.dict()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error pausing workflow {workflow_id}: {str(e)}")
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
    """WebSocket endpoint for workflow updates."""
    try:
        await ws_workflow_manager.connect(websocket, client_id)
        
        while True:
            try:
                data = await websocket.receive_json()
                
                if data.get("action") == "subscribe":
                    workflow_id = data.get("workflow_id")
                    if workflow_id:
                        await ws_workflow_manager.subscribe_to_workflow(client_id, workflow_id)
                        await websocket.send_json({
                            "type": "subscription_update",
                            "status": "success",
                            "workflow_id": workflow_id,
                            "message": f"Subscribed to workflow {workflow_id}"
                        })
                
                elif data.get("action") == "unsubscribe":
                    workflow_id = data.get("workflow_id")
                    if workflow_id:
                        await ws_workflow_manager.unsubscribe_from_workflow(client_id, workflow_id)
                        await websocket.send_json({
                            "type": "subscription_update",
                            "status": "success",
                            "workflow_id": workflow_id,
                            "message": f"Unsubscribed from workflow {workflow_id}"
                        })
                
            except WebSocketDisconnect:
                await ws_workflow_manager.handle_disconnect(client_id)
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