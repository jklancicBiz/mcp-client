"""
Tests for the error handling system.
"""

import unittest
from unittest.mock import MagicMock, patch
import logging
from PyQt6.QtCore import QObject

from mcp_agent.ui.error_handler import ErrorHandler, ErrorSeverity
from mcp_agent.core.exceptions import MCPError, MCPConnectionError, MCPToolError


class TestErrorHandler(unittest.TestCase):
    """Test cases for the ErrorHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create error handler
        self.error_handler = ErrorHandler()
        
        # Create mock for signal
        self.error_handler.error_occurred = MagicMock()
        
        # Create mock for logger
        self.mock_logger = MagicMock()
        self.error_handler.logger = self.mock_logger
    
    def test_handle_exception_basic(self):
        """Test basic exception handling."""
        # Create test exception
        test_exception = ValueError("Test error")
        
        # Handle exception
        result = self.error_handler.handle_exception(
            test_exception,
            context="Test context",
            severity=ErrorSeverity.ERROR,
            show_dialog=False
        )
        
        # Check result
        self.assertIn("Invalid value provided", result)
        self.assertIn("Test context", result)
        
        # Check signal emission
        self.error_handler.error_occurred.emit.assert_called_once()
        args = self.error_handler.error_occurred.emit.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertIn("Test context", args[0])
        self.assertEqual(args[1], ErrorSeverity.ERROR.value)
        
        # Check logging
        self.mock_logger.error.assert_called_once()
    
    def test_handle_mcp_connection_error(self):
        """Test handling of MCPConnectionError."""
        # Create test exception
        test_exception = MCPConnectionError("Connection failed")
        
        # Handle exception
        result = self.error_handler.handle_exception(
            test_exception,
            severity=ErrorSeverity.ERROR,
            show_dialog=False
        )
        
        # Check result
        self.assertIn("Failed to connect to MCP server", result)
        
        # Check signal emission
        self.error_handler.error_occurred.emit.assert_called_once()
        
        # Check logging
        self.mock_logger.error.assert_called_once()
    
    def test_handle_mcp_tool_error(self):
        """Test handling of MCPToolError."""
        # Create test exception
        test_exception = MCPToolError("Tool execution failed")
        
        # Handle exception
        result = self.error_handler.handle_exception(
            test_exception,
            severity=ErrorSeverity.WARNING,
            show_dialog=False
        )
        
        # Check result
        self.assertIn("An error occurred while executing a tool", result)
        
        # Check signal emission
        self.error_handler.error_occurred.emit.assert_called_once()
        args = self.error_handler.error_occurred.emit.call_args[0]
        self.assertEqual(args[1], ErrorSeverity.WARNING.value)
        
        # Check logging
        self.mock_logger.warning.assert_called_once()
    
    def test_show_error_message(self):
        """Test showing an error message without an exception."""
        # Show error message
        self.error_handler.show_error_message(
            "Test error message",
            severity=ErrorSeverity.INFO,
            show_dialog=False
        )
        
        # Check signal emission
        self.error_handler.error_occurred.emit.assert_called_once()
        args = self.error_handler.error_occurred.emit.call_args[0]
        self.assertEqual(args[0], "Test error message")
        self.assertEqual(args[1], ErrorSeverity.INFO.value)
        
        # Check logging
        self.mock_logger.info.assert_called_once()
    
    @patch('mcp_agent.ui.error_handler.QMessageBox')
    def test_show_error_dialog(self, mock_message_box):
        """Test showing an error dialog."""
        # Create mock parent
        mock_parent = MagicMock()
        
        # Create mock message box instance
        mock_msg_box_instance = MagicMock()
        mock_message_box.return_value = mock_msg_box_instance
        
        # Show error message with dialog
        self.error_handler.show_error_message(
            "Test error message",
            severity=ErrorSeverity.ERROR,
            show_dialog=True,
            parent=mock_parent
        )
        
        # Check message box creation
        mock_message_box.assert_called_once()
        
        # Check message box configuration
        mock_msg_box_instance.setIcon.assert_called_once()
        mock_msg_box_instance.setWindowTitle.assert_called_once()
        mock_msg_box_instance.setText.assert_called_once_with("Test error message")
        mock_msg_box_instance.exec.assert_called_once()
    
    def test_get_fallback_options(self):
        """Test getting fallback options for different error types."""
        # Test MCPConnectionError
        options = self.error_handler.get_fallback_options(MCPConnectionError)
        self.assertIn("Retry Connection", options)
        self.assertIn("Change Server", options)
        self.assertIn("Work Offline", options)
        
        # Test MCPToolError
        options = self.error_handler.get_fallback_options(MCPToolError)
        self.assertIn("Retry Tool", options)
        self.assertIn("Skip Tool", options)
        
        # Test other error type
        options = self.error_handler.get_fallback_options(ValueError)
        self.assertEqual(len(options), 0)


if __name__ == '__main__':
    unittest.main()