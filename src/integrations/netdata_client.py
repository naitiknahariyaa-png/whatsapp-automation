"""
Netdata Integration - FREE Real-Time Monitoring
==============================================
System and application monitoring

Based on: https://github.com/netdata/netdata

Features:
- Real-time monitoring
- System metrics
- Custom charts
- Alerts & notifications
- 100% FREE!

Setup:
    curl https://my-netdata.io/kickstart.sh | sh
"""

import os
import logging
import requests
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class NetdataClient:
    """
    Netdata Monitoring Client
    
    Use Cases:
    - Monitor server health
    - Track bot performance
    - System alerts
    - Custom metrics
    - Dashboard API
    
    Setup:
    1. Install on server:
       curl https://my-netdata.io/kickstart.sh | sh
    
    2. Docker:
       docker run -d -p 19999:19999 \\
         -v /proc:/host/proc \\
         -v /sys:/host/sys \\
         netdata/netdata
    
    Environment:
    - NETDATA_URL=http://localhost:19999
    """
    
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("NETDATA_URL", "http://localhost:19999")
        self.enabled = self._check_connection()
        
        if self.enabled:
            logger.info(f"✅ Netdata configured: {self.url}")
        else:
            logger.warning("⚠️ Netdata not configured")
    
    def _check_connection(self) -> bool:
        try:
            r = requests.get(f"{self.url}/api/v1/info", timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def get_allmetrics(self, chart: Optional[str] = None) -> Dict:
        """Get all or specific chart metrics"""
        endpoint = "/api/v1/allmetrics"
        if chart:
            endpoint += f"?chart={chart}"
        
        try:
            response = requests.get(f"{self.url}{endpoint}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Netdata metrics error: {e}")
            return {}
    
    def get_chart_data(
        self,
        chart: str,
        after: int = -3600,
        before: int = 0,
        group: str = "average",
        points: int = 100
    ) -> Optional[Dict]:
        """Get chart data for graphing"""
        params = {
            "chart": chart,
            "after": after,
            "before": before,
            "group": group,
            "points": points,
            "format": "json"
        }
        
        try:
            response = requests.get(
                f"{self.url}/api/v1/data",
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Netdata chart error: {e}")
            return None
    
    def get_system_info(self) -> Optional[Dict]:
        """Get system information"""
        try:
            response = requests.get(f"{self.url}/api/v1/info", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Netdata info error: {e}")
            return None
    
    def get_alarms(self) -> List[Dict]:
        """Get all alarms"""
        try:
            response = requests.get(
                f"{self.url}/api/v1/alarms",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("alarms", [])
            return []
        except Exception as e:
            logger.error(f"Netdata alarms error: {e}")
            return []
    
    def get_active_alarms(self) -> List[Dict]:
        """Get only active (triggered) alarms"""
        alarms = self.get_alarms()
        return [a for a in alarms if a.get("status") == "CRITICAL" or a.get("status") == "WARNING"]
    
    def get_custom_metric(
        self,
        metric: str,
        after: int = -60,
        before: int = 0
    ) -> Optional[List]:
        """Get specific metric data"""
        chart = f"app.{metric}"
        data = self.get_chart_data(chart, after, before)
        
        if data and "data" in data:
            return data["data"]
        return None
    
    def get_cpu_usage(self) -> Optional[float]:
        """Get current CPU usage percentage"""
        data = self.get_chart_data("system.cpu", after=-60, points=1)
        if data and data.get("data"):
            # Average of last minute
            values = data["data"][0][1:]  # Skip timestamp
            return sum(values) / len(values) if values else 0
        return None
    
    def get_memory_usage(self) -> Optional[Dict]:
        """Get memory usage stats"""
        data = self.get_chart_data("system.ram", after=-60, points=1)
        if data and data.get("data"):
            labels = data.get("labels", [])
            values = data["data"][0][1:]
            return dict(zip(labels, values))
        return None
    
    def get_network_stats(self) -> Optional[Dict]:
        """Get network I/O stats"""
        inbound = self.get_chart_data("net.net", after=-60, points=1)
        outbound = self.get_chart_data("net.net", after=-60, points=1)
        
        return {
            "inbound_kbs": inbound.get("data", [[0, 0]])[0][-1] if inbound.get("data") else 0,
            "outbound_kbs": outbound.get("data", [[0, 0]])[0][-1] if outbound.get("data") else 0
        }
    
    def check_health(self) -> Dict:
        """Quick health check"""
        alarms = self.get_active_alarms()
        cpu = self.get_cpu_usage()
        
        status = "healthy"
        issues = []
        
        if alarms:
            status = "alert"
            issues = [a.get("name", "Unknown") for a in alarms]
        
        if cpu and cpu > 90:
            status = "warning" if status == "healthy" else status
            issues.append(f"High CPU: {cpu:.1f}%")
        
        return {
            "status": status,
            "cpu_percent": cpu,
            "active_alarms": len(alarms),
            "issues": issues
        }


def setup_netdata():
    """Setup guide for Netdata"""
    print("\n" + "="*50)
    print("📊 Netdata Monitoring Setup")
    print("="*50 + "\n")
    
    print("Installation (Linux):")
    print("-" * 40)
    print("curl https://my-netdata.io/kickstart.sh | sh")
    print("\nDocker:")
    print("-" * 40)
    print("docker run -d -p 19999:19999 \\")
    print("  -v /proc:/host/proc \\")
    print("  -v /sys:/host/sys \\")
    print("  netdata/netdata")
    print("\nWindows:")
    print("-" * 40)
    print("Use WSL2 or install on Linux VM\n")
    
    url = input("Netdata URL (press Enter for default): ").strip()
    if not url:
        url = "http://localhost:19999"
    
    with open(".env", "a") as f:
        f.write(f"\n# Netdata (Real-Time Monitoring)\n")
        f.write(f"NETDATA_URL={url}\n")
    print("✅ Saved to .env!")
    print(f"\nDashboard: {url}")


if __name__ == "__main__":
    setup_netdata()
