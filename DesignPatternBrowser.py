from crewai import Agent, Task, Crew, Process


from crewai_tools import (
    DirectoryReadTool,
    CSVSearchTool,
    TXTSearchTool,
    FileReadTool,
    JSONSearchTool,
    CodeDocsSearchTool,
    CodeInterpreterTool,
    WebsiteSearchTool
)
import os

from langchain_openai import ChatOpenAI

#os.environ['OPENAI_MODEL_NAME']='gpt-4o'
os.environ['OPENAI_MODEL_NAME']='gpt-4o-mini'


def callback_function(output):
    # Do something after the task is completed
    # Example: Send an email to the manager
    print(f"""
        Task completed!
        Task: {output.description}
        Output: {output.raw_output}
    """)

query = 'write a c++ code with a function that takes a packed string as input and returns an unpacked string as output. The input string is packed with N[PackedString] expressions, which should be unpacked by repeating PackedString N times in the output. Please note that N is an integer greater than 0. Calling the function with fg2[eset]3[hi] returns fgesetesethihihi'

aPatternSelectorAgent = Agent(
    verbose=True,
    role = 'Software Architect',
    goal = 'Find the best design pattern for a given problem and refine the problem details by breaking down the problem to many tasks based on known architectonical patterns.',
    backstory = 'This agent is responsible for browsing the Refactoring Guru website to find the best design pattern for a given problem.',
    tools = [ JSONSearchTool(json_path='project_templates.json'), WebsiteSearchTool(website='https://refactoring.guru/design-patterns') ],
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
)

aTaskCreator = Agent(
    verbose=True,
    role='Technical Writer',
    goal='Identify coding tasks in User input in order to compose Coding Tasks with details: Problem description, assumed Design Pattern to follow, Acceptance Criteria File names & Programming language by extension, Software Components affected. Writing Software Requirements & Design Decisions for the codebase, documenting working features and constraints or TODOs.',
    backstory="Creates tasks and describe the desired features to be implemented by other agents. Ensures that the task created has clear and testable acceptance criteria. Writes documentation.",
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7),
    tools = [ FileReadTool(file_path='template_README.md') ]
)

aComponentAgent = Agent(
    verbose=True,
    role = 'Code Writer',
    goal = 'Implement coding task in C++ from designed components according to the pattern implementation instructions.',
    backstory = 'This agent is responsible for creating the components of the project, ensuring they align with the selected design pattern. It works closely with other agents to ensure a cohesive and functional project structure.',
    llm=ChatOpenAI(model_name="gpt-4o", temperature=0.7),
    tools = [FileReadTool(file_path='gen/README.MD')], #'CodeDocsSearchTool, CodeInterpreterTool, DirectorySearchTool, FileReadTool'
)

aValidatorAgent = Agent(
    verbose=True,
    role = 'Code Tester',
    goal = 'Validates implementation of coding tasks, compiles code and runs tests.',
    backstory = 'This agent is responsible for validating the solution that it meets the requirements',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
    tools = [DirectoryReadTool(directory='gen'), CodeInterpreterTool()], #'CodeDocsSearchTool, CodeInterpreterTool, DirectorySearchTool, FileReadTool'
)

defineProblem = Task(
    description='user request: ' + query,
    expected_output='Complete User request with full definition of the problem.',
    agent=aTaskCreator,
    callback=callback_function
)

selectPattern = Task(
    description='Identify algorithmic challenges and find the best design pattern for a given problem.',
    expected_output='Functionality descripted with suggested design pattern names & files/classes/methods/function names to implement with such pattern',
    agent=aPatternSelectorAgent,
    context=[defineProblem],
    callback=callback_function
)

breakToSubTasks = Task(
    description='Break down the problem into tasks that can be implemented by software developers',
    expected_output='list of task names where task name contains class name that is implemented by task',
    agent=aPatternSelectorAgent,
    context=[defineProblem, selectPattern],
    callback=callback_function
)

createCodingTask = Task(
    description='Create detailed coding tasks and refine incomplete tasks ',
    expected_output='Complete coding task with all necessary details for the developer to implement it.',
    agent=aTaskCreator,
    context=[defineProblem, selectPattern, breakToSubTasks],
    callback=callback_function
)

createReadme = Task(
    description='Determine user request.',
    expected_output='README.md file with full project documentation, including ',
    agent=aTaskCreator,
    context=[defineProblem, selectPattern, breakToSubTasks, createCodingTask],
    output_file='gen/README.md',
    create_directory=True,
    async_execution=True,
    callback=callback_function
)

implementClasses = Task(
    description='Implements and refactors classes and data structures for the given problem to implement',
    expected_output='class, methods and functions implementations',
    agent=aComponentAgent,
    context=[createCodingTask],
    async_execution=True,
    callback=callback_function
)

queryTask = Task(
    description=query,
    expected_output='Review and validate contents of source code files for project in respective files in the project directory structure. Investigate errors and write a TODO list with work needed to be done next.',
    agent=aValidatorAgent,
    context=[implementClasses, createReadme],
    output_file='gen/TODO.md',
    create_directory=True,
    callback=callback_function
)

# Define a feedback mechanism to adjust the plan based on previous task outcomes
def feedback_mechanism(task, outcome):
    if outcome == 'success':
        print(f'Task {task.description} completed successfully.')
    elif outcome == 'failure':
        print(f'Task {task.description} failed. Adjusting plan...')
        # Adjust the plan by re-assigning tasks or modifying task parameters
        task.agent = aPatternSelectorAgent
        task.context = [breakToSubTasks]

# Assemble a crew with planning enabled
crew = Crew(
    agents=[aPatternSelectorAgent, aComponentAgent, aTaskCreator, aValidatorAgent],
    tasks=[defineProblem, selectPattern, breakToSubTasks, createCodingTask, createReadme, implementClasses, queryTask],
    verbose=True,
    planning=True,  # Enable planning feature
    full_output=True,
    feedback_mechanism=feedback_mechanism,
    parallel=True,
    process=Process.sequential,
    cache=True,
    
)

# Execute tasks
result = crew.kickoff()

print(result)
print(crew.usage_metrics)
