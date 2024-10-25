from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QCheckBox, QPushButton, QFormLayout)
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
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add a label at the top
        title_label = QLabel("Configure License Systems")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Debug print
        print("Config contents:", self.config)
        print("License systems in config:", self.config.get('license_systems', {}))
        
        # Create combo box for license systems
        self.system_combo = QComboBox()
        self.system_combo.setMinimumWidth(200)  # Set minimum width
        
        # Populate combo box
        license_systems = self.config.get('license_systems', {})
        if not license_systems:
            print("No license systems found, using DEFAULT_SYSTEMS")
            # Use DEFAULT_SYSTEMS if no systems in config
            from config.license_systems import DEFAULT_SYSTEMS
            license_systems = {
                system_id: {
                    "name": system.name,
                    "enabled": system.enabled,
                    "install_path": str(system.install_path),
                    "default_port": system.default_port,
                    "description": system.description
                }
                for system_id, system in DEFAULT_SYSTEMS.items()
            }
            self.config['license_systems'] = license_systems
        
        for system_id, system_data in license_systems.items():
            print(f"Adding system to combo box: {system_data['name']} ({system_id})")
            self.system_combo.addItem(system_data['name'], system_id)
        
        form_layout.addRow("License System:", self.system_combo)
        
        # Create enabled checkbox
        self.enabled_checkbox = QCheckBox("Enabled")
        form_layout.addRow("Status:", self.enabled_checkbox)
        
        # Add description label
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        form_layout.addRow("Description:", self.description_label)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add spacer
        layout.addStretch()
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.setFixedWidth(100)
        cancel_button.setFixedWidth(100)
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Connect combo box change to update UI
        self.system_combo.currentIndexChanged.connect(self.update_system_status)
        self.update_system_status()  # Initialize with current selection
        
    def update_system_status(self):
        system_id = self.system_combo.currentData()
        if system_id:
            system_data = self.config['license_systems'].get(system_id, {})
            self.enabled_checkbox.setChecked(system_data.get('enabled', False))
            self.description_label.setText(system_data.get('description', ''))
            print(f"Updated status for system {system_id}: {system_data}")
