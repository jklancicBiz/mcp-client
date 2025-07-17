"""
Feedback Manager component for MCP Agent.

This module provides user feedback mechanisms for the MCP Agent UI,
including status messages, progress indicators, and notifications.
"""

import time
import uuid
from enum import Enum
from typing import Optional, Callable, Dict, Any, Union, List
from PyQt6.QtWidgets import QWidget, QStatusBar, QProgressBar, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QEventLoop
from PyQt6.QtGui import QIcon

from mcp_agent.ui.components.notification import NotificationManager, NotificationType
from mcp_agent.ui.components.progress_indicator import ProgressIndicator, ProgressIndicatorType


class ProgressType(Enum):
    """Enum for progress indicator types."""
    DETERMINATE = 0  # Progress with known percentage
    INDETERMINATE = 1  # Progress with unknown percentage (activity indicator)


class FeedbackManager(QObject):
    """Manager for user feedback mechanisms."""
    
    # Signal emitted when status message changes
    status_changed = pyqtSignal(str)
    
    # Signal emitted when progress starts
    progress_started = pyqtSignal(str, str)  # operation_id, message
    
    # Signal emitted when progress updates
    progress_updated = pyqtSignal(str, int, str)  # operation_id, value, message
    
    # Signal emitted when progress completes
    progress_completed = pyqtSignal(str)  # operation_id
    
    # Signal emitted when notification is shown
    notification_shown = pyqtSignal(str, int)  # message, notification_type
    
    # Signal emitted when operation starts
    operation_started = pyqtSignal(str, str)  # operation_id, message
    
    # Signal emitted when operation completes
    operation_completed = pyqtSignal(str, bool)  # operation_id, success
    
    def __init__(self, parent_window: QWidget):
        """Initialize the feedback manager.
        
        Args:
            parent_window: Parent window for notifications and dialogs.
        """
        super().__init__()
        self.parent_window = parent_window
        self.status_bar = parent_window.status_bar if hasattr(parent_window, 'status_bar') else None
        self.notification_manager = NotificationManager(parent_window)
        self.active_progress_bars = {}
        self.status_message_timer = QTimer()
        self.status_message_timer.setSingleShot(True)
        self.status_message_timer.timeout.connect(self._clear_temporary_status)
        self.default_status = "Ready"
    
    def set_status_bar(self, status_bar: QStatusBar):
        """Set the status bar for status messages.
        
        Args:
            status_bar: The status bar widget.
        """
        self.status_bar = status_bar
    
    def show_status_message(self, message: str, timeout: int = 0):
        """Show a message in the status bar.
        
        Args:
            message: The message to display.
            timeout: Time in milliseconds before reverting to default status (0 for permanent).
        """
        if self.status_bar:
            self.status_bar.showMessage(message)
            
            # Cancel any pending timer
            if self.status_message_timer.isActive():
                self.status_message_timer.stop()
            
            # Set timer for temporary messages
            if timeout > 0:
                self.status_message_timer.start(timeout)
            
            # Emit signal
            self.status_changed.emit(message)
    
    def _clear_temporary_status(self):
        """Clear temporary status message and revert to default."""
        if self.status_bar:
            self.status_bar.showMessage(self.default_status)
            self.status_changed.emit(self.default_status)
    
    def set_default_status(self, message: str):
        """Set the default status message.
        
        Args:
            message: The default message to display.
        """
        self.default_status = message
        
        # If no temporary message is active, update status bar
        if not self.status_message_timer.isActive() and self.status_bar:
            self.status_bar.showMessage(self.default_status)
            self.status_changed.emit(self.default_status)
    
    def show_progress(self, operation_id: str, message: str, 
                     progress_type: ProgressType = ProgressType.INDETERMINATE,
                     initial_value: int = 0, maximum: int = 100) -> QProgressBar:
        """Show a progress indicator in the status bar.
        
        Args:
            operation_id: Unique identifier for the operation.
            message: Message to display alongside the progress bar.
            progress_type: Type of progress indicator.
            initial_value: Initial progress value (for determinate progress).
            maximum: Maximum progress value (for determinate progress).
            
        Returns:
            The created progress bar widget.
        """
        if not self.status_bar:
            return None
        
        # Remove existing progress bar with same ID if it exists
        self.hide_progress(operation_id)
        
        # Create label for the message
        label = QLabel(message)
        self.status_bar.addPermanentWidget(label)
        
        # Create progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximumWidth(150)
        progress_bar.setMaximumHeight(15)
        
        if progress_type == ProgressType.INDETERMINATE:
            progress_bar.setRange(0, 0)  # Indeterminate mode
        else:
            progress_bar.setRange(0, maximum)
            progress_bar.setValue(initial_value)
        
        # Add progress bar to status bar
        self.status_bar.addPermanentWidget(progress_bar)
        
        # Store progress bar and label
        self.active_progress_bars[operation_id] = {
            'progress_bar': progress_bar,
            'label': label,
            'type': progress_type
        }
        
        # Emit signal
        self.progress_started.emit(operation_id, message)
        
        return progress_bar
    
    def update_progress(self, operation_id: str, value: int, message: Optional[str] = None):
        """Update a progress indicator.
        
        Args:
            operation_id: Identifier for the operation.
            value: New progress value.
            message: Optional new message to display.
        """
        if operation_id not in self.active_progress_bars:
            return
        
        progress_data = self.active_progress_bars[operation_id]
        progress_bar = progress_data['progress_bar']
        label = progress_data['label']
        
        # Update progress value if determinate
        if progress_data['type'] == ProgressType.DETERMINATE:
            progress_bar.setValue(value)
        
        # Update message if provided
        if message is not None:
            label.setText(message)
        
        # Emit signal
        self.progress_updated.emit(operation_id, value, message if message is not None else label.text())
    
    def hide_progress(self, operation_id: str):
        """Hide a progress indicator.
        
        Args:
            operation_id: Identifier for the operation.
        """
        if operation_id not in self.active_progress_bars:
            return
        
        progress_data = self.active_progress_bars[operation_id]
        progress_bar = progress_data['progress_bar']
        label = progress_data['label']
        
        # Remove widgets from status bar
        self.status_bar.removeWidget(progress_bar)
        self.status_bar.removeWidget(label)
        
        # Delete widgets
        progress_bar.deleteLater()
        label.deleteLater()
        
        # Remove from active progress bars
        del self.active_progress_bars[operation_id]
        
        # Emit signal
        self.progress_completed.emit(operation_id)
    
    def show_notification(self, message: str, 
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5000, action_text: Optional[str] = None,
                         action_callback: Optional[Callable] = None):
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
        notification = self.notification_manager.show_notification(
            message,
            notification_type,
            duration,
            action_text,
            action_callback
        )
        
        # Emit signal
        self.notification_shown.emit(message, notification_type.value)
        
        return notification
    
    def clear_all_notifications(self):
        """Clear all active notifications."""
        self.notification_manager.clear_all()
    
    def clear_all_progress(self):
        """Clear all active progress indicators."""
        for operation_id in list(self.active_progress_bars.keys()):
            self.hide_progress(operation_id)
    
    def run_with_progress(self, operation_id: str, message: str, function: Callable,
                         progress_type: ProgressType = ProgressType.INDETERMINATE,
                         success_message: Optional[str] = None,
                         error_message: Optional[str] = None):
        """Run a function with a progress indicator.
        
        Args:
            operation_id: Unique identifier for the operation.
            message: Message to display alongside the progress bar.
            function: Function to run.
            progress_type: Type of progress indicator.
            success_message: Message to show on success (None for no message).
            error_message: Message to show on error (None for default error message).
            
        Returns:
            The result of the function.
        """
        # Show progress
        self.show_progress(operation_id, message, progress_type)
        
        try:
            # Run function
            result = function()
            
            # Show success message if provided
            if success_message:
                self.show_notification(
                    success_message,
                    NotificationType.SUCCESS,
                    3000
                )
            
            return result
        except Exception as e:
            # Show error message
            error_msg = error_message if error_message else f"Error: {str(e)}"
            self.show_notification(
                error_msg,
                NotificationType.ERROR,
                5000
            )
            
            # Re-raise exception
            raise
        finally:
            # Hide progress
            self.hide_progress(operation_id)
    
    def run_with_status(self, message: str, function: Callable, timeout: int = 0):
        """Run a function with a status message.
        
        Args:
            message: Message to display in the status bar.
            function: Function to run.
            timeout: Time in milliseconds before reverting to default status (0 for permanent).
            
        Returns:
            The result of the function.
        """
        # Show status message
        self.show_status_message(message)
        
        try:
            # Run function
            return function()
        finally:
            # Clear status message after timeout
            if timeout > 0:
                self.show_status_message(message, timeout)
            else:
                self.show_status_message(self.default_status)
    
    def pulse_progress(self, operation_id: str, interval: int = 100):
        """Start pulsing an indeterminate progress bar to make it more visually active.
        
        Args:
            operation_id: Identifier for the operation.
            interval: Pulse interval in milliseconds.
            
        Returns:
            Timer that controls the pulsing (call stop() to stop pulsing).
        """
        if operation_id not in self.active_progress_bars:
            return None
        
        progress_data = self.active_progress_bars[operation_id]
        
        # Only pulse indeterminate progress bars
        if progress_data['type'] != ProgressType.INDETERMINATE:
            return None
        
        # Create timer for pulsing
        timer = QTimer()
        timer.setInterval(interval)
        
        # Connect timer to update function
        def _pulse():
            if operation_id in self.active_progress_bars:
                # Process events to keep UI responsive
                QApplication.processEvents()
            else:
                # Stop timer if progress bar no longer exists
                timer.stop()
        
        timer.timeout.connect(_pulse)
        timer.start()
        
        return timer
        
    def start_operation(self, message: str = None, show_progress: bool = True, 
                       progress_type: ProgressType = ProgressType.INDETERMINATE) -> str:
        """Start a long-running operation with feedback.
        
        Args:
            message: Message to display (None for no message).
            show_progress: Whether to show a progress indicator.
            progress_type: Type of progress indicator.
            
        Returns:
            Operation ID that can be used to update or complete the operation.
        """
        # Generate unique operation ID
        operation_id = str(uuid.uuid4())
        
        # Show status message if provided
        if message:
            self.show_status_message(message)
        
        # Show progress indicator if requested
        if show_progress and self.status_bar:
            self.show_progress(operation_id, message or "Working...", progress_type)
        
        # Emit signal
        self.operation_started.emit(operation_id, message or "")
        
        return operation_id
    
    def update_operation(self, operation_id: str, progress: int = None, message: str = None):
        """Update a running operation.
        
        Args:
            operation_id: The operation ID.
            progress: Progress value (None for no update).
            message: New message (None for no update).
        """
        # Update status message if provided
        if message:
            self.show_status_message(message)
        
        # Update progress if provided
        if progress is not None and operation_id in self.active_progress_bars:
            self.update_progress(operation_id, progress, message)
    
    def complete_operation(self, operation_id: str, success: bool = True, 
                          message: str = None, notification: bool = False,
                          notification_duration: int = 3000):
        """Complete an operation.
        
        Args:
            operation_id: The operation ID.
            success: Whether the operation was successful.
            message: Completion message (None for default).
            notification: Whether to show a notification.
            notification_duration: Duration for the notification in milliseconds.
        """
        # Hide progress indicator
        self.hide_progress(operation_id)
        
        # Show completion message
        if message:
            self.show_status_message(message, timeout=5000)
        
        # Show notification if requested
        if notification:
            notification_type = NotificationType.SUCCESS if success else NotificationType.ERROR
            self.show_notification(
                message or ("Operation completed successfully" if success else "Operation failed"),
                notification_type,
                notification_duration
            )
        
        # Emit signal
        self.operation_completed.emit(operation_id, success)
    
    def run_async_operation(self, message: str, async_function: Callable, 
                           on_complete: Callable = None, on_error: Callable = None,
                           show_progress: bool = True, 
                           progress_type: ProgressType = ProgressType.INDETERMINATE,
                           show_notification: bool = False):
        """Run an asynchronous operation with feedback.
        
        This method is designed to be used with PyQt's QThread or similar async mechanisms.
        The caller is responsible for setting up the async execution and connecting signals.
        
        Args:
            message: Message to display.
            async_function: Async function to run.
            on_complete: Callback for when operation completes successfully.
            on_error: Callback for when operation fails.
            show_progress: Whether to show a progress indicator.
            progress_type: Type of progress indicator.
            show_notification: Whether to show a notification on completion.
            
        Returns:
            Operation ID that can be used to update or complete the operation.
        """
        # Start operation
        operation_id = self.start_operation(message, show_progress, progress_type)
        
        # Define completion handler
        def _on_complete(result):
            self.complete_operation(
                operation_id, 
                success=True,
                message=f"{message} completed",
                notification=show_notification
            )
            if on_complete:
                on_complete(result)
        
        # Define error handler
        def _on_error(error):
            self.complete_operation(
                operation_id,
                success=False,
                message=f"{message} failed: {str(error)}",
                notification=show_notification
            )
            if on_error:
                on_error(error)
        
        # Return operation ID for further updates
        return operation_id