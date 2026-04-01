"""
Data models and schemas for the Luxury Ride Share Agent
Defines database models and Pydantic schemas for API validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class ServiceTierEnum(str, Enum):
    """Available service tiers"""
    EXECUTIVE = "executive"
    PREMIER = "premier"
    VIP = "vip"


class BookingStatusEnum(str, Enum):
    """Booking status states"""
    QUOTED = "quoted"
    CONFIRMED = "confirmed"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LeadStatusEnum(str, Enum):
    """Lead qualification status"""
    NEW = "new"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"
    CLOSED = "closed"


# ===================== Request/Response Schemas =====================

class ChatMessage(BaseModel):
    """Chat message from client"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: Optional[str] = None


class ChatResponse(BaseModel):
    """Agent response to chat message"""
    response: str
    session_id: str
    extracted_data: Optional[dict] = None
    lead_score: Optional[float] = None
    conversation_state: str  # "greeting", "qualifying", "booking", "payment_ready"


class CustomerProfile(BaseModel):
    """Customer profile information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    phone: str
    preferred_service_tier: ServiceTierEnum
    total_bookings: int = 0
    total_spent: float = 0.0
    average_rating: Optional[float] = None
    is_vip: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BookingRequest(BaseModel):
    """Booking request from customer"""
    customer_id: str
    pickup_location: str
    dropoff_location: str
    booking_date: str  # ISO format: YYYY-MM-DD
    booking_time: str  # HH:MM format
    passenger_count: int = Field(ge=1, le=6)
    service_tier: ServiceTierEnum
    special_requests: Optional[str] = None
    contact_email: EmailStr


class BookingQuote(BaseModel):
    """Price quote for a booking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    service_tier: ServiceTierEnum
    base_fare: float
    estimated_distance_miles: float
    distance_charge: float
    estimated_duration_minutes: float
    duration_charge: float
    subtotal: float
    tax_rate: float
    tax: float
    total_fare: float
    currency: str = "USD"
    valid_until: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Booking(BaseModel):
    """Complete booking record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_email: EmailStr
    customer_phone: str
    pickup_location: str
    dropoff_location: str
    booking_date: str
    booking_time: str
    passenger_count: int
    service_tier: ServiceTierEnum
    special_requests: Optional[str] = None
    quote: BookingQuote
    status: BookingStatusEnum = BookingStatusEnum.QUOTED
    payment_id: Optional[str] = None
    confirmation_number: str = Field(default_factory=lambda: f"BRR-{uuid.uuid4().hex[:8].upper()}")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Lead(BaseModel):
    """Lead record with qualification score"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str  # "wix_chat", "web_chat", "phone", etc.
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    initial_message: str
    
    # Qualification factors
    budget_score: float = Field(ge=0, le=100)
    frequency_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    preference_score: float = Field(ge=0, le=100)
    engagement_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)
    
    status: LeadStatusEnum = LeadStatusEnum.NEW
    conversation_summary: Optional[str] = None
    recommended_tier: Optional[ServiceTierEnum] = None
    next_steps: Optional[str] = None
    assigned_to: Optional[str] = None  # Sales rep or agent
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    converted_at: Optional[datetime] = None


class ConversationSession(BaseModel):
    """Conversation session tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lead_id: Optional[str] = None
    customer_id: Optional[str] = None
    source: str  # "wix_chat", "web_chat", "phone"
    messages: List[dict] = []  # Array of {role, content, timestamp}
    extracted_data: dict = {}  # Captured booking/customer data
    status: str = "active"  # active, completed, escalated
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None


class PaymentIntent(BaseModel):
    """Square payment intent"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    amount_cents: int  # Amount in cents
    currency: str = "USD"
    status: str = "pending"  # pending, processing, completed, failed
    payment_method: str  # "square", "apple_pay", "google_pay"
    square_payment_id: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WixWebhookPayload(BaseModel):
    """Wix webhook payload for chat events"""
    event_type: str  # "chat_message", "contact_created", etc.
    timestamp: str
    data: dict
    signature: Optional[str] = None


class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None
