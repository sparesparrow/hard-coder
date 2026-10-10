# hard-coder

An early agentic coding workspace: a reasoning-and-planning assistant that turns an idea into
working code, tests and documentation. It was built before LLMs had native reasoning and before
agent frameworks matured, so planning, decomposition and self-review are implemented as explicit
instructions, design-pattern templates and multi-agent roles.

**Evolution:** custom GPT in the OpenAI GPT Store → migrated to the Anthropic API (tool use, MCP)
→ refactored into CrewAI agent crews → distilled into Cursor Composer rules and notepads.
The repository keeps every stage, which is why it reads as a workspace rather than a single package.

**Status:** exploratory and no longer actively developed (last major update February 2025). Its ideas
continue in [mcp-prompts](https://github.com/sparesparrow/mcp-prompts) and
[mcp-project-orchestrator](https://github.com/sparesparrow/mcp-project-orchestrator).

## What's inside

| Path | Contents |
|---|---|
| [`docs/AssistantInstructions.md`](docs/AssistantInstructions.md) | The original system prompt: pick a project template, define the component hierarchy, document, implement, test |
| [`DesignPatterns/`](DesignPatterns) | Pattern write-ups the assistant draws on: agentic (attention router, chain-of-thought orchestrator, context shepherd, anti-patterns), communication, async, structural |
| [`Projects/AnthropicClient/`](Projects/AnthropicClient) | Anthropic API client with tool use, a file annotator, naming and skeleton agents |
| [`Projects/CrewAI-Agency/`](Projects/CrewAI-Agency), [`Projects/BlackBoard/`](Projects/BlackBoard) | CrewAI multi-agent orchestration and a blackboard-architecture experiment |
| [`Projects/MCP/`](Projects/MCP) | Model Context Protocol client and server prototypes in Python, TypeScript and Kotlin |
| [`Projects/MermaidGenerator/`](Projects/MermaidGenerator) | Structured-input → Mermaid diagram generator |
| [`Projects/SystemContextMonitor/`](Projects/SystemContextMonitor), [`services/api/`](services/api) | FastAPI service (routers, repositories, WebSockets) for monitoring agent workflows |
| [`core/tools/`](core/tools) | Tool registry with rate limiting and timeouts |
| [`cursor-rules/`](cursor-rules) | The Cursor rules the project ended up as |
| [`llm-models-evaluation.md`](llm-models-evaluation.md) | Notes comparing LLMs for coding tasks |

## Working in this repository

### Suggested development workflow
- clone this repo
- `cd workspace`
- `git clone` your existing project
- install dependencies
- `python3 -m venv .venv` && `source .venv/bin/activate`
- Integrate [Projects](Projects/Projects.md)

### File/Folder Structure

- Important folders include a markdown file named as `FOLDER_NAME.md` containing information about the files and folders located in that folder. Alternatively, like in case of many Projects, this file could be named `README.md`
- There might be a `TODO.txt` file in any folder, containing TODOs for the files/folders within this folder. The file should be removed once issues are solved.

### Documents

- Basically every markdown file is supposed to be readable by both humans and machines.
- [AssistantInstructions](docs/AssistantInstructions.md) contains original instructions formerly used for an aggregated Assistant. This project aims to modularize and decentralize the instructions with a more agentic approach
- [Applicable Tools for Agents and Tasks](docs/tools.md) 

