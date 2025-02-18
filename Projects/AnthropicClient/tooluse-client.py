from typing import List, Dict, Any, Optional, Union
import asyncio
import logging
import anyio
from datetime import datetime
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ToolExecutionError(Exception):
    """Custom exception for tool execution failures"""
    pass

class MCPClient:
    """Enhanced client for interacting with MCP tools server"""
    
    def __init__(self, default_timeout: int = 10):
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self.default_timeout = default_timeout
        self._tool_stats: Dict[str, Dict[str, Union[int, float]]] = {}

    def _log_tool_stats(self, tool_name: str, duration: float, success: bool):
        """Track statistics for tool usage"""
        if tool_name not in self._tool_stats:
            self._tool_stats[tool_name] = {
                'calls': 0,
                'successes': 0,
                'failures': 0,
                'total_duration': 0.0
            }
        
        stats = self._tool_stats[tool_name]
        stats['calls'] += 1
        stats['total_duration'] += duration
        if success:
            stats['successes'] += 1
        else:
            stats['failures'] += 1

    async def connect(self, server_script_path: str):
        """Establish connection to MCP server with enhanced logging and validation"""
        try:
            logger.info(f"Initiating connection to server at: {server_script_path}")
            
            # Configure server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                env=None
            )

            async def receive_loop(session: ClientSession):
                """Enhanced message handling loop with detailed logging"""
                logger.info("Starting message receive loop")
                try:
                    async for message in session.incoming_messages:
                        if isinstance(message, Exception):
                            logger.error(f"Error received from server: {message}", exc_info=True)
                            continue
                        
                        logger.debug(f"Received message from server: {message}")
                        
                        # Additional message validation could be added here
                        if not message:
                            logger.warning("Received empty message from server")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error in receive loop: {str(e)}", exc_info=True)
                    raise

            # Create session using the SDK's pattern
            async with stdio_client(server_params) as streams:
                async with ClientSession(*streams) as session:
                    self.session = session
                    
                    logger.info("Starting message handling loop")
                    async with anyio.create_task_group() as tg:
                        tg.start_soon(receive_loop, session)
                        
                        # Initialize session with timeout
                        logger.info("Initializing session")
                        try:
                            await asyncio.wait_for(
                                session.initialize(),
                                timeout=self.default_timeout
                            )
                            logger.info("Session initialized successfully")
                        except asyncio.TimeoutError:
                            logger.error("Session initialization timed out")
                            raise
                        
                        # List and validate available tools
                        try:
                            response = await asyncio.wait_for(
                                session.list_tools(),
                                timeout=self.default_timeout
                            )
                            self.available_tools = response.tools
                            logger.info(f"Found {len(self.available_tools)} tools:")
                            for tool in self.available_tools:
                                logger.info(f"  - {tool.name}: {tool.description}")
                        except asyncio.TimeoutError:
                            logger.error("Tool listing timed out")
                            raise
                        
                        return True

        except Exception as e:
            logger.error(f"Connection failed: {str(e)}", exc_info=True)
            raise

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], timeout: Optional[int] = None) -> Any:
        """Generic tool execution method with timing and error handling"""
        if not self.session:
            raise RuntimeError("Client not connected to server")

        # Validate tool exists
        if not any(tool.name == tool_name for tool in self.available_tools):
            raise ValueError(f"Tool '{tool_name}' not found in available tools")

        timeout = timeout or self.default_timeout
        start_time = datetime.now()
        success = False

        try:
            logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")
            
            result = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments),
                timeout=timeout
            )
            
            logger.info(f"Tool '{tool_name}' executed successfully")
            success = True
            return result

        except asyncio.TimeoutError:
            logger.error(f"Tool execution timed out after {timeout} seconds")
            raise ToolExecutionError(f"Tool '{tool_name}' execution timed out")
        
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
            raise ToolExecutionError(f"Tool '{tool_name}' execution failed: {str(e)}")
        
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            self._log_tool_stats(tool_name, duration, success)

    async def execute_computer_action(self, action: str, coordinates: Optional[List[int]] = None):
        """Execute a computer interaction action"""
        args = {"action": action}
        if coordinates:
            args["coordinate"] = coordinates
        
        return await self.execute_tool("anthropic_computer_use", args)

    async def execute_bash_command(self, command: str):
        """Execute a bash command"""
        return await self.execute_tool("anthropic_bash", {"command": command})

    async def edit_text_file(self, path: str, command: str, **kwargs):
        """Interact with the text editor"""
        args = {"path": path, "command": command, **kwargs}
        return await self.execute_tool("anthropic_text_editor", args)

    def get_tool_stats(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """Get statistics about tool usage"""
        return self._tool_stats

async def main():
    """Example usage of the enhanced MCP client"""
    client = MCPClient(default_timeout=10)  # 10 second default timeout
    try:
        # Connect to your server
        server_path = '/home/sparrow/projects/hard-coder/Projects/AnthropicClient/tooluse.py'
        await client.connect(server_path)

        # Execute tools with automatic logging and timeout handling
        try:
            result = await client.execute_computer_action("right_click")
            print(result)
        except ToolExecutionError as e:
            print(f"Tool execution failed: {e}")

        # Get statistics about tool usage
        stats = client.get_tool_stats()
        print(stats)
        # Example: Execute a computer action with timeout
        try:
            result = await client.execute_computer_action("right_click", timeout=5)
            logger.info(f"Computer action result: {result}")
        except ToolExecutionError as e:
            logger.error(f"Computer action failed: {str(e)}")

        # Example: Execute a bash command
        try:
            result = await client.execute_bash_command("ls -la")
            logger.info(f"Bash command result: {result}")
        except ToolExecutionError as e:
            logger.error(f"Bash command failed: {str(e)}")

        # Example: View a text file
        try:
            result = await client.edit_text_file("/path/to/file.txt", "view")
            logger.info(f"Text editor result: {result}")
        except ToolExecutionError as e:
            logger.error(f"Text editor operation failed: {str(e)}")

        # Print tool usage statistics
        logger.info("Tool execution statistics:")
        for tool_name, stats in client.get_tool_stats().items():
            logger.info(f"{tool_name}: {stats}")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())