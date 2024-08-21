import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI
import json
import json
import os
from utils import safe_json_parse, FileTools


print("All files have been created based on the provided tasks.")

# Callback function to create initial empty files



# Combined task: Define problem, select pattern, and create coding tasks
def combined_developer_task_callback(output):
    #print("DEBUG: Received output from agent:", output)
    
    try:
        output_data = safe_json_parse(output)

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
    
    except Exception as e:
        print(f"Error in combined_developer_task_callback: {e}")

