from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                           QPushButton, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
from ..dialogs.product_dialog import ProductDialog
from core.product import Product

class ProductManagerDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        self.setWindowTitle("Product Manager")
        layout = QVBoxLayout(self)
        
        # Product Table
        self.product_table = QTableWidget(0, 4)
        self.product_table.setHorizontalHeaderLabels(
            ["Product Name", "Version", "Features", "Description"]
        )
        layout.addWidget(self.product_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Product")
        edit_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Product")
        delete_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(save_btn)
        dialog_buttons.addWidget(cancel_btn)
        layout.addLayout(dialog_buttons)
        
    def load_products(self):
        """Load products from config"""
        self.product_table.setRowCount(0)
        products = self.config.get('products', [])
        
        for product in products:
            self.add_product_to_table(Product(**product))
    
    def add_product(self):
        """Add new product"""
        dialog = ProductDialog(parent=self)
        if dialog.exec_():
            product = dialog.get_product()
            self.add_product_to_table(product)
    
    def add_product_to_table(self, product: Product):
        """Add product to table"""
        row = self.product_table.rowCount()
        self.product_table.insertRow(row)
        
        self.product_table.setItem(row, 0, QTableWidgetItem(product.name))
        self.product_table.setItem(row, 1, QTableWidgetItem(product.version))
        self.product_table.setItem(row, 2, QTableWidgetItem(
            ", ".join(f.name for f in product.features)
        ))
        # Handle case where description might not exist
        description = getattr(product, 'description', '')
        self.product_table.setItem(row, 3, QTableWidgetItem(description))

    def edit_product(self):
        selected_items = self.product_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a product to edit")
            return
            
        selected_item = selected_items[0]
        product_id = selected_item.data(Qt.UserRole)
        
        dialog = ProductDialog(self.config, product_id, self)
        if dialog.exec_():
            self.load_products()  # Refresh the list after editing

    def delete_product(self):
        """Delete selected product"""
        selected_items = self.product_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a product to delete")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            self.product_table.removeRow(row)

    def accept(self):
        """Override accept to save products before closing"""
        try:
            # Convert products in table to list of dictionaries
            products = []
            for row in range(self.product_table.rowCount()):
                product = {
                    'name': self.product_table.item(row, 0).text(),
                    'version': self.product_table.item(row, 1).text(),
                    'features': [],  # Get features from the table cell
                    'quantity': 1  # Default quantity
                }
                
                # Parse features from the features column
                features_text = self.product_table.item(row, 2).text()
                if features_text:
                    features = [{'name': f.strip(), 'value': '', 'quantity': 1, 'enabled': True} 
                              for f in features_text.split(',')]
                    product['features'] = features

                products.append(product)
            
            # Update config with new products
            self.config['products'] = products
            
            super().accept()  # Call parent's accept method
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save products: {str(e)}"
            )
