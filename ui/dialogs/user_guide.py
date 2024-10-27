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
        
        # Create text browser for the guide content
        guide = QTextBrowser()
        guide.setOpenExternalLinks(True)
        guide.setFont(QFont('Arial', 10))
        
        # HTML content for the user guide
        guide.setHtml("""
        <h1>License Management System - Detailed Setup Guide</h1>

        <h2>Table of Contents</h2>
        <ul>
            <li><a href="#system-architecture">System Architecture</a></li>
            <li><a href="#initial-setup">Initial Setup</a></li>
            <li><a href="#key-management">Key Management</a></li>
            <li><a href="#license-types">License Types and Generation</a></li>
            <li><a href="#directory-structure">Directory Structure</a></li>
            <li><a href="#server-sync">Server Synchronization</a></li>
        </ul>

        <h2 id="system-architecture">System Architecture</h2>
        <p>The system consists of several key components:</p>
        <ul>
            <li><strong>Key Management</strong>: Handles cryptographic keys for license signing</li>
            <li><strong>License Generator</strong>: Creates different types of licenses</li>
            <li><strong>Directory Manager</strong>: Organizes customer and license files</li>
            <li><strong>License Systems</strong>: Supports multiple licensing backends (FlexLM, HASP, etc.)</li>
        </ul>

        <h2 id="initial-setup">Initial Setup</h2>
        <h3>1. Directory Structure Setup</h3>
        <pre>
        project_root/
        ├── config/
        │   ├── keys/
        │   │   ├── private_key.pem
        │   │   └── public_key.pem
        │   ├── config.json
        │   └── license_systems.py
        ├── customers/
        └── logs/
        </pre>

        <h3>2. Configuration Files</h3>
        <p>Create config.json with the following structure:</p>
        <pre>
        {
            "paths": {
                "config": "config",
                "keys": {
                    "private_key_path": "config/keys/private_key.pem",
                    "public_key_path": "config/keys/public_key.pem"
                }
            },
            "license_systems": {
                "flexlm": {
                    "enabled": true,
                    "install_path": "vendor/flexlm",
                    "default_port": 27000
                },
                "hasp": {
                    "enabled": true,
                    "install_path": "vendor/hasp",
                    "default_port": 1947
                }
            }
        }
        </pre>

        <h2 id="key-management">Key Management Setup</h2>
        <h3>1. Generate Cryptographic Keys</h3>
        <ol>
            <li>Launch Key Management tool (Tools → Key Management)</li>
            <li>Click "Generate New Keys"</li>
            <li>Choose key strength (2048/4096 bits recommended)</li>
            <li>Keys will be saved to config/keys/</li>
        </ol>

        <h3>2. Key Validation</h3>
        <p>The system supports two methods of key validation:</p>
        <ul>
            <li><strong>Manual Validation</strong>: Use the "Validate Keys" button in Key Management</li>
            <li><strong>Automatic Validation</strong>: Occurs during system startup</li>
        </ul>

        <h3>3. Key Backup</h3>
        <p>Regular key backups are essential:</p>
        <ol>
            <li>Use "Backup Keys" in Key Management</li>
            <li>Select secure backup location</li>
            <li>System creates timestamped backup folder</li>
            <li>Both public and private keys are backed up</li>
        </ol>

        <h2 id="license-types">License Types and Generation</h2>
        <h3>Supported License Types:</h3>
        <ul>
            <li><strong>Single-User License</strong>: Basic single installation license</li>
            <li><strong>Volume License</strong>: Multiple installation support</li>
            <li><strong>Subscription</strong>: Time-limited access</li>
            <li><strong>Trial</strong>: Evaluation period license</li>
            <li><strong>Floating</strong>: Network-based concurrent usage</li>
            <li><strong>Node-Locked</strong>: Hardware-specific licensing</li>
        </ul>

        <h3>License Generation Process:</h3>
        <ol>
            <li>Select license type</li>
            <li>Enter customer information</li>
            <li>Choose products and features</li>
            <li>Set expiration and maintenance dates</li>
            <li>System generates cryptographically signed license</li>
            <li>License is saved in customer's directory</li>
        </ol>

        <h2 id="directory-structure">Directory Structure Management</h2>
        <h3>Customer Directory Organization:</h3>
        <pre>
        customers/
        ├── CustomerName/
        │   └── CustomerID/
        │       └── YYYY/
        │           └── MM/
        │               └── licenses/
        </pre>

        <p>The system automatically:</p>
        <ul>
            <li>Creates customer directories</li>
            <li>Organizes by year and month</li>
            <li>Sanitizes directory names</li>
            <li>Maintains directory permissions</li>
        </ul>

        <h2 id="server-sync">Server Synchronization</h2>
        <h3>Product Synchronization:</h3>
        <ol>
            <li>Configure server connection in settings</li>
            <li>Use "Sync Products" from Tools menu</li>
            <li>System will:
                <ul>
                    <li>Download product updates</li>
                    <li>Sync feature definitions</li>
                    <li>Update local database</li>
                </ul>
            </li>
        </ol>

        <h3>License System Integration</h3>
        <p>For each supported license system (FlexLM, HASP, etc.):</p>
        <ol>
            <li>Verify installation path in config</li>
            <li>Configure port settings</li>
            <li>Enable/disable systems as needed</li>
            <li>Test connection using health check tool</li>
        </ol>

        <h2>Security Considerations</h2>
        <ul>
            <li>Keep private keys secure and backed up</li>
            <li>Use strong passwords for key protection</li>
            <li>Regularly rotate encryption keys</li>
            <li>Monitor license generation logs</li>
            <li>Implement access controls for key management</li>
        </ul>

        <h2>Troubleshooting</h2>
        <h3>Common Issues:</h3>
        <table border="1" cellpadding="5">
            <tr>
                <th>Issue</th>
                <th>Solution</th>
            </tr>
            <tr>
                <td>Key validation fails</td>
                <td>
                    <ul>
                        <li>Check key file permissions</li>
                        <li>Verify key file paths in config</li>
                        <li>Ensure key format is correct (PEM)</li>
                    </ul>
                </td>
            </tr>
            <tr>
                <td>License generation error</td>
                <td>
                    <ul>
                        <li>Verify private key is accessible</li>
                        <li>Check customer directory permissions</li>
                        <li>Validate product configuration</li>
                    </ul>
                </td>
            </tr>
            <tr>
                <td>Server sync fails</td>
                <td>
                    <ul>
                        <li>Check network connectivity</li>
                        <li>Verify server credentials</li>
                        <li>Check server URL configuration</li>
                    </ul>
                </td>
            </tr>
        </table>
        """)
        
        layout.addWidget(guide)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
