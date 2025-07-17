"""Abstract base class for LLM providers"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from ..core.models import MCPTool


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[MCPTool]] = None) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_tool_call(self, messages: List[Dict[str, str]], tools: List[MCPTool]) -> Dict[str, Any]:
        """Generate a tool call from the LLM"""
        pass