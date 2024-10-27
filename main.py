import sys
import logging
from pathlib import Path
import json
import os
from PyQt5.QtWidgets import QApplication

# Local imports
from ui.main_window import MainWindow
from utils.file_operations import ensure_directory_exists

class LicenseManagementSystem:
    def __init__(self):
        # Initialize config file path
        self.config_file = Path("config/config.json")
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
        """Load configuration from file or initialize defaults"""
        try:
            # Ensure config directory exists
            ensure_directory_exists(self.config_file.parent)
            
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
            
            # Initialize license systems if not present
            if 'license_systems' not in self.config:
                from config.license_systems import DEFAULT_SYSTEMS
                self.config['license_systems'] = {
                    system_id: {
                        "name": system.name,
                        "enabled": system.enabled,
                        "install_path": str(system.install_path),
                        "default_port": system.default_port,
                        "description": system.description
                    }
                    for system_id, system in DEFAULT_SYSTEMS.items()
                }
                
                # Save the initial configuration
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f, indent=4)
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise

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
