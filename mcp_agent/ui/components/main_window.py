"""
Main Window component for MCP Agent.

This module provides the main window for the MCP Agent GUI.
"""

from PyQt6.QtWidgets import QMainWindow, QSplitter, QStatusBar, QMenuBar, QMenu, QDialog, QProgressBar, QLabel
from PyQt6.QtCore import Qt, QSize, QPoint, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QAction
from mcp_agent.ui.components.chat_panel import ChatPanel
from mcp_agent.ui.components.tools_panel import ToolsPanel
from mcp_agent.ui.components.notification import NotificationManager, NotificationType
from mcp_agent.ui.components.feedback_manager import FeedbackManager, ProgressType
from mcp_agent.ui.models.ui_config import UIConfig

class MainWindow(QMainWindow):
    """Main window for the MCP Agent GUI."""
    
    # Signal emitted when window state changes
    window_state_changed = pyqtSignal(tuple, tuple)
    
    def __init__(self, controller):
        """Initialize the main window.
        
        Args:
            controller: The UI controller.
        """
        super().__init__()
        self.controller = controller
        self.chat_panel = None
        self.tools_panel = None
        self.ui_config = None
        
        # Load UI configuration
        self.load_ui_config()
        
        # Initialize UI components
        self.init_ui()
        
        # Restore window state
        self.restore_window_state()
        
        # Initialize feedback controller
        if hasattr(self.controller, 'feedback_controller'):
            self.controller.feedback_controller.initialize(self)
        
    def load_ui_config(self):
        """Load UI configuration from settings."""
        try:
            self.ui_config = self.controller.settings_controller.config_manager.get_ui_config()
        except Exception as e:
            print(f"Error loading UI configuration: {e}")
            self.ui_config = UIConfig()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("MCP Agent")
        self.setMinimumSize(800, 600)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add permanent status widgets
        self.connection_status_label = QLabel("Not connected")
        self.status_bar.addPermanentWidget(self.connection_status_label)
        
        # Show or hide status bar based on configuration
        self.status_bar.setVisible(self.ui_config.show_status_bar)
        
        # Create main layout
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)
        
        # Create panels
        self.chat_panel = ChatPanel(self.controller)
        self.tools_panel = ToolsPanel(self.controller)
        
        # Set tools panel reference in controller
        self.controller.set_tools_panel(self.tools_panel)
        
        # Add panels to splitter
        self.splitter.addWidget(self.chat_panel)
        self.splitter.addWidget(self.tools_panel)
        
        # Show or hide tool panel based on configuration
        self.tools_panel.setVisible(self.ui_config.show_tool_panel)
        
        # Set initial splitter sizes
        if self.ui_config.show_tool_panel:
            self.splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
        else:
            self.splitter.setSizes([self.width(), 0])
        
    def create_menu_bar(self):
        """Create the menu bar."""
        menu_bar = QMenuBar()
        
        # File menu
        file_menu = QMenu("&File", self)
        export_action = QAction("&Export Conversation", self)
        export_action.triggered.connect(self.export_conversation)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = QMenu("&Edit", self)
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = QMenu("&View", self)
        toggle_tools_action = QAction("&Tools Panel", self)
        toggle_tools_action.setCheckable(True)
        toggle_tools_action.setChecked(self.ui_config.show_tool_panel)
        toggle_tools_action.triggered.connect(self.toggle_tools_panel)
        view_menu.addAction(toggle_tools_action)
        
        toggle_status_action = QAction("&Status Bar", self)
        toggle_status_action.setCheckable(True)
        toggle_status_action.setChecked(self.ui_config.show_status_bar)
        toggle_status_action.triggered.connect(self.toggle_status_bar)
        view_menu.addAction(toggle_status_action)
        
        # Tools menu
        tools_menu = QMenu("&Tools", self)
        
        # Help menu
        help_menu = QMenu("&Help", self)
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Add menus to menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(view_menu)
        menu_bar.addMenu(tools_menu)
        menu_bar.addMenu(help_menu)
        
        self.setMenuBar(menu_bar)
    
    def restore_window_state(self):
        """Restore window size and position from configuration."""
        if self.ui_config.window_size:
            self.resize(QSize(*self.ui_config.window_size))
        
        if self.ui_config.window_position:
            self.move(QPoint(*self.ui_config.window_position))
    
    def save_window_state(self):
        """Save window size and position to configuration."""
        # Update UI config with current window state
        self.ui_config.window_size = (self.width(), self.height())
        self.ui_config.window_position = (self.x(), self.y())
        self.ui_config.show_tool_panel = self.tools_panel.isVisible()
        self.ui_config.show_status_bar = self.status_bar.isVisible()
        
        # Save UI config
        try:
            self.controller.settings_controller.config_manager.save_ui_config(self.ui_config)
        except Exception as e:
            print(f"Error saving window state: {e}")
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event.
        
        Args:
            event: The close event.
        """
        # Save window state before closing
        self.save_window_state()
        
        # Accept the event to close the window
        event.accept()
    
    def toggle_tools_panel(self, checked: bool):
        """Toggle the visibility of the tools panel.
        
        Args:
            checked: Whether the panel should be visible.
        """
        self.tools_panel.setVisible(checked)
        self.ui_config.show_tool_panel = checked
        
        # Adjust splitter sizes
        if checked:
            self.splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
        else:
            self.splitter.setSizes([self.width(), 0])
    
    def toggle_status_bar(self, checked: bool):
        """Toggle the visibility of the status bar.
        
        Args:
            checked: Whether the status bar should be visible.
        """
        self.status_bar.setVisible(checked)
        self.ui_config.show_status_bar = checked
        
        # Update feedback manager if available
        if hasattr(self.controller, 'feedback_controller') and self.controller.feedback_controller.feedback_manager:
            if checked:
                self.controller.feedback_controller.feedback_manager.set_status_bar(self.status_bar)
            else:
                self.controller.feedback_controller.feedback_manager.set_status_bar(None)
    
    def show_settings(self):
        """Show the settings dialog."""
        # This will be implemented in task 3.4
        from mcp_agent.ui.components.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.controller, self)
        dialog.exec()
    
    def show_about(self):
        """Show the about dialog."""
        # Simple about dialog implementation
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About MCP Agent",
            "MCP Agent\n\n"
            "A Python application that connects to MCP (Model Context Protocol) servers "
            "with pluggable LLM backends."
        )
    
    def export_conversation(self):
        """Export the current conversation."""
        # This will be implemented in task 7.2
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Conversation",
            "",
            f"JSON Files (*.json);;Text Files (*.txt);;Markdown Files (*.md)"
        )
        
        if file_path:
            QMessageBox.information(
                self,
                "Export Conversation",
                "Conversation export will be implemented in task 7.2."
            )
    
    def update_status(self, message: str):
        """Update the status bar message.
        
        Args:
            message: The message to display.
        """
        self.status_bar.showMessage(message)
        
    def update_connection_status(self, connected: bool, server_name: str = None, model_name: str = None):
        """Update the connection status in the status bar.
        
        Args:
            connected: Whether the agent is connected.
            server_name: Name of the connected server.
            model_name: Name of the LLM model.
        """
        if connected:
            status_text = f"Connected to {server_name}"
            if model_name:
                status_text += f" | {model_name}"
        else:
            status_text = "Not connected"
            
        self.connection_status_label.setText(status_text)