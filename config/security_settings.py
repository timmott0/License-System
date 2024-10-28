from dataclasses import dataclass, asdict
from typing import Literal, Optional, Dict, Any

@dataclass
class KeySettings:
    key_length: Literal[2048, 3072, 4096] = 2048
    public_exponent: int = 65537
    key_format: Literal['PKCS8', 'PKCS1'] = 'PKCS8'
    encryption_enabled: bool = False
    encryption_algorithm: Optional[str] = None
    key_password: Optional[str] = None
    backup_enabled: bool = True
    backup_location: str = 'config/keys/backup'
    rotation_period_days: int = 365

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary format"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeySettings':
        """Create settings from dictionary format"""
        return cls(**data)

DEFAULT_SECURITY_SETTINGS = {
    'key_settings': KeySettings().to_dict(),
    'validation': {
        'enforce_key_length': True,
        'minimum_key_length': 2048,
        'require_password': False
    }
}

def validate_settings(settings: Dict[str, Any]) -> bool:
    """Validate security settings structure and values"""
    try:
        # Validate key settings
        key_settings = KeySettings.from_dict(settings['key_settings'])
        
        # Validate validation settings
        validation = settings['validation']
        assert isinstance(validation['enforce_key_length'], bool)
        assert isinstance(validation['minimum_key_length'], int)
        assert isinstance(validation['require_password'], bool)
        
        # Additional validation rules
        if validation['enforce_key_length']:
            assert key_settings.key_length >= validation['minimum_key_length']
        
        if validation['require_password']:
            assert key_settings.encryption_enabled
            assert key_settings.key_password is not None
            
        return True
        
    except (KeyError, AssertionError, TypeError):
        return False 