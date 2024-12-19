# Purpose

This folder should contain generic interfaces for various abstraction layers, providing simple access to lower-layered providers seemlessly.

For example, there are multiple 3rdParty providers with various APIs
We might aggregate generic `Tools` from crewai-tools, anthropic-tools, custom tools etc.

# Brainstorming
define interfaces for abstraction layers, like tools, LLM requests writer & response reader etc.

Structure
Maybe a flatbuffers schema?

## Data processing, formatting

### LLM Provider Interaction

#### Send request
- Query + YAML -> JSON -> Python/JS/bash-curl -> HTTP Request -> Store request ID


#### Get response


#### Get streamed response

