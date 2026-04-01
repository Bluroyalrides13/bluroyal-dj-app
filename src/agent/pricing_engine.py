"""
Pricing Engine
Calculates dynamic pricing based on service tier, distance, time, and demand
"""

import logging
from datetime import datetime
from typing import Dict, Tuple

from config.settings import Settings

logger = logging.getLogger(__name__)


class PricingEngine:
    """Manages pricing calculations and quotes"""
    
    def __init__(self):
        self.settings = Settings()
        self.service_tiers = self.settings.SERVICE_TIERS
    
    def calculate_fare(self, 
                      distance: float,
                      duration: float,
                      service_tier: str,
                      peak_factor: float = 1.0) -> Dict:
        """
        Calculate fare for a ride
        
        Args:
            distance: Distance in miles
            duration: Duration in minutes
            service_tier: One of executive, premier, vip
            peak_factor: Pricing multiplier for peak times (1.0 = normal, 1.5 = peak)
            
        Returns:
            Dict with fare breakdown
        """
        
        tier_config = self.service_tiers.get(service_tier, self.service_tiers["executive"])
        
        # Calculate components
        base_fare = tier_config["base_fare"]
        distance_charge = distance * tier_config["per_mile"]
        duration_charge = duration * tier_config["per_minute"]
        subtotal = (base_fare + distance_charge + duration_charge) * peak_factor
        
        # Apply tax
        tax_rate = 0.08  # 8% sales tax
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        return {
            "service_tier": service_tier,
            "base_fare": round(base_fare, 2),
            "distance_miles": round(distance, 2),
            "distance_charge": round(distance_charge * peak_factor, 2),
            "duration_minutes": round(duration, 1),
            "duration_charge": round(duration_charge * peak_factor, 2),
            "subtotal": round(subtotal, 2),
            "tax_rate": tax_rate,
            "tax": round(tax, 2),
            "total": round(total, 2),
            "peak_factor": peak_factor,
            "currency": "USD"
        }
    
    def get_peak_factor(self, booking_datetime: str) -> float:
        """
        Get pricing multiplier based on time of day/day of week
        
        Returns:
            Factor to multiply base prices by (1.0 = normal, 1.25 = moderate peak, 1.5 = high peak)
        """
        try:
            dt = datetime.fromisoformat(booking_datetime.replace(" ", "T"))
        except:
            return 1.0
        
        hour = dt.hour
        weekday = dt.weekday()  # 0 = Monday, 6 = Sunday
        
        # Peak times: 7-10am, 12-1pm, 4-7pm on weekdays
        if weekday < 5:  # Weekday
            if (7 <= hour < 10) or (12 <= hour < 13) or (16 <= hour < 19):
                return 1.25
            elif (10 <= hour < 12) or (13 <= hour < 16) or (hour >= 19):
                return 1.0
        else:  # Weekend
            if 10 <= hour < 23:
                return 1.15
        
        return 1.0
    
    def get_applicable_discounts(self, customer_data: Dict) -> Dict:
        """
        Determine applicable discounts for a customer
        
        Args:
            customer_data: Customer profile information
            
        Returns:
            Dict with applicable discounts
        """
        
        discounts = {
            "loyalty_discount": 0.0,
            "bulk_discount": 0.0,
            "promotional_discount": 0.0,
            "total_discount_percent": 0.0
        }
        
        # Loyalty discount for repeat customers
        total_bookings = customer_data.get("total_bookings", 0)
        if total_bookings >= 10:
            discounts["loyalty_discount"] = 0.10  # 10% for 10+ bookings
        elif total_bookings >= 5:
            discounts["loyalty_discount"] = 0.05  # 5% for 5+ bookings
        
        # VIP customer bonus
        if customer_data.get("is_vip"):
            discounts["loyalty_discount"] = max(0.15, discounts["loyalty_discount"])
        
        # Bulk booking discount (multiple riders or frequent bookings)
        if customer_data.get("total_spent", 0) > 1000:
            discounts["bulk_discount"] = 0.05  # 5% for $1000+ spent
        
        # Calculate total
        discounts["total_discount_percent"] = min(
            discounts["loyalty_discount"] + discounts["bulk_discount"],
            0.20  # Cap at 20% total discount
        )
        
        return discounts
    
    def apply_promotional_code(self, code: str) -> Dict:
        """
        Validate and apply promotional code
        
        In production, this would check against a promotions database
        """
        
        # Example promotional codes
        promotions = {
            "WELCOME10": {"discount": 0.10, "description": "10% off first ride"},
            "LUXURY20": {"discount": 0.20, "description": "20% off luxury rides"},
            "SUMMERSALE": {"discount": 0.15, "description": "15% off summer rides"},
        }
        
        if code.upper() in promotions:
            return {
                "valid": True,
                "code": code.upper(),
                **promotions[code.upper()]
            }
        
        return {
            "valid": False,
            "code": code.upper(),
            "error": "Invalid promotional code"
        }
    
    def format_quote(self, fare_breakdown: Dict, customer_name: str = "Valued Customer") -> str:
        """
        Format fare breakdown as a professional quote
        
        Returns:
            Formatted quote string
        """
        
        quote = f"""
═══════════════════════════════════════
    BLU ROYAL RIDES - PRICE QUOTE
═══════════════════════════════════════

Service Tier:           {fare_breakdown['service_tier'].upper()}
Distance:              {fare_breakdown['distance_miles']} miles @ ${fare_breakdown['distance_charge']/fare_breakdown['distance_miles']:.2f}/mi
Ride Duration:         {fare_breakdown['duration_minutes']:.0f} minutes @ ${fare_breakdown['duration_charge']/fare_breakdown['duration_minutes']:.2f}/min

─────────────────────────────────────────
Base Fare:             ${fare_breakdown['base_fare']:>8.2f}
Distance Charge:       ${fare_breakdown['distance_charge']:>8.2f}
Duration Charge:       ${fare_breakdown['duration_charge']:>8.2f}
─────────────────────────────────────────
Subtotal:              ${fare_breakdown['subtotal']:>8.2f}
Tax ({fare_breakdown['tax_rate']*100:.0f}%):                ${fare_breakdown['tax']:>8.2f}
═════════════════════════════════════════
TOTAL FARE:            ${fare_breakdown['total']:>8.2f}
═════════════════════════════════════════

All prices in {fare_breakdown['currency']}
Thank you for choosing Blu Royal Rides!
"""
        
        return quote
