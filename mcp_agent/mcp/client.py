"""MCP client for communicating with MCP servers"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

from ..core.models import MCPTool, MCPResource
from ..core.exceptions import MCPConnectionError, MCPToolError


class MCPClient:
    """Client for communicating with MCP servers"""
    
    def __init__(self, server_config: Dict[str, Any]):
        self.server_config = server_config
        self.process = None
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._request_id = 0
    
    def _next_request_id(self) -> int:
        """Get the next request ID"""
        self._request_id += 1
        return self._request_id
    
    def _build_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build a JSON-RPC request"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": method
        }
        
        if params is not None:
            request["params"] = params
            
        return request
        
    async def _send_jsonrpc_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server"""
        request = self._build_request(method, params)
        return await self._send_request(request)
    
    async def connect(self):
        """Connect to the MCP server"""
        try:
            # Start the MCP server process
            cmd = self.server_config.get('command', [])
            args = self.server_config.get('args', [])
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd, *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize the connection
            await self._send_jsonrpc_request(
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "clientInfo": {
                        "name": "mcp-agent",
                        "version": "1.0.0"
                    }
                }
            )
            
            # List available tools
            await self._discover_tools()
            
            # List available resources
            await self._discover_resources()
            
            logging.info(f"Connected to MCP server with {len(self.tools)} tools and {len(self.resources)} resources")
            
        except Exception as e:
            logging.error(f"Failed to connect to MCP server: {e}")
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response"""
        if not self.process:
            raise MCPConnectionError("Not connected to MCP server")
            
        # Send request
        request_str = json.dumps(request) + '\n'
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise MCPConnectionError("MCP server closed connection")
            
        response = json.loads(response_line.decode())
        
        if "error" in response:
            raise MCPConnectionError(f"MCP server error: {response['error']}")
            
        return response
    
    async def _discover_tools(self):
        """Discover available tools from the MCP server"""
        try:
            response = await self._send_jsonrpc_request(method="tools/list")
            
            for tool_info in response.get("result", {}).get("tools", []):
                tool = MCPTool(
                    name=tool_info["name"],
                    description=tool_info.get("description", ""),
                    input_schema=tool_info.get("inputSchema", {})
                )
                self.tools[tool.name] = tool
                
        except Exception as e:
            logging.warning(f"Failed to discover tools: {e}")
    
    async def _discover_resources(self):
        """Discover available resources from the MCP server"""
        try:
            response = await self._send_jsonrpc_request(method="resources/list")
            
            for resource_info in response.get("result", {}).get("resources", []):
                resource = MCPResource(
                    uri=resource_info["uri"],
                    name=resource_info.get("name", ""),
                    description=resource_info.get("description"),
                    mime_type=resource_info.get("mimeType")
                )
                self.resources[resource.uri] = resource
                
        except Exception as e:
            logging.warning(f"Failed to discover resources: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server"""
        if tool_name not in self.tools:
            raise MCPToolError(f"Tool '{tool_name}' not found")
            
        try:
            response = await self._send_jsonrpc_request(
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            
            return response.get("result", {}).get("content", [])
        except Exception as e:
            raise MCPToolError(f"Failed to call tool '{tool_name}': {e}")
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource from the MCP server"""
        try:
            response = await self._send_jsonrpc_request(
                method="resources/read",
                params={
                    "uri": uri
                }
            )
            
            contents = response.get("result", {}).get("contents", [])
            if contents:
                return contents[0].get("text", "")
            return ""
        except Exception as e:
            raise MCPToolError(f"Failed to read resource '{uri}': {e}")
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None