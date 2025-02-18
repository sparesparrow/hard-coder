FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY mcp_system_context ./mcp_system_context

# Install Python dependencies
RUN pip install --no-cache-dir .

# Create non-root user
RUN useradd -m -r -s /bin/bash mcp
USER mcp

# Create data directory for vector DB
RUN mkdir -p /home/mcp/data
ENV MCP_CONTEXT_DB_PATH=/home/mcp/data

# Set environment variables
ENV MCP_ALLOWED_USERS=mcp
ENV MCP_PATH_PATTERNS=/home/mcp/*
ENV MCP_REMOTE_ENABLED=true

# Expose port if needed
EXPOSE 8080

# Run the server
ENTRYPOINT ["python", "-m", "mcp_system_context"]
CMD ["--allowed-paths", "/home/mcp"] 
