"""Enhanced clipboard history management module."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import time

import pyperclip
from pydantic import BaseModel


class ClipboardEntry(BaseModel):
    """Clipboard history entry."""
    content: str
    timestamp: float
    content_type: str = "text"
    source: Optional[str] = None
    metadata: Dict = {}

    def to_dict(self):
        return {"timestamp": self.timestamp, "content": self.content, "content_type": self.content_type}

    @classmethod
    def from_dict(cls, data):
        entry = cls(content=data["content"])
        entry.timestamp = data["timestamp"]
        entry.content_type = data.get("content_type", "text")
        return entry


class ClipboardManager:
    """Manages clipboard history and operations."""
    
    def __init__(self, history_file: Optional[str] = None):
        """Initialize clipboard manager."""
        self.history_file = Path(
            history_file or "~/.mcp/clipboard_history.json"
        ).expanduser()
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._history: List[ClipboardEntry] = []
        self._max_history = 100
        self._load_history()
        
        # Start monitoring clipboard
        self._last_content = self.get_clipboard_content()
        
    def _load_history(self) -> None:
        """Load clipboard history from file."""
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text())
                self._history = [ClipboardEntry.from_dict(item) for item in data]
            except Exception as e:
                print(f"Error loading clipboard history: {e}")
                
    def _save_history(self) -> None:
        """Save clipboard history to file."""
        try:
            data = [entry.to_dict() for entry in self._history]
            self.history_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error saving clipboard history: {e}")
            
    def get_clipboard_content(self) -> str:
        """Get current clipboard content."""
        try:
            return pyperclip.paste() or ""
        except Exception as e:
            return f"Unable to access clipboard: {e}"
            
    def add_to_history(
        self,
        content: str,
        content_type: str = "text",
        source: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add content to clipboard history."""
        if not content or content == self._last_content:
            return
            
        entry = ClipboardEntry(
            content=content,
            timestamp=time.time(),
            content_type=content_type,
            source=source,
            metadata=metadata or {}
        )
        
        self._history.append(entry)
        self._last_content = content
        
        # Trim history if needed
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
            
        self._save_history()
        
    def get_history(
        self,
        limit: int = 10,
        content_type: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[ClipboardEntry]:
        """Get clipboard history with optional filtering."""
        history = self._history
        
        if content_type:
            history = [e for e in history if e.content_type == content_type]
        if source:
            history = [e for e in history if e.source == source]
            
        return history[-limit:]
        
    def search_history(
        self,
        query: str,
        limit: int = 10
    ) -> List[ClipboardEntry]:
        """Search clipboard history for content matching query."""
        matches = [
            entry for entry in self._history
            if query.lower() in entry.content.lower()
        ]
        return matches[-limit:]
        
    def clear_history(self) -> None:
        """Clear clipboard history."""
        self._history = []
        self._save_history()
        
    def monitor_clipboard(self) -> None:
        """Check for clipboard changes and update history."""
        try:
            current = self.get_clipboard_content()
            if current != self._last_content:
                self.add_to_history(current)
        except Exception as e:
            print(f"Clipboard monitoring error: {str(e)}")
            
    def copy_to_clipboard(self, content: str) -> None:
        """Copy content to clipboard and add to history."""
        try:
            pyperclip.copy(content)
            self.add_to_history(content, source="mcp")
        except Exception as e:
            print(f"Error copying to clipboard: {e}") 