from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import ast

class SolidPrinciple(str, Enum):
    SRP = "Single Responsibility Principle"
    OCP = "Open/Closed Principle"
    LSP = "Liskov Substitution Principle"
    ISP = "Interface Segregation Principle"
    DIP = "Dependency Inversion Principle"

@dataclass
class CodeAnalysis:
    """Analysis results for a code segment."""
    principle: SolidPrinciple
    violations: List[str]
    recommendations: List[str]
    code_suggestions: Dict[str, str]

@dataclass
class SolidAnalyzerConfig:
    """Configuration for SOLID analyzer."""
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 8192
    temperature: float = 0
    system_prompt: str = """You are a SOLID principles expert. Analyze code for adherence to SOLID principles 
    and provide specific, actionable recommendations for improvement. Focus on practical solutions that maintain 
    existing functionality while improving code structure."""
    
class SolidAnalyzerAgent:
    """Agent for analyzing and improving code according to SOLID principles."""
    
    def __init__(self, client: AnthropicClient, config: Optional[SolidAnalyzerConfig] = None):
        self.client = client
        self.config = config or SolidAnalyzerConfig()
        
    async def analyze_code(self, code: str, principles: Optional[List[SolidPrinciple]] = None) -> List[CodeAnalysis]:
        """Analyze code for SOLID principles compliance."""
        principles = principles or list(SolidPrinciple)
        analyses = []
        
        for principle in principles:
            analysis = await self._analyze_principle(code, principle)
            analyses.append(analysis)
            
        return analyses
    
    async def _analyze_principle(self, code: str, principle: SolidPrinciple) -> CodeAnalysis:
        """Analyze code for a specific SOLID principle."""
        template_variables = {
            "code": code,
            "principle": principle.value
        }
        
        message = await self.client.create_message(
            template_name="solid_analysis",
            template_variables=template_variables,
            config=MessageConfig(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.config.system_prompt
            )
        )
        
        # Parse analysis from message
        analysis = self._parse_analysis(message.content)
        return analysis
    
    def _parse_analysis(self, content: str) -> CodeAnalysis:
        """Parse analysis from message content."""
        # Implementation would parse structured response from LLM
        # This is a simplified version
        pass
    
    async def suggest_improvements(self, code: str, analyses: List[CodeAnalysis]) -> str:
        """Suggest code improvements based on analyses."""
        template_variables = {
            "code": code,
            "analyses": [
                {
                    "principle": analysis.principle.value,
                    "violations": analysis.violations,
                    "recommendations": analysis.recommendations
                }
                for analysis in analyses
            ]
        }
        
        message = await self.client.create_message(
            template_name="solid_improvements",
            template_variables=template_variables,
            config=MessageConfig(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.config.system_prompt
            )
        )
        
        return message.content

class SolidCodeImprover:
    """Improves code based on SOLID principles."""
    
    def __init__(self, analyzer: SolidAnalyzerAgent):
        self.analyzer = analyzer
    
    async def improve_code(self, code: str) -> str:
        """Analyze and improve code according to SOLID principles."""
        # Analyze code
        analyses = await self.analyzer.analyze_code(code)
        
        # Get improvement suggestions
        improved_code = await self.analyzer.suggest_improvements(code, analyses)
        
        return improved_code

# Add to AnthropicClient's tool configuration
SOLID_ANALYSIS_TOOL = Tool(
    name="solid_analyzer",
    description="Analyzes code for SOLID principles compliance and suggests improvements",
    input_schema={
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Code to analyze"
            },
            "principles": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [p.value for p in SolidPrinciple]
                },
                "description": "SOLID principles to analyze"
            }
        },
        "required": ["code"]
    },
    handler=None  # Will be set during initialization
)

# Example templates

# templates/solid_analysis.j2
"""
Analyze the following code for {{ principle }}:

{{ code }}

Provide analysis in the following format:
<analysis>
  <violations>
    [List violations here]
  </violations>
  <recommendations>
    [List recommendations here]
  </recommendations>
  <code_suggestions>
    [Provide specific code improvements]
  </code_suggestions>
</analysis>
"""

# templates/solid_improvements.j2
"""
Improve the following code based on SOLID principle analyses:

Original Code:
{{ code }}

Analyses:
{% for analysis in analyses %}
{{ analysis.principle }}:
- Violations: {{ analysis.violations | join(', ') }}
- Recommendations: {{ analysis.recommendations | join(', ') }}
{% endfor %}

Provide improved code that addresses these issues while maintaining functionality.
"""

# Example usage
async def main():
    # Initialize client and agent
    client = AnthropicClient(...)
    analyzer = SolidAnalyzerAgent(client)
    improver = SolidCodeImprover(analyzer)
    
    # Example code to analyze
    code = """
    class UserManager:
        def __init__(self):
            self.db = Database()
            self.logger = Logger()
            
        def create_user(self, user_data):
            self.logger.log("Creating user")
            self.db.insert("users", user_data)
            self.send_welcome_email(user_data["email"])
            
        def send_welcome_email(self, email):
            # Email sending logic here
            pass
    """
    
    # Improve code
    improved_code = await improver.improve_code(code)
    print(improved_code)

if __name__ == "__main__":
    asyncio.run(main())