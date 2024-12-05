from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton,
                           QScrollArea, QWidget, QGroupBox, QCheckBox, QTableWidgetItem,
                           QDialog, QTextEdit, QMessageBox, QStackedWidget, QFormLayout, QSpinBox,
                           QFileDialog, QTableWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSlot
from .dialogs.platform_select import PlatformSelectDialog
from .dialogs.product_dialog import ProductDialog
from core.product import Product
from core.license_generator import LicenseGeneratorFactory, LicenseType
from core.key_manager import KeyManager
from encryption.license_signing import LicenseSigner
from pathlib import Path
import json
from utils.validation import LicenseValidator
from utils.host_identifier import HostIdentifier
from typing import List, Tuple, Dict
from enum import Enum
from .dialogs.floating_license_dialog import FloatingLicenseDialog
from .dialogs.credentials_dialog import CredentialsDialog
from security.credentials_manager import CredentialsManager
from utils.directory_manager import CustomerDirectoryManager
from datetime import datetime, date
from core.license_enforcer import LicenseEnforcer

class LicenseType(Enum):
    SINGLE_USER = "Single-User License"
    VOLUME = "Volume License"
    SUBSCRIPTION = "Subscription License"
    TRIAL = "Trial License"
    FREEMIUM = "Freemium License"
    FLOATING = "Floating License"
    CONCURRENT = "Concurrent License"
    NODELOCK = "Node-Locked License"
    SQL = "SQL Database License"
    # Add new types here, for example:
    # ENTERPRISE = "Enterprise License"

class BaseLicenseGenerator:
    """Base class for all license generators"""
    
    def __init__(self, signer):
        self.signer = signer  # LicenseSigner instance
    
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        raise NotImplementedError()
    
    def save_license(self, license_data: str, output_path: Path) -> None:
        """Save license data to file"""
        try:
            # Default implementation for text-based licenses
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(license_data)
        except Exception as e:
            raise IOError(f"Failed to save license: {str(e)}")

class FlexLMGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        # Validate required fields
        if not all([customer_info, license_info, products]):
            raise ValueError("Missing required license information")
            
        # Prepare FlexLM format data
        license_data = {
            'type': 'flexlm',
            'server': {
                'host': host_info.get('hostid', 'ANY'),
                'port': license_info.get('port', '27000'),
                'vendor_daemon': license_info.get('vendor_daemon', 'vendor_daemon')
            },
            'customer': customer_info,
            'license': license_info,
            'products': [
                {
                    'name': product.name,
                    'version': product.version,
                    'quantity': product.quantity,
                    'expiration': license_info['expiration_date']
                }
                for product in products
            ]
        }
        
        # Sign and return the license data
        return self.signer.sign_license_data(license_data)

    def save_license(self, license_data: str, output_path: Path) -> None:
        # FlexLM uses specific text format
        super().save_license(license_data, output_path)

class HASPGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        # Prepare HASP format data
        license_data = {
            'type': 'hasp',
            'version': '1.0',
            'customer': customer_info,
            'products': [
                {
                    'name': p.name,
                    'version': p.version,
                    'quantity': p.quantity
                }
                for p in products
            ],
            'license': license_info,
            'host': host_info
        }
        
        # Sign the license data using the provided signer
        return self.signer.sign_license_data(license_data)

class MySQLGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        # Prepare MySQL format data
        license_data = {
            'type': 'mysql',
            'database': {
                'host': license_info.get('sql_host', 'localhost'),
                'port': license_info.get('sql_port', 3306),
                'name': license_info.get('sql_database', 'licenses')
            },
            'customer': customer_info,
            'license': license_info,
            'products': [
                {
                    'name': product.name,
                    'version': product.version,
                    'quantity': product.quantity,
                    'expiration': license_info['expiration_date'].isoformat()
                }
                for product in products
            ]
        }
        
        # Sign the license data using the provided signer
        return self.signer.sign_license_data(license_data)

# Add other generator implementations...

class LicenseFrame(QFrame):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.validate_config(config)
        self.initialize_components(config)
        self.setup_ui()
        self.server_connected = False
        self.server_path = None
        self.server_info = None
        self.license_enforcer = LicenseEnforcer()

    def validate_config(self, config: Dict):
        """Validate configuration structure"""
        if not config:
            raise ValueError("Configuration is required")
            
        # Validate paths
        key_paths = config.get('paths', {}).get('keys', {})
        required_paths = ['private_key_path', 'public_key_path']
        missing = [p for p in required_paths if not key_paths.get(p)]
        if missing:
            raise ValueError(f"Missing required key paths: {', '.join(missing)}")
            
        # Validate license systems
        if not isinstance(config.get('license_systems'), dict):
            raise ValueError("Invalid license systems configuration")

    def initialize_components(self, config: Dict):
        self.config = config
        self.floating_license_config = None  # Store floating license settings
        self.credentials_manager = CredentialsManager()
        self.selected_platforms = []  # Initialize selected_platforms list
        
        # Initialize key management
        key_paths = config.get('paths', {}).get('keys', {})
        self.key_manager = KeyManager(
            private_key_path=key_paths.get('private_key_path'),
            public_key_path=key_paths.get('public_key_path')
        )
        self.signer = LicenseSigner(self.key_manager)
        
        # Create SQL options widget
        self.sql_options = self.create_sql_options()
        self.sql_options.setVisible(False)  # Hide by default
        
    def setup_ui(self):
        """Initialize the license frame UI"""
        main_layout = QVBoxLayout(self)
        
        # Add save location group
        save_location_group = self.create_save_location_group()
        main_layout.addWidget(save_location_group)
        
        # Create scroll area for license details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)
        
        # Customer Information Group
        customer_group = self.create_customer_group()
        content_layout.addWidget(customer_group)
        
        # License Settings Group
        license_group = self.create_license_group()
        content_layout.addWidget(license_group)
        
        # Product Settings Group
        product_group = self.create_product_group()
        content_layout.addWidget(product_group)
        
        # Active Licenses Table
        self.active_licenses_table = QTableWidget()
        self.active_licenses_table.setColumnCount(3)
        self.active_licenses_table.setHorizontalHeaderLabels(['License ID', 'Type', 'Expiration'])
        content_layout.addWidget(self.active_licenses_table)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        generate_button = QPushButton("Generate License")
        generate_button.clicked.connect(self.generate_license)
        button_layout.addWidget(generate_button)
        
        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.preview_license)
        button_layout.addWidget(preview_button)
        
        main_layout.addLayout(button_layout)
        
        # REMOVE these lines that create duplicate dropdowns
        # self.form_layout = QFormLayout()
        # self.license_type_combo = QComboBox()
        # for license_type in LicenseType:
        #     self.license_type_combo.addItem(license_type.value, license_type)
        # self.license_type_combo.currentIndexChanged.connect(self.on_license_type_changed)
        # self.form_layout.addRow("License Type:", self.license_type_combo)
        # main_layout.addLayout(self.form_layout)

    def create_customer_group(self):
        """Create the customer information group with directory management"""
        group = QGroupBox("Customer Information")
        layout = QGridLayout()
        
        # Customer Name
        layout.addWidget(QLabel("Customer Name:"), 0, 0)
        self.customer_name = QLineEdit()
        self.customer_name.textChanged.connect(self.update_customer_path)
        layout.addWidget(self.customer_name, 0, 1)
        
        # Customer ID
        layout.addWidget(QLabel("Customer ID:"), 1, 0)
        self.customer_id = QLineEdit()
        self.customer_id.textChanged.connect(self.update_customer_path)
        layout.addWidget(self.customer_id, 1, 1)
        
        # Contact Email
        layout.addWidget(QLabel("Contact Email:"), 2, 0)
        self.contact_email = QLineEdit()
        layout.addWidget(self.contact_email, 2, 1)
        
        # Customer Directory Path (read-only)
        layout.addWidget(QLabel("License Directory:"), 3, 0)
        self.directory_path = QLineEdit()
        self.directory_path.setReadOnly(True)
        layout.addWidget(self.directory_path, 3, 1)
        
        # Create Directory Button
        self.create_dir_button = QPushButton("Create Directory")
        self.create_dir_button.clicked.connect(self.create_customer_directory)
        self.create_dir_button.setEnabled(False)
        layout.addWidget(self.create_dir_button, 3, 2)
        
        group.setLayout(layout)
        
        # Initialize directory manager
        base_path = self.config.get('paths', {}).get('customer_base', 'customers')
        self.dir_manager = CustomerDirectoryManager(base_path)
        
        return group
        
    def create_license_group(self):
        """Create the license settings group"""
        group = QGroupBox("License Settings")
        layout = QGridLayout()
        
        # License Type dropdown with correct license types
        layout.addWidget(QLabel("License Type:"), 0, 0)
        self.license_type_combo = QComboBox()
        for license_type in LicenseType:
            self.license_type_combo.addItem(license_type.value, license_type)
        self.license_type_combo.currentTextChanged.connect(self.on_license_type_changed)
        layout.addWidget(self.license_type_combo, 0, 1)
        
        # Platform
        layout.addWidget(QLabel("Platform:"), 1, 0)
        self.platform_label = QLabel("No platforms selected")  # Add this line
        self.platform_button = QPushButton("Select Platform...")
        self.platform_button.clicked.connect(self.show_platform_dialog)
        
        # Create a horizontal layout for platform selection
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(self.platform_label)
        platform_layout.addWidget(self.platform_button)
        layout.addLayout(platform_layout, 1, 1)  # Changed from addWidget to addLayout
        
        # Expiration Date
        layout.addWidget(QLabel("Expiration Date:"), 2, 0)
        self.expiration_date = QDateEdit()
        self.expiration_date.setCalendarPopup(True)
        self.expiration_date.setDate(QDate.currentDate().addYears(1))
        layout.addWidget(self.expiration_date, 2, 1)
        
        # Maintenance Date
        layout.addWidget(QLabel("Maintenance Until:"), 3, 0)
        self.maintenance_date = QDateEdit()
        self.maintenance_date.setCalendarPopup(True)
        self.maintenance_date.setDate(QDate.currentDate().addMonths(3))
        layout.addWidget(self.maintenance_date, 3, 1)
        
        # License System (FlexLM, HASP, SQL, etc.)
        layout.addWidget(QLabel("License System:"), 4, 0)
        self.license_system_combo = QComboBox()
        self.populate_license_systems()  # Add this method call
        layout.addWidget(self.license_system_combo, 4, 1)
        
        # Add this line to connect the change event
        self.license_system_combo.currentIndexChanged.connect(self.on_license_system_changed)
        
        # Add SQL-specific options container
        self.sql_options = self.create_sql_options()
        self.sql_options.setVisible(False)  # Hide by default
        layout.addWidget(self.sql_options, 5, 0, 1, 2)

        group.setLayout(layout)
        return group
        
    def create_product_group(self):
        """Create the product settings group"""
        group = QGroupBox("Product Selection")
        layout = QVBoxLayout()
        
        # Create a scrollable area for product checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Container for checkboxes
        self.product_container = QWidget()
        self.product_layout = QVBoxLayout(self.product_container)
        
        scroll.setWidget(self.product_container)
        layout.addWidget(scroll)
        
        group.setLayout(layout)
        return group
        
    def on_license_type_changed(self, index_or_text):
        """Handle license type selection changes"""
        license_type = self.license_type_combo.currentData()
        
        # Hide all system-specific options by default
        if hasattr(self, 'sql_options'):
            self.sql_options.setVisible(False)
        
        if license_type == LicenseType.FLOATING:
            dialog = FloatingLicenseDialog(self)
            if dialog.exec_():
                self.floating_license_config = dialog.get_values()
                print(f"Floating license configured with {self.floating_license_config}")
        
        # Show SQL options if SQL license type is selected
        elif license_type == LicenseType.SQL:
            if hasattr(self, 'sql_options'):
                self.sql_options.setVisible(True)

    def show_platform_dialog(self):
        """Show platform selection dialog"""
        # Pass the currently selected platforms to the dialog
        dialog = PlatformSelectDialog(current_platforms=self.selected_platforms, parent=self)
        if dialog.exec_():
            self.selected_platforms = dialog.get_selected_platforms()
            # Update the label to show selected platforms
            if self.selected_platforms:
                self.platform_label.setText(", ".join(self.selected_platforms))
            else:
                self.platform_label.setText("No platforms selected")
            
    def validate_form(self) -> Tuple[bool, List[str]]:
        """Validate all form inputs"""
        errors = []
        
        try:
            # Validate customer information
            customer_info = {
                'name': self.customer_name.text().strip(),
                'id': self.customer_id.text().strip(),
                'email': self.contact_email.text().strip()
            }
            
            if not all(customer_info.values()):
                errors.append("All customer information fields are required")
                
            # Validate license type
            if not self.license_type_combo.currentData():
                errors.append("License type must be selected")
            
            # Validate platforms
            if not self.selected_platforms:
                errors.append("At least one platform must be selected")
            
            # Validate products
            if not self.get_products():
                errors.append("At least one product must be selected")
            
            # Validate dates
            if self.expiration_date.date() <= QDate.currentDate():
                errors.append("Expiration date must be in the future")
            
            # Validate system-specific options
            license_system = self.license_system_combo.currentData()
            if license_system == 'mysql':
                if not self.sql_host.text().strip():
                    errors.append("Database host is required")
                if not self.sql_database.text().strip():
                    errors.append("Database name is required")
            
        except AttributeError as e:
            errors.append(f"Form validation failed: {str(e)}")
            
        return len(errors) == 0, errors

    def generate_license(self):
        """Generate license based on selected system"""
        try:
            # Validate form first
            valid, errors = self.validate_form()
            if not valid:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "\n".join(errors)
                )
                return

            # Get selected license system from combo
            license_system = self.license_system_combo.currentData()
            
            # Create generator using factory
            generator = LicenseGeneratorFactory.create_generator(
                license_system,
                self.signer
            )
            
            # Generate license
            license_data = generator.generate_license(
                self.get_customer_info(),
                self.get_license_info(),
                self.get_products(),
                self.get_host_info()
            )
            
            # Save license
            self.save_license(license_data, license_system)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate license: {str(e)}"
            )
    
    def get_system_options(self, license_system: str) -> Dict:
        """Get options specific to the selected license system"""
        if license_system == 'flexlm':
            return {
                'port': self.flexlm_port.value() if hasattr(self, 'flexlm_port') else 27000,
                'vendor_daemon': self.flexlm_vendor.text() if hasattr(self, 'flexlm_vendor') else 'vendor_daemon',
                'additional_options': self.flexlm_options.text() if hasattr(self, 'flexlm_options') else ''
            }
        elif license_system == 'hasp':
            return {
                'feature_id': self.hasp_feature_id.value() if hasattr(self, 'hasp_feature_id') else 1,
                'vendor_code': self.hasp_vendor_code.text() if hasattr(self, 'hasp_vendor_code') else 'hasp'
            }
        return {}
    
    def preview_license(self):
        """Preview the license configuration"""
        try:
            # Generate license data without saving
            customer_info = {
                'name': self.customer_name.text(),
                'id': self.customer_id.text(),
                'email': self.contact_email.text()
            }
            
            license_info = {
                'type': self.license_type_combo.currentText(),
                'expiration_date': self.expiration_date.date().toPyDate().isoformat(),
                'maintenance_date': self.maintenance_date.date().toPyDate().isoformat(),
                'platforms': self.selected_platforms
            }
            
            products = [p.to_dict() for p in self.get_all_products()]
            
            preview_data = {
                'customer': customer_info,
                'license': license_info,
                'products': products
            }
            
            # Show preview dialog
            preview_text = json.dumps(preview_data, indent=2)
            dialog = QDialog(self)
            dialog.setWindowTitle("License Preview")
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(preview_text)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate preview: {str(e)}"
            )

    def add_product(self):
        """Add a new product"""
        dialog = ProductDialog(parent=self)
        if dialog.exec_():
            product = dialog.get_product()
            self.add_product_to_table(product)

    def edit_product(self):
        """Edit selected product"""
        current_row = self.product_table.currentRow()
        if current_row >= 0:
            product = self.get_product_from_row(current_row)
            dialog = ProductDialog(product, parent=self)
            if dialog.exec_():
                updated_product = dialog.get_product()
                self.update_product_in_table(current_row, updated_product)

    def remove_product(self):
        """Remove selected product"""
        current_row = self.product_table.currentRow()
        if current_row >= 0:
            self.product_table.removeRow(current_row)

    def add_product_to_table(self, product: Product):
        """Add product to the table"""
        row = self.product_table.rowCount()
        self.product_table.insertRow(row)
        
        self.product_table.setItem(row, 0, QTableWidgetItem(product.name))
        self.product_table.setItem(row, 1, QTableWidgetItem(product.version))
        self.product_table.setItem(row, 2, QTableWidgetItem(str(product.quantity)))
        
        features_text = ", ".join(f.name for f in product.features)
        self.product_table.setItem(row, 3, QTableWidgetItem(features_text))

    def update_product_in_table(self, row: int, product: Product):
        """Update product in the table"""
        self.product_table.setItem(row, 0, QTableWidgetItem(product.name))
        self.product_table.setItem(row, 1, QTableWidgetItem(product.version))
        self.product_table.setItem(row, 2, QTableWidgetItem(str(product.quantity)))
        
        features_text = ", ".join(f.name for f in product.features)
        self.product_table.setItem(row, 3, QTableWidgetItem(features_text))

    def get_product_from_row(self, row: int) -> Product:
        """Get product object from table row"""
        name = self.product_table.item(row, 0).text()
        version = self.product_table.item(row, 1).text()
        quantity = int(self.product_table.item(row, 2).text())
        
        # Note: This is a simplified version - in a real implementation,
        # you'd want to store the full product object somewhere
        return Product(
            name=name,
            version=version,
            features=[],
            quantity=quantity
        )

    def get_all_products(self) -> List[Product]:
        """Get all products from the table"""
        products = []
        for row in range(self.product_table.rowCount()):
            products.append(self.get_product_from_row(row))
        return products

    def create_flexlm_options(self):
        """Create FlexLM-specific options widget"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.flexlm_port = QSpinBox()
        self.flexlm_port.setRange(1024, 65535)
        self.flexlm_port.setValue(27000)
        layout.addRow("License Server Port:", self.flexlm_port)
        
        self.flexlm_vendor = QLineEdit()
        layout.addRow("Vendor Daemon:", self.flexlm_vendor)
        
        self.flexlm_options = QLineEdit()
        layout.addRow("Additional Options:", self.flexlm_options)
        
        return widget
    
    def create_hasp_options(self):
        """Create HASP-specific options widget"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.hasp_feature_id = QSpinBox()
        layout.addRow("Feature ID:", self.hasp_feature_id)
        
        self.hasp_vendor_code = QLineEdit()
        layout.addRow("Vendor Code:", self.hasp_vendor_code)
        
        return widget
    
    def on_license_system_changed(self, index):
        """Handle license system selection change"""
        system_id = self.license_system_combo.currentData()
        
        if system_id == 'mysql_licenses':
            # Use database settings from config
            db_config = self.config.get('database', {})
            self.sql_host.setText(db_config.get('host', 'localhost'))
            self.sql_port.setValue(db_config.get('port', 3306))
            self.sql_database.setText(db_config.get('database', 'licenses'))
            self.sql_username.setText(db_config.get('username', ''))
        else:
            self.sql_options.setVisible(False)

    def save_license(self, license_data: str, license_system: str):
        """Save the license file with the appropriate extension"""
        try:
            # Get the save path from the input field
            save_path = Path(self.save_path_input.text())
            
            if not save_path.exists():
                save_path.mkdir(parents=True, exist_ok=True)
            
            customer_name = self.customer_name.text().strip()
            customer_id = self.customer_id.text().strip()
            
            if not customer_name or not customer_id:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please enter customer name and ID before saving."
                )
                return
            
            # Get or create the customer directory
            path = self.dir_manager.create_customer_structure(customer_name, customer_id)
            
            # Determine file extension based on license system
            extensions = {
                'flexlm': '.lic',
                'hasp': '.v2c',
                'sentinel': '.c2v',
                'mysql': '.sql'
            }
            extension = extensions.get(license_system, '.lic')
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"license_{timestamp}{extension}"
            
            # Full path for the license file
            license_path = path / filename
            
            # Save the license data
            if isinstance(license_data, str):
                with open(license_path, 'w', encoding='utf-8') as f:
                    f.write(license_data)
            else:
                with open(license_path, 'wb') as f:
                    f.write(license_data)
            
            QMessageBox.information(
                self,
                "Success",
                f"License saved successfully to:\n{license_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save license: {str(e)}"
            )

    def setup_license_system_dropdown(self):
        """Populate the license system dropdown"""
        self.license_system_combo.clear()
        
        # Get license systems from config
        license_systems = self.config.get('license_systems', {})  # Changed from self.parent().config
        
        # Add enabled systems to dropdown
        for system_id, system in license_systems.items():
            if system.get('enabled', True):  # Only add enabled systems
                self.license_system_combo.addItem(system['name'], system_id)
                
        # Connect signal to handle selection changes
        self.license_system_combo.currentIndexChanged.connect(self.on_license_system_changed)

    def clear_fields(self):
        """Clear all input fields"""
        for widget in self.findChildren(QLineEdit):
            widget.clear()
        for widget in self.findChildren(QTextEdit):
            widget.clear()
        for widget in self.findChildren(QComboBox):
            widget.setCurrentIndex(0)

    def set_default_values(self):
        """Set default values for new license"""
        # Add any default values you want to set
        # For example:
        # self.expiry_date.setDate(QDate.currentDate().addYears(1))
        # self.status_combo.setCurrentText("Active")
        pass

    def load_data(self, data: dict):
        """Load license data into the form"""
        # Implement loading data into your form fields
        # Example:
        # self.name_input.setText(data.get('name', ''))
        # self.expiry_date.setDate(QDate.fromString(data.get('expiry', '')))
        pass

    def get_data(self) -> dict:
        """Get license data from the form"""
        # Implement collecting data from your form fields
        # Example:
        return {
            # 'name': self.name_input.text(),
            # 'expiry': self.expiry_date.date().toString(),
            # Add all your fields here
        }

    def setup_license_type_combo(self):
        self.license_type_combo = QComboBox()
        for license_type in LicenseType:
            self.license_type_combo.addItem(license_type.value, license_type)
        self.license_type_combo.currentIndexChanged.connect(self.on_license_type_changed)

    def on_license_type_changed(self, index):
        """Handle license type selection changes"""
        license_type = self.license_type_combo.currentData()  # Now using consistent name
        
        if license_type == LicenseType.FLOATING:
            dialog = FloatingLicenseDialog(self)
            if dialog.exec_():
                self.floating_license_config = dialog.get_values()
                print(f"Floating license configured with {self.floating_license_config}")
    
    def get_license_data(self):
        data = {
            'type': self.license_type_combo.currentData(),
            # ... other existing fields ...
        }
        
        # Add floating license specific data if applicable
        if data['type'] == LicenseType.FLOATING:
            data.update(self.floating_license_config)
        
        return data

    def validate_server_path(self, server_path: str):
        """Validate server path and request credentials if needed"""
        # Check if we have credentials for this path
        credentials = self.credentials_manager.get_credentials(server_path)
        
        if not credentials:
            # Show credentials dialog
            dialog = CredentialsDialog(server_path, self)
            if dialog.exec_() == QDialog.Accepted:
                credentials = dialog.get_credentials()
                # Save the credentials
                self.credentials_manager.save_credentials(
                    server_path,
                    credentials['username'],
                    credentials['password']
                )
                return True
            return False
        return True

    def on_server_path_changed(self, path: str):
        """Handle server path changes"""
        if path.startswith(('\\\\', 'http://', 'https://')):
            if not self.validate_server_path(path):
                QMessageBox.warning(
                    self,
                    "Credentials Required",
                    "Valid credentials are required for server access."
                )

    def update_customer_path(self):
        """Update the directory path display when customer info changes"""
        customer_name = self.customer_name.text().strip()
        customer_id = self.customer_id.text().strip()
        
        if customer_name and customer_id:
            # Check if directory exists
            current_path = self.dir_manager.get_customer_path(customer_name, customer_id)
            
            if current_path:
                self.directory_path.setText(str(current_path))
                self.create_dir_button.setEnabled(False)
                self.directory_path.setStyleSheet("color: green;")
            else:
                # Show what the path would be
                safe_name = self.dir_manager.sanitize_name(customer_name)
                safe_id = self.dir_manager.sanitize_name(customer_id)
                potential_path = self.dir_manager.base_path / safe_name / safe_id
                self.directory_path.setText(f"{potential_path} (Not Created)")
                self.create_dir_button.setEnabled(True)
                self.directory_path.setStyleSheet("color: red;")
        else:
            self.directory_path.setText("")
            self.create_dir_button.setEnabled(False)
            self.directory_path.setStyleSheet("")

    def create_customer_directory(self):
        """Create the customer directory structure"""
        try:
            customer_name = self.customer_name.text().strip()
            customer_id = self.customer_id.text().strip()
            
            if customer_name and customer_id:
                path = self.dir_manager.create_customer_structure(customer_name, customer_id)
                self.directory_path.setText(str(path))
                self.directory_path.setStyleSheet("color: green;")
                self.create_dir_button.setEnabled(False)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Created directory structure for customer:\n{path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create directory structure: {str(e)}"
            )

    def generate_license_data(self):
        """Generate license data with proper validation and error handling"""
        try:
            # CRITICAL: Must validate before generating
            valid, errors = self.validate_form()
            if not valid:
                raise ValueError(f"Validation failed: {', '.join(errors)}")
                
            # CRITICAL: Must check license system
            license_system = self.license_system_combo.currentData()
            if not license_system:
                raise ValueError("No license system selected")
                
            # CRITICAL: Must validate products
            products = self.get_products()
            if not products:
                raise ValueError("No products selected")
            
            # Create appropriate generator based on license system
            if license_system == 'flexlm':
                generator = FlexLMGenerator(self.signer)
            elif license_system == 'hasp':
                generator = HASPGenerator(self.signer)
            elif license_system == 'mysql':
                generator = MySQLGenerator(self.signer)
            else:
                raise ValueError(f"Unsupported license system: {license_system}")
                
            return generator.generate_license(
                self.get_customer_info(),
                self.get_license_info(),
                products,
                self.get_host_info()
            )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"License generation failed: {str(e)}")
            raise

    def get_license_info(self) -> Dict:
        """Get license information from the form"""
        return {
            'expiration_date': self.expiration_date.date().toPyDate().isoformat(),  # Convert to ISO string
            'maintenance_date': self.maintenance_date.date().toPyDate().isoformat(),  # Convert to ISO string
            'license_type': self.license_type_combo.currentData().value,
            'platforms': getattr(self, 'selected_platforms', []),
            # Add any other license info fields
        }

    def get_host_info(self) -> Dict:
        """Get host information"""
        # You might want to get this from a form or configuration
        return {
            'hostid': 'ANY',  # Default to ANY if not specified
            'port': '27000'   # Default port
        }

    def get_customer_info(self):
        """Get customer information from the form"""
        # CRITICAL: Must validate all fields
        customer_info = {
            'name': self.customer_name.text().strip(),
            'id': self.customer_id.text().strip(),
            'email': self.contact_email.text().strip()
        }
        
        # CRITICAL: Must check for empty values
        if not all(customer_info.values()):
            raise ValueError("All fields required")
        
        return customer_info

    def refresh_product_list(self):
        """Refresh the product checkboxes after changes"""
        # Clear existing checkboxes
        while self.product_layout.count():
            item = self.product_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Load products from config
        products = self.config.get('products', [])
        
        # Add checkbox for each product
        for product_data in products:
            product = Product(**product_data)
            checkbox = QCheckBox(f"{product.name} (v{product.version})")
            checkbox.setProperty('product_data', product_data)  # Store product data
            self.product_layout.addWidget(checkbox)
        
        # Add stretch at the end to keep checkboxes at top
        self.product_layout.addStretch()

    def get_selected_products(self) -> List[Product]:
        """Get list of selected products"""
        selected_products = []
        for i in range(self.product_layout.count()):
            item = self.product_layout.itemAt(i)
            if item and item.widget():
                checkbox = item.widget()
                if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                    product_data = checkbox.property('product_data')
                    selected_products.append(Product(**product_data))
        return selected_products

    def get_products(self) -> List[Product]:
        """Get selected products for the license"""
        return self.get_selected_products()

    def create_sql_options(self):
        """Create SQL-specific options widget"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.sql_host = QLineEdit()
        layout.addRow("Database Host:", self.sql_host)
        
        self.sql_port = QSpinBox()
        self.sql_port.setRange(1, 65535)
        self.sql_port.setValue(3306)  # Default MySQL port
        layout.addRow("Database Port:", self.sql_port)
        
        self.sql_database = QLineEdit()
        layout.addRow("Database Name:", self.sql_database)
        
        self.sql_username = QLineEdit()
        layout.addRow("Username:", self.sql_username)
        
        widget.setLayout(layout)
        return widget

    def populate_license_systems(self):
        """Populate the license systems combo box"""
        self.license_system_combo.clear()
        if self.config and 'license_systems' in self.config:
            for system_id, system in self.config['license_systems'].items():
                if system.get('enabled', True):
                    self.license_system_combo.addItem(system['name'], system_id)

    def browse_save_location(self):
        """Browse for save location, using server path if connected"""
        try:
            if self.server_connected:
                # Start from server path
                initial_path = self.server_path
            else:
                # Use local default path
                initial_path = self.config.get('paths', {}).get('default_save_path', '')

            # Show directory selection dialog
            selected_path = QFileDialog.getExistingDirectory(
                self,
                "Select Save Location",
                initial_path,
                QFileDialog.ShowDirsOnly
            )

            if selected_path:
                # Update the path display
                self.save_path_input.setText(selected_path)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to browse directories: {str(e)}"
            )

    def update_server_status(self, connected: bool, server_path: str = None):
        """Update the server connection status and path"""
        self.server_connected = connected
        self.server_path = server_path
        
        if connected and server_path:
            self.server_status_label.setText(f"Connected to: {server_path}")
            self.server_status_label.setStyleSheet("color: green;")
        else:
            self.server_status_label.setText("Not connected to server")
            self.server_status_label.setStyleSheet("color: gray;")

    def create_save_location_group(self):
        """Create the save location group with server status indicator"""
        group = QGroupBox("Save Location")
        layout = QVBoxLayout()  # Changed to QVBoxLayout for better organization
        
        # Add server status indicator
        self.server_status_label = QLabel("Not connected to server")
        self.server_status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.server_status_label)
        
        # Path selection layout
        path_layout = QHBoxLayout()
        self.save_path_input = QLineEdit()
        self.save_path_input.setText(self.config.get('paths', {}).get('default_save_path', ''))
        path_layout.addWidget(self.save_path_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_save_location)
        path_layout.addWidget(browse_button)
        
        layout.addLayout(path_layout)
        group.setLayout(layout)
        return group

    @pyqtSlot(dict)
    def update_server_connection(self, server_info):
        """Update the frame with server connection information"""
        self.server_info = server_info
        
        if server_info and server_info.get('connected'):
            # Update save location with server path
            server_path = server_info.get('path', '')
            self.save_path_input.setText(server_path)
            self.save_path_input.setToolTip(f"Connected to: {server_path}")
            self.save_path_input.setStyleSheet("QLineEdit { background-color: #e6ffe6; }")  # Light green background
            
            # Update server status in UI
            self.update_server_status(True, server_path)
            
            # If the server provides license system information, update the combo
            if 'license_systems' in server_info:
                self.config['license_systems'].update(server_info['license_systems'])
                self.populate_license_systems()
            
            # If the server provides product information, update the product list
            if 'products' in server_info:
                self.config['products'] = server_info['products']
                self.refresh_product_list()
                
            QMessageBox.information(
                self,
                "Server Connected",
                f"Successfully connected to server at:\n{server_path}"
            )
        else:
            # Reset to local configuration
            default_path = self.config.get('paths', {}).get('default_save_path', '')
            self.save_path_input.setText(default_path)
            self.save_path_input.setToolTip("Using local configuration")
            self.save_path_input.setStyleSheet("")  # Reset style
            
            # Update server status
            self.update_server_status(False)
            
            # Refresh with local configuration
            self.populate_license_systems()
            self.refresh_product_list()

    def enforce_license(self, license_data: Dict):
        """Enforce license using the LicenseEnforcer"""
        success = self.license_enforcer.enforce_license(license_data)
        if success:
            self.update_active_licenses_table()  # Update the table with active licenses
        else:
            QMessageBox.critical(self, "License Error", 
                                 "Failed to enforce license restrictions")
        return success

    def get_all_features(self) -> List:
        """Get all features available in the application"""
        # Implement logic to return all features
        return []

    def update_active_licenses_table(self):
        """Update the table with active licenses"""
        self.active_licenses_table.setRowCount(len(self.license_enforcer.active_licenses))
        for row, license_data in enumerate(self.license_enforcer.active_licenses):
            self.active_licenses_table.setItem(row, 0, QTableWidgetItem(license_data.get('id', '')))
            self.active_licenses_table.setItem(row, 1, QTableWidgetItem(license_data.get('type', '')))
            self.active_licenses_table.setItem(row, 2, QTableWidgetItem(license_data.get('expiration_date', '')))







