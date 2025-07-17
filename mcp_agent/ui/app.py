"""
Main application entry point for the MCP Agent GUI.

This module provides the main application class and entry point for the GUI.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from mcp_agent.ui.controllers.ui_controller import UIController
from mcp_agent.config.manager import ConfigManager

class MCPAgentApp:
    """Main application class for the MCP Agent GUI."""
    
    def __init__(self, args=None):
        """Initialize the application.
        
        Args:
            args (argparse.Namespace, optional): Command line arguments.
        """
        # Store command line arguments
        self.args = args or {}
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("MCP Agent")
        
        # Set application style
        self.app.setStyle("Fusion")
        
        # Create UI controller with config path from args
        config_path = getattr(self.args, 'config', None)
        self.controller = UIController(config_path)
        
    def run(self):
        """Run the application.
        
        Returns:
            int: Application exit code.
        """
        try:
            # Initialize the controller
            self.controller.initialize()
            
            # Run the application event loop
            return self.app.exec()
            
        except Exception as e:
            logging.error(f"Error running GUI application: {e}")
            self._show_error_dialog(f"Failed to start application: {e}")
            return 1
            
    def _show_error_dialog(self, message):
        """Show an error dialog with the given message.
        
        Args:
            message (str): The error message to display.
        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(message)
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()

def main():
    """Entry point for the GUI application."""
    app = MCPAgentApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()