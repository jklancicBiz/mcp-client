"""
Tests for the SettingsDialog component.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtTest import QTest

# Import the SettingsDialog class
from mcp_agent.ui.components.settings_dialog import SettingsDialog
from mcp_agent.ui.models.ui_config import UIConfig

# Create a QApplication instance for testing
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

class TestSettingsDialog(unittest.TestCase):
    """Test cases for the SettingsDialog class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create the settings dialog
        self.dialog = SettingsDialog()
        
        # Create a sample configuration
        self.sample_config = {
            "ui": {
                "theme": "dark",
                "font_size": 12,
                "high_dpi_scaling": True,
                "show_tool_panel": True,
                "show_status_bar": True,
                "conversation_history_limit": 50,
                "default_export_format": "json"
            },
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": "test-api-key",
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "mcp_servers": {
                "filesystem": {
                    "command": ["python", "-m", "mcp_server_filesystem"],
                    "args": ["--path", "."],
                    "autoApprove": ["list_files", "read_file"],
                    "disabled": False
                },
                "git": {
                    "command": ["python", "-m", "mcp_server_git"],
                    "args": [],
                    "autoApprove": [],
                    "disabled": True
                }
            },
            "default_server": "filesystem"
        }
        
        # Load the sample configuration
        self.dialog.load_settings(self.sample_config)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Close the dialog
        self.dialog.close()
    
    def test_init(self):
        """Test that the dialog initializes correctly."""
        # Check that the dialog has the correct title
        self.assertEqual(self.dialog.windowTitle(), "Settings")
        
        # Check that the dialog has the correct minimum size
        self.assertEqual(self.dialog.minimumSize(), QSize(600, 500))
        
        # Check that the dialog has a tab widget
        self.assertIsNotNone(self.dialog.tab_widget)
        
        # Check that the dialog has three tabs
        self.assertEqual(self.dialog.tab_widget.count(), 3)
        self.assertEqual(self.dialog.tab_widget.tabText(0), "General")
        self.assertEqual(self.dialog.tab_widget.tabText(1), "LLM")
        self.assertEqual(self.dialog.tab_widget.tabText(2), "MCP Servers")
    
    def test_load_settings_general(self):
        """Test that general settings are loaded correctly."""
        # Check theme
        self.assertEqual(self.dialog.theme_combo.currentText(), "Dark")
        
        # Check font size
        self.assertEqual(self.dialog.font_size_combo.currentText(), "Medium")
        
        # Check high DPI scaling
        self.assertTrue(self.dialog.high_dpi_check.isChecked())
        
        # Check panel visibility
        self.assertTrue(self.dialog.tool_panel_check.isChecked())
        self.assertTrue(self.dialog.status_bar_check.isChecked())
        
        # Check conversation settings
        self.assertEqual(self.dialog.history_limit_spin.value(), 50)
        self.assertEqual(self.dialog.export_format_combo.currentText(), "JSON")
    
    def test_load_settings_llm(self):
        """Test that LLM settings are loaded correctly."""
        # Check provider
        self.assertEqual(self.dialog.provider_combo.currentText(), "OpenAI")
        
        # Check model
        self.assertEqual(self.dialog.model_combo.currentText(), "gpt-4")
        
        # Check API key
        self.assertEqual(self.dialog.api_key_edit.text(), "test-api-key")
        
        # Check advanced settings
        self.assertEqual(self.dialog.temperature_spin.value(), 70)  # 0.7 * 100
        self.assertEqual(self.dialog.max_tokens_spin.value(), 4000)
    
    def test_load_settings_servers(self):
        """Test that server settings are loaded correctly."""
        # Check server list
        self.assertEqual(self.dialog.server_list.count(), 2)
        
        # Check default server
        self.assertEqual(self.dialog.server_list.item(0).text(), "filesystem (Default)")
        
        # Check that the second server is not the default
        self.assertEqual(self.dialog.server_list.item(1).text(), "git")
    
    def test_update_model_options(self):
        """Test that model options are updated when the provider changes."""
        # Check initial model options for OpenAI
        self.assertEqual(self.dialog.model_combo.count(), 3)
        self.assertEqual(self.dialog.model_combo.itemText(0), "gpt-4")
        self.assertEqual(self.dialog.model_combo.itemText(1), "gpt-4-turbo")
        self.assertEqual(self.dialog.model_combo.itemText(2), "gpt-3.5-turbo")
        
        # Change provider to Anthropic
        self.dialog.provider_combo.setCurrentText("Anthropic")
        
        # Check updated model options
        self.assertEqual(self.dialog.model_combo.count(), 3)
        self.assertEqual(self.dialog.model_combo.itemText(0), "claude-3-opus-20240229")
        self.assertEqual(self.dialog.model_combo.itemText(1), "claude-3-sonnet-20240229")
        self.assertEqual(self.dialog.model_combo.itemText(2), "claude-3-haiku-20240307")
    
    def test_toggle_api_key_input(self):
        """Test that API key input is toggled correctly."""
        # Check initial state
        self.assertTrue(self.dialog.api_key_edit.isEnabled())
        self.assertFalse(self.dialog.api_key_env_edit.isEnabled())
        
        # Toggle to use environment variable
        self.dialog.api_key_env_check.setChecked(True)
        
        # Check updated state
        self.assertFalse(self.dialog.api_key_edit.isEnabled())
        self.assertTrue(self.dialog.api_key_env_edit.isEnabled())
        
        # Toggle back to use direct API key
        self.dialog.api_key_env_check.setChecked(False)
        
        # Check updated state
        self.assertTrue(self.dialog.api_key_edit.isEnabled())
        self.assertFalse(self.dialog.api_key_env_edit.isEnabled())
    
    def test_update_api_key_env_var(self):
        """Test that API key environment variable placeholder is updated."""
        # Check initial placeholder for OpenAI
        self.assertEqual(self.dialog.api_key_env_edit.placeholderText(), "OPENAI_API_KEY")
        
        # Change provider to Anthropic
        self.dialog.provider_combo.setCurrentText("Anthropic")
        
        # Check updated placeholder
        self.assertEqual(self.dialog.api_key_env_edit.placeholderText(), "ANTHROPIC_API_KEY")
    
    def test_validate_settings_valid(self):
        """Test validation with valid settings."""
        # Set valid settings
        self.dialog.api_key_edit.setText("valid-api-key")
        
        # Validate
        self.assertTrue(self.dialog.validate_settings())
        self.assertEqual(len(self.dialog.validation_errors), 0)
    
    def test_validate_settings_invalid_api_key(self):
        """Test validation with invalid API key."""
        # Set invalid settings
        self.dialog.api_key_edit.setText("")
        self.dialog.api_key_env_check.setChecked(False)
        
        # Validate
        self.assertFalse(self.dialog.validate_settings())
        self.assertIn("API Key", self.dialog.validation_errors)
    
    def test_validate_settings_invalid_env_var(self):
        """Test validation with invalid environment variable."""
        # Set invalid settings
        self.dialog.api_key_env_check.setChecked(True)
        self.dialog.api_key_env_edit.setText("")
        
        # Validate
        self.assertFalse(self.dialog.validate_settings())
        self.assertIn("API Key Environment Variable", self.dialog.validation_errors)
    
    def test_save_settings(self):
        """Test that settings are saved correctly."""
        # Set up a mock signal handler
        self.dialog.settings_updated = MagicMock()
        
        # Change some settings
        self.dialog.theme_combo.setCurrentText("Light")
        self.dialog.font_size_combo.setCurrentText("Large")
        self.dialog.provider_combo.setCurrentText("Anthropic")
        self.dialog.model_combo.setCurrentText("claude-3-opus-20240229")
        self.dialog.api_key_edit.setText("new-api-key")
        
        # Save settings
        self.dialog.save_settings()
        
        # Check that the signal was emitted with the correct config
        self.dialog.settings_updated.emit.assert_called_once()
        saved_config = self.dialog.settings_updated.emit.call_args[0][0]
        
        # Check UI settings
        self.assertEqual(saved_config["ui"]["theme"], "light")
        self.assertEqual(saved_config["ui"]["font_size"], 14)  # Large = 14
        
        # Check LLM settings
        self.assertEqual(saved_config["llm"]["provider"], "anthropic")
        self.assertEqual(saved_config["llm"]["model"], "claude-3-opus-20240229")
        self.assertEqual(saved_config["llm"]["api_key"], "new-api-key")
    
    def test_server_list_operations(self):
        """Test server list operations."""
        # Check initial state
        self.assertEqual(self.dialog.server_list.count(), 2)
        self.assertFalse(self.dialog.server_details_group.isVisible())
        
        # Test add server button
        self.dialog.add_server()
        self.assertTrue(self.dialog.server_details_group.isVisible())
        
        # Fill server details
        self.dialog.server_name_edit.setText("test-server")
        self.dialog.server_command_edit.setText("python -m test_server")
        self.dialog.server_args_edit.setText("--arg1 value1")
        self.dialog.auto_approve_edit.setText("tool1, tool2")
        
        # Save server
        self.dialog.save_server()
        
        # Check that server was added
        self.assertEqual(self.dialog.server_list.count(), 3)
        self.assertFalse(self.dialog.server_details_group.isVisible())
        
        # Check server config
        server_config = self.dialog.config["mcp_servers"]["test-server"]
        self.assertEqual(server_config["command"], ["python", "-m", "test_server"])
        self.assertEqual(server_config["args"], ["--arg1", "value1"])
        self.assertEqual(server_config["autoApprove"], ["tool1", "tool2"])
        self.assertFalse(server_config["disabled"])
        
        # Test edit server
        # Select the server
        self.dialog.server_list.setCurrentRow(2)  # Select the new server
        
        # Check that buttons are enabled
        self.assertTrue(self.dialog.edit_server_button.isEnabled())
        self.assertTrue(self.dialog.remove_server_button.isEnabled())
        self.assertTrue(self.dialog.default_server_button.isEnabled())
        
        # Edit the server
        self.dialog.edit_server()
        self.assertTrue(self.dialog.server_details_group.isVisible())
        
        # Check that form is filled correctly
        self.assertEqual(self.dialog.server_name_edit.text(), "test-server")
        self.assertEqual(self.dialog.server_command_edit.text(), "python -m test_server")
        self.assertEqual(self.dialog.server_args_edit.text(), "--arg1 value1")
        self.assertEqual(self.dialog.auto_approve_edit.text(), "tool1, tool2")
        
        # Change some values
        self.dialog.server_args_edit.setText("--arg1 value1 --arg2 value2")
        self.dialog.server_disabled_check.setChecked(True)
        
        # Save changes
        self.dialog.save_server()
        
        # Check that server was updated
        server_config = self.dialog.config["mcp_servers"]["test-server"]
        self.assertEqual(server_config["args"], ["--arg1", "value1", "--arg2", "value2"])
        self.assertTrue(server_config["disabled"])
        
        # Test set default server
        self.dialog.server_list.setCurrentRow(2)  # Select the new server
        self.dialog.set_default_server()
        
        # Check that default server was updated
        self.assertEqual(self.dialog.config["default_server"], "test-server")
        
        # Check that the list was updated
        self.assertEqual(self.dialog.server_list.item(2).text(), "test-server (Default)")


if __name__ == "__main__":
    unittest.main()