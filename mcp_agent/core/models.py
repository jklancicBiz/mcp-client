"""Data models for MCP Agent"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class MCPTool:
    """Represents an MCP tool with its schema"""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPResource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None