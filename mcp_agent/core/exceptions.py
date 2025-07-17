"""Custom exceptions for MCP Agent"""


class MCPError(Exception):
    """Base exception for MCP-related errors"""
    pass


class MCPConnectionError(MCPError):
    """Raised when connection to MCP server fails"""
    pass


class MCPToolError(MCPError):
    """Raised when tool execution fails"""
    pass