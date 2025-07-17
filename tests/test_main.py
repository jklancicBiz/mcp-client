"""
Tests for the main application entry point.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
import argparse

# Import the functions from main.py
from main import parse_args, setup_logging, run_gui_mode, run_cli_mode

class TestMainEntryPoint(unittest.TestCase):
    """Test cases for the main application entry point."""
    
    def test_parse_args_default(self):
        """Test parsing command line arguments with default values."""
        with patch('sys.argv', ['main.py']):
            args = parse_args()
            self.assertFalse(args.gui)
            self.assertIsNone(args.config)
            self.assertFalse(args.verbose)
            self.assertIsNone(args.server)
            self.assertIsNone(args.llm)
            self.assertIsNone(args.model)
    
    def test_parse_args_gui_mode(self):
        """Test parsing command line arguments with GUI mode."""
        with patch('sys.argv', ['main.py', '--gui']):
            args = parse_args()
            self.assertTrue(args.gui)
    
    def test_parse_args_cli_options(self):
        """Test parsing command line arguments with CLI options."""
        with patch('sys.argv', ['main.py', '--server', 'test-server', 
                               '--llm', 'openai', '--model', 'gpt-4', 
                               '--config', 'test-config.yaml', '--verbose']):
            args = parse_args()
            self.assertEqual(args.server, 'test-server')
            self.assertEqual(args.llm, 'openai')
            self.assertEqual(args.model, 'gpt-4')
            self.assertEqual(args.config, 'test-config.yaml')
            self.assertTrue(args.verbose)
    
    @patch('logging.basicConfig')
    def test_setup_logging_default(self, mock_logging_config):
        """Test setting up logging with default values."""
        setup_logging(False)
        mock_logging_config.assert_called_once()
        # Check that INFO level was used
        self.assertEqual(mock_logging_config.call_args[1]['level'], 20)  # 20 is logging.INFO
    
    @patch('logging.basicConfig')
    def test_setup_logging_verbose(self, mock_logging_config):
        """Test setting up logging with verbose flag."""
        setup_logging(True)
        mock_logging_config.assert_called_once()
        # Check that DEBUG level was used
        self.assertEqual(mock_logging_config.call_args[1]['level'], 10)  # 10 is logging.DEBUG
    
    @patch('mcp_agent.ui.app.MCPAgentApp')
    def test_run_gui_mode_success(self, mock_app_class):
        """Test running GUI mode successfully."""
        # Setup mock
        mock_app = MagicMock()
        mock_app.run.return_value = 0
        mock_app_class.return_value = mock_app
        
        # Create args
        args = argparse.Namespace(config='test-config.yaml', verbose=True)
        
        # Run function
        result = run_gui_mode(args)
        
        # Verify
        mock_app_class.assert_called_once_with(args)
        mock_app.run.assert_called_once()
        self.assertEqual(result, 0)
    
    @patch('mcp_agent.ui.app.MCPAgentApp')
    def test_run_gui_mode_error(self, mock_app_class):
        """Test running GUI mode with an error."""
        # Setup mock to raise an exception
        mock_app_class.side_effect = Exception("Test error")
        
        # Create args
        args = argparse.Namespace(config='test-config.yaml', verbose=True)
        
        # Run function
        result = run_gui_mode(args)
        
        # Verify
        self.assertEqual(result, 1)
    
    def test_run_cli_mode_success(self):
        """Test running CLI mode successfully."""
        # Create args
        args = argparse.Namespace(config='test-config.yaml', verbose=True)
        
        # Mock asyncio.run and cli_main
        with patch('asyncio.run') as mock_asyncio_run:
            # Run function
            result = run_cli_mode(args)
            
            # Verify
            mock_asyncio_run.assert_called_once()
            self.assertEqual(result, 0)
    
    def test_run_cli_mode_error(self):
        """Test running CLI mode with an error."""
        # Create args
        args = argparse.Namespace(config='test-config.yaml', verbose=True)
        
        # Mock asyncio.run to raise an exception
        with patch('asyncio.run', side_effect=Exception("Test error")):
            # Run function
            result = run_cli_mode(args)
            
            # Verify
            self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()