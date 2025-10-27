"""
database logging for voice assistant.
"""
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """database handler for logging requests."""
    
    def __init__(self, db_path="voice_assistant_logs.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()
        logger.info(f"Database initialized: {db_path}")
    
    def _create_table(self):
        """Create the table if it doesn't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_time TEXT,
                text TEXT,
                intent TEXT,
                intent_source TEXT,
                action_executed INTEGER,
                action_success INTEGER,
                tts_text TEXT,
                total_time REAL,
                had_error INTEGER,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def log_request(self, data):
        """Save request data to database."""
        try:
            self.conn.execute("""
                INSERT INTO request_logs 
                (request_time, text, intent, intent_source, action_executed, 
                 action_success, tts_text, total_time, had_error, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('request_time'),
                data.get('text'),
                data.get('intent'),
                data.get('intent_source'),
                1 if data.get('action_executed') else 0,
                1 if data.get('action_success') else 0,
                data.get('tts_text'),
                data.get('total_time'),
                1 if data.get('had_error') else 0,
                data.get('error_message')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            return False
    
    def get_recent_logs(self, limit=50):
        """Get recent logs."""
        try:
            rows = self.conn.execute("""
                SELECT * FROM request_logs 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        self.conn.close()

