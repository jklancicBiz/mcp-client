"""
Error handling system for MCP Agent UI.

This module provides centralized error handling for the MCP Agent UI.
"""

import logging
import traceback
import sys
from enum import Enum
from typing import Optional, Dict, Any, Callable
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

from mcp_agent.core.exceptions import MCPError, MCPConnectionError, MCPToolError


class ErrorSeverity(Enum):
    """Enum for error severity levels."""
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3


class ErrorHandler(QObject):
    """Centralized error handler for the MCP Agent UI."""
    
    # Signal emitted when an error occurs
    error_occurred = pyqtSignal(str, int)  # message, severity
    
    # Mapping of exception types to user-friendly messages
    ERROR_MESSAGES = {
        MCPConnectionError: "Failed to connect to MCP server. Please check your connection settings.",
        MCPToolError: "An error occurred while executing a tool. Please try again.",
        ValueError: "Invalid value provided. Please check your input.",
        KeyError: "Required configuration key not found. Please check your settings.",
        FileNotFoundError: "File not found. Please check the file path.",
        PermissionError: "Permission denied. Please check your file permissions.",
        TimeoutError: "Operation timed out. Please try again later.",
    }
    
    def __init__(self):
        """Initialize the error handler."""
        super().__init__()
        self.logger = logging.getLogger("mcp_agent.ui.error_handler")
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler to root logger if not already added
        if not root_logger.handlers:
            root_logger.addHandler(console_handler)
            
        # Create file handler
        try:
            file_handler = logging.FileHandler("mcp_agent.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except (PermissionError, FileNotFoundError) as e:
            # Log to console if file handler creation fails
            self.logger.warning(f"Could not create log file: {e}")
    
    def handle_exception(self, exception: Exception, context: Optional[str] = None, 
                         severity: ErrorSeverity = ErrorSeverity.ERROR,
                         show_dialog: bool = False, parent=None) -> str:
        """Handle an exception and return a user-friendly error message.
        
        Args:
            exception: The exception to handle.
            context: Optional context information about where the error occurred.
            severity: The severity level of the error.
            show_dialog: Whether to show an error dialog.
            parent: Parent widget for the error dialog.
            
        Returns:
            A user-friendly error message.
        """
        # Get exception details
        exc_type = type(exception)
        exc_message = str(exception)
        exc_traceback = traceback.format_exc()
        
        # Get user-friendly message
        user_message = self._get_user_message(exc_type, exc_message)
        
        # Add context if provided
        if context:
            user_message = f"{context}: {user_message}"
        
        # Log the error
        self._log_error(user_message, exc_message, exc_traceback, severity)
        
        # Emit error signal
        self.error_occurred.emit(user_message, severity.value)
        
        # Show error dialog if requested
        if show_dialog and parent:
            self._show_error_dialog(user_message, exc_message, severity, parent)
        
        return user_message
    
    def _get_user_message(self, exc_type: type, exc_message: str) -> str:
        """Get a user-friendly error message for the exception type.
        
        Args:
            exc_type: The exception type.
            exc_message: The exception message.
            
        Returns:
            A user-friendly error message.
        """
        # Check if we have a specific message for this exception type
        for exception_class, message in self.ERROR_MESSAGES.items():
            if issubclass(exc_type, exception_class):
                return message
        
        # If no specific message, use a generic one with the exception message
        return f"An error occurred: {exc_message}"
    
    def _log_error(self, user_message: str, exc_message: str, 
                  exc_traceback: str, severity: ErrorSeverity):
        """Log the error with appropriate severity.
        
        Args:
            user_message: The user-friendly error message.
            exc_message: The exception message.
            exc_traceback: The exception traceback.
            severity: The severity level of the error.
        """
        log_message = f"{user_message}\nOriginal error: {exc_message}\n{exc_traceback}"
        
        if severity == ErrorSeverity.INFO:
            self.logger.info(log_message)
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(log_message)
        elif severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
    
    def _show_error_dialog(self, user_message: str, exc_message: str, 
                          severity: ErrorSeverity, parent):
        """Show an error dialog with the error message.
        
        Args:
            user_message: The user-friendly error message.
            exc_message: The exception message.
            severity: The severity level of the error.
            parent: Parent widget for the error dialog.
        """
        # Determine icon based on severity
        if severity == ErrorSeverity.INFO:
            icon = QMessageBox.Icon.Information
            title = "Information"
        elif severity == ErrorSeverity.WARNING:
            icon = QMessageBox.Icon.Warning
            title = "Warning"
        elif severity == ErrorSeverity.ERROR:
            icon = QMessageBox.Icon.Critical
            title = "Error"
        elif severity == ErrorSeverity.CRITICAL:
            icon = QMessageBox.Icon.Critical
            title = "Critical Error"
        
        # Create message box
        msg_box = QMessageBox(parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(user_message)
        
        # Add details if available
        if exc_message and exc_message != str(user_message):
            msg_box.setDetailedText(f"Technical details: {exc_message}")
        
        # Add buttons based on severity
        if severity == ErrorSeverity.CRITICAL:
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
        else:
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Show dialog
        msg_box.exec()
    
    def show_error_message(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR,
                          show_dialog: bool = False, parent=None):
        """Show an error message without an exception.
        
        Args:
            message: The error message to show.
            severity: The severity level of the error.
            show_dialog: Whether to show an error dialog.
            parent: Parent widget for the error dialog.
        """
        # Log the error
        self._log_error(message, message, "", severity)
        
        # Emit error signal
        self.error_occurred.emit(message, severity.value)
        
        # Show error dialog if requested
        if show_dialog and parent:
            self._show_error_dialog(message, "", severity, parent)
    
    def get_fallback_options(self, error_type: type) -> Dict[str, Callable]:
        """Get fallback options for a specific error type.
        
        Args:
            error_type: The type of error.
            
        Returns:
            A dictionary of option name -> callback function.
        """
        fallback_options = {}
        
        # Add fallback options based on error type
        if issubclass(error_type, MCPConnectionError):
            fallback_options["Retry Connection"] = lambda: None  # Placeholder
            fallback_options["Change Server"] = lambda: None  # Placeholder
            fallback_options["Work Offline"] = lambda: None  # Placeholder
        elif issubclass(error_type, MCPToolError):
            fallback_options["Retry Tool"] = lambda: None  # Placeholder
            fallback_options["Skip Tool"] = lambda: None  # Placeholder
        
        return fallback_options