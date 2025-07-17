"""
Conversation model for MCP Agent.

This module provides the data models for representing conversations.
"""

from dataclasses import dataclass, field
from typing import List, Union, Dict, Any, Optional
from datetime import datetime
import uuid

@dataclass
class Message:
    """Represents a message in a conversation."""
    
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ToolCall:
    """Represents a tool call in a conversation."""
    
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Conversation:
    """Represents a complete conversation session."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    messages: List[Union[Message, ToolCall]] = field(default_factory=list)
    
    def add_user_message(self, content: str) -> Message:
        """Add a user message to the conversation.
        
        Args:
            content: The message content.
            
        Returns:
            The created message.
        """
        message = Message(role="user", content=content)
        self.messages.append(message)
        return message
    
    def add_assistant_message(self, content: str) -> Message:
        """Add an assistant message to the conversation.
        
        Args:
            content: The message content.
            
        Returns:
            The created message.
        """
        message = Message(role="assistant", content=content)
        self.messages.append(message)
        return message
    
    def add_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: Any) -> ToolCall:
        """Add a tool call to the conversation.
        
        Args:
            tool_name: The name of the tool.
            arguments: The arguments passed to the tool.
            result: The result of the tool call.
            
        Returns:
            The created tool call.
        """
        tool_call = ToolCall(tool_name=tool_name, arguments=arguments, result=result)
        self.messages.append(tool_call)
        return tool_call
    
    def end(self):
        """End the conversation."""
        self.end_time = datetime.now()