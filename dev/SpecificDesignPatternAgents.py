from crewai import Task, Agent, Crew

aClientServerAgent = Agent(
	role = 'Implementer',
	goal = 'Implement the Client-Server pattern in the project.',
	backstory = 'This agent focuses on creating the client and server components, ensuring they interact correctly via API calls. It implements the necessary services and modules for the Client-Server pattern.',
	tools = 'BrowserbaseLoadTool, ComposioTool, LlamaIndexTool, RagTool'
)

aMVCAGENT = Agent(
	role = 'Implementer',
	goal = 'Implement the Model-View-Controller (MVC) pattern in the project.',
	backstory = 'This agent is responsible for separating concerns into three interconnected components: Model, View, and Controller. It ensures that the project follows the MVC pattern for modularity and ease of maintenance.',
	tools = 'CodeDocsSearchTool, CodeInterpreterTool, DirectorySearchTool, FileReadTool'
)

class ImplementClientServerTask(Task):
    def __init__(self):
        super().__init__()
        self.description = "Implement the Client-Server pattern in the project"
        self.agent = aClientServerAgent
        self.expected_output = "Client-Server pattern implemented with client and server components interacting correctly"

class ImplementMVCDataTask(Task):
    def __init__(self):
        super().__init__()
        self.description = "Implement the Model-View-Controller (MVC) pattern in the project"
        self.agent = aMVCAGENT
        self.expected_output = "MVC pattern implemented with model, view, and controller components interacting correctly"

implement_client_server_task = ImplementClientServerTask()
implement_mvc_data_task = ImplementMVCDataTask()


# Define crew
class ProjectCrew(Crew):
    def __init__(self):
        super().__init__()
        self.agents = []
        self.tasks = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def add_task(self, task):
        self.tasks.append(task)

# Create crew
project_crew = ProjectCrew()
project_crew.add_agent(client_server_agent)
project_crew.add_agent(mvc_agent)