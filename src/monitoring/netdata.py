"""
Netdata Monitoring - Real-time Performance Metrics
Track bot performance, messages/hour, response times, and more.
"""

import os
import logging
import subprocess
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class NetdataMetrics:
    """
    Custom Netdata metrics for WhatsApp bot
    
    Features:
    - Messages processed per minute
    - Response time tracking
    - Active sessions count
    - Queue size monitoring
    - Cache hit rate
    - Error rate tracking
    
    Setup:
    1. Install Netdata: bash <(curl -Ss https://my-netdata.io/kickstart.sh)
    2. Configure Python collector
    3. Start metrics collector
    """
    
    def __init__(self):
        self.metrics_file = os.getenv(
            "NETDATA_METRICS_FILE",
            "/var/run/netdata/plugin/whatsapp_bot_metrics"
        )
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect all bot metrics
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "messages_processed": self.get_messages_count(),
            "replies_sent": self.get_replies_count(),
            "failed_messages": self.get_failed_count(),
            "response_time_avg": self.get_avg_response_time(),
            "active_sessions": self.get_active_sessions(),
            "queue_size": self.get_queue_size(),
            "cache_hit_rate": self.get_cache_hit_rate(),
            "unique_users_today": self.get_unique_users()
        }
        
        return metrics
    
    def get_messages_count(self) -> int:
        """Get total messages processed today"""
        try:
            from src.core.database import get_database
            db = get_database()
            return db.get_message_count_today()
        except:
            return 0
    
    def get_replies_count(self) -> int:
        """Get total replies sent today"""
        try:
            from src.core.database import get_database
            db = get_database()
            stats = db.get_stats()
            return stats.get("replies_sent", 0)
        except:
            return 0
    
    def get_failed_count(self) -> int:
        """Get failed message count"""
        try:
            # Check logs for errors
            result = subprocess.run(
                ["tail", "-100", "/var/log/whatsapp_bot.log"],
                capture_output=True, text=True
            )
            return result.stdout.count("[ERROR]")
        except:
            return 0
    
    def get_avg_response_time(self) -> float:
        """Get average AI response time in seconds"""
        try:
            from src.core.database import get_database
            db = get_database()
            return db.get_avg_response_time()
        except:
            return 0.0
    
    def get_active_sessions(self) -> int:
        """Get active WhatsApp sessions"""
        try:
            import os
            session_dir = "data/session"
            if os.path.exists(session_dir):
                return len([f for f in os.listdir(session_dir) if f.endswith(".json")])
            return 0
        except:
            return 0
    
    def get_queue_size(self) -> int:
        """Get pending message queue size"""
        try:
            from src.core.queue import get_queue_size
            return get_queue_size()
        except:
            return 0
    
    def get_cache_hit_rate(self) -> float:
        """Get Redis cache hit rate"""
        try:
            from src.integrations.redis_client import RedisCache
            cache = RedisCache()
            
            if cache.enabled:
                info = cache.client.info("stats")
                hits = info.get("keyspace_hits", 0)
                misses = info.get("keyspace_misses", 0)
                total = hits + misses
                
                if total > 0:
                    return round((hits / total) * 100, 2)
            return 0.0
        except:
            return 0.0
    
    def get_unique_users(self) -> int:
        """Get unique users today"""
        try:
            from src.core.database import get_database
            db = get_database()
            return db.get_unique_users_today()
        except:
            return 0
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics formatted for display"""
        metrics = self.collect()
        
        return {
            "messages": {
                "processed_today": metrics["messages_processed"],
                "replies_sent": metrics["replies_sent"],
                "failed": metrics["failed_messages"],
                "unique_users": metrics["unique_users_today"]
            },
            "performance": {
                "avg_response_time": f"{metrics['response_time_avg']:.2f}s",
                "cache_hit_rate": f"{metrics['cache_hit_rate']}%"
            },
            "status": {
                "active_sessions": metrics["active_sessions"],
                "queue_size": metrics["queue_size"]
            }
        }


class NetdataCollector:
    """
    Export metrics to Netdata
    
    This collector writes metrics to a format Netdata can read.
    """
    
    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file or "/var/run/netdata/plugin/whatsapp_bot.conf"
        self.metrics = NetdataMetrics()
    
    def collect_and_export(self):
        """Collect metrics and export to Netdata format"""
        metrics = self.metrics.collect()
        
        try:
            with open(self.output_file, "w") as f:
                # Chart definition
                f.write("CHART whatsapp_bot.messages '' 'WhatsApp Messages' 'count' 'whatsapp' 'whatsapp_bot.messages' line 1000000\n")
                f.write("DIMENSION messages_processed 'processed' absolute 1 1\n")
                f.write("DIMENSION replies_sent 'sent' absolute 1 1\n")
                f.write("DIMENSION failed 'failed' absolute 1 1\n")
                
                f.write("CHART whatsapp_bot.performance '' 'Performance' 'seconds' 'whatsapp' 'whatsapp_bot.performance' line 1000000\n")
                f.write("DIMENSION response_time_avg 'avg_response' absolute 1000 1000\n")
                f.write("DIMENSION cache_hit_rate 'cache_hit' absolute 1 1\n")
                
                f.write("CHART whatsapp_bot.status '' 'Bot Status' 'count' 'whatsapp' 'whatsapp_bot.status' line 1000000\n")
                f.write("DIMENSION active_sessions 'sessions' absolute 1 1\n")
                f.write("DIMENSION queue_size 'queue' absolute 1 1\n")
                
                # BEGIN blocks with values
                f.write(f"BEGIN whatsapp_bot.messages\n")
                f.write(f"SET processed = {metrics['messages_processed']}\n")
                f.write(f"SET sent = {metrics['replies_sent']}\n")
                f.write(f"SET failed = {metrics['failed_messages']}\n")
                f.write(f"END\n")
                
                f.write(f"BEGIN whatsapp_bot.performance\n")
                f.write(f"SET avg_response = {int(metrics['response_time_avg'] * 1000)}\n")
                f.write(f"SET cache_hit = {metrics['cache_hit_rate']}\n")
                f.write(f"END\n")
                
                f.write(f"BEGIN whatsapp_bot.status\n")
                f.write(f"SET sessions = {metrics['active_sessions']}\n")
                f.write(f"SET queue = {metrics['queue_size']}\n")
                f.write(f"END\n")
            
            logger.debug("Exported metrics to Netdata")
            
        except Exception as e:
            logger.error(f"Netdata export error: {e}")


class PrometheusMetrics:
    """
    Export metrics in Prometheus format
    
    Can be scraped by Prometheus or used with Grafana.
    """
    
    def __init__(self):
        self.metrics = NetdataMetrics()
    
    def get_prometheus_output(self) -> str:
        """Get metrics in Prometheus format"""
        metrics = self.metrics.collect()
        
        output = f"""# HELP whatsapp_messages_processed_total Total messages processed
# TYPE whatsapp_messages_processed_total counter
whatsapp_messages_processed_total {metrics['messages_processed']}

# HELP whatsapp_replies_sent_total Total replies sent
# TYPE whatsapp_replies_sent_total counter
whatsapp_replies_sent_total {metrics['replies_sent']}

# HELP whatsapp_failed_messages_total Total failed messages
# TYPE whatsapp_failed_messages_total counter
whatsapp_failed_messages_total {metrics['failed_messages']}

# HELP whatsapp_response_time_seconds Average response time in seconds
# TYPE whatsapp_response_time_seconds gauge
whatsapp_response_time_seconds {metrics['response_time_avg']}

# HELP whatsapp_active_sessions Number of active sessions
# TYPE whatsapp_active_sessions gauge
whatsapp_active_sessions {metrics['active_sessions']}

# HELP whatsapp_cache_hit_rate Cache hit rate percentage
# TYPE whatsapp_cache_hit_rate gauge
whatsapp_cache_hit_rate {metrics['cache_hit_rate']}

# HELP whatsapp_unique_users_today Unique users today
# TYPE whatsapp_unique_users_today gauge
whatsapp_unique_users_today {metrics['unique_users_today']}
"""
        
        return output
    
    def save_to_file(self, filepath: str = "/var/www/html/metrics.txt"):
        """Save metrics to file for Prometheus scraping"""
        try:
            with open(filepath, "w") as f:
                f.write(self.get_prometheus_output())
        except Exception as e:
            logger.error(f"Prometheus metrics save error: {e}")


def setup_netdata():
    """Guide user to setup Netdata"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           Netdata Monitoring Setup                       ║
╚══════════════════════════════════════════════════════════╝

1. Install Netdata:
   bash <(curl -Ss https://my-netdata.io/kickstart.sh)

2. Access Dashboard:
   http://localhost:19999

3. Configure Custom Metrics:

   # Create collector config
   sudo nano /etc/netdata/python.d/whatsapp_bot.conf
   
   # Add:
   whatsapp_bot:
     name: 'whatsapp'
     metrics_file: '/var/run/netdata/plugin/whatsapp_bot_metrics'

4. Run Metrics Collector:
   
   python -m src.monitoring.netdata

5. View in Dashboard:
   - Go to http://localhost:19999
   - Find "whatsapp_bot" charts

Available Metrics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Messages:
   - messages_processed_total
   - replies_sent_total
   - failed_messages_total
   - unique_users_today

⚡ Performance:
   - response_time_avg
   - cache_hit_rate

🔄 Status:
   - active_sessions
   - queue_size

Prometheus Export:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Add to prometheus.yml:
   scrape_configs:
     - job_name: 'whatsapp-bot'
       static_configs:
         - targets: ['localhost:8000']

# In your bot, add metrics endpoint:
   @app.get('/metrics')
   async def metrics():
       prom = PrometheusMetrics()
       return Response(
           content=prom.get_prometheus_output(),
           media_type='text/plain'
       )

Grafana Dashboard:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Import dashboard from:
https://grafana.com/dashboards/ (search for "WhatsApp Bot")
""")


if __name__ == "__main__":
    setup_netdata()
