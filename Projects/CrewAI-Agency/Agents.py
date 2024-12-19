from crewai import Agent, Task, Crew, Process

from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    JSONSearchTool,
    SerperDevTool,
    WebsiteSearchTool
)

aPatternSelectorAgent = Agent(
    role = "Software Architect",
    goal = "Find the best design pattern for a given problem and refine the problem details by breaking down the problem to many tasks based on known architectonical patterns.",
    backstory = "This agent is responsible for browsing the Refactoring Guru website to find the best design pattern for a given problem.",
    tools = [ WebsiteSearchTool(website='https://refactoring.guru/design-patterns'), JSONSearchTool(json_path='project_templates.json') ]
)

selectPattern = Task(
    description='Find the best design pattern for a given problem: write a function that takes a packed string as input and returns an unpacked string as output. The input string is packed with N[PackedString] expressions, which should be unpacked by repeating PackedString N times in the output. Please note that N is an integer greater than 0. Calling the function with fg2[eset]3[hi] returns fgesetesethihihi',
    expected_output='pattern name, covered classes names',
    agent=aPatternSelectorAgent
)

aComponentAgent = Agent(
    role = 'Code Writer',
    goal = 'Implement coding task from designed components according to the pattern implementation instructions.',
    backstory = 'This agent is responsible for creating the components of the project, ensuring they align with the selected design pattern. It works closely with other agents to ensure a cohesive and functional project structure.',
    tools = [] #'CodeDocsSearchTool, CodeInterpreterTool, DirectorySearchTool, FileReadTool'
)

implementClasses = Task(
    description='Implements and refactors classes and data structures for the given problem to implement',
    expected_output='class implementations',
    agent=aComponentAgent,
    context=selectPattern
)


# Assemble a crew with planning enabled
crew = Crew(
    agents=[aPatternSelectorAgent, aComponentAgent],
    tasks=[selectPattern, implementClasses],
    verbose=True,
    planning=True,  # Enable planning feature
)

# Execute tasks
crew.kickoff()


aReadmeAgent = Agent(
	role = 'Documenter',
	goal = 'Create a comprehensive README file for the project.',
	backstory = 'This agent focuses on documenting the project, including its overview, setup instructions, and directory structure. It ensures that the README file is informative and easy to follow.',
	tools = [] #'MDXSearchTool, TXTSearchTool, JSONSearchTool'
)

aTestAgent = Agent(
	role = 'Tester',
	goal = 'Develop tests for the project components.',
	backstory = 'This agent is responsible for writing tests to ensure the components function as expected. It covers unit tests, integration tests, and other necessary tests to guarantee the project\'s stability and reliability.',
	tools = [] #'CodeDocsSearchTool, CodeInterpreterTool, DirectorySearchTool, FileReadTool'
)

aProjectManagerAgent = Agent(
	role = 'Manager',
	goal = 'Oversee the project\'s progress and ensure it adheres to the chosen design pattern.',
	backstory = 'This agent manages the project\'s workflow, ensuring that all components are implemented correctly and tests are conducted thoroughly. It coordinates the efforts of other agents to deliver a successful project.',
	tools = [] #'EXASearchTool, FirecrawlSearchTool, GithubSearchTool, PGSearchTool'
)


# Define agents
class ComponentAgent(Agent):
    def __init__(self, name, type, description, path):
        super().__init__()
        self.name = name
        self.type = type
        self.description = description
        self.path = path

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

# Create agents
component_agent = ComponentAgent("ComponentAgent", "component", "Handles component-related tasks.", "components")
readme_agent = ReadmeAgent()
test_agent = TestAgent()
project_manager_agent = ProjectManagerAgent()
coding_task_creator = CodingTaskCreator()

# Define tasks
class ImplementComponentTask(Task):
    def __init__(self, component):
        super().__init__()
        self.description = f"Implement {component.name} component"
        self.agent = ComponentAgent()
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
        self.agent = DesignPatternBrowser()
        self.expected_output = "Design pattern selected and documented with reasoning"

class CreateCodingTask(Task):
    def __init__(self):
        super().__init__()
        self.description = "Create a new coding task with a draft based on the selected design pattern"
        self.agent = CodingTaskCreator()
        self.expected_output = "Coding task created with draft and assigned to a suitable agent"

# Create tasks
implement_component_task = ImplementComponentTask(ComponentAgent())
create_readme_task = CreateReadmeTask()
write_tests_task = WriteTestsTask()
design_pattern_selection_task = DesignPatternSelectionTask()
create_coding_task = CreateCodingTask()


# Create tasks
implement_component_task = ImplementComponentTask(component_agent)
create_readme_task = CreateReadmeTask()
write_tests_task = WriteTestsTask()






class DocumentationWriters(Crew):
    def __init__(self):
        self.agents = [DocumentationAgent()]

    def run(self):
        for agent in self.agents:
            agent.run()

class CodeWriters(Crew):
    def __init__(self):
        self.agents = [ImplementationAgent()]

    def run(self):
        for agent in self.agents:
            agent.run()

class TestWriters(Crew):
    def __init__(self):
        self.agents = [TestingAgent()]

    def run(self):
        for agent in self.agents:
            agent.run()










# Define crew
class ProjectCrew(Crew):
    def __init__(self):
        super().__init__()
        self.agents = []
        self.tasks = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def add_task(self, task):
        self.tasks.append(task)

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

# Define process
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



