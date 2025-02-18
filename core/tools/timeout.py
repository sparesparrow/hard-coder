from typing import TypeVar, Callable, Optional, Any
import asyncio
from datetime import datetime
import logging
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

class TimeoutError(Exception):
    """Exception raised when tool execution times out."""
    def __init__(self, tool_id: str, timeout: float):
        self.tool_id = tool_id
        self.timeout = timeout
        super().__init__(f"Tool {tool_id} execution timed out after {timeout} seconds")

class TimeoutManager:
    """Manages execution timeouts for tools."""
    
    def __init__(self, default_timeout: float = 30.0):
        self._default_timeout = default_timeout
        self._active_executions: dict = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the timeout manager."""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Timeout manager cleanup task started")
    
    async def stop(self) -> None:
        """Stop the timeout manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Timeout manager cleanup task stopped")
    
    async def execute_with_timeout(
        self,
        tool_id: str,
        func: Callable[..., T],
        timeout: Optional[float] = None,
        *args,
        **kwargs
    ) -> T:
        """Execute a function with timeout."""
        timeout = timeout or self._default_timeout
        execution_id = f"{tool_id}_{datetime.utcnow().timestamp()}"
        
        try:
            # Create task
            task = asyncio.create_task(func(*args, **kwargs))
            self._active_executions[execution_id] = {
                "task": task,
                "start_time": datetime.utcnow(),
                "timeout": timeout
            }
            
            # Wait for completion or timeout
            try:
                result = await asyncio.wait_for(task, timeout=timeout)
                return result
            except asyncio.TimeoutError:
                # Cancel task on timeout
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                logger.warning(
                    f"Tool execution timed out",
                    extra={
                        "tool_id": tool_id,
                        "execution_id": execution_id,
                        "timeout": timeout
                    }
                )
                raise TimeoutError(tool_id, timeout)
                
        finally:
            # Clean up execution record
            self._active_executions.pop(execution_id, None)
    
    def timeout_decorator(
        self,
        tool_id: str,
        timeout: Optional[float] = None
    ) -> Callable:
        """Decorator to add timeout to a function."""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                return await self.execute_with_timeout(
                    tool_id,
                    func,
                    timeout,
                    *args,
                    **kwargs
                )
            return wrapper
        return decorator
    
    async def _cleanup_loop(self) -> None:
        """Periodically clean up stale executions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in timeout manager cleanup: {str(e)}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _cleanup(self) -> None:
        """Clean up stale executions."""
        current_time = datetime.utcnow()
        stale_executions = [
            execution_id for execution_id, execution in self._active_executions.items()
            if (current_time - execution["start_time"]).total_seconds() > execution["timeout"] * 2
        ]
        
        for execution_id in stale_executions:
            execution = self._active_executions.pop(execution_id, None)
            if execution:
                task = execution["task"]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        pass
    
    def get_active_executions(self) -> dict:
        """Get information about active executions."""
        current_time = datetime.utcnow()
        return {
            execution_id: {
                "elapsed": (current_time - execution["start_time"]).total_seconds(),
                "timeout": execution["timeout"],
                "is_done": execution["task"].done()
            }
            for execution_id, execution in self._active_executions.items()
        } 