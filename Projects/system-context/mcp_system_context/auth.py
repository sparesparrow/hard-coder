"""Authentication and authorization module for MCP System Context Server."""

import os
import pwd
import re
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


class AuthConfig(BaseModel):
    """Configuration for authentication and authorization."""
    allowed_users: List[str]
    allowed_paths: List[Path]
    path_patterns: List[str] = []

    @classmethod
    def from_env(cls) -> "AuthConfig":
        """Create AuthConfig from environment variables."""
        allowed_users = os.getenv("MCP_ALLOWED_USERS", "").split(",")
        path_patterns = os.getenv("MCP_PATH_PATTERNS", "").split(",")
        
        return cls(
            allowed_users=allowed_users,
            allowed_paths=[],  # Will be set after initialization
            path_patterns=[p for p in path_patterns if p]
        )


class AuthManager:
    """Manage user authorization and path validations."""
    
    def __init__(self, allowed_paths):
        self.allowed_paths = [Path(p).resolve() for p in allowed_paths]

    def validate_path(self, path_obj: Path) -> None:
        """Validate if the provided path is within the allowed paths. Raise an error if not allowed."""
        resolved_path = path_obj.resolve()
        if not any(str(resolved_path).startswith(str(allowed)) for allowed in self.allowed_paths):
            raise PermissionError(f"Access denied for path: {resolved_path}")
    
    def is_path_allowed(self, path: Path) -> bool:
        """Check if a path is within allowed directories."""
        path = path.resolve()
        
        # Check for path traversal attempts
        if ".." in str(path):
            return False
            
        # Check against allowed paths
        return any(
            str(path).startswith(str(allowed_path))
            for allowed_path in self.allowed_paths
        )
    
    def get_current_user(self) -> str:
        """Get current user name."""
        return pwd.getpwuid(os.getuid()).pw_name 