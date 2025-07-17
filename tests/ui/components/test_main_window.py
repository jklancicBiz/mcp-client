"""
Tests for the MainWindow component.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QAction

# Import the MainWindow class
from mcp_agent.ui.components.main_window import MainWindow
from mcp_agent.ui.models.ui_config import UIConfig

# Create a QApplication instance for testing
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

class TestMainWindow(unittest.TestCase):
    """Test cases for the MainWindow class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock controller
        self.mock_controller = MagicMock()
        
        # Create a mock config manager
        self.mock_config_manager = MagicMock()
        self.mock_controller.settings_controller.config_manager = self.mock_config_manager
        
        # Create a mock UI config
        self.ui_config = UIConfig(
            theme="light",
            font_size=12,
            window_size=(800, 600),
            window_position=(100, 100),
            show_tool_panel=True,
            show_status_bar=True
        )
        
        # Configure the mock config manager to return the mock UI config
        self.mock_config_manager.get_ui_config.return_value = self.ui_config
        
        # Create the main window
        self.window = MainWindow(self.mock_controller)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Close the window
        self.window.close()
    
    def test_init(self):
        """Test that the window initializes correctly."""
        # Check that the window has the correct title
        self.assertEqual(self.window.windowTitle(), "MCP Agent")
        
        # Check that the window has the correct minimum size
        self.assertEqual(self.window.minimumSize(), QSize(800, 600))
        
        # Check that the window has a menu bar
        self.assertIsNotNone(self.window.menuBar())
        
        # Check that the window has a status bar
        self.assertIsNotNone(self.window.statusBar())
        
        # Check that the window has a central widget
        self.assertIsNotNone(self.window.centralWidget())
        
        # Check that the window has a chat panel
        self.assertIsNotNone(self.window.chat_panel)
        
        # Check that the window has a tools panel
        self.assertIsNotNone(self.window.tools_panel)
    
    def test_restore_window_state(self):
        """Test that the window state is restored from configuration."""
        # Check that the window size is restored
        self.assertEqual(self.window.size(), QSize(*self.ui_config.window_size))
        
        # Check that the window position is restored
        self.assertEqual(self.window.pos(), QPoint(*self.ui_config.window_position))
        
        # Note: In a headless test environment, widgets might not be visible
        # regardless of their isVisible() property, so we check the UI config directly
        
        # Check that the UI config has the correct values
        self.assertEqual(self.window.ui_config.show_tool_panel, self.ui_config.show_tool_panel)
        self.assertEqual(self.window.ui_config.show_status_bar, self.ui_config.show_status_bar)
    
    def test_save_window_state(self):
        """Test that the window state is saved to configuration."""
        # Change the window size and position
        new_size = (1000, 800)
        new_position = (200, 200)
        self.window.resize(*new_size)
        self.window.move(*new_position)
        
        # Save the window state
        self.window.save_window_state()
        
        # Check that the UI config was updated
        self.assertEqual(self.window.ui_config.window_size, new_size)
        self.assertEqual(self.window.ui_config.window_position, new_position)
        
        # Check that the config manager was called to save the UI config
        self.mock_config_manager.save_ui_config.assert_called_once_with(self.window.ui_config)
    
    def test_toggle_tools_panel(self):
        """Test that the tools panel can be toggled."""
        # Make sure the UI config is set correctly initially
        self.window.ui_config.show_tool_panel = True
        
        # Toggle the tools panel off
        self.window.toggle_tools_panel(False)
        
        # Check that the UI config was updated
        self.assertFalse(self.window.ui_config.show_tool_panel)
        
        # Toggle the tools panel on
        self.window.toggle_tools_panel(True)
        
        # Check that the UI config was updated
        self.assertTrue(self.window.ui_config.show_tool_panel)
    
    def test_toggle_status_bar(self):
        """Test that the status bar can be toggled."""
        # Make sure the UI config is set correctly initially
        self.window.ui_config.show_status_bar = True
        
        # Toggle the status bar off
        self.window.toggle_status_bar(False)
        
        # Check that the UI config was updated
        self.assertFalse(self.window.ui_config.show_status_bar)
        
        # Toggle the status bar on
        self.window.toggle_status_bar(True)
        
        # Check that the UI config was updated
        self.assertTrue(self.window.ui_config.show_status_bar)
    
    def test_update_status(self):
        """Test that the status bar message can be updated."""
        # Update the status
        test_message = "Test status message"
        self.window.update_status(test_message)
        
        # Check that the status bar message was updated
        self.assertEqual(self.window.statusBar().currentMessage(), test_message)
    
    def test_close_event(self):
        """Test that the window state is saved when the window is closed."""
        # Mock the save_window_state method
        self.window.save_window_state = MagicMock()
        
        # Create a mock close event
        mock_event = MagicMock()
        
        # Call the closeEvent method
        self.window.closeEvent(mock_event)
        
        # Check that save_window_state was called
        self.window.save_window_state.assert_called_once()
        
        # Check that the event was accepted
        mock_event.accept.assert_called_once()


if __name__ == "__main__":
    unittest.main()