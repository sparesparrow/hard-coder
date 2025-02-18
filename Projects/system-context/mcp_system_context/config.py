"""Configuration management for MCP System Context Server."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ClipboardConfig(BaseModel):
    """Clipboard manager configuration."""
    max_history: int = Field(default=100, gt=0)
    history_file: Path = Field(
        default=Path("~/.mcp/clipboard_history.json").expanduser()
    )
    monitor_interval: float = Field(default=1.0, gt=0)
    save_on_change: bool = Field(default=True)


class SystemMonitorConfig(BaseModel):
    """System monitor configuration."""
    max_command_history: int = Field(default=1000, gt=0)
    default_log_lines: int = Field(default=100, gt=0)
    command_timeout: float = Field(default=5.0, gt=0)
    default_log_since: str = Field(default="1h")
    allowed_commands: List[str] = Field(default=[
        "journalctl", "ss", "ip", "ps", "hostname", 
        "uname", "free", "df"
    ])


class VectorDBConfig(BaseModel):
    """Vector database configuration."""
    persist_directory: Path = Field(
        default=Path("~/.mcp/vector_db").expanduser()
    )
    collection_name: str = Field(default="files")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    anonymized_telemetry: bool = Field(default=False)


class ServerConfig(BaseSettings):
    """Main server configuration."""
    allowed_paths: List[Path] = Field(default_factory=lambda: [
        Path("~/projects").expanduser()
    ])
    allowed_users: List[str] = Field(default_factory=list)
    path_patterns: List[str] = Field(default_factory=list)
    remote_enabled: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    clipboard: ClipboardConfig = Field(default_factory=ClipboardConfig)
    system_monitor: SystemMonitorConfig = Field(
        default_factory=SystemMonitorConfig
    )
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    
    class Config:
        """Pydantic config."""
        env_prefix = "MCP_"
        env_nested_delimiter = "__"
        
    @classmethod
    def from_env_file(cls, env_file: Optional[str] = None) -> "ServerConfig":
        """Create config from environment file."""
        if env_file:
            return cls(_env_file=env_file)
        return cls()
        
    def save_to_file(self, path: str) -> None:
        """Save configuration to file."""
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=2))
            
    @classmethod
    def load_from_file(cls, path: str) -> "ServerConfig":
        """Load configuration from file."""
        with open(path) as f:
            return cls.model_validate_json(f.read())
            
    def create_directories(self) -> None:
        """Create necessary directories."""
        self.clipboard.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.vector_db.persist_directory.mkdir(parents=True, exist_ok=True) 