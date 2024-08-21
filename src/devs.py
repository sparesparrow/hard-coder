from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from utils import append_to_blackboard
from utils import safe_json_parse


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

def read_blackboard():
    task_read_blackboard = Task(
        description='Read the Blackboard and perform necessary actions.',
        expected_output='Content read and processed from Blackboard.md',
        agent=Agent(
            role='Blackboard Reader',
            goal='Read the content of Blackboard.md.',
            backstory='Reader of ../workspace/Blackboard.md and provider of there stored contents.',
            llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
            tools=[FileReadTool(file_path='../workspace/Blackboard.md')]
        ),
        verbose=True,
        async_execution=False,
        #callback=lambda output: append_to_blackboard('Updates', output)
    )
    crew = Crew(
        agents=[task_read_blackboard.agent],
        tasks=[task_read_blackboard],
        verbose=True
    )
    result = crew.kickoff()
    print(result)
    return task_read_blackboard

task_read_blackboard = read_blackboard()

# Combined task: Define problem, select pattern, and create coding tasks
def combined_developer_task_callback(output):
    print("DEBUG: Received output from agent:", output)
    
    try:
        output_data = safe_json_parse(output)
    
    except Exception as e:
        print(f"Error in combined_developer_task_callback: {e}")

    if output_data and isinstance(output_data, list):
        files_and_tasks = output_data  # Assuming output_data is a list of dictionaries

        for file_task_pair in files_and_tasks:
            filename = file_task_pair.get('filename')
            coding_task = file_task_pair.get('coding_task')

            if filename and coding_task:
                # Create an empty file
                file_path = os.path.join('../workspace/gen/', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write('// TODO: Implement this file \n' + filename)
                    f.write('/*    \n' + coding_task + '    \n*/')
                print(f"Created file: {file_path}")

                # Update the Blackboard with the coding task
                #append_to_blackboard("3. Developer Tasks", f"### {filename}\n\n{coding_task}")
                print(f"Updated Blackboard with coding task for: {filename}")
    else:
        print("Invalid output format received in combined_developer_task_callback.")


combined_developer_task = Task(
    description='Define problem, select pattern, and create coding tasks.',
    expected_output='Problem defined, pattern selected, and coding tasks created.',
    agent=Agent(
        verbose=True,
        role='Tech linquist Software architect',
        goal='Read User Request from the Blackboard (accessible with FileReadTool) in order to define the problem, select design pattern and create detailed coding tasks for software developers to implement. Output as json dictionary, each node being a pair of 1. filename (to create dummy files now and the implementation will be placed there later), and 2. Extensive detailed Coding Task for the developer to implement later. The dictionary should contain complete structured information for the developers to implement the whole problem solution with no more data required from the user.',
        backstory='This agent handles the entire process from problem definition to coding task creation to reduce the number of tasks and streamline the workflow.',
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7),
        #tools=[readBlackBoard],
    ),
    verbose=True,
    async_execution=False,
    context=[task_read_blackboard],
    callback=combined_developer_task_callback,
)

# Combined task: Write source code and generate README
def combined_code_and_readme_callback(output):
    print("DEBUG: Received output from agent:", output)

    try:
        output_data = safe_json_parse(output)
    
        if output_data and isinstance(output_data, dict):
            source_files = output_data.get('source_files', {})
            readme_content = output_data.get('readme_content', '')

            # Write source files
            for filename, file_content in source_files.items():
                file_path = os.path.join('../workspace/gen/', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(file_content)
                print(f"Written source code to file: {file_path}")

            # Generate README.md
            readme_path = os.path.join('../workspace/gen/', 'README.md')
            os.makedirs(os.path.dirname(readme_path), exist_ok=True)
            with open(readme_path, 'w') as readme_file:
                readme_file.write(readme_content)
            print("README.md generated and saved.")

            # Update the Blackboard with the code and README link
            source_code_block = '\n\n'.join([f"```cpp\n{content}\n```" for content in source_files.values()])
            readme_link = f"[README.md](gen/README.md)"

            append_to_blackboard("1. Unlocked Section", f"### Source Code:\n\n{source_code_block}\n\n### Documentation:\n\n{readme_content}\n\n{readme_link}")
            print("Blackboard updated with source code and README link.")
        else:
            print("Invalid output format received in combined_code_and_readme_callback.")

    except Exception as e:
        print(f"Error in combined_code_and_readme_callback: {e}")


combined_code_and_readme_task = Task(
    description='Write source code and generate README.',
    expected_output='Source code written and README generated.',
    agent=Agent(
        verbose=True,
        role='Source Code and Technical Writer',
        goal='Write the source code for given coding tasks to resolve, and generate project documentation & design decisions based on the information on the shared blackboard in the workspace.',
        backstory='This agent handles both code writing and documentation generation in a single task to streamline the development process. Outputs both the code and docs in a single markdown codeblock, updating the shared workspace\'s blackboard with it.',
        llm=ChatOpenAI(model_name="gpt-4o", temperature=0.5),
        #tools=[readBlackBoard],
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
    #planning=True,
    full_output=True,
    #parallel=True,
    process=Process.sequential,
    #cache=True,
    output_log_file='crew_log_devs.md'
)

result = developers_crew.kickoff()

print(result)
print(developers_crew.usage_metrics)


