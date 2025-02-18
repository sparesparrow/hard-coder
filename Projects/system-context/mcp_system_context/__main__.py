#!/usr/bin/env python3
"""
MCP System Context Server Entry Point

This script serves as the entry point for the MCP System Context Server,
which provides system context information to MCP clients.
"""

import os
import asyncio
import logging
from pathlib import Path
from mcp_system_context import SystemContextServer
from mcp_system_context.config import ServerConfig
import sys

async def async_main():
    """Async main entry point for the MCP System Context Server."""
    # Default allowed paths - can be overridden by config
    default_paths = [
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/projects"),
    ]
    
    try:
        # Load config from environment/file
        config = ServerConfig(
            allowed_paths=default_paths,
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO")
        )
        
        # Initialize server
        server = SystemContextServer(config)
        
        if os.getenv("MCP_REMOTE_ENABLED"):
            server._enable_remote_transport()
            
        # Run server
        await server.run()
        
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        raise

def main():
    """Main entry point that runs the async main function."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
