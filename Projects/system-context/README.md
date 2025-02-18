# MCP System Context Server

A Model Context Protocol (MCP) server that provides contextual data from the system environment to LLMs, including filesystem access, shell history, clipboard content, and semantic search capabilities.

## Features

- Secure filesystem access with path whitelisting
- Shell history and clipboard content access
- Vector database integration for semantic search
- Real-time directory monitoring
- Access control and user authorization
- Async operations for improved performance

## Installation

```bash
pip install mcp-system-context
```

## Configuration

Create a `.env` file with the following settings:

```env
MCP_ALLOWED_USERS=user1,user2
MCP_PATH_PATTERNS=/home/user/projects/*,/tmp/*
MCP_REMOTE_ENABLED=true
```

## Usage

Basic usage:

```python
from mcp_system_context import SystemContextServer

ALLOWED_PATHS = [
    "~/projects",
    "~/Downloads"
]

server = SystemContextServer(ALLOWED_PATHS)
server.run()
```

For more examples, see the [documentation](docs/).

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Security Considerations

- All paths are validated against whitelisted patterns
- User authorization is required
- Path traversal protection is implemented
- Secure handling of sensitive data

## Contributing

Please read [CONTRIBUTING.md](../../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 