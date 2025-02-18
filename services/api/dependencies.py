from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# Rate limiting
class RateLimiter:
    def __init__(self):
        self._requests = {}
        self._max_requests = 100  # requests per window
        self._window_size = timedelta(minutes=1)

    def is_allowed(self, api_key: str) -> bool:
        now = datetime.utcnow()
        window_start = now - self._window_size

        # Clean up old requests
        self._requests = {
            k: v for k, v in self._requests.items()
            if v[-1] > window_start
        }

        # Get requests in current window
        requests = self._requests.get(api_key, [])
        requests = [ts for ts in requests if ts > window_start]

        if len(requests) >= self._max_requests:
            return False

        # Update requests
        self._requests[api_key] = requests + [now]
        return True

rate_limiter = RateLimiter()

# Dependencies
async def get_api_key(api_key: str = Depends(API_KEY_HEADER)) -> str:
    """Validate API key and check rate limits."""
    # TODO: Replace with actual API key validation against database
    if api_key != "test_key":
        logger.warning(f"Invalid API key attempt: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check rate limits
    if not rate_limiter.is_allowed(api_key):
        logger.warning(f"Rate limit exceeded for API key: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    return api_key

# Database session dependency (to be implemented)
# async def get_db():
#     """Get database session."""
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()

# Service dependencies (to be implemented)
# async def get_monitoring_service():
#     """Get monitoring service instance."""
#     return MonitoringService()

# async def get_workflow_service():
#     """Get workflow service instance."""
#     return WorkflowService() 