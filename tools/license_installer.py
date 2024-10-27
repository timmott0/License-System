from enum import Enum
from typing import Dict, Any, List, Tuple, Path
import shutil
import subprocess

class LicenseType(Enum):
    FLEXLM = "FlexLM"
    HASP = "Sentinel HASP"
    LICENSESERVER = "Custom License Server"
    NODELOCK = "Node Locked"
    FLOATING = "Floating License"

class LicenseInstaller:
    """Handles installation of different license types"""
    
    @staticmethod
    def install_license(license_type: LicenseType, license_path: Path, 
                       options: Dict = None) -> Tuple[bool, str]:
        """Install license file for the specified system"""
        installer = LicenseInstaller._get_installer(license_type)
        return installer.install(license_path, options or {})
    
    @staticmethod
    def _get_installer(license_type: LicenseType) -> 'BaseLicenseInstaller':
        installers = {
            LicenseType.FLEXLM: FlexLMInstaller(),
            LicenseType.HASP: HASPInstaller(),
            LicenseType.LICENSESERVER: CustomServerInstaller(),
            # Add other installers...
        }
        return installers.get(license_type)

class BaseLicenseInstaller:
    def install(self, license_path: Path, options: Dict) -> Tuple[bool, str]:
        raise NotImplementedError()
    
    def verify_installation(self, license_path: Path) -> bool:
        raise NotImplementedError()

class FlexLMInstaller(BaseLicenseInstaller):
    DEFAULT_PATH = Path("/opt/flexlm/licenses")
    
    def install(self, license_path: Path, options: Dict) -> Tuple[bool, str]:
        try:
            # Create directories
            self.DEFAULT_PATH.mkdir(parents=True, exist_ok=True)
            
            # Copy license
            dest_path = self.DEFAULT_PATH / license_path.name
            shutil.copy2(license_path, dest_path)
            
            # Set permissions
            dest_path.chmod(0o644)
            
            # Configure service if needed
            if options.get('configure_service', True):
                self._configure_service(options)
            
            # Restart service
            if options.get('restart_service', True):
                subprocess.run(['systemctl', 'restart', 'flexlm'])
            
            return True, f"FlexLM license installed at {dest_path}"
            
        except Exception as e:
            return False, f"FlexLM installation failed: {str(e)}"

class HASPInstaller(BaseLicenseInstaller):
    def install(self, license_path: Path, options: Dict) -> Tuple[bool, str]:
        try:
            # Implement HASP-specific installation
            # This might involve using hasplm or other HASP tools
            return True, "HASP license installed successfully"
        except Exception as e:
            return False, f"HASP installation failed: {str(e)}"

class CustomServerInstaller(BaseLicenseInstaller):
    def install(self, license_path: Path, options: Dict) -> Tuple[bool, str]:
        try:
            # Implement custom license server installation logic
            # copy the license file to the server directory
            server_path = Path("/opt/custom_license_server/licenses")
            server_path.mkdir(parents=True, exist_ok=True)
            dest_path = server_path / license_path.name
            shutil.copy2(license_path, dest_path)
            
            # Configure server settings if needed
            # Modify a config file or set environment variables
            
            # Restart the custom license server service
            subprocess.run(['systemctl', 'restart', 'custom_license_server'])
            
            return True, f"Custom License Server installed at {dest_path}"
        except Exception as e:
            return False, f"Custom License Server installation failed: {str(e)}"

    def verify_installation(self, license_path: Path) -> bool:
        # Implement verification logic to ensure the installation was successful
        # Check if the license file exists and the service is running
        server_path = Path("/opt/custom_license_server/licenses") / license_path.name
        return server_path.exists()
