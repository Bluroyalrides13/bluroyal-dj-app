"""
Quick Start Examples for Luxury Ride Share Agent

Run this file to test core functionality:
    python examples.py
"""

import asyncio
from datetime import datetime, timedelta

from src.agent.chat_interface import ChatInterface
from src.agent.booking_manager import BookingManager
from src.agent.pricing_engine import PricingEngine
from src.agent.lead_qualifier import LeadQualifier
from src.models.schemas import ChatMessage, BookingRequest


def example_chat_conversation():
    """Example: Multi-turn conversation and lead qualification"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Chat Conversation & Lead Qualification")
    print("="*60)
    
    chat = ChatInterface()
    
    # Simulate a conversation
    messages = [
        "Hi, I'm interested in luxury rides for my business trips",
        "I'm based in New York City and need regular pickups",
        "I travel about 3-4 times per week to meetings",
        "Premium service would be perfect for my needs"
    ]
    
    for user_msg in messages:
        msg = ChatMessage(message=user_msg)
        response = chat.process_message(msg)
        
        print(f"\nCustomer: {user_msg}")
        print(f"Agent: {response.response}")
        print(f"Lead Score: {response.lead_score}")
        print(f"State: {response.conversation_state}")
        if response.extracted_data:
            print(f"Extracted: {response.extracted_data}")


def example_pricing():
    """Example: Generate pricing quotes"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Pricing & Quote Generation")
    print("="*60)
    
    pricing = PricingEngine()
    
    # NYC to JFK Airport
    fare = pricing.calculate_fare(
        distance=15.0,
        duration=35.0,
        service_tier="premier"
    )
    
    print("\nRoute: NYC to JFK Airport")
    print(f"Service Tier: {fare['service_tier'].upper()}")
    print(f"Distance: {fare['distance_miles']} miles @ ${fare['distance_charge']/fare['distance_miles']:.2f}/mi")
    print(f"Duration: {fare['duration_minutes']:.0f} minutes")
    print(f"\nBreakdown:")
    print(f"  Base Fare:      ${fare['base_fare']:>8.2f}")
    print(f"  Distance:       ${fare['distance_charge']:>8.2f}")
    print(f"  Duration:       ${fare['duration_charge']:>8.2f}")
    print(f"  Subtotal:       ${fare['subtotal']:>8.2f}")
    print(f"  Tax (8%):       ${fare['tax']:>8.2f}")
    print(f"  ───────────────────────────")
    print(f"  TOTAL:          ${fare['total']:>8.2f}")
    
    # Show different service tiers
    print("\n\nComparison Across Service Tiers:")
    for tier in ["executive", "premier", "vip"]:
        fare = pricing.calculate_fare(15.0, 35.0, tier)
        print(f"{tier.upper():12} → ${fare['total']:>7.2f}")
    
    # Peak pricing
    print("\n\nPeak Pricing Example:")
    normal_fare = pricing.calculate_fare(10.0, 20.0, "premier", peak_factor=1.0)
    peak_fare = pricing.calculate_fare(10.0, 20.0, "premier", peak_factor=1.25)
    print(f"Normal time: ${normal_fare['total']:.2f}")
    print(f"Peak time:   ${peak_fare['total']:.2f} (1.25x multiplier)")


def example_lead_scoring():
    """Example: Lead qualification with different conversation patterns"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Lead Qualification Scoring")
    print("="*60)
    
    qualifier = LeadQualifier()
    
    # High-quality lead conversation
    high_quality = [
        {"role": "user", "content": "I need premium transportation for executive clients"},
        {"role": "assistant", "content": "We'd be happy to help!"},
        {"role": "user", "content": "We need reliable service multiple times per week"},
        {"role": "assistant", "content": "Our VIP tier might be perfect"},
        {"role": "user", "content": "Budget isn't a concern, quality and reliability are"},
        {"role": "assistant", "content": "Excellent!"},
    ]
    
    scores = qualifier.qualify_lead(high_quality)
    overall = scores.get("overall_score", 0)
    
    print("\nHigh-Quality Lead Conversation:")
    print(f"  Budget Score:     {scores.get('budget_score', 0):.0f}/100")
    print(f"  Frequency Score:  {scores.get('frequency_score', 0):.0f}/100")
    print(f"  Location Score:   {scores.get('location_score', 0):.0f}/100")
    print(f"  Engagement Score: {scores.get('engagement_score', 0):.0f}/100")
    print(f"  ─────────────────────────")
    print(f"  Overall Score:    {overall:.0f}/100")
    
    recommendation = qualifier.get_recommendation(scores)
    print(f"\nRecommendation: {recommendation['message']}")
    print(f"Status: {recommendation['status'].upper()}")
    print(f"Suggested Tier: {recommendation['suggested_tier'].upper()}")


def example_booking():
    """Example: Create a booking and generate quote"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Booking Management")
    print("="*60)
    
    manager = BookingManager()
    
    # Create a booking request
    booking_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    booking_time = "14:00"
    
    try:
        request = BookingRequest(
            customer_id="cust_example_001",
            pickup_location="New York City, NY",
            dropoff_location="JFK Airport",
            booking_date=booking_date,
            booking_time=booking_time,
            passenger_count=2,
            service_tier="premier",
            contact_email="example@business.com"
        )
        
        booking, quote = manager.create_booking(request)
        
        print(f"\n✓ Booking Created Successfully")
        print(f"  Booking ID:         {booking.id}")
        print(f"  Confirmation #:     {booking.confirmation_number}")
        print(f"  Route:              {booking.pickup_location} → {booking.dropoff_location}")
        print(f"  Date/Time:          {booking.booking_date} at {booking.booking_time}")
        print(f"  Service Tier:       {booking.service_tier.upper()}")
        print(f"  Passengers:         {booking.passenger_count}")
        print(f"\nQuote:")
        print(f"  Distance:           {quote.estimated_distance_miles} miles")
        print(f"  Duration:           {quote.estimated_duration_minutes:.0f} minutes")
        print(f"  Base Fare:          ${quote.base_fare:.2f}")
        print(f"  Distance Charge:    ${quote.distance_charge:.2f}")
        print(f"  Duration Charge:    ${quote.duration_charge:.2f}")
        print(f"  Subtotal:           ${quote.subtotal:.2f}")
        print(f"  Tax:                ${quote.tax:.2f}")
        print(f"  Total Fare:         ${quote.total_fare:.2f}")
        print(f"  Quote Valid Until:  {quote.valid_until.isoformat()}")
        
    except ValueError as e:
        print(f"✗ Booking Error: {e}")
        print("(This is expected if booking time is not sufficiently in the future)")


def example_discounts():
    """Example: Discount calculations"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Loyalty Discounts & Promotions")
    print("="*60)
    
    pricing = PricingEngine()
    
    # Loyal customer
    loyal_customer = {
        "total_bookings": 12,
        "total_spent": 1500,
        "is_vip": False
    }
    
    discounts = pricing.get_applicable_discounts(loyal_customer)
    print("\nLoyal Customer (12+ bookings, $1500+ spent):")
    print(f"  Loyalty Discount:    {discounts['loyalty_discount']*100:.0f}%")
    print(f"  Bulk Discount:       {discounts['bulk_discount']*100:.0f}%")
    print(f"  Total Discount:      {discounts['total_discount_percent']*100:.0f}%")
    
    # VIP customer
    vip_customer = {
        "total_bookings": 50,
        "total_spent": 5000,
        "is_vip": True
    }
    
    discounts = pricing.get_applicable_discounts(vip_customer)
    print("\nVIP Customer (50+ bookings, $5000+ spent):")
    print(f"  Loyalty Discount:    {discounts['loyalty_discount']*100:.0f}%")
    print(f"  Bulk Discount:       {discounts['bulk_discount']*100:.0f}%")
    print(f"  Total Discount:      {discounts['total_discount_percent']*100:.0f}%")
    
    # Promo codes
    print("\nPromo Code Examples:")
    for code in ["WELCOME10", "LUXURY20", "SUMMERSALE", "INVALID"]:
        result = pricing.apply_promotional_code(code)
        status = "✓" if result["valid"] else "✗"
        if result["valid"]:
            print(f"  {status} {code:15} → {result['discount']*100:.0f}% off ({result['description']})")
        else:
            print(f"  {status} {code:15} → Invalid")


def main():
    """Run all examples"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Luxury Ride Share Agent - Examples".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        example_chat_conversation()
        example_pricing()
        example_lead_scoring()
        example_booking()
        example_discounts()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
