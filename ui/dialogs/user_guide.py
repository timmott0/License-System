from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTextBrowser, 
                           QPushButton, QScrollArea, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UserGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Guide")
        self.setMinimumSize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        guide = QTextBrowser()
        guide.setOpenExternalLinks(True)
        guide.setFont(QFont('Arial', 10))
        
        guide.setHtml("""
        <h1>License Management System - Comprehensive Guide</h1>

        <h2>Table of Contents</h2>
        <ul>
            <li><a href="#system-overview">System Overview</a></li>
            <li><a href="#settings">Settings Configuration</a></li>
            <li><a href="#license-generation">License Generation Process</a></li>
            <li><a href="#data-organization">Data Organization</a></li>
            <li><a href="#troubleshooting">Troubleshooting</a></li>
        </ul>

        <h2 id="system-overview">System Overview</h2>
        <p>The License Management System supports multiple license types and backend systems:</p>
        
        <h3>Supported License Types:</h3>
        <ul>
            <li><strong>Single-User License</strong>: For individual installations</li>
            <li><strong>Volume License</strong>: For multiple installations</li>
            <li><strong>Subscription</strong>: Time-limited access</li>
            <li><strong>Trial</strong>: Evaluation period license</li>
            <li><strong>Floating</strong>: Network-based concurrent usage</li>
            <li><strong>Node-Locked</strong>: Hardware-specific licensing</li>
            <li><strong>SQL Database</strong>: Database-backed licensing</li>
        </ul>

        <h3>Supported Backend Systems:</h3>
        <ul>
            <li><strong>FlexLM</strong>: Traditional license manager
                <ul>
                    <li>Uses .lic file format</li>
                    <li>Supports network floating licenses</li>
                    <li>Configurable ports and vendor daemons</li>
                </ul>
            </li>
            <li><strong>Database Systems</strong>: SQL-based licensing
                <ul>
                    <li>Supports MySQL, PostgreSQL, SQLite, MSSQL</li>
                    <li>Real-time license tracking</li>
                    <li>Usage analytics support</li>
                </ul>
            </li>
        </ul>

        <h2 id="settings">Settings Configuration</h2>
        
        <h3>License Systems Tab</h3>
        <p>Configure backend systems in Settings → License Systems:</p>
        <ol>
            <li><strong>FlexLM Configuration</strong>
                <ul>
                    <li>Installation Path: Full path to FlexLM binaries
                        <ul>
                            <li>Windows: Usually "C:\Program Files\FlexLM"</li>
                            <li>Linux: Often "/opt/flexlm" or "/usr/local/flexlm"</li>
                            <li>Required files: lmgrd, vendor daemon</li>
                        </ul>
                    </li>
                    <li>Network Configuration
                        <ul>
                            <li>Default Port Range: 27000-27009 (configurable)</li>
                            <li>Vendor Daemon Port: Separate port for vendor daemon</li>
                            <li>Hostname: System hostname or IP address</li>
                        </ul>
                    </li>
                    <li>Vendor Daemon Settings
                        <ul>
                            <li>Daemon Name: Unique identifier for your vendor daemon</li>
                            <li>Options File: Path to vendor daemon options file</li>
                            <li>Debug Log: Path for daemon debug log</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li><strong>Database System Configuration</strong>
                <ul>
                    <li>MySQL Settings
                        <ul>
                            <li>Host: Database server hostname/IP</li>
                            <li>Port: Default 3306</li>
                            <li>Database Name: Name of license database</li>
                            <li>Connection Pool: Min/Max connections</li>
                            <li>Timeout Settings: Connection/Read/Write timeouts</li>
                        </ul>
                    </li>
                    <li>PostgreSQL Settings
                        <ul>
                            <li>Host: Database server hostname/IP</li>
                            <li>Port: Default 5432</li>
                            <li>Schema: Database schema name</li>
                            <li>SSL Mode: disable/require/verify-full</li>
                            <li>Connection Parameters: Application name, SSL certificates</li>
                        </ul>
                    </li>
                    <li>MSSQL Settings
                        <ul>
                            <li>Server: SQL Server instance name</li>
                            <li>Port: Default 1433</li>
                            <li>Authentication: Windows/SQL Server</li>
                            <li>TLS Settings: Version, encryption requirements</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li><strong>Security Settings</strong>
                <ul>
                    <li>Encryption Settings
                        <ul>
                            <li>Key Length: 2048/4096 bits</li>
                            <li>Key Storage Location</li>
                            <li>Key Rotation Policy</li>
                        </ul>
                    </li>
                    <li>Access Control
                        <ul>
                            <li>User Roles: Admin, Manager, Viewer</li>
                            <li>Permission Levels</li>
                            <li>IP Restrictions</li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ol>

        <h3>Server Settings Tab</h3>
        <p>Configure server connectivity and authentication:</p>
        
        <h4>1. Server URL Configuration</h4>
        <ul>
            <li><strong>URL Structure</strong>
                <ul>
                    <li>Protocol: http:// or https://</li>
                    <li>Domain/IP: server address</li>
                    <li>Port: if non-standard</li>
                    <li>Path: /api/v1, etc.</li>
                    <li>Example: https://license.company.com:8443/api/v1</li>
                </ul>
            </li>
            <li><strong>Synology NAS Setup</strong>
                <ul>
                    <li>Access Method
                        <ul>
                            <li>QuickConnect ID: quick.synology.com</li>
                            <li>DDNS: your-domain.synology.me</li>
                            <li>Local IP: 192.168.x.x:5001</li>
                        </ul>
                    </li>
                    <li>Required Packages
                        <ul>
                            <li>Web Station</li>
                            <li>PHP</li>
                            <li>MariaDB/MySQL</li>
                        </ul>
                    </li>
                    <li>Security Settings
                        <ul>
                            <li>Enable HTTPS</li>
                            <li>Configure SSL certificate</li>
                            <li>Set up firewall rules</li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ul>

        <h4>2. Authentication Configuration</h4>
        <ul>
            <li><strong>Authentication Methods</strong>
                <ul>
                    <li>Basic Auth
                        <ul>
                            <li>Username/Password</li>
                            <li>Base64 encoding</li>
                            <li>HTTPS required</li>
                        </ul>
                    </li>
                    <li>API Key
                        <ul>
                            <li>Key Generation</li>
                            <li>Header: X-API-Key</li>
                            <li>Key rotation policy</li>
                        </ul>
                    </li>
                    <li>OAuth 2.0
                        <ul>
                            <li>Client ID/Secret</li>
                            <li>Authorization flow</li>
                            <li>Token management</li>
                            <li>Refresh token handling</li>
                        </ul>
                    </li>
                    <li>JWT
                        <ul>
                            <li>Token structure</li>
                            <li>Signing algorithms</li>
                            <li>Expiration policies</li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ul>

        <h4>3. SSL/TLS Configuration</h4>
        <ul>
            <li><strong>Certificate Management</strong>
                <ul>
                    <li>Certificate Types
                        <ul>
                            <li>Self-signed</li>
                            <li>Let's Encrypt</li>
                            <li>Commercial CA</li>
                        </ul>
                    </li>
                    <li>Certificate Path</li>
                    <li>Private Key Location</li>
                    <li>Chain Certificates</li>
                </ul>
            </li>
            <li><strong>Security Settings</strong>
                <ul>
                    <li>Minimum TLS Version: 1.2/1.3</li>
                    <li>Cipher Suites</li>
                    <li>Certificate Verification</li>
                </ul>
            </li>
        </ul>

        <h4>4. Connection Settings</h4>
        <ul>
            <li><strong>Timeouts</strong>
                <ul>
                    <li>Connection Timeout: 30s default</li>
                    <li>Read Timeout: 60s default</li>
                    <li>Write Timeout: 60s default</li>
                </ul>
            </li>
            <li><strong>Retry Configuration</strong>
                <ul>
                    <li>Max Retries: 3 default</li>
                    <li>Retry Delay: 5s default</li>
                    <li>Backoff Factor: 2.0</li>
                </ul>
            </li>
        </ul>

        <h4>5. Proxy Configuration</h4>
        <ul>
            <li><strong>Proxy Types</strong>
                <ul>
                    <li>HTTP Proxy
                        <ul>
                            <li>Host and Port</li>
                            <li>Authentication</li>
                            <li>Allowed Methods</li>
                        </ul>
                    </li>
                    <li>SOCKS Proxy
                        <ul>
                            <li>SOCKS4/SOCKS5</li>
                            <li>Authentication methods</li>
                            <li>DNS resolution options</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li><strong>Proxy Authentication</strong>
                <ul>
                    <li>Username/Password</li>
                    <li>API Key</li>
                    <li>Certificate-based</li>
                </ul>
            </li>
            <li><strong>Bypass Rules</strong>
                <ul>
                    <li>Local addresses</li>
                    <li>Domain patterns</li>
                    <li>IP ranges</li>
                </ul>
            </li>
        </ul>

        <h2 id="license-generation">License Generation Process</h2>
        
        <h3>1. Customer Information</h3>
        <p>Required fields:</p>
        <ul>
            <li>Customer Name</li>
            <li>Customer ID</li>
            <li>Contact Email</li>
            <li>Additional Notes (optional)</li>
        </ul>

        <h3>2. License Configuration</h3>
        <p>Essential settings:</p>
        <ul>
            <li>License Type Selection</li>
            <li>Platform Selection</li>
            <li>Expiration Date</li>
            <li>Maintenance Date</li>
            <li>Backend System Selection</li>
        </ul>

        <h3>3. Product Selection</h3>
        <p>Product configuration:</p>
        <ul>
            <li>Select Products</li>
            <li>Configure Features</li>
            <li>Set Quantities (for volume licenses)</li>
            <li>Add Product-Specific Options</li>
        </ul>

        <h2 id="data-organization">Data Organization</h2>
        
        <h3>Directory Structure</h3>
        <pre>
        customers/
        ├── CustomerName/
        │   └── CustomerID/
        │       └── YYYY/
        │           └── MM/
        │               ├── licenses/
        │               │   ├── license_20240315_123456.lic
        │               │   └── license_20240315_123456.json
        │               └── metadata/
        </pre>

        <h3>License File Formats</h3>
        <table border="1" cellpadding="5">
            <tr>
                <th>System</th>
                <th>File Extension</th>
                <th>Format</th>
            </tr>
            <tr>
                <td>FlexLM</td>
                <td>.lic</td>
                <td>Text-based license file</td>
            </tr>
            <tr>
                <td>Database</td>
                <td>.json</td>
                <td>JSON metadata + DB entry</td>
            </tr>
        </table>

        <h3>Database Schema</h3>
        <p>For database-backed licenses:</p>
        <pre>
        licenses
        ├── id (PRIMARY KEY)
        ├── customer_id
        ├── license_type
        ├── products
        ├── features
        ├── expiration_date
        ├── maintenance_date
        ├── status
        └── metadata
        </pre>

        <h2 id="troubleshooting">Troubleshooting</h2>

        <h3>Common Issues and Solutions</h3>
        <table border="1" cellpadding="5">
            <tr>
                <th>Issue</th>
                <th>Possible Causes</th>
                <th>Solutions</th>
            </tr>
            <tr>
                <td>License Generation Fails</td>
                <td>
                    <ul>
                        <li>Missing customer information</li>
                        <li>Invalid product selection</li>
                        <li>Backend system unavailable</li>
                    </ul>
                </td>
                <td>
                    <ul>
                        <li>Verify all required fields</li>
                        <li>Check product configuration</li>
                        <li>Test backend connectivity</li>
                    </ul>
                </td>
            </tr>
            <tr>
                <td>Database Connection Error</td>
                <td>
                    <ul>
                        <li>Invalid credentials</li>
                        <li>Wrong host/port</li>
                        <li>Network issues</li>
                    </ul>
                </td>
                <td>
                    <ul>
                        <li>Verify credentials in settings</li>
                        <li>Check network connectivity</li>
                        <li>Test connection in Settings dialog</li>
                    </ul>
                </td>
            </tr>
            <tr>
                <td>FlexLM License Invalid</td>
                <td>
                    <ul>
                        <li>Wrong vendor daemon</li>
                        <li>Invalid feature configuration</li>
                        <li>Port conflicts</li>
                    </ul>
                </td>
                <td>
                    <ul>
                        <li>Verify vendor daemon settings</li>
                        <li>Check feature definitions</li>
                        <li>Ensure port availability</li>
                    </ul>
                </td>
            </tr>
        </table>

        <h3>Error Messages and Resolution</h3>
        <ul>
            <li><strong>"Failed to save license"</strong>
                <ul>
                    <li>Check write permissions</li>
                    <li>Verify customer directory exists</li>
                    <li>Ensure valid file name</li>
                </ul>
            </li>
            <li><strong>"Invalid configuration"</strong>
                <ul>
                    <li>Review system settings</li>
                    <li>Check configuration file format</li>
                    <li>Verify paths and permissions</li>
                </ul>
            </li>
            <li><strong>"Database connection failed"</strong>
                <ul>
                    <li>Check network connectivity</li>
                    <li>Verify database credentials</li>
                    <li>Test connection in settings</li>
                </ul>
            </li>
        </ul>

        <h3>Best Practices</h3>
        <ul>
            <li>Always preview licenses before generation</li>
            <li>Maintain regular database backups</li>
            <li>Document custom configurations</li>
            <li>Test in non-production environment first</li>
            <li>Keep system settings up to date</li>
        </ul>
        """)
        
        layout.addWidget(guide)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
