"""CLI interface and main entry point"""

import argparse
import asyncio
import logging
import os
import sys

from ..agent.agent import MCPAgent
from ..mcp.client import MCPClient
from ..llm.openai import OpenAIProvider
from ..llm.anthropic import AnthropicProvider
from ..config.manager import ConfigManager


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP Agent - Connect to MCP servers with different LLMs")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--server", help="MCP server to connect to")
    parser.add_argument("--llm", choices=["openai", "anthropic"], help="LLM provider to use")
    parser.add_argument("--model", help="Model name to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--gui", action="store_true", help="Launch with graphical user interface")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Load configuration
        config_manager = ConfigManager(args.config)
        
        # Get LLM configuration
        llm_config = config_manager.get_llm_config()
        llm_provider_name = args.llm or llm_config.get("provider", "openai")
        model_name = args.model or llm_config.get("model", "gpt-4")
        
        # Create LLM provider
        if llm_provider_name == "openai":
            api_key = llm_config.get("api_key") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable or add it to config.")
                return
            llm_provider = OpenAIProvider(api_key, model_name)
        elif llm_provider_name == "anthropic":
            api_key = llm_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("❌ Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable or add it to config.")
                return
            llm_provider = AnthropicProvider(api_key, model_name)
        else:
            print(f"❌ Unknown LLM provider: {llm_provider_name}")
            return
        
        # Get MCP server configuration
        server_name = args.server or config_manager.get_default_server()
        server_config = config_manager.get_mcp_server_config(server_name)
        
        if not server_config:
            print(f"❌ MCP server '{server_name}' not found in configuration.")
            return
        
        # Create MCP client
        mcp_client = MCPClient(server_config)
        
        # Create and start agent
        agent = MCPAgent(llm_provider, mcp_client)
        
        print(f"🚀 Starting MCP Agent with {llm_provider_name} ({model_name}) and server '{server_name}'")
        
        await agent.start()
        await agent.run_interactive()
        
    except Exception as e:
        logging.error(f"Failed to start agent: {e}")
        print(f"❌ Error: {e}")
    finally:
        if 'agent' in locals():
            await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())