#!/usr/bin/env python3
"""
Hugo Blog Manager - Complete PySide6 Qt Application
A comprehensive tool for managing Hugo blog projects with theme management,
content generation, data import/export, and Git integration.
"""

import sys
import os
import json
import subprocess
import threading
import time
import socket
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import toml
except ImportError:
    print("Installing required toml package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "toml"])
    import toml

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QTextEdit,
    QFileDialog, QMessageBox, QScrollArea, QFrame, QGridLayout,
    QGroupBox, QSplitter, QProgressBar, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, QObject, Signal, QTimer, QProcess
from PySide6.QtGui import QFont, QPalette, QColor, QTextCursor

# Configuration Arrays - Easy Access for Modifications
HUGO_COMMANDS = [
    "hugo server --openBrowser",
    "hugo server --disableFastRender --openBrowser", 
    "hugo server --buildDrafts --openBrowser",
    "hugo version"
]

EXPORT_FORMATS = [".json", ".md", ".docx"]
IMPORT_INPUT_FORMATS = [".json", ".md"]
IMPORT_OUTPUT_FORMATS = [".json", ".md"]
IMPORT_FILE_FILTERS = "Data Files (*.json *.md);;JSON Files (*.json);;Markdown Files (*.md)"
DOCX_TEMPLATE_FILTER = "Word Templates (*.docx);;All Files (*)"

# Path Templates
LOCAL_DATA_PATH = "{local}/data"
TESTING_UI_PATH = "{local}/data/testing-ui.json"
MOVES_DATA_PATH = "{local}/data/moves.json"
THEME_PATH = "{local}/themes"
CONTENT_MOVES_PATH = "{local}/content/rules/move"
GENERATED_PATH = "{local}/local/generated"
HUGO_CONFIG_PATH = "{local}/hugo.toml"
MOVES_CHANGELOG_PATH = "{local}/moves-changelog"

# Script Templates  
GENERATE_MOVES_SCRIPT = "{local}/scripts/generateMovesContent.py"
IMPORT_MOVES_SCRIPT = "{local}/scripts/importMovesData.py"
EXPORT_MOVES_SCRIPT = "{local}/scripts/exportMovesData.py"
RESET_GIT_SCRIPT = "{local}/scripts/resetGit.py"

class ProcessWorker(QObject):
    """Worker for running processes in separate thread"""
    finished = Signal(str, int)
    output = Signal(str)
    error = Signal(str)
    
    def __init__(self, command, cwd=None):
        super().__init__()
        self.command = command
        self.cwd = cwd
        
    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.output.emit(output.strip())
                    
            stderr = process.stderr.read()
            if stderr:
                self.error.emit(stderr.strip())
                
            return_code = process.poll()
            self.finished.emit(self.command, return_code)
            
        except Exception as e:
            self.error.emit(f"Process error: {str(e)}")
            self.finished.emit(self.command, -1)

class ConfirmationDialog(QDialog):
    """Custom confirmation dialog for destructive operations"""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Yes | QDialogButtonBox.No,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

class LoggingArea(QTextEdit):
    """Enhanced logging area with color coding and timestamps"""
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMinimumHeight(200)
        font = QFont("Consolas", 9)
        font.setFamily("monospace")
        self.setFont(font)
        
    def log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Color coding based on level
        if level == "error":
            color = "red"
        elif level == "warning":
            color = "orange"
        elif level == "success":
            color = "green"
        else:
            color = "black"
            
        html = f'<span style="color: {color};">{formatted_message}</span><br>'
        self.insertHtml(html)
        self.moveCursor(QTextCursor.End)
        
    def log_command(self, command, cwd=None):
        cwd_str = f" (in {cwd})" if cwd else ""
        self.log(f"Executing: {command}{cwd_str}", "info")

class HugoBlogManager(QMainWindow):
    """Main Hugo Blog Manager Application"""
    
    def __init__(self):
        super().__init__()
        self.project_dir = ""
        self.theme_dir = ""
        self.hugo_process = None
        self.ui_data = {}
        self.most_recent_export = ""
        
        self.init_ui()
        # Load UI data after UI is created
        QTimer.singleShot(100, self.load_ui_data_delayed)  # Delayed to ensure UI is fully created
        self.setup_tooltips()
        
    def load_ui_data_delayed(self):
        """Delayed loading of UI data after UI is fully initialized"""
        self.load_ui_data()
        # Load hugo.toml settings if project directory exists
        if self.project_dir and os.path.exists(HUGO_CONFIG_PATH.format(local=self.project_dir)):
            self.load_hugo_toml_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Hugo Blog Manager")
        self.setMinimumSize(1000, 800)
        
        # Create central widget with scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)
        
        # Main layout
        main_layout = QVBoxLayout(scroll_widget)
        
        # Create all sections
        self.create_project_section(main_layout)
        self.create_theme_settings_section(main_layout)
        self.create_generate_content_section(main_layout)
        self.create_import_section(main_layout)
        self.create_export_section(main_layout)
        self.create_git_section(main_layout)
        self.create_hugo_section(main_layout)
        self.create_logging_section(main_layout)
        
        # Apply styling
        self.apply_styles()
        
    def create_section(self, title) -> QGroupBox:
        """Create a styled section container"""
        section = QGroupBox(title)
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        return section
        
    def create_subsection(self, title) -> QGroupBox:
        """Create a styled subsection container"""
        subsection = QGroupBox(title)
        subsection.setStyleSheet("""
            QGroupBox {
                font-weight: normal;
                font-size: 10px;
                border: 1px solid #aaaaaa;
                border-radius: 4px;
                margin-top: 1ex;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        return subsection
        
    def create_project_section(self, parent_layout):
        """Create Project Directory section"""
        section = self.create_section("Project Directory")
        layout = QVBoxLayout(section)
        
        # Project subsection
        project_sub = self.create_subsection("Project")
        project_layout = QHBoxLayout(project_sub)
        
        self.project_path_edit = QLineEdit()
        self.project_browse_btn = QPushButton("Browse")
        self.project_browse_btn.clicked.connect(self.browse_project_directory)
        
        # Connect text fields to auto-save
        self.project_path_edit.textChanged.connect(self.save_ui_data)
        
        project_layout.addWidget(self.project_path_edit)
        project_layout.addWidget(self.project_browse_btn)
        layout.addWidget(project_sub)
        
        # Theme subsection
        theme_sub = self.create_subsection("Theme")
        theme_layout = QHBoxLayout(theme_sub)
        
        self.theme_path_edit = QLineEdit()
        self.theme_browse_btn = QPushButton("Browse")
        self.theme_browse_btn.clicked.connect(self.browse_theme_directory)
        
        # Connect text fields to auto-save
        self.theme_path_edit.textChanged.connect(self.save_ui_data)
        
        theme_layout.addWidget(self.theme_path_edit)
        theme_layout.addWidget(self.theme_browse_btn)
        layout.addWidget(theme_sub)
        
        parent_layout.addWidget(section)
        
    def create_theme_settings_section(self, parent_layout):
        """Create Theme Settings section with dynamic hugo.toml editing"""
        self.theme_section = self.create_section("Theme Settings")
        self.theme_layout = QVBoxLayout(self.theme_section)
        
        # Will be populated dynamically when project is selected
        self.theme_settings_loaded = False
        
        parent_layout.addWidget(self.theme_section)
        
    def load_hugo_toml_settings(self):
        """Load and create UI elements for hugo.toml settings"""
        if not self.project_dir or self.theme_settings_loaded:
            return
            
        hugo_toml_path = HUGO_CONFIG_PATH.format(local=self.project_dir)
        
        if not os.path.exists(hugo_toml_path):
            self.log.log(f"hugo.toml not found at {hugo_toml_path}", "warning")
            return
            
        try:
            with open(hugo_toml_path, 'r', encoding='utf-8') as f:
                toml_data = toml.load(f)
                
            subsection = self.create_subsection("Changes theme settings in hugo.toml")
            grid_layout = QGridLayout(subsection)
            
            self.toml_widgets = {}
            row = [0]  # Use list to allow modification in nested function
            
            def process_toml_section(data, prefix=""):
                """Recursively process TOML sections"""
                if not isinstance(data, dict):
                    return
                    
                for key, value in data.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    
                    # Skip ignored sections and their subsections
                    if (key in ['menus', 'module']) or (prefix.startswith('menus') or prefix.startswith('module')):
                        continue
                        
                    if isinstance(value, dict):
                        # Handle nested sections
                        process_toml_section(value, full_key)
                    elif isinstance(value, list):
                        # Skip list values (like menu arrays) but log them
                        self.log.log(f"Skipping list field: {full_key}", "info")
                        continue
                    elif value is None:
                        # Skip null values
                        continue
                    else:
                        # Handle leaf values
                        try:
                            self.create_toml_field_ui(grid_layout, full_key, value, row)
                        except Exception as e:
                            self.log.log(f"Error creating UI for {full_key}: {str(e)}", "warning")
            
            process_toml_section(toml_data)
            
            self.theme_layout.addWidget(subsection)
            self.theme_settings_loaded = True
            self.log.log(f"Loaded hugo.toml settings with {row[0]} fields", "success")
            
        except Exception as e:
            self.log.log(f"Error loading hugo.toml: {str(e)}", "error")
            
    def create_toml_field_ui(self, grid_layout, key, value, row):
        """Create UI elements for a single TOML field"""
        label = QLabel(f"{key}:")
        
        if isinstance(value, bool):
            # Boolean field: dropdown + textfield-button
            dropdown = QComboBox()
            dropdown.addItems(["true", "false"])
            dropdown.setCurrentText(str(value).lower())
            
            text_field = QLineEdit(str(value).lower())
            apply_btn = QPushButton("Apply")
            apply_btn.clicked.connect(
                lambda checked, k=key, d=dropdown, t=text_field: 
                self.update_hugo_toml_nested(k, d.currentText())
            )
            
            # Sync dropdown and text field
            dropdown.currentTextChanged.connect(text_field.setText)
            text_field.textChanged.connect(
                lambda text, d=dropdown: d.setCurrentText(text) if text in ["true", "false"] else None
            )
            
            grid_layout.addWidget(label, row[0], 0)
            grid_layout.addWidget(dropdown, row[0], 1)
            grid_layout.addWidget(text_field, row[0], 2)
            grid_layout.addWidget(apply_btn, row[0], 3)
            
            self.toml_widgets[key] = (dropdown, text_field)
            
        else:
            # String/Number field: textfield-button
            text_field = QLineEdit(str(value))
            apply_btn = QPushButton("Apply")
            apply_btn.clicked.connect(
                lambda checked, k=key, t=text_field: 
                self.update_hugo_toml_nested(k, t.text())
            )
            
            grid_layout.addWidget(label, row[0], 0)
            grid_layout.addWidget(text_field, row[0], 1, 1, 2)  # Span 2 columns
            grid_layout.addWidget(apply_btn, row[0], 3)
            
            self.toml_widgets[key] = text_field
            
        row[0] += 1
            
    def update_hugo_toml_nested(self, key, value):
        """Update a nested field in hugo.toml"""
        hugo_toml_path = HUGO_CONFIG_PATH.format(local=self.project_dir)
        
        try:
            with open(hugo_toml_path, 'r', encoding='utf-8') as f:
                toml_data = toml.load(f)
                
            # Navigate to nested key
            keys = key.split('.')
            current_section = toml_data
            
            # Navigate to the parent section
            for k in keys[:-1]:
                if k not in current_section:
                    current_section[k] = {}
                current_section = current_section[k]
            
            # Convert value to appropriate type
            final_key = keys[-1]
            if value.lower() == "true":
                current_section[final_key] = True
            elif value.lower() == "false":
                current_section[final_key] = False
            elif value.isdigit():
                current_section[final_key] = int(value)
            else:
                try:
                    current_section[final_key] = float(value)
                except ValueError:
                    current_section[final_key] = value
                    
            with open(hugo_toml_path, 'w', encoding='utf-8') as f:
                toml.dump(toml_data, f)
                
            self.log.log(f"Updated hugo.toml: {key} = {value}", "success")
            
        except Exception as e:
            self.log.log(f"Error updating hugo.toml: {str(e)}", "error")
            
    def create_generate_content_section(self, parent_layout):
        """Create Generate Blog Content section"""
        section = self.create_section("Generate Blog Content")
        layout = QVBoxLayout(section)
        
        subsection = self.create_subsection("Generate moves.json related content")
        sub_layout = QVBoxLayout(subsection)
        
        # Generate button
        generate_btn = QPushButton("Execute generateMovesContent.py")
        generate_btn.clicked.connect(self.generate_moves_content)
        sub_layout.addWidget(generate_btn)
        
        # Open moves directory button
        open_moves_btn = QPushButton("Open Moves Directory")
        open_moves_btn.clicked.connect(self.open_moves_directory)
        sub_layout.addWidget(open_moves_btn)
        
        layout.addWidget(subsection)
        parent_layout.addWidget(section)
        
    def create_import_section(self, parent_layout):
        """Create Import Project Data section"""
        section = self.create_section("Import Project Data [json|md]")
        layout = QVBoxLayout(section)
        
        subsection = self.create_subsection("Import moves data with changelog tracking")
        sub_layout = QVBoxLayout(subsection)
        
        # Input file section
        input_group = QGroupBox("Input File")
        input_layout = QGridLayout(input_group)
        
        # Input format selection
        input_layout.addWidget(QLabel("Input Format:"), 0, 0)
        self.import_input_format_combo = QComboBox()
        self.import_input_format_combo.addItems(IMPORT_INPUT_FORMATS)
        self.import_input_format_combo.currentTextChanged.connect(self.save_ui_data)
        input_layout.addWidget(self.import_input_format_combo, 0, 1)
        
        # Input file selection
        input_layout.addWidget(QLabel("Input File:"), 1, 0)
        self.import_file_edit = QLineEdit()
        self.import_file_edit.textChanged.connect(self.save_ui_data)
        self.import_browse_btn = QPushButton("Browse")
        self.import_browse_btn.clicked.connect(self.browse_import_file)
        input_layout.addWidget(self.import_file_edit, 1, 1)
        input_layout.addWidget(self.import_browse_btn, 1, 2)
        
        sub_layout.addWidget(input_group)
        
        # Output file section
        output_group = QGroupBox("Output File")
        output_layout = QGridLayout(output_group)
        
        # Output format selection
        output_layout.addWidget(QLabel("Output Format:"), 0, 0)
        self.import_output_format_combo = QComboBox()
        self.import_output_format_combo.addItems(IMPORT_OUTPUT_FORMATS)
        self.import_output_format_combo.currentTextChanged.connect(self.save_ui_data)
        output_layout.addWidget(self.import_output_format_combo, 0, 1)
        
        # Output file selection
        output_layout.addWidget(QLabel("Output File:"), 1, 0)
        self.import_output_file_edit = QLineEdit()
        self.import_output_file_edit.textChanged.connect(self.save_ui_data)
        self.import_output_browse_btn = QPushButton("Browse")
        self.import_output_browse_btn.clicked.connect(self.browse_import_output_file)
        output_layout.addWidget(self.import_output_file_edit, 1, 1)
        output_layout.addWidget(self.import_output_browse_btn, 1, 2)
        
        sub_layout.addWidget(output_group)
        
        # Changelog directory section
        changelog_group = QGroupBox("Changelog Directory (Optional)")
        changelog_layout = QHBoxLayout(changelog_group)
        
        self.import_changelog_dir_edit = QLineEdit()
        self.import_changelog_dir_edit.textChanged.connect(self.save_ui_data)
        self.import_changelog_browse_btn = QPushButton("Browse")
        self.import_changelog_browse_btn.clicked.connect(self.browse_import_changelog_dir)
        
        changelog_layout.addWidget(self.import_changelog_dir_edit)
        changelog_layout.addWidget(self.import_changelog_browse_btn)
        sub_layout.addWidget(changelog_group)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        # Import button
        import_btn = QPushButton("Import Data with Changelog")
        import_btn.clicked.connect(self.import_moves_data)
        buttons_layout.addWidget(import_btn)
        
        # Open current moves.json button
        open_moves_btn = QPushButton("Open Current moves.json")
        open_moves_btn.clicked.connect(self.open_moves_json)
        buttons_layout.addWidget(open_moves_btn)
        
        # Open changelog directory button
        open_changelog_btn = QPushButton("Open Changelog Directory")
        open_changelog_btn.clicked.connect(self.open_changelog_directory)
        buttons_layout.addWidget(open_changelog_btn)
        
        sub_layout.addLayout(buttons_layout)
        
        layout.addWidget(subsection)
        parent_layout.addWidget(section)
        
    def create_export_section(self, parent_layout):
        """Create Export Project Data section"""
        section = self.create_section("Export Project Data [json|md|docx]")
        layout = QVBoxLayout(section)
        
        subsection = self.create_subsection("Export moves.json")
        sub_layout = QVBoxLayout(subsection)
        
        # Output filename
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("Filename:"))
        self.export_filename_edit = QLineEdit("moves_export")
        self.export_filename_edit.textChanged.connect(self.save_ui_data)  # Auto-save
        filename_layout.addWidget(self.export_filename_edit)
        sub_layout.addLayout(filename_layout)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(EXPORT_FORMATS)
        format_layout.addWidget(self.export_format_combo)
        sub_layout.addLayout(format_layout)
        
        # Output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output Directory:"))
        self.export_dir_edit = QLineEdit()
        self.export_dir_edit.textChanged.connect(self.save_ui_data)  # Auto-save
        self.export_dir_browse_btn = QPushButton("Browse")
        self.export_dir_browse_btn.clicked.connect(self.browse_export_directory)
        dir_layout.addWidget(self.export_dir_edit)
        dir_layout.addWidget(self.export_dir_browse_btn)
        sub_layout.addLayout(dir_layout)
        
        # Template file (for DOCX)
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template (DOCX only):"))
        self.export_template_edit = QLineEdit()
        self.export_template_edit.textChanged.connect(self.save_ui_data)  # Auto-save
        self.export_template_browse_btn = QPushButton("Browse")
        self.export_template_browse_btn.clicked.connect(self.browse_export_template)
        template_layout.addWidget(self.export_template_edit)
        template_layout.addWidget(self.export_template_browse_btn)
        sub_layout.addLayout(template_layout)
        
        # Export button
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_moves_data)
        sub_layout.addWidget(export_btn)
        
        # Open generated directory button
        open_gen_btn = QPushButton("Open Generated Directory")
        open_gen_btn.clicked.connect(self.open_generated_directory)
        sub_layout.addWidget(open_gen_btn)
        
        # Open most recent file button
        self.open_recent_btn = QPushButton("Opens most recent generated file")
        self.open_recent_btn.clicked.connect(self.open_recent_export)
        self.open_recent_btn.setEnabled(False)
        sub_layout.addWidget(self.open_recent_btn)
        
        layout.addWidget(subsection)
        parent_layout.addWidget(section)
        
    def create_git_section(self, parent_layout):
        """Create Source Control section"""
        section = self.create_section("Source Control")
        layout = QVBoxLayout(section)
        
        subsection = self.create_subsection("Git")
        sub_layout = QVBoxLayout(subsection)
        
        reset_git_btn = QPushButton("Reset Git Repository")
        reset_git_btn.clicked.connect(self.reset_git_repository)
        sub_layout.addWidget(reset_git_btn)
        
        layout.addWidget(subsection)
        parent_layout.addWidget(section)
        
    def create_hugo_section(self, parent_layout):
        """Create Run Hugo section"""
        section = self.create_section("Run Hugo")
        layout = QVBoxLayout(section)
        
        # Test Hugo availability
        test_btn = QPushButton("Test Hugo Installation")
        test_btn.clicked.connect(lambda: self.run_hugo_command("hugo version"))
        test_btn.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
        layout.addWidget(test_btn)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Predefined Hugo commands
        for cmd in HUGO_COMMANDS:
            btn = QPushButton(cmd)
            btn.clicked.connect(lambda checked, command=cmd: self.run_hugo_command(command))
            layout.addWidget(btn)
            
        # Custom Hugo command
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("hugo server"))
        self.hugo_custom_edit = QLineEdit()
        self.hugo_custom_edit.setPlaceholderText("Additional parameters...")
        self.hugo_custom_edit.textChanged.connect(self.save_ui_data)  # Auto-save
        custom_btn = QPushButton("Run Custom")
        custom_btn.clicked.connect(self.run_custom_hugo_command)
        
        custom_layout.addWidget(self.hugo_custom_edit)
        custom_layout.addWidget(custom_btn)
        layout.addLayout(custom_layout)
        
        # Stop Hugo server
        stop_btn = QPushButton("Stop Hugo Server")
        stop_btn.clicked.connect(self.stop_hugo_server)
        stop_btn.setStyleSheet("background-color: #ffebee; color: #c62828; font-weight: bold;")
        layout.addWidget(stop_btn)
        
        # Check Hugo server status
        status_btn = QPushButton("Check Hugo Server Status")
        status_btn.clicked.connect(self.check_hugo_status)
        status_btn.setStyleSheet("background-color: #f3e5f5; color: #7b1fa2;")
        layout.addWidget(status_btn)
        
        parent_layout.addWidget(section)
        
    def check_hugo_status(self):
        """Check if Hugo server is running on common ports"""
        self.log.log("Checking Hugo server status...", "info")
        
        # Check process status
        if hasattr(self, 'hugo_process') and self.hugo_process:
            if self.hugo_process.state() == QProcess.Running:
                self.log.log("Hugo QProcess is running", "success")
            elif self.hugo_process.state() == QProcess.Starting:
                self.log.log("Hugo QProcess is starting", "info")
            else:
                self.log.log("Hugo QProcess is not running", "info")
        else:
            self.log.log("No Hugo QProcess found", "info")
            
        # Check common Hugo ports
        hugo_ports = [1313, 1314, 1315, 1316]
        running_ports = []
        
        for port in hugo_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:  # Port is open
                    running_ports.append(port)
                    self.log.log(f"Hugo server detected on localhost:{port}", "success")
                    
            except Exception as e:
                self.log.log(f"Error checking port {port}: {str(e)}", "warning")
                
        if not running_ports:
            self.log.log("No Hugo servers detected on common ports", "info")
        else:
            self.log.log(f"Total Hugo servers found: {len(running_ports)}", "success")
        
    def create_logging_section(self, parent_layout):
        """Create Debug Log section"""
        section = self.create_section("Debug Log")
        layout = QVBoxLayout(section)
        
        self.log = LoggingArea()
        layout.addWidget(self.log)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(lambda: self.log.clear())
        button_layout.addWidget(clear_btn)
        
        # Open settings file button
        settings_btn = QPushButton("Open Settings File")
        settings_btn.clicked.connect(self.open_settings_file)
        button_layout.addWidget(settings_btn)
        
        layout.addLayout(button_layout)
        parent_layout.addWidget(section)
        
        # Initial log message with version info
        self.log.log("Hugo Blog Manager initialized", "success")
        self.log.log("Ready to load project settings...", "info")
        
    def open_settings_file(self):
        """Open the UI settings file"""
        if not self.project_dir:
            self.log.log("No project directory selected", "warning")
            return
            
        ui_data_path = TESTING_UI_PATH.format(local=self.project_dir)
        
        # Create file if it doesn't exist
        if not os.path.exists(ui_data_path):
            self.save_ui_data()
            
        self.open_file(ui_data_path)
        
    def apply_styles(self):
        """Apply global styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #e1e1e1;
                border: 1px solid #adadad;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d4edda;
            }
            QPushButton:pressed {
                background-color: #c3e6cb;
            }
            QLineEdit {
                border: 1px solid #adadad;
                border-radius: 4px;
                padding: 4px;
                font-size: 10px;
            }
            QComboBox {
                border: 1px solid #adadad;
                border-radius: 4px;
                padding: 4px;
                font-size: 10px;
            }
        """)
        
    def setup_tooltips(self):
        """Set up tooltips for all UI elements"""
        # Project section tooltips
        self.project_path_edit.setToolTip("Select the main Hugo project directory")
        self.project_browse_btn.setToolTip("Browse for Hugo project directory")
        self.theme_path_edit.setToolTip("Select the theme directory within the project")
        self.theme_browse_btn.setToolTip("Browse for theme directory")
        
        # Import section tooltips
        self.import_input_format_combo.setToolTip("Select input file format (.json or .md)")
        self.import_file_edit.setToolTip("Select input file to import")
        self.import_browse_btn.setToolTip("Browse for input file to import")
        
        self.import_output_format_combo.setToolTip("Select output file format (.json or .md)")
        self.import_output_file_edit.setToolTip("Select output file path")
        self.import_output_browse_btn.setToolTip("Browse for output file location")
        
        self.import_changelog_dir_edit.setToolTip("Directory for changelog files (optional, defaults to ./moves-changelog)")
        self.import_changelog_browse_btn.setToolTip("Browse for changelog directory")
        
        # Export section tooltips
        self.export_filename_edit.setToolTip("Output filename without extension")
        self.export_format_combo.setToolTip("Choose export format")
        self.export_dir_edit.setToolTip("Directory where exported file will be saved")
        self.export_template_edit.setToolTip("Template file for DOCX export")
        
    def load_ui_data(self):
        """Load UI data from local storage"""
        settings_found = False
        loaded_project_dir = None
        
        # First, try to find and load existing settings files
        potential_settings_paths = []
        
        # Check current directory first
        current_dir = self.normalize_path(os.getcwd())
        current_settings = TESTING_UI_PATH.format(local=current_dir)
        potential_settings_paths.append((current_dir, current_settings))
        
        # Check if there are any settings files in subdirectories
        try:
            for root, dirs, files in os.walk(current_dir):
                if 'testing-ui.json' in files and 'data' in root:
                    project_dir = self.normalize_path(root.replace('/data', '').replace('\\data', ''))
                    settings_path = os.path.join(root, 'testing-ui.json')
                    potential_settings_paths.append((project_dir, settings_path))
        except:
            pass  # Ignore walk errors
            
        # Try to load from the first available settings file
        for proj_dir, settings_path in potential_settings_paths:
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        self.ui_data = json.load(f)
                    
                    # PRIORITY: Use project_dir from settings if it exists and is valid
                    if 'project_dir' in self.ui_data and self.ui_data['project_dir']:
                        test_project_dir = self.normalize_path(self.ui_data['project_dir'])
                        if os.path.exists(test_project_dir):
                            loaded_project_dir = test_project_dir
                            self.log.log(f"Using saved project directory: {loaded_project_dir}", "success")
                        else:
                            self.log.log(f"Saved project directory not found: {test_project_dir}", "warning")
                    
                    # Only fall back to settings file location if saved project_dir is invalid
                    if not loaded_project_dir:
                        loaded_project_dir = proj_dir
                        self.log.log(f"Falling back to settings file location: {loaded_project_dir}", "info")
                        
                    settings_found = True
                    self.log.log(f"Loaded settings from: {settings_path}", "success")
                    break
                    
                except Exception as e:
                    self.log.log(f"Error reading settings {settings_path}: {str(e)}", "warning")
                    continue
        
        # Final fallback to current directory if no settings found or loaded
        if not settings_found or not loaded_project_dir:
            loaded_project_dir = current_dir
            self.ui_data = {}
            self.log.log("No existing settings found or invalid, using current directory", "info")
            
        # Set the determined project directory
        self.project_dir = loaded_project_dir
        self.project_path_edit.setText(self.project_dir)
        
        # Restore all UI state from loaded data
        if 'theme_dir' in self.ui_data and self.ui_data['theme_dir']:
            test_theme_dir = self.normalize_path(self.ui_data['theme_dir'])
            if os.path.exists(test_theme_dir):
                self.theme_dir = test_theme_dir
                self.theme_path_edit.setText(self.theme_dir)
            else:
                self.log.log(f"Saved theme directory not found: {test_theme_dir}", "warning")
                self._auto_detect_theme()
        else:
            # Auto-detect theme if not in settings or invalid
            self._auto_detect_theme()
            
        # Restore import fields
        if 'import_input_format' in self.ui_data and self.ui_data['import_input_format']:
            self.import_input_format_combo.setCurrentText(self.ui_data['import_input_format'])
        
        if 'import_output_format' in self.ui_data and self.ui_data['import_output_format']:
            self.import_output_format_combo.setCurrentText(self.ui_data['import_output_format'])
            
        if 'import_file' in self.ui_data and self.ui_data['import_file']:
            self.import_file_edit.setText(self.normalize_path(self.ui_data['import_file']))
            
        if 'import_output_file' in self.ui_data and self.ui_data['import_output_file']:
            self.import_output_file_edit.setText(self.normalize_path(self.ui_data['import_output_file']))
        else:
            # Set default output file
            default_moves_path = MOVES_DATA_PATH.format(local=self.project_dir)
            self.import_output_file_edit.setText(default_moves_path)
            
        if 'import_changelog_dir' in self.ui_data and self.ui_data['import_changelog_dir']:
            self.import_changelog_dir_edit.setText(self.normalize_path(self.ui_data['import_changelog_dir']))
        else:
            # Set default changelog directory
            default_changelog_path = MOVES_CHANGELOG_PATH.format(local=self.project_dir)
            self.import_changelog_dir_edit.setText(default_changelog_path)
            
        # Restore other UI fields
        if 'export_filename' in self.ui_data and self.ui_data['export_filename']:
            self.export_filename_edit.setText(self.ui_data['export_filename'])
        else:
            self.export_filename_edit.setText("moves_export")  # default
            
        if 'export_dir' in self.ui_data and self.ui_data['export_dir']:
            test_export_dir = self.normalize_path(self.ui_data['export_dir'])
            self.export_dir_edit.setText(test_export_dir)
        else:
            # Set default export directory
            gen_path = self.normalize_path(GENERATED_PATH.format(local=self.project_dir))
            self.export_dir_edit.setText(gen_path)
            
        if 'export_template' in self.ui_data and self.ui_data['export_template']:
            self.export_template_edit.setText(self.normalize_path(self.ui_data['export_template']))
            
        if 'hugo_custom' in self.ui_data and self.ui_data['hugo_custom']:
            self.hugo_custom_edit.setText(self.ui_data['hugo_custom'])
        
        self.log.log(f"UI initialized with project: {self.project_dir}", "success")
        
    def _auto_detect_theme(self):
        """Auto-detect theme directory"""
        themes_path = THEME_PATH.format(local=self.project_dir)
        if os.path.exists(themes_path):
            theme_dirs = [d for d in os.listdir(themes_path) 
                         if os.path.isdir(os.path.join(themes_path, d))]
            if theme_dirs:
                first_theme = self.normalize_path(os.path.join(themes_path, theme_dirs[0]))
                self.theme_dir = first_theme
                self.theme_path_edit.setText(first_theme)
                self.log.log(f"Auto-detected theme: {first_theme}", "info")
                
    def save_ui_data(self):
        """Save UI data to local storage"""
        if not self.project_dir:
            return
            
        # Ensure data directory exists
        data_dir = LOCAL_DATA_PATH.format(local=self.project_dir)
        os.makedirs(data_dir, exist_ok=True)
        
        self.ui_data.update({
            'project_dir': self.normalize_path(self.project_path_edit.text()),
            'theme_dir': self.normalize_path(self.theme_path_edit.text()),
            'import_input_format': self.import_input_format_combo.currentText(),
            'import_output_format': self.import_output_format_combo.currentText(),
            'import_file': self.normalize_path(self.import_file_edit.text()),
            'import_output_file': self.normalize_path(self.import_output_file_edit.text()),
            'import_changelog_dir': self.normalize_path(self.import_changelog_dir_edit.text()),
            'export_filename': self.export_filename_edit.text(),
            'export_dir': self.normalize_path(self.export_dir_edit.text()),
            'export_template': self.normalize_path(self.export_template_edit.text()),
            'hugo_custom': self.hugo_custom_edit.text()
        })
        
        ui_data_path = TESTING_UI_PATH.format(local=self.project_dir)
        
        try:
            with open(ui_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.ui_data, f, indent=2)
            self.log.log(f"Saved UI data to: {ui_data_path}", "success")
        except Exception as e:
            self.log.log(f"Error saving UI data: {str(e)}", "error")
            
    def normalize_path(self, path):
        """Normalize path to use forward slashes consistently"""
        return path.replace('\\', '/') if path else path
    
    def browse_project_directory(self):
        """Browse for project directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Hugo Project Directory", 
            self.project_path_edit.text() or os.getcwd()
        )
        if dir_path:
            self.project_dir = self.normalize_path(dir_path)
            self.project_path_edit.setText(self.project_dir)
            self.log.log(f"Selected project directory: {self.project_dir}", "info")
            
            # Auto-detect theme directory
            themes_path = THEME_PATH.format(local=self.project_dir)
            if os.path.exists(themes_path):
                theme_dirs = [d for d in os.listdir(themes_path) 
                             if os.path.isdir(os.path.join(themes_path, d))]
                if theme_dirs:
                    first_theme = self.normalize_path(os.path.join(themes_path, theme_dirs[0]))
                    self.theme_dir = first_theme
                    self.theme_path_edit.setText(first_theme)
                    self.log.log(f"Auto-detected theme: {first_theme}", "info")
                    
            # Set default paths for new project
            gen_path = self.normalize_path(GENERATED_PATH.format(local=self.project_dir))
            self.export_dir_edit.setText(gen_path)
            
            default_moves_path = MOVES_DATA_PATH.format(local=self.project_dir)
            self.import_output_file_edit.setText(default_moves_path)
            
            default_changelog_path = MOVES_CHANGELOG_PATH.format(local=self.project_dir)
            self.import_changelog_dir_edit.setText(default_changelog_path)
            
            # Reset and reload hugo.toml settings for new project
            self.theme_settings_loaded = False
            # Clear existing theme settings UI
            if hasattr(self, 'theme_layout'):
                # Remove existing subsections except the first one
                while self.theme_layout.count() > 0:
                    child = self.theme_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            
            # Load hugo.toml settings for new project
            self.load_hugo_toml_settings()
            
            self.save_ui_data()
            
    def browse_theme_directory(self):
        """Browse for theme directory"""
        start_dir = self.theme_path_edit.text() or THEME_PATH.format(local=self.project_dir)
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Theme Directory", start_dir
        )
        if dir_path:
            self.theme_dir = self.normalize_path(dir_path)
            self.theme_path_edit.setText(self.theme_dir)
            self.log.log(f"Selected theme directory: {self.theme_dir}", "info")
            self.save_ui_data()
            
    def browse_import_file(self):
        """Browse for import input file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Import Input File", 
            self.import_file_edit.text() or self.project_dir,
            IMPORT_FILE_FILTERS
        )
        if file_path:
            file_path = self.normalize_path(file_path)
            self.import_file_edit.setText(file_path)
            
            # Auto-detect input format from file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext in IMPORT_INPUT_FORMATS:
                self.import_input_format_combo.setCurrentText(ext)
                
            self.log.log(f"Selected import input file: {file_path}", "info")
            self.save_ui_data()
            
    def browse_import_output_file(self):
        """Browse for import output file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Import Output File", 
            self.import_output_file_edit.text() or MOVES_DATA_PATH.format(local=self.project_dir),
            "JSON Files (*.json);;Markdown Files (*.md);;All Files (*)"
        )
        if file_path:
            file_path = self.normalize_path(file_path)
            self.import_output_file_edit.setText(file_path)
            
            # Auto-detect output format from file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext in IMPORT_OUTPUT_FORMATS:
                self.import_output_format_combo.setCurrentText(ext)
                
            self.log.log(f"Selected import output file: {file_path}", "info")
            self.save_ui_data()
            
    def browse_import_changelog_dir(self):
        """Browse for import changelog directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Changelog Directory", 
            self.import_changelog_dir_edit.text() or MOVES_CHANGELOG_PATH.format(local=self.project_dir)
        )
        if dir_path:
            dir_path = self.normalize_path(dir_path)
            self.import_changelog_dir_edit.setText(dir_path)
            self.log.log(f"Selected changelog directory: {dir_path}", "info")
            self.save_ui_data()
            
    def browse_export_directory(self):
        """Browse for export directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Export Directory", 
            self.export_dir_edit.text() or GENERATED_PATH.format(local=self.project_dir)
        )
        if dir_path:
            dir_path = self.normalize_path(dir_path)
            self.export_dir_edit.setText(dir_path)
            self.log.log(f"Selected export directory: {dir_path}", "info")
            self.save_ui_data()
            
    def browse_export_template(self):
        """Browse for export template file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Template File", 
            self.export_template_edit.text() or self.project_dir,
            DOCX_TEMPLATE_FILTER
        )
        if file_path:
            file_path = self.normalize_path(file_path)
            self.export_template_edit.setText(file_path)
            self.log.log(f"Selected template file: {file_path}", "info")
            self.save_ui_data()
            
    def run_script_async(self, script_path, *args):
        """Run a Python script asynchronously"""
        if not os.path.exists(script_path):
            self.log.log(f"Script not found: {script_path}", "error")
            return
            
        command = [sys.executable, script_path] + list(args)
        command_str = ' '.join(command)
        
        self.log.log_command(command_str, self.project_dir)
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = ProcessWorker(command_str, self.project_dir)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.output.connect(lambda msg: self.log.log(msg, "info"))
        self.worker.error.connect(lambda msg: self.log.log(msg, "error"))
        self.worker.finished.connect(self.on_script_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Start worker
        self.worker_thread.start()
        
    def on_script_finished(self, command, return_code):
        """Handle script completion"""
        if return_code == 0:
            self.log.log(f"Script completed successfully: {command}", "success")
        else:
            self.log.log(f"Script failed with code {return_code}: {command}", "error")
            
    def generate_moves_content(self):
        """Execute generateMovesContent.py script"""
        script_path = GENERATE_MOVES_SCRIPT.format(local=self.project_dir)
        self.run_script_async(script_path)
        
    def open_moves_directory(self):
        """Open moves content directory"""
        moves_path = CONTENT_MOVES_PATH.format(local=self.project_dir)
        self.open_directory(moves_path)
        
    def import_moves_data(self):
        """Import moves data with the new parameters"""
        input_format = self.import_input_format_combo.currentText()
        input_file = self.import_file_edit.text()
        output_format = self.import_output_format_combo.currentText()
        output_file = self.import_output_file_edit.text()
        changelog_dir = self.import_changelog_dir_edit.text()
        
        # Validation
        if not input_file or not os.path.exists(input_file):
            self.log.log("Please select a valid input file", "warning")
            return
            
        if not output_file:
            self.log.log("Please specify an output file", "warning")
            return
            
        # Use default changelog directory if empty
        if not changelog_dir:
            changelog_dir = MOVES_CHANGELOG_PATH.format(local=self.project_dir)
            self.import_changelog_dir_edit.setText(changelog_dir)
            
        # Confirmation dialog
        dialog = ConfirmationDialog(
            "Confirm Import", 
            f"Import Settings:\n"
            f"Input: {input_file} ({input_format})\n"
            f"Output: {output_file} ({output_format})\n"
            f"Changelog: {changelog_dir}\n\n"
            f"This will modify/replace the output file. Continue?",
            self
        )
        
        if dialog.exec() == QDialog.Accepted:
            script_path = IMPORT_MOVES_SCRIPT.format(local=self.project_dir)
            
            # Prepare arguments for the new script format
            args = [input_format, input_file, output_format, output_file, changelog_dir]
            
            self.run_script_async(script_path, *args)
        else:
            self.log.log("Import cancelled by user", "info")
            
    def open_moves_json(self):
        """Open current moves.json file"""
        moves_path = MOVES_DATA_PATH.format(local=self.project_dir)
        self.open_file(moves_path)
        
    def open_changelog_directory(self):
        """Open changelog directory"""
        changelog_path = self.import_changelog_dir_edit.text() or MOVES_CHANGELOG_PATH.format(local=self.project_dir)
        self.open_directory(changelog_path)
        
    def export_moves_data(self):
        """Export moves data"""
        filename = self.export_filename_edit.text()
        if not filename:
            self.log.log("Please enter an output filename", "warning")
            return
            
        export_format = self.export_format_combo.currentText()
        export_dir = self.export_dir_edit.text()
        template_file = self.export_template_edit.text()
        
        if not export_dir:
            self.log.log("Please select an export directory", "warning")
            return
            
        os.makedirs(export_dir, exist_ok=True)
        
        script_path = EXPORT_MOVES_SCRIPT.format(local=self.project_dir)
        args = [export_format, export_dir, filename]
        
        if export_format == ".docx" and template_file:
            args.append(template_file)
            
        self.run_script_async(script_path, *args)
        
        # Update most recent export path
        self.most_recent_export = os.path.join(export_dir, filename + export_format)
        self.open_recent_btn.setEnabled(True)
        self.open_recent_btn.setText(f"Open: {os.path.basename(self.most_recent_export)}")
        
    def open_generated_directory(self):
        """Open generated files directory"""
        gen_path = GENERATED_PATH.format(local=self.project_dir)
        self.open_directory(gen_path)
        
    def open_recent_export(self):
        """Open most recent export file"""
        if self.most_recent_export and os.path.exists(self.most_recent_export):
            self.open_file(self.most_recent_export)
        else:
            self.log.log("No recent export file found", "warning")
            
    def reset_git_repository(self):
        """Reset git repository with confirmation"""
        dialog = ConfirmationDialog(
            "Confirm Git Reset",
            "This will remove the old project and fetch a new one.\n\nThis is a destructive operation. Continue?",
            self
        )
        
        if dialog.exec() == QDialog.Accepted:
            script_path = RESET_GIT_SCRIPT.format(local=self.project_dir)
            self.run_script_async(script_path)
        else:
            self.log.log("Git reset cancelled by user", "info")
            
    def run_hugo_command(self, command):
        """Run a Hugo command"""
        if not self.project_dir:
            self.log.log("No project directory selected", "warning")
            return
            
        self.log.log_command(command, self.project_dir)
        
        # Kill existing Hugo process if running
        if hasattr(self, 'hugo_process') and self.hugo_process and self.hugo_process.state() != QProcess.NotRunning:
            self.hugo_process.kill()
            self.hugo_process.waitForFinished(3000)
            
        # Create new QProcess for Hugo commands
        self.hugo_process = QProcess(self)
        self.hugo_process.readyReadStandardOutput.connect(self.read_hugo_output)
        self.hugo_process.readyReadStandardError.connect(self.read_hugo_error)
        self.hugo_process.finished.connect(self.hugo_finished)
        self.hugo_process.setWorkingDirectory(self.project_dir)
        
        # Handle different platforms and command formats
        if sys.platform == "win32":
            # On Windows, use cmd.exe to run the command
            self.hugo_process.start("cmd.exe", ["/c", command])
        else:
            # On Unix-like systems, use shell
            self.hugo_process.start("/bin/sh", ["-c", command])
            
        if not self.hugo_process.waitForStarted(5000):
            self.log.log(f"Failed to start Hugo command: {command}", "error")
        else:
            self.log.log(f"Started Hugo command successfully", "info")
            
    def run_custom_hugo_command(self):
        """Run custom Hugo command"""
        custom_params = self.hugo_custom_edit.text().strip()
        if not custom_params:
            self.log.log("Please enter custom Hugo parameters", "warning")
            return
            
        command = f"hugo server {custom_params}"
        self.run_hugo_command(command)
        
    def stop_hugo_server(self):
        """Stop running Hugo server with aggressive termination"""
        if not hasattr(self, 'hugo_process') or not self.hugo_process:
            self.log.log("No Hugo server process found", "warning")
            return
            
        process_state = self.hugo_process.state()
        if process_state == QProcess.NotRunning:
            self.log.log("Hugo server is not running", "info")
            return
            
        self.log.log("Attempting to stop Hugo server...", "info")
        
        # Step 1: Try graceful termination first
        if process_state == QProcess.Running:
            self.hugo_process.terminate()
            if self.hugo_process.waitForFinished(3000):  # Wait 3 seconds
                self.log.log("Hugo server stopped gracefully", "success")
                return
            else:
                self.log.log("Graceful termination failed, forcing kill...", "warning")
        
        # Step 2: Force kill if still running
        if self.hugo_process.state() != QProcess.NotRunning:
            self.hugo_process.kill()
            if self.hugo_process.waitForFinished(5000):  # Wait 5 seconds
                self.log.log("Hugo server force killed", "success")
            else:
                self.log.log("Failed to kill Hugo process", "error")
                
        # Step 3: Additional cleanup - try to kill Hugo processes by name (platform specific)
        try:
            if sys.platform == "win32":
                # Windows: Kill hugo.exe processes
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", "hugo.exe"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.log.log("Killed remaining Hugo processes on Windows", "success")
                else:
                    if "not found" not in result.stderr.lower():
                        self.log.log(f"Windows taskkill result: {result.stderr.strip()}", "info")
            else:
                # Unix-like: Kill hugo processes
                result = subprocess.run(
                    ["pkill", "-f", "hugo server"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.log.log("Killed remaining Hugo processes on Unix", "success")
                # pkill returns 1 if no processes found, which is normal
                    
        except subprocess.TimeoutExpired:
            self.log.log("Process cleanup timed out", "warning")
        except FileNotFoundError:
            self.log.log("System process tools not available", "info")
        except Exception as e:
            self.log.log(f"Error during system-level process cleanup: {str(e)}", "warning")
            
        # Step 4: Try to verify the server is actually stopped
        self.log.log("Verifying Hugo server shutdown...", "info")
        try:
            # Check common Hugo ports
            still_running = []
            for port in [1313, 1314, 1315, 1316]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:  # Port still occupied
                    still_running.append(port)
                    
            if still_running:
                self.log.log(f"Warning: Ports still occupied: {still_running}", "warning")
                self.log.log("Hugo server may still be running or port not released yet", "warning")
            else:
                self.log.log("All common Hugo ports are free", "success")
                
        except Exception as e:
            self.log.log(f"Could not verify port status: {str(e)}", "info")
            
        # Reset our process reference
        self.hugo_process = None
        self.log.log("Hugo server stop sequence completed", "info")
            
    def read_hugo_output(self):
        """Read Hugo process stdout"""
        if self.hugo_process and self.hugo_process.state() != QProcess.NotRunning:
            data = self.hugo_process.readAllStandardOutput()
            output = bytes(data).decode('utf-8', errors='replace')
            for line in output.strip().split('\n'):
                if line.strip():
                    # Color code based on content
                    if "ERROR" in line.upper() or "FATAL" in line.upper():
                        self.log.log(f"Hugo: {line}", "error")
                    elif "WARN" in line.upper():
                        self.log.log(f"Hugo: {line}", "warning")
                    elif "Web Server is available at" in line or "Press Ctrl+C to stop" in line:
                        self.log.log(f"Hugo: {line}", "success")
                    else:
                        self.log.log(f"Hugo: {line}", "info")
                    
    def read_hugo_error(self):
        """Read Hugo process stderr"""
        if self.hugo_process and self.hugo_process.state() != QProcess.NotRunning:
            data = self.hugo_process.readAllStandardError()
            output = bytes(data).decode('utf-8', errors='replace')
            for line in output.strip().split('\n'):
                if line.strip():
                    self.log.log(f"Hugo Error: {line}", "error")
                    
    def hugo_finished(self, exit_code, exit_status):
        """Handle Hugo process completion"""
        if exit_code == 0:
            self.log.log("Hugo command completed successfully", "success")
        else:
            self.log.log(f"Hugo command failed with exit code {exit_code}", "error")
            
        # Additional debug info
        if hasattr(self, 'hugo_process') and self.hugo_process:
            if exit_code != 0:
                error_string = self.hugo_process.errorString()
                if error_string:
                    self.log.log(f"Hugo process error: {error_string}", "error")
            
    def open_file(self, file_path):
        """Open a file with system default application"""
        if not os.path.exists(file_path):
            self.log.log(f"File not found: {file_path}", "error")
            return
            
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
                
            self.log.log(f"Opened file: {file_path}", "info")
        except Exception as e:
            self.log.log(f"Error opening file: {str(e)}", "error")
            
    def open_directory(self, dir_path):
        """Open a directory with system file explorer"""
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            
        try:
            if sys.platform == "win32":
                os.startfile(dir_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", dir_path])
            else:
                subprocess.run(["xdg-open", dir_path])
                
            self.log.log(f"Opened directory: {dir_path}", "info")
        except Exception as e:
            self.log.log(f"Error opening directory: {str(e)}", "error")
            
    def closeEvent(self, event):
        """Handle application close event"""
        self.save_ui_data()
        
        # Properly terminate Hugo process
        if hasattr(self, 'hugo_process') and self.hugo_process and self.hugo_process.state() != QProcess.NotRunning:
            self.log.log("Shutting down Hugo server...", "info")
            self.hugo_process.kill()
            self.hugo_process.waitForFinished(3000)
            
        # Cleanup worker threads
        if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait(3000)
            
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Hugo Blog Manager")
    app.setApplicationVersion("1.0")
    
    window = HugoBlogManager()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()