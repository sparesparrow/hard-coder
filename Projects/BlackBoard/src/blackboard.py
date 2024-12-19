from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from utils import append_to_blackboard

# BlackboardWriter Agent
blackboard_writer = Agent(
    verbose=True,
    role='Blackboard Writer',
    goal='Aggregate and write validated content into Blackboard.md.',
    backstory='Responsible for keeping the Blackboard updated with all validated outputs from other crews.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
    tools=[],  # Replace with actual tools
)

def blackboard_writer_callback(output):
    append_to_blackboard("1. Unlocked Section", f"Aggregated Content:\n\n{output}")
    print("Blackboard updated.")

# DiagramUpdater Agent
diagram_updater = Agent(
    verbose=True,
    role='Diagram Updater',
    goal='Generate and update Mermaid diagrams based on the Blackboard content.',
    backstory='Ensures that diagrams are always up-to-date with the latest content on the Blackboard.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
    tools=[],  # Replace with actual tools
)

def diagram_updater_callback(output):
    append_to_blackboard("4. Diagrams Section", f"Updated Diagram:\n\n{output}")
    print("Diagrams updated on Blackboard.")

# SectionLocking Agent
section_locker = Agent(
    verbose=True,
    role='Section Locker',
    goal='Lock sections of Blackboard.md after human approval.',
    backstory='Ensures that no further changes can be made to approved sections of the Blackboard.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
)

def section_locking_callback(output):
    append_to_blackboard("2. Locked Section", f"Locked Content:\n\n{output}")
    print("Section locked in Blackboard.")

# Define the tasks
update_blackboard_task = Task(
    description='Aggregate content and update Blackboard.md.',
    expected_output='Blackboard.md updated with new content.',
    agent=blackboard_writer,
    verbose=True,
    async_execution=True,
    callback=blackboard_writer_callback,
)

update_diagrams_task = Task(
    description='Generate and update Mermaid diagrams.',
    expected_output='Diagrams updated on Blackboard.md.',
    agent=diagram_updater,
    verbose=True,
    async_execution=True,
    callback=diagram_updater_callback,
)

lock_section_task = Task(
    description='Lock sections in Blackboard.md after human approval.',
    expected_output='Sections locked in Blackboard.md.',
    agent=section_locker,
    verbose=True,
    async_execution=True,
    callback=section_locking_callback,
)

# Assemble the Blackboard Crew
blackboard_crew = Crew(
    agents=[blackboard_writer, diagram_updater, section_locker],
    tasks=[update_blackboard_task, update_diagrams_task, lock_section_task],
    verbose=True,
    planning=True,
    full_output=True,
    process=Process.parallel,
    cache=True,
    output_log_file='crew_log_blackboard.md'
)

# Agent Manager to coordinate tasks
class AgentManager(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_tasks = []

    def manage_tasks(self):
        # Logic for prioritizing and managing tasks
        pass

agent_manager = AgentManager(
    verbose=True,
    role='Agent Manager',
    goal='Oversee and coordinate the activities of all agents within the Blackboard Crew.',
    backstory='Manages tasks, resolves conflicts, and ensures smooth operation across all crews.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
)

def run_blackboard_crew():
    agent_manager.managetasks()
    result = blackboard_crew.kickoff()
    print(result)
    print(blackboard_crew.usage_metrics)

