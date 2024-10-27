from pathlib import Path
from datetime import datetime
import os
import platform
from typing import Optional

class CustomerDirectoryManager:
    def __init__(self, base_path: str):
        """
        Initialize with base path for all customer directories
        base_path: Root directory for all customer folders
        """
        self.base_path = Path(base_path)
        
    def create_customer_structure(self, customer_name: str, customer_id: str) -> Path:
        """
        Creates the directory structure for a customer:
        base_path/
            CustomerName/
                CustomerID/
                    YYYY/
                        MM/
        Returns the path to the current month's directory
        """
        # Sanitize customer name and ID for file system
        safe_customer_name = self.sanitize_name(customer_name)
        safe_customer_id = self.sanitize_name(customer_id)
        
        # Create the date-based structure
        now = datetime.now()
        year = str(now.year)
        month = f"{now.month:02d}"
        
        # Build the full path
        customer_path = self.base_path / safe_customer_name / safe_customer_id / year / month
        
        # Create all directories if they don't exist
        customer_path.mkdir(parents=True, exist_ok=True)
        
        return customer_path
    
    def get_customer_path(self, customer_name: str, customer_id: str) -> Optional[Path]:
        """
        Get the path for an existing customer structure
        Returns None if the customer directory doesn't exist
        """
        safe_customer_name = self.sanitize_name(customer_name)
        safe_customer_id = self.sanitize_name(customer_id)
        
        customer_path = self.base_path / safe_customer_name / safe_customer_id
        
        return customer_path if customer_path.exists() else None
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """
        Sanitize name for file system use
        Removes or replaces invalid characters
        """
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove leading/trailing spaces and periods
        name = name.strip('. ')
        
        # Ensure name isn't empty after sanitization
        if not name:
            name = "unnamed"
            
        return name
    
    def get_all_customers(self):
        """
        Returns a list of all customer names in the base directory
        """
        if not self.base_path.exists():
            return []
        
        return [d.name for d in self.base_path.iterdir() if d.is_dir()]
    
    def get_customer_ids(self, customer_name: str):
        """
        Returns a list of all customer IDs for a given customer name
        """
        customer_path = self.base_path / self.sanitize_name(customer_name)
        if not customer_path.exists():
            return []
        
        return [d.name for d in customer_path.iterdir() if d.is_dir()]
