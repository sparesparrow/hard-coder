from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from utils import append_to_blackboard
from utils import safe_json_parse, FileTools


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
import json

from langchain.tools import tool
from langchain_openai import ChatOpenAI

manager_llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)  # A more capable model for planning and management

function_calling_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)  # Used for specific function calls

file_tools = FileTools()

manager_agent = Agent(
    verbose=True,
    role='Project Manager',
    goal='Oversee the project, delegate tasks to other agents, and ensure all components work together seamlessly.',
    backstory='This agent manages the overall workflow and delegates specific tasks to specialized agents.',
    llm=manager_llm,
    function_calling_llm=function_calling_llm,
    allow_delegation=True,
)

function_agent = Agent(
    verbose=True,
    role='Function Specialist',
    goal='Execute precise tasks such as generating code, running calculations, or processing data.',
    backstory='This agent is specialized in executing specific functions as directed by the manager agent.',
    llm=function_calling_llm,
    allow_code_execution=True,
    max_iter=5,
)

# Task to manage the overall project
manage_project_task = Task(
    description='Manage the project, delegate tasks to other agents, and ensure everything is running smoothly.',
    expected_output='Project managed successfully, with all tasks completed by the appropriate agents.',
    agent=manager_agent,
    verbose=True,
    async_execution=False,
)

# Task to execute a specific function
execute_function_task = Task(
    description='Generate the required C++ code for the DatabaseHandler class.',
    expected_output='C++ code generated successfully.',
    agent=function_agent,
    verbose=True,
    async_execution=False,
)

prepare_empty_files_with_tasks = Task(
    description='Define problem, select pattern, and create coding tasks.',
    expected_output='Problem defined, pattern selected, and coding tasks created.',
    agent=Agent(
        verbose=True,
        role='Tech Linguist Software Architect',
        goal='Translate user requests into a clear problem statement, select an appropriate design pattern, and generate coding tasks.',
        backstory='Handles the entire process from problem definition to coding task creation.',
        llm=manager_llm,  
        function_calling_llm=function_calling_llm,  
        allow_code_execution=True,
        allow_delegation=True,
        max_iter=10,
        cache=True,
    ),
    verbose=True,
    async_execution=False,
    output_file='../workspace/gen/tasks.json',
    callback=lambda output: file_tools.create_initial_files_callback('../workspace/gen/tasks.json'),
)


write_code_from_task = Task(
    description='Write source code and generate README.',
    expected_output='Source code written and README generated.',
    agent=Agent(
        verbose=True,
        role='Source Code and Technical Writer',
        goal='To generate C++ files with appropriate content based on input data and the information on the shared blackboard in the workspace.',
        backstory='This agent handles code writing. Outputs all C++ code into files where filenames are given from the coding tasks as well. No markdown output formatting, only valid C++ code, writing to .h or .cpp files - with the files can help you colleague prepare_empty_files_with_tasks.',
        llm=manager_llm,
        allow_code_execution=True,
        max_execution_time=300,  # 5 minutes max
        allow_delegation=True,
        max_iter=5,
    ),   
    verbose=True,
    async_execution=False,
    context=[prepare_empty_files_with_tasks],
)

task_read_blackboard = Task(
    description='Read the Blackboard and structure its content.',
    expected_output='Content read and processed from Blackboard.md',
    agent=Agent(
        role='Blackboard Reader',
        goal='Read the content of Blackboard.md.',
        backstory='Reader of ../workspace/Blackboard.md and provider of there stored contents.',
        llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5),
        tools=[FileReadTool(file_path='../workspace/Blackboard.md')],
        allow_code_execution=True,
        cache=True
    ),
    verbose=True,
    async_execution=False,
    #callback=lambda output: append_to_blackboard('Updates', output)
)

developers_crew = Crew(
    agents=[task_read_blackboard.agent, prepare_empty_files_with_tasks.agent, write_code_from_task.agent],
    tasks=[task_read_blackboard, prepare_empty_files_with_tasks, write_code_from_task],
    verbose=True,
    planning=True,
    planning_llm=ChatOpenAI(model="gpt-4o"),
    full_output=True,
    #parallel=True,
    process=Process.sequential,
    cache=True,
    output_log_file='crew_log_devs.md'
)

result = developers_crew.kickoff()

print(result)
print(developers_crew.usage_metrics)


