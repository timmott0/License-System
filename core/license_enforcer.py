from typing import Dict, List
from .feature import Feature, FeatureType
from core.product import Product
import logging

class LicenseEnforcer:
    def __init__(self):
        self.features: Dict[str, Feature] = {}
        self.products: Dict[str, Product] = {}
        self.active_licenses: List[Dict] = []
        
    def register_feature(self, feature: Feature):
        """Register a feature with the enforcer"""
        self.features[feature.name] = feature
        
    def register_product(self, product: Product):
        """Register a product with the enforcer"""
        self.products[product.name] = product
        
    def enforce_license(self, license_data: Dict):
        """Enforce a license based on its data"""
        try:
            # Store the license
            self.active_licenses.append(license_data)
            
            # Enable licensed features
            licensed_features = license_data.get('features', [])
            self._enforce_features(licensed_features)
            
            # Enable licensed products
            licensed_products = license_data.get('products', [])
            self._enforce_products(licensed_products)
            
            # Handle specific license type requirements
            self._enforce_license_type(license_data.get('type'))
            
            logging.info(f"License enforced successfully: {license_data.get('id', 'unknown')}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to enforce license: {str(e)}")
            return False
    
    def _enforce_features(self, licensed_features: List[str]):
        """Enable/disable features based on license"""
        for feature_name, feature in self.features.items():
            if feature_name in licensed_features:
                feature.enable()
            else:
                feature.disable()
    
    def _enforce_products(self, licensed_products: List[Dict]):
        """Enable/disable products based on license"""
        licensed_product_names = [p['name'] for p in licensed_products]
        for product_name, product in self.products.items():
            if product_name in licensed_product_names:
                product.enable()
            else:
                product.disable()
    
    def _enforce_license_type(self, license_type: str):
        """Handle specific license type requirements"""
        if license_type == "floating":
            self._handle_floating_license()
        elif license_type == "single_user":
            self._handle_single_user_license()
    
    def _handle_floating_license(self):
        """Handle floating license checkout"""
        # Implement floating license logic here
        pass
    
    def _handle_single_user_license(self):
        """Handle single user license restrictions"""
        # Implement single user license logic here
        pass 