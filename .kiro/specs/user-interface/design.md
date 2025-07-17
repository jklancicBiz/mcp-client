# Design Document: MCP Agent User Interface

## Overview

This document outlines the design for adding a graphical user interface (GUI) to the MCP Agent. The GUI will provide users with an intuitive way to interact with the agent, configure settings, and visualize tool interactions, while maintaining all the functionality of the existing CLI version.

The design follows a modular architecture that separates the UI layer from the core agent functionality, allowing the existing agent code to be reused without significant modifications. The GUI will be implemented using PyQt6, a modern Python binding for the Qt framework, which provides cross-platform compatibility and a rich set of UI components.

## Architecture

The architecture follows the Model-View-Controller (MVC) pattern to separate concerns and maintain a clean codebase:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  UI Components  │◄────┤  UI Controller  │◄────┤   MCP Agent    │
│    (View)       │     │  (Controller)   │     │    (Model)      │
│                 │─────►                 │─────►                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Components:

1. **UI Layer**:
   - Main Window: The primary container for all UI components
   - Chat Panel: Displays conversation history and input field
   - Settings Panel: Interface for configuring the agent
   - Tools Panel: Displays available tools and resources
   - Status Bar: Shows connection status and other information

2. **Controller Layer**:
   - UI Controller: Manages UI state and coordinates between UI and agent
   - Settings Controller: Handles configuration changes
   - Chat Controller: Manages conversation flow and history

3. **Model Layer**:
   - Reuses existing MCP Agent components (MCPAgent, MCPClient, LLMProvider)
   - Conversation Model: Stores and manages conversation history
   - Configuration Model: Handles loading and saving configuration

## Components and Interfaces

### UI Components

#### Main Window
- Main application window with menu bar, status bar, and central widget
- Implements layout management and window behavior
- Provides access to application-level functionality

```python
class MainWindow(QMainWindow):
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.chat_panel = ChatPanel()
        self.tools_panel = ToolsPanel()
        self.settings_dialog = SettingsDialog()
        # ...
```

#### Chat Panel
- Displays conversation history with different styling for user and assistant messages
- Provides input field for user messages
- Shows loading indicator during processing
- Implements scrolling for long conversations

```python
class ChatPanel(QWidget):
    message_sent = Signal(str)  # Signal emitted when user sends a message
    
    def __init__(self):
        self.chat_display = QTextEdit(readOnly=True)
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        # ...
    
    def add_user_message(self, message):
        # Add user message to display with styling
        
    def add_assistant_message(self, message):
        # Add assistant message to display with styling
        
    def add_tool_call(self, tool_name, arguments, result):
        # Add tool call information to display
```

#### Settings Panel
- Provides interface for configuring LLM providers and MCP servers
- Securely handles API keys
- Validates input before saving

```python
class SettingsDialog(QDialog):
    settings_updated = Signal(dict)  # Signal emitted when settings are saved
    
    def __init__(self):
        self.llm_section = LLMSettingsSection()
        self.server_section = ServerSettingsSection()
        # ...
    
    def load_settings(self, config):
        # Load settings from config
        
    def save_settings(self):
        # Save settings to config
```

#### Tools Panel
- Displays available tools and resources
- Shows details when a tool or resource is selected
- Updates when connection changes

```python
class ToolsPanel(QWidget):
    def __init__(self):
        self.tools_list = QListWidget()
        self.resources_list = QListWidget()
        self.details_view = QTextEdit(readOnly=True)
        # ...
    
    def update_tools(self, tools):
        # Update tools list
        
    def update_resources(self, resources):
        # Update resources list
```

### Controller Components

#### UI Controller
- Coordinates between UI components and agent
- Manages application state
- Handles events and signals

```python
class UIController:
    def __init__(self):
        self.agent_controller = AgentController()
        self.settings_controller = SettingsController()
        self.main_window = MainWindow(self)
        # ...
    
    def initialize(self):
        # Initialize application
        
    def handle_message(self, message):
        # Process user message and update UI
```

#### Agent Controller
- Manages the MCP Agent instance
- Handles agent initialization and cleanup
- Processes messages and tool calls

```python
class AgentController:
    def __init__(self):
        self.agent = None
        self.llm_provider = None
        self.mcp_client = None
        # ...
    
    async def initialize_agent(self, config):
        # Initialize agent with configuration
        
    async def process_message(self, message):
        # Process message with agent and return response
```

#### Settings Controller
- Manages configuration loading and saving
- Validates settings changes
- Applies settings to agent

```python
class SettingsController:
    def __init__(self):
        self.config_manager = ConfigManager()
        # ...
    
    def load_config(self):
        # Load configuration
        
    def save_config(self, config):
        # Save configuration
        
    def apply_settings(self, settings):
        # Apply settings to agent
```

### Model Components

The design will reuse the existing model components from the MCP Agent:

- **MCPAgent**: Main agent that coordinates between LLM and MCP server
- **MCPClient**: Client for communicating with MCP servers
- **LLMProvider**: Abstract base class for LLM providers with concrete implementations
- **ConfigManager**: Manages configuration loading and saving

Additional model components will be added:

#### Conversation Model
- Stores conversation history
- Provides methods for adding messages and tool calls
- Handles exporting and importing conversations

```python
class ConversationModel:
    def __init__(self):
        self.messages = []
        # ...
    
    def add_user_message(self, message):
        # Add user message to history
        
    def add_assistant_message(self, message):
        # Add assistant message to history
        
    def add_tool_call(self, tool_name, arguments, result):
        # Add tool call to history
        
    def export_conversation(self, file_path):
        # Export conversation to file
        
    def import_conversation(self, file_path):
        # Import conversation from file
```

## Data Models

### Message
Represents a message in the conversation history.

```python
@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
```

### ToolCall
Represents a tool call in the conversation history.

```python
@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    timestamp: datetime
```

### Conversation
Represents a complete conversation session.

```python
@dataclass
class Conversation:
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    messages: List[Union[Message, ToolCall]]
```

### UIConfig
Represents UI-specific configuration.

```python
@dataclass
class UIConfig:
    theme: str  # "light", "dark", or "system"
    font_size: int
    window_size: Tuple[int, int]
    window_position: Tuple[int, int]
    show_tool_panel: bool
```

## Error Handling

The UI will implement comprehensive error handling to provide a smooth user experience:

1. **Connection Errors**:
   - Display error messages in the UI
   - Provide retry options
   - Offer troubleshooting guidance

2. **Tool Call Errors**:
   - Show error details in the conversation
   - Suggest possible solutions
   - Allow retrying failed tool calls

3. **Configuration Errors**:
   - Validate input before saving
   - Provide clear error messages
   - Highlight problematic fields

4. **Runtime Errors**:
   - Catch and log exceptions
   - Show user-friendly error messages
   - Prevent application crashes

## Testing Strategy

The testing strategy will include:

1. **Unit Tests**:
   - Test individual UI components
   - Test controller logic
   - Test model components

2. **Integration Tests**:
   - Test interaction between UI and agent
   - Test configuration loading and saving
   - Test conversation flow

3. **End-to-End Tests**:
   - Test complete user workflows
   - Test cross-platform compatibility
   - Test with different MCP servers

4. **Usability Testing**:
   - Gather feedback from users
   - Test with different screen sizes
   - Test accessibility features

## Implementation Considerations

### Cross-Platform Compatibility
- Use PyQt6 for cross-platform UI
- Test on Windows, macOS, and Linux
- Handle platform-specific differences

### Performance
- Use asynchronous operations for non-blocking UI
- Optimize rendering for large conversations
- Implement efficient data structures

### Security
- Securely store API keys
- Validate user input
- Handle sensitive information properly

### Accessibility
- Support keyboard navigation
- Implement screen reader compatibility
- Provide high-contrast themes

### Internationalization
- Design for localization
- Use translatable strings
- Support right-to-left languages

## UI Mockups

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ MCP Agent                                              _ □ X │
├─────────────────────────────────────────────────────────────┤
│ File  Edit  View  Tools  Help                               │
├───────────────────────────────┬─────────────────────────────┤
│                               │                             │
│                               │                             │
│                               │                             │
│                               │                             │
│       Chat Panel              │      Tools Panel            │
│                               │                             │
│                               │                             │
│                               │                             │
│                               │                             │
│                               │                             │
├───────────────────────────────┴─────────────────────────────┤
│ Status: Connected to filesystem server | OpenAI (gpt-4)     │
└─────────────────────────────────────────────────────────────┘
```

### Chat Panel

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  👤 User: How can I list files in the current directory?    │
│                                                             │
│  🤖 Assistant: I can help you list files in the current     │
│  directory. I'll use the filesystem.list_files tool.        │
│                                                             │
│  🔧 Tool: filesystem.list_files                             │
│  Arguments: { "path": "." }                                 │
│  Result: [                                                  │
│    { "name": "file1.txt", "type": "file", "size": 1024 },   │
│    { "name": "dir1", "type": "directory" }                  │
│  ]                                                          │
│                                                             │
│  🤖 Assistant: Here are the files in the current directory: │
│  - file1.txt (file, 1 KB)                                   │
│  - dir1 (directory)                                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Type a message...                                   Send ▶ │
└─────────────────────────────────────────────────────────────┘
```

### Settings Dialog

```
┌─────────────────────────────────────────────────────────────┐
│ Settings                                              _ □ X │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐                                             │
│ │ General     │  LLM Provider                               │
│ │ LLM         │  ┌─────────────────────────────────────┐    │
│ │ MCP Servers │  │ OpenAI                           ▼ │    │
│ │             │  └─────────────────────────────────────┘    │
│ │             │                                             │
│ │             │  Model                                      │
│ │             │  ┌─────────────────────────────────────┐    │
│ │             │  │ gpt-4                             ▼ │    │
│ │             │  └─────────────────────────────────────┘    │
│ │             │                                             │
│ │             │  API Key                                    │
│ │             │  ┌─────────────────────────────────────┐    │
│ │             │  │ ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●● │    │
│ │             │  └─────────────────────────────────────┘    │
│ │             │                                             │
│ └─────────────┘                                             │
│                                                             │
│                                          Cancel     Save    │
└─────────────────────────────────────────────────────────────┘
```