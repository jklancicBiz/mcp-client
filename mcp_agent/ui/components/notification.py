"""
Notification component for MCP Agent.

This module provides notification functionality for the MCP Agent UI.
"""

import time
from enum import Enum
from typing import Optional, Callable
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QColor, QPalette


class NotificationType(Enum):
    """Enum for notification types."""
    INFO = 0
    SUCCESS = 1
    WARNING = 2
    ERROR = 3


class Notification(QWidget):
    """Notification widget that appears and automatically disappears."""
    
    # Signal emitted when notification is closed
    closed = pyqtSignal()
    
    # Signal emitted when action button is clicked
    action_clicked = pyqtSignal()
    
    def __init__(self, parent: QWidget, message: str, 
                 notification_type: NotificationType = NotificationType.INFO,
                 duration: int = 5000, action_text: Optional[str] = None,
                 action_callback: Optional[Callable] = None):
        """Initialize the notification.
        
        Args:
            parent: Parent widget.
            message: Message to display.
            notification_type: Type of notification.
            duration: Duration in milliseconds before auto-hiding (0 for no auto-hide).
            action_text: Text for action button (None for no button).
            action_callback: Callback for action button.
        """
        super().__init__(parent)
        
        self.parent = parent
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.action_text = action_text
        self.action_callback = action_callback
        
        # Set up UI
        self.setup_ui()
        
        # Set up auto-hide timer if duration > 0
        if duration > 0:
            self.timer = QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.hide_animation)
            self.timer.start(duration)
        
        # Show animation
        self.show_animation()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Set window flags
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set size and position
        self.setFixedWidth(300)
        self.setMinimumHeight(50)
        
        # Create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # Create message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        content_layout.addWidget(self.message_label, 1)
        
        # Create action button if action_text is provided
        if self.action_text:
            self.action_button = QPushButton(self.action_text)
            self.action_button.setFixedHeight(30)
            self.action_button.clicked.connect(self._on_action_clicked)
            content_layout.addWidget(self.action_button)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        # Set style based on notification type
        self._set_style()
    
    def _set_style(self):
        """Set the style based on notification type."""
        base_style = """
            QWidget {
                border-radius: 5px;
                padding: 5px;
            }
        """
        
        if self.notification_type == NotificationType.INFO:
            self.setStyleSheet(base_style + """
                QWidget {
                    background-color: #2196F3;
                    color: white;
                }
                QPushButton {
                    background-color: #0D47A1;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
            """)
        elif self.notification_type == NotificationType.SUCCESS:
            self.setStyleSheet(base_style + """
                QWidget {
                    background-color: #4CAF50;
                    color: white;
                }
                QPushButton {
                    background-color: #2E7D32;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
            """)
        elif self.notification_type == NotificationType.WARNING:
            self.setStyleSheet(base_style + """
                QWidget {
                    background-color: #FF9800;
                    color: white;
                }
                QPushButton {
                    background-color: #E65100;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
        elif self.notification_type == NotificationType.ERROR:
            self.setStyleSheet(base_style + """
                QWidget {
                    background-color: #F44336;
                    color: white;
                }
                QPushButton {
                    background-color: #B71C1C;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #C62828;
                }
            """)
    
    def show_animation(self):
        """Show the notification with animation."""
        # Calculate position (top-right corner of parent)
        parent_rect = self.parent.rect()
        self.setGeometry(
            parent_rect.width() - self.width() - 20,
            -self.height(),
            self.width(),
            self.height()
        )
        
        # Show the widget
        self.show()
        
        # Create animation
        self.show_anim = QPropertyAnimation(self, b"geometry")
        self.show_anim.setDuration(300)
        self.show_anim.setStartValue(self.geometry())
        self.show_anim.setEndValue(QRect(
            parent_rect.width() - self.width() - 20,
            20,
            self.width(),
            self.height()
        ))
        self.show_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.show_anim.start()
    
    def hide_animation(self):
        """Hide the notification with animation."""
        # Create animation
        self.hide_anim = QPropertyAnimation(self, b"geometry")
        self.hide_anim.setDuration(300)
        self.hide_anim.setStartValue(self.geometry())
        self.hide_anim.setEndValue(QRect(
            self.parent.width() - self.width() - 20,
            -self.height(),
            self.width(),
            self.height()
        ))
        self.hide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.hide_anim.finished.connect(self._on_hide_finished)
        self.hide_anim.start()
    
    def _on_hide_finished(self):
        """Handle hide animation finished."""
        self.hide()
        self.closed.emit()
        self.deleteLater()
    
    def _on_action_clicked(self):
        """Handle action button click."""
        if self.action_callback:
            self.action_callback()
        self.action_clicked.emit()
        self.hide_animation()


class NotificationManager:
    """Manager for showing notifications."""
    
    def __init__(self, parent: QWidget):
        """Initialize the notification manager.
        
        Args:
            parent: Parent widget for notifications.
        """
        self.parent = parent
        self.active_notifications = []
    
    def show_notification(self, message: str, 
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5000, action_text: Optional[str] = None,
                         action_callback: Optional[Callable] = None) -> Notification:
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
        # Create notification
        notification = Notification(
            self.parent,
            message,
            notification_type,
            duration,
            action_text,
            action_callback
        )
        
        # Connect closed signal
        notification.closed.connect(lambda: self._on_notification_closed(notification))
        
        # Add to active notifications
        self.active_notifications.append(notification)
        
        return notification
    
    def _on_notification_closed(self, notification: Notification):
        """Handle notification closed.
        
        Args:
            notification: The notification that was closed.
        """
        if notification in self.active_notifications:
            self.active_notifications.remove(notification)
    
    def clear_all(self):
        """Clear all active notifications."""
        for notification in list(self.active_notifications):
            notification.hide_animation()