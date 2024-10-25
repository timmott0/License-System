# Standard library and GUI imports
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QFileDialog
from pathlib import Path
# Custom utility imports for license verification
from utils.validation import LicenseVerifier
import json

class LicenseViewer(QMainWindow):
    """A GUI application for viewing and verifying license files"""
    
    def __init__(self):
        """Initialize the main window and setup the UI components"""
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Configure the user interface layout and components"""
        # Set window properties
        self.setWindowTitle("License Viewer")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)  # Make it read-only to prevent editing
        layout.addWidget(self.text_display)
        
        # Create and configure the open button
        open_button = QPushButton("Open License")
        open_button.clicked.connect(self.open_license)  # Connect button click to handler
        layout.addWidget(open_button)
        
    def open_license(self):
        """
        Handle the open license button click event.
        Opens a file dialog and displays the license content if valid.
        """
        # Show file dialog to select license file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open License File",
            "",  # Start in current directory
            "License Files (*.lic);;All Files (*.*)"  # File type filters
        )
        
        if file_path:
            # Verify the selected license file
            valid, message, license_data = LicenseVerifier.verify_license_file(
                file_path,
                'config/rsa_keys/public_key.pem'  # Path to public key for verification
            )
            
            # Prepare the display text with verification results
            display_text = f"License Status: {'Valid' if valid else 'Invalid'}\n"
            display_text += f"Message: {message}\n\n"
            
            # If license data was successfully extracted, add it to display
            if license_data:
                display_text += "License Details:\n"
                display_text += json.dumps(license_data, indent=2)
            
            # Update the text display with results
            self.text_display.setPlainText(display_text)

def main():
    """Initialize and run the license viewer application"""
    # Create the Qt application instance
    app = QApplication(sys.argv)
    # Create and show the main window
    viewer = LicenseViewer()
    viewer.show()
    # Start the application event loop
    sys.exit(app.exec_())

# Only run if script is executed directly
if __name__ == "__main__":
    main()
