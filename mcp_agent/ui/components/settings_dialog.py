"""
Settings Dialog component for MCP Agent.

This module provides the settings dialog for configuring the MCP Agent.
"""

import os
import logging
from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QWidget, QLabel, QLineEdit, 
    QComboBox, QGroupBox, QFormLayout, QListWidget,
    QListWidgetItem, QMessageBox, QCheckBox, QSpinBox,
    QGridLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from mcp_agent.ui.models.ui_config import UIConfig

class SettingsDialog(QDialog):
    """Settings dialog for the MCP Agent GUI."""
    
    settings_updated = pyqtSignal(dict)  # Signal emitted when settings are saved
    
    def __init__(self, parent=None):
        """Initialize the settings dialog.
        
        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        
        # Initialize validation state
        self.validation_errors = {}
        
        # Initialize configuration
        self.config = {}
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.general_tab = self.create_general_tab()
        self.llm_tab = self.create_llm_tab()
        self.server_tab = self.create_server_tab()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.llm_tab, "LLM")
        self.tab_widget.addTab(self.server_tab, "MCP Servers")
        
        # Create error message area
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        main_layout.addWidget(self.error_label)
        
        # Create buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")
        self.save_button.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.validate_and_save)
        
    def create_general_tab(self):
        """Create the general settings tab.
        
        Returns:
            QWidget: The general settings tab.
        """
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # UI settings group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout()
        ui_group.setLayout(ui_layout)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        ui_layout.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Small", "Medium", "Large", "X-Large"])
        ui_layout.addRow("Font Size:", self.font_size_combo)
        
        # High DPI scaling
        self.high_dpi_check = QCheckBox("Enable High DPI Scaling")
        ui_layout.addRow("", self.high_dpi_check)
        
        layout.addWidget(ui_group)
        
        # Panel visibility group
        panel_group = QGroupBox("Panel Visibility")
        panel_layout = QFormLayout()
        panel_group.setLayout(panel_layout)
        
        # Tool panel visibility
        self.tool_panel_check = QCheckBox("Show Tools Panel")
        panel_layout.addRow("", self.tool_panel_check)
        
        # Status bar visibility
        self.status_bar_check = QCheckBox("Show Status Bar")
        panel_layout.addRow("", self.status_bar_check)
        
        layout.addWidget(panel_group)
        
        # Conversation settings group
        conv_group = QGroupBox("Conversation Settings")
        conv_layout = QFormLayout()
        conv_group.setLayout(conv_layout)
        
        # Conversation history limit
        self.history_limit_spin = QSpinBox()
        self.history_limit_spin.setRange(10, 1000)
        self.history_limit_spin.setSingleStep(10)
        conv_layout.addRow("History Limit:", self.history_limit_spin)
        
        # Default export format
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["JSON", "Text", "Markdown"])
        conv_layout.addRow("Export Format:", self.export_format_combo)
        
        layout.addWidget(conv_group)
        layout.addStretch()
        
        return tab
        
    def create_llm_tab(self):
        """Create the LLM settings tab.
        
        Returns:
            QWidget: The LLM settings tab.
        """
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # LLM provider group
        provider_group = QGroupBox("LLM Provider")
        provider_layout = QFormLayout()
        provider_group.setLayout(provider_layout)
        
        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic"])
        provider_layout.addRow("Provider:", self.provider_combo)
        
        # Model selection
        self.model_combo = QComboBox()
        self.update_model_options()
        provider_layout.addRow("Model:", self.model_combo)
        
        # API key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your API key")
        provider_layout.addRow("API Key:", self.api_key_edit)
        
        # API key environment variable
        env_var_layout = QHBoxLayout()
        self.api_key_env_check = QCheckBox("Use environment variable:")
        self.api_key_env_edit = QLineEdit()
        self.api_key_env_edit.setPlaceholderText("OPENAI_API_KEY")
        env_var_layout.addWidget(self.api_key_env_check)
        env_var_layout.addWidget(self.api_key_env_edit)
        provider_layout.addRow("", env_var_layout)
        
        # Connect signals for API key handling
        self.api_key_env_check.stateChanged.connect(self.toggle_api_key_input)
        self.provider_combo.currentIndexChanged.connect(self.update_api_key_env_var)
        
        layout.addWidget(provider_group)
        
        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()
        advanced_group.setLayout(advanced_layout)
        
        # Temperature
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 100)
        self.temperature_spin.setSingleStep(5)
        self.temperature_spin.setValue(70)  # Default 0.7
        self.temperature_spin.setSuffix("%")
        advanced_layout.addRow("Temperature:", self.temperature_spin)
        
        # Max tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 100000)
        self.max_tokens_spin.setSingleStep(100)
        self.max_tokens_spin.setValue(4000)
        advanced_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        layout.addWidget(advanced_group)
        
        # Connect signals
        self.provider_combo.currentIndexChanged.connect(self.update_model_options)
        
        layout.addStretch()
        
        return tab
        
    def create_server_tab(self):
        """Create the MCP server settings tab.
        
        Returns:
            QWidget: The MCP server settings tab.
        """
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Server list group
        server_group = QGroupBox("MCP Servers")
        server_layout = QVBoxLayout()
        server_group.setLayout(server_layout)
        
        # Server list
        self.server_list = QListWidget()
        self.server_list.setMinimumHeight(150)
        server_layout.addWidget(self.server_list)
        
        # Server buttons
        server_buttons_layout = QHBoxLayout()
        self.add_server_button = QPushButton("Add")
        self.edit_server_button = QPushButton("Edit")
        self.remove_server_button = QPushButton("Remove")
        self.default_server_button = QPushButton("Set as Default")
        
        server_buttons_layout.addWidget(self.add_server_button)
        server_buttons_layout.addWidget(self.edit_server_button)
        server_buttons_layout.addWidget(self.remove_server_button)
        server_buttons_layout.addWidget(self.default_server_button)
        server_layout.addLayout(server_buttons_layout)
        
        # Server details group
        self.server_details_group = QGroupBox("Server Details")
        self.server_details_layout = QFormLayout()
        self.server_details_group.setLayout(self.server_details_layout)
        
        # Server name
        self.server_name_edit = QLineEdit()
        self.server_details_layout.addRow("Name:", self.server_name_edit)
        
        # Server command
        self.server_command_edit = QLineEdit()
        self.server_details_layout.addRow("Command:", self.server_command_edit)
        
        # Server arguments
        self.server_args_edit = QLineEdit()
        self.server_details_layout.addRow("Arguments:", self.server_args_edit)
        
        # Auto-approve tools
        self.auto_approve_edit = QLineEdit()
        self.auto_approve_edit.setPlaceholderText("Comma-separated list of tool names")
        self.server_details_layout.addRow("Auto-approve:", self.auto_approve_edit)
        
        # Disabled checkbox
        self.server_disabled_check = QCheckBox("Disabled")
        self.server_details_layout.addRow("", self.server_disabled_check)
        
        # Server buttons
        server_detail_buttons_layout = QHBoxLayout()
        self.save_server_button = QPushButton("Save Server")
        self.cancel_server_button = QPushButton("Cancel")
        
        server_detail_buttons_layout.addStretch()
        server_detail_buttons_layout.addWidget(self.cancel_server_button)
        server_detail_buttons_layout.addWidget(self.save_server_button)
        self.server_details_layout.addRow("", server_detail_buttons_layout)
        
        # Initially hide the server details
        self.server_details_group.setVisible(False)
        
        server_layout.addWidget(self.server_details_group)
        layout.addWidget(server_group)
        
        # Connect signals
        self.add_server_button.clicked.connect(self.add_server)
        self.edit_server_button.clicked.connect(self.edit_server)
        self.remove_server_button.clicked.connect(self.remove_server)
        self.default_server_button.clicked.connect(self.set_default_server)
        self.save_server_button.clicked.connect(self.save_server)
        self.cancel_server_button.clicked.connect(self.cancel_server_edit)
        self.server_list.itemSelectionChanged.connect(self.update_server_buttons)
        
        # Initially disable the edit, remove, and default buttons
        self.edit_server_button.setEnabled(False)
        self.remove_server_button.setEnabled(False)
        self.default_server_button.setEnabled(False)
        
        layout.addStretch()
        
        return tab
        
    def update_model_options(self):
        """Update the model options based on the selected provider."""
        self.model_combo.clear()
        
        if self.provider_combo.currentText() == "OpenAI":
            self.model_combo.addItems([
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ])
        else:  # Anthropic
            self.model_combo.addItems([
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ])
        
        # Update the API key environment variable placeholder
        self.update_api_key_env_var()
            
    def update_api_key_env_var(self):
        """Update the API key environment variable placeholder based on the selected provider."""
        if self.provider_combo.currentText() == "OpenAI":
            self.api_key_env_edit.setPlaceholderText("OPENAI_API_KEY")
        else:  # Anthropic
            self.api_key_env_edit.setPlaceholderText("ANTHROPIC_API_KEY")
            
    def toggle_api_key_input(self, state):
        """Toggle the API key input field based on the environment variable checkbox."""
        self.api_key_edit.setEnabled(not state)
        self.api_key_env_edit.setEnabled(state)
        
    def add_server(self):
        """Show the server details form for adding a new server."""
        # Clear the form
        self.server_name_edit.clear()
        self.server_command_edit.clear()
        self.server_args_edit.clear()
        self.auto_approve_edit.clear()
        self.server_disabled_check.setChecked(False)
        
        # Show the form
        self.server_details_group.setVisible(True)
        self.server_list.clearSelection()
        self.update_server_buttons()
        
    def edit_server(self):
        """Show the server details form for editing the selected server."""
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            return
            
        server_name = selected_items[0].text()
        server_config = self.config.get("mcp_servers", {}).get(server_name, {})
        
        # Fill the form
        self.server_name_edit.setText(server_name)
        
        # Handle command (could be a string or a list)
        command = server_config.get("command", "")
        if isinstance(command, list):
            command = " ".join(command)
        self.server_command_edit.setText(command)
        
        # Handle arguments (could be a string or a list)
        args = server_config.get("args", "")
        if isinstance(args, list):
            args = " ".join(args)
        self.server_args_edit.setText(args)
        
        # Handle auto-approve list
        auto_approve = server_config.get("autoApprove", [])
        self.auto_approve_edit.setText(", ".join(auto_approve))
        
        # Handle disabled flag
        self.server_disabled_check.setChecked(server_config.get("disabled", False))
        
        # Show the form
        self.server_details_group.setVisible(True)
        
    def remove_server(self):
        """Remove the selected server from the list."""
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            return
            
        server_name = selected_items[0].text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove the server '{server_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from the list widget
            self.server_list.takeItem(self.server_list.row(selected_items[0]))
            
            # Remove from the config
            if "mcp_servers" in self.config and server_name in self.config["mcp_servers"]:
                del self.config["mcp_servers"][server_name]
                
            # If this was the default server, reset the default
            if self.config.get("default_server") == server_name:
                self.config["default_server"] = ""
                
            # Hide the server details form
            self.server_details_group.setVisible(False)
            
    def set_default_server(self):
        """Set the selected server as the default."""
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            return
            
        server_name = selected_items[0].text()
        self.config["default_server"] = server_name
        
        # Update the list to show which server is the default
        self.update_server_list()
        
    def save_server(self):
        """Save the server details to the configuration."""
        server_name = self.server_name_edit.text().strip()
        
        # Validate server name
        if not server_name:
            QMessageBox.warning(self, "Validation Error", "Server name cannot be empty.")
            return
            
        # Get the command and arguments
        command_text = self.server_command_edit.text().strip()
        args_text = self.server_args_edit.text().strip()
        
        # Validate command
        if not command_text:
            QMessageBox.warning(self, "Validation Error", "Server command cannot be empty.")
            return
            
        # Parse command and arguments as lists
        command = command_text.split()
        args = args_text.split() if args_text else []
        
        # Parse auto-approve list
        auto_approve_text = self.auto_approve_edit.text().strip()
        auto_approve = [item.strip() for item in auto_approve_text.split(",")] if auto_approve_text else []
        
        # Create or update the server configuration
        if "mcp_servers" not in self.config:
            self.config["mcp_servers"] = {}
            
        self.config["mcp_servers"][server_name] = {
            "command": command,
            "args": args,
            "autoApprove": auto_approve,
            "disabled": self.server_disabled_check.isChecked()
        }
        
        # If this is the first server, set it as the default
        if not self.config.get("default_server"):
            self.config["default_server"] = server_name
            
        # Update the server list
        self.update_server_list()
        
        # Hide the server details form
        self.server_details_group.setVisible(False)
        
    def cancel_server_edit(self):
        """Cancel editing the server details."""
        self.server_details_group.setVisible(False)
        
    def update_server_buttons(self):
        """Update the state of the server buttons based on the selection."""
        has_selection = len(self.server_list.selectedItems()) > 0
        
        self.edit_server_button.setEnabled(has_selection)
        self.remove_server_button.setEnabled(has_selection)
        self.default_server_button.setEnabled(has_selection)
        
    def update_server_list(self):
        """Update the server list widget from the configuration."""
        self.server_list.clear()
        
        servers = self.config.get("mcp_servers", {})
        default_server = self.config.get("default_server", "")
        
        for server_name in servers:
            item = QListWidgetItem(server_name)
            if server_name == default_server:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setText(f"{server_name} (Default)")
            self.server_list.addItem(item)
            
    def load_settings(self, config):
        """Load settings from config.
        
        Args:
            config (dict): The configuration dictionary.
        """
        # Store the config
        self.config = config.copy() if config else {}
        
        # General settings
        ui_config = config.get("ui", {})
        
        # Theme
        theme = ui_config.get("theme", "system")
        self.theme_combo.setCurrentText(theme.capitalize())
        
        # Font size
        font_size = ui_config.get("font_size", 12)
        font_size_name = UIConfig.get_font_size_name(font_size)
        self.font_size_combo.setCurrentText(font_size_name.capitalize())
        
        # High DPI scaling
        self.high_dpi_check.setChecked(ui_config.get("high_dpi_scaling", True))
        
        # Panel visibility
        self.tool_panel_check.setChecked(ui_config.get("show_tool_panel", True))
        self.status_bar_check.setChecked(ui_config.get("show_status_bar", True))
        
        # Conversation settings
        self.history_limit_spin.setValue(ui_config.get("conversation_history_limit", 50))
        
        export_format = ui_config.get("default_export_format", "json")
        self.export_format_combo.setCurrentText(export_format.capitalize())
        
        # LLM settings
        llm_config = config.get("llm", {})
        
        # Provider
        provider = llm_config.get("provider", "openai")
        self.provider_combo.setCurrentText(provider.capitalize())
        
        # Model
        model = llm_config.get("model", "")
        if model:
            self.model_combo.setCurrentText(model)
            
        # API key
        api_key = llm_config.get("api_key", "")
        api_key_env = llm_config.get("api_key_env", "")
        
        if api_key_env:
            self.api_key_env_check.setChecked(True)
            self.api_key_env_edit.setText(api_key_env)
            self.api_key_edit.setEnabled(False)
        else:
            self.api_key_env_check.setChecked(False)
            self.api_key_edit.setText(api_key)
            self.api_key_env_edit.setEnabled(False)
            
        # Advanced LLM settings
        temperature = llm_config.get("temperature", 0.7)
        self.temperature_spin.setValue(int(temperature * 100))
        
        max_tokens = llm_config.get("max_tokens", 4000)
        self.max_tokens_spin.setValue(max_tokens)
        
        # Server settings
        self.update_server_list()
        
    def validate_and_save(self):
        """Validate settings and save if valid."""
        # Clear previous errors
        self.validation_errors = {}
        self.error_label.setText("")
        self.error_label.setVisible(False)
        
        # Validate settings
        valid = self.validate_settings()
        
        if valid:
            self.save_settings()
        else:
            # Show error message
            error_message = "Please correct the following errors:\n"
            for field, error in self.validation_errors.items():
                error_message += f"• {field}: {error}\n"
                
            self.error_label.setText(error_message)
            self.error_label.setVisible(True)
            
    def validate_settings(self):
        """Validate the settings.
        
        Returns:
            bool: True if the settings are valid, False otherwise.
        """
        valid = True
        
        # Validate LLM settings
        if not self.api_key_env_check.isChecked() and not self.api_key_edit.text().strip():
            self.validation_errors["API Key"] = "API key is required unless using environment variable"
            valid = False
            
        if self.api_key_env_check.isChecked() and not self.api_key_env_edit.text().strip():
            self.validation_errors["API Key Environment Variable"] = "Environment variable name is required"
            valid = False
            
        # Validate UI settings
        try:
            # Create a UIConfig object to validate UI settings
            ui_config = UIConfig(
                theme=self.theme_combo.currentText().lower(),
                font_size=UIConfig.get_font_size_from_name(self.font_size_combo.currentText().lower()),
                high_dpi_scaling=self.high_dpi_check.isChecked(),
                show_tool_panel=self.tool_panel_check.isChecked(),
                show_status_bar=self.status_bar_check.isChecked(),
                conversation_history_limit=self.history_limit_spin.value(),
                default_export_format=self.export_format_combo.currentText().lower()
            )
            ui_config.validate()
        except ValueError as e:
            self.validation_errors["UI Settings"] = str(e)
            valid = False
            
        return valid
        
    def save_settings(self):
        """Save settings and emit settings_updated signal."""
        # UI settings
        if "ui" not in self.config:
            self.config["ui"] = {}
            
        self.config["ui"].update({
            "theme": self.theme_combo.currentText().lower(),
            "font_size": UIConfig.get_font_size_from_name(self.font_size_combo.currentText().lower()),
            "high_dpi_scaling": self.high_dpi_check.isChecked(),
            "show_tool_panel": self.tool_panel_check.isChecked(),
            "show_status_bar": self.status_bar_check.isChecked(),
            "conversation_history_limit": self.history_limit_spin.value(),
            "default_export_format": self.export_format_combo.currentText().lower()
        })
        
        # LLM settings
        if "llm" not in self.config:
            self.config["llm"] = {}
            
        self.config["llm"].update({
            "provider": self.provider_combo.currentText().lower(),
            "model": self.model_combo.currentText(),
            "temperature": self.temperature_spin.value() / 100.0,
            "max_tokens": self.max_tokens_spin.value()
        })
        
        # API key handling
        if self.api_key_env_check.isChecked():
            self.config["llm"]["api_key_env"] = self.api_key_env_edit.text().strip()
            self.config["llm"]["api_key"] = ""
        else:
            self.config["llm"]["api_key"] = self.api_key_edit.text().strip()
            self.config["llm"]["api_key_env"] = ""
        
        # Emit the settings_updated signal
        self.settings_updated.emit(self.config)
        self.accept()