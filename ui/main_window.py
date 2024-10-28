from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QMenuBar, QMenu, QAction, QMessageBox, QDialog, QFileDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from .license_frame import LicenseFrame
from .dialogs.eval_dialog import EvalDialog
from .dialogs.common_settings import CommonSettingsDialog
from pathlib import Path
import json
from .dialogs.license_systems_dialog import LicenseSystemsDialog
from core.license_generator import LicenseType
from .dialogs.server_sync_dialog import ServerSyncDialog  # Add this import
from .dialogs.user_guide import UserGuideDialog

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
        
        # Products Menu
        products_menu = menubar.addMenu('&Products')
        
        manage_products_action = QAction('&Manage Products...', self)
        manage_products_action.triggered.connect(self.show_product_manager)
        products_menu.addAction(manage_products_action)
        
        sync_products_action = QAction('&Sync Products...', self)
        sync_products_action.triggered.connect(self.sync_products)
        products_menu.addAction(sync_products_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu('&Tools')
        
        settings_action = QAction('&Settings...', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Add License Systems configuration to Tools menu
        license_systems_action = QAction('License &Systems...', self)
        license_systems_action.triggered.connect(self.show_license_systems)
        tools_menu.addAction(license_systems_action)
        
        # Add Key Management to Tools menu
        key_management_action = QAction('&Key Management...', self)
        key_management_action.triggered.connect(self.show_key_management)
        tools_menu.addAction(key_management_action)
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        # User Guide
        user_guide_action = QAction('User Guide', self)
        user_guide_action.setShortcut('F1')  # Add F1 shortcut for quick access
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
        
        # About
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def new_license(self):
        """Create a new license"""
        # Clear all fields in the license frame
        self.license_frame.clear_fields()
        
        # Optionally set default values if needed
        self.license_frame.set_default_values()

    def open_license(self):
        """Open an existing license"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open License File",
            "",
            "License Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    license_data = json.load(file)
                    self.license_frame.load_data(license_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open license: {str(e)}")

    def save_license(self):
        """Save the current license"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save License File",
            "",
            "License Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                license_data = self.license_frame.get_data()
                with open(file_path, 'w') as file:
                    json.dump(license_data, file, indent=4)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save license: {str(e)}")

    def show_settings(self):
        """Show the settings dialog"""
        dialog = CommonSettingsDialog(self.config, self)
        if dialog.exec_():
            # Save the updated config
            try:
                config_path = Path(self.config['paths']['config']) / 'config.json'
                with open(config_path, 'w') as f:
                    json.dump(self.config, f, indent=4)
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "Settings have been saved successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save settings: {str(e)}"
                )

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
                        "system_type": system.system_type,  # Add this
                        "install_path": str(system.install_path) if system.install_path else None,
                        "default_port": system.default_port,
                        "description": system.description,
                        "database_config": {  # Add this block
                            "type": system.database_config.type,
                            "host": system.database_config.host,
                            "port": system.database_config.port,
                            "database": system.database_config.database,
                            "username": system.database_config.username,
                            "connection_string": system.database_config.connection_string
                        } if system.database_config else None
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

    def show_product_manager(self):
        """Show the product manager dialog"""
        from .dialogs.product_manager_dialog import ProductManagerDialog
        dialog = ProductManagerDialog(self.config, self)
        if dialog.exec_():
            # Save updated products to config
            self.save_products_config()
            # Update product dropdown in license frame
            self.license_frame.refresh_product_list()

    def sync_products(self):
        """Synchronize products with server"""
        try:
            dialog = ServerSyncDialog(self.config, self)
            if dialog.exec_():
                # Refresh local product list after sync
                self.load_products_from_server()
                self.license_frame.refresh_product_list()
                QMessageBox.information(
                    self,
                    "Sync Complete",
                    "Products have been synchronized successfully."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Sync Error",
                f"Failed to synchronize products: {str(e)}"
            )

    def save_products_config(self):
        """Save products configuration to file"""
        try:
            products_file = Path(self.config['paths']['config']) / 'products.json'
            with open(products_file, 'w') as f:
                json.dump(self.config['products'], f, indent=4)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save products configuration: {str(e)}"
            )

    def show_key_management(self):
        """Launch the key management GUI"""
        try:
            import subprocess
            import sys
            from pathlib import Path
            
            # Get the path to the key management script
            key_mgmt_path = Path(__file__).parent.parent / 'tools' / 'key_management_gui.py'
            
            if not key_mgmt_path.exists():
                raise FileNotFoundError(f"Key management script not found at {key_mgmt_path}")
            
            # Launch the key management GUI as a separate process
            process = subprocess.Popen([sys.executable, str(key_mgmt_path)])
            
            # Optional: Wait for the process to complete
            # process.wait()
            
            # Refresh the license frame if needed
            # self.license_frame.refresh_key_info()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to launch key management: {str(e)}"
            )

    def show_user_guide(self):
        """Show the user guide dialog"""
        guide = UserGuideDialog(self)
        guide.exec_()

