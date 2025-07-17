"""
UI Configuration model for MCP Agent.

This module provides the data model for UI-specific configuration.
"""

import os
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional, List, ClassVar

@dataclass
class UIConfig:
    """Represents UI-specific configuration.
    
    This class stores UI-specific settings for the MCP Agent GUI, including
    appearance preferences, window settings, and panel visibility options.
    
    Attributes:
        theme: The UI theme ("light", "dark", or "system")
        font_size: The font size in points
        window_size: The window size as (width, height) in pixels
        window_position: The window position as (x, y) coordinates
        show_tool_panel: Whether to show the tool panel
        show_status_bar: Whether to show the status bar
        conversation_history_limit: Maximum number of conversations to keep in history
        recent_servers: List of recently used MCP servers
        default_export_format: Default format for exporting conversations
        high_dpi_scaling: Whether to enable high DPI scaling
    
    Class Attributes:
        VALID_THEMES: Valid theme options
        VALID_EXPORT_FORMATS: Valid export format options
        DEFAULT_FONT_SIZES: Default font size options
    """
    
    # Class constants for validation
    VALID_THEMES: ClassVar[List[str]] = ["light", "dark", "system"]
    VALID_EXPORT_FORMATS: ClassVar[List[str]] = ["json", "text", "markdown"]
    DEFAULT_FONT_SIZES: ClassVar[Dict[str, int]] = {
        "small": 10,
        "medium": 12,
        "large": 14,
        "x-large": 16
    }
    
    # Appearance settings
    theme: str = "system"  # "light", "dark", or "system"
    font_size: int = 12
    high_dpi_scaling: bool = True
    
    # Window settings
    window_size: Tuple[int, int] = (800, 600)
    window_position: Optional[Tuple[int, int]] = None
    
    # Panel visibility
    show_tool_panel: bool = True
    show_status_bar: bool = True
    
    # Conversation settings
    conversation_history_limit: int = 50
    default_export_format: str = "json"  # "json", "text", or "markdown"
    
    # Server settings
    recent_servers: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary.
        
        Returns:
            A dictionary representation of the configuration.
        """
        return {
            # Appearance settings
            "theme": self.theme,
            "font_size": self.font_size,
            "high_dpi_scaling": self.high_dpi_scaling,
            
            # Window settings
            "window_size": self.window_size,
            "window_position": self.window_position,
            
            # Panel visibility
            "show_tool_panel": self.show_tool_panel,
            "show_status_bar": self.show_status_bar,
            
            # Conversation settings
            "conversation_history_limit": self.conversation_history_limit,
            "default_export_format": self.default_export_format,
            
            # Server settings
            "recent_servers": self.recent_servers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIConfig':
        """Create a configuration from a dictionary.
        
        Args:
            data: The dictionary containing configuration values.
            
        Returns:
            A UIConfig instance.
        """
        # Convert window_size from list to tuple if needed
        window_size = data.get("window_size", (800, 600))
        if isinstance(window_size, list):
            window_size = tuple(window_size)
            
        # Convert window_position from list to tuple if needed
        window_position = data.get("window_position")
        if isinstance(window_position, list):
            window_position = tuple(window_position)
            
        return cls(
            # Appearance settings
            theme=data.get("theme", "system"),
            font_size=data.get("font_size", 12),
            high_dpi_scaling=data.get("high_dpi_scaling", True),
            
            # Window settings
            window_size=window_size,
            window_position=window_position,
            
            # Panel visibility
            show_tool_panel=data.get("show_tool_panel", True),
            show_status_bar=data.get("show_status_bar", True),
            
            # Conversation settings
            conversation_history_limit=data.get("conversation_history_limit", 50),
            default_export_format=data.get("default_export_format", "json"),
            
            # Server settings
            recent_servers=data.get("recent_servers", [])
        )
        
    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            bool: True if the configuration is valid, False otherwise.
        
        Raises:
            ValueError: If the configuration is invalid.
        """
        # Validate theme
        if self.theme not in self.VALID_THEMES:
            raise ValueError(f"Invalid theme: {self.theme}. Valid themes are: {', '.join(self.VALID_THEMES)}")
        
        # Validate font size
        if self.font_size <= 0:
            raise ValueError(f"Invalid font size: {self.font_size}. Font size must be positive.")
        
        # Validate window size
        if self.window_size[0] <= 0 or self.window_size[1] <= 0:
            raise ValueError(f"Invalid window size: {self.window_size}. Window dimensions must be positive.")
        
        # Validate export format
        if self.default_export_format not in self.VALID_EXPORT_FORMATS:
            raise ValueError(
                f"Invalid export format: {self.default_export_format}. "
                f"Valid formats are: {', '.join(self.VALID_EXPORT_FORMATS)}"
            )
        
        # Validate conversation history limit
        if self.conversation_history_limit <= 0:
            raise ValueError(
                f"Invalid conversation history limit: {self.conversation_history_limit}. "
                "Limit must be positive."
            )
        
        return True
    
    def add_recent_server(self, server_name: str) -> None:
        """Add a server to the recent servers list.
        
        If the server is already in the list, it will be moved to the front.
        
        Args:
            server_name: The name of the server to add.
        """
        # Remove the server if it's already in the list
        if server_name in self.recent_servers:
            self.recent_servers.remove(server_name)
        
        # Add the server to the front of the list
        self.recent_servers.insert(0, server_name)
        
        # Limit the list to the most recent servers
        self.recent_servers = self.recent_servers[:5]
    
    @classmethod
    def get_font_size_name(cls, size: int) -> str:
        """Get the name of a font size.
        
        Args:
            size: The font size in points.
            
        Returns:
            The name of the font size, or "custom" if not a standard size.
        """
        for name, value in cls.DEFAULT_FONT_SIZES.items():
            if value == size:
                return name
        return "custom"
    
    @classmethod
    def get_font_size_from_name(cls, name: str) -> int:
        """Get the font size from a name.
        
        Args:
            name: The name of the font size.
            
        Returns:
            The font size in points.
            
        Raises:
            ValueError: If the name is not a valid font size name.
        """
        if name.lower() in cls.DEFAULT_FONT_SIZES:
            return cls.DEFAULT_FONT_SIZES[name.lower()]
        raise ValueError(f"Invalid font size name: {name}")