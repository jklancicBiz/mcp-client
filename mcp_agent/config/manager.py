"""Configuration manager for MCP Agent"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Union, List, Tuple

# Import UIConfig lazily to avoid circular imports
# This is needed because UIConfig might need to import ConfigManager

# Custom YAML representer for tuples
def tuple_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', list(data))

# Custom YAML constructor for sequences that should be tuples
def tuple_constructor(loader, node):
    return tuple(loader.construct_sequence(node))

# Register the representer and constructor
yaml.add_representer(tuple, tuple_representer)
yaml.add_constructor('tag:yaml.org,2002:seq', tuple_constructor)


class ConfigManager:
    """Manages configuration for the MCP agent"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.mcp-agent/config.yaml")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        # Import UIConfig here to avoid circular imports
        from mcp_agent.ui.models.ui_config import UIConfig
        
        default_config = {
            "llm": {
                "provider": "openai",  # or "anthropic"
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY", "")
            },
            "mcp_servers": {
                "filesystem": {
                    "command": ["python", "-m", "mcp_server_filesystem"],
                    "args": ["--path", "."]
                }
            },
            "default_server": "filesystem",
            "ui": UIConfig().to_dict()  # Add default UI configuration
        }
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Save default config
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"📄 Created default config at {self.config_path}")
        print("Please edit the config file to add your API keys and MCP server configurations.")
        
        return default_config
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.config.get("llm", {})
    
    def get_mcp_server_config(self, server_name: str) -> Dict[str, Any]:
        """Get MCP server configuration"""
        servers = self.config.get("mcp_servers", {})
        return servers.get(server_name, {})
    
    def get_default_server(self) -> str:
        """Get default MCP server name"""
        return self.config.get("default_server", "filesystem")
        
    def get_ui_config(self):
        """Get UI configuration
        
        Returns:
            UIConfig: The UI configuration object
        """
        # Import UIConfig here to avoid circular imports
        from mcp_agent.ui.models.ui_config import UIConfig
        
        ui_dict = self.config.get("ui", {})
        return UIConfig.from_dict(ui_dict)
        
    def save_ui_config(self, ui_config) -> None:
        """Save UI configuration
        
        Args:
            ui_config (UIConfig): The UI configuration to save
        """
        # Import UIConfig here to avoid circular imports
        from mcp_agent.ui.models.ui_config import UIConfig
        
        # Type check
        if not isinstance(ui_config, UIConfig):
            raise TypeError("ui_config must be an instance of UIConfig")
            
        # Validate the configuration before saving
        ui_config.validate()
        
        # Update the config dictionary
        self.config["ui"] = ui_config.to_dict()
        
        # Save to file
        self._save_config()
        
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")