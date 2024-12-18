# Standard library imports for data structures and typing
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class ProductFeature:
    """Represents a feature or capability of a software product"""
    name: str        # Name of the feature
    value: str       # Value or configuration of the feature
    quantity: int = 1    # Number of instances/licenses for this feature
    enabled: bool = True # Whether the feature is currently enabled

    def enable(self):
        """Enable the feature"""
        self.enabled = True

    def disable(self):
        """Disable the feature"""
        self.enabled = False

@dataclass
class Product:
    """
    Represents a software product with its features and licensing information
    """
    name: str        # Name of the product
    version: str     # Version string of the product
    features: List[ProductFeature]  # List of features included in this product
    quantity: int = 1    # Number of product licenses
    expiration_date: Optional[datetime] = None     # When the product license expires
    maintenance_date: Optional[datetime] = None    # When maintenance support ends
    enabled: bool = False  # Whether the product is currently enabled

    def enable(self):
        """Enable the product and its features"""
        self.enabled = True
        for feature in self.features:
            feature.enable()

    def disable(self):
        """Disable the product and its features"""
        self.enabled = False
        for feature in self.features:
            feature.disable()

    def to_dict(self) -> Dict:
        """
        Convert product to dictionary format for serialization
        
        Returns:
            Dict containing all product information in a serializable format
        """
        return {
            "name": self.name,
            "version": self.version,
            "quantity": self.quantity,
            "features": [
                {
                    "name": f.name,
                    "value": f.value,
                    "quantity": f.quantity,
                    "enabled": f.enabled
                }
                for f in self.features
            ],
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "maintenance_date": self.maintenance_date.isoformat() if self.maintenance_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Product':
        """
        Create product instance from dictionary format
        
        Args:
            data: Dictionary containing product information
            
        Returns:
            New Product instance with data from dictionary
        """
        features = [
            ProductFeature(**f) for f in data.get("features", [])
        ]
        
        return cls(
            name=data["name"],
            version=data["version"],
            features=features,
            quantity=data.get("quantity", 1),
            expiration_date=datetime.fromisoformat(data["expiration_date"]) if data.get("expiration_date") else None,
            maintenance_date=datetime.fromisoformat(data["maintenance_date"]) if data.get("maintenance_date") else None
        )
