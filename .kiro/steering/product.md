# MCP Agent

MCP Agent is a Python application that connects to MCP (Model Context Protocol) servers with pluggable LLM backends. It serves as a bridge between large language models (LLMs) like OpenAI's GPT and Anthropic's Claude, and MCP servers that provide various tools and resources.

## Core Features

- **Pluggable LLM backends**: Supports OpenAI and Anthropic models with an extensible architecture for adding more providers
- **MCP protocol support**: Full implementation of the MCP protocol for tool calling and resource access
- **Interactive chat interface**: Terminal-based chat interface for interacting with the agent
- **Tool discovery**: Automatically discovers available tools from connected MCP servers
- **Resource handling**: Access to MCP resources with proper error handling
- **Configurable**: YAML-based configuration with environment variable fallbacks

## Use Cases

- Interacting with file systems through natural language
- Performing Git operations via conversation
- Web browsing and information retrieval
- Database operations and API interactions
- Custom tool integration through the MCP protocol

The agent is designed to be extensible, allowing developers to add new LLM providers and connect to various MCP server implementations.