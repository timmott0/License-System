from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLabel, QLineEdit, QSpinBox, QPushButton,
                           QCheckBox, QTabWidget, QWidget, QTableWidget,
                           QTableWidgetItem, QMessageBox, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt
from security.credentials_manager import CredentialsManager
from .credentials_dialog import CredentialsDialog
import socket
import ssl
from urllib.parse import urlparse
import requests
from requests.auth import HTTPBasicAuth

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
        
        # Connect SSL checkbox state changes
        self.use_ssl.stateChanged.connect(self.on_ssl_state_changed)
        self.verify_ssl.stateChanged.connect(self.on_verify_ssl_state_changed)
        
        # Initial SSL state setup
        self.on_ssl_state_changed(self.use_ssl.checkState())

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
        
        # Add Test Connection button next to Primary Server Host
        primary_server_layout = QHBoxLayout()
        primary_server_layout.addWidget(self.primary_server_host)
        test_connection_btn = QPushButton("Test Connection")
        test_connection_btn.clicked.connect(self.test_server_connection)
        primary_server_layout.addWidget(test_connection_btn)
        
        server_layout.addRow("Primary Server Host:", primary_server_layout)
        server_layout.addRow("Primary Server Port:", self.primary_server_port)  # Add this line
        
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
        
        # Customer Directory Settings
        customer_group = QGroupBox("Customer Directory Settings")
        customer_layout = QFormLayout()
        
        self.customer_base_path = QLineEdit()
        self.customer_base_path.setText(self.config.get('paths', {}).get('customer_base', 'customers'))
        base_browse_btn = QPushButton("Browse...")
        base_browse_btn.clicked.connect(self.browse_customer_base)
        
        base_layout = QHBoxLayout()
        base_layout.addWidget(self.customer_base_path)
        base_layout.addWidget(base_browse_btn)
        customer_layout.addRow("Customer Base Directory:", base_layout)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
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
        test_creds_button = QPushButton("Test Credentials")  # Add new button
        
        add_button.clicked.connect(self.add_credentials)
        edit_button.clicked.connect(self.edit_credentials)
        remove_button.clicked.connect(self.remove_credentials)
        test_creds_button.clicked.connect(self.test_credentials)  # Add new connection
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(test_creds_button)  # Add button to layout
        layout.addLayout(button_layout)
        
        # Load existing credentials
        self.load_credentials()
        
        return widget
        
    def load_credentials(self):
        """Load existing credentials into the table"""
        self.credentials_table.setRowCount(0)
        stored_paths = self.credentials_manager.get_stored_paths()
        
        print(f"Stored paths: {stored_paths}")  # Debugging line

        for path in stored_paths:
            credentials = self.credentials_manager.get_credentials(path)
            print(f"Loading credentials for {path}: {credentials}")  # Debugging line
            if credentials:
                row = self.credentials_table.rowCount()
                self.credentials_table.insertRow(row)
                self.credentials_table.setItem(row, 0, QTableWidgetItem(path))
                self.credentials_table.setItem(row, 1, QTableWidgetItem(credentials['username']))
    
    def add_credentials(self):
        """Add new server credentials"""
        server_path = self.primary_server_host.text().strip()  # Use Primary Server Host as server_path
        if not server_path:
            QMessageBox.warning(
                self,
                "Error",
                "Primary Server Host cannot be empty."
            )
            return

        dialog = CredentialsDialog(server_path=server_path, parent=self)
        if dialog.exec_():
            credentials = dialog.get_credentials()
            
            # Save credentials
            success = self.credentials_manager.save_credentials(
                server_path,
                credentials['username'],
                credentials['password']
            )
            
            if success:
                print("Credentials saved successfully.")
                self.load_credentials()  # Refresh table
            else:
                print("Failed to save credentials.")
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
                new_server_path = self.primary_server_host.text().strip()  # Use Primary Server Host as new server_path
                
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

    def browse_customer_base(self):
        """Browse for customer base directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Customer Base Directory",
            self.customer_base_path.text()
        )
        if directory:
            self.customer_base_path.setText(directory)

    def on_ssl_state_changed(self, state):
        """Handle SSL checkbox state changes"""
        is_enabled = state == Qt.Checked
        self.verify_ssl.setEnabled(is_enabled)
        self.cert_path.setEnabled(is_enabled)
        
        if not is_enabled:
            self.verify_ssl.setChecked(False)
            self.cert_path.clear()

    def on_verify_ssl_state_changed(self, state):
        """Handle Verify SSL checkbox state changes"""
        is_enabled = state == Qt.Checked
        self.cert_path.setEnabled(is_enabled)
        
        if not is_enabled:
            self.cert_path.clear()

    def test_server_connection(self):
        """Test connection to the primary server"""
        host = self.primary_server_host.text().strip()
        port = self.primary_server_port.value()
        timeout = self.timeout_spinbox.value()
        use_ssl = self.use_ssl.isChecked()

        if not host:
            QMessageBox.warning(
                self,
                "Connection Test",
                "Please enter a server host address."
            )
            return

        # Add debug message
        print(f"Attempting to connect to {host}:{port}")
        print(f"SSL Enabled: {use_ssl}")

        try:
            # Create a progress dialog
            progress = QMessageBox(self)
            progress.setIcon(QMessageBox.Information)
            progress.setText(f"Testing connection to {host}:{port}...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()
            
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            # Try to resolve hostname first
            try:
                ip_address = socket.gethostbyname(host)
                print(f"Resolved {host} to {ip_address}")
            except socket.gaierror:
                progress.hide()
                QMessageBox.critical(
                    self,
                    "Connection Test",
                    f"Could not resolve hostname: {host}\nPlease verify the hostname/IP is correct."
                )
                return

            # If using SSL/TLS
            if use_ssl:
                try:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=host)
                except Exception as e:
                    print(f"SSL Setup Error: {str(e)}")
                    raise

            # Try to connect
            try:
                sock.connect((host, port))
                print(f"Successfully connected to {host}:{port}")
            except ConnectionRefusedError:
                raise Exception(
                    f"Connection refused. Please verify:\n"
                    f"1. Port {port} is open on {host}\n"
                    f"2. The service is running\n"
                    f"3. Firewall allows the connection"
                )

            sock.close()
            
            progress.hide()
            QMessageBox.information(
                self,
                "Connection Test",
                f"Successfully connected to {host}:{port}"
            )

        except Exception as e:
            progress.hide()
            QMessageBox.critical(
                self,
                "Connection Test",
                f"Connection failed:\n{str(e)}"
            )
        finally:
            try:
                sock.close()
            except:
                pass

    def test_credentials(self):
        """Test the selected credentials"""
        current_row = self.credentials_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Test Credentials",
                "Please select credentials to test."
            )
            return

        server_path = self.credentials_table.item(current_row, 0).text()
        credentials = self.credentials_manager.get_credentials(server_path)
        
        if not credentials:
            QMessageBox.warning(
                self,
                "Test Credentials",
                "Could not retrieve credentials for testing."
            )
            return

        # Get connection details
        host = self.primary_server_host.text().strip()
        port = self.primary_server_port.value()
        use_ssl = self.use_ssl.isChecked()
        
        try:
            # Create a progress dialog
            progress = QMessageBox(self)
            progress.setIcon(QMessageBox.Information)
            progress.setText(f"Testing credentials for {server_path}...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()

            # Construct the URL
            protocol = "https" if use_ssl else "http"
            url = f"{protocol}://{host}:{port}"

            # Create HTTP request
            import requests
            from requests.auth import HTTPBasicAuth
            
            # Disable SSL verification warnings if SSL verification is disabled
            if use_ssl and not self.verify_ssl.isChecked():
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(
                url,
                auth=HTTPBasicAuth(credentials['username'], credentials['password']),
                verify=self.verify_ssl.isChecked() if use_ssl else True,
                timeout=self.timeout_spinbox.value()
            )
            
            progress.hide()

            if response.status_code == 200:
                QMessageBox.information(
                    self,
                    "Test Credentials",
                    f"Successfully authenticated with server using credentials for {server_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Test Credentials",
                    f"Authentication failed with status code: {response.status_code}\n"
                    f"Response: {response.text}"
                )

        except requests.exceptions.SSLError as e:
            progress.hide()
            QMessageBox.critical(
                self,
                "Test Credentials",
                f"SSL/TLS Error:\n{str(e)}\n\n"
                "Try disabling SSL verification if using a self-signed certificate."
            )
        except requests.exceptions.ConnectionError as e:
            progress.hide()
            QMessageBox.critical(
                self,
                "Test Credentials",
                f"Connection Error:\n{str(e)}\n\n"
                "Please verify the server address and port are correct."
            )
        except Exception as e:
            progress.hide()
            QMessageBox.critical(
                self,
                "Test Credentials",
                f"Failed to test credentials:\n{str(e)}"
            )

    def accept(self):
        """Save settings when OK is clicked"""
        # Validate primary server host
        if not self.primary_server_host.text().strip():
            QMessageBox.warning(
                self,
                "Invalid Settings",
                "Primary Server Host cannot be empty."
            )
            return
            
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
        
        # Update customer base path
        self.config['paths']['customer_base'] = self.customer_base_path.text()
        
        # Validate SSL settings
        if self.use_ssl.isChecked():
            if self.verify_ssl.isChecked() and not self.cert_path.text().strip():
                QMessageBox.warning(
                    self,
                    "Invalid Settings",
                    "When SSL verification is enabled, a certificate path must be provided."
                )
                return
        
        # Load existing values when dialog is created
        super().accept()


