# MCP Agent

A Python agent that connects to MCP (Model Context Protocol) servers with pluggable LLM backends, similar to Claude Code.

## Features

- 🔌 **Pluggable LLM backends**: Switch between OpenAI, Anthropic, or custom LLMs
- 🛠️ **MCP protocol support**: Full support for MCP tools and resources
- 💬 **Interactive interfaces**: Choose between CLI (terminal) or GUI mode
- ⚙️ **Configurable**: Easy YAML-based configuration
- 🔍 **Tool discovery**: Automatically discovers available tools from MCP servers
- 🛡️ **Error handling**: Robust error handling for network and API issues
- 📝 **Resource support**: Read and work with MCP resources

## Architecture

The agent consists of several key components:

1. **MCPClient**: Handles communication with MCP servers via JSON-RPC
2. **LLMProvider**: Abstract interface for different LLM providers (OpenAI, Anthropic, custom)
3. **MCPAgent**: Main orchestrator that coordinates between LLM and MCP tools
4. **ConfigManager**: Manages configuration and settings
5. **UI Components**: Modular GUI components for the graphical interface

## Installation

### Prerequisites

- Python 3.8+
- MCP server implementations (e.g., filesystem, git, browser)
- PyQt6 (for GUI mode)

### Setup

1. **Clone or download the code**
2. **Install dependencies:**
   ```bash
   # Core dependencies
   pip install pyyaml openai anthropic
   
   # GUI dependencies (optional, only needed for GUI mode)
   pip install PyQt6
   ```

3. **Set up API keys:**
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   ```

4. **Install MCP servers** (examples):
   ```bash
   pip install mcp-server-filesystem
   pip install mcp-server-git
   pip install mcp-server-browser
   ```

## Configuration

The agent uses a YAML configuration file located at `~/.mcp-agent/config.yaml`. A default configuration is created on first run:

```yaml
llm:
  provider: openai  # or anthropic
  model: gpt-4     # or claude-3-sonnet-20240229
  api_key: your-api-key-here

mcp_servers:
  filesystem:
    command: ["python", "-m", "mcp_server_filesystem"]
    args: ["--path", "."]
  
  git:
    command: ["python", "-m", "mcp_server_git"]
    args: ["--repository", "."]
  
  browser:
    command: ["python", "-m", "mcp_server_browser"]
    args: []

default_server: filesystem
```

## Usage

### Command Line Arguments

The application supports both CLI (Command Line Interface) and GUI (Graphical User Interface) modes.

```bash
python main.py [options]
```

#### Interface Mode Options
- `--gui`: Run in GUI mode (default is CLI mode)

#### Common Options
- `--config PATH`: Path to configuration file
- `--verbose`: Enable verbose logging

#### CLI-specific Options
- `--server SERVER`: MCP server to connect to
- `--llm {openai,anthropic}`: LLM provider to use
- `--model MODEL`: LLM model to use

### CLI Mode Examples

**Basic usage:**
```bash
python main.py
```

**With specific server:**
```bash
python main.py --server filesystem
```

**With specific LLM:**
```bash
python main.py --llm anthropic --model claude-3-sonnet-20240229
```

**With custom config:**
```bash
python main.py --config /path/to/config.yaml
```

**Verbose logging:**
```bash
python main.py --verbose
```

### GUI Mode Examples

**Launch GUI:**
```bash
python main.py --gui
```

**Launch GUI with custom config:**
```bash
python main.py --gui --config /path/to/config.yaml
```

**Launch GUI with verbose logging:**
```bash
python main.py --gui --verbose
```

### Programmatic Usage

```python
import asyncio
from mcp_agent import MCPAgent, MCPClient, OpenAIProvider

async def main():
    # Configure MCP server
    server_config = {
        "command": ["python", "-m", "mcp_server_filesystem"],
        "args": ["--path", "."]
    }
    
    # Create components
    mcp_client = MCPClient(server_config)
    llm_provider = OpenAIProvider("your-api-key", "gpt-4")
    agent = MCPAgent(llm_provider, mcp_client)
    
    try:
        # Start the agent
        await agent.start()
        
        # Process messages
        response = await agent.process_message("List files in current directory")
        print(response)
        
    finally:
        await agent.cleanup()

asyncio.run(main())
```

## Example Interactions

Once running, you can interact with the agent like this:

```
👤 You: What files are in the current directory?
🤖 Assistant: I'll check the current directory for you.

I found the following files in the current directory:
- mcp_agent.py (Main agent implementation)
- config.yaml (Configuration file)
- README.md (Documentation)
- requirements.txt (Python dependencies)
- examples/ (Example usage directory)

👤 You: Can you read the README.md file and summarize it?
🤖 Assistant: I'll read the README.md file for you.

The README.md file contains documentation for the MCP Agent project. It describes:
- A Python agent for connecting to MCP servers
- Support for multiple LLM providers (OpenAI, Anthropic)
- Interactive chat interface
- Configuration options
- Installation and usage instructions
- Examples of programmatic usage

👤 You: Create a new file called test.txt with some sample content
🤖 Assistant: I'll create a new file called test.txt with sample content for you.

I've successfully created test.txt with sample content. The file contains:
- A welcome message
- Current timestamp
- Some example text for testing

The file has been saved to the current directory.
```

## Supported LLM Providers

### OpenAI
- Models: gpt-4, gpt-3.5-turbo, etc.
- Requires: `OPENAI_API_KEY`
- Features: Full tool calling support

### Anthropic
- Models: claude-3-sonnet-20240229, claude-3-opus-20240229, etc.
- Requires: `ANTHROPIC_API_KEY`
- Features: Full tool calling support

### Custom LLM Provider
You can implement your own LLM provider by extending the `LLMProvider` base class:

```python
class CustomLLMProvider(LLMProvider):
    async def generate_response(self, messages, tools=None):
        # Your implementation here
        pass
    
    async def generate_tool_call(self, messages, tools):
        # Your implementation here
        pass
```

## MCP Server Support

The agent supports any MCP server that implements the MCP protocol. Popular servers include:

- **filesystem**: File system operations
- **git**: Git repository operations
- **browser**: Web browsing capabilities
- **database**: Database operations
- **api**: REST API interactions

## Error Handling

The agent includes comprehensive error handling:

- **Connection errors**: Automatic retry and graceful degradation
- **API errors**: Clear error messages and fallback options
- **Tool errors**: Detailed error reporting and recovery
- **Configuration errors**: Helpful setup guidance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**"MCP server not found"**
- Check that the MCP server is installed: `pip install mcp-server-filesystem`
- Verify the command path in your configuration

**"API key not found"**
- Set environment variables: `export OPENAI_API_KEY="your-key"`
- Or add to configuration file

**"Connection refused"**
- Ensure MCP server is properly configured
- Check server logs for detailed error messages

**"Tool not found"**
- Verify the MCP server supports the requested tool
- Check tool discovery logs with `--verbose` flag

### Debug Mode

Run with verbose logging to see detailed information:
```bash
python main.py --verbose
```

This will show:
- MCP server connection details
- Tool discovery process
- API calls and responses
- Error stack traces

## GUI Mode Features

The GUI interface provides a user-friendly way to interact with the MCP Agent:

- **Chat Panel**: Interactive chat interface with message history
- **Tools Panel**: Visual display of available MCP tools and resources
- **Settings Dialog**: Configure LLM providers and MCP servers
- **Status Bar**: Real-time connection and processing status
- **Error Handling**: Visual error notifications and recovery options

### GUI Components

The GUI is built with PyQt6 and follows a Model-View-Controller (MVC) architecture:

1. **Models**: Data structures for conversations and configuration
2. **Views**: UI components for user interaction
3. **Controllers**: Logic for handling user actions and coordinating between models and views

### GUI Screenshots

*Screenshots will be added here*

## Roadmap

- [ ] Support for more LLM providers (Llama, Mistral, etc.)
- [ ] Plugin system for custom tools
- [x] GUI interface
- [ ] Multi-server orchestration
- [ ] Conversation persistence
- [ ] Performance optimizations