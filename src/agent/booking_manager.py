"""
Booking Manager
Handles reservation creation, modification, and cancellation
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from config.settings import Settings
from src.models.schemas import (
    BookingRequest, Booking, BookingQuote, BookingStatusEnum
)
from src.models.database import DatabaseManager

logger = logging.getLogger(__name__)


class BookingManager:
    """Manages ride bookings and reservations"""
    
    def __init__(self):
        self.settings = Settings()
        self.db = DatabaseManager(self.settings.DATABASE_URL)
        self.service_tiers = self.settings.SERVICE_TIERS
    
    def create_booking(self, request: BookingRequest) -> Tuple[Booking, BookingQuote]:
        """
        Create a new booking and generate quote
        
        Returns:
            Tuple of (Booking, Quote)
        """
        # Validate minimum advance booking
        booking_datetime = f"{request.booking_date}T{request.booking_time}"
        if not self._validate_booking_time(booking_datetime):
            raise ValueError(f"Bookings must be made at least {self.service_tiers[request.service_tier]['min_advance_booking']} minutes in advance")
        
        # Create quote
        quote = self._generate_quote(
            request.pickup_location,
            request.dropoff_location,
            request.service_tier,
            request.booking_date
        )
        
        # Create booking
        booking_id = str(uuid.uuid4())
        booking = Booking(
            id=booking_id,
            customer_id=request.customer_id,
            customer_email=request.contact_email,
            customer_phone=request.phone if hasattr(request, 'phone') else "",
            pickup_location=request.pickup_location,
            dropoff_location=request.dropoff_location,
            booking_date=request.booking_date,
            booking_time=request.booking_time,
            passenger_count=request.passenger_count,
            service_tier=request.service_tier,
            special_requests=request.special_requests,
            quote=quote,
            status=BookingStatusEnum.QUOTED
        )
        
        # Save to database
        booking_dict = booking.model_dump()
        booking_dict['quote'] = quote.model_dump()
        self.db.create_booking(booking_dict)
        
        logger.info(f"Created booking {booking_id} for customer {request.customer_id}")
        
        return booking, quote
    
    def confirm_booking(self, booking_id: str, payment_id: Optional[str] = None) -> Booking:
        """Confirm a booking and update status"""
        booking = self.db.get_booking(booking_id)
        
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        # Update status
        updates = {
            "status": "confirmed",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if payment_id:
            updates["payment_id"] = payment_id
            updates["status"] = "scheduled"
        
        self.db.update_booking(booking_id, updates)
        
        logger.info(f"Confirmed booking {booking_id}")
        
        return booking
    
    def cancel_booking(self, booking_id: str, reason: Optional[str] = None) -> bool:
        """Cancel a booking"""
        booking = self.db.get_booking(booking_id)
        
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        # Check if cancellation is allowed
        status = booking.get("status")
        if status in ["completed", "cancelled"]:
            raise ValueError(f"Cannot cancel booking with status {status}")
        
        # Update status
        updates = {
            "status": "cancelled",
            "notes": reason or "Cancelled by customer",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.db.update_booking(booking_id, updates)
        
        logger.info(f"Cancelled booking {booking_id}")
        return True
    
    def _generate_quote(self, pickup: str, dropoff: str, tier: str, date: str) -> BookingQuote:
        """Generate price quote for a booking"""
        
        tier_config = self.service_tiers.get(tier, self.service_tiers["executive"])
        
        # Estimate distance (simplified - in production, use real routing API)
        estimated_distance = self._estimate_distance(pickup, dropoff)
        estimated_duration = self._estimate_duration(estimated_distance)
        
        # Calculate charges
        base_fare = tier_config["base_fare"]
        distance_charge = estimated_distance * tier_config["per_mile"]
        duration_charge = estimated_duration * tier_config["per_minute"]
        
        subtotal = base_fare + distance_charge + duration_charge
        tax_rate = 0.08  # 8% tax
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        quote = BookingQuote(
            booking_id="",  # Will be set when booking is created
            service_tier=tier,
            base_fare=round(base_fare, 2),
            estimated_distance_miles=round(estimated_distance, 2),
            distance_charge=round(distance_charge, 2),
            estimated_duration_minutes=round(estimated_duration, 1),
            duration_charge=round(duration_charge, 2),
            subtotal=round(subtotal, 2),
            tax_rate=tax_rate,
            tax=round(tax, 2),
            total_fare=round(total, 2),
            valid_until=datetime.utcnow() + timedelta(hours=1)
        )
        
        return quote
    
    def _estimate_distance(self, pickup: str, dropoff: str) -> float:
        """
        Estimate distance between two locations
        In production, use Google Maps API or similar
        """
        # Simplified estimation based on location pairs
        location_distances = {
            ("New York City, NY", "JFK Airport"): 15.0,
            ("New York City, NY", "Manhattan Hotel"): 3.0,
            ("Los Angeles, CA", "LAX Airport"): 18.0,
            ("Chicago, IL", "Downtown"): 12.0,
            ("Miami, FL", "Beach Resort"): 8.0,
        }
        
        # Check exact match
        key = (pickup, dropoff)
        if key in location_distances:
            return location_distances[key]
        
        # Default estimate
        return 10.0
    
    def _estimate_duration(self, distance: float) -> float:
        """Estimate ride duration in minutes based on distance"""
        # Assume average speed of 25 mph in urban area + 10 min base
        return 10 + (distance / 25) * 60
    
    def _validate_booking_time(self, booking_datetime: str) -> bool:
        """Validate that booking meets minimum advance notice requirement"""
        from datetime import datetime
        
        # Parse booking time
        booking_dt = datetime.fromisoformat(booking_datetime.replace("T", " "))
        now = datetime.utcnow()
        
        # Calculate minutes until booking
        minutes_until = (booking_dt - now).total_seconds() / 60
        
        # Check against minimum requirement (2 hours = 120 minutes)
        return minutes_until >= 120
