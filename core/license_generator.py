# Standard library imports
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import json
import logging
from enum import Enum

# Local imports
from .product import Product
from encryption.license_signing import LicenseSigner
from config.license_systems import DatabaseConfig

# Configure logger for this module
logger = logging.getLogger(__name__)

class LicenseType(Enum):
    SINGLE_USER = "Single-User License"
    VOLUME = "Volume License"
    SUBSCRIPTION = "Subscription License"
    TRIAL = "Trial License"
    FREEMIUM = "Freemium License"
    FLOATING = "Floating License"
    CONCURRENT = "Concurrent License"
    NODELOCK = "Node-Locked License"
    SQL = "SQL Database License"

class LicenseGeneratorFactory:
    """Factory to create appropriate license generator based on type"""
    
    @staticmethod
    def create_generator(license_type: LicenseType, signer) -> 'BaseLicenseGenerator':
        if license_type == LicenseType.FLEXLM:
            return FlexLMGenerator(signer)
        elif license_type == LicenseType.HASP:
            return HASPGenerator(signer)
        elif license_type == LicenseType.LICENSESERVER:
            return CustomServerGenerator(signer)
        elif license_type == LicenseType.NODELOCK:
            return NodeLockedGenerator(signer)
        elif license_type == LicenseType.FLOATING:
            return FloatingLicenseGenerator(signer)
        elif license_type == LicenseType.SQL:  # Add this case
            return SQLLicenseGenerator(signer)
        else:
            raise ValueError(f"Unsupported license type: {license_type}")

class BaseLicenseGenerator:
    """Base class for all license generators"""
    
    def __init__(self, signer):
        self.signer = signer
    
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        raise NotImplementedError()
    
    def save_license(self, license_data: str, output_path: Path):
        raise NotImplementedError()

class FlexLMGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        flexlm_data = [
            f"SERVER this_host {host_info.get('hostid', 'ANY')} {license_info.get('port', '27000')}",
            "VENDOR vendor_daemon",
            ""
        ]
        
        for product in products:
            feature_line = (
                f"FEATURE {product.name} vendor_daemon {product.version} "
                f"{license_info['expiration_date'].strftime('%d-%b-%Y')} "
                f"{product.quantity} HOSTID={host_info.get('hostid', 'ANY')} "
                f"VENDOR_STRING=\"{customer_info['name']}\" "
                f"ISSUER={customer_info['id']} "
                f"SIGN={self.signer.generate_flexlm_signature()}"
            )
            flexlm_data.append(feature_line)
            
        return "\n".join(flexlm_data)

class HASPGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        # Implement HASP-specific license generation
        hasp_data = {
            "header": {
                "type": "hasp",
                "version": "1.0"
            },
            "customer": customer_info,
            "products": [p.to_dict() for p in products],
            # Add HASP-specific fields
        }
        return self.signer.sign_hasp_data(hasp_data)

class CustomServerGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        license_data = {
            "type": "custom_server",
            "customer": customer_info,
            "license": license_info,
            "products": [p.to_dict() for p in products],
            "host": host_info
        }
        return self.signer.sign_license_data(license_data)

class NodeLockedGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        license_data = {
            "type": "node_locked",
            "customer": customer_info,
            "license": license_info,
            "products": [p.to_dict() for p in products],
            "host": host_info,
            "machine_id": host_info.get('machine_id', '')
        }
        return self.signer.sign_license_data(license_data)

class FloatingLicenseGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        license_data = {
            "type": "floating",
            "customer": customer_info,
            "license": license_info,
            "products": [p.to_dict() for p in products],
            "host": host_info,
            "concurrent_users": license_info.get('concurrent_users', 1)
        }
        return self.signer.sign_license_data(license_data)

# Add other generator implementations After Matt shows me how to do it

# Add this class after your other generator classes
class SQLLicenseGenerator(BaseLicenseGenerator):
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List, host_info: Dict) -> str:
        """Generate SQL-based license"""
        license_data = {
            "type": "sql",
            "customer": customer_info,
            "license": license_info,
            "products": [p.to_dict() for p in products],
            "host": host_info,
            "database_config": license_info.get('database_config', {})
        }
        return self.signer.sign_license_data(license_data)

    def save_license(self, license_data: str, db_config: DatabaseConfig):
        """Save license to SQL database"""
        # Implementation will depend on your database structure
        pass
