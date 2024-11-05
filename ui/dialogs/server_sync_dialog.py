from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                           QProgressBar, QLineEdit, QMessageBox)
from pathlib import Path
import os
import shutil

class ServerSyncDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Sync Products")
        
        layout = QVBoxLayout(self)
        
        # Server path display
        self.server_path_label = QLabel("Server Path:")
        layout.addWidget(self.server_path_label)
        
        self.server_path = QLineEdit()
        self.server_path.setReadOnly(True)
        layout.addWidget(self.server_path)
        
        # Status label
        self.status_label = QLabel("Ready to sync...")
        layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Test Connection button
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)
        
        # Sync button (initially disabled)
        self.sync_button = QPushButton("Sync")
        self.sync_button.setEnabled(False)
        self.sync_button.clicked.connect(self.sync_directories)
        layout.addWidget(self.sync_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)
        
        # Initialize server path from config
        self.server_path.setText(self.config.get('server', {}).get('path', ''))

    def test_connection(self):
        """Test connection to server and verify directory access"""
        try:
            server_path = Path(self.server_path.text())
            
            # Verify server path exists and is accessible
            if not server_path.exists():
                raise FileNotFoundError("Server path does not exist")
            
            # Try to list directory contents
            list(server_path.iterdir())
            
            # If successful, enable sync button and update status
            self.sync_button.setEnabled(True)
            self.status_label.setText("Connection successful! Ready to sync.")
            self.status_label.setStyleSheet("color: green")
            
            # Save server path to config
            if 'server' not in self.config:
                self.config['server'] = {}
            self.config['server']['path'] = str(server_path)
            
            QMessageBox.information(self, "Success", "Successfully connected to server directory!")
            
        except Exception as e:
            self.sync_button.setEnabled(False)
            self.status_label.setText(f"Connection failed: {str(e)}")
            self.status_label.setStyleSheet("color: red")
            QMessageBox.critical(self, "Error", f"Failed to connect to server: {str(e)}")

    def sync_directories(self):
        """Sync local and server directories"""
        try:
            server_path = Path(self.server_path.text())
            local_path = Path(self.config['paths']['licenses'])
            
            # Create local directory if it doesn't exist
            local_path.mkdir(parents=True, exist_ok=True)
            
            # Count total files for progress bar
            total_files = len(list(server_path.glob('**/*')))
            self.progress.setMaximum(total_files)
            current_progress = 0
            
            # Sync files from server to local
            for src_path in server_path.glob('**/*'):
                if src_path.is_file():
                    # Calculate relative path
                    rel_path = src_path.relative_to(server_path)
                    dst_path = local_path / rel_path
                    
                    # Create parent directories if needed
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_path, dst_path)
                    
                    # Update progress
                    current_progress += 1
                    self.progress.setValue(current_progress)
            
            self.status_label.setText("Sync completed successfully!")
            QMessageBox.information(self, "Success", "Directory sync completed!")
            
        except Exception as e:
            self.status_label.setText(f"Sync failed: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to sync directories: {str(e)}")

    def accept(self):
        # Save any final config changes before closing
        if self.server_path.text():
            if 'server' not in self.config:
                self.config['server'] = {}
            self.config['server']['path'] = self.server_path.text()
        super().accept()

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
