from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Dict, Any
import logging
from datetime import datetime

from ..dependencies import get_api_key
from ..mcp.server import get_mcp_server
from ..mcp.transport import MCPTransport
from ..managers.metrics_collector import MetricsCollector
from ..core.container import get_container

logger = logging.getLogger(__name__)

router = APIRouter()

# Store MCP transport instances
mcp_transports: Dict[str, MCPTransport] = {}

async def get_metrics_collector() -> MetricsCollector:
    """Get metrics collector instance."""
    container = get_container()
    return await container.get(MetricsCollector)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    api_key: str = Depends(get_api_key)
):
    """WebSocket endpoint for MCP communication."""
    try:
        # Initialize MCP server and transport
        async with get_mcp_server() as server:
            metrics = await get_metrics_collector()
            transport = MCPTransport(server, metrics)
            await transport.initialize()
            
            try:
                # Handle connection
                await transport.handle_connection(websocket)
            finally:
                await transport.cleanup()
                
    except Exception as e:
        logger.error(f"Error in MCP WebSocket endpoint: {str(e)}")
        if websocket.client_state.connected:
            await websocket.close(code=status.WS_1011_INTERNAL_SERVER_ERROR)

@router.get("/connections")
async def get_connections(
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """Get information about active MCP connections."""
    try:
        connections_info = {
            transport_id: transport.get_connection_info()
            for transport_id, transport in mcp_transports.items()
        }
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "transports": connections_info
        }
    except Exception as e:
        logger.error(f"Error getting MCP connections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )