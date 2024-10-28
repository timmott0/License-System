from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import logging
import json
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self, key_dir: Path, settings_path: Path = None):
        self.key_dir = key_dir
        self.private_key_path = key_dir / "private_key.pem"
        self.public_key_path = key_dir / "public_key.pem"
        
        # Load security settings
        self.settings_path = settings_path or (key_dir / "security_settings.json")
        self.load_security_settings()
        
    def load_security_settings(self):
        """Load security settings from config file"""
        try:
            with open(self.settings_path) as f:
                self.security_settings = json.load(f)
        except FileNotFoundError:
            logger.warning("Security settings not found, using defaults")
            from config.security_settings import DEFAULT_SECURITY_SETTINGS
            self.security_settings = DEFAULT_SECURITY_SETTINGS
            
    def generate_key_pair(self, key_length: int = None, password: str = None):
        """Generate new RSA key pair with configurable settings"""
        try:
            # Use provided key length or get from settings
            key_length = key_length or self.security_settings['key_settings']['key_length']
            
            # Validate key length
            if self.security_settings['validation']['enforce_key_length']:
                min_length = self.security_settings['validation']['minimum_key_length']
                if key_length < min_length:
                    raise ValueError(f"Key length must be at least {min_length} bits")
            
            # Check if password is required
            if self.security_settings['validation']['require_password'] and not password:
                raise ValueError("Password is required for key generation")
            
            private_key = rsa.generate_private_key(
                public_exponent=self.security_settings['key_settings']['public_exponent'],
                key_size=key_length,
                backend=default_backend()
            )
            
            public_key = private_key.public_key()
            
            # Determine encryption algorithm
            if self.security_settings['key_settings']['encryption_enabled'] and password:
                encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
            else:
                encryption_algorithm = serialization.NoEncryption()
            
            # Backup existing keys if backup is enabled
            if self.security_settings['key_settings']['backup_enabled']:
                self.backup_existing_keys()
            
            # Save private key
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
                
            logger.info(f"Generated new RSA key pair ({key_length} bits)")
            return private_key, public_key
            
        except Exception as e:
            logger.error(f"Failed to generate key pair: {str(e)}")
            raise
            
    def backup_existing_keys(self):
        """Backup existing keys if they exist"""
        backup_dir = Path(self.security_settings['key_settings']['backup_location'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for key_path in [self.private_key_path, self.public_key_path]:
            if key_path.exists():
                backup_path = backup_dir / f"{key_path.stem}_{timestamp}{key_path.suffix}"
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(key_path, backup_path)
                logger.info(f"Backed up {key_path} to {backup_path}")
                
    def save_key_metadata(self, key_length: int):
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
