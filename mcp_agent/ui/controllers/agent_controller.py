"""
Agent Controller for MCP Agent.

This module provides the controller for managing the MCP Agent instance.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from mcp_agent.agent.agent import MCPAgent
from mcp_agent.llm.base import LLMProvider
from mcp_agent.mcp.client import MCPClient
from mcp_agent.core.exceptions import MCPConnectionError, MCPToolError
from mcp_agent.ui.components.notification import NotificationType
from mcp_agent.ui.components.feedback_manager import ProgressType

class AgentController(QObject):
    """Controller for managing the MCP Agent instance."""
    
    message_processed = pyqtSignal(str)
    tool_called = pyqtSignal(str, dict, object)
    error_occurred = pyqtSignal(str)
    
    # Signals for tools panel
    tools_updated = pyqtSignal(dict)
    resources_updated = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(bool, str)
    
    # Signal for model information
    model_info_updated = pyqtSignal(str, str)  # provider_name, model_name
    
    def __init__(self):
        """Initialize the agent controller."""
        super().__init__()
        self.agent = None
        self.llm_provider = None
        self.mcp_client = None
        self.connected = False
        self.server_name = None
        self.model_name = None
        self.provider_name = None
        self.feedback_controller = None
        
    def set_feedback_controller(self, feedback_controller):
        """Set the feedback controller.
        
        Args:
            feedback_controller: The feedback controller.
        """
        self.feedback_controller = feedback_controller
        
    async def initialize_agent(self, config):
        """Initialize agent with configuration.
        
        Args:
            config (dict): The configuration for the agent.
            
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        # Start progress operation if feedback controller is available
        operation_id = None
        if self.feedback_controller:
            operation_id = self.feedback_controller.start_progress(
                "Initializing agent...",
                ProgressType.INDETERMINATE
            )
        
        try:
            # Update progress
            if self.feedback_controller and operation_id:
                self.feedback_controller.update_progress(
                    operation_id,
                    message="Connecting to MCP server..."
                )
            
            # Get server configuration
            server_config = config.get('server', {})
            self.server_name = server_config.get('name', 'Unknown')
            
            # Initialize MCP client
            self.mcp_client = MCPClient(server_config)
            await self.mcp_client.connect()
            
            # Update progress
            if self.feedback_controller and operation_id:
                self.feedback_controller.update_progress(
                    operation_id,
                    message="Initializing LLM provider..."
                )
            
            # Initialize LLM provider
            llm_config = config.get('llm', {})
            llm_type = llm_config.get('type', 'openai')
            
            if llm_type == 'openai':
                from mcp_agent.llm.openai import OpenAIProvider
                self.llm_provider = OpenAIProvider(llm_config)
                self.provider_name = "OpenAI"
            elif llm_type == 'anthropic':
                from mcp_agent.llm.anthropic import AnthropicProvider
                self.llm_provider = AnthropicProvider(llm_config)
                self.provider_name = "Anthropic"
            else:
                raise ValueError(f"Unsupported LLM provider: {llm_type}")
            
            # Get model name
            self.model_name = llm_config.get('model', 'Unknown')
            
            # Update progress
            if self.feedback_controller and operation_id:
                self.feedback_controller.update_progress(
                    operation_id,
                    message="Creating agent..."
                )
            
            # Initialize agent
            self.agent = MCPAgent(self.llm_provider, self.mcp_client)
            
            # Update connection status
            self.connected = True
            self.connection_status_changed.emit(True, self.server_name)
            self.model_info_updated.emit(self.provider_name, self.model_name)
            
            # Emit signals for tools and resources
            self.tools_updated.emit(self.mcp_client.tools)
            self.resources_updated.emit(self.mcp_client.resources)
            
            # Complete progress operation
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=True,
                    message=f"Connected to {self.server_name} with {self.provider_name} ({self.model_name})",
                    notification=True
                )
            
            return True
            
        except MCPConnectionError as e:
            logging.error(f"Failed to connect to MCP server: {e}")
            self.error_occurred.emit(f"Failed to connect to MCP server: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Failed to connect to MCP server: {e}",
                    notification=True
                )
            
            return False
        except ValueError as e:
            logging.error(f"Invalid configuration: {e}")
            self.error_occurred.emit(f"Invalid configuration: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Invalid configuration: {e}",
                    notification=True
                )
            
            return False
        except Exception as e:
            logging.error(f"Failed to initialize agent: {e}")
            self.error_occurred.emit(f"Failed to initialize agent: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Failed to initialize agent: {e}",
                    notification=True
                )
            
            return False
        
    async def process_message(self, message):
        """Process message with agent and return response.
        
        Args:
            message (str): The user message to process.
            
        Returns:
            str: The assistant's response.
        """
        if not self.agent:
            error_msg = "Agent not initialized. Please check your configuration and try again."
            self.error_occurred.emit("Agent not initialized")
            
            # Show notification if feedback controller is available
            if self.feedback_controller:
                self.feedback_controller.show_notification(
                    "Agent not initialized",
                    NotificationType.ERROR,
                    5000
                )
            
            return error_msg
        
        # Start progress operation if feedback controller is available
        operation_id = None
        if self.feedback_controller:
            operation_id = self.feedback_controller.start_progress(
                "Processing message...",
                ProgressType.INDETERMINATE
            )
            
        try:
            # Update status message
            if self.feedback_controller:
                self.feedback_controller.show_status_message("Processing message...")
            
            # Process message
            response = await self.agent.process_message(message)
            
            # Emit signal
            self.message_processed.emit(response)
            
            # Complete progress operation
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=True,
                    message="Message processed",
                    notification=False
                )
                
                # Update status message
                self.feedback_controller.show_status_message("Ready", 3000)
            
            return response
        except MCPConnectionError as e:
            logging.error(f"Connection error while processing message: {e}")
            self.error_occurred.emit(f"Connection error: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Connection error: {e}",
                    notification=True
                )
            
            return f"Connection error: {e}. Please check your connection and try again."
        except MCPToolError as e:
            logging.error(f"Tool error while processing message: {e}")
            self.error_occurred.emit(f"Tool error: {e}")
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Tool error: {e}",
                    notification=True
                )
            
            return f"Tool error: {e}. Please try a different approach."
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            self.error_occurred.emit(f"Error processing message: {e}")
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Error processing message: {e}",
                    notification=True
                )
            
            return f"Error processing message: {e}"
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        # Start progress operation if feedback controller is available
        operation_id = None
        if self.feedback_controller:
            operation_id = self.feedback_controller.start_progress(
                "Disconnecting...",
                ProgressType.INDETERMINATE
            )
        
        try:
            if self.mcp_client:
                await self.mcp_client.disconnect()
                
            self.connected = False
            self.connection_status_changed.emit(False, None)
            self.mcp_client = None
            self.agent = None
            
            # Complete progress operation
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=True,
                    message="Disconnected",
                    notification=False
                )
        except Exception as e:
            logging.error(f"Error disconnecting from MCP server: {e}")
            self.error_occurred.emit(f"Error disconnecting from MCP server: {e}")
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Error disconnecting: {e}",
                    notification=True
                )
        
    def get_tools(self):
        """Get the available tools.
        
        Returns:
            dict: Dictionary of tool name -> MCPTool objects.
        """
        if self.mcp_client:
            return self.mcp_client.tools
        return {}
        
    def get_resources(self):
        """Get the available resources.
        
        Returns:
            dict: Dictionary of resource URI -> MCPResource objects.
        """
        if self.mcp_client:
            return self.mcp_client.resources
        return {}
        
    async def refresh_tools_and_resources(self):
        """Refresh the tools and resources from the MCP server."""
        if not self.mcp_client:
            self.error_occurred.emit("Not connected to MCP server")
            
            # Show notification if feedback controller is available
            if self.feedback_controller:
                self.feedback_controller.show_notification(
                    "Not connected to MCP server",
                    NotificationType.ERROR,
                    5000
                )
            
            return
        
        # Start progress operation if feedback controller is available
        operation_id = None
        if self.feedback_controller:
            operation_id = self.feedback_controller.start_progress(
                "Refreshing tools and resources...",
                ProgressType.INDETERMINATE
            )
            
        try:
            # Discover tools and resources
            await self.mcp_client._discover_tools()
            await self.mcp_client._discover_resources()
            
            # Emit signals for tools and resources
            self.tools_updated.emit(self.mcp_client.tools)
            self.resources_updated.emit(self.mcp_client.resources)
            
            # Complete progress operation
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=True,
                    message="Tools and resources refreshed",
                    notification=True
                )
            
        except MCPConnectionError as e:
            logging.error(f"Error refreshing tools and resources: {e}")
            self.error_occurred.emit(f"Error refreshing tools and resources: {e}")
            
            # Update connection status if connection was lost
            self.connected = False
            self.connection_status_changed.emit(False, None)
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Error refreshing tools and resources: {e}",
                    notification=True
                )
        except Exception as e:
            logging.error(f"Unexpected error refreshing tools and resources: {e}")
            self.error_occurred.emit(f"Unexpected error refreshing tools and resources: {e}")
            
            # Complete progress operation with error
            if self.feedback_controller and operation_id:
                self.feedback_controller.complete_progress(
                    operation_id,
                    success=False,
                    message=f"Unexpected error refreshing tools and resources: {e}",
                    notification=True
                )
            
            # Don't update connection status for non-connection errors
            # as the connection might still be valid