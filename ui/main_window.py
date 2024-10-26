from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QMenuBar, QMenu, QAction, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from .license_frame import LicenseFrame
from .dialogs.eval_dialog import EvalDialog
from .dialogs.common_settings import CommonSettingsDialog
from pathlib import Path
import json
from .dialogs.license_systems_dialog import LicenseSystemsDialog

class MainWindow(QMainWindow):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        # Add default config paths if not present
        if 'paths' not in self.config:
            self.config['paths'] = {'config': 'src/config'}
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface"""
        # Set minimum window dimensions to prevent UI from breaking
        self.setMinimumSize(QSize(1000, 800))
        
        # Main stylesheet for the entire application
        self.setStyleSheet("""
            /* Main window background */
            QMainWindow {
                background-color: #fafafa;  /* Light gray background for better contrast */
            }
            
            /* Top menu bar styling */
            QMenuBar {
                background-color: #ffffff;  /* White background */
                border-bottom: 1px solid #f0f0f0;  /* Subtle separator */
                padding: 10px 0px;  /* Vertical padding for better clickability */
                font-size: 13px;  /* Standard readable font size */
            }
            
            /* Individual menu items in the top bar */
            QMenuBar::item {
                padding: 8px 12px;  /* Padding around menu items */
                margin: 0px 4px;    /* Space between items */
                border-radius: 6px;  /* Rounded corners */
                color: #424242;      /* Dark gray text for readability */
            }
            
            /* Hover state for menu items */
            QMenuBar::item:selected {
                background-color: #f5f5f5;  /* Light gray background on hover */
                color: #1a73e8;            /* Google Blue for selected items */
            }
            
            /* Dropdown menus */
            QMenu {
                background-color: #ffffff;  /* White background */
                border: 1px solid #f0f0f0;  /* Subtle border */
                border-radius: 8px;         /* Rounded corners */
                padding: 8px 4px;           /* Inner spacing */
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);  /* Subtle drop shadow */
            }
            
            /* Dropdown menu items */
            QMenu::item {
                padding: 10px 30px;  /* Comfortable clicking area */
                border-radius: 6px;  /* Rounded corners */
                margin: 2px 4px;     /* Spacing between items looks odd TM */
                color: #424242;      /* Dark gray text */
            }
            
            /* Hover state for dropdown items */
            QMenu::item:selected {
                background-color: #f8f9fa;  /* Very light gray background */
                color: #1a73e8;            /* Google Blue */
            }
            
            /* Menu separators */
            QMenu::separator {
                height: 1px;                 /* Thin line */
                background-color: #f0f0f0;   /* Light gray */
                margin: 6px 15px;            /* Spacing around separator */
            }
            
            /* Global font settings */
            QWidget {
                /* System font stack - falls back to next font if first isn't available */
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 13px;
            }
            
            /* Button styling */
            QPushButton {
                background-color: #1a73e8;  /* Google Blue */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;           /* Semi-bold text */
                min-width: 80px;            /* Minimum button width */
            }
            
            /* Button states */
            QPushButton:hover {
                background-color: #1557b0;  /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #174ea6;  /* Even darker when clicked */
            }
            QPushButton:disabled {
                background-color: #e0e0e0;  /* Gray when disabled */
                color: #9e9e9e;
            }
            
            /* Input fields styling */
            QLineEdit, QTextEdit, QComboBox {
                padding: 10px;
                border: 1.5px solid #e0e0e0;  /* Light gray border */
                border-radius: 6px;
                background-color: #ffffff;
                color: #424242;
                selection-background-color: #e8f0fe;  /* Light blue selection */
                selection-color: #1a73e8;
            }
            
            /* Input field focus and hover states */
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #1a73e8;  /* Blue border when focused */
                padding: 9px;               /* Adjust padding to prevent size jump */
            }
            QLineEdit:hover, QTextEdit:hover, QComboBox:hover {
                border: 1.5px solid #bdbdbd;  /* Darker border on hover */
            }
            
            /* Frame containers */
            QFrame {
                border-radius: 10px;
                background-color: #ffffff;
                border: 1px solid #f0f0f0;
            }
            
            /* Custom scrollbar styling */
            QScrollBar:vertical {
                border: none;
                background-color: #f5f5f5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdbdbd;  /* Gray scrollbar handle */
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9e9e9e;  /* Darker on hover */
            }
        """)
        
        # Create main layout container and set it as the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Set up the main vertical layout with generous margins
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(32, 32, 32, 32)  # Left, Top, Right, Bottom margins
        self.layout.setSpacing(20)  # Space between widgets
        
        # Create license frame and add it to the layout
        self.license_frame = LicenseFrame(self, config=self.config)  # Pass config here
        self.layout.addWidget(self.license_frame)
        #TODO: Add the eval frame to the layout
        self.create_menu_bar()
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New License', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_license)
        file_menu.addAction(new_action)
        
        open_action = QAction('&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_license)
        file_menu.addAction(open_action)
        
        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_license)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu('&Tools')
        
        settings_action = QAction('&Settings...', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Add License Systems configuration to Tools menu
        license_systems_action = QAction('License &Systems...', self)
        license_systems_action.triggered.connect(self.show_license_systems)
        tools_menu.addAction(license_systems_action)
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def new_license(self):
        """Create a new license"""
        # TODO: Implement new license creation
        pass

    def open_license(self):
        """Open an existing license"""
        # TODO: Implement license opening
        pass

    def save_license(self):
        """Save the current license"""
        # TODO: Implement license saving
        pass

    def show_settings(self):
        """Show the settings dialog"""
        dialog = CommonSettingsDialog(self.config, self)
        dialog.exec_()

    def show_about(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "About License Management System",
            f"License Management System\nVersion: {self.config.get('application', {}).get('version', '1.0.0')}\n\
            {self.config.get('application', {}).get('description', 'A secure system for creating and managing software licenses. Developed by Timothy Mott.')}"
        )

    def show_license_systems(self):
        """Show the license systems configuration dialog"""
        try:
            from config.license_systems import DEFAULT_SYSTEMS
            
            # Initialize license systems if not present
            if 'license_systems' not in self.config:
                print("Initializing license systems in config")
                self.config['license_systems'] = {
                    system_id: {
                        "name": system.name,
                        "enabled": system.enabled,
                        "install_path": str(system.install_path),
                        "default_port": system.default_port,
                        "description": system.description
                    }
                    for system_id, system in DEFAULT_SYSTEMS.items()
                }
            
            dialog = LicenseSystemsDialog(self.config, self)
            result = dialog.exec_()
            print(f"Dialog result: {result}")
            
            if result == QDialog.Accepted:
                # Save the updated configuration
                system_id = dialog.system_combo.currentData()
                if system_id:
                    self.config['license_systems'][system_id]['enabled'] = dialog.enabled_checkbox.isChecked()
                    print(f"Updated system {system_id} enabled status to {dialog.enabled_checkbox.isChecked()}")
                    
        except Exception as e:
            print(f"Error in show_license_systems: {str(e)}")
            QMessageBox.warning(
                self,
                "Warning",
                f"Could not open license systems configuration: {str(e)}"
            )
