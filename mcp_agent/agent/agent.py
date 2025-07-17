"""Main agent that coordinates between LLM and MCP server"""

from typing import Dict, List

from ..llm.base import LLMProvider
from ..mcp.client import MCPClient


class MCPAgent:
    """Main agent that coordinates between LLM and MCP server"""
    
    def __init__(self, llm_provider: LLMProvider, mcp_client: MCPClient):
        self.llm_provider = llm_provider
        self.mcp_client = mcp_client
        self.conversation_history: List[Dict[str, str]] = []
    
    async def start(self):
        """Start the agent"""
        await self.mcp_client.connect()
        
        # Add system message about available tools
        tools_info = self._get_tools_info()
        system_message = f"""You are an AI assistant with access to the following tools via MCP:

{tools_info}

You can use these tools to help the user accomplish their tasks. When you need to use a tool, I will call it for you and provide the results.
"""
        
        self.conversation_history.append({
            "role": "system",
            "content": system_message
        })
        
        print("🤖 MCP Agent started! Type 'quit' to exit.")
        print(f"📋 Available tools: {', '.join(self.mcp_client.tools.keys())}")
        print()
    
    def _get_tools_info(self) -> str:
        """Get formatted information about available tools"""
        if not self.mcp_client.tools:
            return "No tools available."
        
        tools_info = []
        for tool in self.mcp_client.tools.values():
            tools_info.append(f"- {tool.name}: {tool.description}")
        
        return "\n".join(tools_info)
    
    async def process_message(self, user_input: str) -> str:
        """Process a user message and return response"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Check if LLM wants to use a tool
        tool_call = await self.llm_provider.generate_tool_call(
            self.conversation_history,
            list(self.mcp_client.tools.values())
        )
        
        if tool_call and "tool_name" in tool_call:
            # Execute the tool call
            tool_name = tool_call["tool_name"]
            arguments = tool_call.get("arguments", {})
            
            try:
                tool_result = await self.mcp_client.call_tool(tool_name, arguments)
                
                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"I used the {tool_name} tool with arguments: {arguments}"
                })
                
                self.conversation_history.append({
                    "role": "user",
                    "content": f"Tool result: {tool_result}"
                })
                
                # Generate final response
                response = await self.llm_provider.generate_response(self.conversation_history)
                
            except Exception as e:
                response = f"Error using tool {tool_name}: {str(e)}"
        else:
            # Generate direct response
            response = await self.llm_provider.generate_response(self.conversation_history)
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    async def run_interactive(self):
        """Run the agent in interactive mode"""
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Assistant: ", end="", flush=True)
                response = await self.process_message(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
    
    async def cleanup(self):
        """Clean up resources"""
        await self.mcp_client.disconnect()