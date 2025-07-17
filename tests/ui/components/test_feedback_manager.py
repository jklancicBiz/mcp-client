"""
Tests for the feedback manager component.
"""

import unittest
from unittest.mock import MagicMock, patch, call
from PyQt6.QtWidgets import QStatusBar, QProgressBar, QLabel, QApplication
from PyQt6.QtCore import QTimer

from mcp_agent.ui.components.feedback_manager import FeedbackManager, ProgressType
from mcp_agent.ui.components.notification import NotificationType
from mcp_agent.ui.components.progress_indicator import ProgressIndicatorType


class TestFeedbackManager(unittest.TestCase):
    """Test cases for the FeedbackManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock parent window
        self.mock_parent = MagicMock()
        self.mock_status_bar = MagicMock(spec=QStatusBar)
        self.mock_parent.status_bar = self.mock_status_bar
        
        # Create feedback manager
        self.feedback_manager = FeedbackManager(self.mock_parent)
        
        # Mock notification manager
        self.feedback_manager.notification_manager = MagicMock()
        
        # Mock status_changed signal
        self.feedback_manager.status_changed = MagicMock()
    
    def test_show_status_message(self):
        """Test showing a status message."""
        # Show status message
        self.feedback_manager.show_status_message("Test message")
        
        # Check status bar update
        self.mock_status_bar.showMessage.assert_called_once_with("Test message")
        
        # Check signal emission
        self.feedback_manager.status_changed.emit.assert_called_once_with("Test message")
    
    def test_show_temporary_status_message(self):
        """Test showing a temporary status message."""
        # Mock QTimer
        with patch.object(QTimer, 'start') as mock_timer_start:
            # Show temporary status message
            self.feedback_manager.show_status_message("Test message", timeout=1000)
            
            # Check timer start
            mock_timer_start.assert_called_once_with(1000)
    
    def test_set_default_status(self):
        """Test setting the default status message."""
        # Set default status
        self.feedback_manager.set_default_status("Default message")
        
        # Check default status update
        self.assertEqual(self.feedback_manager.default_status, "Default message")
        
        # Check status bar update
        self.mock_status_bar.showMessage.assert_called_once_with("Default message")
        
        # Check signal emission
        self.feedback_manager.status_changed.emit.assert_called_once_with("Default message")
    
    @patch('mcp_agent.ui.components.feedback_manager.QProgressBar')
    @patch('mcp_agent.ui.components.feedback_manager.QLabel')
    def test_show_progress_determinate(self, mock_label_class, mock_progress_bar_class):
        """Test showing a determinate progress indicator."""
        # Create mock progress bar
        mock_progress_bar = MagicMock(spec=QProgressBar)
        mock_progress_bar_class.return_value = mock_progress_bar
        
        # Create mock label
        mock_label = MagicMock(spec=QLabel)
        mock_label_class.return_value = mock_label
        
        # Show progress
        result = self.feedback_manager.show_progress(
            "test_op",
            "Test operation",
            progress_type=ProgressType.DETERMINATE,
            initial_value=10,
            maximum=100
        )
        
        # Check result
        self.assertEqual(result, mock_progress_bar)
        
        # Check progress bar configuration
        mock_progress_bar.setRange.assert_called_once_with(0, 100)
        mock_progress_bar.setValue.assert_called_once_with(10)
        
        # Check status bar update
        self.mock_status_bar.addPermanentWidget.assert_any_call(mock_label)
        self.mock_status_bar.addPermanentWidget.assert_any_call(mock_progress_bar)
        
        # Check active progress bars update
        self.assertIn("test_op", self.feedback_manager.active_progress_bars)
        self.assertEqual(
            self.feedback_manager.active_progress_bars["test_op"]["progress_bar"],
            mock_progress_bar
        )
        self.assertEqual(
            self.feedback_manager.active_progress_bars["test_op"]["label"],
            mock_label
        )
    
    @patch('mcp_agent.ui.components.feedback_manager.QProgressBar')
    @patch('mcp_agent.ui.components.feedback_manager.QLabel')
    def test_show_progress_indeterminate(self, mock_label_class, mock_progress_bar_class):
        """Test showing an indeterminate progress indicator."""
        # Create mock progress bar
        mock_progress_bar = MagicMock(spec=QProgressBar)
        mock_progress_bar_class.return_value = mock_progress_bar
        
        # Create mock label
        mock_label = MagicMock(spec=QLabel)
        mock_label_class.return_value = mock_label
        
        # Show progress
        result = self.feedback_manager.show_progress(
            "test_op",
            "Test operation",
            progress_type=ProgressType.INDETERMINATE
        )
        
        # Check result
        self.assertEqual(result, mock_progress_bar)
        
        # Check progress bar configuration
        mock_progress_bar.setRange.assert_called_once_with(0, 0)
        
        # Check status bar update
        self.mock_status_bar.addPermanentWidget.assert_any_call(mock_label)
        self.mock_status_bar.addPermanentWidget.assert_any_call(mock_progress_bar)
    
    def test_update_progress(self):
        """Test updating a progress indicator."""
        # Create mock progress bar and label
        mock_progress_bar = MagicMock(spec=QProgressBar)
        mock_label = MagicMock(spec=QLabel)
        
        # Add to active progress bars
        self.feedback_manager.active_progress_bars["test_op"] = {
            "progress_bar": mock_progress_bar,
            "label": mock_label
        }
        
        # Update progress
        self.feedback_manager.update_progress("test_op", 50, "Updated message")
        
        # Check progress bar update
        mock_progress_bar.setValue.assert_called_once_with(50)
        
        # Check label update
        mock_label.setText.assert_called_once_with("Updated message")
    
    def test_hide_progress(self):
        """Test hiding a progress indicator."""
        # Create mock progress bar and label
        mock_progress_bar = MagicMock(spec=QProgressBar)
        mock_label = MagicMock(spec=QLabel)
        
        # Add to active progress bars
        self.feedback_manager.active_progress_bars["test_op"] = {
            "progress_bar": mock_progress_bar,
            "label": mock_label
        }
        
        # Hide progress
        self.feedback_manager.hide_progress("test_op")
        
        # Check status bar update
        self.mock_status_bar.removeWidget.assert_any_call(mock_progress_bar)
        self.mock_status_bar.removeWidget.assert_any_call(mock_label)
        
        # Check widget cleanup
        mock_progress_bar.deleteLater.assert_called_once()
        mock_label.deleteLater.assert_called_once()
        
        # Check active progress bars update
        self.assertNotIn("test_op", self.feedback_manager.active_progress_bars)
    
    def test_show_notification(self):
        """Test showing a notification."""
        # Show notification
        self.feedback_manager.show_notification(
            "Test notification",
            notification_type=NotificationType.INFO,
            duration=3000,
            action_text="Action",
            action_callback=lambda: None
        )
        
        # Check notification manager call
        self.feedback_manager.notification_manager.show_notification.assert_called_once_with(
            "Test notification",
            NotificationType.INFO,
            3000,
            "Action",
            lambda: None
        )
    
    def test_clear_all_notifications(self):
        """Test clearing all notifications."""
        # Clear notifications
        self.feedback_manager.clear_all_notifications()
        
        # Check notification manager call
        self.feedback_manager.notification_manager.clear_all.assert_called_once()
    
    def test_clear_all_progress(self):
        """Test clearing all progress indicators."""
        # Create mock progress bars and labels
        mock_progress_bar1 = MagicMock(spec=QProgressBar)
        mock_label1 = MagicMock(spec=QLabel)
        mock_progress_bar2 = MagicMock(spec=QProgressBar)
        mock_label2 = MagicMock(spec=QLabel)
        
        # Add to active progress bars
        self.feedback_manager.active_progress_bars["op1"] = {
            "progress_bar": mock_progress_bar1,
            "label": mock_label1
        }
        self.feedback_manager.active_progress_bars["op2"] = {
            "progress_bar": mock_progress_bar2,
            "label": mock_label2
        }
        
        # Clear progress
        self.feedback_manager.clear_all_progress()
        
        # Check status bar update
        self.mock_status_bar.removeWidget.assert_any_call(mock_progress_bar1)
        self.mock_status_bar.removeWidget.assert_any_call(mock_label1)
        self.mock_status_bar.removeWidget.assert_any_call(mock_progress_bar2)
        self.mock_status_bar.removeWidget.assert_any_call(mock_label2)
        
        # Check widget cleanup
        mock_progress_bar1.deleteLater.assert_called_once()
        mock_label1.deleteLater.assert_called_once()
        mock_progress_bar2.deleteLater.assert_called_once()
        mock_label2.deleteLater.assert_called_once()
        
        # Check active progress bars update
        self.assertEqual(len(self.feedback_manager.active_progress_bars), 0)


if __name__ == '__main__':
    unittest.main() 
   def test_start_operation(self):
        """Test starting an operation."""
        # Mock signals
        self.feedback_manager.operation_started = MagicMock()
        
        # Mock show_progress
        with patch.object(self.feedback_manager, 'show_progress') as mock_show_progress:
            # Start operation
            operation_id = self.feedback_manager.start_operation(
                "Test operation",
                show_progress=True,
                progress_type=ProgressType.INDETERMINATE
            )
            
            # Check operation ID
            self.assertIsNotNone(operation_id)
            
            # Check status message
            self.mock_status_bar.showMessage.assert_called_once_with("Test operation")
            
            # Check progress indicator
            mock_show_progress.assert_called_once_with(
                operation_id,
                "Test operation",
                ProgressType.INDETERMINATE
            )
            
            # Check signal emission
            self.feedback_manager.operation_started.emit.assert_called_once_with(
                operation_id,
                "Test operation"
            )
    
    def test_update_operation(self):
        """Test updating an operation."""
        # Create mock progress bar and label
        mock_progress_bar = MagicMock(spec=QProgressBar)
        mock_label = MagicMock(spec=QLabel)
        
        # Add to active progress bars
        operation_id = "test_op"
        self.feedback_manager.active_progress_bars[operation_id] = {
            "progress_bar": mock_progress_bar,
            "label": mock_label,
            "type": ProgressType.DETERMINATE
        }
        
        # Update operation
        self.feedback_manager.update_operation(
            operation_id,
            progress=50,
            message="Updated message"
        )
        
        # Check status message
        self.mock_status_bar.showMessage.assert_called_once_with("Updated message")
        
        # Check progress bar update
        mock_progress_bar.setValue.assert_called_once_with(50)
        
        # Check label update
        mock_label.setText.assert_called_once_with("Updated message")
    
    def test_complete_operation(self):
        """Test completing an operation."""
        # Mock signals
        self.feedback_manager.operation_completed = MagicMock()
        
        # Create mock progress bar and label
        mock_progress_bar = MagicMock(spec=QProgressBar)
        mock_label = MagicMock(spec=QLabel)
        
        # Add to active progress bars
        operation_id = "test_op"
        self.feedback_manager.active_progress_bars[operation_id] = {
            "progress_bar": mock_progress_bar,
            "label": mock_label,
            "type": ProgressType.DETERMINATE
        }
        
        # Mock hide_progress
        with patch.object(self.feedback_manager, 'hide_progress') as mock_hide_progress:
            # Mock show_notification
            with patch.object(self.feedback_manager, 'show_notification') as mock_show_notification:
                # Complete operation
                self.feedback_manager.complete_operation(
                    operation_id,
                    success=True,
                    message="Operation completed",
                    notification=True,
                    notification_duration=3000
                )
                
                # Check hide progress
                mock_hide_progress.assert_called_once_with(operation_id)
                
                # Check status message
                self.mock_status_bar.showMessage.assert_called_once_with("Operation completed", timeout=5000)
                
                # Check notification
                mock_show_notification.assert_called_once_with(
                    "Operation completed",
                    NotificationType.SUCCESS,
                    3000
                )
                
                # Check signal emission
                self.feedback_manager.operation_completed.emit.assert_called_once_with(
                    operation_id,
                    True
                )
    
    def test_run_async_operation(self):
        """Test running an asynchronous operation."""
        # Mock start_operation
        with patch.object(self.feedback_manager, 'start_operation') as mock_start_operation:
            # Mock operation ID
            mock_start_operation.return_value = "test_op"
            
            # Create mock async function
            mock_async_function = MagicMock()
            
            # Create mock callbacks
            mock_on_complete = MagicMock()
            mock_on_error = MagicMock()
            
            # Run async operation
            operation_id = self.feedback_manager.run_async_operation(
                "Test operation",
                mock_async_function,
                on_complete=mock_on_complete,
                on_error=mock_on_error,
                show_progress=True,
                progress_type=ProgressType.INDETERMINATE,
                show_notification=True
            )
            
            # Check operation ID
            self.assertEqual(operation_id, "test_op")
            
            # Check start_operation call
            mock_start_operation.assert_called_once_with(
                "Test operation",
                True,
                ProgressType.INDETERMINATE
            )
            
            # Get completion handler
            completion_handler = mock_start_operation.call_args[0][0]
            
            # Test completion handler with mock complete_operation
            with patch.object(self.feedback_manager, 'complete_operation') as mock_complete_operation:
                # Call completion handler
                result = "test_result"
                self.feedback_manager.run_async_operation.__closure__[0].cell_contents(result)
                
                # Check complete_operation call
                mock_complete_operation.assert_called_once()
                
                # Check on_complete callback
                mock_on_complete.assert_called_once_with(result)