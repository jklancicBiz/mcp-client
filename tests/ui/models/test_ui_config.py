"""
Tests for the UI configuration model.
"""

import unittest
import os
import tempfile
import shutil
from mcp_agent.ui.models.ui_config import UIConfig
from mcp_agent.config.manager import ConfigManager


class TestUIConfig(unittest.TestCase):
    """Tests for the UIConfig class."""
    
    def test_init_defaults(self):
        """Test initialization with default values."""
        config = UIConfig()
        
        # Appearance settings
        self.assertEqual(config.theme, "system")
        self.assertEqual(config.font_size, 12)
        self.assertTrue(config.high_dpi_scaling)
        
        # Window settings
        self.assertEqual(config.window_size, (800, 600))
        self.assertIsNone(config.window_position)
        
        # Panel visibility
        self.assertTrue(config.show_tool_panel)
        self.assertTrue(config.show_status_bar)
        
        # Conversation settings
        self.assertEqual(config.conversation_history_limit, 50)
        self.assertEqual(config.default_export_format, "json")
        
        # Server settings
        self.assertEqual(config.recent_servers, [])
    
    def test_init_custom(self):
        """Test initialization with custom values."""
        config = UIConfig(
            # Appearance settings
            theme="dark",
            font_size=14,
            high_dpi_scaling=False,
            
            # Window settings
            window_size=(1024, 768),
            window_position=(100, 100),
            
            # Panel visibility
            show_tool_panel=False,
            show_status_bar=False,
            
            # Conversation settings
            conversation_history_limit=100,
            default_export_format="markdown",
            
            # Server settings
            recent_servers=["filesystem", "git"]
        )
        
        # Appearance settings
        self.assertEqual(config.theme, "dark")
        self.assertEqual(config.font_size, 14)
        self.assertFalse(config.high_dpi_scaling)
        
        # Window settings
        self.assertEqual(config.window_size, (1024, 768))
        self.assertEqual(config.window_position, (100, 100))
        
        # Panel visibility
        self.assertFalse(config.show_tool_panel)
        self.assertFalse(config.show_status_bar)
        
        # Conversation settings
        self.assertEqual(config.conversation_history_limit, 100)
        self.assertEqual(config.default_export_format, "markdown")
        
        # Server settings
        self.assertEqual(config.recent_servers, ["filesystem", "git"])
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = UIConfig(
            # Appearance settings
            theme="light",
            font_size=16,
            high_dpi_scaling=True,
            
            # Window settings
            window_size=(1200, 800),
            window_position=(200, 200),
            
            # Panel visibility
            show_tool_panel=True,
            show_status_bar=False,
            
            # Conversation settings
            conversation_history_limit=75,
            default_export_format="text",
            
            # Server settings
            recent_servers=["browser", "database"]
        )
        
        config_dict = config.to_dict()
        
        # Appearance settings
        self.assertEqual(config_dict["theme"], "light")
        self.assertEqual(config_dict["font_size"], 16)
        self.assertTrue(config_dict["high_dpi_scaling"])
        
        # Window settings
        self.assertEqual(config_dict["window_size"], (1200, 800))
        self.assertEqual(config_dict["window_position"], (200, 200))
        
        # Panel visibility
        self.assertTrue(config_dict["show_tool_panel"])
        self.assertFalse(config_dict["show_status_bar"])
        
        # Conversation settings
        self.assertEqual(config_dict["conversation_history_limit"], 75)
        self.assertEqual(config_dict["default_export_format"], "text")
        
        # Server settings
        self.assertEqual(config_dict["recent_servers"], ["browser", "database"])
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            # Appearance settings
            "theme": "dark",
            "font_size": 14,
            "high_dpi_scaling": False,
            
            # Window settings
            "window_size": (1024, 768),
            "window_position": (100, 100),
            
            # Panel visibility
            "show_tool_panel": False,
            "show_status_bar": False,
            
            # Conversation settings
            "conversation_history_limit": 100,
            "default_export_format": "markdown",
            
            # Server settings
            "recent_servers": ["filesystem", "git"]
        }
        
        config = UIConfig.from_dict(config_dict)
        
        # Appearance settings
        self.assertEqual(config.theme, "dark")
        self.assertEqual(config.font_size, 14)
        self.assertFalse(config.high_dpi_scaling)
        
        # Window settings
        self.assertEqual(config.window_size, (1024, 768))
        self.assertEqual(config.window_position, (100, 100))
        
        # Panel visibility
        self.assertFalse(config.show_tool_panel)
        self.assertFalse(config.show_status_bar)
        
        # Conversation settings
        self.assertEqual(config.conversation_history_limit, 100)
        self.assertEqual(config.default_export_format, "markdown")
        
        # Server settings
        self.assertEqual(config.recent_servers, ["filesystem", "git"])
    
    def test_from_dict_partial(self):
        """Test creation from partial dictionary."""
        config_dict = {
            "theme": "light",
            "font_size": 16,
            "show_status_bar": False
        }
        
        config = UIConfig.from_dict(config_dict)
        
        # Specified values
        self.assertEqual(config.theme, "light")
        self.assertEqual(config.font_size, 16)
        self.assertFalse(config.show_status_bar)
        
        # Default values
        self.assertTrue(config.high_dpi_scaling)
        self.assertEqual(config.window_size, (800, 600))
        self.assertIsNone(config.window_position)
        self.assertTrue(config.show_tool_panel)
        self.assertEqual(config.conversation_history_limit, 50)
        self.assertEqual(config.default_export_format, "json")
        self.assertEqual(config.recent_servers, [])


class TestUIConfigWithConfigManager(unittest.TestCase):
    """Tests for the integration of UIConfig with ConfigManager."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for config files
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.yaml")
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_config_manager_default_ui_config(self):
        """Test that ConfigManager creates default UI config."""
        config_manager = ConfigManager(config_path=self.config_path)
        ui_config = config_manager.get_ui_config()
        
        # Check that default values are set
        self.assertEqual(ui_config.theme, "system")
        self.assertEqual(ui_config.font_size, 12)
        self.assertTrue(ui_config.high_dpi_scaling)
        self.assertEqual(ui_config.window_size, (800, 600))
        
    def test_save_and_load_ui_config(self):
        """Test saving and loading UI config through ConfigManager."""
        # Create a config manager and get default UI config
        config_manager = ConfigManager(config_path=self.config_path)
        
        # Create a custom UI config
        custom_ui_config = UIConfig(
            theme="dark",
            font_size=16,
            window_size=(1200, 800),
            show_tool_panel=False
        )
        
        # Save the custom UI config
        config_manager.save_ui_config(custom_ui_config)
        
        # Create a new config manager to load the saved config
        new_config_manager = ConfigManager(config_path=self.config_path)
        loaded_ui_config = new_config_manager.get_ui_config()
        
        # Check that the loaded config matches the saved config
        self.assertEqual(loaded_ui_config.theme, "dark")
        self.assertEqual(loaded_ui_config.font_size, 16)
        self.assertEqual(loaded_ui_config.window_size, (1200, 800))
        self.assertFalse(loaded_ui_config.show_tool_panel)
        
    def test_partial_ui_config_update(self):
        """Test updating only part of the UI config."""
        # Create a config manager
        config_manager = ConfigManager(config_path=self.config_path)
        
        # Get the default UI config and modify it
        ui_config = config_manager.get_ui_config()
        ui_config.theme = "light"
        ui_config.font_size = 14
        
        # Save the modified UI config
        config_manager.save_ui_config(ui_config)
        
        # Create a new config manager to load the saved config
        new_config_manager = ConfigManager(config_path=self.config_path)
        loaded_ui_config = new_config_manager.get_ui_config()
        
        # Check that the modified values are saved
        self.assertEqual(loaded_ui_config.theme, "light")
        self.assertEqual(loaded_ui_config.font_size, 14)
        
        # Check that other values remain at defaults
        self.assertTrue(loaded_ui_config.high_dpi_scaling)
        self.assertEqual(loaded_ui_config.window_size, (800, 600))
        self.assertTrue(loaded_ui_config.show_tool_panel)


class TestUIConfigValidation(unittest.TestCase):
    """Tests for the UIConfig validation methods."""
    
    def test_valid_config(self):
        """Test validation of a valid configuration."""
        config = UIConfig(
            theme="dark",
            font_size=14,
            window_size=(1024, 768),
            default_export_format="json",
            conversation_history_limit=50
        )
        self.assertTrue(config.validate())
    
    def test_invalid_theme(self):
        """Test validation with an invalid theme."""
        config = UIConfig(theme="blue")
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("Invalid theme", str(context.exception))
    
    def test_invalid_font_size(self):
        """Test validation with an invalid font size."""
        config = UIConfig(font_size=0)
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("Invalid font size", str(context.exception))
    
    def test_invalid_window_size(self):
        """Test validation with an invalid window size."""
        config = UIConfig(window_size=(0, 600))
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("Invalid window size", str(context.exception))
    
    def test_invalid_export_format(self):
        """Test validation with an invalid export format."""
        config = UIConfig(default_export_format="csv")
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("Invalid export format", str(context.exception))
    
    def test_invalid_history_limit(self):
        """Test validation with an invalid conversation history limit."""
        config = UIConfig(conversation_history_limit=0)
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn("Invalid conversation history limit", str(context.exception))


class TestUIConfigUtilities(unittest.TestCase):
    """Tests for the UIConfig utility methods."""
    
    def test_add_recent_server(self):
        """Test adding a server to the recent servers list."""
        config = UIConfig()
        self.assertEqual(config.recent_servers, [])
        
        # Add a server
        config.add_recent_server("filesystem")
        self.assertEqual(config.recent_servers, ["filesystem"])
        
        # Add another server
        config.add_recent_server("git")
        self.assertEqual(config.recent_servers, ["git", "filesystem"])
        
        # Add an existing server (should move to front)
        config.add_recent_server("filesystem")
        self.assertEqual(config.recent_servers, ["filesystem", "git"])
        
        # Add multiple servers to test limit
        config.add_recent_server("browser")
        config.add_recent_server("database")
        config.add_recent_server("api")
        config.add_recent_server("search")
        self.assertEqual(len(config.recent_servers), 5)
        self.assertEqual(config.recent_servers[0], "search")
    
    def test_get_font_size_name(self):
        """Test getting the name of a font size."""
        self.assertEqual(UIConfig.get_font_size_name(10), "small")
        self.assertEqual(UIConfig.get_font_size_name(12), "medium")
        self.assertEqual(UIConfig.get_font_size_name(14), "large")
        self.assertEqual(UIConfig.get_font_size_name(16), "x-large")
        self.assertEqual(UIConfig.get_font_size_name(18), "custom")
    
    def test_get_font_size_from_name(self):
        """Test getting the font size from a name."""
        self.assertEqual(UIConfig.get_font_size_from_name("small"), 10)
        self.assertEqual(UIConfig.get_font_size_from_name("medium"), 12)
        self.assertEqual(UIConfig.get_font_size_from_name("large"), 14)
        self.assertEqual(UIConfig.get_font_size_from_name("x-large"), 16)
        
        # Test case insensitivity
        self.assertEqual(UIConfig.get_font_size_from_name("SMALL"), 10)
        self.assertEqual(UIConfig.get_font_size_from_name("Medium"), 12)
        
        # Test invalid name
        with self.assertRaises(ValueError) as context:
            UIConfig.get_font_size_from_name("huge")
        self.assertIn("Invalid font size name", str(context.exception))


if __name__ == "__main__":
    unittest.main()