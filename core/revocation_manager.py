# Standard library imports
from pathlib import Path
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

class RevocationManager:
    """Manages the revocation of software licenses and maintains a revocation database"""
    
    def __init__(self, db_path: Path):
        """
        Initialize the revocation manager
        Args:
            db_path: Path to the SQLite or repository database file (should be in the license_server_data folder)
        """
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """Initialize the revocation database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Create table for storing individual revoked licenses
            conn.execute("""
                CREATE TABLE IF NOT EXISTS revoked_licenses (
                    license_id TEXT PRIMARY KEY,      -- Unique identifier for the license
                    customer_id TEXT,                 -- Customer identifier
                    revocation_date TEXT,             -- When the license was revoked
                    reason TEXT,                      -- Reason for revocation
                    metadata TEXT                     -- Additional JSON metadata
                )
            """)
            
            # Create table for storing published revocation lists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS revocation_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing list ID
                    publication_date TEXT,                 -- When the list was published
                    revoked_licenses TEXT                  -- JSON array of revoked license IDs
                )
            """)
            
    def revoke_license(self, license_id: str, customer_id: str, reason: str, metadata: Dict = None):
        """
        Revoke a specific license
        
        Args:
            license_id: Unique identifier of the license to revoke
            customer_id: Identifier of the customer who owns the license
            reason: Reason for revocation
            metadata: Optional additional information about the revocation
        """
        with sqlite3.connect(self.db_path) as conn:
            # Insert revocation record with current timestamp
            conn.execute(
                "INSERT INTO revoked_licenses (license_id, customer_id, revocation_date, reason, metadata) "
                "VALUES (?, ?, ?, ?, ?)",
                (license_id, customer_id, datetime.now().isoformat(), reason, json.dumps(metadata or {}))
            )
            
    def is_revoked(self, license_id: str) -> bool:
        """
        Check if a specific license has been revoked
        
        Args:
            license_id: License identifier to check
            
        Returns:
            bool: True if license is revoked, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM revoked_licenses WHERE license_id = ?",
                (license_id,)
            )
            return cursor.fetchone() is not None
            
    def get_revocation_info(self, license_id: str) -> Optional[Dict]:
        """
        Get detailed information about a revoked license
        
        Args:
            license_id: License identifier to look up
            
        Returns:
            Dict containing revocation details if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM revoked_licenses WHERE license_id = ?",
                (license_id,)
            )
            row = cursor.fetchone()
            if row:
                # Convert database row to dictionary with parsed metadata
                return {
                    'license_id': row[0],
                    'customer_id': row[1],
                    'revocation_date': row[2],
                    'reason': row[3],
                    'metadata': json.loads(row[4])
                }
        return None
        
    def publish_revocation_list(self) -> str:
        """
        Create and publish a new revocation list
        
        Returns:
            str: JSON string containing the published revocation list
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get all currently revoked license IDs
            cursor = conn.execute("SELECT license_id FROM revoked_licenses")
            revoked_licenses = [row[0] for row in cursor.fetchall()]
            
            # Create the revocation list with current timestamp
            publication_date = datetime.now().isoformat()
            revocation_list = {
                'publication_date': publication_date,
                'revoked_licenses': revoked_licenses
            }
            
            # Store the published list in the database
            conn.execute(
                "INSERT INTO revocation_list (publication_date, revoked_licenses) VALUES (?, ?)",
                (publication_date, json.dumps(revoked_licenses))
            )
            
            return json.dumps(revocation_list)
