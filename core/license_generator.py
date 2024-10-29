# Standard library imports
from datetime import datetime
from typing import List, Dict, Any, Union
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
    def create_generator(license_type: Union[str, LicenseType], signer: LicenseSigner) -> 'BaseLicenseGenerator':
        """
        Create appropriate generator based on license system type
        Supports both string-based types and LicenseType enum
        """
        # Map both enum types and string IDs to generators
        generator_map = {
            # Enum-based mappings
            LicenseType.SINGLE_USER: NodeLockedGenerator,
            LicenseType.VOLUME: NodeLockedGenerator,
            LicenseType.SUBSCRIPTION: CustomServerGenerator,
            LicenseType.TRIAL: CustomServerGenerator,
            LicenseType.FREEMIUM: CustomServerGenerator,
            LicenseType.FLOATING: FloatingLicenseGenerator,
            LicenseType.CONCURRENT: FloatingLicenseGenerator,
            LicenseType.NODELOCK: NodeLockedGenerator,
            LicenseType.SQL: SQLLicenseGenerator,
            # String-based mappings for backwards compatibility
            'flexlm': FlexLMGenerator,
            'hasp': HASPGenerator,
            'mysql': SQLLicenseGenerator,
            'custom': CustomServerGenerator,
            'nodelock': NodeLockedGenerator,
            'floating': FloatingLicenseGenerator,
            'licenseserver': CustomServerGenerator
        }
        
        # If input is string, convert to lowercase for matching
        if isinstance(license_type, str):
            license_type = license_type.lower()
            
        generator_class = generator_map.get(license_type)
        if generator_class:
            return generator_class(signer)
        else:
            raise ValueError(f"Unsupported license system: {license_type}")

class BaseLicenseGenerator:
    """Base class for all license generators"""
    
    def __init__(self, signer: LicenseSigner):
        self.signer = signer
    
    def generate_license(self, customer_info: Dict, license_info: Dict, 
                        products: List[Product], host_info: Dict) -> str:
        """Validate common fields before specific generation"""
        if not all([customer_info, license_info, products]):
            raise ValueError("Missing required license information")
        
        # Validate customer info
        required_customer_fields = ['name', 'id', 'email']
        if not all(field in customer_info for field in required_customer_fields):
            raise ValueError("Missing required customer information")
            
        # Validate license info
        required_license_fields = ['license_type', 'expiration_date']
        if not all(field in license_info for field in required_license_fields):
            raise ValueError("Missing required license information")
        
        return self._generate_specific_license(customer_info, license_info, products, host_info)
    
    def _generate_specific_license(self, customer_info: Dict, license_info: Dict, 
                                 products: List[Product], host_info: Dict) -> str:
        """To be implemented by specific generators"""
        raise NotImplementedError()

class FlexLMGenerator(BaseLicenseGenerator):
    def _generate_specific_license(self, customer_info: Dict, license_info: Dict, 
                                 products: List[Product], host_info: Dict) -> str:
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
    def _generate_specific_license(self, customer_info: Dict, license_info: Dict, 
                                 products: List[Product], host_info: Dict) -> str:
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
    def _generate_specific_license(self, customer_info: Dict, license_info: Dict, 
                                 products: List[Product], host_info: Dict) -> str:
        license_data = {
            "type": "custom_server",
            "customer": customer_info,
            "license": license_info,
            "products": [p.to_dict() for p in products],
            "host": host_info
        }
        return self.signer.sign_license_data(license_data)

class NodeLockedGenerator(BaseLicenseGenerator):
    def _generate_specific_license(self, customer_info: Dict, license_info: Dict, 
                                 products: List[Product], host_info: Dict) -> str:
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
    def _generate_specific_license(self, customer_info: Dict, license_info: Dict, 
                                 products: List[Product], host_info: Dict) -> str:
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
    def _generate_specific_license(self, customer_info: Dict, license_info: Dict, 
                                 products: List[Product], host_info: Dict) -> str:
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
