"""Example of integrating MCP System Context Server with LLMs."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

from mcp_system_context import SystemContextServer
from mcp_system_context.config import ServerConfig


class LLMContext:
    """Manages context collection for LLM interactions."""
    
    def __init__(self, server: SystemContextServer):
        """Initialize LLM context manager."""
        self.server = server
        self.context: Dict[str, Any] = {}
        
    async def collect_system_context(self) -> Dict[str, Any]:
        """Collect relevant system context."""
        # Get system information
        self.context["system_info"] = await self.server.system_monitor.get_system_info()
        
        # Get recent clipboard content
        clipboard_history = self.server.clipboard_manager.get_history(limit=5)
        self.context["clipboard"] = [
            {
                "content": entry.content,
                "timestamp": entry.timestamp.isoformat(),
                "type": entry.content_type
            } for entry in clipboard_history
        ]
        
        # Get recent shell commands
        self.context["shell_history"] = self.server.history_manager.get_shell_history(limit=10)
        
        # Get network status
        self.context["network"] = {
            "connections": [
                conn.dict() for conn in (await self.server.system_monitor.get_network_connections())[:5]
            ],
            "routes": [
                route.dict() for route in (await self.server.system_monitor.get_network_routes())
            ]
        }
        
        return self.context
        
    def format_for_llm(self) -> str:
        """Format context for LLM consumption."""
        sections = []
        
        # System Information
        if "system_info" in self.context:
            sections.append("=== System Information ===")
            for key, value in self.context["system_info"].items():
                sections.append(f"{key}: {value}")
        
        # Clipboard History
        if "clipboard" in self.context:
            sections.append("\n=== Recent Clipboard Content ===")
            for entry in self.context["clipboard"]:
                sections.append(f"[{entry['timestamp']}] {entry['content'][:100]}...")
        
        # Shell History
        if "shell_history" in self.context:
            sections.append("\n=== Recent Shell Commands ===")
            sections.extend(self.context["shell_history"])
        
        # Network Status
        if "network" in self.context:
            sections.append("\n=== Network Status ===")
            sections.append("Active Connections:")
            for conn in self.context["network"]["connections"]:
                sections.append(f"- {conn['protocol']} {conn['local_address']} -> {conn['remote_address']} ({conn['state']})")
        
        return "\n".join(sections)
        
    def save_context(self, path: str) -> None:
        """Save context to file."""
        with open(path, "w") as f:
            json.dump(self.context, f, indent=2, default=str)


async def main():
    """Run LLM integration example."""
    # Initialize server with configuration
    config = ServerConfig(
        allowed_paths=[Path.cwd()],
        vector_db={"collection_name": "llm_context"}
    )
    
    server = SystemContextServer(config)
    context_manager = LLMContext(server)
    
    # Collect context
    print("Collecting system context...")
    await context_manager.collect_system_context()
    
    # Save raw context
    context_manager.save_context("llm_context.json")
    print("\nRaw context saved to llm_context.json")
    
    # Display formatted context
    print("\nFormatted context for LLM:")
    print("-" * 50)
    print(context_manager.format_for_llm())
    print("-" * 50)
    
    # Example LLM prompt
    prompt = f"""
    You have access to the following system context:
    
    {context_manager.format_for_llm()}
    
    Based on this context, please:
    1. Summarize the system's current state
    2. Identify any potential issues or anomalies
    3. Suggest relevant commands or actions
    
    Please provide your response in a clear, structured format.
    """
    
    print("\nExample LLM Prompt:")
    print(prompt)


if __name__ == "__main__":
    asyncio.run(main()) 