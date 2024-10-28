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
        
        # Enable/Disable checkbox
        self.enabled_checkbox = QCheckBox("Enabled")
        system_layout.addRow("", self.enabled_checkbox)
        
        # Description label
        self.description_label = QLabel()
        system_layout.addRow("Description:", self.description_label)
        
        layout.addLayout(system_layout)
        
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
        self.update_system_info()

    def accept(self):
        """Save settings when OK is clicked"""
        system_id = self.system_combo.currentData()
        if not system_id:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please select a license system."
            )
            return

        # Update system configuration
        system_data = self.config['license_systems'][system_id]
        system_data['enabled'] = self.enabled_checkbox.isChecked()
        
        # Handle credentials
        if self.save_credentials_cb.isChecked():
            if not self.username_edit.text().strip():
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please enter a username."
                )
                return
            
            # Save credentials securely using keyring
            import keyring
            keyring.set_password(
                "license_manager",
                f"{system_id}_username",
                self.username_edit.text()
            )
            keyring.set_password(
                "license_manager",
                f"{system_id}_password",
                self.password_edit.text()
            )
        else:
            # Remove any saved credentials
            import keyring
            try:
                keyring.delete_password("license_manager", f"{system_id}_username")
                keyring.delete_password("license_manager", f"{system_id}_password")
            except keyring.errors.PasswordDeleteError:
                pass  # No saved credentials to delete
        
        super().accept()

    def update_system_info(self):
        """Update UI with system info and load saved credentials"""
        system_id = self.system_combo.currentData()
        if system_id:
            system_data = self.config['license_systems'].get(system_id, {})
            self.enabled_checkbox.setChecked(system_data.get('enabled', False))
            self.description_label.setText(system_data.get('description', ''))
            print(f"Updated status for system {system_id}: {system_data}")
            
            # Load saved credentials if they exist
            import keyring
            saved_username = keyring.get_password("license_manager", f"{system_id}_username")
            saved_password = keyring.get_password("license_manager", f"{system_id}_password")
            
            if saved_username and saved_password:
                self.username_edit.setText(saved_username)
                self.password_edit.setText(saved_password)
                self.save_credentials_cb.setChecked(True)
            else:
                self.username_edit.clear()
                self.password_edit.clear()
                self.save_credentials_cb.setChecked(False)
