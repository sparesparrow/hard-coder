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
