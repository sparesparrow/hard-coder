from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int = 100  # Maximum requests per window
    window_seconds: int = 60  # Time window in seconds
    max_concurrent: int = 10  # Maximum concurrent executions
    burst_limit: int = 20    # Maximum burst requests
    cooldown_seconds: int = 5  # Cooldown period after burst

class RateLimiter:
    """Rate limiter for tool execution."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self._config = config or RateLimitConfig()
        self._requests: Dict[str, list] = {}  # tool_id -> list of timestamps
        self._concurrent: Dict[str, int] = {}  # tool_id -> current concurrent executions
        self._burst_state: Dict[str, Tuple[int, datetime]] = {}  # tool_id -> (count, start_time)
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the rate limiter with cleanup task."""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Rate limiter cleanup task started")
    
    async def stop(self) -> None:
        """Stop the rate limiter and cleanup."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Rate limiter cleanup task stopped")
    
    async def check_rate_limit(self, tool_id: str) -> bool:
        """Check if a tool execution is allowed under rate limits."""
        async with self._lock:
            current_time = datetime.utcnow()
            window_start = current_time - timedelta(seconds=self._config.window_seconds)
            
            # Initialize tracking for new tools
            if tool_id not in self._requests:
                self._requests[tool_id] = []
                self._concurrent[tool_id] = 0
            
            # Clean up old requests
            self._requests[tool_id] = [
                ts for ts in self._requests[tool_id]
                if ts > window_start
            ]
            
            # Check window limit
            if len(self._requests[tool_id]) >= self._config.max_requests:
                logger.warning(
                    f"Rate limit exceeded for tool {tool_id}: "
                    f"{len(self._requests[tool_id])} requests in {self._config.window_seconds}s"
                )
                return False
            
            # Check concurrent limit
            if self._concurrent[tool_id] >= self._config.max_concurrent:
                logger.warning(
                    f"Concurrent execution limit exceeded for tool {tool_id}: "
                    f"{self._concurrent[tool_id]} concurrent executions"
                )
                return False
            
            # Check burst limit
            if not self._check_burst_limit(tool_id, current_time):
                return False
            
            # Update tracking
            self._requests[tool_id].append(current_time)
            self._concurrent[tool_id] += 1
            
            return True
    
    def _check_burst_limit(self, tool_id: str, current_time: datetime) -> bool:
        """Check if burst limit is exceeded."""
        if tool_id not in self._burst_state:
            self._burst_state[tool_id] = (1, current_time)
            return True
        
        count, start_time = self._burst_state[tool_id]
        time_diff = (current_time - start_time).total_seconds()
        
        # Reset burst state if cooldown period elapsed
        if time_diff > self._config.cooldown_seconds:
            self._burst_state[tool_id] = (1, current_time)
            return True
        
        # Check burst limit
        if count >= self._config.burst_limit:
            logger.warning(
                f"Burst limit exceeded for tool {tool_id}: "
                f"{count} requests in {time_diff}s"
            )
            return False
        
        # Update burst count
        self._burst_state[tool_id] = (count + 1, start_time)
        return True
    
    async def release(self, tool_id: str) -> None:
        """Release a concurrent execution slot."""
        async with self._lock:
            if tool_id in self._concurrent:
                self._concurrent[tool_id] = max(0, self._concurrent[tool_id] - 1)
    
    async def _cleanup_loop(self) -> None:
        """Periodically clean up old rate limit data."""
        while True:
            try:
                await asyncio.sleep(self._config.window_seconds)
                await self._cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {str(e)}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _cleanup(self) -> None:
        """Clean up old rate limit data."""
        async with self._lock:
            current_time = datetime.utcnow()
            window_start = current_time - timedelta(seconds=self._config.window_seconds)
            
            # Clean up old requests
            for tool_id in list(self._requests.keys()):
                self._requests[tool_id] = [
                    ts for ts in self._requests[tool_id]
                    if ts > window_start
                ]
                
                # Remove empty entries
                if not self._requests[tool_id]:
                    del self._requests[tool_id]
                    self._concurrent.pop(tool_id, None)
            
            # Clean up old burst states
            for tool_id in list(self._burst_state.keys()):
                count, start_time = self._burst_state[tool_id]
                if (current_time - start_time).total_seconds() > self._config.cooldown_seconds:
                    del self._burst_state[tool_id]
    
    def get_limits(self, tool_id: str) -> Dict[str, int]:
        """Get current rate limit counters for a tool."""
        return {
            "requests": len(self._requests.get(tool_id, [])),
            "concurrent": self._concurrent.get(tool_id, 0),
            "burst": self._burst_state.get(tool_id, (0, datetime.utcnow()))[0]
        } 