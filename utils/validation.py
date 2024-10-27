import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from encryption.key_management import KeyManager
from encryption.license_signing import LicenseSigner
from utils.host_identifier import HostIdentifier

class LicenseValidator:
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            return False, "Email is required"
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, ""

    @staticmethod
    def validate_dates(expiration: datetime, maintenance: datetime) -> Tuple[bool, str]:
        """Validate license dates"""
        now = datetime.now()
        if expiration < now:
            return False, "Expiration date cannot be in the past"
        if maintenance > expiration:
            return False, "Maintenance date cannot be after expiration"
        return True, ""

    @staticmethod
    def validate_product(product: Dict) -> Tuple[bool, str]:
        """Validate product configuration"""
        if not product.get('name'):
            return False, "Product name is required"
        if not product.get('version'):
            return False, "Product version is required"
        if not product.get('features'):
            return False, "At least one feature is required"
        return True, ""

    @staticmethod
    def validate_customer_info(customer_info: Dict) -> List[str]:
        """Validate customer information"""
        errors = []
        if not customer_info.get('name'):
            errors.append("Customer name is required")
        if not customer_info.get('id'):
            errors.append("Customer ID is required")
        valid_email, email_error = LicenseValidator.validate_email(customer_info.get('email', ''))
        if not valid_email:
            errors.append(email_error)
        return errors

class LicenseVerifier:
    @staticmethod
    def verify_license_file(license_path: str, public_key_path: str) -> Tuple[bool, str, Optional[Dict]]:
        """Verify a license file's signature and return its contents"""
        try:
            with open(license_path, 'r') as f:
                license_data = json.loads(f.read())

            # Verify signature
            signer = LicenseSigner(KeyManager(Path(public_key_path).parent))
            if not signer.verify_license(json.dumps(license_data)):
                return False, "Invalid license signature", None

            # Verify expiration
            exp_date = datetime.fromisoformat(license_data['data']['license']['expiration_date'])
            if exp_date < datetime.now():
                return False, "License has expired", license_data['data']

            # Verify host binding if applicable
            if license_data['data']['license']['type'] == 'node_locked':
                current_host = HostIdentifier.get_host_identifiers()
                if not all(current_host.get(k) == v for k, v in license_data['data']['host'].items()):
                    return False, "License is not valid for this machine", license_data['data']

            return True, "License is valid", license_data['data']

        except Exception as e:
            return False, f"Error verifying license: {str(e)}", None
