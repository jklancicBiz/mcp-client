"""
Tests for the agent controller.
"""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from mcp_agent.ui.controllers.agent_controller import AgentController
from mcp_agent.ui.components.notification import NotificationType
from mcp_agent.ui.components.feedback_manager import ProgressType
from mcp_agent.core.exceptions import MCPConnectionError, MCPToolError


class TestAgentController(unittest.TestCase):
    """Test cases for the AgentController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create agent controller
        self.agent_controller = AgentController()
        
        # Mock feedback controller
        self.mock_feedback_controller = MagicMock()
        self.agent_controller.set_feedback_controller(self.mock_feedback_controller)
        
        # Mock signals
        self.agent_controller.message_processed = MagicMock()
        self.agent_controller.tool_called = MagicMock()
        self.agent_controller.error_occurred = MagicMock()
        self.agent_controller.tools_updated = MagicMock()
        self.agent_controller.resources_updated = MagicMock()
        self.agent_controller.connection_status_changed = MagicMock()
        self.agent_controller.model_info_updated = MagicMock()
    
    @patch('mcp_agent.ui.controllers.agent_controller.MCPClient')
    @patch('mcp_agent.ui.controllers.agent_controller.OpenAIProvider')
    @patch('mcp_agent.ui.controllers.agent_controller.MCPAgent')
    def test_initialize_agent_success(self, mock_agent_class, mock_openai_class, mock_client_class):
        """Test initializing agent successfully."""
        # Create mock objects
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.tools = {'tool1': MagicMock(), 'tool2': MagicMock()}
        mock_client.resources = {'resource1': MagicMock(), 'resource2': MagicMock()}
        
        mock_provider = MagicMock()
        mock_openai_class.return_value = mock_provider
        
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # Mock start_progress
        self.mock_feedback_controller.start_progress.return_value = "test-op-id"
        
        # Create test config
        config = {
            'server': {
                'name': 'test-server',
                'url': 'http://localhost:8000'
            },
            'llm': {
                'type': 'openai',
                'model': 'gpt-4',
                'api_key': 'test-key'
            }
        }
        
        # Initialize agent
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.agent_controller.initialize_agent(config))
        
        # Check result
        self.assertTrue(result)
        
        # Check client initialization
        mock_client_class.assert_called_once_with(config['server'])
        mock_client.connect.assert_called_once()
        
        # Check provider initialization
        mock_openai_class.assert_called_once_with(config['llm'])
        
        # Check agent initialization
        mock_agent_class.assert_called_once_with(mock_provider, mock_client)
        
        # Check connection status update
        self.assertTrue(self.agent_controller.connected)
        self.assertEqual(self.agent_controller.server_name, 'test-server')
        self.assertEqual(self.agent_controller.model_name, 'gpt-4')
        self.assertEqual(self.agent_controller.provider_name, 'OpenAI')
        
        # Check signal emissions
        self.agent_controller.connection_status_changed.emit.assert_called_once_with(True, 'test-server')
        self.agent_controller.model_info_updated.emit.assert_called_once_with('OpenAI', 'gpt-4')
        self.agent_controller.tools_updated.emit.assert_called_once_with(mock_client.tools)
        self.agent_controller.resources_updated.emit.assert_called_once_with(mock_client.resources)
        
        # Check feedback controller calls
        self.mock_feedback_controller.start_progress.assert_called_once_with(
            "Initializing agent...",
            ProgressType.INDETERMINATE
        )
        self.mock_feedback_controller.update_progress.assert_any_call(
            "test-op-id",
            message="Connecting to MCP server..."
        )
        self.mock_feedback_controller.update_progress.assert_any_call(
            "test-op-id",
            message="Initializing LLM provider..."
        )
        self.mock_feedback_controller.update_progress.assert_any_call(
            "test-op-id",
            message="Creating agent..."
        )
        self.mock_feedback_controller.complete_progress.assert_called_once_with(
            "test-op-id",
            success=True,
            message="Connected to test-server with OpenAI (gpt-4)",
            notification=True
        )
    
    @patch('mcp_agent.ui.controllers.agent_controller.MCPClient')
    def test_initialize_agent_connection_error(self, mock_client_class):
        """Test initializing agent with connection error."""
        # Create mock client that raises connection error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.connect.side_effect = MCPConnectionError("Connection failed")
        
        # Mock start_progress
        self.mock_feedback_controller.start_progress.return_value = "test-op-id"
        
        # Create test config
        config = {
            'server': {
                'name': 'test-server',
                'url': 'http://localhost:8000'
            },
            'llm': {
                'type': 'openai',
                'model': 'gpt-4',
                'api_key': 'test-key'
            }
        }
        
        # Initialize agent
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.agent_controller.initialize_agent(config))
        
        # Check result
        self.assertFalse(result)
        
        # Check client initialization
        mock_client_class.assert_called_once_with(config['server'])
        mock_client.connect.assert_called_once()
        
        # Check connection status update
        self.assertFalse(self.agent_controller.connected)
        
        # Check signal emissions
        self.agent_controller.error_occurred.emit.assert_called_once_with("Failed to connect to MCP server: Connection failed")
        self.agent_controller.connection_status_changed.emit.assert_called_once_with(False, None)
        
        # Check feedback controller calls
        self.mock_feedback_controller.start_progress.assert_called_once_with(
            "Initializing agent...",
            ProgressType.INDETERMINATE
        )
        self.mock_feedback_controller.update_progress.assert_called_once_with(
            "test-op-id",
            message="Connecting to MCP server..."
        )
        self.mock_feedback_controller.complete_progress.assert_called_once_with(
            "test-op-id",
            success=False,
            message="Failed to connect to MCP server: Connection failed",
            notification=True
        )
    
    def test_process_message_agent_not_initialized(self):
        """Test processing message when agent is not initialized."""
        # Process message
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.agent_controller.process_message("Test message"))
        
        # Check result
        self.assertIn("Agent not initialized", result)
        
        # Check signal emissions
        self.agent_controller.error_occurred.emit.assert_called_once_with("Agent not initialized")
        
        # Check feedback controller calls
        self.mock_feedback_controller.show_notification.assert_called_once_with(
            "Agent not initialized",
            NotificationType.ERROR,
            5000
        )
    
    @patch('mcp_agent.ui.controllers.agent_controller.MCPAgent')
    def test_process_message_success(self, mock_agent_class):
        """Test processing message successfully."""
        # Create mock agent
        mock_agent = AsyncMock()
        mock_agent.process_message.return_value = "Test response"
        mock_agent_class.return_value = mock_agent
        
        # Set agent
        self.agent_controller.agent = mock_agent
        
        # Mock start_progress
        self.mock_feedback_controller.start_progress.return_value = "test-op-id"
        
        # Process message
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.agent_controller.process_message("Test message"))
        
        # Check result
        self.assertEqual(result, "Test response")
        
        # Check agent call
        mock_agent.process_message.assert_called_once_with("Test message")
        
        # Check signal emissions
        self.agent_controller.message_processed.emit.assert_called_once_with("Test response")
        
        # Check feedback controller calls
        self.mock_feedback_controller.start_progress.assert_called_once_with(
            "Processing message...",
            ProgressType.INDETERMINATE
        )
        self.mock_feedback_controller.show_status_message.assert_any_call("Processing message...")
        self.mock_feedback_controller.complete_progress.assert_called_once_with(
            "test-op-id",
            success=True,
            message="Message processed",
            notification=False
        )
        self.mock_feedback_controller.show_status_message.assert_any_call("Ready", 3000)
    
    @patch('mcp_agent.ui.controllers.agent_controller.MCPAgent')
    def test_process_message_tool_error(self, mock_agent_class):
        """Test processing message with tool error."""
        # Create mock agent that raises tool error
        mock_agent = AsyncMock()
        mock_agent.process_message.side_effect = MCPToolError("Tool failed")
        mock_agent_class.return_value = mock_agent
        
        # Set agent
        self.agent_controller.agent = mock_agent
        
        # Mock start_progress
        self.mock_feedback_controller.start_progress.return_value = "test-op-id"
        
        # Process message
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.agent_controller.process_message("Test message"))
        
        # Check result
        self.assertIn("Tool error: Tool failed", result)
        
        # Check agent call
        mock_agent.process_message.assert_called_once_with("Test message")
        
        # Check signal emissions
        self.agent_controller.error_occurred.emit.assert_called_once_with("Tool error: Tool failed")
        
        # Check feedback controller calls
        self.mock_feedback_controller.start_progress.assert_called_once_with(
            "Processing message...",
            ProgressType.INDETERMINATE
        )
        self.mock_feedback_controller.show_status_message.assert_called_once_with("Processing message...")
        self.mock_feedback_controller.complete_progress.assert_called_once_with(
            "test-op-id",
            success=False,
            message="Tool error: Tool failed",
            notification=True
        )
    
    @patch('mcp_agent.ui.controllers.agent_controller.MCPClient')
    def test_disconnect(self, mock_client_class):
        """Test disconnecting from MCP server."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Set client
        self.agent_controller.mcp_client = mock_client
        self.agent_controller.connected = True
        
        # Mock start_progress
        self.mock_feedback_controller.start_progress.return_value = "test-op-id"
        
        # Disconnect
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.agent_controller.disconnect())
        
        # Check client call
        mock_client.disconnect.assert_called_once()
        
        # Check connection status update
        self.assertFalse(self.agent_controller.connected)
        self.assertIsNone(self.agent_controller.mcp_client)
        self.assertIsNone(self.agent_controller.agent)
        
        # Check signal emissions
        self.agent_controller.connection_status_changed.emit.assert_called_once_with(False, None)
        
        # Check feedback controller calls
        self.mock_feedback_controller.start_progress.assert_called_once_with(
            "Disconnecting...",
            ProgressType.INDETERMINATE
        )
        self.mock_feedback_controller.complete_progress.assert_called_once_with(
            "test-op-id",
            success=True,
            message="Disconnected",
            notification=False
        )
    
    @patch('mcp_agent.ui.controllers.agent_controller.MCPClient')
    def test_refresh_tools_and_resources_success(self, mock_client_class):
        """Test refreshing tools and resources successfully."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.tools = {'tool1': MagicMock(), 'tool2': MagicMock()}
        mock_client.resources = {'resource1': MagicMock(), 'resource2': MagicMock()}
        
        # Set client
        self.agent_controller.mcp_client = mock_client
        
        # Mock start_progress
        self.mock_feedback_controller.start_progress.return_value = "test-op-id"
        
        # Refresh tools and resources
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.agent_controller.refresh_tools_and_resources())
        
        # Check client calls
        mock_client._discover_tools.assert_called_once()
        mock_client._discover_resources.assert_called_once()
        
        # Check signal emissions
        self.agent_controller.tools_updated.emit.assert_called_once_with(mock_client.tools)
        self.agent_controller.resources_updated.emit.assert_called_once_with(mock_client.resources)
        
        # Check feedback controller calls
        self.mock_feedback_controller.start_progress.assert_called_once_with(
            "Refreshing tools and resources...",
            ProgressType.INDETERMINATE
        )
        self.mock_feedback_controller.complete_progress.assert_called_once_with(
            "test-op-id",
            success=True,
            message="Tools and resources refreshed",
            notification=True
        )
    
    def test_refresh_tools_and_resources_not_connected(self):
        """Test refreshing tools and resources when not connected."""
        # Ensure client is None
        self.agent_controller.mcp_client = None
        
        # Refresh tools and resources
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.agent_controller.refresh_tools_and_resources())
        
        # Check signal emissions
        self.agent_controller.error_occurred.emit.assert_called_once_with("Not connected to MCP server")
        
        # Check feedback controller calls
        self.mock_feedback_controller.show_notification.assert_called_once_with(
            "Not connected to MCP server",
            NotificationType.ERROR,
            5000
        )


if __name__ == '__main__':
    unittest.main()