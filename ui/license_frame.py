from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton,
                           QScrollArea, QWidget, QGroupBox, QTableWidget, QTableWidgetItem,
                           QDialog, QTextEdit, QMessageBox, QStackedWidget, QFormLayout, QSpinBox,
                           QFileDialog)
from PyQt5.QtCore import Qt, QDate
from .dialogs.platform_select import PlatformSelectDialog
from .dialogs.product_dialog import ProductDialog
from core.product import Product
from core.license_generator import LicenseGeneratorFactory
from encryption.key_management import KeyManager
from encryption.license_signing import LicenseSigner
from pathlib import Path
import json
from utils.validation import LicenseValidator
from utils.host_identifier import HostIdentifier
from typing import List, Tuple, Dict
from enum import Enum

class LicenseType(Enum):
    FLEXLM = "FlexLM"
    HASP = "Sentinel HASP"
    LICENSESERVER = "Custom License Server"
    NODELOCK = "Node Locked"
    FLOATING = "Floating License"

class BaseLicenseGenerator:
    """Base class for all license generators"""
    
    def __init__(self, signer):
        self.signer = signer
    
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        raise NotImplementedError()
    
    def save_license(self, license_data: str, output_path: Path):
        raise NotImplementedError()

class FlexLMGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        flexlm_data = [
            f"SERVER this_host {host_info.get('hostid', 'ANY')} {license_info.get('port', '27000')}",
            "VENDOR vendor_daemon",
            ""
        ]
        
        for product in products:
            feature_line = (
                f"FEATURE {product.name} vendor_daemon {product.version} "
                f"{license_info['expiration_date'].strftime('%d-%b-%Y')} "
                f"{product.quantity} HOSTID={host_info.get('hostid', 'ANY')} "
                f"VENDOR_STRING=\"{customer_info['name']}\" "
                f"ISSUER={customer_info['id']} "
                f"SIGN={self.signer.generate_flexlm_signature()}"
            )
            flexlm_data.append(feature_line)
            
        return "\n".join(flexlm_data)

class HASPGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        # Implement HASP-specific license generation
        hasp_data = {
            "header": {
                "type": "hasp",
                "version": "1.0"
            },
            "customer": customer_info,
            "products": [p.to_dict() for p in products],
            # Add HASP-specific fields
        }
        return self.signer.sign_hasp_data(hasp_data)

# Add other generator implementations...

class LicenseFrame(QFrame):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the license frame UI"""
        main_layout = QVBoxLayout(self)
        
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
        
    def create_customer_group(self):
        """Create the customer information group"""
        group = QGroupBox("Customer Information")
        layout = QGridLayout()
        
        # Customer Name
        layout.addWidget(QLabel("Customer Name:"), 0, 0)
        self.customer_name = QLineEdit()
        layout.addWidget(self.customer_name, 0, 1)
        
        # Customer ID
        layout.addWidget(QLabel("Customer ID:"), 1, 0)
        self.customer_id = QLineEdit()
        layout.addWidget(self.customer_id, 1, 1)
        
        # Contact Email
        layout.addWidget(QLabel("Contact Email:"), 2, 0)
        self.contact_email = QLineEdit()
        layout.addWidget(self.contact_email, 2, 1)
        
        group.setLayout(layout)
        return group
        
    def create_license_group(self):
        """Create the license settings group"""
        group = QGroupBox("License Settings")
        layout = QGridLayout()
        
        # License Type
        layout.addWidget(QLabel("License Type:"), 0, 0)
        self.license_type = QComboBox()
        self.license_type.addItems(["Node Locked", "Server Based", "Redundant"])
        self.license_type.currentTextChanged.connect(self.on_license_type_changed)
        layout.addWidget(self.license_type, 0, 1)
        
        # Platform
        layout.addWidget(QLabel("Platform:"), 1, 0)
        self.platform_button = QPushButton("Select Platform...")
        self.platform_button.clicked.connect(self.show_platform_dialog)
        layout.addWidget(self.platform_button, 1, 1)
        
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
        
        # Add license system selection
        layout.addWidget(QLabel("License System:"), 4, 0)
        self.license_system_combo = QComboBox()
        self.license_system_combo.setObjectName("license_system_combo")
        
        # Populate the license systems dropdown using local config
        if self.config:
            license_systems = self.config.get('license_systems', {})
            for system_id, system in license_systems.items():
                if system.get('enabled', True):
                    self.license_system_combo.addItem(system['name'], system_id)
        
        layout.addWidget(self.license_system_combo, 4, 1)
        
        # Create stacked widget for system-specific options
        self.system_options = QStackedWidget()
        
        # Add FlexLM options
        flexlm_widget = self.create_flexlm_options()
        self.system_options.addWidget(flexlm_widget)
        
        # Add HASP options
        hasp_widget = self.create_hasp_options()
        self.system_options.addWidget(hasp_widget)
        
        # Connect the signal after adding widgets
        self.license_system_combo.currentIndexChanged.connect(self.on_license_system_changed)
        
        # Add stacked widget to layout
        layout.addWidget(self.system_options, 5, 0, 1, 2)
        
        group.setLayout(layout)
        return group
        
    def create_product_group(self):
        """Create the product settings group"""
        group = QGroupBox("Product Settings")
        layout = QVBoxLayout()
        
        # Product Table
        self.product_table = QTableWidget(0, 4)
        self.product_table.setHorizontalHeaderLabels(
            ["Product Name", "Version", "Quantity", "Features"]
        )
        layout.addWidget(self.product_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_product_btn = QPushButton("Add Product")
        add_product_btn.clicked.connect(self.add_product)
        button_layout.addWidget(add_product_btn)
        
        edit_product_btn = QPushButton("Edit Product")
        edit_product_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(edit_product_btn)
        
        remove_product_btn = QPushButton("Remove Product")
        remove_product_btn.clicked.connect(self.remove_product)
        button_layout.addWidget(remove_product_btn)
        
        layout.addLayout(button_layout)
        group.setLayout(layout)
        return group
        
    def on_license_type_changed(self, license_type):
        """Handle license type changes"""
        # Update UI based on license type
        pass
        
    def show_platform_dialog(self):
        """Show platform selection dialog"""
        dialog = PlatformSelectDialog(self)
        if dialog.exec_():
            # Handle platform selection
            pass
            
    def validate_form(self) -> Tuple[bool, List[str]]:
        """Validate all form inputs"""
        errors = []
        
        # Validate customer information
        customer_info = {
            'name': self.customer_name.text(),
            'id': self.customer_id.text(),
            'email': self.contact_email.text()
        }
        errors.extend(LicenseValidator.validate_customer_info(customer_info))
        
        # Validate dates
        valid_dates, date_error = LicenseValidator.validate_dates(
            self.expiration_date.date().toPyDate(),
            self.maintenance_date.date().toPyDate()
        )
        if not valid_dates:
            errors.append(date_error)
        
        # Validate products
        if self.product_table.rowCount() == 0:
            errors.append("At least one product is required")
        
        # Validate platform selection
        if not hasattr(self, 'selected_platforms') or not self.selected_platforms:
            errors.append("At least one platform must be selected")
        
        return len(errors) == 0, errors

    def generate_license(self):
        """Generate license based on selected system"""
        try:
            # Get selected license type
            license_type = LicenseType(self.license_system_combo.currentText())
            
            # Get system-specific options
            system_options = self.get_system_options(license_type)
            
            # Create appropriate generator
            generator = LicenseGeneratorFactory.create_generator(
                license_type,
                self.signer
            )
            
            # Generate license with system-specific options
            license_data = generator.generate_license(
                self.get_customer_info(),
                {**self.get_license_info(), **system_options},
                self.get_products(),
                self.get_host_info()
            )
            
            # Save license
            self.save_license(license_data, license_type)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate license: {str(e)}")
    
    def get_system_options(self, license_type: LicenseType) -> Dict:
        """Get options specific to the selected license system"""
        if license_type == LicenseType.FLEXLM:
            return {
                'port': self.flexlm_port.value(),
                'vendor_daemon': self.flexlm_vendor.text(),
                'additional_options': self.flexlm_options.text()
            }
        elif license_type == LicenseType.HASP:
            return {
                'feature_id': self.hasp_feature_id.value(),
                'vendor_code': self.hasp_vendor_code.text()
            }
        # Add other system options...
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
                'type': self.license_type.currentText(),
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
        if system_id:
            system = self.config['license_systems'][system_id]
            # Update port
            self.flexlm_port.setValue(system['default_port'])  # Correct attribute
            # Update other fields based on selected system
            if system_id == 'flexlm':
                self.flexlm_vendor.setText('fe')
                self.flexlm_options.setText('ewew')
            elif system_id == 'sentinel':
                self.hasp_vendor_code.setText('hasp')
                self.hasp_feature_id.setValue(1)
            # Add other systems if necessary

    def save_license(self, license_data: str, license_type: LicenseType):
        """Save the license file with the appropriate extension"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save License File",
            "",
            f"{license_type.value} License Files (*.{license_type.value}lic);;All Files (*.*)"
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(license_data)
            QMessageBox.information(
                self,
                "Success",
                f"License file saved successfully as {file_path}"
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

















