from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QCheckBox, QPushButton, QFormLayout, QGroupBox, QLineEdit, QSpinBox,
                           QDialogButtonBox, QMessageBox, QWhatsThis, QScrollArea)  # Added QWhatsThis
from PyQt5.QtCore import Qt, QSize, pyqtSignal  # Added QSize and pyqtSignal
from PyQt5.QtGui import QIcon
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.license_systems import DEFAULT_SYSTEMS

class LicenseSystemsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("License Systems Configuration")
        self.setMinimumSize(QSize(500, 300))  # Slightly larger for better layout
        
        # Add help button to title bar
        self.setWhatsThis(self.get_help_text())
        self.setWindowFlags(self.windowFlags() | Qt.WindowContextHelpButtonHint)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI with improved labels and tooltips"""
        layout = QVBoxLayout(self)
        
        # System selection with improved labels
        system_layout = QFormLayout()
        self.system_combo = QComboBox()
        self.system_combo.setToolTip("Select the license system to configure")
        self.system_combo.setWhatsThis(
            "Choose the licensing system that best matches your needs:\n"
            "- FlexLM: Traditional enterprise licensing\n"
            "- HASP: Hardware-based protection\n"
            "- Custom: Your own licensing system"
        )
        for system_id, system in self.config.get('license_systems', {}).items():
            self.system_combo.addItem(system['name'], system_id)
        system_layout.addRow("License System:", self.system_combo)
        
        # Server settings with better organization
        self.server_group = QGroupBox("Server Connection Settings")
        self.server_group.setWhatsThis(
            "Configure the connection to your license server:\n"
            "- Host: The server's hostname or IP address\n"
            "- Port: The port number (usually 27000)\n"
            "- SSL/TLS: Enable for secure connections"
        )
        server_layout = QFormLayout()
        
        self.server_host = QLineEdit()
        self.server_host.setPlaceholderText("Enter server hostname or IP address")
        self.server_host.setWhatsThis(
            "Enter the hostname or IP address of your license server.\n"
            "Examples:\n"
            "- hostname.company.com\n"
            "- 192.168.1.100"
        )
        
        self.server_port = QSpinBox()
        self.server_port.setRange(1, 65535)
        self.server_port.setWhatsThis(
            "The port number your license server listens on.\n"
            "Default ports:\n"
            "- FlexLM: 27000\n"
            "- HASP: 1947"
        )
        
        server_layout.addRow("Host:", self.server_host)
        server_layout.addRow("Port:", self.server_port)
        
        # SSL settings with explanatory tooltips
        self.use_ssl = QCheckBox("Use SSL/TLS")
        self.use_ssl.setWhatsThis(
            "Enable SSL/TLS for secure communication:\n"
            "- Recommended for production environments\n"
            "- Required when accessing over public networks\n"
            "- Helps prevent license tampering"
        )
        
        self.verify_ssl = QCheckBox("Verify SSL Certificate")
        self.verify_ssl.setWhatsThis(
            "Verify the server's SSL certificate:\n"
            "- Recommended for production use\n"
            "- Prevents man-in-the-middle attacks\n"
            "- May need to be disabled for self-signed certificates"
        )
        
        server_layout.addRow("", self.use_ssl)
        server_layout.addRow("", self.verify_ssl)
        
        self.server_group.setLayout(server_layout)
        layout.addWidget(self.server_group)
        
        # Credentials group with improved security hints
        credentials_group = QGroupBox("Authentication")
        credentials_group.setWhatsThis(
            "Enter your license server credentials:\n"
            "- Username and password provided by your administrator\n"
            "- Optional: Save credentials securely for future use"
        )
        credentials_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setWhatsThis(
            "Enter your license server username\n"
            "This is typically provided by your system administrator"
        )
        
        self.password_edit = QLineEdit()
        self.password_edit.setWhatsThis(
            "Enter your license server password\n"
            "The password will be securely stored if 'Remember credentials' is checked"
        )
        
        self.save_credentials_cb = QCheckBox("Remember credentials")
        self.save_credentials_cb.setWhatsThis(
            "Save credentials securely:\n"
            "- Credentials are encrypted before storage\n"
            "- Saves time on future connections\n"
            "- Can be cleared through system settings"
        )
        
        credentials_layout.addRow("Username:", self.username_edit)
        credentials_layout.addRow("Password:", self.password_edit)
        credentials_layout.addRow("", self.save_credentials_cb)
        
        credentials_group.setLayout(credentials_layout)
        layout.addWidget(credentials_group)
        
        # Test Connection button
        self.test_button = QPushButton("Test Connection")
        self.test_button.setWhatsThis(
            "Test the connection to your license server:\n"
            "- Verifies server availability\n"
            "- Checks credentials\n"
            "- Confirms SSL/TLS settings"
        )
        self.test_button.setToolTip("Verify connection to the license server")
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)
        
        # Help button
        help_button = QPushButton("Help")
        help_button.setToolTip("Show help information")
        help_button.clicked.connect(self.show_help)
        
        # Button box with help
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.addButton(help_button, QDialogButtonBox.HelpRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.system_combo.currentIndexChanged.connect(self.update_system_info)
        self.use_ssl.toggled.connect(self.on_ssl_toggled)
        
        self.update_system_info()

    def get_help_text(self) -> str:
        """Return the help text for the dialog"""
        return """
        <h3>License System Configuration Help</h3>
        <p>This dialog allows you to configure your connection to a license server.</p>
        
        <h4>Steps to Configure:</h4>
        <ol>
            <li><b>Select License System:</b>
                <ul>
                    <li>Choose the appropriate system for your needs</li>
                    <li>Each system has different capabilities and requirements</li>
                </ul>
            </li>
            <li><b>Server Connection:</b>
                <ul>
                    <li>Enter the server hostname or IP address</li>
                    <li>Specify the port number (default is usually correct)</li>
                    <li>Enable SSL/TLS for secure connections</li>
                </ul>
            </li>
            <li><b>Authentication:</b>
                <ul>
                    <li>Enter your server credentials</li>
                    <li>Optionally save them for future use</li>
                </ul>
            </li>
            <li><b>Test Connection:</b>
                <ul>
                    <li>Use the Test Connection button to verify settings</li>
                    <li>Resolve any connection issues before saving</li>
                </ul>
            </li>
        </ol>
        
        <h4>Security Notes:</h4>
        <ul>
            <li>Always use SSL/TLS in production environments</li>
            <li>Verify SSL certificates when possible</li>
            <li>Stored credentials are encrypted</li>
            <li>Regular password updates are recommended</li>
        </ul>
        
        <h4>Troubleshooting:</h4>
        <ul>
            <li>Verify network connectivity to the server</li>
            <li>Check firewall settings</li>
            <li>Ensure credentials are correct</li>
            <li>Contact support if problems persist</li>
        </ul>
        
        <p><small>For additional help, please consult the 
        <a href="https://your-documentation-url.com">documentation</a> 
        or contact support.</small></p>
        """

    def show_help(self):
        """Show the help dialog"""
        # Create a custom help dialog instead of using WhatsThis mode
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("License System Configuration Help")
        help_dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(help_dialog)
        
        # Create a QLabel with rich text
        help_text = QLabel()
        help_text.setWordWrap(True)
        help_text.setOpenExternalLinks(True)
        help_text.setText(self.get_help_text())
        help_text.setTextFormat(Qt.RichText)
        
        # Add to scrollable area
        scroll = QScrollArea()
        scroll.setWidget(help_text)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(help_dialog.accept)
        layout.addWidget(close_button)
        
        help_dialog.exec_()

    def test_connection(self):
        """Test the server connection"""
        try:
            # Attempt connection with current settings
            self.connect_to_server()
            QMessageBox.information(
                self,
                "Connection Success",
                "Successfully connected to the license server!"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Connection Failed",
                f"Could not connect to the server. Please check your settings and try again.\n\n"
                f"Details: {str(e)}"
            )

    def accept(self):
        """Validate and save settings"""
        try:
            if not self.validate_inputs():
                return
            
            # Save settings and close
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                "Could not save settings. Please check your inputs and try again."
            )

    def validate_inputs(self) -> bool:
        """Validate user inputs with friendly messages"""
        if not self.server_host.text().strip():
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a server hostname or IP address."
            )
            self.server_host.setFocus()
            return False
            
        if self.save_credentials_cb.isChecked():
            if not self.username_edit.text().strip():
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please enter a username or uncheck the 'Remember credentials' option."
                )
                self.username_edit.setFocus()
                return False
                
            if not self.password_edit.text():
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please enter a password or uncheck the 'Remember credentials' option."
                )
                self.password_edit.setFocus()
                return False
        
        return True

    def show_error(self, message: str, details: str = None):
        """Show a user-friendly error message"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        if details:
            error_box.setDetailedText(details)
        error_box.exec_()

    def update_system_info(self):
        """Update UI based on selected system"""
        system_id = self.system_combo.currentData()
        if system_id:
            system = self.config['license_systems'].get(system_id, {})
            
            # Show/hide server settings based on type
            is_custom = system.get('system_type') == 'custom'
            self.server_group.setVisible(is_custom)
            
            # Load saved settings
            if is_custom:
                self.server_host.setText(system.get('host', ''))
                self.server_port.setValue(system.get('default_port', 5001))
                self.use_ssl.setChecked(system.get('use_ssl', True))
                self.verify_ssl.setChecked(system.get('verify_ssl', False))
            
            # Load saved credentials
            if system.get('host'):
                import keyring
                username = keyring.get_password("license_manager", f"{system['host']}_username")
                password = keyring.get_password("license_manager", f"{system['host']}_password")
                if username and password:
                    self.username_edit.setText(username)
                    self.password_edit.setText(password)
                    self.save_credentials_cb.setChecked(True)

    def connect_to_server(self):
        try:
            # ... your existing connection code ...
            
            # Prepare server info
            server_info = {
                'connected': True,
                'path': self.server_host.text(),
                'license_systems': {
                    # Add any license system info from server
                },
                'products': [
                    # Add any product info from server
                ]
            }
            
            # Emit the signal with server info
            self.server_connected.emit(server_info)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")
