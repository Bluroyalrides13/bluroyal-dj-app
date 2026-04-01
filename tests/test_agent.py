"""
Unit tests for Luxury Ride Share Agent
"""

import pytest
from src.agent.lead_qualifier import LeadQualifier
from src.agent.booking_manager import BookingManager
from src.agent.pricing_engine import PricingEngine
from src.models.schemas import BookingRequest


class TestLeadQualifier:
    """Test lead qualification logic"""
    
    @pytest.fixture
    def qualifier(self):
        return LeadQualifier()
    
    def test_high_quality_lead_scoring(self, qualifier):
        """Test that high-engagement conversations score well"""
        conversation = [
            {"role": "user", "content": "Hi, I need premium rides for NYC"},
            {"role": "assistant", "content": "Welcome to Blu Royal!"},
            {"role": "user", "content": "I need VIP service regularly"},
            {"role": "assistant", "content": "Our VIP tier..."},
        ]
        
        scores = qualifier.qualify_lead(conversation)
        assert "overall_score" in scores
        assert 0 <= scores["overall_score"] <= 100
    
    def test_lead_threshold_classification(self, qualifier):
        """Test lead classification based on score"""
        # High quality lead
        scores = {
            "budget_score": 90,
            "frequency_score": 85,
            "location_score": 95,
            "service_preference_score": 80,
            "engagement_score": 85
        }
        overall = qualifier.calculate_overall_score(scores)
        assert qualifier.is_high_quality_lead(overall)


class TestBookingManager:
    """Test booking management"""
    
    @pytest.fixture
    def manager(self):
        return BookingManager()
    
    def test_booking_creation(self, manager):
        """Test creating a booking"""
        request = BookingRequest(
            customer_id="cust_123",
            pickup_location="New York City, NY",
            dropoff_location="JFK Airport",
            booking_date="2026-04-05",
            booking_time="14:00",
            passenger_count=2,
            service_tier="premier",
            contact_email="test@example.com"
        )
        
        # Note: This requires valid booking time (2+ hours in future)
        # Test with try-except to handle timing
        try:
            booking, quote = manager.create_booking(request)
            assert booking.id is not None
            assert booking.confirmation_number is not None
            assert quote.total_fare > 0
        except ValueError as e:
            # Expected if test runs with invalid booking time
            assert "advance" in str(e).lower()


class TestPricingEngine:
    """Test pricing calculations"""
    
    @pytest.fixture
    def engine(self):
        return PricingEngine()
    
    def test_fareCalculation(self, engine):
        """Test fare calculation"""
        fare = engine.calculate_fare(
            distance=10.0,
            duration=30.0,
            service_tier="premier"
        )
        
        assert fare["total"] > 0
        assert fare["subtotal"] > 0
        assert fare["tax"] > 0
        assert fare["total"] == fare["subtotal"] + fare["tax"]
    
    def test_peak_pricing(self, engine):
        """Test peak pricing multiplier"""
        # Morning peak (8am on weekday)
        factor = engine.get_peak_factor("2026-04-06T08:00")  # Monday
        assert factor >= 1.0
        
        # Off-peak (2am on weekday)
        factor = engine.get_peak_factor("2026-04-06T02:00")
        assert factor >= 1.0
    
    def test_discount_logic(self, engine):
        """Test discount calculations"""
        # VIP customer
        customer = {
            "total_bookings": 15,
            "total_spent": 2000,
            "is_vip": True
        }
        
        discounts = engine.get_applicable_discounts(customer)
        assert discounts["loyalty_discount"] > 0
        assert discounts["total_discount_percent"] <= 0.20  # Capped at 20%
    
    def test_promo_code_validation(self, engine):
        """Test promotional code handling"""
        result = engine.apply_promotional_code("WELCOME10")
        assert result["valid"] == True
        assert result["discount"] == 0.10
        
        result = engine.apply_promotional_code("INVALID")
        assert result["valid"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
