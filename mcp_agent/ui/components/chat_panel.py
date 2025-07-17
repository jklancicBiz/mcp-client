"""
Chat Panel component for MCP Agent.

This module provides the chat panel for the MCP Agent GUI.
"""

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QPushButton,
    QLabel, QProgressBar, QScrollArea,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QTextCursor, QFont, QIcon

class ChatPanel(QWidget):
    """Chat panel for the MCP Agent GUI."""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, controller):
        """Initialize the chat panel.
        
        Args:
            controller: The UI controller.
        """
        super().__init__()
        self.controller = controller
        self.is_processing = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Set default font
        font = QFont("Segoe UI", 10)
        self.chat_display.setFont(font)
        
        layout.addWidget(self.chat_display)
        
        # Create loading indicator
        self.loading_frame = QFrame()
        loading_layout = QHBoxLayout()
        self.loading_frame.setLayout(loading_layout)
        self.loading_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        
        self.loading_label = QLabel("Processing...")
        self.loading_progress = QProgressBar()
        self.loading_progress.setRange(0, 0)  # Indeterminate progress
        self.loading_progress.setFixedHeight(10)
        self.loading_progress.setTextVisible(False)
        
        loading_layout.addWidget(self.loading_label)
        loading_layout.addWidget(self.loading_progress, 1)
        
        self.loading_frame.setVisible(False)
        layout.addWidget(self.loading_frame)
        
        # Create input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #004e8c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
    def send_message(self):
        """Send the current message."""
        message = self.input_field.text().strip()
        if message and not self.is_processing:
            self.add_user_message(message)
            self.message_sent.emit(message)
            self.input_field.clear()
            self.set_processing(True)
            
    def set_processing(self, is_processing):
        """Set the processing state.
        
        Args:
            is_processing (bool): Whether the agent is processing a message.
        """
        self.is_processing = is_processing
        self.loading_frame.setVisible(is_processing)
        self.loading_frame.setHidden(not is_processing)  # Explicitly set hidden state
        self.input_field.setEnabled(not is_processing)
        self.send_button.setEnabled(not is_processing)
        
        if is_processing:
            self.input_field.setPlaceholderText("Waiting for response...")
        else:
            self.input_field.setPlaceholderText("Type a message...")
            
    def add_user_message(self, message):
        """Add a user message to the chat display.
        
        Args:
            message (str): The message to add.
        """
        html = f"""
        <div style="margin: 10px 0; text-align: right;">
            <div style="display: inline-block; background-color: #dcf8c6; 
                        border-radius: 10px; padding: 10px; max-width: 80%; 
                        text-align: left;">
                <span style="font-weight: bold;">You</span><br>
                {self._format_message_content(message)}
            </div>
        </div>
        """
        self._append_html(html)
        
    def add_assistant_message(self, message):
        """Add an assistant message to the chat display.
        
        Args:
            message (str): The message to add.
        """
        html = f"""
        <div style="margin: 10px 0;">
            <div style="display: inline-block; background-color: #f1f0f0; 
                        border-radius: 10px; padding: 10px; max-width: 80%;">
                <span style="font-weight: bold;">Assistant</span><br>
                {self._format_message_content(message)}
            </div>
        </div>
        """
        self._append_html(html)
        self.set_processing(False)
        
    def add_tool_call(self, tool_name, arguments, result):
        """Add a tool call to the chat display.
        
        Args:
            tool_name (str): The name of the tool.
            arguments (dict): The arguments passed to the tool.
            result: The result of the tool call.
        """
        # Format arguments and result as JSON
        formatted_args = self._format_json(arguments)
        formatted_result = self._format_json(result)
        
        html = f"""
        <div style="margin: 10px 0;">
            <div style="display: inline-block; background-color: #e3f2fd; 
                        border-radius: 10px; padding: 10px; max-width: 80%;">
                <span style="font-weight: bold;">🔧 Tool: {tool_name}</span><br>
                <div style="margin-top: 5px;">
                    <span style="font-weight: bold;">Arguments:</span><br>
                    <pre style="background-color: #f8f9fa; padding: 5px; 
                                border-radius: 5px; overflow-x: auto; 
                                font-family: monospace;">{formatted_args}</pre>
                </div>
                <div style="margin-top: 5px;">
                    <span style="font-weight: bold;">Result:</span><br>
                    <pre style="background-color: #f8f9fa; padding: 5px; 
                                border-radius: 5px; overflow-x: auto; 
                                font-family: monospace;">{formatted_result}</pre>
                </div>
            </div>
        </div>
        """
        self._append_html(html)
        
    def _format_message_content(self, content):
        """Format message content with Markdown-like styling.
        
        Args:
            content (str): The message content to format.
            
        Returns:
            str: The formatted message content.
        """
        # Replace newlines with <br>
        content = content.replace('\n', '<br>')
        
        # Simple code block formatting
        content = self._format_code_blocks(content)
        
        return content
        
    def _format_code_blocks(self, content):
        """Format code blocks in the message content.
        
        Args:
            content (str): The message content to format.
            
        Returns:
            str: The formatted message content.
        """
        # This is a simple implementation that could be enhanced with a proper Markdown parser
        lines = content.split('<br>')
        in_code_block = False
        result = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End code block
                    result.append('</pre>')
                    in_code_block = False
                else:
                    # Start code block
                    result.append('<pre style="background-color: #f8f9fa; padding: 5px; border-radius: 5px; overflow-x: auto; font-family: monospace;">')
                    in_code_block = True
            else:
                result.append(line)
                
        # Close any open code block
        if in_code_block:
            result.append('</pre>')
            
        return '<br>'.join(result)
        
    def _format_json(self, data):
        """Format JSON data for display.
        
        Args:
            data: The data to format.
            
        Returns:
            str: The formatted JSON string.
        """
        try:
            if isinstance(data, str):
                # Try to parse as JSON if it's a string
                try:
                    data = json.loads(data)
                    return json.dumps(data, indent=2)
                except json.JSONDecodeError:
                    return data
            else:
                return json.dumps(data, indent=2)
        except Exception:
            # Fall back to string representation if JSON formatting fails
            return str(data)
            
    def _append_html(self, html):
        """Append HTML to the chat display and scroll to bottom.
        
        Args:
            html (str): The HTML to append.
        """
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(html)
        
        # Add a bit of spacing between messages
        self.chat_display.append("")
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
    def clear_chat(self):
        """Clear the chat display."""
        self.chat_display.clear()
        
    def enable_input(self):
        """Enable the input field and send button."""
        self.set_processing(False)
        
    def disable_input(self):
        """Disable the input field and send button."""
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)