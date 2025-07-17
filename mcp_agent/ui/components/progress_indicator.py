"""
Progress indicator component for MCP Agent.

This module provides progress indicator functionality for the MCP Agent UI.
"""

from enum import Enum
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QProgressBar, QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal


class ProgressIndicatorType(Enum):
    """Enum for progress indicator types."""
    DETERMINATE = 0  # Progress with known percentage
    INDETERMINATE = 1  # Progress with unknown percentage (activity indicator)


class ProgressIndicator(QWidget):
    """Progress indicator widget for long operations."""
    
    # Signal emitted when progress is updated
    progress_updated = pyqtSignal(int)
    
    # Signal emitted when progress is completed
    progress_completed = pyqtSignal()
    
    def __init__(self, parent: QWidget, message: str, 
                 indicator_type: ProgressIndicatorType = ProgressIndicatorType.INDETERMINATE,
                 initial_value: int = 0, maximum: int = 100):
        """Initialize the progress indicator.
        
        Args:
            parent: Parent widget.
            message: Message to display.
            indicator_type: Type of progress indicator.
            initial_value: Initial progress value (for determinate progress).
            maximum: Maximum progress value (for determinate progress).
        """
        super().__init__(parent)
        
        self.parent = parent
        self.message = message
        self.indicator_type = indicator_type
        self.initial_value = initial_value
        self.maximum = maximum
        self.pulse_timer = None
        
        # Set up UI
        self.setup_ui()
        
        # Start pulsing for indeterminate progress
        if self.indicator_type == ProgressIndicatorType.INDETERMINATE:
            self.start_pulse()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create message label
        self.message_label = QLabel(self.message)
        layout.addWidget(self.message_label)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setMaximumHeight(15)
        
        if self.indicator_type == ProgressIndicatorType.INDETERMINATE:
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
        else:
            self.progress_bar.setRange(0, self.maximum)
            self.progress_bar.setValue(self.initial_value)
        
        layout.addWidget(self.progress_bar)
        
        # Set size policy
        self.setSizePolicy(
            QWidget.SizePolicy.Preferred,
            QWidget.SizePolicy.Fixed
        )
    
    def update_progress(self, value: int, message: Optional[str] = None):
        """Update the progress value and optionally the message.
        
        Args:
            value: New progress value.
            message: Optional new message to display.
        """
        if self.indicator_type == ProgressIndicatorType.DETERMINATE:
            self.progress_bar.setValue(value)
        
        if message is not None:
            self.message_label.setText(message)
        
        # Emit signal
        self.progress_updated.emit(value)
    
    def complete(self):
        """Mark the progress as complete."""
        if self.indicator_type == ProgressIndicatorType.DETERMINATE:
            self.progress_bar.setValue(self.maximum)
        
        # Stop pulsing
        self.stop_pulse()
        
        # Emit signal
        self.progress_completed.emit()
    
    def start_pulse(self):
        """Start pulsing the progress bar for indeterminate progress."""
        if self.indicator_type != ProgressIndicatorType.INDETERMINATE:
            return
        
        # Create timer for pulsing
        self.pulse_timer = QTimer(self)
        self.pulse_timer.setInterval(100)
        self.pulse_timer.timeout.connect(self._pulse)
        self.pulse_timer.start()
    
    def stop_pulse(self):
        """Stop pulsing the progress bar."""
        if self.pulse_timer and self.pulse_timer.isActive():
            self.pulse_timer.stop()
    
    def _pulse(self):
        """Update the progress bar to create a pulse effect."""
        # For indeterminate progress bars, we don't need to do anything
        # as Qt handles the animation automatically
        pass