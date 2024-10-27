from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QListWidget, QPushButton, QListWidgetItem)
from PyQt5.QtCore import Qt

class PlatformSelectDialog(QDialog):
    def __init__(self, current_platforms=None, parent=None):
        super().__init__(parent)
        self.current_platforms = current_platforms or []
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the platform selection dialog UI"""
        self.setWindowTitle("Select Platforms")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Platform list
        self.platform_list = QListWidget()
        self.platform_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Add common platforms
        platforms = ["Windows", "Linux", "macOS", "Android", "iOS"]
        for platform in platforms:
            item = QListWidgetItem(platform)
            self.platform_list.addItem(item)
            # Pre-select current platforms
            if platform in self.current_platforms:
                item.setSelected(True)
                
        layout.addWidget(self.platform_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def get_selected_platforms(self):
        """Return list of selected platforms"""
        return [item.text() for item in self.platform_list.selectedItems()]
