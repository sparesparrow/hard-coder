## Anti-patterns

### Context Flooding 
**Problem**: Overwhelming the LLM with unnecessary context, leading to poor performance.
**Solution**: Use the Context Shepherd pattern and implement proper context pruning.

### Prompt Injection Vulnerability
**Problem**: Allowing unvalidated user input to modify system prompts. 
**Solution**: Implement proper prompt sanitization and validation layers.

### Memory Leakage
**Problem**: Sensitive information persisting in LLM context across conversations.
**Solution**: Implement proper context isolation and cleanup mechanisms. 

### Hallucination Propagation
**Problem**: Allowing hallucinated information to propagate through multiple system components.
**Solution**: Implement fact-checking and verification layers between components.

### Context Tunneling  
**Problem**: Over-optimizing for a specific context, leading to brittle behavior in edge cases.
**Solution**: Maintain context diversity and implement robust fallback mechanisms.

