from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLabel, QLineEdit, QSpinBox, QPushButton,
                           QCheckBox, QTabWidget, QWidget, QTableWidget,
                           QTableWidgetItem, QMessageBox, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt
from security.credentials_manager import CredentialsManager
from .credentials_dialog import CredentialsDialog

class CommonSettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.credentials_manager = CredentialsManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the settings dialog UI"""
        self.setWindowTitle("Settings")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # General Settings Tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")
        
        # Server Credentials Tab
        credentials_tab = self.create_credentials_tab()
        tab_widget.addTab(credentials_tab, "Server Credentials")
        
        layout.addWidget(tab_widget)
        
        # Add OK/Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def create_general_tab(self):
        """Create the general settings tab with server connection settings"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Server Connection Settings group
        server_group = QGroupBox("Server Connection")
        server_layout = QFormLayout()
        
        # Primary Server
        self.primary_server_host = QLineEdit()
        self.primary_server_port = QSpinBox()
        self.primary_server_port.setRange(1, 65535)
        self.primary_server_port.setValue(self.config.get('server', {}).get('port', 27000))
        
        server_layout.addRow("Primary Server Host:", self.primary_server_host)
        server_layout.addRow("Primary Server Port:", self.primary_server_port)
        
        # Backup Server (Optional)
        self.backup_server_host = QLineEdit()
        self.backup_server_port = QSpinBox()
        self.backup_server_port.setRange(1, 65535)
        self.backup_server_port.setValue(self.config.get('backup_server', {}).get('port', 27000))
        
        server_layout.addRow("Backup Server Host:", self.backup_server_host)
        server_layout.addRow("Backup Server Port:", self.backup_server_port)
        
        # Connection Settings
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 300)  # 1-300 seconds
        self.timeout_spinbox.setValue(self.config.get('connection', {}).get('timeout', 30))
        server_layout.addRow("Connection Timeout (seconds):", self.timeout_spinbox)
        
        self.retry_spinbox = QSpinBox()
        self.retry_spinbox.setRange(0, 10)  # 0-10 retries
        self.retry_spinbox.setValue(self.config.get('connection', {}).get('max_retries', 3))
        server_layout.addRow("Max Retry Attempts:", self.retry_spinbox)
        
        # SSL/TLS Settings
        self.use_ssl = QCheckBox("Use SSL/TLS")
        self.use_ssl.setChecked(self.config.get('connection', {}).get('use_ssl', True))
        server_layout.addRow("", self.use_ssl)
        
        self.verify_ssl = QCheckBox("Verify SSL Certificate")
        self.verify_ssl.setChecked(self.config.get('connection', {}).get('verify_ssl', True))
        server_layout.addRow("", self.verify_ssl)
        
        # Custom Certificate Path
        self.cert_path = QLineEdit()
        self.cert_path.setText(self.config.get('connection', {}).get('cert_path', ''))
        cert_browse_btn = QPushButton("Browse...")
        cert_browse_btn.clicked.connect(self.browse_cert_path)
        
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(self.cert_path)
        cert_layout.addWidget(cert_browse_btn)
        server_layout.addRow("Custom Certificate Path:", cert_layout)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # License File Settings group
        license_group = QGroupBox("License File Settings")
        license_layout = QFormLayout()
        
        # Default save path
        self.default_save_path = QLineEdit()
        self.default_save_path.setText(self.config.get('paths', {}).get('default_save', ''))
        save_browse_btn = QPushButton("Browse...")
        save_browse_btn.clicked.connect(self.browse_save_path)
        
        save_layout = QHBoxLayout()
        save_layout.addWidget(self.default_save_path)
        save_layout.addWidget(save_browse_btn)
        license_layout.addRow("Default Save Path:", save_layout)
        
        license_group.setLayout(license_layout)
        layout.addWidget(license_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_credentials_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create table for stored credentials
        self.credentials_table = QTableWidget(0, 2)  # 2 columns: Server Path, Username
        self.credentials_table.setHorizontalHeaderLabels(["Server Path", "Username"])
        self.credentials_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.credentials_table)
        
        # Buttons for managing credentials
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        edit_button = QPushButton("Edit")
        remove_button = QPushButton("Remove")
        
        add_button.clicked.connect(self.add_credentials)
        edit_button.clicked.connect(self.edit_credentials)
        remove_button.clicked.connect(self.remove_credentials)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(remove_button)
        layout.addLayout(button_layout)
        
        # Load existing credentials
        self.load_credentials()
        
        return widget
        
    def load_credentials(self):
        """Load existing credentials into the table"""
        self.credentials_table.setRowCount(0)
        stored_paths = self.credentials_manager.get_stored_paths()
        
        for path in stored_paths:
            credentials = self.credentials_manager.get_credentials(path)
            if credentials:
                row = self.credentials_table.rowCount()
                self.credentials_table.insertRow(row)
                self.credentials_table.setItem(row, 0, QTableWidgetItem(path))
                self.credentials_table.setItem(row, 1, QTableWidgetItem(credentials['username']))
    
    def add_credentials(self):
        """Add new server credentials"""
        dialog = CredentialsDialog(server_path="", parent=self)
        if dialog.exec_():
            credentials = dialog.get_credentials()
            server_path = dialog.get_server_path()
            
            # Save credentials
            if self.credentials_manager.save_credentials(
                server_path,
                credentials['username'],
                credentials['password']
            ):
                self.load_credentials()  # Refresh table
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to save credentials"
                )
    
    def edit_credentials(self):
        """Edit selected server credentials"""
        current_row = self.credentials_table.currentRow()
        if current_row >= 0:
            server_path = self.credentials_table.item(current_row, 0).text()
            current_credentials = self.credentials_manager.get_credentials(server_path)
            
            dialog = CredentialsDialog(
                server_path=server_path,
                username=current_credentials['username'] if current_credentials else "",
                parent=self
            )
            
            if dialog.exec_():
                credentials = dialog.get_credentials()
                new_server_path = dialog.get_server_path()
                
                # If path changed, delete old credentials
                if new_server_path != server_path:
                    self.credentials_manager.delete_credentials(server_path)
                
                # Save new credentials
                if self.credentials_manager.save_credentials(
                    new_server_path,
                    credentials['username'],
                    credentials['password']
                ):
                    self.load_credentials()  # Refresh table
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Failed to save credentials"
                    )
    
    def remove_credentials(self):
        """Remove selected server credentials"""
        current_row = self.credentials_table.currentRow()
        if current_row >= 0:
            server_path = self.credentials_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to remove credentials for {server_path}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.credentials_manager.delete_credentials(server_path):
                    self.load_credentials()  # Refresh table
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Failed to remove credentials"
                    )

    def browse_cert_path(self):
        """Browse for SSL certificate file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SSL Certificate",
            "",
            "Certificate Files (*.pem *.crt *.cer);;All Files (*.*)"
        )
        if file_path:
            self.cert_path.setText(file_path)

    def browse_save_path(self):
        """Browse for default save directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Default Save Directory",
            ""
        )
        if directory:
            self.default_save_path.setText(directory)

    def accept(self):
        """Save settings when OK is clicked"""
        # Update config with new values
        if 'server' not in self.config:
            self.config['server'] = {}
        if 'backup_server' not in self.config:
            self.config['backup_server'] = {}
        if 'connection' not in self.config:
            self.config['connection'] = {}
        if 'paths' not in self.config:
            self.config['paths'] = {}
        
        # Server settings
        self.config['server']['host'] = self.primary_server_host.text()
        self.config['server']['port'] = self.primary_server_port.value()
        
        self.config['backup_server']['host'] = self.backup_server_host.text()
        self.config['backup_server']['port'] = self.backup_server_port.value()
        
        # Connection settings
        self.config['connection'].update({
            'timeout': self.timeout_spinbox.value(),
            'max_retries': self.retry_spinbox.value(),
            'use_ssl': self.use_ssl.isChecked(),
            'verify_ssl': self.verify_ssl.isChecked(),
            'cert_path': self.cert_path.text()
        })
        
        # Path settings
        self.config['paths']['default_save'] = self.default_save_path.text()
        
        # Load existing values when dialog is created
        super().accept()
