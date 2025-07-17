"""OpenAI LLM provider implementation"""

import json
from typing import Dict, List, Optional, Any

from .base import LLMProvider
from ..core.models import MCPTool


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        
        # Import OpenAI client
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[MCPTool]] = None) -> str:
        """Generate a response using OpenAI"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._format_tools_for_openai(tools) if tools else None
        )
        
        return response.choices[0].message.content
    
    async def generate_tool_call(self, messages: List[Dict[str, str]], tools: List[MCPTool]) -> Dict[str, Any]:
        """Generate a tool call using OpenAI"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._format_tools_for_openai(tools),
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "tool_name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments)
            }
        
        return {}
    
    def _format_tools_for_openai(self, tools: List[MCPTool]) -> List[Dict[str, Any]]:
        """Format MCP tools for OpenAI API"""
        formatted_tools = []
        for tool in tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
            })
        return formatted_tools