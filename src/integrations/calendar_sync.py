"""
Calendar/Availability Integration
Manages ride availability and driver scheduling
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AvailabilityManager:
    """Manages ride availability and scheduling"""
    
    def __init__(self):
        self.blocked_times = {}  # Times when no rides available
        self.driver_availability = {}  # Per-driver availability
    
    def check_availability(self, city: str, date: str, time: str) -> bool:
        """
        Check if rides are available for requested date/time
        
        Args:
            city: Service city
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            
        Returns:
            True if rides available
        """
        
        try:
            datetime.fromisoformat(f"{date}T{time}")
        except ValueError:
            logger.error(f"Invalid date/time format: {date} {time}")
            return False
        
        # Check if time is blocked
        key = f"{city}_{date}_{time}"
        if key in self.blocked_times:
            return False
        
        # In production, check against actual driver availability
        return True
    
    def get_available_time_windows(self, city: str, date: str) -> List[Dict]:
        """
        Get available time windows for a given date
        
        Returns:
            List of available time windows
        """
        
        windows = []
        current_hour = 6  # Service starts at 6am
        
        while current_hour < 24:
            for minute in [0, 30]:
                time_str = f"{current_hour:02d}:{minute:02d}"
                key = f"{city}_{date}_{time_str}"
                
                if key not in self.blocked_times:
                    windows.append({
                        "time": time_str,
                        "available": True
                    })
            
            current_hour += 1
        
        return windows
    
    def block_time_window(self, city: str, date: str, time: str, duration_minutes: int = 60):
        """Block a time window from being booked"""
        
        # Block the requested time and duration
        start = datetime.fromisoformat(f"{date}T{time}")
        
        for i in range(duration_minutes // 30):
            blocked_time = start + timedelta(minutes=i*30)
            key = f"{city}_{blocked_time.strftime('%Y-%m-%d')}_{blocked_time.strftime('%H:%M')}"
            self.blocked_times[key] = True
    
    def unblock_time_window(self, city: str, date: str, time: str):
        """Unblock a previously blocked time"""
        
        key = f"{city}_{date}_{time}"
        if key in self.blocked_times:
            del self.blocked_times[key]
