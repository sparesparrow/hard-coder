"""MCP System Context Server for providing contextual data to LLMs."""

from .server import SystemContextServer
from .config import ServerConfig
from .auth import AuthManager
from .storage.clipboard import ClipboardManager
from .storage.files import FileManager
from .storage.history import HistoryManager
from .system.monitor import SystemMonitor
from .vector.chroma import VectorManager

__version__ = "0.1.0"
__all__ = ["SystemContextServer"] 