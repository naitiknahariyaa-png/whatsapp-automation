"""
Plausible Analytics Integration - Privacy-Focused Analytics
=======================================================
FREE self-hosted Google Analytics alternative

Based on: https://github.com/plausible/analytics

Features:
- Privacy-friendly analytics
- No cookies required
- GDPR compliant
- Real-time stats
- 100% FREE (self-hosted)

Setup:
    1. Docker: docker run -d -p 8000:8000 plausible/analytics
    2. Get site key from dashboard
    
Environment:
    PLAUSIBLE_URL=http://localhost:8000
    PLAUSIBLE_SITE_KEY=your-site.com
"""

import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PlausibleAnalytics:
    """
    Plausible Analytics Client
    
    Use Cases:
    - Track website/app visitors
    - Real-time dashboard
    - Custom events
    - Privacy-compliant analytics
    
    Setup:
    1. Self-hosted (FREE):
       docker run -d -p 8000:8000 -e DATABASE_URL=sqlite plausible/analytics
    
    2. Cloud:
       https://plausible.io
    
    Environment:
    - PLAUSIBLE_URL=https://plausible.io
    - PLAUSIBLE_SITE_KEY=your-domain.com
    - PLAUSIBLE_API_KEY=xxx
    """
    
    def __init__(
        self,
        site_key: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.site_key = site_key or os.getenv("PLAUSIBLE_SITE_KEY", "")
        self.url = url or os.getenv("PLAUSIBLE_URL", "https://plausible.io")
        self.api_key = api_key or os.getenv("PLAUSIBLE_API_KEY", "")
        self.enabled = bool(self.site_key)
        
        if self.enabled:
            logger.info(f"✅ Plausible configured: {self.site_key}")
        else:
            logger.warning("⚠️ Plausible not configured")
    
    def track_event(
        self,
        name: str,
        props: Optional[Dict] = None,
        domain: Optional[str] = None
    ) -> bool:
        """
        Track custom event
        
        Use JavaScript on frontend:
        plausible('Pageview', {props: {key: 'value'}})
        """
        if not self.enabled:
            return False
        
        payload = {
            "name": name,
            "url": f"https://{domain or self.site_key}",
            "domain": domain or self.site_key,
            "props": props or {}
        }
        
        try:
            response = requests.post(
                f"{self.url}/api/event",
                json=payload,
                timeout=10
            )
            return response.status_code in [200, 202]
        except Exception as e:
            logger.error(f"Plausible track error: {e}")
            return False
    
    def track_pageview(self, url: str, domain: Optional[str] = None) -> bool:
        """Track pageview"""
        return self.track_event("pageview", {"url": url}, domain)
    
    def track_conversion(
        self,
        goal: str,
        user_id: Optional[str] = None,
        props: Optional[Dict] = None
    ) -> bool:
        """Track conversion/event"""
        data = props or {}
        data["user_id"] = user_id
        return self.track_event(goal, data)
    
    def get_stats(
        self,
        period: str = "30d",
        metrics: Optional[list] = None
    ) -> Optional[Dict]:
        """
        Get analytics stats
        
        periods: 24h, 7d, 30d, 6mo, 12mo, year, all
        metrics: visitors, pageviews, bounce_rate, visit_duration
        """
        if not self.api_key:
            logger.warning("Plausible API key required for stats")
            return None
        
        if not metrics:
            metrics = ["visitors", "pageviews", "bounce_rate", "visit_duration"]
        
        params = {
            "period": period,
            "metrics": ",".join(metrics)
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.get(
                f"{self.url}/api/v1/stats/aggregate",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Plausible stats error: {e}")
            return None
    
    def get_top_pages(self, period: str = "30d", limit: int = 10) -> list:
        """Get top pages"""
        if not self.api_key:
            return []
        
        params = {
            "period": period,
            "limit": limit
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.get(
                f"{self.url}/api/v1/stats/breakdown",
                params={**params, "property": "event:page"},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
        except Exception as e:
            logger.error(f"Plausible pages error: {e}")
            return []
    
    def get_sources(self, period: str = "30d") -> list:
        """Get traffic sources (referrals, utm)"""
        if not self.api_key:
            return []
        
        params = {"period": period}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.get(
                f"{self.url}/api/v1/stats/breakdown",
                params={**params, "property": "visit:source"},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
        except Exception as e:
            logger.error(f"Plausible sources error: {e}")
            return []
    
    def get_realtime_visitors(self) -> Optional[Dict]:
        """Get current realtime visitors"""
        if not self.api_key:
            return None
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.get(
                f"{self.url}/api/v1/stats/realtime/visitors",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Plausible realtime error: {e}")
            return None
    
    def generate_script_tag(self) -> str:
        """Generate tracking script tag for website"""
        return f'''
<script defer data-domain="{self.site_key}" src="{self.url}/js/script.tagged-events.js"></script>
'''
    
    def generate_script_custom_event(self) -> str:
        """Generate script for custom events"""
        return '''
<script>
window.plausible = window.plausible || function() { (window.plausible.q = window.plausible.q || []).push(arguments) }
</script>
'''


def setup_plausible():
    """Setup guide for Plausible"""
    print("\n" + "="*50)
    print("📊 Plausible Analytics Setup")
    print("="*50 + "\n")
    
    print("OPTION 1: Self-hosted (FREE)")
    print("-" * 40)
    print("1. Install Docker")
    print("2. Run:")
    print("   docker run -d -p 8000:8000 \\")
    print("     -e DATABASE_URL=sqlite.db \\")
    print("     -e BASE_URL=http://localhost:8000 \\")
    print("     plausible/analytics")
    print("3. Visit http://localhost:8000")
    print("4. Create admin account\n")
    
    print("OPTION 2: Cloud (Free tier)")
    print("-" * 40)
    print("1. Go to https://plausible.io")
    print("2. Sign up free")
    print("3. Add your website\n")
    
    url = input("Plausible URL: ").strip()
    site_key = input("Site Key (your-domain.com): ").strip()
    api_key = input("API Key (optional): ").strip()
    
    if url and site_key:
        with open(".env", "a") as f:
            f.write(f"\n# Plausible Analytics (Privacy-Friendly)\n")
            f.write(f"PLAUSIBLE_URL={url}\n")
            f.write(f"PLAUSIBLE_SITE_KEY={site_key}\n")
            if api_key:
                f.write(f"PLAUSIBLE_API_KEY={api_key}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ URL and Site Key required!")


if __name__ == "__main__":
    setup_plausible()
