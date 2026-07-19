"""
Cal.com Integration - FREE Scheduling System
===========================================
Open-source Calendly alternative

Based on: https://github.com/calcom/cal.com

Features:
- Appointment booking
- Team scheduling
- Video meetings
- Calendar sync
- 100% FREE!

Setup:
    git clone https://github.com/calcom/docker.git cal-docker
    cd cal-docker
    docker compose up -d
"""

import os
import logging
import requests
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CalClient:
    """
    Cal.com Scheduling Client
    
    Use Cases:
    - Book appointments via WhatsApp
    - Meeting scheduling
    - Service booking
    - Team calendar
    
    Setup:
    1. Self-hosted (FREE):
       git clone https://github.com/calcom/docker.git cal-docker
       cd cal-docker
       docker compose up -d
    
    2. Cloud (Free tier):
       https://cal.com
    
    Environment:
    - CAL_URL=https://cal.com (or your self-hosted URL)
    - CAL_API_KEY=xxx
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("CAL_API_KEY", "")
        self.url = url or os.getenv("CAL_URL", "https://api.cal.com/v1")
        self.enabled = bool(self.api_key)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.enabled:
            logger.info(f"✅ Cal.com configured")
        else:
            logger.warning("⚠️ Cal.com not configured (set CAL_API_KEY)")
    
    def get_event_types(self) -> List[Dict]:
        """Get available event types (services)"""
        try:
            response = requests.get(
                f"{self.url}/event-types",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("event_types", [])
            return []
        except Exception as e:
            logger.error(f"Cal.com event types error: {e}")
            return []
    
    def get_availability(
        self,
        event_type_id: int,
        date_from: str,
        date_to: str
    ) -> Optional[Dict]:
        """Get available slots"""
        params = {
            "eventTypeId": event_type_id,
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        try:
            response = requests.get(
                f"{self.url}/availability",
                headers=self.headers,
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Cal.com availability error: {e}")
            return None
    
    def create_booking(
        self,
        event_type_id: int,
        start: str,
        end: str,
        name: str,
        email: str,
        phone: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a booking
        
        Args:
            event_type_id: Event type ID from get_event_types
            start: Start time ISO format
            end: End time ISO format
            name: Customer name
            email: Customer email
            phone: Customer phone
            notes: Additional notes
        """
        payload = {
            "eventTypeId": event_type_id,
            "start": start,
            "end": end,
            "responses": {
                "name": name,
                "email": email
            }
        }
        
        if phone:
            payload["responses"]["phone"] = phone
        if notes:
            payload["responses"]["notes"] = notes
        
        try:
            response = requests.post(
                f"{self.url}/bookings",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Cal.com booking error: {e}")
            return None
    
    def list_bookings(
        self,
        status: str = "upcoming"
    ) -> List[Dict]:
        """List bookings"""
        params = {"status": status}
        
        try:
            response = requests.get(
                f"{self.url}/bookings",
                headers=self.headers,
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("bookings", [])
            return []
        except Exception as e:
            logger.error(f"Cal.com list bookings error: {e}")
            return []
    
    def cancel_booking(self, booking_id: int, reason: str = "") -> bool:
        """Cancel a booking"""
        payload = {"cancellationReason": reason}
        
        try:
            response = requests.delete(
                f"{self.url}/bookings/{booking_id}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Cal.com cancel error: {e}")
            return False
    
    def get_available_slots(
        self,
        event_type_id: int,
        date: str
    ) -> List[str]:
        """Get available time slots for a date"""
        available = self.get_availability(
            event_type_id,
            date,
            date
        )
        
        if not available:
            return []
        
        slots = []
        for slot in available.get("busy", []):
            start = slot.get("start", "")
            if start:
                slots.append(start)
        
        return slots


def setup_cal():
    """Setup guide for Cal.com"""
    print("\n" + "="*50)
    print("📅 Cal.com Scheduling Setup")
    print("="*50 + "\n")
    
    print("OPTION 1: Self-hosted (FREE)")
    print("-" * 40)
    print("git clone https://github.com/calcom/docker.git cal-docker")
    print("cd cal-docker")
    print("cp .env.example .env")
    print("docker compose up -d")
    print("\nVisit http://localhost:8080\n")
    
    print("OPTION 2: Cloud (Free tier)")
    print("-" * 40)
    print("1. Go to https://cal.com")
    print("2. Sign up free")
    print("3. Create event types (services)")
    print("4. Get API key from Settings\n")
    
    url = input("Cal.com URL (press Enter for cloud): ").strip()
    if not url:
        url = "https://api.cal.com/v1"
    
    key = input("API Key: ").strip()
    
    if key:
        with open(".env", "a") as f:
            f.write(f"\n# Cal.com (Scheduling)\n")
            f.write(f"CAL_API_KEY={key}\n")
            if "cal.com" in url:
                f.write(f"CAL_URL={url}\n")
            else:
                f.write(f"CAL_URL={url}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ API Key required!")


if __name__ == "__main__":
    setup_cal()
