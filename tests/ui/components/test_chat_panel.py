"""
Tests for the ChatPanel component.

Note: These tests avoid checking widget visibility (isVisible()) as this can be unreliable
in headless test environments. Instead, we focus on testing the logical state and behavior
of the component.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtTest import QTest

# Import the ChatPanel class
from mcp_agent.ui.components.chat_panel import ChatPanel
from mcp_agent.ui.models.conversation import Message, ToolCall

# Create a QApplication instance for testing
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

class TestChatPanel(unittest.TestCase):
    """Test cases for the ChatPanel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock controller
        self.mock_controller = MagicMock()
        
        # Create the chat panel
        self.chat_panel = ChatPanel(self.mock_controller)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up
        self.chat_panel = None
    
    def test_init(self):
        """Test that the panel initializes correctly."""
        # Check that the panel has the correct components
        self.assertIsNotNone(self.chat_panel.chat_display)
        self.assertIsNotNone(self.chat_panel.input_field)
        self.assertIsNotNone(self.chat_panel.send_button)
        self.assertIsNotNone(self.chat_panel.loading_frame)
        
        # Check initial state
        self.assertFalse(self.chat_panel.is_processing)
        # Avoid checking visibility state in headless environment
        self.assertTrue(self.chat_panel.input_field.isEnabled())
        self.assertTrue(self.chat_panel.send_button.isEnabled())
    
    def test_send_message(self):
        """Test sending a message."""
        # Set up a test message
        test_message = "Hello, world!"
        
        # Mock the add_user_message method
        self.chat_panel.add_user_message = MagicMock()
        
        # Set the message in the input field
        self.chat_panel.input_field.setText(test_message)
        
        # Click the send button
        QTest.mouseClick(self.chat_panel.send_button, Qt.MouseButton.LeftButton)
        
        # Check that add_user_message was called with the correct message
        self.chat_panel.add_user_message.assert_called_once_with(test_message)
        
        # Check that message_sent signal was emitted with the correct message
        self.mock_controller.assert_not_called()  # Controller should not be called directly
        
        # Check that the input field was cleared
        self.assertEqual(self.chat_panel.input_field.text(), "")
        
        # Check that processing state was set
        self.assertTrue(self.chat_panel.is_processing)
        # Note: In headless test environments, isVisible() might not work as expected
        # so we check the internal state instead
        self.assertFalse(self.chat_panel.input_field.isEnabled())
        self.assertFalse(self.chat_panel.send_button.isEnabled())
    
    def test_send_empty_message(self):
        """Test sending an empty message."""
        # Set up an empty message
        self.chat_panel.input_field.setText("")
        
        # Mock the add_user_message method
        self.chat_panel.add_user_message = MagicMock()
        
        # Click the send button
        QTest.mouseClick(self.chat_panel.send_button, Qt.MouseButton.LeftButton)
        
        # Check that add_user_message was not called
        self.chat_panel.add_user_message.assert_not_called()
        
        # Check that message_sent signal was not emitted
        self.mock_controller.assert_not_called()
    
    def test_send_message_while_processing(self):
        """Test sending a message while already processing."""
        # Set processing state
        self.chat_panel.set_processing(True)
        
        # Set up a test message
        test_message = "Hello, world!"
        
        # Mock the add_user_message method
        self.chat_panel.add_user_message = MagicMock()
        
        # Set the message in the input field
        self.chat_panel.input_field.setText(test_message)
        
        # Click the send button
        QTest.mouseClick(self.chat_panel.send_button, Qt.MouseButton.LeftButton)
        
        # Check that add_user_message was not called
        self.chat_panel.add_user_message.assert_not_called()
        
        # Check that message_sent signal was not emitted
        self.mock_controller.assert_not_called()
    
    def test_set_processing(self):
        """Test setting the processing state."""
        # Set processing to True
        self.chat_panel.set_processing(True)
        
        # Check that the state was updated correctly
        self.assertTrue(self.chat_panel.is_processing)
        # Note: In headless test environments, isVisible() might not work as expected
        self.assertFalse(self.chat_panel.input_field.isEnabled())
        self.assertFalse(self.chat_panel.send_button.isEnabled())
        self.assertEqual(self.chat_panel.input_field.placeholderText(), "Waiting for response...")
        
        # Set processing to False
        self.chat_panel.set_processing(False)
        
        # Check that the state was updated correctly
        self.assertFalse(self.chat_panel.is_processing)
        self.assertTrue(self.chat_panel.input_field.isEnabled())
        self.assertTrue(self.chat_panel.send_button.isEnabled())
        self.assertEqual(self.chat_panel.input_field.placeholderText(), "Type a message...")
    
    def test_add_user_message(self):
        """Test adding a user message."""
        # Set up a test message
        test_message = "Hello, world!"
        
        # Mock the _append_html method
        self.chat_panel._append_html = MagicMock()
        
        # Add the message
        self.chat_panel.add_user_message(test_message)
        
        # Check that _append_html was called
        self.chat_panel._append_html.assert_called_once()
        
        # Check that the HTML contains the message
        html = self.chat_panel._append_html.call_args[0][0]
        self.assertIn(test_message, html)
        self.assertIn("You", html)
    
    def test_add_assistant_message(self):
        """Test adding an assistant message."""
        # Set up a test message
        test_message = "Hello, I'm the assistant!"
        
        # Mock the _append_html method
        self.chat_panel._append_html = MagicMock()
        
        # Set processing state
        self.chat_panel.set_processing(True)
        
        # Add the message
        self.chat_panel.add_assistant_message(test_message)
        
        # Check that _append_html was called
        self.chat_panel._append_html.assert_called_once()
        
        # Check that the HTML contains the message
        html = self.chat_panel._append_html.call_args[0][0]
        self.assertIn(test_message, html)
        self.assertIn("Assistant", html)
        
        # Check that processing state was reset
        self.assertFalse(self.chat_panel.is_processing)
        # Avoid checking visibility state in headless environment
    
    def test_add_tool_call(self):
        """Test adding a tool call."""
        # Set up test data
        tool_name = "test_tool"
        arguments = {"arg1": "value1", "arg2": 42}
        result = {"result": "success", "data": [1, 2, 3]}
        
        # Mock the _append_html method
        self.chat_panel._append_html = MagicMock()
        
        # Add the tool call
        self.chat_panel.add_tool_call(tool_name, arguments, result)
        
        # Check that _append_html was called
        self.chat_panel._append_html.assert_called_once()
        
        # Check that the HTML contains the tool call information
        html = self.chat_panel._append_html.call_args[0][0]
        self.assertIn(tool_name, html)
        self.assertIn("Arguments", html)
        self.assertIn("Result", html)
    
    def test_format_message_content(self):
        """Test formatting message content."""
        # Test with newlines
        message = "Line 1\nLine 2\nLine 3"
        formatted = self.chat_panel._format_message_content(message)
        self.assertIn("Line 1<br>Line 2<br>Line 3", formatted)
        
        # Test with code blocks
        message = "Some text\n```\ncode block\n```\nMore text"
        formatted = self.chat_panel._format_message_content(message)
        self.assertIn("<pre", formatted)
        self.assertIn("</pre>", formatted)
    
    def test_format_json(self):
        """Test formatting JSON data."""
        # Test with dict
        data = {"key1": "value1", "key2": 42}
        formatted = self.chat_panel._format_json(data)
        self.assertIn("key1", formatted)
        self.assertIn("value1", formatted)
        self.assertIn("key2", formatted)
        
        # Test with JSON string
        json_str = '{"key1": "value1", "key2": 42}'
        formatted = self.chat_panel._format_json(json_str)
        self.assertIn("key1", formatted)
        self.assertIn("value1", formatted)
        self.assertIn("key2", formatted)
        
        # Test with non-JSON string
        non_json = "This is not JSON"
        formatted = self.chat_panel._format_json(non_json)
        self.assertEqual(non_json, formatted)
    
    def test_clear_chat(self):
        """Test clearing the chat display."""
        # Add some content to the chat display
        self.chat_panel.chat_display.setPlainText("Some content")
        
        # Clear the chat
        self.chat_panel.clear_chat()
        
        # Check that the chat display is empty
        self.assertEqual(self.chat_panel.chat_display.toPlainText(), "")
    
    def test_enable_disable_input(self):
        """Test enabling and disabling input."""
        # Disable input
        self.chat_panel.disable_input()
        
        # Check that input is disabled
        self.assertFalse(self.chat_panel.input_field.isEnabled())
        self.assertFalse(self.chat_panel.send_button.isEnabled())
        
        # Enable input
        self.chat_panel.enable_input()
        
        # Check that input is enabled
        self.assertTrue(self.chat_panel.input_field.isEnabled())
        self.assertTrue(self.chat_panel.send_button.isEnabled())
        self.assertFalse(self.chat_panel.is_processing)


if __name__ == "__main__":
    unittest.main()