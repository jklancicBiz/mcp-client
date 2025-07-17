"""
UI Controller for MCP Agent.

This module provides the main controller for the MCP Agent GUI.
"""

import asyncio
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from mcp_agent.ui.controllers.agent_controller import AgentController
from mcp_agent.ui.controllers.settings_controller import SettingsController
from mcp_agent.ui.error_handler import ErrorHandler, ErrorSeverity
from mcp_agent.core.exceptions import MCPError, MCPConnectionError, MCPToolError

class UIController(QObject):
    """Main controller for the MCP Agent GUI."""
    
    # Signal emitted when an error occurs
    error_occurred = pyqtSignal(str, int)  # message, severity
    
    def __init__(self, config_path=None):
        """Initialize the UI controller.
        
        Args:
            config_path (str, optional): Path to the configuration file.
        """
        super().__init__()
        self.agent_controller = AgentController()
        self.settings_controller = SettingsController(config_path)
        self.main_window = None  # Will be initialized later
        self.tools_panel = None  # Will be set by MainWindow
        self.error_handler = ErrorHandler()
        
        # Connect error signals
        self.error_handler.error_occurred.connect(self.on_error_occurred)
        
    def initialize(self):
        """Initialize the application components."""
        # Import here to avoid circular imports
        from mcp_agent.ui.components.main_window import MainWindow
        
        # Initialize controllers
        self.settings_controller.load_config()
        
        # Initialize main window
        self.main_window = MainWindow(self)
        
        # Connect signals for tools panel
        self.connect_tools_panel_signals()
        
        # Show the main window
        self.main_window.show()
        
        # Initialize agent with current configuration
        asyncio.create_task(self.initialize_agent())
        
    def connect_tools_panel_signals(self):
        """Connect signals for the tools panel."""
        if not self.tools_panel:
            logging.warning("Tools panel not set, cannot connect signals")
            return
            
        # Connect agent controller signals to tools panel
        self.agent_controller.tools_updated.connect(self.tools_panel.update_tools)
        self.agent_controller.resources_updated.connect(self.tools_panel.update_resources)
        self.agent_controller.connection_status_changed.connect(self.tools_panel.update_connection_status)
        
        # Connect tools panel signals to agent controller
        self.tools_panel.tool_selected.connect(self.on_tool_selected)
        
    def set_tools_panel(self, tools_panel):
        """Set the tools panel reference and connect signals.
        
        Args:
            tools_panel: The tools panel instance.
        """
        self.tools_panel = tools_panel
        self.connect_tools_panel_signals()
        
    def on_error_occurred(self, message, severity):
        """Handle error signal from error handler.
        
        Args:
            message (str): The error message.
            severity (int): The severity level of the error.
        """
        # Forward the error signal
        self.error_occurred.emit(message, severity)
        
        # Update status bar if main window exists
        if self.main_window:
            self.main_window.update_status(f"Error: {message}")
            
    async def initialize_agent(self):
        """Initialize the agent with the current configuration."""
        try:
            config = self.settings_controller.get_active_config()
            if not config:
                self.error_handler.show_error_message(
                    "No active configuration found. Please check your settings.",
                    ErrorSeverity.WARNING,
                    show_dialog=True,
                    parent=self.main_window
                )
                if self.main_window:
                    self.main_window.update_status("No active configuration")
                return
                
            success = await self.agent_controller.initialize_agent(config)
            if success and self.main_window:
                self.main_window.update_status(f"Connected to {config.get('server', {}).get('name', 'Unknown')}")
            elif self.main_window:
                self.main_window.update_status("Failed to connect to MCP server")
        except Exception as e:
            self.error_handler.handle_exception(
                e,
                context="Failed to initialize agent",
                severity=ErrorSeverity.ERROR,
                show_dialog=True,
                parent=self.main_window
            )
        
    async def handle_message(self, message):
        """Process user message and update UI.
        
        Args:
            message (str): The user message to process.
            
        Returns:
            str: The assistant's response.
        """
        if self.main_window:
            self.main_window.update_status("Processing message...")
            
        try:
            response = await self.agent_controller.process_message(message)
            
            if self.main_window:
                self.main_window.update_status("Ready")
                
            return response
        except Exception as e:
            error_message = self.error_handler.handle_exception(
                e,
                context="Error processing message",
                severity=ErrorSeverity.ERROR,
                show_dialog=False,
                parent=self.main_window
            )
            
            if self.main_window:
                self.main_window.update_status("Ready")
                
            # Return error message as response so it appears in the chat
            return f"Error: {error_message}"
    
    def on_tool_selected(self, tool_name):
        """Handle tool selection from the tools panel.
        
        Args:
            tool_name (str): The name of the selected tool.
        """
        # This could be used to insert tool usage into the chat input
        # or to show additional information about the tool
        logging.info(f"Tool selected: {tool_name}")
        
    async def refresh_tools_and_resources(self):
        """Refresh the tools and resources from the MCP server."""
        if self.main_window:
            self.main_window.update_status("Refreshing tools and resources...")
            
        try:
            await self.agent_controller.refresh_tools_and_resources()
            
            if self.main_window:
                self.main_window.update_status("Ready")
        except Exception as e:
            self.error_handler.handle_exception(
                e,
                context="Failed to refresh tools and resources",
                severity=ErrorSeverity.WARNING,
                show_dialog=True,
                parent=self.main_window
            )
            
            if self.main_window:
                self.main_window.update_status("Ready")