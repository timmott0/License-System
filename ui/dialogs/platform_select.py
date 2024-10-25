from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QListWidget, QPushButton, QLabel)

class PlatformSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_platforms = set()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the platform selection dialog UI"""
        self.setWindowTitle("Select Platforms")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        layout.addWidget(QLabel("Select target platforms for the license:"))
        
        # Platform List
        self.platform_list = QListWidget()
        self.platform_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Add common platforms
        platforms = [
            "Windows x86",
            "Windows x64",
            "Linux x86",
            "Linux x64",
            "macOS x64",
            "macOS ARM64",
            "AIX",
            "Solaris SPARC",
            "Solaris x86"
        ]
        
        for platform in platforms:
            self.platform_list.addItem(platform)
            
        layout.addWidget(self.platform_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_selection)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def select_all(self):
        """Select all platforms"""
        for i in range(self.platform_list.count()):
            self.platform_list.item(i).setSelected(True)
            
    def clear_selection(self):
        """Clear all selections"""
        for i in range(self.platform_list.count()):
            self.platform_list.item(i).setSelected(False)
            
    def get_selected_platforms(self):
        """Get list of selected platforms"""
        return [item.text() for item in self.platform_list.selectedItems()]
