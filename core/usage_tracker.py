from pathlib import Path
import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class UsageTracker:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        """Initialize the usage tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS license_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_id TEXT,
                    customer_id TEXT,
                    product_id TEXT,
                    feature_id TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    host_info TEXT,
                    usage_data TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_id TEXT,
                    metric_type TEXT,
                    metric_value REAL,
                    timestamp TEXT
                )
            """)
            
    def record_usage(self, license_id: str, customer_id: str, product_id: str,
                    feature_id: str, host_info: Dict, usage_data: Dict):
        """Record license usage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO license_usage 
                (license_id, customer_id, product_id, feature_id, start_time, host_info, usage_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    license_id,
                    customer_id,
                    product_id,
                    feature_id,
                    datetime.now().isoformat(),
                    json.dumps(host_info),
                    json.dumps(usage_data)
                )
            )
            
    def end_usage_session(self, license_id: str, product_id: str, feature_id: str):
        """End a usage session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE license_usage 
                SET end_time = ? 
                WHERE license_id = ? AND product_id = ? AND feature_id = ? AND end_time IS NULL
                """,
                (datetime.now().isoformat(), license_id, product_id, feature_id)
            )
            
    def record_metric(self, license_id: str, metric_type: str, metric_value: float):
        """Record a usage metric"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO usage_metrics (license_id, metric_type, metric_value, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (license_id, metric_type, metric_value, datetime.now().isoformat())
            )
            
    def get_usage_report(self, license_id: str, start_date: datetime = None, 
                        end_date: datetime = None) -> Dict:
        """Generate usage report for a license"""
        with sqlite3.connect(self.db_path) as conn:
            # Get usage sessions
            query = "SELECT * FROM license_usage WHERE license_id = ?"
            params = [license_id]
            
            if start_date:
                query += " AND start_time >= ?"
                params.append(start_date.isoformat())
            if end_date:
                query += " AND start_time <= ?"
                params.append(end_date.isoformat())
                
            cursor = conn.execute(query, params)
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'product_id': row[3],
                    'feature_id': row[4],
                    'start_time': row[5],
                    'end_time': row[6],
                    'host_info': json.loads(row[7]),
                    'usage_data': json.loads(row[8])
                })
                
            # Get metrics
            cursor = conn.execute(
                "SELECT metric_type, AVG(metric_value) FROM usage_metrics "
                "WHERE license_id = ? GROUP BY metric_type",
                (license_id,)
            )
            metrics = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'license_id': license_id,
                'sessions': sessions,
                'metrics': metrics,
                'total_sessions': len(sessions),
                'report_generated': datetime.now().isoformat()
            }
