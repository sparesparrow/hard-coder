from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from utils import append_to_blackboard

# Combined task: File writing, Compilation, and Initial Execution
def combined_task_callback(output):
    # Implement the combined task logic
    pass

combined_task = Task(
    description='Write source code, compile, and execute binary.',
    expected_output='Source code compiled and executed.',
    agent=Agent(
        verbose=True,
        role='Combined Task Executor',
        goal='Write source code to file, compile it, and execute the binary.',
        backstory='This agent handles the file writing, compilation, and initial execution in one step to minimize serial processing time.',
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
        tools=[],  # Replace with actual tools
    ),
    verbose=True,
    async_execution=False,
    callback=combined_task_callback,
)

# Final test and report generation task
def final_test_callback(output):
    # Implement the final test and report generation logic
    pass

final_test_task = Task(
    description='Check logs, generate test report, and mark result.',
    expected_output='Logs checked, test report generated, and result marked.',
    agent=Agent(
        verbose=True,
        role='Final Test Processor',
        goal='Check logs, generate test report, and mark result as passed or failed.',
        backstory='This agent handles the final steps of checking logs, generating test reports, and marking results to reduce the total number of tasks.',
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
        tools=[],  # Replace with actual tools
    ),
    verbose=True,
    async_execution=False,
    callback=final_test_callback,
)

# Assemble the Testers' Crew
testers_crew = Crew(
    agents=[combined_task.agent, final_test_task.agent],
    tasks=[combined_task, final_test_task],
    verbose=True,
    planning=True,
    full_output=True,
    process=Process.sequential,
    cache=True,
    output_log_file='crew_log_testers.md'
)

result = testers_crew.kickoff()

print(result)
print(testers_crew.usage_metrics)
