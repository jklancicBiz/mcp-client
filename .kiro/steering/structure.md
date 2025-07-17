# Project Structure

## Overview
The MCP Agent project follows a modular package structure with clear separation of concerns. The main package is `mcp_agent` with several subpackages for specific functionality.

## Directory Structure

```
mcp_agent/
├── __init__.py           # Package initialization
├── agent/                # Agent implementation
│   ├── __init__.py
│   └── agent.py          # Main MCPAgent class
├── cli/                  # Command-line interface
│   ├── __init__.py
│   └── main.py           # CLI entry point and argument parsing
├── config/               # Configuration management
│   ├── __init__.py
│   └── manager.py        # ConfigManager for loading/creating configs
├── core/                 # Core components and utilities
│   ├── __init__.py
│   ├── exceptions.py     # Custom exception classes
│   └── models.py         # Data models (MCPTool, MCPResource)
├── llm/                  # LLM provider implementations
│   ├── __init__.py
│   ├── anthropic.py      # Anthropic Claude integration
│   ├── base.py           # Abstract LLMProvider base class
│   └── openai.py         # OpenAI GPT integration
└── mcp/                  # MCP protocol implementation
    ├── __init__.py
    └── client.py         # MCPClient for server communication
```

## Key Files

- **main.py**: Root entry point that runs the CLI main function
- **mcp_agent/cli/main.py**: Command-line interface and argument parsing
- **mcp_agent/agent/agent.py**: Core agent implementation that coordinates LLM and MCP
- **mcp_agent/config/manager.py**: Configuration loading and management
- **mcp_agent/llm/base.py**: Abstract base class for LLM providers
- **mcp_agent/mcp/client.py**: Client for MCP server communication

## Code Organization Principles

1. **Modularity**: Each component is isolated in its own module with clear responsibilities
2. **Abstraction**: Abstract base classes define interfaces for extensibility
3. **Dependency Injection**: Components receive their dependencies through constructors
4. **Error Handling**: Custom exceptions for different error scenarios
5. **Asynchronous Design**: Uses asyncio for non-blocking operations

## Extension Points

- **LLM Providers**: Add new providers by implementing the `LLMProvider` interface
- **MCP Tools**: New tools are discovered automatically from MCP servers
- **Configuration**: Extend the ConfigManager for additional settings