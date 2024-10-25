from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import json
import base64
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LicenseSigner:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        
    def sign_license_data(self, license_data: Dict[str, Any]) -> str:
        """Sign license data and return signed license string"""
        try:
            # Add timestamp to license data
            license_data['timestamp'] = datetime.utcnow().isoformat()
            
            # Convert license data to JSON string
            license_json = json.dumps(license_data, sort_keys=True)
            
            # Sign the license data
            private_key = self.key_manager.load_private_key()
            signature = private_key.sign(
                license_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Create final license format
            final_license = {
                'data': license_data,
                'signature': base64.b64encode(signature).decode('utf-8')
            }
            
            return json.dumps(final_license, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to sign license: {str(e)}")
            raise
            
    def verify_license(self, license_string: str) -> bool:
        """Verify a signed license"""
        try:
            # Parse license
            license_data = json.loads(license_string)
            
            # Extract components
            data = license_data['data']
            signature = base64.b64decode(license_data['signature'])
            
            # Verify signature
            public_key = self.key_manager.load_public_key()
            data_json = json.dumps(data, sort_keys=True)
            
            public_key.verify(
                signature,
                data_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"License verification failed: {str(e)}")
            return False
