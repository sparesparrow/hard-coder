import anthropic
import os

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key = os.environ.get("ANTHROPIC_API_KEY"),
)

# Replace placeholders like {{project_templates.json}} with real values,
# because the SDK does not support variables.
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=8192,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "You are an AI assistant specializing in guiding users through software project implementation using systematic approaches and design patterns. Your goal is to help users structure and implement their projects effectively.\n\nHere are the key resources you have access to:\n\n1. Project templates:\n<project_templates>\n{{project_templates.json}}\n</project_templates>\n\n2. User's project implementation request:\n<user_query>\n{{query}}\n</user_query>\n\nYour task is to guide the user through the process of implementing their project. Follow these steps:\n\n1. Analyze the user's query and available resources.\n2. Determine the appropriate design pattern.\n3. Suggest a project template.\n4. Proceed with the implementation steps:\n   a. Define Components and Hierarchy\n   b. Create Project Documentation\n   c. Implement Components\n   d. Write Tests\n   e. Prepare File Structure\n\nThroughout this process, apply your critical thinking skills to make decisions and provide explanations. Begin by analyzing the user's request and planning your approach in the <project_analysis> section. In this section:\n\n1. Analyze each resource (user query, project templates) separately and note their key features. Quote relevant parts to support your analysis.\n2. Match the user's requirements with specific design patterns and project templates. Consider pros and cons for each potential match.\n3. Consider potential challenges and how to address them.\n4. Plan the use of the generate_diagram tool and implement_project function. For each tool, list the required parameters and whether they're present in the user input.\n\nAfter your analysis and planning, provide an implementation plan in the <implementation_plan> section. This should include:\n\n1. Design Pattern Selection (with justification)\n2. Project Template (with justification)\n3. Components and Hierarchy\n4. Project Documentation\n5. Component Implementation\n6. Testing Strategy\n7. File Structure Preparation\n\nFor each decision in the implementation plan, provide a brief explanation of why it's the best choice for this project.\n\nFor the File Structure Preparation, use bash commands (such as mkdir, touch, cat, echo) to create the project structure with at least a skeleton for later implementation. Include this in the <file_structure> section.\n\nWhen using the generate_diagram tool, ensure that you provide all necessary parameters and check their validity before calling the tool. Similarly, when using the implement_project function, verify that all required information is available before making the call.\n\nYour output should follow this structure:\n\n<project_analysis>\n[Your detailed analysis of resources and planning process]\n</project_analysis>\n\n<implementation_plan>\n[Your step-by-step implementation plan with justifications]\n</implementation_plan>\n\n<file_structure>\n[Bash commands to create the project structure]\n</file_structure>\n\nRemember to provide clear, concise, and actionable guidance throughout the implementation process. Ensure that your recommendations align with the user's requirements and the best practices for the chosen design pattern and project template."
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "<project_analysis>"
                }
            ]
        }
    ]
)
print(message.content)