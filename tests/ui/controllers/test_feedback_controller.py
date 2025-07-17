"""
Tests for the feedback controller.
"""

import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal

from mcp_agent.ui.controllers.feedback_controller import FeedbackController
from mcp_agent.ui.components.notification import NotificationType
from mcp_agent.ui.components.feedback_manager import ProgressType
from mcp_agent.ui.error_handler import ErrorSeverity


class TestFeedbackController(unittest.TestCase):
    """Test cases for the FeedbackController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock parent window
        self.mock_parent = MagicMock()
        self.mock_status_bar = MagicMock()
        self.mock_parent.status_bar = self.mock_status_bar
        
        # Create feedback controller
        self.feedback_controller = FeedbackController()
        
        # Mock feedback manager
        self.mock_feedback_manager = MagicMock()
        self.feedback_controller.feedback_manager = self.mock_feedback_manager
        
        # Mock error handler
        self.mock_error_handler = MagicMock()
        self.feedback_controller.error_handler = self.mock_error_handler
        
        # Mock signals
        self.feedback_controller.operation_started = MagicMock()
        self.feedback_controller.operation_completed = MagicMock()
    
    def test_initialize(self):
        """Test initialization with parent window."""
        # Create mock agent controller
        mock_agent_controller = MagicMock()
        mock_agent_controller.error_occurred = MagicMock()
        mock_agent_controller.connection_status_changed = MagicMock()
        
        # Create mock parent window with controller
        mock_parent = MagicMock()
        mock_parent.controller = MagicMock()
        mock_parent.controller.agent_controller = mock_agent_controller
        mock_parent.status_bar = self.mock_status_bar
        
        # Initialize with parent window
        with patch('mcp_agent.ui.controllers.feedback_controller.FeedbackManager') as mock_feedback_manager_class:
            # Create mock feedback manager
            mock_feedback_manager = MagicMock()
            mock_feedback_manager_class.return_value = mock_feedback_manager
            
            # Initialize
            self.feedback_controller.initialize(mock_parent)
            
            # Check feedback manager creation
            mock_feedback_manager_class.assert_called_once_with(mock_parent)
            
            # Check status bar setting
            mock_feedback_manager.set_status_bar.assert_called_once_with(mock_parent.status_bar)
            
            # Check signal connections
            mock_agent_controller.error_occurred.connect.assert_called_once()
            mock_agent_controller.connection_status_changed.connect.assert_called_once()
    
    def test_handle_agent_error(self):
        """Test handling agent error."""
        # Call handler
        self.feedback_controller._handle_agent_error("Test error")
        
        # Check notification
        self.mock_feedback_manager.show_notification.assert_called_once_with(
            "Test error",
            NotificationType.ERROR,
            5000
        )
    
    def test_handle_connection_status_change_connected(self):
        """Test handling connection status change when connected."""
        # Call handler
        self.feedback_controller._handle_connection_status_change(True, "test-server")
        
        # Check status message
        self.mock_feedback_manager.show_status_message.assert_called_once_with("Connected to test-server")
        
        # Check notification
        self.mock_feedback_manager.show_notification.assert_called_once_with(
            "Connected to test-server",
            NotificationType.SUCCESS,
            3000
        )
    
    def test_handle_connection_status_change_disconnected(self):
        """Test handling connection status change when disconnected."""
        # Call handler
        self.feedback_controller._handle_connection_status_change(False, "test-server")
        
        # Check status message
        self.mock_feedback_manager.show_status_message.assert_called_once_with("Disconnected")
        
        # Check notification
        self.mock_feedback_manager.show_notification.assert_called_once_with(
            "Disconnected from test-server",
            NotificationType.WARNING,
            3000
        )
    
    def test_handle_error(self):
        """Test handling error from error handler."""
        # Call handler
        self.feedback_controller._handle_error("Test error", ErrorSeverity.ERROR.value)
        
        # Check notification
        self.mock_feedback_manager.show_notification.assert_called_once_with(
            "Test error",
            NotificationType.ERROR,
            5000
        )
    
    def test_show_status_message(self):
        """Test showing status message."""
        # Show message
        self.feedback_controller.show_status_message("Test message", 1000)
        
        # Check feedback manager call
        self.mock_feedback_manager.show_status_message.assert_called_once_with("Test message", 1000)
    
    def test_set_default_status(self):
        """Test setting default status."""
        # Set default status
        self.feedback_controller.set_default_status("Default message")
        
        # Check feedback manager call
        self.mock_feedback_manager.set_default_status.assert_called_once_with("Default message")
    
    def test_show_notification(self):
        """Test showing notification."""
        # Mock callback
        mock_callback = MagicMock()
        
        # Show notification
        self.feedback_controller.show_notification(
            "Test notification",
            NotificationType.INFO,
            3000,
            "Action",
            mock_callback
        )
        
        # Check feedback manager call
        self.mock_feedback_manager.show_notification.assert_called_once_with(
            "Test notification",
            NotificationType.INFO,
            3000,
            "Action",
            mock_callback
        )
    
    def test_start_progress(self):
        """Test starting progress operation."""
        # Mock start_operation
        self.mock_feedback_manager.start_operation.return_value = "test-op-id"
        
        # Start progress
        with patch('mcp_agent.ui.controllers.feedback_controller.uuid.uuid4') as mock_uuid:
            # Mock UUID
            mock_uuid.return_value = "test-op-id"
            
            # Start progress
            operation_id = self.feedback_controller.start_progress(
                "Test operation",
                ProgressType.INDETERMINATE
            )
            
            # Check operation ID
            self.assertEqual(operation_id, "test-op-id")
            
            # Check feedback manager call
            self.mock_feedback_manager.start_operation.assert_called_once_with(
                "Test operation",
                True,
                ProgressType.INDETERMINATE
            )
            
            # Check signal emission
            self.feedback_controller.operation_started.emit.assert_called_once_with(
                "test-op-id",
                "Test operation"
            )
    
    def test_update_progress(self):
        """Test updating progress operation."""
        # Add active operation
        self.feedback_controller.active_operations = {
            "test-op-id": {
                "message": "Test operation",
                "start_time": 0,
                "progress_type": ProgressType.DETERMINATE
            }
        }
        
        # Update progress
        self.feedback_controller.update_progress(
            "test-op-id",
            50,
            "Updated message"
        )
        
        # Check feedback manager call
        self.mock_feedback_manager.update_operation.assert_called_once_with(
            "test-op-id",
            50,
            "Updated message"
        )
        
        # Check operation details update
        self.assertEqual(
            self.feedback_controller.active_operations["test-op-id"]["message"],
            "Updated message"
        )
    
    def test_complete_progress(self):
        """Test completing progress operation."""
        # Add active operation
        self.feedback_controller.active_operations = {
            "test-op-id": {
                "message": "Test operation",
                "start_time": 0,
                "progress_type": ProgressType.DETERMINATE
            }
        }
        
        # Complete progress
        self.feedback_controller.complete_progress(
            "test-op-id",
            True,
            "Operation completed",
            True
        )
        
        # Check feedback manager call
        self.mock_feedback_manager.complete_operation.assert_called_once_with(
            "test-op-id",
            True,
            "Operation completed",
            True
        )
        
        # Check operation removal
        self.assertNotIn("test-op-id", self.feedback_controller.active_operations)
        
        # Check signal emission
        self.feedback_controller.operation_completed.emit.assert_called_once_with(
            "test-op-id",
            True
        )
    
    def test_run_with_progress_success(self):
        """Test running function with progress indicator (success case)."""
        # Mock function
        mock_function = MagicMock()
        mock_function.return_value = "test-result"
        
        # Mock start_progress
        with patch.object(self.feedback_controller, 'start_progress') as mock_start_progress:
            # Mock operation ID
            mock_start_progress.return_value = "test-op-id"
            
            # Mock complete_progress
            with patch.object(self.feedback_controller, 'complete_progress') as mock_complete_progress:
                # Run with progress
                result = self.feedback_controller.run_with_progress(
                    "Test operation",
                    mock_function,
                    ProgressType.DETERMINATE,
                    "Operation succeeded",
                    "Operation failed"
                )
                
                # Check result
                self.assertEqual(result, "test-result")
                
                # Check start_progress call
                mock_start_progress.assert_called_once_with(
                    "Test operation",
                    ProgressType.DETERMINATE
                )
                
                # Check function call
                mock_function.assert_called_once()
                
                # Check complete_progress call
                mock_complete_progress.assert_called_once_with(
                    "test-op-id",
                    True,
                    "Operation succeeded",
                    True
                )
    
    def test_run_with_progress_error(self):
        """Test running function with progress indicator (error case)."""
        # Mock function
        mock_function = MagicMock()
        mock_function.side_effect = ValueError("Test error")
        
        # Mock start_progress
        with patch.object(self.feedback_controller, 'start_progress') as mock_start_progress:
            # Mock operation ID
            mock_start_progress.return_value = "test-op-id"
            
            # Mock complete_progress
            with patch.object(self.feedback_controller, 'complete_progress') as mock_complete_progress:
                # Run with progress
                with self.assertRaises(ValueError):
                    self.feedback_controller.run_with_progress(
                        "Test operation",
                        mock_function,
                        ProgressType.DETERMINATE,
                        "Operation succeeded",
                        "Operation failed"
                    )
                
                # Check start_progress call
                mock_start_progress.assert_called_once_with(
                    "Test operation",
                    ProgressType.DETERMINATE
                )
                
                # Check function call
                mock_function.assert_called_once()
                
                # Check complete_progress call
                mock_complete_progress.assert_called_once_with(
                    "test-op-id",
                    False,
                    "Operation failed",
                    True
                )
    
    def test_run_async_operation(self):
        """Test running asynchronous operation."""
        # Mock start_progress
        with patch.object(self.feedback_controller, 'start_progress') as mock_start_progress:
            # Mock operation ID
            mock_start_progress.return_value = "test-op-id"
            
            # Mock callbacks
            mock_on_complete = MagicMock()
            mock_on_error = MagicMock()
            
            # Run async operation
            operation_id, complete_callback, error_callback = self.feedback_controller.run_async_operation(
                "Test operation",
                MagicMock(),
                mock_on_complete,
                mock_on_error,
                ProgressType.INDETERMINATE,
                True
            )
            
            # Check operation ID
            self.assertEqual(operation_id, "test-op-id")
            
            # Check start_progress call
            mock_start_progress.assert_called_once_with(
                "Test operation",
                ProgressType.INDETERMINATE
            )
            
            # Test complete callback
            with patch.object(self.feedback_controller, 'complete_progress') as mock_complete_progress:
                # Call complete callback
                complete_callback("test-result")
                
                # Check complete_progress call
                mock_complete_progress.assert_called_once_with(
                    "test-op-id",
                    True,
                    "Test operation completed",
                    True
                )
                
                # Check on_complete callback
                mock_on_complete.assert_called_once_with("test-result")
            
            # Test error callback
            with patch.object(self.feedback_controller, 'complete_progress') as mock_complete_progress:
                # Call error callback
                error_callback(ValueError("Test error"))
                
                # Check complete_progress call
                mock_complete_progress.assert_called_once_with(
                    "test-op-id",
                    False,
                    "Test operation failed: Test error",
                    True
                )
                
                # Check on_error callback
                mock_on_error.assert_called_once()
    
    def test_handle_exception(self):
        """Test handling exception."""
        # Create test exception
        test_exception = ValueError("Test error")
        
        # Handle exception
        self.feedback_controller.handle_exception(
            test_exception,
            "Test context",
            ErrorSeverity.ERROR,
            True
        )
        
        # Check error handler call
        self.mock_error_handler.handle_exception.assert_called_once_with(
            test_exception,
            "Test context",
            ErrorSeverity.ERROR,
            True,
            self.feedback_controller.parent_window
        )
    
    def test_pulse_status_message(self):
        """Test pulsing status message."""
        # Mock QTimer
        with patch('mcp_agent.ui.controllers.feedback_controller.QTimer') as mock_timer_class:
            # Create mock timer
            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer
            
            # Pulse status message
            timer = self.feedback_controller.pulse_status_message(
                "Loading",
                500,
                3
            )
            
            # Check timer
            self.assertEqual(timer, mock_timer)
            
            # Check timer configuration
            mock_timer.setInterval.assert_called_once_with(500)
            mock_timer.start.assert_called_once()
            
            # Check initial message
            self.mock_feedback_manager.show_status_message.assert_called_once()


if __name__ == '__main__':
    unittest.main()