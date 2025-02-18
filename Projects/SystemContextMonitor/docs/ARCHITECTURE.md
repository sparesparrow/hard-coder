# System Architecture Documentation

## Overview

The System Context Monitor is built using a modern, scalable architecture that emphasizes real-time monitoring, efficient state management, and robust error handling.

## System Components

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#2ecc71',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#27ae60',
      'lineColor': '#3498db',
      'secondaryColor': '#ff0000'
    }
  }
}%%
graph TD
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef primary fill:#2ecc71,stroke:#27ae60,color:#fff;
    classDef secondary fill:#3498db,stroke:#2980b9,color:#fff;
    classDef storage fill:#e74c3c,stroke:#c0392b,color:#fff;

    subgraph "Frontend Layer" ["Frontend Layer"]
        UI[React UI]
        Store[Zustand Store]
        MCP[MCP Provider]
        ErrorB[Error Boundaries]
        
        UI --> Store
        UI --> MCP
        UI --> ErrorB
    end

    subgraph "API Layer" ["API Layer"]
        API[FastAPI Server]
        WS[WebSocket Server]
        Auth[Authentication]
        Rate[Rate Limiter]
        
        API --> WS
        API --> Auth
        API --> Rate
    end

    subgraph "Service Layer" ["Service Layer"]
        MS[Monitoring Service]
        CS[Context Service]
        WF[Workflow Service]
        
        MS --> CS
        WF --> CS
    end

    subgraph "Data Layer" ["Data Layer"]
        Cache[Redis Cache]
        DB[State Store]
        Queue[Message Queue]
        
        Cache --> DB
        Queue --> DB
    end

    UI <--> API
    MCP <--> WS
    API <--> MS
    API <--> WF
    MS --> Queue
    WF --> Queue

    class UI,Store,MCP,ErrorB primary;
    class API,WS,Auth,Rate secondary;
    class MS,CS,WF secondary;
    class Cache,DB,Queue storage;
```

## Component Details

### Frontend Components

1. **Dashboard (SystemContextDashboard)**
   - Main application container
   - Manages global state and routing
   - Handles error boundaries

2. **Monitoring Panel**
   - Displays real-time monitoring data
   - Manages tab-based navigation
   - Handles data visualization

3. **Context Viewer**
   - Shows current system context
   - Provides context manipulation
   - Real-time updates

4. **Workflow Manager**
   - Workflow CRUD operations
   - Status monitoring
   - Error handling

5. **QR Display**
   - Context sharing
   - Mobile integration
   - Dynamic updates

### State Management

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#3498db',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#2980b9',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c'
    }
  }
}%%
graph LR
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef store fill:#3498db,stroke:#2980b9,color:#fff;
    classDef cache fill:#e74c3c,stroke:#c0392b,color:#fff;
    classDef queue fill:#f1c40f,stroke:#f39c12,color:#fff;

    subgraph "Frontend State"
        ZS[Zustand Store]
        MC[MCP Context]
        LC[Local Cache]
        
        ZS --> MC
        ZS --> LC
    end

    subgraph "Backend State"
        RS[Redis Store]
        PS[Persistent Store]
        MQ[Message Queue]
        
        RS --> PS
        MQ --> PS
    end

    ZS <--> RS
    MC <--> MQ

    class ZS,MC store;
    class LC,RS,PS cache;
    class MQ queue;

    linkStyle default stroke-width:2px;
```

### Data Flow

1. **Monitoring Data Flow**
   ```mermaid
   %%{
     init: {
       'theme': 'base',
       'themeVariables': {
         'primaryColor': '#3498db',
         'primaryTextColor': '#fff',
         'primaryBorderColor': '#2980b9',
         'lineColor': '#2c3e50',
         'secondaryColor': '#e74c3c',
         'tertiaryColor': '#2ecc71'
       }
     }
   }%%
   sequenceDiagram
       participant UI as Frontend UI
       participant API as API Gateway
       participant MS as Monitoring Service
       participant Q as Message Queue
       participant DB as State Store
       
       autonumber
       
       Note over UI,API: Real-time Monitoring Flow
       UI->>+API: Request monitoring data
       API->>+MS: Forward request
       MS->>Q: Publish data
       Q->>DB: Store data
       DB-->>UI: Send updates via WebSocket
       
       Note over MS,DB: Async Processing
       MS->>MS: Process metrics
       MS->>Q: Publish metrics
       Q->>DB: Store metrics
       
       Note over UI,DB: Error Handling
       alt Error occurs
           DB-->>API: Error notification
           API-->>UI: Display error
       else Success
           DB-->>UI: Confirmation
       end
   ```

2. **Workflow Execution Flow**
   ```mermaid
   sequenceDiagram
       participant UI as Frontend
       participant WF as Workflow Service
       participant CS as Context Service
       participant DB as Database
       
       UI->>WF: Execute workflow
       WF->>CS: Get context
       CS->>DB: Update state
       DB-->>UI: Send state update
   ```

## Technical Specifications

### Frontend Stack

```typescript
// State Management
interface AppState {
  context: SystemContext;
  isLoading: boolean;
  error: Error | null;
  // ... other state properties
}

// MCP Provider
interface MCPContext {
  isConnected: boolean;
  isInitialized: boolean;
  capabilities: Record<string, boolean>;
  // ... other context properties
}

// Component Architecture
type ComponentProps = {
  data: DataType;
  isLoading?: boolean;
  error?: Error | null;
  onAction: (data: ActionData) => Promise<void>;
};
```

### Backend Stack

```python
# FastAPI Application
app = FastAPI(
    title="System Context Monitor",
    description="Backend API for system monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Service Layer
class MonitoringService:
    async def capture_screenshot(self):
        # Implementation
        pass

    async def monitor_clipboard(self):
        # Implementation
        pass

    async def track_network(self):
        # Implementation
        pass

# Data Layer
class StateManager:
    async def update_context(self, context: SystemContext):
        # Implementation
        pass

    async def get_context(self) -> SystemContext:
        # Implementation
        pass
```

## Security Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant Auth
    participant API
    participant Service
    
    Client->>Auth: Request access
    Auth->>Auth: Validate credentials
    Auth-->>Client: Issue token
    Client->>API: Request with token
    API->>Auth: Validate token
    Auth-->>API: Token valid
    API->>Service: Process request
```

### Security Measures

1. **Data Protection**
   - End-to-end encryption for sensitive data
   - Secure WebSocket connections
   - Rate limiting on API endpoints

2. **Access Control**
   - Role-based access control
   - Token-based authentication
   - Session management

3. **Resource Protection**
   - Request rate limiting
   - Data storage quotas
   - CPU/Memory restrictions

## Performance Optimization

### Frontend Optimization

1. **Component Optimization**
   - React.memo for pure components
   - Lazy loading for routes
   - Virtual scrolling for large lists

2. **State Management**
   - Selective state updates
   - Optimistic updates
   - Proper memoization

3. **Network Optimization**
   - Request batching
   - Data compression
   - Proper caching

### Backend Optimization

1. **API Optimization**
   - Response compression
   - Query optimization
   - Connection pooling

2. **Caching Strategy**
   - Redis for frequent data
   - In-memory caching
   - Cache invalidation

3. **Resource Management**
   - Worker processes
   - Connection pooling
   - Memory management

## Deployment Architecture

```mermaid
graph TD
    subgraph "Production Environment"
        LB[Load Balancer]
        
        subgraph "Application Servers"
            API1[API Server 1]
            API2[API Server 2]
            WS1[WebSocket Server 1]
            WS2[WebSocket Server 2]
        end
        
        subgraph "Data Storage"
            Redis[Redis Cluster]
            DB[Database Cluster]
            MQ[Message Queue]
        end
        
        LB --> API1 & API2
        LB --> WS1 & WS2
        API1 & API2 --> Redis
        API1 & API2 --> DB
        WS1 & WS2 --> MQ
    end
```

## Error Handling

### Error Categories

1. **Frontend Errors**
   - Network errors
   - State management errors
   - Rendering errors

2. **Backend Errors**
   - API errors
   - Service errors
   - Database errors

### Error Recovery

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#e74c3c',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#c0392b',
      'lineColor': '#2c3e50',
      'secondaryColor': '#2ecc71'
    }
  }
}%%
sequenceDiagram
    participant UI as Frontend UI
    participant API as API Gateway
    participant Service as Service Layer
    participant DB as Database
    
    autonumber
    
    Note over UI,DB: Error Detection & Recovery
    UI->>+API: Initial request
    API->>Service: Process request
    Service->>DB: Database operation
    
    alt Database Error
        DB-->>Service: Operation failed
        Service-->>API: Service error
        API-->>UI: Show error UI
        Note over UI: Implement retry logic
        UI->>API: Retry request
        API->>Service: Reprocess
        Service->>DB: Retry operation
        DB-->>UI: Success response
    else Network Error
        API-->>UI: Network failed
        Note over UI: Auto-reconnect
        UI->>API: Reconnect
        API-->>UI: Connection restored
    else Service Error
        Service-->>API: Service failed
        API-->>UI: Service error
        Note over UI: Fallback logic
        UI->>API: Use fallback
        API-->>UI: Fallback response
    end
```

## Monitoring and Logging

### System Monitoring Flow

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#3498db',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#2980b9',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c',
      'tertiaryColor': '#2ecc71'
    }
  }
}%%
sequenceDiagram
    participant UI as Frontend
    participant MS as Monitoring Service
    participant MQ as Message Queue
    participant DB as Database
    participant Log as Logger
    
    autonumber
    
    Note over UI,Log: Real-time Monitoring Workflow
    
    UI->>+MS: Initialize monitoring
    activate MS
    
    par Screenshot Monitoring
        MS->>MS: Capture screenshot
        MS->>MQ: Publish screenshot
        MQ->>DB: Store screenshot
        DB-->>UI: Update UI
    and Clipboard Monitoring
        MS->>MS: Monitor clipboard
        MS->>MQ: Publish changes
        MQ->>DB: Store changes
        DB-->>UI: Update UI
    and Network Monitoring
        MS->>MS: Track network
        MS->>MQ: Publish activity
        MQ->>DB: Store activity
        DB-->>UI: Update UI
    end
    
    alt Error Occurs
        MS->>Log: Log error
        Log-->>UI: Show error
        Note over MS: Implement recovery
    else Resource Limit
        MS->>Log: Log warning
        MS->>MS: Adjust sampling
    end
    
    Note over UI,Log: Continuous Monitoring Loop
    
    deactivate MS
```

### Logging Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#f1c40f',
      'primaryTextColor': '#000',
      'primaryBorderColor': '#f39c12',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c'
    }
  }
}%%
graph TD
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef logger fill:#f1c40f,stroke:#f39c12,color:#000;
    classDef storage fill:#3498db,stroke:#2980b9,color:#fff;
    classDef processor fill:#2ecc71,stroke:#27ae60,color:#fff;
    
    subgraph "Logging System"
        L1[Application Logger]
        L2[Access Logger]
        L3[Error Logger]
        L4[Audit Logger]
        
        P1[Log Processor]
        P2[Log Aggregator]
        P3[Log Analyzer]
        
        S1[Log Storage]
        S2[Metrics DB]
        S3[Archive]
        
        L1 & L2 & L3 & L4 --> P1
        P1 --> P2
        P2 --> P3
        P3 --> S1 & S2
        S1 --> S3
    end
    
    class L1,L2,L3,L4 logger;
    class P1,P2,P3 processor;
    class S1,S2,S3 storage;
    
    linkStyle default stroke-width:2px;
```

## Future Considerations

1. **Scalability**
   - Horizontal scaling
   - Microservices architecture
   - Distributed caching

2. **Features**
   - AI-powered analysis
   - Advanced visualization
   - Mobile applications

3. **Integration**
   - Third-party services
   - API marketplace
   - Plugin system

## Component Architecture

### Frontend Component Structure

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#3498db',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#2980b9',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c'
    }
  }
}%%
classDiagram
    class SystemContextDashboard {
        +render()
        -handleRefreshContext()
        -handleMCPReconnect()
    }
    
    class DashboardContent {
        -isLoading: boolean
        -error: Error
        +initializeApp()
        +clearError()
        -handleDeleteWorkflow()
        -handleRestartWorkflow()
    }
    
    class MonitoringPanel {
        -screenshots: ScreenshotData[]
        -clipboard: ClipboardData[]
        -network: NetworkData[]
        +handleTabChange()
    }
    
    class ContextViewer {
        -context: SystemContext
        +onRefresh()
        -getStatusColor()
        -getStatusIcon()
    }
    
    class WorkflowManager {
        -workflows: WorkflowState[]
        +onDeleteWorkflow()
        +onRestartWorkflow()
        -handleOpenDetails()
    }
    
    class QRDisplay {
        -data: QRDisplayData
        +onRefresh()
        -handleRefresh()
    }
    
    SystemContextDashboard --> DashboardContent
    DashboardContent --> MonitoringPanel
    DashboardContent --> ContextViewer
    DashboardContent --> WorkflowManager
    DashboardContent --> QRDisplay
```

### Service Layer Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#2ecc71',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#27ae60',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c'
    }
  }
}%%
classDiagram
    class BaseService {
        <<abstract>>
        #config: ServiceConfig
        #logger: Logger
        +initialize()*
        +start()*
        +stop()*
        #validate_config()*
    }
    
    class MonitoringService {
        -screenshot_manager: ScreenshotManager
        -clipboard_monitor: ClipboardMonitor
        -network_tracker: NetworkTracker
        +capture_screenshot()
        +monitor_clipboard()
        +track_network()
    }
    
    class ContextService {
        -context_store: ContextStore
        -event_bus: EventBus
        +update_context()
        +get_context()
        -notify_subscribers()
    }
    
    class WorkflowService {
        -workflow_registry: WorkflowRegistry
        -executor: WorkflowExecutor
        +execute_workflow()
        +delete_workflow()
        +restart_workflow()
    }
    
    BaseService <|-- MonitoringService
    BaseService <|-- ContextService
    BaseService <|-- WorkflowService
```

### Data Flow Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#f1c40f',
      'primaryTextColor': '#000',
      'primaryBorderColor': '#f39c12',
      'lineColor': '#2c3e50',
      'secondaryColor': '#3498db'
    }
  }
}%%
graph TB
    classDef input fill:#f1c40f,stroke:#f39c12,color:#000;
    classDef process fill:#3498db,stroke:#2980b9,color:#fff;
    classDef storage fill:#e74c3c,stroke:#c0392b,color:#fff;
    classDef output fill:#2ecc71,stroke:#27ae60,color:#fff;

    subgraph "Data Sources"
        SS[Screenshot Capture]
        CB[Clipboard Events]
        NW[Network Activity]
    end

    subgraph "Processing Layer"
        DP[Data Processor]
        TF[Transform]
        VL[Validate]
        AG[Aggregate]
    end

    subgraph "Storage Layer"
        RC[Redis Cache]
        DB[Database]
        MQ[Message Queue]
    end

    subgraph "Output Layer"
        RT[Real-time Updates]
        AN[Analytics]
        NT[Notifications]
    end

    SS & CB & NW --> DP
    DP --> TF --> VL --> AG
    AG --> RC & DB & MQ
    RC & DB & MQ --> RT & AN & NT

    class SS,CB,NW input;
    class DP,TF,VL,AG process;
    class RC,DB,MQ storage;
    class RT,AN,NT output;
```

### State Management Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#9b59b6',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#8e44ad',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c'
    }
  }
}%%
graph LR
    classDef store fill:#9b59b6,stroke:#8e44ad,color:#fff;
    classDef action fill:#e74c3c,stroke:#c0392b,color:#fff;
    classDef effect fill:#2ecc71,stroke:#27ae60,color:#fff;
    classDef component fill:#3498db,stroke:#2980b9,color:#fff;

    subgraph "Store Layer"
        ZS[Zustand Store]
        MC[MCP Context]
        PS[Persistent Storage]
    end

    subgraph "Action Layer"
        AC[Action Creators]
        TH[Thunks]
        MD[Middleware]
    end

    subgraph "Effect Layer"
        SE[Side Effects]
        WS[WebSocket]
        API[API Calls]
    end

    subgraph "Component Layer"
        UI[UI Components]
        HK[Hooks]
        SL[Selectors]
    end

    UI --> HK --> SL
    SL --> ZS
    ZS --> AC --> TH
    TH --> MD --> SE
    SE --> WS & API
    WS & API --> MC
    MC --> PS

    class ZS,MC,PS store;
    class AC,TH,MD action;
    class SE,WS,API effect;
    class UI,HK,SL component;
```

### Error Handling Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#e74c3c',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#c0392b',
      'lineColor': '#2c3e50',
      'secondaryColor': '#3498db'
    }
  }
}%%
graph TB
    classDef error fill:#e74c3c,stroke:#c0392b,color:#fff;
    classDef handler fill:#3498db,stroke:#2980b9,color:#fff;
    classDef recovery fill:#2ecc71,stroke:#27ae60,color:#fff;
    classDef boundary fill:#f1c40f,stroke:#f39c12,color:#000;

    subgraph "Error Types"
        NE[Network Errors]
        SE[Service Errors]
        DE[Data Errors]
        VE[Validation Errors]
    end

    subgraph "Error Handlers"
        GH[Global Handler]
        BH[Boundary Handler]
        CH[Component Handler]
        SH[Service Handler]
    end

    subgraph "Recovery Strategies"
        RT[Retry Logic]
        FL[Fallback Logic]
        CR[Circuit Breaker]
        CP[Checkpoint]
    end

    subgraph "Error Boundaries"
        EB[Error Boundary]
        EL[Error Logger]
        EM[Error Metrics]
    end

    NE & SE & DE & VE --> GH
    GH --> BH & CH & SH
    BH & CH & SH --> RT & FL & CR & CP
    RT & FL & CR & CP --> EB
    EB --> EL --> EM

    class NE,SE,DE,VE error;
    class GH,BH,CH,SH handler;
    class RT,FL,CR,CP recovery;
    class EB,EL,EM boundary;
```

These diagrams provide a comprehensive view of:
1. Frontend component relationships and hierarchy
2. Service layer abstraction and implementation
3. Data flow through the system
4. State management architecture
5. Error handling patterns and recovery strategies

Would you like me to:
1. Add more detailed class diagrams for specific components?
2. Create diagrams for other architectural aspects?
3. Add more detailed relationships between components?
4. Include implementation details in the diagrams?

### Monitoring Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#2ecc71',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#27ae60',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c'
    }
  }
}%%
classDiagram
    class MonitoringAgent {
        -collectors: Map<string, DataCollector>
        -processors: Map<string, DataProcessor>
        -alertManager: AlertManager
        +monitor()
        -collectData()
        -processMetrics()
        #handleMonitoringError()
    }

    class DataCollector {
        <<interface>>
        +collect()
        +validate()
        +transform()
    }

    class DataProcessor {
        -validator: Validator
        -transformer: Transformer
        +process()
        -validateData()
        -normalizeData()
        -aggregateData()
    }

    class AlertManager {
        -rules: Map<string, AlertRule>
        -notifiers: Map<string, Notifier>
        +evaluateAlerts()
        -correlateAlerts()
        -sendNotifications()
    }

    class MetricsManager {
        -store: MetricsStore
        -aggregator: MetricsAggregator
        +recordMetric()
        +queryMetrics()
        -aggregateMetrics()
    }

    MonitoringAgent --> DataCollector
    MonitoringAgent --> DataProcessor
    MonitoringAgent --> AlertManager
    MonitoringAgent --> MetricsManager
    DataCollector --> DataProcessor
    DataProcessor --> AlertManager
    AlertManager --> MetricsManager
```

### Testing Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#3498db',
      'primaryTextColor': '#fff',
      'primaryBorderColor': '#2980b9',
      'lineColor': '#2c3e50',
      'secondaryColor': '#e74c3c'
    }
  }
}%%
graph TB
    classDef test fill:#3498db,stroke:#2980b9,color:#fff;
    classDef mock fill:#e74c3c,stroke:#c0392b,color:#fff;
    classDef fixture fill:#2ecc71,stroke:#27ae60,color:#fff;
    classDef runner fill:#9b59b6,stroke:#8e44ad,color:#fff;

    subgraph "Test Suites"
        UT[Unit Tests]
        IT[Integration Tests]
        E2E[E2E Tests]
        PT[Performance Tests]
    end

    subgraph "Test Fixtures"
        TF[Test Factory]
        TD[Test Data]
        TS[Test State]
    end

    subgraph "Mock System"
        MS[Mock Server]
        MC[Mock Client]
        MD[Mock Database]
    end

    subgraph "Test Runner"
        TR[Test Runner]
        RP[Result Processor]
        RG[Report Generator]
    end

    UT & IT & E2E & PT --> TR
    TR --> RP --> RG
    TF --> UT & IT & E2E
    TD --> TF
    TS --> TF
    MS & MC & MD --> IT & E2E

    class UT,IT,E2E,PT test;
    class MS,MC,MD mock;
    class TF,TD,TS fixture;
    class TR,RP,RG runner;
```

### Container Architecture

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#f1c40f',
      'primaryTextColor': '#000',
      'primaryBorderColor': '#f39c12',
      'lineColor': '#2c3e50',
      'secondaryColor': '#3498db'
    }
  }
}%%
graph TB
    classDef container fill:#f1c40f,stroke:#f39c12,color:#000;
    classDef volume fill:#3498db,stroke:#2980b9,color:#fff;
    classDef network fill:#2ecc71,stroke:#27ae60,color:#fff;

    subgraph "Container Stack"
        FE[Frontend Container]
        BE[Backend Container]
        DB[Database Container]
        MQ[Message Queue Container]
    end

    subgraph "Volumes"
        DV[Data Volume]
        LV[Log Volume]
        CV[Config Volume]
    end

    subgraph "Networks"
        FN[Frontend Network]
        BN[Backend Network]
        DN[Database Network]
    end

    FE --> FN
    BE --> FN & BN
    DB --> BN & DN
    MQ --> BN
    BE --> DV & LV & CV
    DB --> DV

    class FE,BE,DB,MQ container;
    class DV,LV,CV volume;
    class FN,BN,DN network;
```

Now, let me create a Podman/Docker compose file to orchestrate these containers. 