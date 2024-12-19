### Memory Cascade Pattern
**Intent**: Organize different types of LLM memory (working, short-term, long-term) in a way that mirrors human cognitive architecture.

**Problem**: Different types of information require different retention strategies and access patterns.

**Solution**: Implement a cascading memory system where:
- Working memory holds immediate conversation context
- Short-term memory stores recent interactions and temporary goals
- Long-term memory persists important information in vector databases
