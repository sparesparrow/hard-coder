"""File system operations module."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

from pydantic import BaseModel

from ..auth import AuthManager


class FileMetadata(BaseModel):
    """Metadata for a file or directory entry."""
    name: str
    type: str
    size: int
    modified: datetime
    permissions: str
    error: Optional[str] = None


class FileManager:
    """Manage file system operations with path validation via the provided auth manager."""
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager

    def read_file(self, path_obj: Path) -> str:
        """Read and return content from the given file."""
        self.auth_manager.validate_path(path_obj)
        try:
            with open(path_obj, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {path_obj}: {e}")

    def list_directory(self, path_obj: Path) -> list:
        """List directory contents (filenames) for the given directory path."""
        self.auth_manager.validate_path(path_obj)
        if not path_obj.is_dir():
            raise NotADirectoryError(f"{path_obj} is not a directory")
        try:
            return [p.name for p in path_obj.iterdir()]
        except Exception as e:
            raise IOError(f"Failed to list directory {path_obj}: {e}")

    def monitor_directory(self, path: str, on_change_callback):
        """Monitor a directory for changes and call the provided callback upon events."""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                on_change_callback(event)
            def on_created(self, event):
                on_change_callback(event)

        observer = Observer()
        event_handler = Handler()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        return observer 