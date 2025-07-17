"""
Unit tests for the Tools Panel component.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QListWidgetItem
from PyQt6.QtCore import Qt

from mcp_agent.ui.components.tools_panel import ToolsPanel
from mcp_agent.core.models import MCPTool, MCPResource

# Mock QApplication for tests
@pytest.fixture
def app():
    """Create a QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # No need to clean up as we're not starting the event loop

@pytest.fixture
def mock_controller():
    """Create a mock controller for tests."""
    controller = MagicMock()
    return controller

@pytest.fixture
def tools_panel(app, mock_controller):
    """Create a ToolsPanel instance for tests."""
    panel = ToolsPanel(mock_controller)
    return panel

@pytest.fixture
def sample_tools():
    """Create sample tools for tests."""
    return {
        "tool1": MCPTool(
            name="tool1",
            description="Test tool 1",
            input_schema={"type": "object", "properties": {"param1": {"type": "string"}}}
        ),
        "tool2": MCPTool(
            name="tool2",
            description="Test tool 2",
            input_schema={"type": "object", "properties": {"param2": {"type": "number"}}}
        )
    }

@pytest.fixture
def sample_resources():
    """Create sample resources for tests."""
    return {
        "uri1": MCPResource(
            uri="uri1",
            name="Resource 1",
            description="Test resource 1",
            mime_type="text/plain"
        ),
        "uri2": MCPResource(
            uri="uri2",
            name="Resource 2",
            description="Test resource 2",
            mime_type="application/json"
        )
    }

def test_tools_panel_init(tools_panel):
    """Test that the tools panel initializes correctly."""
    # Check that the panel has the expected widgets
    assert hasattr(tools_panel, "tools_list")
    assert hasattr(tools_panel, "resources_list")
    assert hasattr(tools_panel, "tool_details")
    assert hasattr(tools_panel, "resource_details")
    assert hasattr(tools_panel, "tab_widget")
    assert hasattr(tools_panel, "search_input")
    
    # Check that the tab widget has the expected tabs
    assert tools_panel.tab_widget.count() == 2
    assert tools_panel.tab_widget.tabText(0) == "Tools"
    assert tools_panel.tab_widget.tabText(1) == "Resources"

def test_update_tools(tools_panel, sample_tools):
    """Test updating the tools list."""
    # Initially the list should be empty
    assert tools_panel.tools_list.count() == 0
    
    # Update with sample tools
    tools_panel.update_tools(sample_tools)
    
    # Check that the tools were added to the list
    assert tools_panel.tools_list.count() == 2
    
    # Check that the tools are sorted alphabetically
    assert tools_panel.tools_list.item(0).text() == "tool1"
    assert tools_panel.tools_list.item(1).text() == "tool2"
    
    # Check that the first item is selected
    assert tools_panel.tools_list.currentRow() == 0

def test_update_resources(tools_panel, sample_resources):
    """Test updating the resources list."""
    # Initially the list should be empty
    assert tools_panel.resources_list.count() == 0
    
    # Update with sample resources
    tools_panel.update_resources(sample_resources)
    
    # Check that the resources were added to the list
    assert tools_panel.resources_list.count() == 2
    
    # Check that the resources are sorted alphabetically
    assert tools_panel.resources_list.item(0).text() == "Resource 1"
    assert tools_panel.resources_list.item(1).text() == "Resource 2"
    
    # Check that the first item is selected
    assert tools_panel.resources_list.currentRow() == 0

def test_show_tool_details(tools_panel, sample_tools):
    """Test showing tool details."""
    # Update with sample tools
    tools_panel.update_tools(sample_tools)
    
    # Create a mock item
    item = QListWidgetItem("tool1")
    item.setData(Qt.ItemDataRole.UserRole, "tool1")
    
    # Show details for the item
    tools_panel.show_tool_details(item)
    
    # Check that the details were updated
    html_content = tools_panel.tool_details.toHtml()
    assert "tool1" in html_content
    assert "Test tool 1" in html_content
    assert "param1" in html_content
    
    # Test with None item
    tools_panel.show_tool_details(None)
    assert tools_panel.tool_details.toPlainText() == ""
    
    # Test with unknown tool
    unknown_item = QListWidgetItem("unknown")
    unknown_item.setData(Qt.ItemDataRole.UserRole, "unknown")
    tools_panel.show_tool_details(unknown_item)
    assert "Tool details not available" in tools_panel.tool_details.toHtml()

def test_show_resource_details(tools_panel, sample_resources):
    """Test showing resource details."""
    # Update with sample resources
    tools_panel.update_resources(sample_resources)
    
    # Create a mock item
    item = QListWidgetItem("Resource 1")
    item.setData(Qt.ItemDataRole.UserRole, "uri1")
    
    # Show details for the item
    tools_panel.show_resource_details(item)
    
    # Check that the details were updated
    html_content = tools_panel.resource_details.toHtml()
    assert "Resource 1" in html_content
    assert "uri1" in html_content
    assert "Test resource 1" in html_content
    assert "text/plain" in html_content
    
    # Test with None item
    tools_panel.show_resource_details(None)
    assert tools_panel.resource_details.toPlainText() == ""
    
    # Test with unknown resource
    unknown_item = QListWidgetItem("unknown")
    unknown_item.setData(Qt.ItemDataRole.UserRole, "unknown")
    tools_panel.show_resource_details(unknown_item)
    assert "Resource details not available" in tools_panel.resource_details.toHtml()

def test_filter_items(tools_panel, sample_tools, sample_resources):
    """Test filtering items based on search text."""
    # Update with sample tools and resources
    tools_panel.update_tools(sample_tools)
    tools_panel.update_resources(sample_resources)
    
    # Set the active tab to tools
    tools_panel.tab_widget.setCurrentIndex(0)
    
    # Filter tools with text that matches one tool
    tools_panel.search_input.setText("tool1")
    
    # Check that only the matching tool is visible
    assert not tools_panel.tools_list.item(0).isHidden()
    assert tools_panel.tools_list.item(1).isHidden()
    
    # Clear the filter
    tools_panel.search_input.setText("")
    
    # Check that all tools are visible
    assert not tools_panel.tools_list.item(0).isHidden()
    assert not tools_panel.tools_list.item(1).isHidden()
    
    # Set the active tab to resources
    tools_panel.tab_widget.setCurrentIndex(1)
    
    # Filter resources with text that matches one resource
    tools_panel.search_input.setText("Resource 1")
    
    # Check that only the matching resource is visible
    assert not tools_panel.resources_list.item(0).isHidden()
    assert tools_panel.resources_list.item(1).isHidden()

def test_update_connection_status(tools_panel, sample_tools, sample_resources):
    """Test updating connection status."""
    # Update with sample tools and resources
    tools_panel.update_tools(sample_tools)
    tools_panel.update_resources(sample_resources)
    
    # Update connection status to disconnected
    tools_panel.update_connection_status(False)
    
    # Check that tools and resources were cleared
    assert tools_panel.tools_list.count() == 0
    assert tools_panel.resources_list.count() == 0
    assert tools_panel.tab_widget.tabText(0) == "Tools"
    assert tools_panel.tab_widget.tabText(1) == "Resources"
    assert tools_panel.status_bar.currentMessage() == "Not connected to any MCP server"
    assert tools_panel.connection_status is False
    assert tools_panel.server_name is None
    
    # Update with sample tools and resources again
    tools_panel.update_tools(sample_tools)
    tools_panel.update_resources(sample_resources)
    
    # Update connection status to connected with server name
    tools_panel.update_connection_status(True, "Test Server")
    
    # Check that tab titles were updated
    assert tools_panel.tab_widget.tabText(0) == "Tools - Test Server"
    assert tools_panel.tab_widget.tabText(1) == "Resources - Test Server"
    assert tools_panel.status_bar.currentMessage() == "Connected to Test Server"
    assert tools_panel.connection_status is True
    assert tools_panel.server_name == "Test Server"

def test_refresh_functionality(tools_panel):
    """Test the refresh functionality."""
    # Set connection status to connected
    tools_panel.update_connection_status(True, "Test Server")
    
    # Mock the refresh_requested signal
    tools_panel.refresh_requested = MagicMock()
    
    # Trigger refresh
    tools_panel._on_refresh_clicked()
    
    # Check that the refresh_requested signal was emitted
    tools_panel.refresh_requested.emit.assert_called_once()
    
    # Check status bar message
    assert "Refreshing tools and resources" in tools_panel.status_bar.currentMessage()
    
    # Test refresh when not connected
    tools_panel.update_connection_status(False)
    tools_panel.refresh_requested.reset_mock()
    
    # Trigger refresh when not connected
    tools_panel._on_refresh_clicked()
    
    # Check that the refresh_requested signal was not emitted
    tools_panel.refresh_requested.emit.assert_not_called()
    
    # Check status bar message
    assert "Not connected to any MCP server" in tools_panel.status_bar.currentMessage()

def test_clear(tools_panel, sample_tools, sample_resources):
    """Test clearing the panel."""
    # Update with sample tools and resources
    tools_panel.update_tools(sample_tools)
    tools_panel.update_resources(sample_resources)
    
    # Clear the panel
    tools_panel.clear()
    
    # Check that tools and resources were cleared
    assert tools_panel.tools_list.count() == 0
    assert tools_panel.resources_list.count() == 0
    assert tools_panel.tools == {}
    assert tools_panel.resources == {}