# Technical Stack

## Languages and Requirements
- **Python**: 3.8+ required
- **Dependencies**:
  - asyncio: For asynchronous operations
  - pyyaml: For configuration management
  - openai (>=1.0.0): For OpenAI LLM integration
  - anthropic (>=0.8.0): For Anthropic LLM integration

## Architecture
The project follows a modular architecture with clear separation of concerns:
- **LLM Providers**: Abstract interface with concrete implementations for different LLM services
- **MCP Client**: Handles communication with MCP servers via JSON-RPC
- **Agent**: Orchestrates interactions between LLMs and MCP tools
- **Config Manager**: Handles configuration loading and defaults

## Build System
The project uses standard Python setuptools for packaging and distribution.

## Common Commands

### Installation
```bash
# Install from source
pip install -e .

# Install dependencies only
pip install -r requirements.txt
```

### Configuration
```bash
# Set API keys as environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Running the Agent
```bash
# Basic usage
python main.py

# With specific server
python main.py --server filesystem

# With specific LLM
python main.py --llm anthropic --model claude-3-sonnet-20240229

# With custom config
python main.py --config /path/to/config.yaml

# With verbose logging
python main.py --verbose
```

### MCP Server Setup
```bash
# Install MCP servers
pip install mcp-server-filesystem
pip install mcp-server-git
pip install mcp-server-browser
```

## Testing
No formal testing framework is currently implemented in the codebase.