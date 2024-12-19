# AnthropicClient

A comprehensive Python client for Anthropic's Claude API with integrated tools for development workflow automation.

## System Architecture

```mermaid
%%{init: {'theme': 'forest'}}%%
graph TD
    classDef core fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    classDef tool fill:#3498db,stroke:#2980b9,stroke-width:2px
    classDef agent fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    classDef interface fill:#f1c40f,stroke:#f39c12,stroke-width:2px

    AC[AnthropicClient]:::core --> |Manages Clipboard| CM[ClipboardManager]
    AC --> |File Operations| FH[FileHandler]
    AC --> |API Communication| AH[AnthropicHandler]
    AC --> |Configuration| TC[ToolConfigs]
    
    subgraph Core Components
        CM:::interface --> |DBus| KI[Klipper Integration]
        FH:::interface --> |I/O Operations| FS[File System]
        AH:::interface --> |HTTP/REST| API[Anthropic API]
    end
    
    subgraph Tools
        TC:::tool --> |Command Execution| BT[Bash Tool]
        TC --> |File Manipulation| TE[Text Editor]
        TC --> |GUI Automation| CU[Computer Use]
        TC --> |Documentation| DG[Diagram Generator]
    end
    
    subgraph Specialized Agents
        SA[SkeletonAgent]:::agent --> |Project Setup| AC
        NA[NamingAgent]:::agent --> |Naming Conventions| AC
        FA[FileAnnotator]:::agent --> |Code Analysis| AC
        AV[AggregateVersions]:::agent --> |Version Management| AC
    end
```

## Data Flow Process

```mermaid
%%{init: {'theme': 'forest'}}%%
sequenceDiagram
    participant User
    participant CM as ClipboardManager
    participant FH as FileHandler
    participant AC as AnthropicClient
    participant API as Anthropic API
    
    Note over User,API: Content Processing Flow
    
    User->>CM: Copy text/path
    activate CM
    
    CM->>CM: Analyze content type
    Note right of CM: Check if content is<br/>file path or text
    
    alt Is File Path
        CM->>FH: Request file contents
        activate FH
        FH->>FH: Validate path
        FH->>FH: Read file
        FH-->>CM: Return contents
        deactivate FH
    else Is Text
        CM->>CM: Prepare text content
    end
    
    CM->>AC: Submit for processing
    deactivate CM
    activate AC
    
    AC->>AC: Apply templates
    AC->>AC: Configure request
    
    AC->>API: Send API request
    activate API
    Note right of API: Process with<br/>Claude model
    API-->>AC: Return response
    deactivate API
    
    AC->>CM: Update clipboard
    deactivate AC
    
    CM-->>User: Notify completion
```

## Tool Integration Architecture

```mermaid
%%{init: {'theme': 'forest'}}%%
graph LR
    classDef primary fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    classDef secondary fill:#3498db,stroke:#2980b9,stroke-width:2px
    classDef operation fill:#e74c3c,stroke:#c0392b,stroke-width:2px

    subgraph Clipboard System
        CP[Copy]:::operation --> |Content| CM[ClipboardManager]:::primary
        CM --> |Result| PT[Paste]:::operation
        CM --> |Events| KL[Klipper]:::secondary
    end
    
    subgraph File System
        FH[FileHandler]:::primary --> |Read| RD[Read Operations]:::operation
        FH --> |Write| WR[Write Operations]:::operation
        FH --> |Check| VL[Path Validation]:::operation
        FH --> |Watch| FW[File Watcher]:::secondary
    end
    
    subgraph API Layer
        AH[AnthropicHandler]:::primary --> |Send| RQ[Request Handler]:::operation
        AH --> |Receive| RS[Response Parser]:::operation
        AH --> |Transform| PR[Content Processor]:::operation
        AH --> |Cache| CH[Response Cache]:::secondary
    end
    
    CM --> |File Content| FH
    FH --> |Processed Data| AH
    AH --> |Results| CM
```

## Agent State Management

```mermaid
%%{init: {'theme': 'forest'}}%%
stateDiagram-v2
    [*] --> Initialize: Start Agent
    Initialize --> LoadTools: Load Configurations
    LoadTools --> ValidateSetup: Check Dependencies
    
    state "Process Execution" as PE {
        [*] --> ContentAnalysis
        ContentAnalysis --> ToolSelection: Analyze Input
        ToolSelection --> ExecutionPrep: Select Tool
        ExecutionPrep --> Execution: Prepare Parameters
        Execution --> ResultValidation: Run Tool
        ResultValidation --> [*]: Validate Output
    }
    
    ValidateSetup --> PE: Setup Complete
    PE --> ResponseGeneration: Process Complete
    
    state "Response Handling" as RH {
        ResponseGeneration --> ContentFormatting: Format Output
        ContentFormatting --> ClipboardUpdate: Prepare Content
        ClipboardUpdate --> UserNotification: Update Clipboard
    }
    
    RH --> [*]: Complete
```

## Core Components

### AnthropicClient (`anthropic-client.py`)
- Main client interface for Anthropic API interactions
- Handles message creation, tool usage, and template management
- Supports system prompts, examples, and tool configurations
- Provides async API for all operations

### ClipboardManager
- Integrates with KDE's Klipper via DBus
- Handles clipboard content retrieval and setting
- Supports file path detection and content loading

### FileHandler
- Manages file system operations
- Handles file reading, writing, and path validation
- Supports various file formats (Python, JSON, YAML)

## Tools

### Bash Tool (`custom_bash.json`)
- Execute shell commands in a persistent environment
- Access to common Linux and Python packages
- State persistence across command calls

### Text Editor (`custom_text_editor.json`)
- View, create, and edit files
- Support for line-based operations
- File content manipulation with undo capability

### Computer Use (`custom_computer_use.json`)
- GUI automation capabilities
- Keyboard and mouse control
- Screenshot functionality

### Diagram Generator (`generate_diagram_tool.json`, `mermaid_generator.json`)
- Generate Mermaid diagrams for documentation
- Support for various diagram types and styles
- Automatic layout optimization

## Specialized Agents

### SkeletonAgent (`SkeletonAgent.json`)
- Pre-development planning and setup
- Project template selection
- Implementation plan generation
- Tool initialization and configuration

### NamingAgent (`NamingAgent.py`)
- Intelligent naming suggestions
- Context-aware naming patterns
- Consistency enforcement

### FileAnnotator (`FileAnnotator.py`)
- Code analysis and annotation
- Documentation generation
- Context-aware commenting

### AggregateVersions (`AggregateVersions.py`)
- Version comparison and merging
- Change tracking
- Conflict resolution

## Usage Examples

### Basic Message Creation
```python
from anthropic_client import AnthropicClient, MessageConfig

config = MessageConfig(
    model="claude-3-5-sonnet-20241022",
    max_tokens=8192,
    temperature=0
)

client = AnthropicClient(default_config=config)

# Create a simple message
message = await client.create_message(
    content="Hello, how can I help you?"
)
```

### Tool Usage
```python
# Use the bash tool
result = await client.create_tool_message(
    tool_name="custom_bash",
    tool_input={
        "command": "ls -la"
    }
)

# Use the text editor
result = await client.create_tool_message(
    tool_name="custom_text_editor",
    tool_input={
        "command": "view",
        "path": "/path/to/file.py"
    }
)
```

### Clipboard Integration
```python
# Process clipboard content
content = await client.clipboard_manager.get_clipboard_content()
if client.clipboard_manager.is_file_path(content):
    content = await client.file_handler.read_file_content(content)
    
response = await client.create_message(content=content)
await client.clipboard_manager.set_clipboard_content(response.content)
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AnthropicClient.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## Configuration

The client can be configured through:
- Environment variables
- YAML configuration files
- Runtime configuration objects

Example configuration:
```yaml
api:
  model: claude-3-5-sonnet-20241022
  max_tokens: 8192
  temperature: 0

templates_dir: templates/
tools_dir: tools/

logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## SkeletonAgent Analysis

The SkeletonAgent is a sophisticated pre-development planning assistant that orchestrates project initialization and setup. Here's a detailed analysis:

### API Integration Flow

```mermaid
%%{init: {'theme': 'forest'}}%%
sequenceDiagram
    participant Client
    participant SA as SkeletonAgent
    participant Tools as Tool Registry
    participant AC as Anthropic Client
    participant FS as File System
    
    rect rgb(191, 223, 255)
        Note over Client,FS: Initialization Phase
        Client->>SA: Initialize Agent
        SA->>Tools: Load Tool Configurations
        Tools-->>SA: Tool Definitions
        SA->>FS: Verify File Structure
    end
    
    rect rgb(200, 255, 200)
        Note over Client,FS: Query Analysis Phase
        Client->>SA: Submit Requirements
        SA->>AC: Analyze Requirements
        AC-->>SA: Pattern Suggestions
        SA->>FS: Load Templates
        FS-->>SA: Project Templates
        SA->>SA: Match Requirements to Templates
    end
    
    rect rgb(255, 228, 196)
        Note over Client,FS: Implementation Planning
        SA->>AC: Generate Implementation Plan
        AC-->>SA: Plan Details
        SA->>FS: Create Project Structure
        SA->>FS: Generate Documentation
        SA->>Client: Return Plan Summary
    end
```

### Tool Orchestration Architecture

```mermaid
%%{init: {'theme': 'forest'}}%%
graph TD
    classDef primary fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    classDef tool fill:#3498db,stroke:#2980b9,stroke-width:2px
    classDef output fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    
    SA[SkeletonAgent]:::primary
    
    subgraph Workflow Steps
        QA[Query Analysis]:::primary
        TI[Template Init]:::primary
        TL[Tools Init]:::primary
        IP[Implementation Plan]:::primary
        TU[Tool Usage Guide]:::primary
        RC[Review Changes]:::primary
    end
    
    subgraph Tools Integration
        CB[Custom Bash]:::tool
        CU[Computer Use]:::tool
        TE[Text Editor]:::tool
        DP[Diagram Planner]:::tool
        DG[Diagram Generator]:::tool
        AA[Async Anthropic]:::tool
    end
    
    subgraph Outputs
        PT[Project Template]:::output
        TS[Tool Setup]:::output
        PL[Project Layout]:::output
        DC[Documentation]:::output
        RV[Review Report]:::output
    end
    
    SA --> QA
    QA --> TI
    TI --> TL
    TL --> IP
    IP --> TU
    TU --> RC
    
    QA --> |Uses| TE
    TI --> |Uses| CB
    TI --> |Uses| DG
    TL --> |Uses| CB
    IP --> |Uses| TE
    TU --> |Uses| CB
    RC --> |Uses| CU
    
    QA --> PT
    TL --> TS
    IP --> PL
    TU --> DC
    RC --> RV
```

### API Usage Examples

1. **Initialize SkeletonAgent**:
```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=SkeletonAgent.system_prompt,
    messages=[{
        "role": "user",
        "content": "Initialize project setup for a new microservice"
    }]
)
```

2. **Query Analysis**:
```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": {
            "type": "tool_use",
            "step": "Query Analysis",
            "input": project_requirements,
            "templates": available_templates
        }
    }]
)
```

3. **Implementation Planning**:
```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": {
            "type": "tool_use",
            "step": "Implementation Plan Generation",
            "pattern": selected_pattern,
            "template": project_template,
            "tools": available_tools
        }
    }]
)
```

### Key Features

1. **Workflow Orchestration**
- Sequential step execution
- Tool coordination
- State management
- Output validation

2. **Tool Integration**
- Custom bash execution
- GUI automation
- File operations
- Diagram generation
- Async API calls

3. **Documentation Generation**
- Project structure
- Implementation plans
- Tool usage guides
- Review reports

4. **Template Management**
- Pattern matching
- Template initialization
- Custom template creation
- Template validation

## Documentation

For detailed development documentation, including component analysis, workflow diagrams, and best practices, see [DEVELOPMENT.md](docs/DEVELOPMENT.md).




