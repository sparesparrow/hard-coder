import os
from typing import Optional, Dict, Any, List
import json
from pathlib import Path
import anthropic
from dataclasses import dataclass
from mcp.client import MCPClient
from tools.manager import ToolManager
from typing import Optional, Dict, Any

@dataclass
class ProjectTemplate:
    name: str
    pattern: str
    description: str
    components: List[str]
    example: Optional[str] = None

class TemplateManager:
    def __init__(self, templates_path: str = "project_templates.json"):
        self.templates_path = templates_path
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, ProjectTemplate]:
        with open(self.templates_path, 'r') as f:
            raw_templates = json.load(f)
            return {
                name: ProjectTemplate(**template_data)
                for name, template_data in raw_templates.items()
            }
    
    def find_best_match(self, query: str) -> ProjectTemplate:
        # TODO: Implement pattern matching logic
        # For now, returns first template
        return next(iter(self.templates.values()))
    
    def get_template(self, pattern: str) -> Optional[ProjectTemplate]:
        return self.templates.get(pattern)

class ProjectImplementor:
    
    def __init__(self, mcp_client: MCPClient, tool_manager: ToolManager):
        self.mcp_client = mcp_client
        self.tool_manager = tool_manager
        self.template_manager = TemplateManager()
        
    def _create_prompt(self, 
                      query: str, 
                      template: ProjectTemplate, 
                      tools: str,
                      design_pattern_browser: str) -> str:
        return f"""
        Project Implementation Request
        
        Query: {query}
        Selected Pattern: {template.pattern}
        
        Available Tools:
        {tools}
        
        Design Pattern Browser:
        {design_pattern_browser}
        
        Please implement this project following these steps:
        1. Define all components and their hierarchy
        2. Create project documentation
        3. Implement components
        4. Write tests
        
        Ensure consistent naming conventions and proper documentation.
        """
    
        
    async def implement_project(self, 
                              query: str,
                              pattern: Optional[str] = None) -> Dict[str, Any]:
        # Get available tools
        tools = await self.tool_manager.get_available_tools()
        
        # Create implementation request
        request_params = {
            "query": query,
            "pattern": pattern,
            "tools": tools
        }
        
        response = await self.mcp_client.call_tool(
            "project/implement",
            **request_params
        )
        
        return response.result
    
    def implement_project(self,
                        query: str,
                        pattern: Optional[str] = None,
                        tools_path: str = "tools.md",
                        design_pattern_path: str = "DesignPatternBrowser.py") -> str:
        # Load tools and design pattern browser
        with open(tools_path, 'r') as f:
            tools = f.read()
        with open(design_pattern_path, 'r') as f:
            design_pattern_browser = f.read()
        
        # Get template
        template = (self.template_manager.get_template(pattern) 
                   if pattern 
                   else self.template_manager.find_best_match(query))
        
        # Create prompt
        prompt = self._create_prompt(
            query,
            template,
            tools,
            design_pattern_browser
        )
        
        # Get implementation from Claude
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }]
        )
        
        return message.content

def main():
    implementor = ProjectImplementor()
    
    # Example usage
    result = implementor.implement_project(
        query="Create a web scraper with data storage",
        pattern=None  # Will auto-select best pattern
    )
    print(result)

if __name__ == "__main__":
    main()