"""Shell history and clipboard operations module."""

import os
from pathlib import Path
from typing import List, Optional
import subprocess
from collections import deque

import pyperclip


class HistoryManager:
    """Manage shell command history operations."""
    
    def __init__(self, history_file: str = "~/.bash_history", max_entries: int = 1000):
        self.history_file = os.path.expanduser(history_file)
        self.max_entries = max_entries
        self._history = deque(maxlen=self.max_entries)
        self.load_history()
        
    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._history.append(line)
        except Exception as e:
            print(f"Error loading shell history: {e}")

    def get_shell_history(self) -> list:
        """Return the list of shell history commands."""
        return list(self._history)
    
    def search_history(self, pattern: str) -> list:
        """Search for commands in history that contain the given pattern."""
        return [cmd for cmd in self._history if pattern in cmd]
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content."""
        try:
            return pyperclip.paste() or "Clipboard is empty"
        except Exception as e:
            return f"Unable to access clipboard: {e}" 