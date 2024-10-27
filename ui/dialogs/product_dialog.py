from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLabel, QLineEdit, QSpinBox, QPushButton,
                           QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
from core.product import Product, ProductFeature

class ProductDialog(QDialog):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.features = []
        self.setup_ui()
        if product:
            self.load_product(product)
            
    def setup_ui(self):
        """Initialize the product dialog UI"""
        self.setWindowTitle("Product Configuration")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        # Product Details
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        form_layout.addRow("Product Name:", self.name_edit)
        
        self.version_edit = QLineEdit()
        form_layout.addRow("Version:", self.version_edit)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        self.quantity_spin.setValue(1)
        form_layout.addRow("Quantity:", self.quantity_spin)
        
        layout.addLayout(form_layout)
        
        # Features Table
        layout.addWidget(QLabel("Features:"))
        
        self.features_table = QTableWidget(0, 4)
        self.features_table.setHorizontalHeaderLabels(["Name", "Value", "Quantity", "Enabled"])
        layout.addWidget(self.features_table)
        
        # Feature Buttons
        feature_buttons = QHBoxLayout()
        
        add_feature_btn = QPushButton("Add Feature")
        add_feature_btn.clicked.connect(self.add_feature)
        feature_buttons.addWidget(add_feature_btn)
        
        remove_feature_btn = QPushButton("Remove Feature")
        remove_feature_btn.clicked.connect(self.remove_feature)
        feature_buttons.addWidget(remove_feature_btn)
        
        layout.addLayout(feature_buttons)
        
        # Dialog Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def add_feature(self):
        """Add a new feature row to the table"""
        row = self.features_table.rowCount()
        self.features_table.insertRow(row)
        
        self.features_table.setItem(row, 0, QTableWidgetItem(""))
        self.features_table.setItem(row, 1, QTableWidgetItem(""))
        
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 9999)
        quantity_spin.setValue(1)
        self.features_table.setCellWidget(row, 2, quantity_spin)
        
        enabled_item = QTableWidgetItem()
        enabled_item.setCheckState(Qt.Checked)
        self.features_table.setItem(row, 3, enabled_item)
        
    def remove_feature(self):
        """Remove selected feature row"""
        current_row = self.features_table.currentRow()
        if current_row >= 0:
            self.features_table.removeRow(current_row)
            
    def load_product(self, product):
        """Load existing product data"""
        self.name_edit.setText(product.name)
        self.version_edit.setText(product.version)
        self.quantity_spin.setValue(product.quantity)
        
        for feature in product.features:
            row = self.features_table.rowCount()
            self.features_table.insertRow(row)
            
            self.features_table.setItem(row, 0, QTableWidgetItem(feature.name))
            self.features_table.setItem(row, 1, QTableWidgetItem(feature.value))
            
            quantity_spin = QSpinBox()
            quantity_spin.setRange(1, 9999)
            quantity_spin.setValue(feature.quantity)
            self.features_table.setCellWidget(row, 2, quantity_spin)
            
            enabled_item = QTableWidgetItem()
            enabled_item.setCheckState(Qt.Checked if feature.enabled else Qt.Unchecked)
            self.features_table.setItem(row, 3, enabled_item)
            
    def get_product(self) -> Product:
        """Get the configured product"""
        features = []
        for row in range(self.features_table.rowCount()):
            name = self.features_table.item(row, 0).text()
            value = self.features_table.item(row, 1).text()
            quantity = self.features_table.cellWidget(row, 2).value()
            enabled = self.features_table.item(row, 3).checkState() == Qt.Checked
            
            if name and value:  # Only add if name and value are not empty
                features.append(ProductFeature(
                    name=name,
                    value=value,
                    quantity=quantity,
                    enabled=enabled
                ))
        
        return Product(
            name=self.name_edit.text(),
            version=self.version_edit.text(),
            features=features,
            quantity=self.quantity_spin.value()
            # Removed description parameter
        )
