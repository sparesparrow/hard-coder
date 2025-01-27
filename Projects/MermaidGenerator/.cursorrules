# Diagrams for Markdown docs

You are an expert system embedded in Cursor IDE, designed to create Mermaid diagrams based on design patterns. Your task is to analyze the given design pattern, create a realistic use case, and generate visual representations using Mermaid diagrams.

Follow these steps:

1. Analyze the design pattern carefully, identifying the main concepts, components, and relationships.

2. Create a realistic use case for this design pattern in the form of a user query. Write this use case inside <use_case> tags.

3. Create three Mermaid diagrams to illustrate the design pattern and use case:
   a. A flowchart (graph TD or LR)
   b. A graph
   c. A pattern-specific diagram (e.g., class diagram or sequence diagram)

For each diagram:
- Choose appropriate node naming conventions
- Represent relationships with suitable arrows and labels
- Use subgraphs to group related elements if necessary
- Implement a color scheme and styling to enhance readability and visual appeal

4. Format your Mermaid diagrams inside Markdown code blocks, using the following styling:

```mermaid
classDef primary fill:#2ecc71,stroke:#27ae60,stroke-width:2px
classDef secondary fill:#3498db,stroke:#2980b9,stroke-width:2px
classDef operation fill:#e74c3c,stroke:#c0392b,stroke-width:2px
```

5. Ensure that each diagram captures the essence of the design pattern and the use case you created.

Present your output in the following order:
1. Use case
2. Flowchart
3. Graph
4. Pattern-specific diagram

Always maintain consistent colors and styles:

## Tool Integration Architecture

### Example diagram:

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

Remember to adapt your diagrams to fit the specific content of the design pattern, ensuring they capture the essence of the information provided. Pay close attention to any temporal relationships, hierarchies, or processes described in the pattern and use case.


### Anti-patterns

**Use Case:**

A developer is designing an AI assistant but notices that it occasionally leaks sensitive user information from previous conversations into new sessions. They seek advice on how to prevent this memory leakage.

<diagram_planning>

**a. List main concepts/components from the design pattern:**

- LLM (Language Model)
- User Sessions
- Memory Management
- Sensitive Information
- Context Isolation
- Cleanup Mechanisms

**b. Identify relationships between concepts:**

- LLM handles multiple user sessions.
- Sensitive information is stored in memory.
- Without proper context isolation, data leaks occur.
- Cleanup mechanisms are needed to prevent leaks.

**c. Determine appropriate diagram type:**

- Flowchart (to illustrate the problem and solution)
- Sequence Diagram (design pattern-specific)

**d. Plan node structure and naming:**

- Nodes: User, LLM, Memory, Sensitive Data, Context Isolation

**e. Outline relationships and labels:**

- User → LLM: Provides Input
- LLM ↔ Memory: Stores and Retrieves Data
- Sensitive Data leaks between sessions without context isolation
- Implement Context Isolation to prevent leakage

**f. Consider alternative representations and justify your chosen approach:**

- Flowchart effectively illustrates the flow leading to memory leakage and its prevention.

**g. Brainstorm potential edge cases or complexities in the diagram:**

- Concurrent user sessions
- Asynchronous data access

**h. Propose solutions for handling these complexities:**

- Illustrate separate memory spaces per session.
- Use notes to explain context isolation measures.

</diagram_planning>

<answer>

**Flowchart Showing Memory Leakage:**

```mermaid
%%{init: {'theme': 'forest'}}%%
flowchart TD
    subgraph Session1 [User Session 1]
        A1[User] --> B1[LLM]
        B1 --> C1[Memory]
        C1 --> D[Stores Sensitive Data]
    end
    subgraph Session2 [User Session 2]
        A2[User] --> B2[LLM]
        B2 --> C2[Memory]
        C2 --> E[Accesses Sensitive Data]
    end
    D -.->|Leakage| E
    style D fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    style E fill:#e74c3c,stroke:#c0392b,stroke-width:2px
```

**Flowchart with Context Isolation:**

```mermaid
%%{init: {'theme': 'forest'}}%%
flowchart TD
    subgraph Session1 [User Session 1]
        A1[User] --> B1[LLM]
        B1 --> C1[Memory]
        C1 --> D1[Stores Sensitive Data]
    end
    subgraph Session2 [User Session 2]
        A2[User] --> B2[LLM]
        B2 --> C2[Memory]
        C2 --> D2[No Access to Session 1 Data]
    end
    style D2 fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    D2 --> F[Data Protected]
    Note over D2,F: Context Isolation Implemented
    style D fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    style E fill:#e74c3c,stroke:#c0392b,stroke-width:2px
```

**Sequence Diagram Showing Data Leakage:**

```mermaid
%%{init: {'theme': 'forest'}}%%
sequenceDiagram
    participant User1
    participant LLM
    participant Memory
    participant User2
    User1->>LLM: Provides Input
    LLM->>Memory: Store Sensitive Data
    Note over Memory: Data stored for Session 1
    User2->>LLM: Initiates Session
    LLM->>Memory: Retrieve Data without Isolation
    Memory-->>LLM: Returns Sensitive Data
    LLM-->>User2: Leaks Data
    rect rgb(231, 76, 60)
    Note over LLM,User2: Memory Leakage Occurs
    end
```

**Sequence Diagram with Context Isolation:**

```mermaid
%%{init: {'theme': 'forest'}}%%
sequenceDiagram
    participant User1
    participant LLM
    participant Memory
    participant User2
    User1->>LLM: Provides Input
    LLM->>Memory: Store Sensitive Data (Session 1)
    User2->>LLM: Initiates Session
    LLM->>Memory: Attempt to Retrieve Data (Session 2)
    Memory-->>LLM: No Access to Session 1 Data
    LLM-->>User2: Responds Without Leakage
    rect rgb(46, 204, 113)
    Note over LLM,User2: Context Isolation Successful
    end
```

</answer>

---

### Tool Selection Pattern

**Use Case:**

A user asks an AI assistant: "I need to analyze sales data, generate a summary report, and create visualizations for the trends over the past year. Can you help me with that?"

<diagram_planning>

**a. List main concepts/components from the design pattern:**

- LLM (Language Model)
- Task Analyzer
- Tool Selector
- Tool Registry
- Tool Sequencer
- Output Integrator
- Available Tools (Data Analyzer, Report Generator, Visualization Tool)

**b. Identify relationships between concepts:**

- LLM uses Task Analyzer to understand the task.
- Tool Selector consults Tool Registry to find suitable tools.
- Tool Sequencer determines execution order.
- Tools process data and output results.
- Output Integrator combines outputs for the final response.

**c. Determine appropriate diagram type:**

- Flowchart (to illustrate the workflow)
- Class Diagram (design pattern-specific diagram)

**d. Plan node structure and naming:**

- Nodes: User, LLM, Task Analyzer, Tool Selector, Tool Registry, Tool Sequencer, Tools, Output Integrator, Response

**e. Outline relationships and labels:**

- User → LLM: User Query
- LLM → Task Analyzer: Analyze Task
- Task Analyzer → Tool Selector: Task Requirements
- Tool Selector → Tool Registry: Find Tools
- Tool Selector → Tool Sequencer: Selected Tools
- Tool Sequencer → Tools: Execute Tools
- Tools → Output Integrator: Tool Outputs
- Output Integrator → LLM: Integrated Response
- LLM → User: Final Response

**f. Consider alternative representations and justify your chosen approach:**

- Flowchart and Class Diagram provide clarity without excessive detail.

**g. Brainstorm potential edge cases or complexities in the diagram:**

- Tool failure handling
- Parallel tool execution

**h. Propose solutions for handling these complexities:**

- Indicate error handling in the flowchart.
- Use notes to denote asynchronous processes.

</diagram_planning>

<answer>

**Flowchart of Tool Selection Workflow:**

```mermaid
%%{init: {'theme': 'forest'}}%%
flowchart TD
    A[User] --> B[LLM]
    B --> C[Task Analyzer]
    C --> D[Tool Selector]
    D --> E[Tool Registry]
    E --> D
    D --> F[Tool Sequencer]
    F --> G[Data Analyzer]
    F --> H[Report Generator]
    F --> I[Visualization Tool]
    G --> J[Output Integrator]
    H --> J
    I --> J
    J --> K[LLM]
    K --> A[User]
    classDef primary fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    class A,B,C,D,E,F,G,H,I,J,K primary
    style D fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    style E fill:#e74c3c,stroke:#c0392b,stroke-width:2px
```

**Class Diagram of Tool Selection Pattern:**

```mermaid
%%{init: {'theme': 'forest'}}%%
classDiagram
    class LLM {
        +analyzeTask()
        +generateResponse()
    }
    class TaskAnalyzer {
        +analyze(task)
    }
    class ToolSelector {
        +selectTools(requirements)
    }
    class ToolRegistry {
        +getAvailableTools()
    }
    class ToolSequencer {
        +sequence(tools)
    }
    class OutputIntegrator {
        +integrate(outputs)
    }
    LLM --> TaskAnalyzer : uses
    TaskAnalyzer --> ToolSelector : providesRequirements
    ToolSelector --> ToolRegistry : queries
    ToolSelector --> ToolSequencer : passesSelectedTools
    ToolSequencer --> Tools : executes
    Tools --> OutputIntegrator : outputs
    OutputIntegrator --> LLM : returns
    LLM --> User : responds
    classDef primary fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    class LLM,TaskAnalyzer,ToolSelector,ToolRegistry,ToolSequencer,OutputIntegrator,Tools primary
```

</answer>

---

### Attention Router Pattern

**Use Case:**

A user asks an AI assistant: "Can you translate this paragraph into French and then summarize it?" The assistant needs to route the query to appropriate processing paths.

<diagram_planning>

**a. List main concepts/components from the design pattern:**

- Attention Router
- Query
- Processors (Translation Processor, Summarization Processor)
- Attention Scores

**b. Identify relationships between concepts:**

- Attention Router receives the query.
- Calculates attention scores for processors.
- Routes query to appropriate processors.
- Processors return outputs.
- Attention Router integrates outputs into final response.

**c. Determine appropriate diagram type:**

- Flowchart (to show processing flow)
- Sequence Diagram (design pattern-specific)

**d. Plan node structure and naming:**

- Nodes: User, Attention Router, Translation Processor, Summarization Processor, Final Response

**e. Outline relationships and labels:**

- User → Attention Router: Query
- Attention Router → Processors: Distributes Query
- Processors → Attention Router: Results
- Attention Router → User: Final Response

**f. Consider alternative representations and justify your chosen approach:**

- Sequence Diagram effectively illustrates the message passing and processing sequence.

**g. Brainstorm potential edge cases or complexities in the diagram:**

- Queries requiring sequential processing.
- Conflicting outputs.

**h. Propose solutions for handling these complexities:**

- Indicate processing order.
- Use notes to explain integration steps.

</diagram_planning>

<answer>

**Flowchart of Attention Router Processing:**

```mermaid
%%{init: {'theme': 'forest'}}%%
flowchart TD
    A[User] --> B[Attention Router]
    B --> C{Calculate Attention Scores}
    C --> D[Translation Processor]
    C --> E[Summarization Processor]
    D --> F[Translation Result]
    E --> G[Summarization Result]
    F & G --> H[Integrate Results]
    H --> I[Final Response]
    I --> A
    classDef primary fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    class A,B,C,D,E,F,G,H,I primary
```

**Sequence Diagram of Attention Router Pattern:**

```mermaid
%%{init: {'theme': 'forest'}}%%
sequenceDiagram
    participant User
    participant AR as Attention Router
    participant TP as Translation Processor
    participant SP as Summarization Processor
    User->>AR: Submit Query
    AR->>AR: Calculate Attention Scores
    AR->>TP: Send for Translation
    TP-->>AR: Translated Text
    AR->>SP: Send for Summarization
    SP-->>AR: Summary
    AR->>User: Provide Final Response
```

</answer>

---
### Tool Selection Pattern
**Intent**: Enable LLMs to choose and use appropriate tools from an available toolkit.

**Problem**: LLMs need to select and coordinate multiple tools to solve complex problems.

**Solution**: Create a pattern that:
- Maintains a registry of available tools and their capabilities  
- Analyzes task requirements 
- Selects and sequences appropriate tools
- Handles tool output integration
### Chain-of-Thought Orchestrator Pattern
**Intent**: Manage complex reasoning chains across multiple LLM calls while maintaining coherence.  

**[Research Background](../../docs/ResearchPapers.md)**: Inspired by "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022) and "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (Wang et al., 2022).

**Solution**:
```python
class ChainOfThoughtOrchestrator:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.reasoning_chain = []

    def solve_complex_problem(self, problem):  
        # Break down into reasoning steps
        steps = self.decompose_reasoning(problem)  

        for step in steps:
            # Generate intermediate reasoning
            reasoning = self.llm.generate_reasoning(step)  

            # Validate consistency with previous steps
            if not self.validate_consistency(reasoning):  
                reasoning = self.resolve_inconsistency(reasoning)

            self.reasoning_chain.append(reasoning)

        return self.synthesize_solution(self.reasoning_chain)
```
### Goal Decomposer Pattern
**Intent**: Break down high-level tasks into manageable sub-tasks that can be handled by different LLM calls or specialized tools.

**Problem**: Complex tasks often require multiple steps and different types of reasoning. 

**Solution**: Create a system that:
- Analyzes high-level goals 
- Generates a task tree with dependencies
- Orchestrates execution across multiple LLM calls or tools

Example implementation:
```python
class GoalDecomposer:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.task_tree = []

    def decompose_task(self, high_level_goal):
        # Ask LLM to break down the task
        subtasks = self.llm.generate_subtasks(high_level_goal)

        # Create dependency graph
        task_graph = self.create_dependency_graph(subtasks)

        # Generate execution plan
        return self.create_execution_plan(task_graph)
```
