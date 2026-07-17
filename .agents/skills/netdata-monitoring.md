# Netdata Monitoring Skill

## Purpose
Real-time monitoring for bot performance and health.

## What is Netdata?
Real-time performance monitoring - CPU, RAM, network, and more.

## Setup

### 1. Install Netdata
```bash
# One-liner install
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### 2. Configure for WhatsApp Bot
```bash
# Enable Python.d plugin for custom metrics
sudo nano /etc/netdata/python.d/whatsapp_bot.conf
```

### 3. Create Custom Metrics
```python
# In monitoring/netdata.py
import subprocess
import re

class NetdataMetrics:
    """Custom Netdata metrics for WhatsApp bot"""
    
    def __init__(self):
        self.metrics_file = "/var/run/netdata/whatsapp_bot_metrics"
    
    def collect(self):
        """Collect bot metrics"""
        metrics = {}
        
        # Messages per minute
        metrics["messages_processed"] = self.get_messages_count()
        metrics["replies_sent"] = self.get_replies_count()
        metrics["failed_messages"] = self.get_failed_count()
        metrics["response_time_avg"] = self.get_avg_response_time()
        metrics["active_sessions"] = self.get_active_sessions()
        metrics["queue_size"] = self.get_queue_size()
        metrics["cache_hit_rate"] = self.get_cache_hit_rate()
        
        return metrics
    
    def get_messages_count(self):
        """Get total messages processed"""
        try:
            from src.core.database import get_database
            db = get_database()
            return db.get_message_count_today()
        except:
            return 0
    
    def get_failed_count(self):
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
    
    def get_active_sessions(self):
        """Get active WhatsApp sessions"""
        try:
            return len([f for f in os.listdir("data/session") if f.endswith(".json")])
        except:
            return 0
    
    def get_queue_size(self):
        """Get pending message queue"""
        try:
            from src.core.queue import get_queue_size
            return get_queue_size()
        except:
            return 0
```

### 4. Export to Netdata
```python
# metrics_collector.py
import time
import os

METRICS_FILE = "/var/run/netdata/plugin/go.d/whatsapp_bot.conf"

def update_netdata():
    """Update Netdata charts"""
    metrics = NetdataMetrics().collect()
    
    # Write to Netdata collector file
    with open(METRICS_FILE, "w") as f:
        for key, value in metrics.items():
            f.write(f"CHART whatsapp_bot.{key} '' '{key}' 'count' 'whatsapp' '{key}' line 1000000\n")
            f.write(f"BEGIN whatsapp_bot.{key}\n")
            f.write(f"SET value = {value}\n")
            f.write(f"END\n")
```

### 5. Start Collector
```bash
# Add to systemd service
sudo nano /etc/systemd/system/netdata-collector.service
```

```ini
[Unit]
Description=Netdata WhatsApp Bot Metrics
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/whatsapp_bot/metrics_collector.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable netdata-collector
sudo systemctl start netdata-collector
```

## Dashboard Metrics

| Metric | Description |
|--------|-------------|
| Messages/Hour | Throughput |
| Response Time | Latency |
| Failed Messages | Error rate |
| Active Sessions | Connected users |
| CPU Usage | Bot CPU |
| RAM Usage | Memory |
| Queue Size | Pending work |

## Access Dashboard
```
http://localhost:19999
http://your-server:19999
```

## Alerts Setup
```bash
# Add health checks
sudo nano /etc/netdata/health.d/whatsapp_bot.conf
```

```
alarm: whatsapp_bot_errors
on: whatsapp_bot.failed_messages
every: 1m
warn: $this > 10
crit: $this > 50
exec: /usr/bin/netdata-silent
to: telegram
```

## Docker Monitoring
```bash
# Monitor bot container
docker run -d \
  --name netdata \
  -p 19999:19999 \
  -v /proc:/host/proc \
  -v /sys:/host/sys \
  netdata/netdata
```

## More Info
- Website: https://www.netdata.cloud
- GitHub: https://github.com/netdata/netdata
