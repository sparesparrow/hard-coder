# implemented by grok
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from utils import append_to_blackboard, safe_json_parse
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BLACKBOARD_PATH = os.getenv('BLACKBOARD_PATH', '../workspace/Blackboard.md')

# Tools
from crewai_tools import FileReadTool, FileWriteTool
from diagram_tools import MermaidDiagramTool  # Assuming this tool exists for diagram generation

# BlackboardWriter Agent
blackboard_writer = Agent(
    verbose=True,
    role='Blackboard Writer',
    goal='Aggregate and write validated content into Blackboard.md.',
    backstory='Responsible for keeping the Blackboard updated with all validated outputs from other crews.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
    tools=[FileReadTool(file_path=BLACKBOARD_PATH), FileWriteTool()]
)

def blackboard_writer_callback(output):
    try:
        append_to_blackboard("1. Unlocked Section", f"Aggregated Content:\n\n{output}")
        logger.info("Blackboard updated.")
    except Exception as e:
        logger.error(f"Failed to update Blackboard: {e}")

# DiagramUpdater Agent
diagram_updater = Agent(
    verbose=True,
    role='Diagram Updater',
    goal='Generate and update Mermaid diagrams based on the Blackboard content.',
    backstory='Ensures that diagrams are always up-to-date with the latest content on the Blackboard.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
    tools=[MermaidDiagramTool(), FileReadTool(file_path=BLACKBOARD_PATH)]
)

def diagram_updater_callback(output):
    try:
        append_to_blackboard("4. Diagrams Section", f"Updated Diagram:\n\n{output}")
        logger.info("Diagrams updated on Blackboard.")
    except Exception as e:
        logger.error(f"Failed to update diagrams: {e}")

# SectionLocking Agent
section_locker = Agent(
    verbose=True,
    role='Section Locker',
    goal='Lock sections of Blackboard.md after human approval.',
    backstory='Ensures that no further changes can be made to approved sections of the Blackboard.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
    tools=[FileReadTool(file_path=BLACKBOARD_PATH), FileWriteTool()]
)

def section_locking_callback(output):
    try:
        append_to_blackboard("2. Locked Section", f"Locked Content:\n\n{output}")
        logger.info("Section locked in Blackboard.")
    except Exception as e:
        logger.error(f"Failed to lock section: {e}")

# Define the tasks with error handling in callbacks
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

# Agent Manager to coordinate tasks
class AgentManager(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_tasks = []

    def manage_tasks(self):
        for task in self.pending_tasks:
            if task.can_be_executed():
                task.execute()
            else:
                self.resolve_conflict(task)

    def resolve_conflict(self, task):
        # Here you would implement conflict resolution logic
        logger.warning(f"Conflict detected for task: {task.description}. Resolving...")
        # Example: reordering tasks or waiting for dependencies
        pass

agent_manager = AgentManager(
    verbose=True,
    role='Agent Manager',
    goal='Oversee and coordinate the activities of all agents within the Blackboard Crew.',
    backstory='Manages tasks, resolves conflicts, and ensures smooth operation across all crews.',
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
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

def run_blackboard_crew():
    agent_manager.manage_tasks()
    result = blackboard_crew.kickoff()
    logger.info(result)
    logger.info(blackboard_crew.usage_metrics)

# Run the crew
if __name__ == "__main__":
    run_blackboard_crew()

