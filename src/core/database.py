"""
Database Module
SQLite database for storing messages, contacts, and statistics
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class Database:
    """SQLite database manager for WhatsApp automation"""
    
    def __init__(self, config=None):
        self.config = config or {}
        db_path = self.config.get('path', 'data/whatsapp.db')
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.init_database()
        
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                content TEXT NOT NULL,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_auto_reply BOOLEAN DEFAULT 1
            )
        ''')
        
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                phone TEXT,
                personality TEXT DEFAULT 'default',
                last_seen DATETIME,
                message_count INTEGER DEFAULT 0,
                is_whitelisted BOOLEAN DEFAULT 0,
                is_blacklisted BOOLEAN DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_name TEXT NOT NULL,
                messages TEXT,  -- JSON array of messages
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                messages_received INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                auto_replies INTEGER DEFAULT 0,
                unique_contacts INTEGER DEFAULT 0
            )
        ''')
        
        # Scheduled messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                scheduled_time TIME NOT NULL,
                contact_name TEXT,
                is_recurring BOOLEAN DEFAULT 0,
                recurrence_pattern TEXT,
                enabled BOOLEAN DEFAULT 1,
                last_sent DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL,
                response TEXT NOT NULL,
                personality TEXT DEFAULT 'default',
                priority INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_message(self, sender: str, content: str, response: str = None, is_auto_reply: bool = True):
        """Log a message and response"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (sender, content, response, is_auto_reply)
            VALUES (?, ?, ?, ?)
        ''', (sender, content, response, is_auto_reply))
        
        # Update contact stats
        cursor.execute('''
            INSERT OR IGNORE INTO contacts (name, message_count)
            VALUES (?, 0)
        ''', (sender,))
        
        cursor.execute('''
            UPDATE contacts 
            SET message_count = message_count + 1, last_seen = CURRENT_TIMESTAMP
            WHERE name = ?
        ''', (sender,))
        
        conn.commit()
        conn.close()
        
    def get_messages(self, limit: int = 100, contact: str = None) -> List[Dict]:
        """Get recent messages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if contact:
            cursor.execute('''
                SELECT id, sender, content, response, timestamp, is_auto_reply
                FROM messages
                WHERE sender = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (contact, limit))
        else:
            cursor.execute('''
                SELECT id, sender, content, response, timestamp, is_auto_reply
                FROM messages
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'sender': row[1],
                'content': row[2],
                'response': row[3],
                'timestamp': row[4],
                'is_auto_reply': row[5]
            }
            for row in rows
        ]
    
    def get_statistics(self) -> Dict:
        """Get bot statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total counts
        cursor.execute('SELECT COUNT(*) FROM messages')
        stats['total_messages'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages WHERE is_auto_reply = 1')
        stats['auto_replied'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT sender) FROM messages')
        stats['unique_contacts'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages WHERE response IS NOT NULL')
        stats['total_replies'] = cursor.fetchone()[0]
        
        # Today's counts
        today = datetime.now().date()
        cursor.execute('''
            SELECT COUNT(*) FROM messages 
            WHERE DATE(timestamp) = ?
        ''', (today,))
        stats['today_messages'] = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM messages 
            WHERE DATE(timestamp) = ? AND is_auto_reply = 1
        ''', (today,))
        stats['today_replies'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def add_contact(self, name: str, phone: str = None, personality: str = 'default'):
        """Add a new contact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO contacts (name, phone, personality)
            VALUES (?, ?, ?)
        ''', (name, phone, personality))
        
        conn.commit()
        conn.close()
        
    def get_contacts(self) -> List[Dict]:
        """Get all contacts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, phone, personality, last_seen, message_count
            FROM contacts
            ORDER BY last_seen DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'name': row[0],
                'phone': row[1],
                'personality': row[2],
                'last_seen': row[3],
                'message_count': row[4]
            }
            for row in rows
        ]
    
    def update_contact(self, name: str, **kwargs):
        """Update contact information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['personality', 'is_whitelisted', 'is_blacklisted', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if updates:
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [name]
            
            cursor.execute(f'''
                UPDATE contacts SET {set_clause} WHERE name = ?
            ''', values)
            
            conn.commit()
            
        conn.close()
        
    def add_scheduled_message(self, message: str, scheduled_time: str, 
                              contact_name: str = None, is_recurring: bool = False,
                              recurrence_pattern: str = None):
        """Add a scheduled message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_messages 
            (message, scheduled_time, contact_name, is_recurring, recurrence_pattern)
            VALUES (?, ?, ?, ?, ?)
        ''', (message, scheduled_time, contact_name, is_recurring, recurrence_pattern))
        
        conn.commit()
        conn.close()
        
    def get_due_messages(self) -> List[Dict]:
        """Get messages that are due to be sent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        current_time = datetime.now().strftime('%H:%M')
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT id, message, contact_name
            FROM scheduled_messages
            WHERE enabled = 1
            AND (last_sent IS NULL OR DATE(last_sent) < ?)
            AND scheduled_time = ?
        ''', (today, current_time))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {'id': row[0], 'message': row[1], 'contact_name': row[2]}
            for row in rows
        ]
    
    def mark_message_sent(self, message_id: int):
        """Mark a scheduled message as sent"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_messages
            SET last_sent = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (message_id,))
        
        conn.commit()
        conn.close()
        
    def save_conversation(self, contact_name: str, messages: List[Dict]):
        """Save conversation history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        messages_json = json.dumps(messages)
        
        cursor.execute('''
            INSERT OR REPLACE INTO conversations (contact_name, messages, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (contact_name, messages_json))
        
        conn.commit()
        conn.close()
        
    def get_conversation(self, contact_name: str) -> List[Dict]:
        """Get conversation history for a contact"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT messages FROM conversations WHERE contact_name = ?
        ''', (contact_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return []
