"""
MCP Agent - A Python agent that can connect to MCP servers and use different LLMs
"""

__version__ = "1.0.0"

from .agent.agent import MCPAgent
from .mcp.client import MCPClient
from .llm.openai import OpenAIProvider
from .llm.anthropic import AnthropicProvider
from .config.manager import ConfigManager

__all__ = [
    "MCPAgent",
    "MCPClient", 
    "OpenAIProvider",
    "AnthropicProvider",
    "ConfigManager"
]