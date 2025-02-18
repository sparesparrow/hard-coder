# System Context Monitor

A comprehensive system monitoring solution that combines real-time monitoring data with advanced cognitive workflows. This project integrates monitoring capabilities with context-aware processing, providing a modern and intelligent approach to system observation and analysis.

## Features

- **Real-time Monitoring**
  - Screenshot capture and analysis
  - Clipboard monitoring
  - Network activity tracking
  - System metrics collection

- **Cognitive Processing**
  - Context-aware workflow orchestration
  - Intelligent data aggregation
  - Pattern recognition and analysis
  - Adaptive monitoring based on context

- **Modern UI**
  - Real-time dashboard updates
  - Interactive workflow management
  - Context visualization
  - QR code-based context sharing

- **Security & Resource Management**
  - Secure data handling
  - Resource usage monitoring
  - Rate limiting and throttling
  - Access control and validation

## System Architecture

```mermaid
graph TD
    subgraph "Frontend Layer"
        UI[Dashboard UI]
        WM[Workflow Manager]
        CV[Context Viewer]
        MP[Monitoring Panel]
    end

    subgraph "Core Processing"
        CO[Cognitive Orchestrator]
        WE[Workflow Engine]
        subgraph "Monitoring Services"
            SS[Screenshot Service]
            NS[Network Service]
            CS[Clipboard Service]
        end
        RM[Resource Manager]
        MM[Metrics Manager]
    end

    subgraph "Data Management"
        DB[(Context Store)]
        MC[Memory Cache]
        MQ[Message Queue]
    end

    UI --> WM
    UI --> CV
    UI --> MP
    
    WM --> CO
    CO --> WE
    WE --> SS & NS & CS
    WE --> RM
    WE --> MM
    
    SS & NS & CS --> MQ
    MQ --> DB
    DB --> MC
    MC --> CO

    style UI fill:#2ecc71,stroke:#27ae60
    style CO fill:#e74c3c,stroke:#c0392b
    style WE fill:#3498db,stroke:#2980b9
    style RM fill:#f1c40f,stroke:#f39c12
    style MM fill:#9b59b6,stroke:#8e44ad
```

## Architecture

The system is built with a modular architecture following agentic design patterns:

```
SystemContextMonitor/
├── core/                    # Core system components
│   ├── agents/             # Agent composers and state managers
│   ├── cognitive/          # Cognitive processing tools
│   └── workflows/          # Predefined workflows
├── services/               # Service implementations
│   ├── monitoring/         # Monitoring services
│   └── context/           # Context management
├── frontend/              # React-based UI
└── infrastructure/        # Deployment configs
```

## Prerequisites

- Python 3.9+
- Node.js 16+
- Poetry (Python dependency management)
- npm or yarn (Node.js package management)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/system-context-monitor.git
   cd system-context-monitor
   ```

2. **Install Python dependencies**
   ```bash
   poetry install
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Development Setup

1. **Start the backend server**
   ```bash
   poetry shell
   python -m services.context.api
   ```

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:5173
   - API Documentation: http://localhost:8000/docs

## Usage

### Starting Monitoring

1. Launch the application
2. Navigate to the dashboard
3. Configure monitoring settings:
   - Screenshot interval
   - Network capture rules
   - Clipboard monitoring preferences

### Managing Workflows

1. Access the Workflow Manager
2. Create new workflows or select existing ones
3. Monitor workflow execution in real-time
4. View detailed results and analytics

### Accessing Context

1. Use the Context Viewer to explore current system state
2. Scan QR codes to share context across devices
3. Export context data for external analysis

## API Documentation

The system provides a comprehensive REST API and WebSocket interface:

### REST Endpoints

- `GET /api/context` - Retrieve current system context
- `POST /api/context` - Update system context
- `POST /api/workflows` - Execute cognitive workflow
- `GET /api/workflows/{id}` - Get workflow state

### WebSocket Events

- `context_update` - Real-time context updates
- `workflow_state` - Workflow execution updates
- `monitoring_data` - Live monitoring data

## Security Considerations

1. **Data Protection**
   - All sensitive data is encrypted
   - Secure WebSocket connections
   - Rate limiting on API endpoints

2. **Access Control**
   - Role-based access control
   - API key authentication
   - Session management

3. **Resource Management**
   - Monitoring rate limits
   - Storage quotas
   - CPU/Memory restrictions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Testing

Run the test suites:

```bash
# Backend tests
poetry run pytest

# Frontend tests
cd frontend
npm test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with FastAPI and React
- Uses Material-UI for frontend components
- Implements agentic design patterns
- Security standards based on OWASP guidelines





Below is the new `diagrams.md` file containing the requested Mermaid diagrams. All diagrams have been created following the Mermaid Diagram Generator standards (mermaid-generator.mdc), including proper syntax validation, incremental building, and style management.

---

# Diagrams for the System Context Monitor

This file includes multiple Mermaid diagrams documenting the architecture, workflows, and processes of our System Context Monitor codebase.

---

## 1. High-Level Code Structure Diagram

This diagram visualizes the overall directory structure and main modules in the project.

```mermaid
graph LR
    A[SystemContextMonitor]
    A --> B[core]
    A --> C[services]
    A --> D[frontend]
    A --> E[infrastructure]

    B --> B1[agents]
    B --> B2[cognitive]
    B --> B3[workflows]

    C --> C1[monitoring]
    C --> C2[context]

    D --> D1[Dashboard UI]
    D --> D2[Workflow Manager]
    D --> D3[Monitoring Panel]
```

---

## 2. System Monitoring Workflow Flow Diagram

This flowchart illustrates the process within the SystemMonitoringWorkflow—from context validation to service initialization, concurrent monitoring, and error handling.

```mermaid
flowchart TD
    A[Start Workflow Execution]
    B[Validate Context]
    C[Initialize Services]
    D[Setup Service Map]
    E[Create Service Instances]
    F[Start Monitoring]
    G[Run Services Concurrently]
    H[Return Initial State]
    I{Error Occurred?}
    J[Perform Cleanup]
    K[Stop All Services]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    G -- Error --> I
    I -- Yes --> J
    J --> K
```

---

## 3. Cognitive Orchestrator Workflow Execution Sequence Diagram

This sequence diagram details how the CognitiveOrchestrator executes a workflow, including context validation, resource checks, execution, and state updates.

```mermaid
sequenceDiagram
    participant Client
    participant Orchestrator
    participant Workflow
    Client->>Orchestrator: execute_workflow(workflow_id, context)
    Orchestrator->>Orchestrator: Validate context (Pydantic)
    Orchestrator->>Workflow: Instantiate workflow instance
    Orchestrator->>Orchestrator: Check resource limits
    Orchestrator->>Workflow: execute(context)
    Workflow-->>Orchestrator: Return results or error
    Orchestrator->>Orchestrator: Update state (completed/failed)
    Orchestrator-->>Client: Return execution_id
```

---

## 4. Context Management Flow Diagram

This diagram highlights the process of adding context data and notifying subscribers via the ContextShepherd module.

```mermaid
sequenceDiagram
    participant App
    participant Shepherd as ContextShepherd
    participant Subscriber
    App->>Shepherd: add_context(source, content, importance)
    Shepherd->>Shepherd: Validate context data
    Shepherd->>Subscriber: Notify subscriber of update
```

---

## 5. Monitoring Service Lifecycle Diagram

This flowchart outlines the lifecycle of a monitoring service—from initialization and metric collection to error handling and cleanup.

```mermaid
flowchart TD
    A[Initialize Monitoring Service]
    B[Start Service]
    C[Enter Monitoring Loop]
    D[Check Resource Usage]
    E[Collect Metric]
    F[Store Metric]
    G[Cleanup Old Metrics]
    H[Error Handling]
    I[Stop Service]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> C
    C -- Error --> H
    H --> I
```

---

## 6. Service Initialization Error Handling Diagram

This sequence diagram visualizes the error handling flow during service initialization, especially when configuration data is invalid.

```mermaid
sequenceDiagram
    participant Workflow as SystemMonitoringWorkflow
    participant Service as MonitoringService
    participant Logger
    Workflow->>Service: Create service instance with config
    Service->>Service: Validate configuration (e.g., output_dir exists)
    alt Config Valid
        Service-->>Workflow: Instance created successfully
    else Invalid Config
        Service-->>Workflow: Raise error ("dict' object has no attribute 'output_dir'")
        Workflow->>Logger: Log error
    end
```

---

## 7. Clipboard Service Monitoring Flow Diagram

This diagram shows the flow of clipboard monitoring—from periodic checking to detecting content changes and notifying subscribers.

```mermaid
sequenceDiagram
    participant Clipboard as ClipboardService
    participant Provider as pyperclip
    participant Handler as _handle_clipboard_change
    participant Subscriber
    Clipboard->>Provider: Get current content
    alt Content Changed
        Clipboard->>Handler: Process new content
        Handler->>Subscriber: Notify change
    else No Change
        Clipboard->>Clipboard: Continue monitoring
    end
```

---

## 8. Test Execution Flow Diagram

This diagram illustrates the overall test execution flow, highlighting service startup, workflow execution, error logging, and cleanup sequences.

```mermaid
sequenceDiagram
    participant TestRunner as run_tests.py
    participant Service as MonitoringService
    participant Workflow as SystemMonitoringWorkflow
    participant Logger
    TestRunner->>Service: Start service
    Service-->>TestRunner: Service started
    TestRunner->>Workflow: Execute workflow
    Workflow-->>Logger: Log error (e.g., resource limit exceeded)
    TestRunner->>Service: Stop service
    Service-->>TestRunner: Service stopped
```
