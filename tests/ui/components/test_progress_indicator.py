"""
Tests for the progress indicator component.
"""

import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QWidget, QProgressBar, QLabel
from PyQt6.QtCore import QTimer

from mcp_agent.ui.components.progress_indicator import ProgressIndicator, ProgressIndicatorType


class TestProgressIndicator(unittest.TestCase):
    """Test cases for the ProgressIndicator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock parent
        self.mock_parent = MagicMock(spec=QWidget)
        
        # Mock signals
        self.progress_updated_signal = MagicMock()
        self.progress_completed_signal = MagicMock()
    
    def test_init_determinate(self):
        """Test initialization of determinate progress indicator."""
        # Create progress indicator
        with patch('mcp_agent.ui.components.progress_indicator.QProgressBar') as mock_progress_bar_class:
            with patch('mcp_agent.ui.components.progress_indicator.QLabel') as mock_label_class:
                # Create mock progress bar
                mock_progress_bar = MagicMock(spec=QProgressBar)
                mock_progress_bar_class.return_value = mock_progress_bar
                
                # Create mock label
                mock_label = MagicMock(spec=QLabel)
                mock_label_class.return_value = mock_label
                
                # Create progress indicator
                progress_indicator = ProgressIndicator(
                    self.mock_parent,
                    "Test message",
                    ProgressIndicatorType.DETERMINATE,
                    10,
                    100
                )
                
                # Check progress bar configuration
                mock_progress_bar.setRange.assert_called_once_with(0, 100)
                mock_progress_bar.setValue.assert_called_once_with(10)
                
                # Check label configuration
                mock_label.setText.assert_called_once_with("Test message")
    
    def test_init_indeterminate(self):
        """Test initialization of indeterminate progress indicator."""
        # Create progress indicator
        with patch('mcp_agent.ui.components.progress_indicator.QProgressBar') as mock_progress_bar_class:
            with patch('mcp_agent.ui.components.progress_indicator.QLabel') as mock_label_class:
                # Create mock progress bar
                mock_progress_bar = MagicMock(spec=QProgressBar)
                mock_progress_bar_class.return_value = mock_progress_bar
                
                # Create mock label
                mock_label = MagicMock(spec=QLabel)
                mock_label_class.return_value = mock_label
                
                # Create progress indicator
                with patch.object(ProgressIndicator, 'start_pulse') as mock_start_pulse:
                    progress_indicator = ProgressIndicator(
                        self.mock_parent,
                        "Test message",
                        ProgressIndicatorType.INDETERMINATE
                    )
                    
                    # Check progress bar configuration
                    mock_progress_bar.setRange.assert_called_once_with(0, 0)
                    
                    # Check pulse start
                    mock_start_pulse.assert_called_once()
    
    def test_update_progress(self):
        """Test updating progress."""
        # Create progress indicator
        with patch('mcp_agent.ui.components.progress_indicator.QProgressBar') as mock_progress_bar_class:
            with patch('mcp_agent.ui.components.progress_indicator.QLabel') as mock_label_class:
                # Create mock progress bar
                mock_progress_bar = MagicMock(spec=QProgressBar)
                mock_progress_bar_class.return_value = mock_progress_bar
                
                # Create mock label
                mock_label = MagicMock(spec=QLabel)
                mock_label_class.return_value = mock_label
                
                # Create progress indicator
                progress_indicator = ProgressIndicator(
                    self.mock_parent,
                    "Test message",
                    ProgressIndicatorType.DETERMINATE,
                    10,
                    100
                )
                
                # Mock signal
                progress_indicator.progress_updated = MagicMock()
                
                # Update progress
                progress_indicator.update_progress(50, "Updated message")
                
                # Check progress bar update
                mock_progress_bar.setValue.assert_called_with(50)
                
                # Check label update
                mock_label.setText.assert_called_with("Updated message")
                
                # Check signal emission
                progress_indicator.progress_updated.emit.assert_called_once_with(50)
    
    def test_complete(self):
        """Test completing progress."""
        # Create progress indicator
        with patch('mcp_agent.ui.components.progress_indicator.QProgressBar') as mock_progress_bar_class:
            with patch('mcp_agent.ui.components.progress_indicator.QLabel') as mock_label_class:
                # Create mock progress bar
                mock_progress_bar = MagicMock(spec=QProgressBar)
                mock_progress_bar_class.return_value = mock_progress_bar
                
                # Create mock label
                mock_label = MagicMock(spec=QLabel)
                mock_label_class.return_value = mock_label
                
                # Create progress indicator
                progress_indicator = ProgressIndicator(
                    self.mock_parent,
                    "Test message",
                    ProgressIndicatorType.DETERMINATE,
                    10,
                    100
                )
                
                # Mock signals
                progress_indicator.progress_completed = MagicMock()
                
                # Mock stop_pulse
                with patch.object(progress_indicator, 'stop_pulse') as mock_stop_pulse:
                    # Complete progress
                    progress_indicator.complete()
                    
                    # Check progress bar update
                    mock_progress_bar.setValue.assert_called_with(100)
                    
                    # Check pulse stop
                    mock_stop_pulse.assert_called_once()
                    
                    # Check signal emission
                    progress_indicator.progress_completed.emit.assert_called_once()
    
    def test_pulse(self):
        """Test pulsing for indeterminate progress."""
        # Create progress indicator
        with patch('mcp_agent.ui.components.progress_indicator.QProgressBar') as mock_progress_bar_class:
            with patch('mcp_agent.ui.components.progress_indicator.QLabel') as mock_label_class:
                # Create mock progress bar
                mock_progress_bar = MagicMock(spec=QProgressBar)
                mock_progress_bar_class.return_value = mock_progress_bar
                
                # Create mock label
                mock_label = MagicMock(spec=QLabel)
                mock_label_class.return_value = mock_label
                
                # Create progress indicator
                with patch.object(ProgressIndicator, 'start_pulse'):
                    progress_indicator = ProgressIndicator(
                        self.mock_parent,
                        "Test message",
                        ProgressIndicatorType.INDETERMINATE
                    )
                
                # Mock QTimer
                with patch('mcp_agent.ui.components.progress_indicator.QTimer') as mock_timer_class:
                    # Create mock timer
                    mock_timer = MagicMock()
                    mock_timer_class.return_value = mock_timer
                    
                    # Start pulse
                    progress_indicator.start_pulse()
                    
                    # Check timer configuration
                    mock_timer.setInterval.assert_called_once_with(100)
                    mock_timer.start.assert_called_once()
                    
                    # Stop pulse
                    progress_indicator.stop_pulse()
                    
                    # Check timer stop
                    mock_timer.stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()