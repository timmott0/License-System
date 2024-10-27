from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QSpinBox, QPushButton)

class FloatingLicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Floating License Configuration")
        
        layout = QVBoxLayout()
        
        # Concurrent users input
        users_layout = QHBoxLayout()
        users_layout.addWidget(QLabel("Concurrent Users:"))
        self.users_spinbox = QSpinBox()
        self.users_spinbox.setMinimum(1)
        self.users_spinbox.setMaximum(1000)
        self.users_spinbox.setValue(1)
        users_layout.addWidget(self.users_spinbox)
        
        layout.addLayout(users_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_values(self):
        return {
            'concurrent_users': self.users_spinbox.value()
        }
