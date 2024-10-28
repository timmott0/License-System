from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLabel, QLineEdit, QSpinBox, QPushButton,
                           QCheckBox, QTabWidget, QWidget, QTableWidget,
                           QTableWidgetItem, QMessageBox, QGroupBox, QFileDialog,
                           QComboBox, QStackedWidget)
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
        tab_widget = QTabWidget()
        
        # License Systems
        tools_tab = self.create_tools_tab()
        tab_widget.addTab(tools_tab, "License Systems")
        
        # Server Settings Tab
        server_tab = self.create_server_tab()
        tab_widget.addTab(server_tab, "Server Settings")
        
        # Paths Tab
        paths_tab = self.create_paths_tab()
        tab_widget.addTab(paths_tab, "Paths")
        
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

    def create_tools_tab(self):
        """Create the tools tab with license system settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # License Systems Group
        systems_group = QGroupBox("License Systems")
        systems_layout = QVBoxLayout()
        
        # System selection
        self.system_combo = QComboBox()
        for system_id, system in self.config.get('license_systems', {}).items():
            self.system_combo.addItem(system['name'], system_id)
        self.system_combo.currentIndexChanged.connect(self.on_system_changed)
        systems_layout.addWidget(self.system_combo)
        
        # Credentials Group
        creds_group = QGroupBox("System Credentials")
        creds_layout = QFormLayout()
        
        self.system_username = QLineEdit()
        self.system_password = QLineEdit()
        self.system_password.setEchoMode(QLineEdit.Password)
        
        creds_layout.addRow("Username:", self.system_username)
        creds_layout.addRow("Password:", self.system_password)
        
        creds_group.setLayout(creds_layout)
        systems_layout.addWidget(creds_group)
        
        # System-specific settings container
        self.system_settings = QStackedWidget()
        systems_layout.addWidget(self.system_settings)
        
        # Add pages for each system type
        self.add_system_pages()
        
        systems_group.setLayout(systems_layout)
        layout.addWidget(systems_group)
        
        return widget

    def add_system_pages(self):
        """Add settings pages for each license system type"""
        # Network-based systems page (FlexLM, HASP)
        network_page = QWidget()
        network_layout = QFormLayout(network_page)
        
        self.install_path = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_install_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.install_path)
        path_layout.addWidget(browse_btn)
        network_layout.addRow("Install Path:", path_layout)
        
        self.default_port = QSpinBox()
        self.default_port.setRange(1, 65535)
        network_layout.addRow("Default Port:", self.default_port)
        
        self.system_settings.addWidget(network_page)
        
        # Database-based systems page
        db_page = QWidget()
        db_layout = QFormLayout(db_page)
        
        self.db_type = QComboBox()
        self.db_type.addItems(['mysql', 'postgresql', 'sqlite', 'mssql'])
        db_layout.addRow("Database Type:", self.db_type)
        
        self.db_host = QLineEdit()
        db_layout.addRow("Host:", self.db_host)
        
        self.db_port = QSpinBox()
        self.db_port.setRange(1, 65535)
        db_layout.addRow("Port:", self.db_port)
        
        self.db_name = QLineEdit()
        db_layout.addRow("Database:", self.db_name)
        
        self.system_settings.addWidget(db_page)

    def create_server_tab(self):
        """Create the server settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Server Connection Group
        connection_group = QGroupBox("Server Connection")
        connection_layout = QFormLayout()
        
        # Primary Server
        self.primary_server_host = QLineEdit()
        self.primary_server_port = QSpinBox()
        self.primary_server_port.setRange(1, 65535)
        
        connection_layout.addRow("Primary Server Host:", self.primary_server_host)
        connection_layout.addRow("Primary Server Port:", self.primary_server_port)
        
        # Connection Settings
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 300)
        connection_layout.addRow("Timeout (seconds):", self.timeout_spinbox)
        
        self.retry_spinbox = QSpinBox()
        self.retry_spinbox.setRange(0, 10)
        connection_layout.addRow("Max Retries:", self.retry_spinbox)
        
        # Add Test Connection button to connection group
        test_connection_btn = QPushButton("Test Connection")
        test_connection_btn.clicked.connect(self.test_server_connection)
        connection_layout.addRow("", test_connection_btn)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # Server Security Group
        security_group = QGroupBox("Security")
        security_layout = QFormLayout()
        
        self.use_ssl = QCheckBox("Use SSL/TLS")
        self.verify_ssl = QCheckBox("Verify SSL Certificate")
        
        security_layout.addRow("", self.use_ssl)
        security_layout.addRow("", self.verify_ssl)
        
        self.cert_path = QLineEdit()
        browse_cert_btn = QPushButton("Browse...")
        browse_cert_btn.clicked.connect(self.browse_cert_path)
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(self.cert_path)
        cert_layout.addWidget(browse_cert_btn)
        security_layout.addRow("Certificate Path:", cert_layout)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
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
            self.default_save_path.text() or ""
        )
        if directory:
            self.default_save_path.setText(directory)

    def browse_customer_base(self):
        """Browse for customer base directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Customer Base Directory",
            self.customer_base_path.text() or ""
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
        """Test basic connectivity to server"""
        host = self.primary_server_host.text().strip()
        port = self.primary_server_port.value()
        
        if not host:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter a server host address."
            )
            return

        if not isinstance(port, int) or not (1 <= port <= 65535):
            QMessageBox.warning(
                self,
                "Validation Error",
                "Port must be a number between 1 and 65535."
            )
            return

        try:
            # Create a progress dialog
            progress = QMessageBox(self)
            progress.setIcon(QMessageBox.Information)
            progress.setText(f"Testing connection to {host}:{port}...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()

            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout_spinbox.value())

            try:
                # Try to resolve hostname first
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

            # Try to connect
            try:
                sock.connect((ip_address, port))
                print(f"Successfully connected to {host}:{port}")
                progress.hide()
                QMessageBox.information(
                    self,
                    "Connection Test",
                    f"Successfully connected to {host}:{port}"
                )
            except ConnectionRefusedError:
                progress.hide()
                QMessageBox.critical(
                    self,
                    "Connection Error",
                    f"Connection refused. Please verify:\n"
                    f"1. Port {port} is open on {host}\n"
                    f"2. The service is running\n"
                    f"3. Firewall allows the connection"
                )
            finally:
                sock.close()

        except Exception as e:
            if 'progress' in locals():
                progress.hide()
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred:\n{str(e)}"
            )

    def test_database_connection(self, host, port, db_config):
        """Test database connection"""
        try:
            # Create progress dialog
            progress = QMessageBox(self)
            progress.setIcon(QMessageBox.Information)
            progress.setText(f"Testing database connection...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()

            # Import appropriate database driver
            if db_config['type'] == 'mysql':
                import mysql.connector
                conn = mysql.connector.connect(
                    host=host,
                    port=port,
                    database=db_config['database'],
                    user=db_config['username']
                )
            elif db_config['type'] == 'postgresql':
                import psycopg2
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    dbname=db_config['database'],
                    user=db_config['username']
                )
            # ... handle other database types

            conn.close()
            progress.hide()
            QMessageBox.information(
                self,
                "Connection Test",
                "Successfully connected to database"
            )

        except Exception as e:
            progress.hide()
            QMessageBox.critical(
                self,
                "Connection Test",
                f"Database connection failed:\n{str(e)}"
            )

    def test_network_connection(self, host, port, username=None, password=None):
        """Test network connection
        
        Args:
            host (str): The host to connect to
            port (int): The port to connect to
            username (str, optional): Username for authentication
            password (str, optional): Password for authentication
        """
        # Input validation
        if not isinstance(host, str) or not host.strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Invalid host address."
            )
            return

        if not isinstance(port, int) or not (1 <= port <= 65535):
            QMessageBox.warning(
                self,
                "Validation Error",
                "Port must be a number between 1 and 65535."
            )
            return

        try:
            # Create a progress dialog
            progress = QMessageBox(self)
            progress.setIcon(QMessageBox.Information)
            progress.setText(f"Testing connection to {host}:{port}...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()

            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout_spinbox.value())

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

                # Try to connect
                try:
                    sock.connect((ip_address, port))
                    print(f"Successfully connected to {host}:{port}")
                    progress.hide()
                    QMessageBox.information(
                        self,
                        "Connection Test",
                        f"Successfully connected to {host}:{port}"
                    )
                except ConnectionRefusedError:
                    progress.hide()
                    QMessageBox.critical(
                        self,
                        "Connection Error",
                        f"Connection refused. Please verify:\n"
                        f"1. Port {port} is open on {host}\n"
                        f"2. The service is running\n"
                        f"3. Firewall allows the connection"
                    )
                except Exception as e:
                    progress.hide()
                    QMessageBox.critical(
                        self,
                        "Connection Error",
                        f"Failed to connect:\n{str(e)}"
                    )

            finally:
                try:
                    sock.close()
                except:
                    pass

        except Exception as e:
            if 'progress' in locals():
                progress.hide()
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred:\n{str(e)}"
            )

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

    def create_paths_tab(self):
        """Create the paths tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
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

    def on_system_changed(self, index):
        """Handle license system selection changes"""
        system_id = self.system_combo.currentData()
        if not system_id:
            return
        
        system = self.config['license_systems'].get(system_id)
        if not system:
            return
        
        # Show appropriate settings page based on system type
        if system.get('system_type') == 'database':
            self.system_settings.setCurrentIndex(1)  # Database page
            
            # Load database settings if they exist
            db_config = system.get('database_config', {})
            if db_config:
                self.db_type.setCurrentText(db_config.get('type', 'mysql'))
                self.db_host.setText(db_config.get('host', ''))
                self.db_port.setValue(db_config.get('port', 3306))
                self.db_name.setText(db_config.get('database', ''))
                
        else:  # network or file type
            self.system_settings.setCurrentIndex(0)  # Network/file page
            
            # Load network settings if they exist
            self.install_path.setText(str(system.get('install_path', '')))
            self.default_port.setValue(system.get('default_port', 27000))

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
        if 'connection' not in self.config:
            self.config['connection'] = {}
        if 'paths' not in self.config:
            self.config['paths'] = {}
        
        # Server settings
        self.config['server']['host'] = self.primary_server_host.text()
        self.config['server']['port'] = self.primary_server_port.value()
        
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
        self.config['paths']['customer_base'] = self.customer_base_path.text()
        
        # Save license system settings
        system_id = self.system_combo.currentData()
        if system_id and system_id in self.config['license_systems']:
            system = self.config['license_systems'][system_id]
            
            # Set default system_type if not present
            if 'system_type' not in system:
                system['system_type'] = 'network'  # Default to network type
            
            if system.get('system_type') == 'database':
                # Update database config
                if 'database_config' not in system:
                    system['database_config'] = {}
                system['database_config'].update({
                    'type': self.db_type.currentText(),
                    'host': self.db_host.text(),
                    'port': self.db_port.value(),
                    'database': self.db_name.text()
                })
            else:
                # Update network/file config
                system['install_path'] = self.install_path.text()
                system['default_port'] = self.default_port.value()
        
        # Validate SSL settings
        if self.use_ssl.isChecked():
            if self.verify_ssl.isChecked() and not self.cert_path.text().strip():
                QMessageBox.warning(
                    self,
                    "Invalid Settings",
                    "When SSL verification is enabled, a certificate path must be provided."
                )
                return
        
        super().accept()

    def browse_install_path(self):
        """Browse for license system installation directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Installation Directory",
            self.install_path.text() or ""
        )
        if directory:
            self.install_path.setText(directory)

    def test_system_connection(self):
        """Test connection to the selected license system"""
        system_id = self.system_combo.currentData()
        if not system_id:
            return
        
        system = self.config['license_systems'].get(system_id)
        if not system:
            return
        
        username = self.system_username.text().strip()
        password = self.system_password.text()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                "Connection Test",
                "Please enter both username and password."
            )
            return
        
        try:
            # Show progress dialog
            progress = QMessageBox(self)
            progress.setIcon(QMessageBox.Information)
            progress.setText(f"Testing connection to {system['name']}...")
            progress.setStandardButtons(QMessageBox.NoButton)
            progress.show()
            
            if system['system_type'] == 'database':
                self.test_database_connection(system, username, password)
            else:  # network or file type
                self.test_network_connection(system, username, password)
                
            progress.hide()
            
        except Exception as e:
            progress.hide()
            QMessageBox.critical(
                self,
                "Connection Test",
                f"Connection failed:\n{str(e)}"
            )

    def test_database_connection(self, system, username, password):
        """Test database connection"""
        db_config = system.get('database_config', {})
        if not db_config:
            raise ValueError("No database configuration found")
        
        if db_config['type'] == 'mysql':
            import mysql.connector
            conn = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=username,
                password=password
            )
            conn.close()
            
        elif db_config['type'] == 'postgresql':
            import psycopg2
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                dbname=db_config['database'],
                user=username,
                password=password
            )
            conn.close()
            
        # Add other database types as needed
        
        QMessageBox.information(
            self,
            "Connection Test",
            f"Successfully connected to {system['name']}"
        )

    def test_network_connection(self, system, username, password):
        """Test network connection"""
        import socket
        import ssl
        
        host = system.get('install_path', 'localhost')
        port = system.get('default_port', 27000)
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        try:
            # Connect to server
            sock.connect((host, port))
            sock.close()
            QMessageBox.information(
                self,
                "Connection Test",
                f"Successfully connected to {system['name']}"
            )
        except Exception as e:
            raise Exception(f"Failed to connect: {str(e)}")


















