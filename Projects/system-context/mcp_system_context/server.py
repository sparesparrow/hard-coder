"""Main server module for MCP System Context Server."""

import asyncio
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, JSONRPCError

from .auth import AuthManager
from .config import ServerConfig
from .storage.files import FileManager
from .storage.clipboard import ClipboardManager
from .storage.history import HistoryManager
from .system.monitor import SystemMonitor
from .vector.chroma import VectorManager, SearchResult


class SystemContextServer:
    """MCP server providing system context to LLMs."""
    
    def __init__(
        self,
        config: Optional[Union[ServerConfig, List[str]]] = None,
        env_file: Optional[str] = None
    ):
        """Initialize the system context server."""
        load_dotenv(env_file)
        
        # Handle legacy initialization with allowed_paths
        if isinstance(config, list):
            self.config = ServerConfig(allowed_paths=config)
        elif isinstance(config, ServerConfig):
            self.config = config
        else:
            self.config = ServerConfig()
            
        # Set up logging
        logging.basicConfig(level=self.config.log_level)
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        self.config.create_directories()
        
        # Initialize managers
        self.auth_manager = AuthManager(self.config.allowed_paths)
        self.file_manager = FileManager(self.auth_manager)
        self.history_manager = HistoryManager()
        self.clipboard_manager = ClipboardManager(
            str(self.config.clipboard.history_file)
        )
        self.system_monitor = SystemMonitor()
        self.vector_manager = VectorManager(
            str(self.config.vector_db.persist_directory)
        )
        
        # Initialize MCP server
        self.mcp = FastMCP("system-context")
        self._setup_resources()
        self._setup_tools()
        
        # Start clipboard monitoring if enabled
        if self.config.clipboard.monitor_interval > 0:
            self._start_clipboard_monitor()
            
    def _start_clipboard_monitor(self):
        """Start monitoring clipboard changes."""
        async def monitor():
            while True:
                try:
                    self.clipboard_manager.monitor_clipboard()
                    await asyncio.sleep(self.config.clipboard.monitor_interval)
                except Exception as e:
                    self.logger.error(f"Error monitoring clipboard: {e}")
                    await asyncio.sleep(1)
                    
        asyncio.create_task(monitor())
        
    def _setup_resources(self):
        """Set up MCP resources."""
        @self.mcp.resource("shell://history")
        def get_shell_history() -> str:
            """Get recent shell command history."""
            return "\n".join(self.history_manager.get_shell_history())
            
        @self.mcp.resource("clipboard://current")
        def get_clipboard() -> str:
            """Get current clipboard content."""
            return self.clipboard_manager.get_clipboard_content()
            
        @self.mcp.resource("clipboard://history")
        def get_clipboard_history() -> str:
            """Get clipboard history."""
            history = self.clipboard_manager.get_history()
            return "\n".join(
                f"{entry.timestamp}: {entry.content[:100]}..."
                for entry in history
            )
            
        @self.mcp.resource("system://logs/{unit}")
        async def get_system_logs(unit: str) -> str:
            """Get systemd logs for a unit."""
            result = await self.system_monitor.get_systemd_logs(
                unit=unit,
                since="1h"  # TODO: Make configurable
            )
            return result.output
            
        @self.mcp.resource("system://network/connections")
        async def get_network_connections() -> str:
            """Get network connections."""
            connections = await self.system_monitor.get_network_connections()
            return "\n".join(str(conn) for conn in connections)
            
        @self.mcp.resource("system://network/routes")
        async def get_network_routes() -> str:
            """Get network routes."""
            routes = await self.system_monitor.get_network_routes()
            return "\n".join(str(route) for route in routes)
            
        @self.mcp.resource("context://vector-db/collections/{collection_name}")
        def get_vector_db_collection(collection_name: str) -> List[SearchResult]:
            """Access a specific collection in the vector database."""
            return self.vector_manager.get_or_create_collection(collection_name)
            
        @self.mcp.resource("file://{path}")
        def get_file_resource(path: str) -> Union[TextContent, JSONRPCError]:
            """Access a file or directory."""
            path_obj = Path(path).resolve()
            if not self._is_path_allowed(path_obj):
                return JSONRPCError(code=403, message=f"Access denied to {path}")

            if path_obj.is_file():
                try:
                    with open(path_obj, 'r', encoding='utf-8') as f:
                        return TextContent(content=f.read())
                except Exception as e:
                    return JSONRPCError(code=500, message=str(e))
            elif path_obj.is_dir():
                # Return directory listing as a structured object
                entries = []
                for entry in path_obj.iterdir():
                    try:
                        stat = entry.stat()
                        entries.append({
                            "name": entry.name,
                            "type": "directory" if entry.is_dir() else "file",
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "permissions": oct(stat.st_mode)[-3:]
                        })
                    except Exception as e:
                        entries.append({
                            "name": entry.name,
                            "error": str(e)
                        })
                return TextContent(content=json.dumps(entries))
            else:
                return JSONRPCError(code=404, message=f"Not found: {path}")
                
    def _setup_tools(self):
        """Set up MCP tools."""
        @self.mcp.tool()
        def list_directory(path: str) -> str:
            """List contents of a directory."""
            entries = self.file_manager.list_directory(path)
            return "\n".join(str(entry) for entry in entries)
            
        @self.mcp.tool()
        def read_file(path: str) -> str:
            """Read contents of a file."""
            return self.file_manager.read_file(path)
            
        @self.mcp.tool()
        def search_history(pattern: str) -> str:
            """Search shell history for a pattern."""
            matches = self.history_manager.search_history(pattern)
            return "\n".join(matches) if matches else "No matching commands found."
            
        @self.mcp.tool()
        def search_clipboard(query: str) -> str:
            """Search clipboard history."""
            matches = self.clipboard_manager.search_history(query)
            return "\n".join(
                f"{entry.timestamp}: {entry.content}"
                for entry in matches
            )
            
        @self.mcp.tool()
        def copy_to_clipboard(content: str) -> str:
            """Copy content to clipboard."""
            self.clipboard_manager.copy_to_clipboard(content)
            return f"Copied to clipboard: {content[:100]}..."
            
        @self.mcp.tool()
        async def get_system_info() -> str:
            """Get system information."""
            info = await self.system_monitor.get_system_info()
            return "\n".join(f"{k}: {v}" for k, v in info.items())
            
        @self.mcp.tool()
        async def get_process_list() -> str:
            """Get list of running processes."""
            result = await self.system_monitor.get_process_list()
            return result.output
            
        @self.mcp.tool()
        def search_files(query: str, max_results: int = 5) -> str:
            """Semantic search across documents."""
            results = self.vector_manager.search(
                collection_name=self.config.vector_db.collection_name,
                query=query,
                n_results=max_results
            )
            return "\n".join(str(result) for result in results)
            
        @self.mcp.tool()
        async def monitor_directory(path: str) -> None:
            """Watch directory for changes and maintain knowledge graph."""
            def on_change(event):
                if event.is_directory:
                    return
                    
                try:
                    content = self.file_manager.read_file(event.src_path)
                    self.vector_manager.add_documents(
                        collection_name=self.config.vector_db.collection_name,
                        documents=[content],
                        metadatas=[{"path": event.src_path}]
                    )
                except Exception as e:
                    self.logger.error(f"Error processing change: {e}")
                    
            observer = await self.file_manager.monitor_directory(path, on_change)
            try:
                while True:
                    await asyncio.sleep(1)
            finally:
                observer.stop()
                observer.join()
                
    async def run(self):
        """Run the MCP server."""
        if self.config.remote_enabled:
            self.logger.info("Remote access enabled")
            self._enable_remote_transport()

        self.logger.info("Starting MCP System Context Server")
        await self.mcp.run()
        
    def _enable_remote_transport(self):
        """Enable remote transport by starting a FastAPI server in a background thread."""
        from fastapi import FastAPI
        import uvicorn
        import threading

        app = FastAPI()

        @app.get("/")
        async def read_root():
            return {"message": "MCP Remote Transport Active"}

        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

        self.logger.info("Starting remote transport server on port 8080")
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

def main():
    """Entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP System Context Server")
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--env-file",
        help="Path to environment file"
    )
    parser.add_argument(
        "--allowed-paths",
        nargs="+",
        help="List of allowed paths (legacy mode)"
    )
    
    args = parser.parse_args()
    
    if args.config:
        config = ServerConfig.load_from_file(args.config)
    elif args.allowed_paths:
        config = args.allowed_paths
    else:
        config = None
        
    server = SystemContextServer(config, env_file=args.env_file)
    asyncio.run(server.run())
    
if __name__ == "__main__":
    main() 