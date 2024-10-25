from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class LicenseSystem:
    name: str
    enabled: bool
    install_path: Path
    default_port: int
    description: str

# Define default license systems
DEFAULT_SYSTEMS = {
    'flexlm': LicenseSystem(
        name='FlexLM',
        enabled=True,
        install_path=Path('C:/Program Files/FlexLM'),
        default_port=27000,
        description='FlexLM License Manager'
    ),
    'sentinel': LicenseSystem(
        name='Sentinel HASP',
        enabled=True,
        install_path=Path('C:/Program Files/SafeNet Sentinel'),
        default_port=1947,
        description='Sentinel HASP License Manager'
    )
}
