"""
Tools Panel component for MCP Agent.

This module provides the tools panel for the MCP Agent GUI, displaying available
tools and resources from connected MCP servers.
"""

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, 
    QListWidget, QTextEdit, QSplitter,
    QListWidgetItem, QLabel, QHBoxLayout,
    QPushButton, QLineEdit, QToolBar,
    QAction, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from mcp_agent.core.models import MCPTool, MCPResource

class ToolsPanel(QWidget):
    """Tools panel for the MCP Agent GUI.
    
    This panel displays available tools and resources from connected MCP servers,
    allowing users to view details about each tool and resource.
    """
    
    # Signal emitted when a tool is selected for use
    tool_selected = pyqtSignal(str)
    
    # Signal emitted when refresh is requested
    refresh_requested = pyqtSignal()
    
    def __init__(self, controller):
        """Initialize the tools panel.
        
        Args:
            controller: The UI controller.
        """
        super().__init__()
        self.controller = controller
        self.tools = {}  # Dictionary of tool name -> MCPTool
        self.resources = {}  # Dictionary of resource URI -> MCPResource
        self.connection_status = False
        self.server_name = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create toolbar with refresh button
        toolbar = QToolBar()
        refresh_action = QAction("Refresh", self)
        refresh_action.setToolTip("Refresh tools and resources")
        refresh_action.triggered.connect(self._on_refresh_clicked)
        toolbar.addAction(refresh_action)
        layout.addWidget(toolbar)
        
        # Create status bar for connection info
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.showMessage("Not connected to any MCP server")
        layout.addWidget(self.status_bar)
        
        # Create search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tools and resources...")
        self.search_input.textChanged.connect(self.filter_items)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tools tab
        tools_widget = QWidget()
        tools_layout = QVBoxLayout()
        tools_widget.setLayout(tools_layout)
        
        tools_splitter = QSplitter(Qt.Orientation.Vertical)
        tools_layout.addWidget(tools_splitter)
        
        self.tools_list = QListWidget()
        tools_splitter.addWidget(self.tools_list)
        
        self.tool_details = QTextEdit()
        self.tool_details.setReadOnly(True)
        tools_splitter.addWidget(self.tool_details)
        
        # Create resources tab
        resources_widget = QWidget()
        resources_layout = QVBoxLayout()
        resources_widget.setLayout(resources_layout)
        
        resources_splitter = QSplitter(Qt.Orientation.Vertical)
        resources_layout.addWidget(resources_splitter)
        
        self.resources_list = QListWidget()
        resources_splitter.addWidget(self.resources_list)
        
        self.resource_details = QTextEdit()
        self.resource_details.setReadOnly(True)
        resources_splitter.addWidget(self.resource_details)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(tools_widget, "Tools")
        self.tab_widget.addTab(resources_widget, "Resources")
        
        # Set initial splitter sizes for both tabs
        tools_splitter.setSizes([int(self.height() * 0.4), int(self.height() * 0.6)])
        resources_splitter.setSizes([int(self.height() * 0.4), int(self.height() * 0.6)])
        
        # Connect signals
        self.tools_list.currentItemChanged.connect(self.show_tool_details)
        self.resources_list.currentItemChanged.connect(self.show_resource_details)
        
        # Set placeholder text for empty lists
        self.update_placeholder_text()
        
    def update_placeholder_text(self):
        """Update placeholder text for empty lists."""
        if self.tools_list.count() == 0:
            self.tool_details.setHtml(
                "<div style='color: gray; text-align: center; margin-top: 20px;'>"
                "<p>No tools available</p>"
                "<p>Connect to an MCP server to see available tools</p>"
                "</div>"
            )
        
        if self.resources_list.count() == 0:
            self.resource_details.setHtml(
                "<div style='color: gray; text-align: center; margin-top: 20px;'>"
                "<p>No resources available</p>"
                "<p>Connect to an MCP server to see available resources</p>"
                "</div>"
            )
    
    def update_tools(self, tools):
        """Update the tools list.
        
        Args:
            tools (dict): Dictionary of tool name -> MCPTool objects.
        """
        self.tools = tools
        self.tools_list.clear()
        
        if not tools:
            self.update_placeholder_text()
            return
            
        # Add tools to list
        for name, tool in tools.items():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)  # Store tool name for lookup
            self.tools_list.addItem(item)
            
        # Sort items alphabetically
        self.tools_list.sortItems()
        
        # Select first item if available
        if self.tools_list.count() > 0:
            self.tools_list.setCurrentRow(0)
            
    def update_resources(self, resources):
        """Update the resources list.
        
        Args:
            resources (dict): Dictionary of resource URI -> MCPResource objects.
        """
        self.resources = resources
        self.resources_list.clear()
        
        if not resources:
            self.update_placeholder_text()
            return
            
        # Add resources to list
        for uri, resource in resources.items():
            item = QListWidgetItem(resource.name or uri)
            item.setData(Qt.ItemDataRole.UserRole, uri)  # Store URI for lookup
            self.resources_list.addItem(item)
            
        # Sort items alphabetically
        self.resources_list.sortItems()
        
        # Select first item if available
        if self.resources_list.count() > 0:
            self.resources_list.setCurrentRow(0)
            
    def filter_items(self, text):
        """Filter items in the current tab based on search text.
        
        Args:
            text (str): The search text.
        """
        # Determine which tab is active
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # Tools tab
            self._filter_list(self.tools_list, text)
        else:  # Resources tab
            self._filter_list(self.resources_list, text)
            
    def _filter_list(self, list_widget, text):
        """Filter items in a list widget.
        
        Args:
            list_widget (QListWidget): The list widget to filter.
            text (str): The search text.
        """
        text = text.lower()
        
        # Show all items if search text is empty
        if not text:
            for i in range(list_widget.count()):
                list_widget.item(i).setHidden(False)
            return
            
        # Hide items that don't match the search text
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setHidden(text not in item.text().lower())
            
    def show_tool_details(self, item):
        """Show details for the selected tool.
        
        Args:
            item: The selected list item.
        """
        if item is None:
            self.tool_details.clear()
            return
            
        # Get tool name from item data
        tool_name = item.data(Qt.ItemDataRole.UserRole)
        
        # Get tool from dictionary
        if tool_name not in self.tools:
            self.tool_details.setHtml(f"<h3>{item.text()}</h3><p>Tool details not available.</p>")
            return
            
        tool = self.tools[tool_name]
        
        # Format input schema as JSON with syntax highlighting
        schema_json = json.dumps(tool.input_schema, indent=2)
        
        # Create HTML content
        html_content = f"""
        <h2>{tool.name}</h2>
        <p><strong>Description:</strong> {tool.description}</p>
        <h3>Input Schema:</h3>
        <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto;">
{schema_json}
</pre>
        """
        
        self.tool_details.setHtml(html_content)
        
    def show_resource_details(self, item):
        """Show details for the selected resource.
        
        Args:
            item: The selected list item.
        """
        if item is None:
            self.resource_details.clear()
            return
            
        # Get resource URI from item data
        resource_uri = item.data(Qt.ItemDataRole.UserRole)
        
        # Get resource from dictionary
        if resource_uri not in self.resources:
            self.resource_details.setHtml(f"<h3>{item.text()}</h3><p>Resource details not available.</p>")
            return
            
        resource = self.resources[resource_uri]
        
        # Create HTML content
        html_content = f"""
        <h2>{resource.name or 'Unnamed Resource'}</h2>
        <p><strong>URI:</strong> {resource.uri}</p>
        """
        
        if resource.description:
            html_content += f"<p><strong>Description:</strong> {resource.description}</p>"
            
        if resource.mime_type:
            html_content += f"<p><strong>MIME Type:</strong> {resource.mime_type}</p>"
            
        self.resource_details.setHtml(html_content)
        
    def update_connection_status(self, connected, server_name=None):
        """Update the panel based on connection status.
        
        Args:
            connected (bool): Whether connected to an MCP server.
            server_name (str, optional): The name of the connected server.
        """
        # Store connection status
        self.connection_status = connected
        self.server_name = server_name
        
        if not connected:
            # Clear tools and resources when disconnected
            self.tools = {}
            self.resources = {}
            self.tools_list.clear()
            self.resources_list.clear()
            self.update_placeholder_text()
            
            # Update tab titles
            self.tab_widget.setTabText(0, "Tools")
            self.tab_widget.setTabText(1, "Resources")
            
            # Update status bar
            self.status_bar.showMessage("Not connected to any MCP server")
        else:
            # Update tab titles with server name if provided
            if server_name:
                self.tab_widget.setTabText(0, f"Tools - {server_name}")
                self.tab_widget.setTabText(1, f"Resources - {server_name}")
                
                # Update status bar
                self.status_bar.showMessage(f"Connected to {server_name}")
                
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        if not self.connection_status:
            self.status_bar.showMessage("Not connected to any MCP server. Cannot refresh.")
            return
            
        self.status_bar.showMessage(f"Refreshing tools and resources from {self.server_name}...")
        self.refresh_requested.emit()
                
    def clear(self):
        """Clear all tools and resources."""
        self.tools = {}
        self.resources = {}
        self.tools_list.clear()
        self.resources_list.clear()
        self.tool_details.clear()
        self.resource_details.clear()
        self.update_placeholder_text()