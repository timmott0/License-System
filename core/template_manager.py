from pathlib import Path
import json
import yaml
from typing import Dict, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LicenseTemplate:
    name: str
    description: str
    type: str
    validity_days: int
    maintenance_days: int
    platforms: List[str]
    features: List[Dict]
    metadata: Dict

class TemplateManager:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
    def create_template(self, template_data: Dict) -> LicenseTemplate:
        """Create a new license template"""
        template = LicenseTemplate(
            name=template_data['name'],
            description=template_data.get('description', ''),
            type=template_data['type'],
            validity_days=template_data.get('validity_days', 365),
            maintenance_days=template_data.get('maintenance_days', 90),
            platforms=template_data.get('platforms', []),
            features=template_data.get('features', []),
            metadata={
                'created_at': datetime.now().isoformat(),
                'version': '1.0',
                **template_data.get('metadata', {})
            }
        )
        
        # Save template
        template_path = self.template_dir / f"{template.name}.yaml"
        self.save_template(template, template_path)
        return template
    
    def save_template(self, template: LicenseTemplate, path: Path):
        """Save template to file"""
        template_data = {
            'name': template.name,
            'description': template.description,
            'type': template.type,
            'validity_days': template.validity_days,
            'maintenance_days': template.maintenance_days,
            'platforms': template.platforms,
            'features': template.features,
            'metadata': template.metadata
        }
        
        with open(path, 'w') as f:
            yaml.dump(template_data, f, default_flow_style=False)
            
    def load_template(self, name: str) -> LicenseTemplate:
        """Load a template by name"""
        template_path = self.template_dir / f"{name}.yaml"
        if not template_path.exists():
            raise ValueError(f"Template {name} not found")
            
        with open(template_path, 'r') as f:
            template_data = yaml.safe_load(f)
            
        return LicenseTemplate(**template_data)
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        return [p.stem for p in self.template_dir.glob("*.yaml")]
    
    def delete_template(self, name: str):
        """Delete a template"""
        template_path = self.template_dir / f"{name}.yaml"
        if template_path.exists():
            template_path.unlink()
