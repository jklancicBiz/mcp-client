"""
Settings Controller for MCP Agent.

This module provides the controller for managing application settings.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from mcp_agent.config.manager import ConfigManager

class SettingsController(QObject):
    """Controller for managing application settings."""
    
    settings_loaded = pyqtSignal(dict)
    settings_saved = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config_path=None):
        """Initialize the settings controller.
        
        Args:
            config_path (str, optional): Path to the configuration file.
        """
        super().__init__()
        self.config_manager = ConfigManager(config_path)
        self.config = {}
        
    def load_config(self):
        """Load configuration from file."""
        try:
            self.config = self.config_manager.load_config()
            self.settings_loaded.emit(self.config)
        except Exception as e:
            self.error_occurred.emit(f"Error loading configuration: {str(e)}")
            
    def save_config(self, config):
        """Save configuration to file.
        
        Args:
            config (dict): The configuration to save.
        """
        try:
            self.config_manager.save_config(config)
            self.config = config
            self.settings_saved.emit()
        except Exception as e:
            self.error_occurred.emit(f"Error saving configuration: {str(e)}")
            
    def apply_settings(self, settings):
        """Apply settings to agent.
        
        Args:
            settings (dict): The settings to apply.
        """
        # This is a placeholder. Actual implementation will depend on
        # how settings are applied in the CLI version.
        pass