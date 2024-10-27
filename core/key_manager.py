from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self, private_key_path=None, public_key_path=None):
        """Initialize KeyManager
        Args:
            private_key_path (str|Path): Path to private key file
            public_key_path (str|Path): Path to public key file
        """
        self.private_key_path = Path(private_key_path) if private_key_path else None
        self.public_key_path = Path(public_key_path) if public_key_path else None
        
    def validate_key(self, key_path: Path) -> bool:
        """Validate a key file"""
        try:
            with open(key_path, 'rb') as key_file:
                key_data = key_file.read()
                try:
                    # Try loading as public key
                    serialization.load_pem_public_key(key_data, backend=default_backend())
                    logger.info(f"Valid public key found at: {key_path}")
                    return True
                except ValueError:
                    try:
                        # Try loading as private key
                        serialization.load_pem_private_key(
                            key_data, 
                            password=None, 
                            backend=default_backend()
                        )
                        logger.info(f"Valid private key found at: {key_path}")
                        return True
                    except ValueError:
                        logger.error(f"Invalid key format at: {key_path}")
                        return False
        except Exception as e:
            logger.error(f"Key validation failed: {e}")
            return False
