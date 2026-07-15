"""
====================================================================
DATABASE MODULE - SQLite with Proper Error Handling
====================================================================
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom database exception"""
    pass


class Database:
    """
    Thread-safe SQLite database wrapper with proper error handling
    """
    
    def __init__(self, db_path: str = "data/whatsapp.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._local = threading.local()
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            try:
                conn = sqlite3.connect(
                    str(self.db_path),
                    timeout=30.0,
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                self._local.connection = conn
            except sqlite3.Error as e:
                logger.error(f"Database connection error: {e}")
                raise DatabaseError(f"Failed to connect to database: {e}")
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            cursor.close()
    
    def init_db(self):
        """Initialize database schema"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT UNIQUE NOT NULL,
                    response TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT,
                    is_ai_response INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total_messages INTEGER DEFAULT 0,
                    total_replies INTEGER DEFAULT 0,
                    total_ai_responses INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("INSERT OR IGNORE INTO stats (id) VALUES (1)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
            
        logger.info("Database initialized successfully")
    
    def add_keyword(self, keyword: str, response: str, category: str = "general") -> bool:
        """Add or update a keyword"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO keywords (keyword, response, category, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(keyword) 
                    DO UPDATE SET response = ?, category = ?, updated_at = CURRENT_TIMESTAMP
                """, (keyword.lower().strip(), response, category, response, category))
            return True
        except DatabaseError as e:
            logger.error(f"Failed to add keyword: {e}")
            return False
    
    def get_all_keywords(self) -> List[Dict[str, str]]:
        """Get all keywords"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT keyword, response, category FROM keywords")
                return [dict(row) for row in cursor.fetchall()]
        except DatabaseError as e:
            logger.error(f"Failed to get all keywords: {e}")
            return []
    
    def find_reply(self, message: str) -> Optional[str]:
        """Find matching keyword response"""
        keywords = self.get_all_keywords()
        message_lower = message.lower()
        
        for kw in keywords:
            if kw['keyword'].lower() in message_lower:
                return kw['response']
        return None
    
    def log_message(self, sender: str, message: str, response: Optional[str] = None, 
                    is_ai: bool = False):
        """Log a message and response"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (sender, message, response, is_ai_response)
                    VALUES (?, ?, ?, ?)
                """, (sender, message, response, 1 if is_ai else 0))
                
                cursor.execute("""
                    UPDATE stats SET 
                        total_messages = total_messages + 1,
                        total_replies = total_replies + 1,
                        total_ai_responses = total_ai_responses + ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = 1
                """, (1 if is_ai else 0,))
        except DatabaseError as e:
            logger.error(f"Failed to log message: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM stats WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return {}
        except DatabaseError as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def clear_all_data(self):
        """Clear all data (reset)"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM keywords")
                cursor.execute("DELETE FROM messages")
                cursor.execute("DELETE FROM conversations")
                cursor.execute("""
                    UPDATE stats SET 
                        total_messages = 0,
                        total_replies = 0,
                        total_ai_responses = 0,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE id = 1
                """)
            logger.info("All data cleared")
        except DatabaseError as e:
            logger.error(f"Failed to clear data: {e}")
            raise DatabaseError(f"Failed to clear data: {e}")
    
    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


_db_instance: Optional[Database] = None


def get_database(db_path: str = "data/whatsapp.db") -> Database:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
        _db_instance.init_db()
    return _db_instance
