"""
📊 Metrics Collection Module
========================
Collect and expose application metrics for monitoring.
"""

import time
import psutil
import threading
from typing import Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SystemMetrics:
    """System-level metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: str


@dataclass
class AppMetrics:
    """Application-level metrics."""
    uptime_seconds: float
    total_requests: int
    total_messages: int
    total_customers: int
    total_orders: int
    cache_hit_rate: float
    ai_requests: int
    error_count: int


class MetricsCollector:
    """
    Collect and store application metrics.
    
    Usage:
        metrics = MetricsCollector()
        metrics.increment("requests")
        current_metrics = metrics.get_all()
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._start_time = time.time()
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
    
    def increment(self, name: str, value: int = 1):
        """Increment a counter."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge value."""
        with self._lock:
            self._gauges[name] = value
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_percent=disk.percent,
            network_sent_mb=net.bytes_sent / (1024 * 1024),
            network_recv_mb=net.bytes_recv / (1024 * 1024),
            timestamp=datetime.now().isoformat()
        )
    
    def get_app_metrics(self) -> AppMetrics:
        """Get current application metrics."""
        with self._lock:
            return AppMetrics(
                uptime_seconds=time.time() - self._start_time,
                total_requests=self._counters.get('requests', 0),
                total_messages=self._counters.get('messages', 0),
                total_customers=self._counters.get('customers', 0),
                total_orders=self._counters.get('orders', 0),
                cache_hit_rate=self._gauges.get('cache_hit_rate', 0.0),
                ai_requests=self._counters.get('ai_requests', 0),
                error_count=self._counters.get('errors', 0)
            )
    
    def get_all(self) -> Dict[str, Any]:
        """Get all metrics combined."""
        system = self.get_system_metrics()
        app = self.get_app_metrics()
        
        return {
            'system': asdict(system),
            'app': asdict(app),
            'counters': dict(self._counters),
            'gauges': dict(self._gauges)
        }
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._start_time = time.time()
            self._counters.clear()
            self._gauges.clear()


# Singleton instance
_metrics_instance = None


def get_metrics() -> MetricsCollector:
    """Get or create metrics collector."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance
