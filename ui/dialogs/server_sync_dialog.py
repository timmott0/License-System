from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar

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
