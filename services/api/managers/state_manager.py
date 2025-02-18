import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json
from ..interfaces.service_interfaces import StateManagerInterface

logger = logging.getLogger(__name__)

class StateEntry:
    """Represents a state entry with optional TTL."""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=ttl) if ttl else None

    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return bool(
            self.expires_at and datetime.utcnow() > self.expires_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

class StateManager(StateManagerInterface):
    """State manager implementation with in-memory storage and TTL support."""
    
    def __init__(self):
        self._state: Dict[str, StateEntry] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = 60  # seconds
        self._max_state_size = 10000
        logger.info("Initializing state manager")

    async def initialize(self) -> None:
        """Initialize the state manager."""
        try:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())
            logger.info("State manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize state manager: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
                self._cleanup_task = None

            self._state.clear()
            logger.info("State manager cleaned up")
        except Exception as e:
            logger.error(f"Error during state manager cleanup: {str(e)}")
            raise

    async def set_state(self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set state value with optional TTL."""
        try:
            # Validate key
            if not isinstance(key, str):
                raise ValueError("Key must be a string")

            # Validate value can be JSON serialized
            try:
                json.dumps(value)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Value must be JSON serializable: {str(e)}")

            # Check state size limit
            if len(self._state) >= self._max_state_size and key not in self._state:
                raise ValueError(f"State size limit ({self._max_state_size}) reached")

            # Create state entry
            entry = StateEntry(value, ttl)
            self._state[key] = entry
            
            logger.debug(f"Set state for key {key} with TTL {ttl}")
        except Exception as e:
            logger.error(f"Failed to set state for key {key}: {str(e)}")
            raise

    async def get_state(self, key: str) -> Optional[Any]:
        """Get state value."""
        try:
            entry = self._state.get(key)
            
            if not entry:
                return None
                
            if entry.is_expired():
                await self.delete_state(key)
                return None
                
            return entry.value
            
        except Exception as e:
            logger.error(f"Failed to get state for key {key}: {str(e)}")
            raise

    async def delete_state(self, key: str) -> None:
        """Delete state value."""
        try:
            if key in self._state:
                del self._state[key]
                logger.debug(f"Deleted state for key {key}")
        except Exception as e:
            logger.error(f"Failed to delete state for key {key}: {str(e)}")
            raise

    async def _cleanup_expired(self) -> None:
        """Periodically clean up expired state entries."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                
                # Find expired keys
                expired_keys = [
                    key for key, entry in self._state.items()
                    if entry.is_expired()
                ]
                
                # Delete expired entries
                for key in expired_keys:
                    await self.delete_state(key)
                    
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired state entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in state cleanup: {str(e)}")

    async def get_state_info(self) -> Dict[str, Any]:
        """Get information about current state."""
        try:
            current_time = datetime.utcnow()
            
            state_info = {
                "total_entries": len(self._state),
                "expired_entries": sum(
                    1 for entry in self._state.values()
                    if entry.is_expired()
                ),
                "ttl_entries": sum(
                    1 for entry in self._state.values()
                    if entry.expires_at is not None
                ),
                "entries": {
                    key: entry.to_dict()
                    for key, entry in self._state.items()
                }
            }
            
            return state_info
            
        except Exception as e:
            logger.error(f"Failed to get state info: {str(e)}")
            raise 