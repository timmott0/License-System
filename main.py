import sys
import logging
from pathlib import Path
import json
from PyQt5.QtWidgets import QApplication

# Local imports
from ui.main_window import MainWindow
from utils.file_operations import ensure_directory_exists

class LicenseManagementSystem:
    def __init__(self):
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configure logging for the application"""
        log_dir = Path("logs")
        ensure_directory_exists(log_dir)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "app.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("License Management System starting...")

    def load_config(self):
        """Load application configuration from config files"""
        try:
            config_path = Path("src/config/settings.json")
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info("Configuration loaded successfully")
            
            # Remove or comment out any code that tries to load license_systems.json
            # It might look something like this:
            # license_systems_path = Path("config/license_systems.json")  # Remove this
            # with open(license_systems_path, 'r') as f:                 # Remove this
            #     self.license_systems = json.load(f)                    # Remove this
        except FileNotFoundError:
            self.logger.error("Configuration file not found")
            self.config = {}
        except json.JSONDecodeError:
            self.logger.error("Invalid configuration file format")
            self.config = {}

    def run(self):
        """Initialize and run the application"""
        try:
            app = QApplication(sys.argv)
            # Remove the license_systems parameter since MainWindow doesn't expect it
            main_window = MainWindow(self.config)
            main_window.show()
            return app.exec_()
        except Exception as e:
            self.logger.error(f"Failed to start application: {str(e)}")
            return 1

def main():
    """Entry point of the application"""
    lms = LicenseManagementSystem()
    sys.exit(lms.run())

if __name__ == "__main__":
    main()

