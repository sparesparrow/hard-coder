"""Basic usage example for MCP System Context Server."""

import asyncio
import os
from pathlib import Path

from mcp_system_context import SystemContextServer
from mcp_system_context.config import ServerConfig


async def main():
    """Run basic usage example."""
    # Create configuration
    config = ServerConfig(
        allowed_paths=[
            Path.home() / "projects",
            Path.home() / "Downloads"
        ],
        allowed_users=[os.getenv("USER")],
        path_patterns=["/tmp/*", "/var/log/*"],
        remote_enabled=True
    )
    
    # Save configuration for future use
    config.save_to_file("mcp_config.json")
    
    # Initialize server
    server = SystemContextServer(config)
    
    # Example: Monitor clipboard changes for 10 seconds
    print("Monitoring clipboard for 10 seconds...")
    await asyncio.sleep(10)
    history = server.clipboard_manager.get_history()
    print("\nClipboard History:")
    for entry in history:
        print(f"{entry.timestamp}: {entry.content[:50]}...")
    
    # Example: Get system information
    print("\nSystem Information:")
    info = await server.system_monitor.get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Example: Get network connections
    print("\nNetwork Connections:")
    connections = await server.system_monitor.get_network_connections()
    for conn in connections[:5]:  # Show first 5
        print(conn)
    
    # Example: Search shell history for 'git'
    print("\nRecent shell commands containing 'git':")
    matches = server.history_manager.search_history("git")
    for cmd in matches[:5]:  # Show first 5
        print(cmd)
    
    # Example: Add documents to vector DB and search
    docs = [
        "Example document for vector search",
        "Another document with different content",
        "Third document for testing"
    ]
    server.vector_manager.add_documents(
        collection_name="example",
        documents=docs,
        metadatas=[{"source": "example"} for _ in docs]
    )
    
    print("\nVector search results for 'example':")
    results = server.vector_manager.search(
        collection_name="example",
        query="example document"
    )
    for result in results:
        print(f"Match (distance={result.distance:.3f}): {result.document}")


if __name__ == "__main__":
    asyncio.run(main()) 