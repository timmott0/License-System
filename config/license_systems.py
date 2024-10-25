from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class LicenseSystemConfig:
    name: str
    enabled: bool
    install_path: Path
    default_port: int
    required_tools: List[str]
    description: str
    config_options: Dict

DEFAULT_SYSTEMS = {
    "flexlm": LicenseSystemConfig(
        name="FlexLM",
        enabled=True,
        install_path=Path("/opt/flexlm/licenses"),
        default_port=27000,
        required_tools=["lmgrd", "lmutil"],
        description="Flexible License Manager by Flexera",
        config_options={
            "vendor_daemon": "",
            "service_name": "flexlm",
            "log_path": "/var/log/flexlm"
        }
    ),
    "hasp": LicenseSystemConfig(
        name="Sentinel HASP",
        enabled=False,
        install_path=Path("/opt/hasp"),
        default_port=1947,
        required_tools=["hasplm", "haspconfig"],
        description="Thales Sentinel HASP License System",
        config_options={
            "vendor_code": "",
            "config_path": "/etc/hasplm"
        }
    ),
    # Add more license systems as needed
}
