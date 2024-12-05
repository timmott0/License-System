from enum import Enum
from typing import List, Dict
from PyQt5.QtWidgets import QWidget

class FeatureType(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    ADMIN = "admin"
    EXPORT = "export"
    IMPORT = "import"
    REPORTING = "reporting"
    API_ACCESS = "api_access"
    REMOTE_ACCESS = "remote_access"
    CUSTOMIZATION = "customization"

class Feature:
    def __init__(self, name: str, feature_type: FeatureType, widgets: List[QWidget] = None):
        self.name = name
        self.type = feature_type
        self.widgets = widgets or []
        self.enabled = False
    
    def enable(self):
        """Enable the feature and its associated widgets"""
        self.enabled = True
        for widget in self.widgets:
            widget.setEnabled(True)
    
    def disable(self):
        """Disable the feature and its associated widgets"""
        self.enabled = False
        for widget in self.widgets:
            widget.setEnabled(False)
    
    def add_widget(self, widget: QWidget):
        """Add a widget to be controlled by this feature"""
        self.widgets.append(widget)
        widget.setEnabled(self.enabled) 