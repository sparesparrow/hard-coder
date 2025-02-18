from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from typing import List, Optional
import logging
from datetime import datetime
import uvicorn
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        self.requests = {ip: times for ip, times in self.requests.items()
                        if any(t > current_time - 60 for t in times)}
        
        # Check rate limit
        if client_ip in self.requests:
            times = self.requests[client_ip]
            times = [t for t in times if t > current_time - 60]
            if len(times) >= self.calls_per_minute:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429
                )
            self.requests[client_ip] = times + [current_time]
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)

# Initialize FastAPI app
app = FastAPI(
    title="System Context Monitor",
    description="A comprehensive system monitoring solution with cognitive workflows",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Security middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(RateLimitMiddleware, calls_per_minute=60)

# API Key security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# Dependencies
async def get_api_key(api_key: str = Depends(API_KEY_HEADER)):
    # TODO: Replace with secure API key validation from environment or database
    valid_keys = {"test_key"}  # In production, load from secure storage
    if api_key not in valid_keys:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key

async def get_current_time():
    return datetime.utcnow().isoformat()

# Health check endpoint
@app.get("/health")
async def health_check(current_time: str = Depends(get_current_time)):
    return {
        "status": "healthy",
        "timestamp": current_time,
        "version": app.version,
        "endpoints": [
            {"path": "/api/monitoring", "status": "active"},
            {"path": "/api/workflows", "status": "active"},
            {"path": "/api/system", "status": "active"}
        ]
    }

# Import routers
from routers import monitoring, workflows, system, mcp

# Mount routers with authentication
app.include_router(
    monitoring.router,
    prefix="/api/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    workflows.router,
    prefix="/api/workflows",
    tags=["workflows"],
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    system.router,
    prefix="/api/system",
    tags=["system"],
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    mcp.router,
    prefix="/api/mcp",
    tags=["mcp"],
    dependencies=[Depends(get_api_key)]
)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting System Context Monitor API")
    try:
        # Initialize database connection
        from database import init_db
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize WebSocket manager
        from websockets.manager import init_websocket_manager
        await init_websocket_manager()
        logger.info("WebSocket manager initialized successfully")
        
        # Initialize service container
        from core.container import get_container
        container = get_container()
        
        # Register service implementations
        from adapters.claude_adapter import ClaudeAdapter
        from adapters.elevenlabs_adapter import ElevenLabsAdapter
        from managers.websocket_manager import WebSocketManager
        from managers.metrics_collector import MetricsCollector
        from managers.state_manager import StateManager
        
        container.register(AIServiceInterface, ClaudeAdapter)
        container.register(AudioServiceInterface, ElevenLabsAdapter)
        container.register(WebSocketManagerInterface, WebSocketManager)
        container.register(MetricsCollectorInterface, MetricsCollector)
        container.register(StateManagerInterface, StateManager)
        
        logger.info("Service container initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down System Context Monitor API")
    try:
        # Cleanup database connections
        from database import close_db
        await close_db()
        logger.info("Database connections closed")
        
        # Cleanup WebSocket connections
        from websockets.manager import cleanup_websocket_manager
        await cleanup_websocket_manager()
        logger.info("WebSocket connections cleaned up")
        
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4,
        log_level="info"
    ) 