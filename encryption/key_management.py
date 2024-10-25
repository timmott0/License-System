from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self, key_dir: Path):
        self.key_dir = key_dir
        self.private_key_path = key_dir / "private_key.pem"
        self.public_key_path = key_dir / "public_key.pem"
        
    def generate_key_pair(self):
        """Generate new RSA key pair"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            public_key = private_key.public_key()
            
            # Save private key
            with open(self.private_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Save public key
            with open(self.public_key_path, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
                
            logger.info("Generated new RSA key pair")
            return private_key, public_key
            
        except Exception as e:
            logger.error(f"Failed to generate key pair: {str(e)}")
            raise
            
    def load_private_key(self):
        """Load existing private key"""
        try:
            with open(self.private_key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            return private_key
        except FileNotFoundError:
            logger.warning("Private key not found, generating new key pair")
            return self.generate_key_pair()[0]
            
    def load_public_key(self):
        """Load existing public key"""
        try:
            with open(self.public_key_path, 'rb') as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            return public_key
        except FileNotFoundError:
            logger.warning("Public key not found, generating new key pair")
            return self.generate_key_pair()[1]
