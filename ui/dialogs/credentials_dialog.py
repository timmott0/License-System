from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                           QLineEdit, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt

class CredentialsDialog(QDialog):
    def __init__(self, server_path: str, parent=None):
        super().__init__(parent)
        self.server_path = server_path
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Server Credentials")
        layout = QVBoxLayout(self)
        
        # Create form for credentials
        form = QFormLayout()
        
        # Username field
        self.username = QLineEdit()
        form.addRow("Username:", self.username)
        
        # Password field
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.password)
        
        layout.addLayout(form)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_credentials(self):
        return {
            'username': self.username.text(),
            'password': self.password.text()
        }
