import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
import json

# Callback function to create initial empty files
def create_initial_files_callback(output):
    tasks = json.loads(output)
    
    for task in tasks:
        filename = task['filename']
        guide = task['guide']
        
        file_path = os.path.join('../workspace/gen/', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(f"// {guide}\n")
        print(f"Created file: {file_path} with guide comment.")

# Agent to read tasks.json and create initial files
initial_file_creator_agent = Agent(
    role='File Creator',
    goal='Create initial files with guides based on tasks.json.',
    backstory='This agent creates initial C++ files with a guide comment extracted from tasks.json.',
    llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5),
    tools=[FileReadTool(file_path='../workspace/gen/tasks.json')],
)

# Task to create initial files
create_initial_files_task = Task(
    description='Create initial C++ files with guide comments.',
    expected_output='Files created with guide comments.',
    agent=initial_file_creator_agent,
    verbose=True,
    async_execution=False,
    callback=create_initial_files_callback,
)

