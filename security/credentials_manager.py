from cryptography.fernet import Fernet
import keyring
import json
import os
from pathlib import Path
from typing import Optional, Dict, List

class CredentialsManager:
    def __init__(self, app_name: str = "LicenseManager"):
        self.app_name = app_name
        self.keyring_service = f"{app_name}_credentials"
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption key"""
        try:
            # Try to retrieve existing key from keyring
            key = keyring.get_password(self.keyring_service, "encryption_key")
            if not key:
                # Generate new key if none exists
                key = Fernet.generate_key()
                keyring.set_password(self.keyring_service, "encryption_key", key.decode())
            self.cipher_suite = Fernet(key if isinstance(key, bytes) else key.encode())
        except Exception as e:
            raise RuntimeError(f"Failed to initialize encryption: {str(e)}")

    def save_credentials(self, server_path: str, username: str, password: str) -> bool:
        """
        Save encrypted credentials for a server path
        
        Args:
            server_path: Path to the server
            username: Username for server access
            password: Password for server access
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Encrypt credentials
            encrypted_data = self.cipher_suite.encrypt(
                json.dumps({
                    "username": username,
                    "password": password
                }).encode()
            )
            
            # Store in keyring
            keyring.set_password(
                self.keyring_service,
                server_path,
                encrypted_data.decode()
            )
            return True
        except Exception as e:
            print(f"Failed to save credentials: {str(e)}")
            return False

    def get_credentials(self, server_path: str) -> Optional[Dict[str, str]]:
        """
        Retrieve credentials for a server path
        
        Args:
            server_path: Path to the server
            
        Returns:
            Dict containing username and password if found, None otherwise
        """
        try:
            encrypted_data = keyring.get_password(self.keyring_service, server_path)
            if encrypted_data:
                decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
                return json.loads(decrypted_data)
            return None
        except Exception as e:
            print(f"Failed to retrieve credentials: {str(e)}")
            return None

    def delete_credentials(self, server_path: str) -> bool:
        """
        Delete stored credentials for a server path
        
        Args:
            server_path: Path to the server
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            keyring.delete_password(self.keyring_service, server_path)
            return True
        except Exception as e:
            print(f"Failed to delete credentials: {str(e)}")
            return False

    def get_stored_paths(self) -> List[str]:
        """
        Get a list of all server paths with stored credentials
        
        Returns:
            List[str]: List of server paths
        """
        try:
            # Get all entries for our service
            import keyring.backends
            backend = keyring.get_keyring()
            
            # This is a bit of a hack since keyring doesn't provide a standard way to list all entries
            if hasattr(backend, 'get_all_credentials'):
                credentials = backend.get_all_credentials()
                return [c.username for c in credentials if c.service == self.keyring_service]
            
            # Fallback to storing paths in a separate keyring entry
            paths = keyring.get_password(self.keyring_service, "stored_paths")
            if paths:
                return json.loads(paths)
            return []
        except Exception as e:
            print(f"Failed to get stored paths: {str(e)}")
            return []
