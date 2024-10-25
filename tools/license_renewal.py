import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
from utils.validation import LicenseVerifier
from core.license_generator import LicenseGenerator
from encryption.key_management import KeyManager
from encryption.license_signing import LicenseSigner

logger = logging.getLogger(__name__)

class LicenseRenewal:
    """Handles the renewal process for existing software licenses"""
    def __init__(self, key_manager: KeyManager):
        """
        Initialize the renewal system with necessary components
        Args:
            key_manager: Manages encryption keys for license signing
        """
        self.key_manager = key_manager
        self.signer = LicenseSigner(key_manager)
        self.generator = LicenseGenerator(self.signer)

    def renew_license(self, 
                     license_path: Path,
                     validity_days: int,
                     maintenance_days: Optional[int] = None) -> Dict:
        """
        Renew an existing license with new expiration dates
        
        Args:
            license_path: Path to the existing license file
            validity_days: Number of days to extend the license
            maintenance_days: Optional maintenance period (defaults to validity_days)
            
        Returns:
            Dict containing paths and dates for the renewed license
            
        Raises:
            ValueError: If the existing license is invalid
        """
        # Verify the authenticity and validity of the current license
        valid, message, license_data = LicenseVerifier.verify_license_file(
            str(license_path),
            str(self.key_manager.public_key_path)
        )

        if not valid:
            raise ValueError(f"Invalid license file: {message}")

        # Calculate new expiration dates based on current date
        new_expiration = datetime.now() + timedelta(days=validity_days)
        new_maintenance = datetime.now() + timedelta(days=maintenance_days if maintenance_days else validity_days)

        # Update the license data with new dates and metadata
        license_data['license']['expiration_date'] = new_expiration.isoformat()
        license_data['license']['maintenance_date'] = new_maintenance.isoformat()
        license_data['metadata']['renewed_at'] = datetime.now().isoformat()
        license_data['metadata']['previous_expiration'] = license_data['license']['expiration_date']

        # Generate and sign the new license data
        new_license_data = self.signer.sign_license_data(license_data)

        # Save the renewed license with a modified filename
        renewed_path = license_path.with_stem(f"{license_path.stem}_renewed")
        self.generator.save_license(new_license_data, renewed_path)

        return {
            "original_license": str(license_path),
            "renewed_license": str(renewed_path),
            "new_expiration": new_expiration.isoformat(),
            "new_maintenance": new_maintenance.isoformat()
        }

def main():
    """
    Command-line interface for license renewal
    Processes arguments and handles the renewal workflow
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='License Renewal Tool')
    parser.add_argument('license_file', help='Path to the license file to renew')
    parser.add_argument('--validity', type=int, default=365,
                      help='New validity period in days')
    parser.add_argument('--maintenance', type=int,
                      help='New maintenance period in days (defaults to validity period)')
    parser.add_argument('--log-file', default='logs/renewal.log',
                      help='Log file path')

    args = parser.parse_args()

    # Configure logging to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(args.log_file),
            logging.StreamHandler()
        ]
    )

    try:
        # Initialize components and perform renewal
        key_manager = KeyManager(Path('config/rsa_keys'))
        renewal = LicenseRenewal(key_manager)
        
        result = renewal.renew_license(
            Path(args.license_file),
            args.validity,
            args.maintenance
        )

        print(f"Renewal complete. Results: {result}")

    except Exception as e:
        logger.error(f"Error renewing license: {e}")

if __name__ == "__main__":
    main()
