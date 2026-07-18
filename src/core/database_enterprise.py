"""
====================================================================
ENTERPRISE DATABASE - Multi-Tenant, Scalable Schema
====================================================================
Features:
- Multi-tenant support (organization_id)
- Message status tracking (delivered, read, failed)
- Campaign management
- Flow builder storage
- Team inbox
- Analytics tables
====================================================================
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import threading
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EnterpriseDatabase:
    """
    Enterprise-grade SQLite database with multi-tenant support
    """
    
    def __init__(self, db_path: str = "data/enterprise.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._local = threading.local()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            conn = sqlite3.connect(str(self.db_path), timeout=60.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
            self._local.connection = conn
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
            raise
        finally:
            cursor.close()
    
    def init_db(self):
        """Initialize complete database schema"""
        with self.get_cursor() as cursor:
            
            # =====================================
            # ORGANIZATIONS (Multi-tenant)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    api_key TEXT UNIQUE,
                    plan TEXT DEFAULT 'free',
                    whatsapp_phone_id TEXT,
                    whatsapp_token TEXT,
                    whatsapp_business_id TEXT,
                    settings TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # =====================================
            # CONTACTS
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    phone TEXT NOT NULL,
                    name TEXT,
                    email TEXT,
                    tags TEXT DEFAULT '[]',
                    attributes TEXT DEFAULT '{}',
                    opted_in INTEGER DEFAULT 0,
                    last_seen DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id),
                    UNIQUE(organization_id, phone)
                )
            """)
            
            # =====================================
            # MESSAGES (With full status tracking)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    message_id TEXT UNIQUE,
                    direction TEXT NOT NULL,
                    to_phone TEXT,
                    from_phone TEXT,
                    content TEXT,
                    message_type TEXT DEFAULT 'text',
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    media_url TEXT,
                    template_id TEXT,
                    idempotency_key TEXT UNIQUE,
                    sent_at DATETIME,
                    delivered_at DATETIME,
                    read_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """)
            
            # =====================================
            # CONVERSATIONS (For team inbox)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    contact_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'open',
                    priority INTEGER DEFAULT 5,
                    assigned_agent_id INTEGER,
                    source TEXT DEFAULT 'whatsapp',
                    tags TEXT DEFAULT '[]',
                    unread_count INTEGER DEFAULT 0,
                    last_message_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id),
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                )
            """)
            
            # =====================================
            # AGENTS (Team members)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    role TEXT DEFAULT 'agent',
                    status TEXT DEFAULT 'offline',
                    max_conversations INTEGER DEFAULT 50,
                    current_conversations INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """)
            
            # =====================================
            # CAMPAIGNS
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    flow_id INTEGER,
                    status TEXT DEFAULT 'draft',
                    segment_criteria TEXT DEFAULT '{}',
                    scheduled_at DATETIME,
                    started_at DATETIME,
                    completed_at DATETIME,
                    stats TEXT DEFAULT '{"total":0,"sent":0,"delivered":0,"read":0,"replied":0,"failed":0}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """)
            
            # =====================================
            # FLOWS (Flow Builder)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    definition TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'draft',
                    trigger_type TEXT DEFAULT 'keyword',
                    trigger_value TEXT,
                    is_active INTEGER DEFAULT 0,
                    version INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """)
            
            # =====================================
            # TEMPLATES (Message templates)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT 'marketing',
                    content TEXT NOT NULL,
                    variables TEXT DEFAULT '[]',
                    meta_template_id TEXT,
                    status TEXT DEFAULT 'pending',
                    approved INTEGER DEFAULT 0,
                    rejection_reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """)
            
            # =====================================
            # KEYWORDS (Auto-reply triggers)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    keyword TEXT NOT NULL,
                    response TEXT NOT NULL,
                    flow_id INTEGER,
                    category TEXT DEFAULT 'general',
                    is_active INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id),
                    UNIQUE(organization_id, keyword)
                )
            """)
            
            # =====================================
            # ANALYTICS (Aggregated metrics)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    metric_type TEXT NOT NULL,
                    value INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id),
                    UNIQUE(organization_id, date, metric_type)
                )
            """)
            
            # =====================================
            # AUDIT LOG (Action tracking)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    actor_type TEXT,
                    actor_id INTEGER,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id INTEGER,
                    details TEXT DEFAULT '{}',
                    ip_address TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """)
            
            # =====================================
            # WEBHOOKS (Integration)
            # =====================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    events TEXT DEFAULT '[]',
                    secret TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            """)
            
            # =====================================
            # INDEXES (Performance optimization)
            # =====================================
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_org ON contacts(organization_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_org ON messages(organization_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_org ON conversations(organization_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_org ON campaigns(organization_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_org_date ON analytics(organization_id, date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords_org ON keywords(organization_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_org ON templates(organization_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_org ON agents(organization_id)")
            
            logger.info("Enterprise database initialized successfully")
    
    # =====================================
    # ORGANIZATION METHODS
    # =====================================
    
    def create_organization(self, name: str, email: str, phone: str = None) -> int:
        """Create new organization"""
        import secrets
        api_key = secrets.token_urlsafe(32)
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO organizations (name, email, phone, api_key)
                VALUES (?, ?, ?, ?)
            """, (name, email, phone, api_key))
            return cursor.lastrowid
    
    def get_organization(self, org_id: int = None, api_key: str = None) -> Optional[Dict]:
        """Get organization by ID or API key"""
        with self.get_cursor() as cursor:
            if org_id:
                cursor.execute("SELECT * FROM organizations WHERE id = ?", (org_id,))
            elif api_key:
                cursor.execute("SELECT * FROM organizations WHERE api_key = ?", (api_key,))
            else:
                return None
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_whatsapp_config(self, org_id: int, phone_id: str, token: str, business_id: str):
        """Update WhatsApp Business API configuration"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE organizations 
                SET whatsapp_phone_id = ?, whatsapp_token = ?, whatsapp_business_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (phone_id, token, business_id, org_id))
    
    # =====================================
    # CONTACT METHODS
    # =====================================
    
    def add_contact(self, org_id: int, phone: str, name: str = None, email: str = None) -> int:
        """Add or update contact"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO contacts (organization_id, phone, name, email)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(organization_id, phone) 
                DO UPDATE SET name = COALESCE(?, name), email = COALESCE(?, email),
                              updated_at = CURRENT_TIMESTAMP
            """, (org_id, phone, name, email, name, email))
            return cursor.lastrowid
    
    def get_contacts(self, org_id: int, tags: List[str] = None, limit: int = 1000) -> List[Dict]:
        """Get contacts with optional tag filtering"""
        with self.get_cursor() as cursor:
            query = "SELECT * FROM contacts WHERE organization_id = ?"
            params = [org_id]
            
            if tags:
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f'%"{tag}"%')
            
            query += " ORDER BY last_seen DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_contact_count(self, org_id: int, segment_criteria: Dict = None) -> int:
        """Count contacts matching segment criteria"""
        with self.get_cursor() as cursor:
            query = "SELECT COUNT(*) FROM contacts WHERE organization_id = ?"
            params = [org_id]
            
            if segment_criteria:
                if segment_criteria.get('opted_in'):
                    query += " AND opted_in = 1"
                if segment_criteria.get('tags'):
                    for tag in segment_criteria['tags']:
                        query += " AND tags LIKE ?"
                        params.append(f'%"{tag}"%')
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    # =====================================
    # MESSAGE METHODS
    # =====================================
    
    def create_message(self, org_id: int, direction: str, content: str,
                       to_phone: str = None, from_phone: str = None,
                       message_type: str = 'text', template_id: int = None,
                       idempotency_key: str = None) -> int:
        """Create new message record"""
        import secrets
        msg_id = secrets.token_urlsafe(16)
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO messages 
                (organization_id, message_id, direction, to_phone, from_phone, 
                 content, message_type, template_id, idempotency_key, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (org_id, msg_id, direction, to_phone, from_phone, 
                  content, message_type, template_id, idempotency_key))
            return cursor.lastrowid
    
    def update_message_status(self, message_id: str, status: str, 
                            error_message: str = None) -> bool:
        """Update message delivery status"""
        with self.get_cursor() as cursor:
            update_fields = ["status = ?"]
            params = [status]
            
            if status == 'delivered':
                update_fields.append("delivered_at = CURRENT_TIMESTAMP")
            elif status == 'read':
                update_fields.append("read_at = CURRENT_TIMESTAMP")
            elif status == 'failed' and error_message:
                update_fields.append("error_message = ?")
                params.append(error_message)
            
            query = f"UPDATE messages SET {', '.join(update_fields)} WHERE message_id = ?"
            params.append(message_id)
            
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def get_messages(self, org_id: int, status: str = None, 
                     start_date: datetime = None, end_date: datetime = None,
                     limit: int = 100) -> List[Dict]:
        """Get messages with filters"""
        with self.get_cursor() as cursor:
            query = "SELECT * FROM messages WHERE organization_id = ?"
            params = [org_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if start_date:
                query += " AND sent_at >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND sent_at <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # =====================================
    # CAMPAIGN METHODS
    # =====================================
    
    def create_campaign(self, org_id: int, name: str, flow_id: int = None,
                       segment_criteria: Dict = None, scheduled_at: datetime = None) -> int:
        """Create new campaign"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO campaigns 
                (organization_id, name, flow_id, segment_criteria, scheduled_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (org_id, name, flow_id, json.dumps(segment_criteria or {}),
                  scheduled_at.isoformat() if scheduled_at else None, 'draft'))
            return cursor.lastrowid
    
    def update_campaign_stats(self, campaign_id: int, stats: Dict):
        """Update campaign statistics"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE campaigns SET stats = ? WHERE id = ?
            """, (json.dumps(stats), campaign_id))
    
    def get_campaign_stats(self, org_id: int, start_date: datetime = None,
                          end_date: datetime = None) -> Dict:
        """Get aggregated campaign statistics"""
        with self.get_cursor() as cursor:
            query = """
                SELECT 
                    COUNT(*) as total_campaigns,
                    SUM(json_extract(stats, '$.sent')) as total_sent,
                    SUM(json_extract(stats, '$.delivered')) as total_delivered,
                    SUM(json_extract(stats, '$.read')) as total_read,
                    SUM(json_extract(stats, '$.replied')) as total_replied
                FROM campaigns 
                WHERE organization_id = ? AND status = 'completed'
            """
            params = [org_id]
            
            if start_date:
                query += " AND completed_at >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND completed_at <= ?"
                params.append(end_date.isoformat())
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            return {
                'total_campaigns': row[0] or 0,
                'total_sent': row[1] or 0,
                'total_delivered': row[2] or 0,
                'total_read': row[3] or 0,
                'total_replied': row[4] or 0,
                'delivery_rate': round((row[2] or 0) / (row[1] or 1) * 100, 1),
                'read_rate': round((row[3] or 0) / (row[2] or 1) * 100, 1),
                'response_rate': round((row[4] or 0) / (row[2] or 1) * 100, 1)
            }
    
    # =====================================
    # FLOW METHODS
    # =====================================
    
    def create_flow(self, org_id: int, name: str, definition: Dict,
                   trigger_type: str = 'keyword', trigger_value: str = None) -> int:
        """Create new flow"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO flows 
                (organization_id, name, definition, trigger_type, trigger_value)
                VALUES (?, ?, ?, ?, ?)
            """, (org_id, name, json.dumps(definition), trigger_type, trigger_value))
            return cursor.lastrowid
    
    def get_flow(self, flow_id: int) -> Optional[Dict]:
        """Get flow by ID"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM flows WHERE id = ?", (flow_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['definition'] = json.loads(result['definition'])
                return result
            return None
    
    def activate_flow(self, flow_id: int):
        """Activate a flow"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE flows SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (flow_id,))
    
    # =====================================
    # TEMPLATE METHODS
    # =====================================
    
    def create_template(self, org_id: int, name: str, content: str,
                       category: str = 'marketing', variables: List[str] = None) -> int:
        """Create message template"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO templates 
                (organization_id, name, content, category, variables)
                VALUES (?, ?, ?, ?, ?)
            """, (org_id, name, content, category, json.dumps(variables or [])))
            return cursor.lastrowid
    
    def get_templates(self, org_id: int, status: str = None) -> List[Dict]:
        """Get templates"""
        with self.get_cursor() as cursor:
            query = "SELECT * FROM templates WHERE organization_id = ?"
            params = [org_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            cursor.execute(query + " ORDER BY created_at DESC", params)
            return [dict(row) for row in cursor.fetchall()]
    
    # =====================================
    # ANALYTICS METHODS
    # =====================================
    
    def track_event(self, org_id: int, metric_type: str, value: int = 1,
                   metadata: Dict = None):
        """Track analytics event"""
        today = datetime.now().date().isoformat()
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO analytics (organization_id, date, metric_type, value, metadata)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(organization_id, date, metric_type)
                DO UPDATE SET value = value + ?, metadata = ?
            """, (org_id, today, metric_type, value, 
                  json.dumps(metadata or {}), value, json.dumps(metadata or {})))
    
    def get_analytics(self, org_id: int, days: int = 30) -> Dict:
        """Get analytics summary"""
        start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT metric_type, SUM(value) as total
                FROM analytics
                WHERE organization_id = ? AND date >= ?
                GROUP BY metric_type
            """, (org_id, start_date))
            
            results = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Calculate rates
            messages_sent = results.get('messages_sent', 0)
            messages_delivered = results.get('messages_delivered', 0)
            messages_read = results.get('messages_read', 0)
            
            return {
                'period_days': days,
                'messages_sent': messages_sent,
                'messages_delivered': messages_delivered,
                'messages_read': messages_read,
                'delivery_rate': round(messages_delivered / messages_sent * 100, 1) if messages_sent else 0,
                'read_rate': round(messages_read / messages_delivered * 100, 1) if messages_delivered else 0,
                'contacts_added': results.get('contacts_added', 0),
                'conversations': results.get('conversations', 0),
                'campaigns_sent': results.get('campaigns_sent', 0),
                'daily_stats': self._get_daily_stats(org_id, start_date)
            }
    
    def _get_daily_stats(self, org_id: int, start_date: str) -> List[Dict]:
        """Get daily statistics"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT date, metric_type, SUM(value) as value
                FROM analytics
                WHERE organization_id = ? AND date >= ?
                GROUP BY date, metric_type
                ORDER BY date DESC
            """, (org_id, start_date))
            
            daily = {}
            for row in cursor.fetchall():
                date, metric, value = row
                if date not in daily:
                    daily[date] = {'date': date}
                daily[date][metric] = value
            
            return list(daily.values())[:30]
    
    # =====================================
    # KEYWORD METHODS
    # =====================================
    
    def add_keyword(self, org_id: int, keyword: str, response: str, 
                   flow_id: int = None, category: str = 'general') -> bool:
        """Add auto-reply keyword"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO keywords (organization_id, keyword, response, flow_id, category)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(organization_id, keyword)
                DO UPDATE SET response = ?, flow_id = ?, category = ?,
                              updated_at = CURRENT_TIMESTAMP
            """, (org_id, keyword.lower(), response, flow_id, category,
                  response, flow_id, category))
            return True
    
    def find_keyword_response(self, org_id: int, message: str) -> Optional[Dict]:
        """Find matching keyword response"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM keywords 
                WHERE organization_id = ? AND is_active = 1
            """, (org_id,))
            
            message_lower = message.lower()
            for row in cursor.fetchall():
                if row['keyword'].lower() in message_lower:
                    result = dict(row)
                    if result.get('flow_id'):
                        result['flow'] = self.get_flow(result['flow_id'])
                    return result
            
            return None
    
    def get_all_keywords(self, org_id: int) -> List[Dict]:
        """Get all keywords for organization"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT k.*, f.name as flow_name 
                FROM keywords k
                LEFT JOIN flows f ON k.flow_id = f.id
                WHERE k.organization_id = ?
                ORDER BY k.created_at DESC
            """, (org_id,))
            return [dict(row) for row in cursor.fetchall()]


# Singleton instance
_db_instance: Optional[EnterpriseDatabase] = None


def get_enterprise_db(db_path: str = "data/enterprise.db") -> EnterpriseDatabase:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = EnterpriseDatabase(db_path)
        _db_instance.init_db()
    return _db_instance
