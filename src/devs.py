from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from utils import append_to_blackboard


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

# Combined task: Define problem, select pattern, and create coding tasks
def combined_developer_task_callback(output):
    # create empty files as per output.data[0] and update blackboard with coding tasks as in output.data[1] 
    pass

combined_developer_task = Task(
    description='Define problem, select pattern, and create coding tasks.',
    expected_output='Problem defined, pattern selected, and coding tasks created.',
    agent=Agent(
        verbose=True,
        role='Tech linquist Software architect',
        goal='Read User Request from the Blackboard (accessible with FileReadTool) in order to define the problem, select design pattern and create detailed coding tasks for software developers to implement. Output as json dictionary, each node being a pair of 1. filename (to create dummy files now and the implementation will be placed there later), and 2. Extensive detailed Coding Task for the developer to implement later. The dictionary should contain complete structured information for the developers to implement the whole problem solution with no more data required from the user.',
        backstory='This agent handles the entire process from problem definition to coding task creation to reduce the number of tasks and streamline the workflow.',
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7),
        tools=[FileReadTool(file_path='workspace/Blackboard.md')],
    ),
    verbose=True,
    async_execution=False,
    callback=combined_developer_task_callback,
)

# Combined task: Write source code and generate README
def combined_code_and_readme_callback(output):
    # Implement combined code writing and README generation logic
    pass

combined_code_and_readme_task = Task(
    description='Write source code and generate README.',
    expected_output='Source code written and README generated.',
    agent=Agent(
        verbose=True,
        role='Source Code and Technical Writer',
        goal='Write the source code for given coding tasks to resolve, and generate project documentation & design decisions onto the shared blackboard within the Shared Section.',
        backstory='This agent handles both code writing and documentation generation in a single task to streamline the development process.',
        llm=ChatOpenAI(model_name="gpt-4o", temperature=0.5),
        tools=[FileReadTool(file_path='workspace/Blackboard.md')],
    ),
    verbose=True,
    async_execution=False,
    callback=combined_code_and_readme_callback,
)

# Assemble the Developers' Crew
developers_crew = Crew(
    agents=[combined_developer_task.agent, combined_code_and_readme_task.agent],
    tasks=[combined_developer_task, combined_code_and_readme_task],
    verbose=True,
    planning=True,
    full_output=True,
    parallel=True,
    process=Process.sequential,
    cache=True,
    output_log_file='crew_log_devs.md'
)

result = developers_crew.kickoff()

print(result)
print(developers_crew.usage_metrics)
