from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import logging
import json
from datetime import datetime
import shutil
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self, key_dir: Path, settings_path: Path = None):
        """Initialize KeyManager with paths and settings
        
        Args:
            key_dir: Directory for key storage
            settings_path: Path to security settings file
        """
        self.key_dir = Path(key_dir)
        self.private_key_path = self.key_dir / "private_key.pem"
        self.public_key_path = self.key_dir / "public_key.pem"
        
        # Load security settings
        self.settings_path = settings_path or (self.key_dir / "security_settings.json")
        self.load_security_settings()
        
    def load_security_settings(self):
        """Load security settings from config file"""
        try:
            with open(self.settings_path) as f:
                self.security_settings = json.load(f)
                logger.info("Loaded security settings from %s", self.settings_path)
        except FileNotFoundError:
            logger.warning("Security settings not found at %s, using defaults", 
                         self.settings_path)
            from config.security_settings import DEFAULT_SECURITY_SETTINGS
            self.security_settings = DEFAULT_SECURITY_SETTINGS
            
    def validate_key_requirements(self, key_length: int, password: Optional[str]) -> None:
        """Validate key generation requirements
        
        Args:
            key_length: Length of key in bits
            password: Optional password for key encryption
            
        Raises:
            ValueError: If requirements are not met
        """
        if self.security_settings['validation']['enforce_key_length']:
            min_length = self.security_settings['validation']['minimum_key_length']
            if key_length < min_length:
                raise ValueError(f"Key length must be at least {min_length} bits")
        
        if self.security_settings['validation']['require_password'] and not password:
            raise ValueError("Password is required for key generation")
            
    def generate_key_pair(self, key_length: Optional[int] = None, 
                         password: Optional[str] = None) -> Tuple[rsa.RSAPrivateKey, 
                                                                rsa.RSAPublicKey]:
        """Generate new RSA key pair with configurable settings
        
        Args:
            key_length: Optional key length in bits
            password: Optional password for key encryption
            
        Returns:
            Tuple of (private_key, public_key)
            
        Raises:
            ValueError: If key requirements are not met
            Exception: If key generation fails
        """
        try:
            # Use provided key length or get from settings
            key_length = key_length or self.security_settings['key_settings']['key_length']
            
            # Validate requirements
            self.validate_key_requirements(key_length, password)
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=self.security_settings['key_settings']['public_exponent'],
                key_size=key_length,
                backend=default_backend()
            )
            
            public_key = private_key.public_key()
            
            # Determine encryption algorithm
            if self.security_settings['key_settings']['encryption_enabled'] and password:
                encryption_algorithm = serialization.BestAvailableEncryption(
                    password.encode())
            else:
                encryption_algorithm = serialization.NoEncryption()
            
            # Backup existing keys if enabled
            if self.security_settings['key_settings']['backup_enabled']:
                self.backup_existing_keys()
            
            # Save private key
            self.key_dir.mkdir(parents=True, exist_ok=True)
            with open(self.private_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=getattr(serialization.PrivateFormat, 
                                 self.security_settings['key_settings']['key_format']),
                    encryption_algorithm=encryption_algorithm
                ))
            
            # Save public key
            with open(self.public_key_path, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            
            # Record key generation metadata
            self.save_key_metadata(key_length)
                
            logger.info("Generated new RSA key pair (%d bits)", key_length)
            return private_key, public_key
            
        except Exception as e:
            logger.error("Failed to generate key pair: %s", str(e))
            raise
            
    def backup_existing_keys(self) -> None:
        """Backup existing keys if they exist"""
        backup_dir = Path(self.security_settings['key_settings']['backup_location'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for key_path in [self.private_key_path, self.public_key_path]:
            if key_path.exists():
                backup_path = backup_dir / f"{key_path.stem}_{timestamp}{key_path.suffix}"
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(key_path, backup_path)
                logger.info("Backed up %s to %s", key_path, backup_path)
                
    def save_key_metadata(self, key_length: int) -> None:
        """Save metadata about generated keys"""
        metadata = {
            'generated_date': datetime.now().isoformat(),
            'key_length': key_length,
            'format': self.security_settings['key_settings']['key_format'],
            'encryption_enabled': self.security_settings['key_settings']['encryption_enabled'],
            'next_rotation_date': (
                datetime.now().timestamp() + 
                (self.security_settings['key_settings']['rotation_period_days'] * 86400)
            )
        }
        
        metadata_path = self.key_dir / 'key_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
            logger.info("Saved key metadata to %s", metadata_path)
            
    def load_private_key(self, password: Optional[str] = None) -> rsa.RSAPrivateKey:
        """Load private key from file
        
        Args:
            password: Optional password for encrypted keys
            
        Returns:
            RSAPrivateKey object
            
        Raises:
            FileNotFoundError: If key file doesn't exist
            ValueError: If password is required but not provided
        """
        if not self.private_key_path.exists():
            raise FileNotFoundError(f"Private key not found at {self.private_key_path}")
            
        try:
            with open(self.private_key_path, 'rb') as f:
                key_data = f.read()
                return serialization.load_pem_private_key(
                    key_data,
                    password=password.encode() if password else None,
                    backend=default_backend()
                )
        except Exception as e:
            logger.error("Failed to load private key: %s", str(e))
            raise
            
    def load_public_key(self) -> rsa.RSAPublicKey:
        """Load public key from file
        
        Returns:
            RSAPublicKey object
            
        Raises:
            FileNotFoundError: If key file doesn't exist
        """
        if not self.public_key_path.exists():
            raise FileNotFoundError(f"Public key not found at {self.public_key_path}")
            
        try:
            with open(self.public_key_path, 'rb') as f:
                key_data = f.read()
                return serialization.load_pem_public_key(
                    key_data,
                    backend=default_backend()
                )
        except Exception as e:
            logger.error("Failed to load public key: %s", str(e))
            raise
