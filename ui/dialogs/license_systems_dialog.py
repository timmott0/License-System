from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QCheckBox, QPushButton, QFormLayout, QGroupBox, QLineEdit, QSpinBox,
                           QDialogButtonBox, QMessageBox)  # Added QMessageBox
from PyQt5.QtCore import Qt, QSize
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
        # Set a minimum size for the dialog
        self.setMinimumSize(QSize(400, 200))
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)
        
        # System selection and basic settings
        system_layout = QFormLayout()
        self.system_combo = QComboBox()
        for system_id, system in self.config.get('license_systems', {}).items():
            self.system_combo.addItem(system['name'], system_id)
        system_layout.addRow("License System:", self.system_combo)
        
        # Server settings for custom types
        self.server_group = QGroupBox("Server Settings")
        server_layout = QFormLayout()
        
        self.server_host = QLineEdit()
        self.server_port = QSpinBox()
        self.server_port.setRange(1, 65535)
        
        server_layout.addRow("Host:", self.server_host)
        server_layout.addRow("Port:", self.server_port)
        
        # SSL settings
        self.use_ssl = QCheckBox("Use SSL/TLS")
        self.verify_ssl = QCheckBox("Verify SSL Certificate")
        server_layout.addRow("", self.use_ssl)
        server_layout.addRow("", self.verify_ssl)
        
        self.server_group.setLayout(server_layout)
        layout.addWidget(self.server_group)
        
        # Credentials group
        credentials_group = QGroupBox("Credentials")
        credentials_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.save_credentials_cb = QCheckBox("Save credentials")
        
        credentials_layout.addRow("Username:", self.username_edit)
        credentials_layout.addRow("Password:", self.password_edit)
        credentials_layout.addRow("", self.save_credentials_cb)
        
        credentials_group.setLayout(credentials_layout)
        layout.addWidget(credentials_group)
        
        # OK/Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.system_combo.currentIndexChanged.connect(self.update_system_info)
        self.use_ssl.toggled.connect(self.on_ssl_toggled)
        
        self.update_system_info()

    def accept(self):
        """Save settings when OK is clicked"""
        system_id = self.system_combo.currentData()
        if not system_id:
            QMessageBox.warning(self, "Error", "Please select a license system")
            return
        
        system = self.config['license_systems'][system_id]
        
        # Save custom server settings
        if system.get('system_type') == 'custom':
            host = self.server_host.text().strip()
            if not host:
                QMessageBox.warning(self, "Error", "Please enter a server host")
                return
            
            system['host'] = host
            system['default_port'] = self.server_port.value()
            system['use_ssl'] = self.use_ssl.isChecked()
            system['verify_ssl'] = self.verify_ssl.isChecked()
        
        # Save credentials if checked
        if self.save_credentials_cb.isChecked():
            if not self.username_edit.text().strip():
                QMessageBox.warning(self, "Error", "Please enter a username")
                return
                
            import keyring
            host = system.get('host', '')
            keyring.set_password(
                "license_manager",
                f"{host}_username",
                self.username_edit.text()
            )
            keyring.set_password(
                "license_manager",
                f"{host}_password",
                self.password_edit.text()
            )
        
        super().accept()

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

    def on_ssl_toggled(self, checked):
        """Handle SSL checkbox state changes"""
        self.verify_ssl.setEnabled(checked)
        if not checked:
            self.verify_ssl.setChecked(False)
