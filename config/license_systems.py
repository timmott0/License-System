from dataclasses import dataclass
from typing import Dict, Optional, Literal
from pathlib import Path

@dataclass
class DatabaseConfig:
    type: Literal['mysql', 'postgresql', 'sqlite', 'mssql']
    host: str = ''
    port: int = 0
    database: str = ''
    username: str = ''
    connection_string: str = ''

@dataclass
class LicenseSystem:
    name: str
    enabled: bool
    system_type: Literal['file', 'database', 'network']
    install_path: Optional[Path] = None
    default_port: Optional[int] = None
    description: str = ''
    database_config: Optional[DatabaseConfig] = None

# Define default license systems
DEFAULT_SYSTEMS = {
    'flexlm': LicenseSystem(
        name='FlexLM',
        enabled=True,
        system_type='network',
        install_path=Path('vendor/flexlm'),
        default_port=27000,
        description='Flexible License Manager by Flexera'
    ),
    'mysql_licenses': LicenseSystem(
        name='MySQL License Database',
        enabled=True,
        system_type='database',
        description='MySQL-based license management',
        database_config=DatabaseConfig(
            type='mysql',
            host='localhost',
            port=3306,
            database='licenses'
        )
    ),
    'hasp': LicenseSystem(
        name='Sentinel HASP',
        enabled=True,
        system_type='network',
        install_path=Path('vendor/hasp'),
        default_port=1947,
        description='Hardware-based licensing by Thales'
    ),
    'custom': LicenseSystem(
        name='Custom License Server',
        enabled=True,
        system_type='network',
        install_path=Path('vendor/custom'),
        default_port=8080,
        description='Custom implementation of license server'
    )
}
