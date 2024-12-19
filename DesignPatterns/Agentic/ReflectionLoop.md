### Reflection Loop Pattern
**Intent**: Enable LLMs to improve their responses through self-reflection and iteration.

**Problem**: Initial LLM responses may be suboptimal or contain errors.

**Solution**: Implement a feedback loop where the LLM:
1. Generates an initial response 
2. Evaluates its own response against quality criteria
3. Identifies potential improvements
4. Generates an improved version

Example implementation:
```python 
class ReflectionLoop:
    def __init__(self, llm_client, max_iterations=3):
        self.llm = llm_client
        self.max_iterations = max_iterations

    def generate_with_reflection(self, prompt):
        response = self.llm.generate(prompt)
        
        for i in range(self.max_iterations):
            evaluation = self.llm.evaluate_response(response)
            if evaluation.quality_score > 0.9:
                break
                
            improvements = self.llm.suggest_improvements(response)
            response = self.llm.generate(prompt, improvements)

        return response  
```
