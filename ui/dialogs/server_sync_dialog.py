from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
from pathlib import Path
import os

class ServerSyncDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Sync Products")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Synchronizing products with server..."))
        
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        self.button = QPushButton("Close")
        self.button.clicked.connect(self.accept)
        layout.addWidget(self.button)

    def update_path_settings(self):
        """Update path settings to user's home directory after successful connection"""
        home_dir = str(Path.home())
        
        # Update paths in config
        if 'paths' in self.config:
            self.config['paths'].update({
                'config': os.path.join(home_dir, '.config/app'),
                'keys': os.path.join(home_dir, '.config/app/keys'),
                'licenses': os.path.join(home_dir, '.config/app/licenses')
            })
            
    def accept(self):
        # Update paths before closing
        self.update_path_settings()
        super().accept()
