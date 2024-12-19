### Context Shepherd Pattern
**Intent**: Manage and maintain context across multiple interactions while preventing context collapse.

**Problem**: LLMs need consistent access to relevant context, but pushing too much context leads to degraded performance and token waste.

**Solution**: Create a Context Shepherd that:
- Maintains a hierarchical context structure
- Prunes irrelevant information using importance scoring
- Retrieves and injects context dynamically based on the current conversation flow

Example implementation:
```python
class ContextShepherd:
    def __init__(self, max_context_length=4000):
        self.context_hierarchy = []
        self.max_length = max_context_length

    def add_context(self, context, importance_score):
        while self.get_total_length() + len(context) > self.max_length:
            self.prune_least_important()
        self.context_hierarchy.append({
            'content': context, 
            'importance': importance_score,
            'timestamp': time.time()
        })

    def get_relevant_context(self, query):
        return self.semantic_search(query, self.context_hierarchy)
```
