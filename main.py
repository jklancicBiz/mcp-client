#!/usr/bin/env python3
"""
Entry point for MCP Agent

This script serves as the main entry point for the MCP Agent application.
It supports both CLI and GUI modes.
"""

import sys
import os
import asyncio
import argparse
import logging
from mcp_agent.cli.main import main as cli_main

def parse_args():
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="MCP Agent - Connect to MCP servers with different LLMs")
    
    # Interface mode selection
    interface_group = parser.add_argument_group("Interface Mode")
    interface_group.add_argument("--gui", action="store_true", help="Run in GUI mode (default: CLI mode)")
    
    # Common arguments
    common_group = parser.add_argument_group("Common Options")
    common_group.add_argument("--config", help="Path to configuration file")
    common_group.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    # CLI-specific arguments
    cli_group = parser.add_argument_group("CLI Options")
    cli_group.add_argument("--server", help="MCP server to connect to")
    cli_group.add_argument("--llm", choices=["openai", "anthropic"], help="LLM provider to use")
    cli_group.add_argument("--model", help="LLM model to use")
    
    return parser.parse_args()

def setup_logging(verbose=False):
    """Set up logging configuration.
    
    Args:
        verbose (bool): Whether to enable verbose logging.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def run_gui_mode(args):
    """Run the application in GUI mode.
    
    Args:
        args (argparse.Namespace): Command line arguments.
        
    Returns:
        int: Exit code.
    """
    try:
        # Import GUI modules only when needed to avoid unnecessary dependencies
        from mcp_agent.ui.app import MCPAgentApp
        
        # Create and run the GUI application
        app = MCPAgentApp(args)
        return app.run()
    except ImportError as e:
        logging.error(f"Failed to import GUI modules: {e}")
        print(f"❌ Error: GUI dependencies not installed. Please install PyQt6 to use the GUI mode.")
        print(f"   You can install it with: pip install PyQt6")
        return 1
    except Exception as e:
        logging.error(f"Failed to start GUI: {e}")
        print(f"❌ Error starting GUI: {e}")
        return 1

def run_cli_mode(args):
    """Run the application in CLI mode.
    
    Args:
        args (argparse.Namespace): Command line arguments.
        
    Returns:
        int: Exit code.
    """
    try:
        asyncio.run(cli_main())
        return 0
    except Exception as e:
        logging.error(f"Failed to run CLI: {e}")
        print(f"❌ Error running CLI: {e}")
        return 1

if __name__ == "__main__":
    args = parse_args()
    setup_logging(args.verbose)
    
    if args.gui:
        # Run in GUI mode
        logging.info("Starting MCP Agent in GUI mode")
        sys.exit(run_gui_mode(args))
    else:
        # Run in CLI mode
        logging.info("Starting MCP Agent in CLI mode")
        sys.exit(run_cli_mode(args))