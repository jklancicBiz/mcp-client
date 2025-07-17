"""
Agent Controller for MCP Agent.

This module provides the controller for managing the MCP Agent instance.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from mcp_agent.agent.agent import MCPAgent
from mcp_agent.llm.base import LLMProvider
from mcp_agent.mcp.client import MCPClient
from mcp_agent.core.exceptions import MCPConnectionError

class AgentController(QObject):
    """Controller for managing the MCP Agent instance."""
    
    message_processed = pyqtSignal(str)
    tool_called = pyqtSignal(str, dict, object)
    error_occurred = pyqtSignal(str)
    
    # Signals for tools panel
    tools_updated = pyqtSignal(dict)
    resources_updated = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(bool, str)
    
    def __init__(self):
        """Initialize the agent controller."""
        super().__init__()
        self.agent = None
        self.llm_provider = None
        self.mcp_client = None
        self.connected = False
        self.server_name = None
        
    async def initialize_agent(self, config):
        """Initialize agent with configuration.
        
        Args:
            config (dict): The configuration for the agent.
            
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Get server configuration
            server_config = config.get('server', {})
            self.server_name = server_config.get('name', 'Unknown')
            
            # Initialize MCP client
            self.mcp_client = MCPClient(server_config)
            await self.mcp_client.connect()
            
            # Initialize LLM provider
            llm_config = config.get('llm', {})
            llm_type = llm_config.get('type', 'openai')
            
            if llm_type == 'openai':
                from mcp_agent.llm.openai import OpenAIProvider
                self.llm_provider = OpenAIProvider(llm_config)
            elif llm_type == 'anthropic':
                from mcp_agent.llm.anthropic import AnthropicProvider
                self.llm_provider = AnthropicProvider(llm_config)
            else:
                raise ValueError(f"Unsupported LLM provider: {llm_type}")
            
            # Initialize agent
            self.agent = MCPAgent(self.llm_provider, self.mcp_client)
            
            # Update connection status
            self.connected = True
            self.connection_status_changed.emit(True, self.server_name)
            
            # Emit signals for tools and resources
            self.tools_updated.emit(self.mcp_client.tools)
            self.resources_updated.emit(self.mcp_client.resources)
            
            return True
            
        except MCPConnectionError as e:
            logging.error(f"Failed to connect to MCP server: {e}")
            self.error_occurred.emit(f"Failed to connect to MCP server: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            return False
        except ValueError as e:
            logging.error(f"Invalid configuration: {e}")
            self.error_occurred.emit(f"Invalid configuration: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            return False
        except Exception as e:
            logging.error(f"Failed to initialize agent: {e}")
            self.error_occurred.emit(f"Failed to initialize agent: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            return False
        
    async def process_message(self, message):
        """Process message with agent and return response.
        
        Args:
            message (str): The user message to process.
            
        Returns:
            str: The assistant's response.
        """
        if not self.agent:
            self.error_occurred.emit("Agent not initialized")
            return "Agent not initialized. Please check your configuration and try again."
            
        try:
            response = await self.agent.process_message(message)
            self.message_processed.emit(response)
            return response
        except MCPConnectionError as e:
            logging.error(f"Connection error while processing message: {e}")
            self.error_occurred.emit(f"Connection error: {e}")
            self.connected = False
            self.connection_status_changed.emit(False, None)
            return f"Connection error: {e}. Please check your connection and try again."
        except MCPToolError as e:
            logging.error(f"Tool error while processing message: {e}")
            self.error_occurred.emit(f"Tool error: {e}")
            return f"Tool error: {e}. Please try a different approach."
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            self.error_occurred.emit(f"Error processing message: {e}")
            return f"Error processing message: {e}"
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.mcp_client:
            try:
                await self.mcp_client.disconnect()
            except Exception as e:
                logging.error(f"Error disconnecting from MCP server: {e}")
                self.error_occurred.emit(f"Error disconnecting from MCP server: {e}")
                
        self.connected = False
        self.connection_status_changed.emit(False, None)
        self.mcp_client = None
        self.agent = None
        
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
            return
            
        try:
            # Discover tools and resources
            await self.mcp_client._discover_tools()
            await self.mcp_client._discover_resources()
            
            # Emit signals for tools and resources
            self.tools_updated.emit(self.mcp_client.tools)
            self.resources_updated.emit(self.mcp_client.resources)
            
        except MCPConnectionError as e:
            logging.error(f"Error refreshing tools and resources: {e}")
            self.error_occurred.emit(f"Error refreshing tools and resources: {e}")
            
            # Update connection status if connection was lost
            self.connected = False
            self.connection_status_changed.emit(False, None)
        except Exception as e:
            logging.error(f"Unexpected error refreshing tools and resources: {e}")
            self.error_occurred.emit(f"Unexpected error refreshing tools and resources: {e}")
            
            # Don't update connection status for non-connection errors
            # as the connection might still be valid