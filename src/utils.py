import os
from crewai import Agent, Task, Crew, Process
import json
from crewai_tools import (FileReadTool)

from langchain.tools import tool
class FileTools:
    
    @tool("WriteFileWithContent")
    def write_file(self, data):
        """
        Writes the provided data to a file.

        Parameters:
        data (dict): A dictionary containing 'filename' and 'content' keys.

        Example of data format:
        {
            "filename": "example.txt",
            "content": "This is the content of the file."
        }
        """
        try:
            filename = data.get('filename')
            content = data.get('content')
            
            if not filename or not content:
                raise ValueError("Both 'filename' and 'content' must be provided in the data dictionary.")
            
            # Write the content to the specified file
            with open(filename, 'w') as file:
                file.write(content)
            
            return f"File '{filename}' has been written successfully."
        
        except Exception as e:
            return f"An error occurred while writing the file: {e}"

    def create_initial_files_callback(self, json_file_path):
        try:
            with open(json_file_path, 'r') as json_file:
                tasks = json.load(json_file)
        except Exception as e:
            print(f"Failed to read JSON file: {e}")
            return

        for task in tasks:
            filename = task.get('filename')
            guide = task.get('guide')

            # Check if filename or guide is missing, None, or empty
            if not filename or not guide or not guide.strip():
                print(f"Skipping task due to invalid format: {task}")
                continue

            # Proceed with writing the file
            try:
                self.write_file.invoke({"filename": filename, "content": guide})
            except Exception as e:
                print(f"Failed to write file {filename}: {e}")

def append_to_blackboard(section_title, content):
    blackboard_path = '../workspace/Blackboard.md'
    new_content = f"### {section_title}\n\n{content}\n\n"

    with open(blackboard_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip() == f"## {section_title}":
            lines.insert(i + 2, new_content)

    with open(blackboard_path, 'w') as file:
        file.writelines(lines)


def safe_json_parse(json_string):
    #print("DEBUG: Received in safe_json_parse:", json_string)
    try:
        if isinstance(json_string, str) and json_string.strip():  # Check if JSON string is not empty
            return json.loads(json_string)
        else:
            raise ValueError("Empty JSON string")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None
    