"""
Tests for the conversation models.
"""

import unittest
from datetime import datetime
from mcp_agent.ui.models.conversation import Message, ToolCall, Conversation


class TestMessage(unittest.TestCase):
    """Tests for the Message class."""
    
    def test_init(self):
        """Test initialization of a Message."""
        message = Message(role="user", content="Hello")
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")
        self.assertIsInstance(message.timestamp, datetime)
    
    def test_custom_timestamp(self):
        """Test initialization with a custom timestamp."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        message = Message(role="assistant", content="Hi there", timestamp=timestamp)
        self.assertEqual(message.timestamp, timestamp)


class TestToolCall(unittest.TestCase):
    """Tests for the ToolCall class."""
    
    def test_init(self):
        """Test initialization of a ToolCall."""
        arguments = {"path": "/tmp"}
        result = {"files": ["file1.txt", "file2.txt"]}
        tool_call = ToolCall(tool_name="list_files", arguments=arguments, result=result)
        self.assertEqual(tool_call.tool_name, "list_files")
        self.assertEqual(tool_call.arguments, arguments)
        self.assertEqual(tool_call.result, result)
        self.assertIsInstance(tool_call.timestamp, datetime)
    
    def test_custom_timestamp(self):
        """Test initialization with a custom timestamp."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        arguments = {"query": "python"}
        result = {"results": ["python.org"]}
        tool_call = ToolCall(
            tool_name="search", 
            arguments=arguments, 
            result=result, 
            timestamp=timestamp
        )
        self.assertEqual(tool_call.timestamp, timestamp)


class TestConversation(unittest.TestCase):
    """Tests for the Conversation class."""
    
    def test_init(self):
        """Test initialization of a Conversation."""
        conversation = Conversation()
        self.assertIsNotNone(conversation.id)
        self.assertIsInstance(conversation.start_time, datetime)
        self.assertIsNone(conversation.end_time)
        self.assertEqual(conversation.messages, [])
    
    def test_add_user_message(self):
        """Test adding a user message to the conversation."""
        conversation = Conversation()
        message = conversation.add_user_message("Hello")
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0], message)
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")
    
    def test_add_assistant_message(self):
        """Test adding an assistant message to the conversation."""
        conversation = Conversation()
        message = conversation.add_assistant_message("Hi there")
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0], message)
        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.content, "Hi there")
    
    def test_add_tool_call(self):
        """Test adding a tool call to the conversation."""
        conversation = Conversation()
        arguments = {"path": "/tmp"}
        result = {"files": ["file1.txt", "file2.txt"]}
        tool_call = conversation.add_tool_call("list_files", arguments, result)
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0], tool_call)
        self.assertEqual(tool_call.tool_name, "list_files")
        self.assertEqual(tool_call.arguments, arguments)
        self.assertEqual(tool_call.result, result)
    
    def test_end(self):
        """Test ending a conversation."""
        conversation = Conversation()
        self.assertIsNone(conversation.end_time)
        conversation.end()
        self.assertIsNotNone(conversation.end_time)
        self.assertIsInstance(conversation.end_time, datetime)
    
    def test_message_sequence(self):
        """Test adding a sequence of messages and tool calls."""
        conversation = Conversation()
        conversation.add_user_message("List files in /tmp")
        conversation.add_assistant_message("I'll list files in /tmp")
        conversation.add_tool_call(
            "list_files", 
            {"path": "/tmp"}, 
            {"files": ["file1.txt", "file2.txt"]}
        )
        conversation.add_assistant_message("Here are the files: file1.txt, file2.txt")
        
        self.assertEqual(len(conversation.messages), 4)
        self.assertEqual(conversation.messages[0].role, "user")
        self.assertEqual(conversation.messages[1].role, "assistant")
        self.assertEqual(conversation.messages[2].tool_name, "list_files")
        self.assertEqual(conversation.messages[3].role, "assistant")


if __name__ == "__main__":
    unittest.main()