from typing import Dict, Any
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

CONFIG_SCHEMA = {
    "type": "object",
    "required": ["license_systems", "paths", "security"],
    "properties": {
        "license_systems": {
            "type": "object",
            "patternProperties": {
                "^[a-zA-Z0-9_]+$": {
                    "type": "object",
                    "required": ["name", "enabled", "system_type"],
                    "properties": {
                        "name": {"type": "string"},
                        "enabled": {"type": "boolean"},
                        "system_type": {
                            "type": "string",
                            "enum": ["file", "database", "network"]
                        },
                        "install_path": {"type": "string"},
                        "default_port": {"type": "integer"},
                        "description": {"type": "string"},
                        "database_config": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["mysql", "postgresql", "sqlite", "mssql"]
                                },
                                "host": {"type": "string"},
                                "port": {"type": "integer"},
                                "database": {"type": "string"},
                                "username": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "paths": {
            "type": "object",
            "required": ["config", "keys", "licenses"],
            "properties": {
                "config": {"type": "string"},
                "keys": {"type": "string"},
                "licenses": {"type": "string"}
            }
        },
        "security": {
            "type": "object",
            "required": ["key_settings", "validation"],
            "properties": {
                "key_settings": {
                    "type": "object",
                    "required": ["key_length", "key_format"],
                    "properties": {
                        "key_length": {
                            "type": "integer",
                            "enum": [2048, 3072, 4096]
                        },
                        "key_format": {
                            "type": "string",
                            "enum": ["PKCS8", "PKCS1"]
                        }
                    }
                }
            }
        }
    }
}

def validate_config_file(config_path: Path) -> Dict[str, Any]:
    """Validate and load configuration file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        ValidationError: If configuration is invalid
    """
    try:
        with open(config_path) as f:
            config = json.load(f)
            
        # Validate against schema
        from jsonschema import validate
        validate(instance=config, schema=CONFIG_SCHEMA)
        
        logger.info(f"Configuration validated successfully: {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise 