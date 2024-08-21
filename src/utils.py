import os

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
