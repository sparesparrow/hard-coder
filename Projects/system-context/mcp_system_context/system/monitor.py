"""System monitoring and information collection module."""

import asyncio
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class SystemCommand(BaseModel):
    """System command execution result."""
    command: str
    output: str
    timestamp: datetime
    exit_code: int
    error: Optional[str] = None


class NetworkConnection(BaseModel):
    """Network connection information."""
    protocol: str
    local_address: str
    remote_address: str
    state: str
    process: Optional[str] = None


class NetworkRoute(BaseModel):
    """Network route information."""
    destination: str
    gateway: str
    interface: str
    metric: Optional[int] = None


class SystemMonitor:
    """Monitors and collects system information."""

    def __init__(self):
        """Initialize system monitor."""
        self._command_history: List[SystemCommand] = []
        self._max_history = 1000

    async def _run_command(self, command: str) -> SystemCommand:
        """Run a system command asynchronously."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return SystemCommand(
                command=command,
                output=stdout.decode(),
                timestamp=datetime.now(),
                exit_code=process.returncode,
                error=stderr.decode() if stderr else None
            )
        except Exception as e:
            return SystemCommand(
                command=command,
                output="",
                timestamp=datetime.now(),
                exit_code=-1,
                error=str(e)
            )

    def _add_to_history(self, result: SystemCommand) -> None:
        """Add command result to history."""
        self._command_history.append(result)
        if len(self._command_history) > self._max_history:
            self._command_history.pop(0)

    async def get_systemd_logs(
        self, 
        unit: Optional[str] = None, 
        since: str = "1h"
    ) -> SystemCommand:
        """Get systemd/journalctl logs."""
        command = f"journalctl -n 100 --no-pager"
        if unit:
            command += f" -u {unit}"
        if since:
            command += f" --since '{since}'"
            
        result = await self._run_command(command)
        self._add_to_history(result)
        return result

    async def get_network_connections(self) -> List[NetworkConnection]:
        """Get current network connections using ss."""
        result = await self._run_command("ss -tupn")
        self._add_to_history(result)
        
        connections = []
        if result.exit_code == 0:
            lines = result.output.split("\n")[1:]  # Skip header
            for line in lines:
                if not line.strip():
                    continue
                try:
                    parts = line.split()
                    if len(parts) >= 5:
                        connections.append(NetworkConnection(
                            protocol=parts[0],
                            local_address=parts[4],
                            remote_address=parts[5] if len(parts) > 5 else "",
                            state=parts[1],
                            process=parts[-1] if "users" in line else None
                        ))
                except Exception as e:
                    print(f"Error parsing connection: {e}")
                    
        return connections

    async def get_network_routes(self) -> List[NetworkRoute]:
        """Get network routing table."""
        result = await self._run_command("ip route show")
        self._add_to_history(result)
        
        routes = []
        if result.exit_code == 0:
            for line in result.output.split("\n"):
                if not line.strip():
                    continue
                try:
                    parts = line.split()
                    routes.append(NetworkRoute(
                        destination=parts[0],
                        gateway=parts[2] if "via" in line else "",
                        interface=parts[-1],
                        metric=int(parts[parts.index("metric") + 1]) 
                            if "metric" in line else None
                    ))
                except Exception as e:
                    print(f"Error parsing route: {e}")
                    
        return routes

    async def get_process_list(self) -> SystemCommand:
        """Get list of running processes."""
        result = await self._run_command("ps aux --no-headers")
        self._add_to_history(result)
        return result

    async def get_system_info(self) -> Dict[str, str]:
        """Get general system information."""
        info = {}
        
        # Get hostname
        hostname = await self._run_command("hostname")
        if hostname.exit_code == 0:
            info["hostname"] = hostname.output.strip()
            
        # Get kernel version
        uname = await self._run_command("uname -a")
        if uname.exit_code == 0:
            info["kernel"] = uname.output.strip()
            
        # Get memory info
        free = await self._run_command("free -h")
        if free.exit_code == 0:
            info["memory"] = free.output.strip()
            
        # Get disk usage
        df = await self._run_command("df -h")
        if df.exit_code == 0:
            info["disk"] = df.output.strip()
            
        return info

    def get_command_history(self, limit: int = 10) -> List[SystemCommand]:
        """Get history of executed commands."""
        return self._command_history[-limit:] 