"""
Google Calendar Integration - Appointment Booking
Let customers book appointments via WhatsApp
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """
    Google Calendar API Client
    
    Perfect for:
    - Book appointments from WhatsApp
    - Show available slots
    - Send calendar invites
    
    Setup:
    1. Go to https://console.cloud.google.com
    2. Create a new project
    3. Enable Google Calendar API
    4. Create OAuth credentials or Service Account
    5. Add to .env
    
    Environment:
    - GOOGLE_CLIENT_ID=xxx
    - GOOGLE_CLIENT_SECRET=xxx
    - GOOGLE_CALENDAR_ID=primary or your-calendar-id
    """
    
    BASE_URL = "https://www.googleapis.com/calendar/v3"
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        calendar_id: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        self.client_id = client_id or os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.calendar_id = calendar_id or os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.access_token = access_token or os.getenv("GOOGLE_ACCESS_TOKEN", "")
        self.refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "")
        
        self.enabled = bool(self.access_token or self.refresh_token)
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        if self.enabled:
            logger.info("✅ Google Calendar configured")
        else:
            logger.warning("⚠️ Google Calendar not configured")
    
    def get_events(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Get upcoming events
        
        Args:
            time_min: Start time (default: now)
            time_max: End time (default: 30 days from now)
            max_results: Number of events to return
        """
        if not self.enabled:
            return []
        
        if not time_min:
            time_min = datetime.now()
        if not time_max:
            time_max = time_min + timedelta(days=30)
        
        params = {
            "timeMin": time_min.isoformat() + "Z",
            "timeMax": time_max.isoformat() + "Z",
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/calendars/{self.calendar_id}/events",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("items", [])
            return []
            
        except Exception as e:
            logger.error(f"Get events error: {e}")
            return []
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a calendar event
        
        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            attendees: List of email addresses
            location: Location
        """
        if not self.enabled:
            return None
        
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Asia/Kolkata"  # IST timezone
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 30}
                ]
            }
        }
        
        if description:
            event["description"] = description
        
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
        
        if location:
            event["location"] = location
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/calendars/{self.calendar_id}/events",
                headers=self.headers,
                json=event,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Create event error: {e}")
            return None
    
    def book_appointment(
        self,
        customer_name: str,
        customer_phone: str,
        service: str,
        start_time: datetime,
        duration_minutes: int = 60
    ) -> Optional[Dict]:
        """
        Quick book appointment
        
        Args:
            customer_name: Customer name
            customer_phone: Customer phone
            service: Service name
            start_time: Appointment start time
            duration_minutes: Duration (default 60 min)
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        description = f"""
**Customer:** {customer_name}
**Phone:** {customer_phone}
**Service:** {service}
**Booked via:** WhatsApp Bot
"""
        
        return self.create_event(
            summary=f"📅 {service} - {customer_name}",
            start_time=start_time,
            end_time=end_time,
            description=description,
            attendees=[]
        )
    
    def get_available_slots(
        self,
        date: datetime,
        duration_minutes: int = 60,
        working_hours: tuple = (9, 18)  # 9 AM to 6 PM
    ) -> List[Dict]:
        """
        Get available time slots for a date
        
        Returns list of available start times
        """
        start_hour, end_hour = working_hours
        start = date.replace(hour=start_hour, minute=0, second=0)
        end = date.replace(hour=end_hour, minute=0, second=0)
        
        events = self.get_events(time_min=start, time_max=end)
        
        slots = []
        current = start
        
        while current < end:
            slot_end = current + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with any event
            is_available = True
            for event in events:
                event_start = event.get("start", {}).get("dateTime")
                event_end = event.get("end", {}).get("dateTime")
                
                if event_start and event_end:
                    event_start = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
                    event_end = datetime.fromisoformat(event_end.replace("Z", "+00:00"))
                    
                    if not (slot_end <= event_start or current >= event_end):
                        is_available = False
                        break
            
            if is_available:
                slots.append({
                    "start": current,
                    "end": slot_end,
                    "available": True
                })
            
            current += timedelta(minutes=30)  # 30-minute slot intervals
        
        return slots


def setup_google_calendar():
    """Interactive setup for Google Calendar"""
    print("\n" + "="*50)
    print("📅 Google Calendar Setup")
    print("="*50 + "\n")
    
    print("How to setup Google Calendar API:")
    print("1. Go to https://console.cloud.google.com")
    print("2. Create new project")
    print("3. Search and enable 'Google Calendar API'")
    print("4. Go to Credentials → Create Credentials → OAuth Client ID")
    print("5. Desktop app, download JSON")
    print("6. Or use Service Account for server-side\n")
    
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    calendar_id = input("Calendar ID (press Enter for 'primary'): ").strip()
    
    if not calendar_id:
        calendar_id = "primary"
    
    if client_id and client_secret:
        with open(".env", "a") as f:
            f.write(f"\n# Google Calendar\n")
            f.write(f"GOOGLE_CLIENT_ID={client_id}\n")
            f.write(f"GOOGLE_CLIENT_SECRET={client_secret}\n")
            f.write(f"GOOGLE_CALENDAR_ID={calendar_id}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ Client ID and Secret required!")


if __name__ == "__main__":
    setup_google_calendar()
