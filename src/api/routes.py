"""
FastAPI REST Routes
Main endpoints for chat, bookings, quotes, and webhooks
"""

import logging
import uuid
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional

from src.models.schemas import (
    ChatMessage, BookingRequest, ChatResponse, ApiResponse
)
from src.agent.chat_interface import ChatInterface
from src.agent.booking_manager import BookingManager
from src.agent.pricing_engine import PricingEngine
from src.integrations.wix_connector import WixConnector, WixWebhookHandler
from config.settings import Settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize components
chat_interface = ChatInterface()
booking_manager = BookingManager()
pricing_engine = PricingEngine()
wix = WixConnector()
wix_handler = WixWebhookHandler(wix)
settings = Settings()


# ===================== Chat Endpoints =====================

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(message: ChatMessage):
    """
    Send a message to the chat agent
    
    Returns agent response with any extracted booking data
    """
    try:
        response = chat_interface.process_message(message)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = chat_interface.get_conversation_history(session_id)
        return ApiResponse(
            success=True,
            message="Chat history retrieved",
            data={"messages": history}
        )
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving history")


@router.post("/chat/end/{session_id}")
async def end_chat_session(session_id: str):
    """
    End a chat session and create lead if qualified
    """
    try:
        lead_id = chat_interface.end_conversation(session_id)
        return ApiResponse(
            success=True,
            message="Chat session ended",
            data={"lead_id": lead_id}
        )
    except Exception as e:
        logger.error(f"Error ending chat session: {e}")
        raise HTTPException(status_code=500, detail="Error ending session")


# ===================== Booking Endpoints =====================

@router.post("/bookings")
async def create_booking(request: BookingRequest):
    """
    Create a new ride booking
    
    Returns booking details and quote
    """
    try:
        booking, quote = booking_manager.create_booking(request)
        
        return ApiResponse(
            success=True,
            message="Booking created",
            data={
                "booking": booking.model_dump(),
                "quote": quote.model_dump()
            }
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=500, detail="Error creating booking")


@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Get booking details"""
    try:
        booking = booking_manager.db.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return ApiResponse(
            success=True,
            message="Booking retrieved",
            data={"booking": booking}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching booking: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving booking")


@router.post("/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: str, payment_id: Optional[str] = None):
    """Confirm a booking (after payment if required)"""
    try:
        booking = booking_manager.confirm_booking(booking_id, payment_id)
        return ApiResponse(
            success=True,
            message="Booking confirmed",
            data={"booking": booking}
        )
    except Exception as e:
        logger.error(f"Error confirming booking: {e}")
        raise HTTPException(status_code=500, detail="Error confirming booking")


@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: str, reason: Optional[str] = None):
    """Cancel a booking"""
    try:
        booking_manager.cancel_booking(booking_id, reason)
        return ApiResponse(
            success=True,
            message="Booking cancelled"
        )
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}")
        raise HTTPException(status_code=500, detail="Error cancelling booking")


# ===================== Quote/Pricing Endpoints =====================

@router.get("/quote")
async def get_quote(
    distance: float,
    duration: float,
    service_tier: str = "executive",
    peak_factor: Optional[float] = None
):
    """
    Get a pricing quote
    
    Query params:
        - distance: Distance in miles
        - duration: Duration in minutes
        - service_tier: executive, premier, or vip
        - peak_factor: Optional pricing multiplier
    """
    try:
        if peak_factor is None:
            peak_factor = 1.0
        
        fare = pricing_engine.calculate_fare(
            distance=distance,
            duration=duration,
            service_tier=service_tier,
            peak_factor=peak_factor
        )
        
        formatted_quote = pricing_engine.format_quote(fare)
        
        return ApiResponse(
            success=True,
            message="Quote generated",
            data={
                "fare": fare,
                "formatted_quote": formatted_quote
            }
        )
    except Exception as e:
        logger.error(f"Error generating quote: {e}")
        raise HTTPException(status_code=500, detail="Error generating quote")


# ===================== Wix Webhook Endpoints =====================

@router.post("/webhooks/wix/chat")
async def wix_chat_webhook(
    request: Request,
    x_wix_signature: str = Header(None)
):
    """
    Receive chat messages from Wix
    
    Verifies webhook signature and processes message
    """
    try:
        body = await request.body()
        
        # Verify signature
        if not wix.verify_webhook_signature(x_wix_signature, body.decode()):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        webhook_data = await request.json()
        result = wix_handler.handle_chat_message(webhook_data)
        
        if result.get("success"):
            # Process message through chat interface
            chat_msg = ChatMessage(
                message=result.get("message"),
                session_id=result.get("contact_id")
            )
            response = chat_interface.process_message(chat_msg)
            
            # Send response back to Wix contact
            wix.send_chat_message(result.get("contact_id"), response.response)
        
        return ApiResponse(success=True, message="Webhook processed")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Wix chat webhook: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


@router.post("/webhooks/wix/contact")
async def wix_contact_webhook(request: Request, x_wix_signature: str = Header(None)):
    """
    Receive contact events from Wix
    
    Handles new contact creation, updates, etc.
    """
    try:
        body = await request.body()
        
        # Verify signature
        if not wix.verify_webhook_signature(x_wix_signature, body.decode()):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        webhook_data = await request.json()
        result = wix_handler.handle_contact_created(webhook_data)
        
        return ApiResponse(success=True, message="Contact webhook processed")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Wix contact webhook: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


# ===================== Payment Endpoints =====================

@router.post("/payments")
async def create_payment(
    booking_id: str,
    amount_cents: int,
    payment_method: str
):
    """
    Create a payment for a booking
    
    Currently supports Square payment processing
    """
    try:
        from src.integrations.square_payments import SquarePaymentProcessor
        processor = SquarePaymentProcessor()
        
        # In production, would use actual payment source from client
        # For now, this is a placeholder
        
        return ApiResponse(
            success=True,
            message="Payment endpoint ready",
            data={"status": "awaiting_implementation"}
        )
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=500, detail="Error creating payment")


# ===================== Health/Status Endpoints =====================

@router.get("/status")
async def api_status():
    """Get API status"""
    return ApiResponse(
        success=True,
        message="API is operational",
        data={
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "claude_model": settings.CLAUDE_MODEL
        }
    )
