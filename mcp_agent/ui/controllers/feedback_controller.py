"""
Feedback Controller for MCP Agent.

This module provides the controller for managing user feedback mechanisms.
"""

import logging
import uuid
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from mcp_agent.ui.components.feedback_manager import FeedbackManager, ProgressType
from mcp_agent.ui.components.notification import NotificationType
from mcp_agent.ui.error_handler import ErrorHandler, ErrorSeverity


class FeedbackController(QObject):
    """Controller for managing user feedback mechanisms."""
    
    # Signal emitted when a long operation starts
    operation_started = pyqtSignal(str, str)  # operation_id, message
    
    # Signal emitted when a long operation completes
    operation_completed = pyqtSignal(str, bool)  # operation_id, success
    
    def __init__(self, parent_window=None):
        """Initialize the feedback controller.
        
        Args:
            parent_window: Parent window for notifications and dialogs.
        """
        super().__init__()
        self.feedback_manager = None
        self.parent_window = parent_window
        self.error_handler = ErrorHandler()
        self.active_operations = {}
        
    def initialize(self, parent_window):
        """Initialize the feedback controller with a parent window.
        
        Args:
            parent_window: Parent window for notifications and dialogs.
        """
        self.parent_window = parent_window
        self.feedback_manager = FeedbackManager(parent_window)
        
        # Set status bar in feedback manager
        if hasattr(parent_window, 'status_bar'):
            self.feedback_manager.set_status_bar(parent_window.status_bar)
        
        # Connect signals from agent controller to feedback manager
        if hasattr(parent_window, 'controller') and hasattr(parent_window.controller, 'agent_controller'):
            agent_controller = parent_window.controller.agent_controller
            agent_controller.error_occurred.connect(self._handle_agent_error)
            agent_controller.connection_status_changed.connect(self._handle_connection_status_change)
            
        # Connect error handler signals
        self.error_handler.error_occurred.connect(self._handle_error)
            
    def _handle_agent_error(self, error_message):
        """Handle error from agent controller.
        
        Args:
            error_message: Error message from agent.
        """
        if self.feedback_manager:
            self.feedback_manager.show_notification(
                error_message,
                NotificationType.ERROR,
                5000
            )
            
    def _handle_connection_status_change(self, connected, server_name):
        """Handle connection status change from agent controller.
        
        Args:
            connected: Whether the agent is connected.
            server_name: Name of the connected server.
        """
        if self.feedback_manager:
            if connected:
                self.feedback_manager.show_status_message(f"Connected to {server_name}")
                self.feedback_manager.show_notification(
                    f"Connected to {server_name}",
                    NotificationType.SUCCESS,
                    3000
                )
            else:
                self.feedback_manager.show_status_message("Disconnected")
                if server_name:
                    self.feedback_manager.show_notification(
                        f"Disconnected from {server_name}",
                        NotificationType.WARNING,
                        3000
                    )
    
    def _handle_error(self, message, severity):
        """Handle error from error handler.
        
        Args:
            message: Error message.
            severity: Error severity level.
        """
        if self.feedback_manager:
            # Map severity to notification type
            notification_type = NotificationType.INFO
            if severity == ErrorSeverity.WARNING.value:
                notification_type = NotificationType.WARNING
            elif severity == ErrorSeverity.ERROR.value or severity == ErrorSeverity.CRITICAL.value:
                notification_type = NotificationType.ERROR
                
            # Show notification
            self.feedback_manager.show_notification(
                message,
                notification_type,
                5000
            )
                    
    def show_status_message(self, message, timeout=0):
        """Show a status message.
        
        Args:
            message: Message to display.
            timeout: Time in milliseconds before reverting to default status (0 for permanent).
        """
        if self.feedback_manager:
            self.feedback_manager.show_status_message(message, timeout)
            
    def set_default_status(self, message):
        """Set the default status message.
        
        Args:
            message: The default message to display.
        """
        if self.feedback_manager:
            self.feedback_manager.set_default_status(message)
            
    def show_notification(self, message, notification_type=NotificationType.INFO, 
                         duration=5000, action_text=None, action_callback=None):
        """Show a notification.
        
        Args:
            message: Message to display.
            notification_type: Type of notification.
            duration: Duration in milliseconds before auto-hiding (0 for no auto-hide).
            action_text: Text for action button (None for no button).
            action_callback: Callback for action button.
            
        Returns:
            The created notification widget.
        """
        if self.feedback_manager:
            return self.feedback_manager.show_notification(
                message,
                notification_type,
                duration,
                action_text,
                action_callback
            )
        return None
        
    def start_progress(self, message, progress_type=ProgressType.INDETERMINATE):
        """Start a progress operation.
        
        Args:
            message: Message to display.
            progress_type: Type of progress indicator.
            
        Returns:
            Operation ID that can be used to update or complete the operation.
        """
        operation_id = str(uuid.uuid4())
        
        if self.feedback_manager:
            self.feedback_manager.start_operation(message, True, progress_type)
            
        # Store operation details
        self.active_operations[operation_id] = {
            'message': message,
            'start_time': QTimer.currentTime().msecsSinceStartOfDay(),
            'progress_type': progress_type
        }
        
        # Emit signal
        self.operation_started.emit(operation_id, message)
        
        return operation_id
        
    def update_progress(self, operation_id, progress=None, message=None):
        """Update a progress operation.
        
        Args:
            operation_id: The operation ID.
            progress: Progress value (None for no update).
            message: New message (None for no update).
        """
        if operation_id not in self.active_operations:
            return
            
        if self.feedback_manager:
            self.feedback_manager.update_operation(operation_id, progress, message)
            
        # Update operation details
        if message:
            self.active_operations[operation_id]['message'] = message
            
    def complete_progress(self, operation_id, success=True, message=None, notification=False):
        """Complete a progress operation.
        
        Args:
            operation_id: The operation ID.
            success: Whether the operation was successful.
            message: Completion message (None for default).
            notification: Whether to show a notification.
        """
        if operation_id not in self.active_operations:
            return
            
        if self.feedback_manager:
            self.feedback_manager.complete_operation(
                operation_id,
                success,
                message,
                notification
            )
            
        # Remove operation from active operations
        operation_details = self.active_operations.pop(operation_id, None)
        
        # Emit signal
        self.operation_completed.emit(operation_id, success)
            
    def run_with_progress(self, message, function, progress_type=ProgressType.INDETERMINATE,
                         success_message=None, error_message=None):
        """Run a function with a progress indicator.
        
        Args:
            message: Message to display.
            function: Function to run.
            progress_type: Type of progress indicator.
            success_message: Message to show on success (None for no message).
            error_message: Message to show on error (None for default error message).
            
        Returns:
            The result of the function.
        """
        operation_id = self.start_progress(message, progress_type)
        
        try:
            # Run function
            result = function()
            
            # Complete progress
            self.complete_progress(
                operation_id,
                success=True,
                message=success_message or f"{message} completed",
                notification=success_message is not None
            )
            
            return result
        except Exception as e:
            # Complete progress with error
            error_msg = error_message or f"{message} failed: {str(e)}"
            self.complete_progress(
                operation_id,
                success=False,
                message=error_msg,
                notification=True
            )
            
            # Log error
            logging.error(f"Error running function: {e}")
            
            # Re-raise exception
            raise
            
    def run_async_operation(self, message, async_function, on_complete=None, on_error=None,
                           progress_type=ProgressType.INDETERMINATE, show_notification=False):
        """Run an asynchronous operation with feedback.
        
        This method is designed to be used with PyQt's QThread or similar async mechanisms.
        The caller is responsible for setting up the async execution and connecting signals.
        
        Args:
            message: Message to display.
            async_function: Async function to run.
            on_complete: Callback for when operation completes successfully.
            on_error: Callback for when operation fails.
            progress_type: Type of progress indicator.
            show_notification: Whether to show a notification on completion.
            
        Returns:
            Operation ID that can be used to update or complete the operation.
        """
        # Start operation
        operation_id = self.start_progress(message, progress_type)
        
        # Define completion handler
        def _on_complete(result):
            self.complete_progress(
                operation_id, 
                success=True,
                message=f"{message} completed",
                notification=show_notification
            )
            if on_complete:
                on_complete(result)
        
        # Define error handler
        def _on_error(error):
            self.complete_progress(
                operation_id,
                success=False,
                message=f"{message} failed: {str(error)}",
                notification=True
            )
            if on_error:
                on_error(error)
        
        # Return operation ID for further updates
        return operation_id, _on_complete, _on_error
        
    def handle_exception(self, exception, context=None, severity=ErrorSeverity.ERROR,
                        show_dialog=False):
        """Handle an exception and show appropriate feedback.
        
        Args:
            exception: The exception to handle.
            context: Optional context information about where the error occurred.
            severity: The severity level of the error.
            show_dialog: Whether to show an error dialog.
            
        Returns:
            A user-friendly error message.
        """
        # Use error handler to get user-friendly message
        user_message = self.error_handler.handle_exception(
            exception,
            context,
            severity,
            show_dialog,
            self.parent_window
        )
        
        return user_message
        
    def pulse_status_message(self, message, interval=1000, count=3):
        """Show a pulsing status message that cycles through variations.
        
        Args:
            message: Base message to display.
            interval: Time in milliseconds between pulses.
            count: Number of variations to cycle through.
            
        Returns:
            Timer that controls the pulsing (call stop() to stop pulsing).
        """
        if not self.feedback_manager:
            return None
            
        # Create variations of the message
        variations = [
            message,
            message + ".",
            message + "..",
            message + "..."
        ]
        
        # Create counter for cycling through variations
        counter = {'index': 0}
        
        # Create timer for pulsing
        timer = QTimer()
        timer.setInterval(interval)
        
        # Connect timer to update function
        def _pulse():
            self.feedback_manager.show_status_message(variations[counter['index'] % len(variations)])
            counter['index'] += 1
            
            # Process events to keep UI responsive
            QApplication.processEvents()
        
        timer.timeout.connect(_pulse)
        
        # Show initial message
        _pulse()
        
        # Start timer
        timer.start()
        
        return timer