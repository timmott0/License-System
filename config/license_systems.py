from dataclasses import dataclass
from typing import Dict
from pathlib import Path

@dataclass
class LicenseSystem:
    name: str
    enabled: bool
    install_path: Path
    default_port: int
    description: str

# Define default license systems using the LicenseSystem dataclass
DEFAULT_SYSTEMS = {
    'flexlm': LicenseSystem(
        name='FlexLM',
        enabled=True,
        install_path=Path('vendor/flexlm'),
        default_port=27000,
        description='Flexible License Manager by Flexera'
    ),
    'hasp': LicenseSystem(
        name='Sentinel HASP',
        enabled=True,
        install_path=Path('vendor/hasp'),
        default_port=1947,
        description='Hardware-based licensing by Thales'
    ),
    'custom': LicenseSystem(
        name='Custom License Server',
        enabled=True,
        install_path=Path('vendor/custom'),
        default_port=8080,
        description='Custom implementation of license server'
    )
}
