import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="my_api_key",
)

# Replace placeholders like {{query}} with real values,
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
                    "text": "<examples>\n<example>\n<query>\nI want to develop an augmented reality (AR) application for educational purposes. It should allow users to scan real-world objects and display interactive 3D models with additional information. How should I structure this project?\n</query>\n<ideal_output>\nI'll help guide you through implementing your AR educational application project. Let me break this down systematically.\n\n<analysis_and_planning>\nFirst, let's analyze the user's query and the available project templates:\n\n1. User Query Analysis:\nThe user wants to develop an augmented reality (AR) application for educational purposes. Key requirements include:\n- Scanning real-world objects\n- Displaying interactive 3D models\n- Providing additional information about scanned objects\nThis suggests a need for computer vision, 3D rendering, and educational content management.\n\n2. Project Template Analysis:\nLooking at the available templates:\na) Mobile Application Architecture:\nPros: \n- Closest match to AR app requirements\n- Includes UI layer and local storage, which will be needed\n- Can be adapted for AR functionality\nCons:\n- Lacks specific AR components\n- May need significant modification\n\nb) Game Engine Architecture:\nPros:\n- Includes rendering engine, which could be adapted for AR\n- Has input handler, useful for user interactions\nCons:\n- Focused on game development, not AR or education\n- Missing components for object recognition and content management\n\nc) IoT System Architecture and Blockchain Architecture:\nThese are not suitable for an AR educational app and can be disregarded.\n\n3. Design Pattern and Template Selection:\nBased on the analysis, the Mobile Application Architecture is the most suitable starting point. We'll need to extend it with AR-specific components.\n\n4. Potential Challenges and Solutions:\n- Challenge: Real-time AR processing\n  Solution: Optimize AR core components and use efficient algorithms\n- Challenge: 3D model management\n  Solution: Implement a robust asset management system\n- Challenge: Educational content integration\n  Solution: Develop a flexible content management system\n\n5. Tool Use Planning:\na) generate_diagram tool:\nRequired parameters:\n- Component hierarchy (available after planning)\n- Interface definitions (to be defined)\n- Data flow patterns (to be defined)\nStatus: Parameters not yet fully available, will use after detailed planning.\n\nb) implement_project function:\nRequired parameters:\n- Modified template structure (to be defined)\n- AR-specific components (to be defined)\n- Educational content framework (to be defined)\nStatus: Parameters not yet available, will use after complete implementation plan.\n\nNow that we have analyzed the requirements and resources, we can proceed with creating a detailed implementation plan.\n</analysis_and_planning>\n\n<implementation_plan>\n1. Design Pattern Selection:\nMobile Application Architecture (modified for AR)\nJustification: Provides foundation for device integration, UI management, and data handling\n\n2. Project Template:\nExtended mobile_app template with AR components\nAdditional components:\n- ar_core (AR engine and processing)\n- object_recognition (scanning and detection)\n- model_renderer (3D visualization)\n- content_management (educational materials)\n\n3. Components and Hierarchy:\n```\nAREducationApp\n├── UI Layer\n│   ├── Camera View\n│   ├── AR Overlay\n│   └── Information Display\n├── AR Core\n│   ├── Object Detection\n│   ├── Pose Estimation\n│   └── Scene Management\n├── Content Management\n│   ├── 3D Models\n│   ├── Educational Content\n│   └── Asset Management\n├── Business Logic\n│   ├── Learning Modules\n│   └── User Progress\n└── Data Layer\n    ├── Local Storage\n    └── Cloud Sync\n```\n\n4. Project Documentation:\n- System Architecture Overview\n- Component Interfaces\n- Data Flow Diagrams\n- User Interaction Flows\n- Content Management Guidelines\n\n5. Component Implementation Priority:\n1. AR Core setup\n2. Camera integration\n3. Object recognition\n4. 3D model rendering\n5. Educational content display\n6. User interface\n\n6. Testing Strategy:\n- Unit tests for each component\n- Integration tests for AR features\n- Performance testing for real-time processing\n- User experience testing\n- Educational effectiveness evaluation\n\n7. File Structure Organization:\nModern modular architecture with clear separation of concerns\n</implementation_plan>\n\n<file_structure>\n```bash\n# Create main project structure\nmkdir -p AREducationApp/{src,tests,docs,assets}\n\n# Create source code directories\nmkdir -p AREducationApp/src/{ui,ar_core,content,business,data}\nmkdir -p AREducationApp/src/ui/{camera,overlay,display}\nmkdir -p AREducationApp/src/ar_core/{detection,pose,scene}\nmkdir -p AREducationApp/src/content/{models,education,management}\nmkdir -p AREducationApp/src/business/{learning,progress}\nmkdir -p AREducationApp/src/data/{local,cloud}\n\n# Create test directories\nmkdir -p AREducationApp/tests/{unit,integration,performance}\n\n# Create asset directories\nmkdir -p AREducationApp/assets/{3d_models,textures,educational_content}\n\n# Create documentation structure\nmkdir -p AREducationApp/docs/{architecture,api,usage}\n\n# Create initial files\ntouch AREducationApp/README.md\ntouch AREducationApp/docs/architecture/system_overview.md\ntouch AREducationApp/docs/architecture/component_interfaces.md\ntouch AREducationApp/src/ar_core/AREngine.swift\ntouch AREducationApp/src/ui/MainViewController.swift\ntouch AREducationApp/src/content/ContentManager.swift\ntouch AREducationApp/tests/unit/AREngineTests.swift\ntouch AREducationApp/tests/integration/ObjectRecognitionTests.swift\n\n# Create configuration files\ntouch AREducationApp/project.config\ntouch AREducationApp/.gitignore\n```\n</file_structure>\n\n<tool_use>\nNow, let's proceed with using the tools to implement the project. Note that the actual tool use may vary depending on the tool_choice parameter and whether parallel tool use is disabled.\n\n1. Implement initial file structure:\nCommand: implement_file_structure(file_structure_output)\n\n2. Generate software architecture design diagram:\nCommand: generate_diagram(component_hierarchy, interface_definitions, data_flow_patterns)\n\n3. Setup, implement, and test the project codebase:\nCommand: implement_project(modified_template_structure, ar_specific_components, educational_content_framework)\n\n4. Take a screenshot of the generated diagram:\nCommand: take_screenshot(generated_diagram)\n\nImportant notes on tool use:\n- If tool_choice is set to \"any\" or \"tool\", there will be no chain-of-thought reasoning before tool use.\n- Parallel tool use can be disabled by setting disable_parallel_tool_use=true in the tool_choice field.\n- When handling tool use and tool result content blocks:\n  1. Extract the name, id, and input from the tool_use block.\n  2. Run the actual tool in your codebase corresponding to that tool name, passing in the tool input.\n  3. Optionally continue the conversation by sending a new message with the role of user, containing a tool_result content block with the tool_use_id, content (result of the tool), and optionally is_error if an error occurred.\n\nThis structure provides a solid foundation for your AR educational application. The implementation follows a modular approach, separating concerns while maintaining clear interfaces between components. The AR-specific features are integrated into the mobile app architecture, with additional consideration for educational content management and real-time processing requirements.\n\nWould you like me to elaborate on any specific aspect of the implementation plan or provide more detailed guidance for a particular component?\n</tool_use>\n</ideal_output>\n</example>\n</examples>\n\n"
                },
                {
                    "type": "text",
                    "text": "You are an AI assistant specializing in guiding users through software project implementation using systematic approaches and design patterns. Your goal is to help users structure and implement their projects effectively.\n\n<user_query>\n{{query}}\n</user_query>\n\nYour task is to guide the user through the process of implementing their project. Follow these steps:\n\n1. Analyze the user's query and available resources.\n2. Determine the appropriate design pattern.\n3. Suggest a project template.\n4. Proceed with the implementation steps:\n   a. Define Components and Hierarchy\n   b. Create Project Documentation\n   c. Implement Components\n   d. Write Tests\n   e. Prepare File Structure\n\nThroughout this process, apply your critical thinking skills to make decisions and provide explanations. Begin by analyzing the user's request and planning your approach in the analysis_and_planning section. In this section:\n\n1. Analyze the user query and project templates separately. Quote relevant parts to support your analysis.\n2. Match the user's requirements with specific design patterns and project templates. For each potential match, list pros and cons.\n3. Identify potential challenges and propose solutions.\n4. Plan the use of the generate_diagram tool and implement_project function. For each tool, list the required parameters and explicitly check whether they're present in the user input.\n\nAfter your analysis and planning, provide an implementation plan in the <implementation_plan> section. This should include:\n\n1. Design Pattern Selection (with justification)\n2. Project Template (with justification)\n3. Components and Hierarchy\n4. Project Documentation\n5. Component Implementation\n6. Testing Strategy\n7. File Structure Preparation\n\nFor each decision in the implementation plan, provide a brief explanation of why it's the best choice for this project.\n\nFor the File Structure Preparation, use bash commands (such as mkdir, touch, cat, echo) to create the project structure with at least a skeleton for later implementation. Include this in the <file_structure> section.\n\nIn the <tool_use> section, describe the process of using tools to implement the project:\n\n1. Implement initial file structure based on file_structure output.\n2. Generate software architecture design diagram.\n3. Setup, implement, and test the project codebase based on analysis_and_planning and implementation_plan output.\n4. After each step, take a screenshot and carefully evaluate if you have achieved the right outcome. Explicitly show your thinking: \"I have evaluated step X...\" If not correct, try again. Only when you confirm a step was executed correctly should you move on to the next one.\n5. Take a screenshot to check that the generated diagram is correct, renders fine in the browser, and accords to intended design planning.\n\nBefore using any tool, ensure that all required parameters are available and valid. If any required information is missing, do not proceed with the tool use and instead explain what information is needed.\n\nYour output should follow this structure:\n\n<analysis_and_planning>\n[Your detailed analysis of resources and planning process]\n</analysis_and_planning>\n\n<implementation_plan>\n[Your step-by-step implementation plan with justifications]\n</implementation_plan>\n\n<file_structure>\n[Bash commands to create the project structure]\n</file_structure>\n\n<tool_use>\n[Detailed description of tool use process, including evaluation after each step]\n</tool_use>\n\nRemember to provide clear, concise, and actionable guidance throughout the implementation process. Ensure that your recommendations align with the user's requirements and the best practices for the chosen design pattern and project template."
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "I'll help guide you through implementing the DictAssist project. Let me analyze and plan the implementation systematically.\n\n<analysis_and_planning>\n1. User Query Analysis:\nThe user wants to create an AI-powered personal thought assistant with these key requirements:\n- Real-time voice interaction and thought capture\n- Thought management and organization\n- Evening review and analysis system\n- Multi-agent architecture (Voice, Thought, Review agents)\n- Privacy and security focused\n- Low latency performance targets\n\n2. Project Template Analysis:\nLooking at the provided code and architecture, this is a complex system requiring:\n- Voice processing capabilities\n- Data storage and management\n- AI/ML integration\n- Real-time processing\n- Multi-threaded operations\n\n3. Design Pattern Analysis:\nThe project follows a multi-agent architecture with clear separation of concerns:\na) Voice Agent:\n- Handles real-time audio processing\n- Uses external services (Whisper, ElevenLabs)\n- Requires continuous listening capability\n\nb) Thought Agent:\n- Manages thought storage and organization\n- Implements vector database and knowledge graph\n- Handles semantic search\n\nc) Review Agent:\n- Performs evening analysis\n- Generates recommendations\n- Manages task scheduling\n\n4. Potential Challenges and Solutions:\n- Challenge: Real-time voice processing latency\n  Solution: Implement efficient audio streaming and processing pipeline\n- Challenge: Data privacy and security\n  Solution: Local processing and encrypted storage\n- Challenge: Complex state management\n  Solution: Implement robust state management system\n\n5. Tool Use Planning:\nLet's check what tools we have available to implement this project:\n\na) text_editor:\n- Can be used to create project files and structure\n- Required parameters: command, path\n- Status: Available and usable\n\nb) bash:\n- Can be used to create directories and install dependencies\n- Required parameters: command\n- Status: Available and usable\n\nc) computer_use:\n- Can be used for testing GUI components if needed\n- Required parameters: action\n- Status: Available but not immediately needed\n\nd) thought_manager:\n- Can be used to test thought storage and retrieval functionality\n- Required parameters: operation\n- Status: Available and useful for testing\n\nLet's proceed with creating a detailed implementation plan.\n</analysis_and_planning>\n\n<implementation_plan>\n1. Project Structure:\n```\nDictAssist/\n├── src/\n│   ├── agents/\n│   │   ├── voice_agent/\n│   │   ├── thought_agent/\n│   │   └── review_agent/\n│   ├── core/\n│   │   ├── assistant.py\n│   │   └── config.py\n│   ├── services/\n│   │   ├── audio/\n│   │   ├── storage/\n│   │   └── nlp/\n│   └── utils/\n├── tests/\n├── docs/\n└── config/\n```\n\n2. Component Implementation Priority:\n1. Core Assistant Framework\n2. Thought Management System\n3. Voice Processing Pipeline\n4. Review System\n5. Integration Layer\n\n3. Testing Strategy:\n- Unit tests for each agent\n- Integration tests for agent communication\n- Performance tests for audio processing\n- Security tests for data handling\n\n4. Documentation Requirements:\n- API Documentation\n- Architecture Overview\n- Security Guidelines\n- User Manual\n</implementation_plan>\n\n<file_structure>\n```bash\n# Create main project structure\nmkdir -p DictAssist/{src,tests,docs,config}\n\n# Create source code structure\nmkdir -p DictAssist/src/{agents,core,services,utils}\nmkdir -p DictAssist/src/agents/{voice_agent,thought_agent,review_agent}\nmkdir -p DictAssist/src/services/{audio,storage,nlp}\n\n# Create test directories\nmkdir -p DictAssist/tests/{unit,integration,performance}\n\n# Create documentation structure\nmkdir -p DictAssist/docs/{api,architecture,security}\n\n# Create initial files\ntouch DictAssist/README.md\ntouch DictAssist/requirements.txt\ntouch DictAssist/setup.py\ntouch DictAssist/src/core/{__init__.py,assistant.py,config.py}\ntouch DictAssist/src/agents/voice_agent/{__init__.py,voice_processor.py}\ntouch DictAssist/src/agents/thought_agent/{__init__.py,thought_manager.py}\ntouch DictAssist/src/agents/review_agent/{__init__.py,analyzer.py}\n```\n</file_structure>\n\n<tool_use>\nLet's implement the project structure and core files:\n\n1. First, let's create the project structure:"
                },
                {
                    "type": "tool_use",
                    "name": "bash",
                    "id": "toolu_01Be41iPzxyeZe43jXgwgyTj",
                    "input": {
                        "command": "mkdir -p DictAssist/{src,tests,docs,config}\nmkdir -p DictAssist/src/{agents,core,services,utils}\nmkdir -p DictAssist/src/agents/{voice_agent,thought_agent,review_agent}\nmkdir -p DictAssist/src/services/{audio,storage,nlp}\nmkdir -p DictAssist/tests/{unit,integration,performance}\nmkdir -p DictAssist/docs/{api,architecture,security}"
                    }
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_01Be41iPzxyeZe43jXgwgyTj",
                    "content": ""
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "2. Let's create the core assistant implementation:"
                },
                {
                    "type": "tool_use",
                    "name": "text_editor",
                    "id": "toolu_0149Ak7oLrDhom4d7b64CHp5",
                    "input": {
                        "path": "/DictAssist/src/core/assistant.py",
                        "command": "create",
                        "file_text": "\"\"\"\nDictAssist Core Assistant Implementation\n\"\"\"\nfrom typing import Dict, List, Optional\nfrom datetime import datetime\n\nclass AssistantCore:\n    def __init__(self):\n        self.thought_collector = None  # Will be initialized with ThoughtAgent\n        self.voice_interface = None    # Will be initialized with VoiceAgent\n        self.evening_reviewer = None   # Will be initialized with ReviewAgent\n        \n    def initialize_agents(self):\n        \"\"\"Initialize all required agents\"\"\"\n        # TODO: Implement agent initialization\n        pass\n        \n    def capture_thought(self, thought: str, context: Optional[Dict] = None) -> bool:\n        \"\"\"Capture a new thought with optional context\"\"\"\n        if not thought:\n            return False\n        return self.thought_collector.add_thought(thought, context)\n        \n    def process_voice_input(self, audio_data: bytes) -> str:\n        \"\"\"Process voice input and return transcribed text\"\"\"\n        return self.voice_interface.process_audio(audio_data)\n        \n    def generate_evening_review(self) -> Dict:\n        \"\"\"Generate evening review summary and recommendations\"\"\"\n        return self.evening_reviewer.generate_review()\n        \n    def handle_command(self, command: str) -> Dict:\n        \"\"\"Process and handle user commands\"\"\"\n        # TODO: Implement command handling\n        pass"
                    }
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_0149Ak7oLrDhom4d7b64CHp5",
                    "content": ""
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "3. Let's create the configuration file:"
                },
                {
                    "type": "tool_use",
                    "name": "text_editor",
                    "id": "toolu_017R8LDjh4tT27ZWd5PyPavs",
                    "input": {
                        "path": "/DictAssist/src/core/config.py",
                        "command": "create",
                        "file_text": "\"\"\"\nDictAssist Configuration Settings\n\"\"\"\nfrom dataclasses import dataclass\nfrom typing import List\n\n@dataclass\nclass VoiceConfig:\n    sample_rate: int = 16000\n    vad_threshold: float = 0.3\n    silence_duration: float = 1.0\n    wake_words: List[str] = (\"hey assistant\", \"start capture\")\n    end_capture_commands: List[str] = (\"end capture\", \"stop capture\")\n\n@dataclass\nclass SecurityConfig:\n    encrypt_storage: bool = True\n    local_processing_only: bool = True\n    data_retention_days: int = 30\n\n@dataclass\nclass PerformanceConfig:\n    max_response_latency_ms: int = 600\n    batch_size: int = 32\n    cache_size_mb: int = 100\n\nclass Config:\n    VOICE = VoiceConfig()\n    SECURITY = SecurityConfig()\n    PERFORMANCE = PerformanceConfig()\n    \n    # API Keys (should be loaded from environment variables)\n    ELEVENLABS_API_KEY: str = \"\"\n    OPENAI_API_KEY: str = \"\""
                    }
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_017R8LDjh4tT27ZWd5PyPavs",
                    "content": ""
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "4. Let's implement the thought management system:"
                },
                {
                    "type": "tool_use",
                    "name": "text_editor",
                    "id": "toolu_01HmWatgV2Sk1BAq9kM6UzQ2",
                    "input": {
                        "path": "/DictAssist/src/agents/thought_agent/thought_manager.py",
                        "command": "create",
                        "file_text": "\"\"\"\nThought Management System Implementation\n\"\"\"\nfrom typing import Dict, List, Optional\nfrom datetime import datetime\nimport json\n\nclass ThoughtManager:\n    def __init__(self):\n        self.thoughts = []\n        self.categories = set()\n        self.tags = set()\n        \n    def add_thought(self, content: str, metadata: Optional[Dict] = None) -> bool:\n        \"\"\"Add a new thought with metadata\"\"\"\n        thought = {\n            'id': len(self.thoughts) + 1,\n            'content': content,\n            'timestamp': datetime.now().isoformat(),\n            'metadata': metadata or {}\n        }\n        self.thoughts.append(thought)\n        return True\n        \n    def get_thoughts(self, \n                    start_date: Optional[datetime] = None,\n                    end_date: Optional[datetime] = None,\n                    category: Optional[str] = None,\n                    tags: Optional[List[str]] = None) -> List[Dict]:\n        \"\"\"Retrieve thoughts based on filters\"\"\"\n        filtered_thoughts = self.thoughts.copy()\n        \n        if start_date:\n            filtered_thoughts = [t for t in filtered_thoughts \n                               if datetime.fromisoformat(t['timestamp']) >= start_date]\n        \n        if end_date:\n            filtered_thoughts = [t for t in filtered_thoughts \n                               if datetime.fromisoformat(t['timestamp']) <= end_date]\n        \n        if category:\n            filtered_thoughts = [t for t in filtered_thoughts \n                               if t['metadata'].get('category') == category]\n        \n        if tags:\n            filtered_thoughts = [t for t in filtered_thoughts \n                               if any(tag in t['metadata'].get('tags', []) \n                                    for tag in tags)]\n        \n        return filtered_thoughts\n        \n    def analyze_patterns(self) -> Dict:\n        \"\"\"Analyze thought patterns and generate insights\"\"\"\n        # TODO: Implement pattern analysis\n        pass"
                    }
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_01HmWatgV2Sk1BAq9kM6UzQ2",
                    "content": ""
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Let's test the thought management system using the thought_manager tool:"
                },
                {
                    "type": "tool_use",
                    "name": "thought_manager",
                    "id": "toolu_01PnRvECPVT7BcgbZwLZcH7t",
                    "input": {
                        "thought": {
                            "tags": [
                                "voice",
                                "error-handling"
                            ],
                            "content": "Need to implement error handling for voice recognition",
                            "category": "development"
                        },
                        "operation": "store"
                    }
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_01PnRvECPVT7BcgbZwLZcH7t",
                    "content": ""
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "name": "thought_manager",
                    "id": "toolu_01KqzPvpsHoVBU97Vt7f51kt",
                    "input": {
                        "query": {
                            "tags": [
                                "voice"
                            ]
                        },
                        "operation": "retrieve"
                    }
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_01KqzPvpsHoVBU97Vt7f51kt",
                    "content": ""
                }
            ]
        }
    ]
)
print(message.content)
