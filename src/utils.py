import os
from crewai import Agent, Task, Crew, Process
import json
from crewai_tools import (FileReadTool)
#readBlackBoard = FileReadTool(file_path='../workspace/Blackboard.md')

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
    print("DEBUG: Received in safe_json_parse:", json_string)
    try:
        if isinstance(json_string, str) and json_string.strip():  # Check if JSON string is not empty
            return json.loads(json_string)
        else:
            raise ValueError("Empty JSON string")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None
    