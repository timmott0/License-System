from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLabel, QLineEdit, QSpinBox, QPushButton,
                           QCheckBox, QTabWidget, QWidget)
from PyQt5.QtCore import Qt

class CommonSettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # General Settings Tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        self.default_validity = QSpinBox()
        self.default_validity.setRange(1, 9999)
        self.default_validity.setValue(
            self.config.get('defaults', {}).get('validity_period', 365)
        )
        general_layout.addRow("Default Validity (days):", self.default_validity)
        
        self.default_maintenance = QSpinBox()
        self.default_maintenance.setRange(0, 9999)
        self.default_maintenance.setValue(
            self.config.get('defaults', {}).get('maintenance_period', 90)
        )
        general_layout.addRow("Default Maintenance (days):", self.default_maintenance)
        
        tab_widget.addTab(general_tab, "General")
        
        # Paths Tab
        paths_tab = QWidget()
        paths_layout = QFormLayout(paths_tab)
        
        self.license_path = QLineEdit()
        self.license_path.setText(
            self.config.get('paths', {}).get('license_storage', 'licenses/')
        )
        paths_layout.addRow("License Storage Path:", self.license_path)
        
        self.backup_path = QLineEdit()
        self.backup_path.setText(
            self.config.get('paths', {}).get('backup', 'backup/')
        )
        paths_layout.addRow("Backup Path:", self.backup_path)
        
        tab_widget.addTab(paths_tab, "Paths")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def save_settings(self):
        """Save the modified settings"""
        # Update config with new values
        if 'defaults' not in self.config:
            self.config['defaults'] = {}
        self.config
