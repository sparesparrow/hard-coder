from crewai import Agent, Task, Crew, Process

from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    JSONSearchTool,
    SerperDevTool,
    WebsiteSearchTool
)
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
import os
from pathlib import Path
import yaml
import json

import inspect
from typing import List, Dict, Optional, Any
import re

class SkeletonArchitect:
    """A lightweight agent that creates code structure without implementations."""
    
    def create_skeleton(self, requirements: Dict[str, Any]) -> str:
        """
        Creates a code skeleton based on requirements.
        
        Args:
            requirements: Dict containing:
                - class_names: List of class names to create
                - methods: Dict mapping class names to lists of method names
                - imports: List of required imports
                - file_structure: Optional dict of file paths and their contents
        """
        code = []
        
        # Add imports
        if 'imports' in requirements:
            for imp in requirements['imports']:
                code.append(f"import {imp}")
            code.append("\n")
            
        # Create classes
        for class_name in requirements.get('class_names', []):
            code.append(f"class {class_name}:")
            methods = requirements.get('methods', {}).get(class_name, [])
            
            if not methods:
                code.append("    pass")
            
            for method in methods:
                code.append(f"""    def {method}(self):
        # TODO: Implement {method}
        pass\n""")
            
            code.append("\n")
            
        return "\n".join(code)

class ImplementationEngineer:
    """A comprehensive agent that implements code skeletons."""
    
    def implement_skeleton(self, skeleton: str, requirements: Dict[str, Any]) -> str:
        """
        Takes a skeleton and adds implementations based on requirements.
        
        Args:
            skeleton: String containing the code skeleton
            requirements: Dict containing:
                - implementations: Dict mapping method names to their implementations
                - docstrings: Optional dict of docstrings for classes/methods
                - type_hints: Optional dict of type hints for methods
        """
        # Parse the skeleton to get structure
        code_lines = skeleton.split('\n')
        implemented_code = []
        current_class = None
        current_method = None
        
        for line in code_lines:
            # Detect class definitions
            if line.startswith('class '):
                current_class = line[6:line.find(':')]
                implemented_code.append(line)
                
                # Add class docstring if available
                if requirements.get('docstrings', {}).get(current_class):
                    implemented_code.append(f'    """{requirements["docstrings"][current_class]}"""')
                    
            # Detect method definitions
            elif line.strip().startswith('def '):
                current_method = line[line.find('def ') + 4:line.find('(')]
                
                # Add type hints if available
                if requirements.get('type_hints', {}).get(current_method):
                    type_hint = requirements['type_hints'][current_method]
                    line = line.replace('(self):', f'(self) -> {type_hint}:')
                
                implemented_code.append(line)
                
                # Add implementation if available
                if requirements.get('implementations', {}).get(current_method):
                    impl = requirements['implementations'][current_method]
                    # Remove TODO comment and pass statement
                    implemented_code.append(f"        {impl}")
                else:
                    implemented_code.append("        pass")
                    
            # Keep other lines as is
            elif line.strip():
                implemented_code.append(line)
                
        return "\n".join(implemented_code)
    

@dataclass
class ProjectComponent:
    """Represents a component of the project."""
    name: str
    path: str
    type: str  # 'component', 'service', 'module', 'class', 'interface'
    dependencies: List[str]
    methods: List[str]
    description: str

class ProjectStructurePlanner:
    """Plans the high-level project structure."""
    
    def __init__(self, project_name: str, design_pattern: str):
        self.project_name = project_name
        self.design_pattern = design_pattern
        
    def plan_structure(self, requirements: Dict) -> Dict:
        """Creates high-level project structure based on requirements."""
        structure = {
            'components': requirements.get('components', []),
            'services': requirements.get('services', []),
            'modules': requirements.get('modules', []),
            'file_structure': {},
            'relationships': [],
            'tests': []
        }
        return structure

class NamingConventionEnforcer:
    """Enforces consistent naming conventions."""
    
    @staticmethod
    def to_snake_case(name: str) -> str:
        """Converts a string to snake_case."""
        return name.lower().replace(' ', '_')
        
    @staticmethod
    def to_camel_case(name: str) -> str:
        """Converts a string to camelCase."""
        components = name.split('_')
        return ''.join(x.title() for x in components)
        
    def enforce_conventions(self, structure: Dict) -> Dict:
        """Applies naming conventions to all project elements."""
        standardized = {
            'components': [self._standardize_component_name(comp) for comp in structure.get('components', [])],
            'services': [self._standardize_component_name(serv) for serv in structure.get('services', [])],
            'modules': [self._standardize_component_name(mod) for mod in structure.get('modules', [])],
            'file_structure': structure.get('file_structure', {}),
            'relationships': structure.get('relationships', []),
            'tests': structure.get('tests', [])
        }
        return standardized
    
    def _standardize_component_name(self, component: Dict) -> Dict:
        """Standardizes the name of a component."""
        if 'name' in component:
            component['name'] = self.to_snake_case(component['name'])
        return component

class ReadmeGenerator:
    """Generates comprehensive README.md for the project."""
    
    def generate_readme(self, project_info: Dict) -> str:
        """Generates the README.md content."""
        template = f"""
# {project_info['name']}

## Project Structure
{self._generate_structure_section(project_info['structure'])}

## Components
{self._generate_components_section(project_info['components'])}

## Services
{self._generate_services_section(project_info['services'])}

## Development Setup
{self._generate_setup_section(project_info)}

## Testing Strategy
{self._generate_testing_section(project_info['tests'])}
"""
        return template
    
    def _generate_structure_section(self, structure: Dict) -> str:
        """Generates the structure documentation."""
        # Implementation will create structure documentation
        return "Structure documentation will be here"

    def _generate_components_section(self, components: List[Dict]) -> str:
        """Generates the components documentation."""
        if not components:
            return "No components defined."
        
        component_docs = "\n".join([f"- {comp['name']}" for comp in components])
        return f"### Components:\n{component_docs}"

    def _generate_services_section(self, services: List[Dict]) -> str:
        """Generates the services documentation."""
        if not services:
            return "No services defined."
        
        service_docs = "\n".join([f"- {serv['name']}" for serv in services])
        return f"### Services:\n{service_docs}"

    def _generate_setup_section(self, project_info: Dict) -> str:
        """Generates the development setup documentation."""
        return "Development setup instructions will be here"

    def _generate_testing_section(self, tests: Dict) -> str:
        """Generates the testing strategy documentation."""
        return "Testing strategy documentation will be here"


class TestPlanGenerator:
    """Generates test skeletons and descriptions."""
    
    def generate_test_plan(self, components: List[ProjectComponent]) -> Dict:
        """Generates a test plan."""
        test_plan = {
            'unit_tests': [],
            'integration_tests': [],
            'e2e_tests': [],
            'test_file_structure': {}
        }
        return test_plan

class ProjectSkeletonGenerator:
    """Main orchestrator for project skeleton generation."""
    
    def __init__(self, project_name: str, design_pattern: str):
        """Initializes the generator with project details."""
        self.project_name = project_name
        self.design_pattern = design_pattern
        self.planner = ProjectStructurePlanner(project_name, design_pattern)
        self.naming = NamingConventionEnforcer()
        self.readme_gen = ReadmeGenerator()
        self.test_gen = TestPlanGenerator()
        
    def generate_skeleton(self, requirements: Dict) -> Dict:
        """Generates complete project skeleton."""
        # 1. Plan basic structure
        structure = self.planner.plan_structure(requirements)
        
        # 2. Apply naming conventions
        standardized = self.naming.enforce_conventions(structure)
        
        # 3. Generate test plan
        test_plan = self.test_gen.generate_test_plan(standardized['components'])
        
        # 4. Generate README
        readme = self.readme_gen.generate_readme({
            'name': self.project_name,
            'structure': standardized,
            'components': standardized['components'],
            'services': standardized['services'],
            'tests': test_plan
        })
        
        return {
            'structure': standardized,
            'readme': readme,
            'test_plan': test_plan,
            'relationships': structure['relationships']
        }
    
    def export_skeleton(self, skeleton: Dict, output_format: str = 'json') -> str:
        """Exports the skeleton in specified format."""
        if output_format == 'json':
            return json.dumps(skeleton, indent=2)
        elif output_format == 'yaml':
            return yaml.dump(skeleton, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")


class SharedContext:
    """A shared context for inter-agent communication."""
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.subscribers: Dict[str, List[Callable]] = {}

    def get_context(self, key: str) -> Any:
        """Retrieve a value from the context."""
        return self.context.get(key)

    def update_context(self, key: str, value: Any) -> None:
        """Update the context and notify subscribers."""
        self.context[key] = value
        self._notify_subscribers(key, value)

    def subscribe_to_event(self, key: str, callback: Callable) -> None:
        """Subscribe to updates for a specific context key."""
        if key not in self.subscribers:
            self.subscribers[key] = []
        self.subscribers[key].append(callback)

    def _notify_subscribers(self, key: str, value: Any) -> None:
        """Notify subscribers of a context update."""
        if key in self.subscribers:
            for callback in self.subscribers[key]:
                callback(value)


ReadmeAgent = Agent(
	role = 'Documenter',
	goal = 'Create a comprehensive README file for the project.',
	backstory = 'This agent focuses on documenting the project, including its overview, setup instructions, and directory structure. It ensures that the README file is informative and easy to follow.',
	tools = [] #'MDXSearchTool, TXTSearchTool, JSONSearchTool'
)

TestAgent = Agent(
	role = 'Tester',
	goal = 'Develop tests for the project components.',
	backstory = 'This agent is responsible for writing tests to ensure the components function as expected. It covers unit tests, integration tests, and other necessary tests to guarantee the project\'s stability and reliability.',
	tools = [] #'CodeDocsSearchTool, CodeInterpreterTool, DirectorySearchTool, FileReadTool'
)

PatternSelectorAgent = Agent(
    role = "Software Architect",
    goal = "Find the best design pattern for a given problem and refine the problem details by breaking down the problem to many tasks based on known architectonical patterns.",
    backstory = "This agent is responsible for browsing the Refactoring Guru website to find the best design pattern for a given problem.",
    tools = [ WebsiteSearchTool(website='https://refactoring.guru/design-patterns'), JSONSearchTool(json_path='project_templates.json') ]
)

ComponentAgent = Agent(
    role = 'Code Writer',
    goal = 'Implement coding task from designed components according to the pattern implementation instructions.',
    backstory = 'This agent is responsible for creating the components of the project, ensuring they align with the selected design pattern. It works closely with other agents to ensure a cohesive and functional project structure.',
    tools = [] #'CodeDocsSearchTool, CodeInterpreterTool, DirectorySearchTool, FileReadTool'
)

ProjectManagerAgent = Agent(
	role = 'Manager',
	goal = 'Oversee the project\'s progress and ensure it adheres to the chosen design pattern.',
	backstory = 'This agent manages the project\'s workflow, ensuring that all components are implemented correctly and tests are conducted thoroughly. It coordinates the efforts of other agents to deliver a successful project.',
	tools = [] #'EXASearchTool, FirecrawlSearchTool, GithubSearchTool, PGSearchTool'
)

design_pattern_agent = Agent(
    role="Software Architect",
    goal="Identify the best design pattern and suggest tasks for implementation.",
    backstory=(
        "An experienced architect who evaluates design patterns to align projects with best practices."
    ),
    tools=[
        WebsiteSearchTool(website="https://refactoring.guru/design-patterns"),
        JSONSearchTool(json_path="project_templates.json"),
    ],
)

component_agent = Agent(
    role="Component Developer",
    goal="Implement the project components based on selected design patterns.",
    backstory="A dedicated developer creating efficient and reusable components.",
    tools=[],  # Add relevant tools here
)

readme_agent = Agent(
    role="Documenter",
    goal="Generate a comprehensive README file for the project.",
    backstory="A meticulous documenter ensuring the project details are well-communicated.",
    tools=[],
)

test_agent = Agent(
    role="Tester",
    goal="Develop comprehensive tests for project components.",
    backstory="An experienced QA engineer focused on ensuring component reliability.",
    tools=[],
)

# Define Tasks
select_pattern_task = Task(
    description="Identify the most suitable design pattern for the project requirements.",
    expected_output="Selected design pattern name with justifications.",
    agent=design_pattern_agent,
)

implement_component_task = Task(
    description="Develop and implement components as per the selected design pattern.",
    expected_output="Source code for project components following best practices.",
    agent=component_agent,
)

create_readme_task = Task(
    description="Create a README file covering project overview, setup, and usage.",
    expected_output="README.md file with project documentation.",
    agent=readme_agent,
)

write_tests_task = Task(
    description="Write unit tests and integration tests for project components.",
    expected_output="Test scripts with adequate coverage.",
    agent=test_agent,
)


selectPattern = Task(
    description='Find the best design pattern for a given problem: write a function that takes a packed string as input and returns an unpacked string as output. The input string is packed with N[PackedString] expressions, which should be unpacked by repeating PackedString N times in the output. Please note that N is an integer greater than 0. Calling the function with fg2[eset]3[hi] returns fgesetesethihihi',
    expected_output='pattern name, covered classes names',
    agent=PatternSelectorAgent
)

implementClasses = Task(
    description='Implements and refactors classes and data structures for the given problem to implement',
    expected_output='class implementations',
    agent=ComponentAgent,
    context=selectPattern
)

# Assemble the Crew
project_crew = Crew(
    agents=[design_pattern_agent, component_agent, readme_agent, test_agent],
    tasks=[select_pattern_task, implement_component_task, create_readme_task, write_tests_task],
    process=Process.sequential,  # Executes tasks sequentially
)

# Kickoff the Crew
project_crew.kickoff(inputs={"project_requirements": {"design_pattern": "Clean Architecture"}})



# Agents
class ComponentAgent(Agent):
    def __init__(self, name, type, description, path, skeleton_architect=None, implementation_engineer=None):
        super().__init__()
        self.name = name
        self.type = type
        self.description = description
        self.path = path
        self.skeleton_architect = skeleton_architect or SkeletonArchitect()
        self.implementation_engineer = implementation_engineer or ImplementationEngineer()

class ReadmeAgent(Agent):
    def __init__(self):
        super().__init__()
        self.name = "ReadmeAgent"
        self.type = "documenter"
        self.description = "Creates a comprehensive README file for the project."
        self.path = "README.md"

class ClassDesigner(Agent):
    def __init__(self):
        super().__init__()
        self.name = "ClassDesigner"
        self.type = "implementer"
        self.description = "Designs and creates classes and data structures for the given problem, acceptance criteria and suggested design pattern to follow."

class TestAgent(Agent):
    def __init__(self):
        super().__init__()
        self.name = "TestAgent"
        self.type = "tester"
        self.description = "Develops tests for the project components."
        self.path = "tests"

class ProjectManagerAgent(Agent):
    def __init__(self):
        super().__init__()
        self.name = "ProjectManagerAgent"
        self.type = "manager"
        self.description = "Oversees the project's progress and ensures it adheres to the chosen design pattern."
        self.path = "project"

class CodingTaskCreator(Agent):
    def __init__(self):
        super().__init__()
        self.name = "CodingTaskCreator"
        self.type = "task_creator"
        self.description = "Creates tasks and describe the desired features to be implemented by other agents. Ensures that the task created has clear and testable acceptance criteria."
        self.path = "tasks"

class VoiceProcessor(Agent):
    def __init__(self, context):
        super().__init__(
            role="Voice Processor",
            goal="Convert voice input into text for further processing.",
            backstory=(
                "A highly efficient processor that transcribes spoken words into structured text."
            ),
        )
        self.context = context

    def process_voice(self, voice_input: str) -> None:
        recognized_text = f"Processed: {voice_input}"  # Simulated output
        print(f"[VoiceProcessor] Recognized text: {recognized_text}")
        self.context.update_context("recognized_text", recognized_text)


class MindmapArchitect(Agent):
    def __init__(self, context):
        super().__init__(
            role="Mindmap Architect",
            goal="Generate a detailed mindmap based on input text.",
            backstory="An experienced mindmap creator specializing in visualizing ideas.",
        )
        self.context = context
        self.context.subscribe_to_event("recognized_text", self.generate_mindmap)

    def generate_mindmap(self, recognized_text: str) -> None:
        mindmap = f"Mindmap based on: {recognized_text}"  # Simulated output
        print(f"[MindmapArchitect] Generated mindmap: {mindmap}")
        self.context.update_context("mindmap", mindmap)


class AnalogyCrafter(Agent):
    def __init__(self, context):
        super().__init__(
            role="Analogy Crafter",
            goal="Create analogies to simplify complex concepts.",
            backstory="A creative thinker adept at connecting ideas through analogies.",
        )
        self.context = context
        self.context.subscribe_to_event("mindmap", self.create_analogies)

    def create_analogies(self, mindmap: str) -> None:
        analogies = f"Analogies for: {mindmap}"  # Simulated output
        print(f"[AnalogyCrafter] Created analogies: {analogies}")
        self.context.update_context("analogies", analogies)


class IllustrationGenerator(Agent):
    def __init__(self, context):
        super().__init__(
            role="Illustration Generator",
            goal="Create illustrations to complement generated ideas.",
            backstory="An artist capable of visualizing abstract concepts into art.",
        )
        self.context = context
        self.context.subscribe_to_event("analogies", self.generate_illustrations)

    def generate_illustrations(self, analogies: str) -> None:
        illustrations = f"Illustrations for: {analogies}"  # Simulated output
        print(f"[IllustrationGenerator] Created illustrations: {illustrations}")
        self.context.update_context("illustrations", illustrations)


class BrainstormFacilitator(Agent):
    def __init__(self, context):
        super().__init__(
            role="Brainstorm Facilitator",
            goal="Facilitate a brainstorming session with the generated outputs.",
            backstory=(
                "A collaborative thinker who uses outputs from all agents to spark ideas."
            ),
        )
        self.context = context
        self.context.subscribe_to_event("illustrations", self.facilitate_brainstorm)

    def facilitate_brainstorm(self, illustrations: str) -> None:
        brainstorm_output = f"Brainstorm session based on: {illustrations}"  # Simulated output
        print(f"[BrainstormFacilitator] Facilitated brainstorm session: {brainstorm_output}")
        self.context.update_context("brainstorm", brainstorm_output)

class VoiceProcessorAgent:
    def __init__(self, context: SharedContext):
        self.context = context

    def process_voice(self, voice_input: str) -> None:
        recognized_text = f"Processed: {voice_input}"  # Simulated output
        print(f"[VoiceProcessor] Recognized text: {recognized_text}")
        self.context.update_context("recognized_text", recognized_text)

class MindmapArchitectAgent:
    def __init__(self, context: SharedContext):
        self.context = context
        self.context.subscribe_to_event("recognized_text", self.generate_mindmap)

    def generate_mindmap(self, recognized_text: str) -> None:
        mindmap = f"Mindmap based on: {recognized_text}"  # Simulated output
        print(f"[MindmapArchitect] Generated mindmap: {mindmap}")
        self.context.update_context("mindmap", mindmap)

# Tasks
class ImplementComponentTask(Task):
    def __init__(self, component):
        super().__init__()
        self.description = f"Implement {component.name} component"
        self.agent = component
        self.expected_output = f"{component.name} component implemented with required functionality"

class CreateReadmeTask(Task):
    def __init__(self):
        super().__init__()
        self.description = "Create a comprehensive README file for the project"
        self.agent = ReadmeAgent()
        self.expected_output = "README file created with project overview, setup instructions, and directory structure"

class WriteTestsTask(Task):
    def __init__(self):
        super().__init__()
        self.description = "Develop tests for the project components"
        self.agent = TestAgent()
        self.expected_output = "Tests written for all project components with adequate coverage"

class DesignPatternSelectionTask(Task):
    def __init__(self):
        super().__init__()
        self.description = "Select a suitable design pattern for the project"
        self.agent = PatternSelectorAgent
        self.expected_output = "Design pattern selected and documented with reasoning"

class CreateCodingTask(Task):
    def __init__(self):
        super().__init__()
        self.description = "Create a new coding task with a draft based on the selected design pattern"
        self.agent = CodingTaskCreator()
        self.expected_output = "Coding task created with draft and assigned to a suitable agent"

class VoiceRecognition(Task):
    def __init__(self, voice_processor):
        super().__init__(
            description="Transcribe voice input into structured text.",
            expected_output="Text transcribed from voice input.",
            agent=voice_processor,
        )


class TextConversion(Task):
    def __init__(self, mindmap_architect):
        super().__init__(
            description="Convert recognized text into a structured format for mindmap generation.",
            expected_output="Structured format for mindmap.",
            agent=mindmap_architect,
        )


class MindMapGeneration(Task):
    def __init__(self, mindmap_architect):
        super().__init__(
            description="Generate a mindmap based on structured text input.",
            expected_output="A detailed mindmap visualization.",
            agent=mindmap_architect,
        )


class AnalogyCreation(Task):
    def __init__(self, analogy_crafter):
        super().__init__(
            description="Craft analogies based on the generated mindmap.",
            expected_output="List of analogies to explain the mindmap concepts.",
            agent=analogy_crafter,
        )


class VisualGeneration(Task):
    def __init__(self, illustration_generator):
        super().__init__(
            description="Generate visual illustrations for the analogies.",
            expected_output="Visual representations of analogies.",
            agent=illustration_generator,
        )


class BrainstormFacilitation(Task):
    def __init__(self, brainstorm_facilitator):
        super().__init__(
            description="Facilitate a brainstorming session using all generated outputs.",
            expected_output="Summary of brainstorming session with generated insights.",
            agent=brainstorm_facilitator,
        )

# Crews

class DocumentationWriters(Crew):
    def __init__(self):
        self.agents = [ReadmeAgent()]

    def run(self):
        for agent in self.agents:
            agent.run()

class CodeWriters(Crew):
    def __init__(self):
        self.agents = [component_agent]

    def run(self):
        for agent in self.agents:
            agent.run()

class TestWriters(Crew):
    def __init__(self):
        self.agents = [TestAgent()]

    def run(self):
        for agent in self.agents:
            agent.run()

class ProjectCrew(Crew):
    def __init__(self):
        super().__init__()
        self.agents = []
        self.tasks = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def add_task(self, task):
        self.tasks.append(task)


# Create agents
component_agent = ComponentAgent("ComponentAgent", "component", "Handles component-related tasks.", "components")
readme_agent = ReadmeAgent()
test_agent = TestAgent()
project_manager_agent = ProjectManagerAgent()
coding_task_creator = CodingTaskCreator()


# Create tasks
implement_component_task = ImplementComponentTask(component_agent)
create_readme_task = CreateReadmeTask()
write_tests_task = WriteTestsTask()
design_pattern_selection_task = DesignPatternSelectionTask()
create_coding_task = CreateCodingTask()


# Assemble a crew with planning enabled
crew = Crew(
    agents=[PatternSelectorAgent, ComponentAgent],
    tasks=[selectPattern, implementClasses],
    verbose=True,
    planning=True,  # Enable planning feature
)

# Execute tasks
crew.kickoff()


# Create crew
project_crew = ProjectCrew()
project_crew.add_agent(component_agent)
project_crew.add_agent(readme_agent)
project_crew.add_agent(test_agent)
project_crew.add_agent(project_manager_agent)
project_crew.add_agent(coding_task_creator)
project_crew.add_task(implement_component_task)
project_crew.add_task(create_readme_task)
project_crew.add_task(write_tests_task)
project_crew.add_task(design_pattern_selection_task)
project_crew.add_task(create_coding_task)


# Initialize shared context
context = SharedContext()

# Initialize agents
voice_processor = VoiceProcessor(context)
mindmap_architect = MindmapArchitect(context)
analogy_crafter = AnalogyCrafter(context)
illustration_generator = IllustrationGenerator(context)
brainstorm_facilitator = BrainstormFacilitator(context)

# Initialize tasks
voice_recognition_task = VoiceRecognition(voice_processor)
text_conversion_task = TextConversion(mindmap_architect)
mindmap_generation_task = MindMapGeneration(mindmap_architect)
analogy_creation_task = AnalogyCreation(analogy_crafter)
visual_generation_task = VisualGeneration(illustration_generator)
brainstorm_facilitation_task = BrainstormFacilitation(brainstorm_facilitator)

# Assemble the crew
crew = Crew(
    agents=[
        voice_processor,
        mindmap_architect,
        analogy_crafter,
        illustration_generator,
        brainstorm_facilitator,
    ],
    tasks=[
        voice_recognition_task,
        text_conversion_task,
        mindmap_generation_task,
        analogy_creation_task,
        visual_generation_task,
        brainstorm_facilitation_task,
    ],
    process=Process.sequential,  # Execute tasks sequentially
)

crew.kickoff(inputs={"voice_input": "Create a mind map of AI concepts."})

# Process
class ProjectProcess(Process):
    def __init__(self):
        super().__init__()
        self.crew = project_crew

    def run(self):
        # Run the tasks
        for task in self.crew.tasks:
            task.run()

# Create process
project_process = ProjectProcess()
project_process.run()


# Example usage
if __name__ == "__main__":
    requirements = {
        'design_pattern': 'clean_architecture',
        'components': [
            {
                'name': 'UserManagement',
                'type': 'module',
                'dependencies': ['AuthService'],
                'methods': ['create_user', 'update_user', 'delete_user']
            }
        ],
        'services': [
            {
                'name': 'AuthService',
                'type': 'service',
                'methods': ['authenticate', 'authorize']
            }
        ]
    }
    
    generator = ProjectSkeletonGenerator("MyProject", "clean_architecture")
    skeleton = generator.generate_skeleton(requirements)
    output = generator.export_skeleton(skeleton, 'json')
    print(output)