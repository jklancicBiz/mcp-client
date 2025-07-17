"""Anthropic LLM provider implementation"""

from typing import Dict, List, Optional, Any

from .base import LLMProvider
from ..core.models import MCPTool


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        
        # Import Anthropic client
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[MCPTool]] = None) -> str:
        """Generate a response using Anthropic"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=messages,
            tools=self._format_tools_for_anthropic(tools) if tools else None
        )
        
        return response.content[0].text
    
    async def generate_tool_call(self, messages: List[Dict[str, str]], tools: List[MCPTool]) -> Dict[str, Any]:
        """Generate a tool call using Anthropic"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=messages,
            tools=self._format_tools_for_anthropic(tools)
        )
        
        for content in response.content:
            if content.type == "tool_use":
                return {
                    "tool_name": content.name,
                    "arguments": content.input
                }
        
        return {}
    
    def _format_tools_for_anthropic(self, tools: List[MCPTool]) -> List[Dict[str, Any]]:
        """Format MCP tools for Anthropic API"""
        formatted_tools = []
        for tool in tools:
            formatted_tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        return formatted_tools