"""
FastAPI REST Routes
Main endpoints for chat, bookings, quotes, and webhooks
"""

import logging
import uuid
import smtplib
from email.message import EmailMessage
from pathlib import Path
from fastapi import APIRouter, HTTPException, Header, Request, Form
from fastapi.responses import FileResponse, RedirectResponse
from typing import List, Optional

from src.models.schemas import (
    ChatMessage, BookingRequest, ChatResponse, ApiResponse,
    InfoProductApplicationRequest,
)
from src.agent.chat_interface import ChatInterface
from src.agent.booking_manager import BookingManager
from src.agent.pricing_engine import PricingEngine
from src.integrations.wix_connector import WixConnector, WixWebhookHandler
from src.marketing.funnel import InfoProductFunnel
from src.dj_tools.engine import (
    build_event_timeline,
    get_questionnaire_template,
    save_questionnaire_answers,
    build_setlist,
    calculate_booking_price,
    generate_content_pack,
    generate_lesson_plan,
    get_dj_profile_template,
    save_dj_profile,
    get_lead_crm_template,
    save_lead_crm_record,
    get_service_agreement_template,
    save_service_agreement_pack,
    save_sales_event,
    get_sales_tracker,
    get_admin_stats,
)
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
funnel = InfoProductFunnel()
STATIC_DIR = Path(__file__).resolve().parents[2] / "static"


def _send_multitasking360_notification(lead_payload: dict, record_id: str) -> bool:
    """Send email notification for a new MultiTasking360 application."""
    recipient = settings.SMTP_TO_EMAIL or settings.SUPPORT_EMAIL
    sender = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    if not (settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD and recipient and sender):
        logger.info("SMTP not configured; skipping application email notification")
        return False

    subject = f"New MultiTasking360 Application: {lead_payload.get('name', 'Unknown')}"
    body_lines = ["A new MultiTasking360 application was submitted.", "", f"Record ID: {record_id}"]
    for key, value in lead_payload.items():
        if value in (None, "", []):
            continue
        label = key.replace("_", " ").title()
        body_lines.append(f"{label}: {value}")
    body = "\n".join(body_lines) + "\n"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        if settings.SMTP_USE_TLS:
            smtp.starttls()
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(msg)
    return True


def _is_dashboard_authenticated(request: Request) -> bool:
    return request.cookies.get("dj_dashboard_auth") == "1"


def _require_dashboard_auth(request: Request):
    if not _is_dashboard_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")


def _is_academy_authenticated(request: Request) -> bool:
    return request.cookies.get("academy_app_auth") == "1"


def _require_academy_auth(request: Request):
    if not _is_academy_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")


# ===================== DJ Dashboard UI =====================

@router.get("/dashboard/login", include_in_schema=False)
async def dashboard_login_page():
    """Serve dashboard login page"""
    return FileResponse(STATIC_DIR / "dashboard-login.html")


@router.post("/dashboard/login", include_in_schema=False)
async def dashboard_login(username: str = Form(...), password: str = Form(...)):
    """Authenticate dashboard access"""
    if username != settings.DASHBOARD_USERNAME or password != settings.DASHBOARD_PASSWORD:
        return RedirectResponse(url="/dashboard/login?error=1", status_code=303)

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="dj_dashboard_auth",
        value="1",
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/dashboard/logout", include_in_schema=False)
async def dashboard_logout():
    """Log out dashboard session"""
    response = RedirectResponse(url="/dashboard/login", status_code=303)
    response.delete_cookie("dj_dashboard_auth")
    return response


@router.get("/dashboard", include_in_schema=False)
async def dashboard_page(request: Request):
    """Serve the DJ Business Engine dashboard"""
    if not _is_dashboard_authenticated(request):
        return RedirectResponse(url="/dashboard/login", status_code=303)
    return FileResponse(STATIC_DIR / "dashboard.html")


@router.get("/dashboard/sales", include_in_schema=False)
async def sales_dashboard_page(request: Request):
    """Serve the private Sales dashboard (owner-only)."""
    if not _is_dashboard_authenticated(request):
        return RedirectResponse(url="/dashboard/login", status_code=303)
    return FileResponse(STATIC_DIR / "sales-dashboard.html")


# ===================== Academy App UI =====================

@router.get("/academy/login", include_in_schema=False)
async def academy_login_page():
    """Serve academy app login page"""
    return FileResponse(STATIC_DIR / "academy-login.html")


@router.post("/academy/login", include_in_schema=False)
async def academy_login(username: str = Form(...), password: str = Form(...)):
    """Authenticate academy app access"""
    if username != settings.ACADEMY_APP_USERNAME or password != settings.ACADEMY_APP_PASSWORD:
        return RedirectResponse(url="/academy/login?error=1", status_code=303)

    response = RedirectResponse(url="/academy", status_code=303)
    response.set_cookie(
        key="academy_app_auth",
        value="1",
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/academy/logout", include_in_schema=False)
async def academy_logout():
    """Log out academy app session"""
    response = RedirectResponse(url="/academy/login", status_code=303)
    response.delete_cookie("academy_app_auth")
    return response


@router.get("/academy", include_in_schema=False)
async def academy_page(request: Request):
    """Serve the standalone academy app dashboard"""
    if not _is_academy_authenticated(request):
        return RedirectResponse(url="/academy/login", status_code=303)
    return FileResponse(STATIC_DIR / "academy-dashboard.html")


# ===================== DJ Tool Endpoints =====================

@router.post("/api/tools/timeline")
async def create_timeline(request: Request):
    """Build an event run-of-show timeline"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = build_event_timeline(
            event_type=body.get("event_type", "general_party"),
            start_time=body.get("start_time", "18:00"),
            event_date=body.get("event_date", ""),
            venue=body.get("venue", ""),
            notes=body.get("notes", ""),
        )
        return ApiResponse(success=True, message="Timeline created", data=result)
    except Exception as e:
        logger.error(f"Timeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/tools/questionnaire/{event_type}")
async def get_questionnaire(event_type: str, request: Request):
    """Return the client questionnaire for a given event type"""
    _require_dashboard_auth(request)
    try:
        result = get_questionnaire_template(event_type)
        return ApiResponse(success=True, message="Questionnaire ready", data=result)
    except Exception as e:
        logger.error(f"Questionnaire error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/questionnaire/submit")
async def submit_questionnaire(request: Request):
    """Save a completed client questionnaire"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = save_questionnaire_answers(
            portal_id=body.get("portal_id", str(uuid.uuid4())),
            event_type=body.get("event_type", "general_party"),
            answers=body.get("answers", {}),
        )
        return ApiResponse(success=True, message="Questionnaire saved", data=result)
    except Exception as e:
        logger.error(f"Questionnaire submit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/setlist")
async def create_setlist(request: Request):
    """Build an organized setlist by moment"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = build_setlist(
            moments=body.get("moments"),
            songs=body.get("songs", []),
        )
        return ApiResponse(success=True, message="Setlist created", data=result)
    except Exception as e:
        logger.error(f"Setlist error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/pricing")
async def get_booking_price(request: Request):
    """Calculate a full DJ booking quote"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = calculate_booking_price(
            event_type=body.get("event_type", "general_party"),
            hours=float(body.get("hours", 4)),
            add_ons=body.get("add_ons", []),
            travel_hours=float(body.get("travel_hours", 0)),
            discount_percent=float(body.get("discount_percent", 0)),
        )
        return ApiResponse(success=True, message="Quote generated", data=result)
    except Exception as e:
        logger.error(f"Pricing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/content-pack")
async def create_content_pack(request: Request):
    """Generate a 30-day Instagram content pack"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = generate_content_pack(
            years_experience=int(body.get("years_experience", 5)),
            specialty=body.get("specialty", "general_party"),
            cta=body.get("cta", "Link in bio to apply."),
        )
        return ApiResponse(success=True, message="Content pack ready", data=result)
    except Exception as e:
        logger.error(f"Content pack error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/lesson-plan")
async def create_lesson_plan(request: Request):
    """Generate a structured multi-week lesson plan with printable resource suggestions"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = generate_lesson_plan(
            theme=body.get("theme", "Seasonal Learning"),
            audience_type=body.get("audience_type", "preschool"),
            duration_weeks=int(body.get("duration_weeks", 4)),
            focus_area=body.get("focus_area", "mixed"),
            session_length_minutes=int(body.get("session_length_minutes", 45)),
            language_mode=body.get("language_mode", "english"),
            include_printables=bool(body.get("include_printables", True)),
        )
        return ApiResponse(success=True, message="Lesson plan ready", data=result)
    except Exception as e:
        logger.error(f"Lesson plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/academy/lesson-plan")
async def create_academy_lesson_plan(request: Request):
    """Generate lesson plans for the standalone academy app"""
    _require_academy_auth(request)
    try:
        body = await request.json()
        result = generate_lesson_plan(
            theme=body.get("theme", "Seasonal Learning"),
            audience_type=body.get("audience_type", "preschool"),
            duration_weeks=int(body.get("duration_weeks", 4)),
            focus_area=body.get("focus_area", "mixed"),
            session_length_minutes=int(body.get("session_length_minutes", 45)),
            language_mode=body.get("language_mode", "english"),
            include_printables=bool(body.get("include_printables", True)),
        )
        return ApiResponse(success=True, message="Academy lesson plan ready", data=result)
    except Exception as e:
        logger.error(f"Academy lesson plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/tools/dj-profile/template")
async def get_dj_profile_setup(request: Request):
    """Return the DJ profile setup template"""
    _require_dashboard_auth(request)
    try:
        result = get_dj_profile_template()
        return ApiResponse(success=True, message="DJ profile template ready", data=result)
    except Exception as e:
        logger.error(f"DJ profile template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/dj-profile/submit")
async def submit_dj_profile(request: Request):
    """Save a completed DJ profile setup"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = save_dj_profile(
            profile_id=body.get("profile_id", str(uuid.uuid4())),
            profile=body.get("profile", {}),
        )
        return ApiResponse(success=True, message="DJ profile saved", data=result)
    except Exception as e:
        logger.error(f"DJ profile submit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/tools/lead-crm/template")
async def get_lead_crm_setup(request: Request):
    """Return the lead CRM template"""
    _require_dashboard_auth(request)
    try:
        result = get_lead_crm_template()
        return ApiResponse(success=True, message="Lead CRM template ready", data=result)
    except Exception as e:
        logger.error(f"Lead CRM template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/lead-crm/submit")
async def submit_lead_crm(request: Request):
    """Save a lead CRM record"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = save_lead_crm_record(
            lead_id=body.get("lead_id", str(uuid.uuid4())),
            lead=body.get("lead", {}),
        )
        return ApiResponse(success=True, message="Lead CRM record saved", data=result)
    except Exception as e:
        logger.error(f"Lead CRM submit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/tools/service-agreement/template")
async def get_service_agreement_setup(request: Request):
    """Return the service agreement forms template"""
    _require_dashboard_auth(request)
    try:
        result = get_service_agreement_template()
        return ApiResponse(success=True, message="Service agreement template ready", data=result)
    except Exception as e:
        logger.error(f"Service agreement template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tools/service-agreement/submit")
async def submit_service_agreement(request: Request):
    """Save a full service agreement forms pack"""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        result = save_service_agreement_pack(
            agreement_id=body.get("agreement_id", str(uuid.uuid4())),
            agreement_pack=body.get("agreement_pack", {}),
        )
        return ApiResponse(success=True, message="Service agreement pack saved", data=result)
    except Exception as e:
        logger.error(f"Service agreement submit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", include_in_schema=False)
async def home_page():
    """Serve the DJ Blu Bloods sales page"""
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/apply", include_in_schema=False)
async def apply_page():
    """Serve the same sales page with the application form in view"""
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/multitasking360", include_in_schema=False)
async def multitasking360_page():
    """Serve the standalone MultiTasking360 landing page."""
    return FileResponse(STATIC_DIR / "multitasking360.html")


@router.get("/multitasking360/apply", include_in_schema=False)
async def multitasking360_apply_page():
    """Serve MultiTasking360 page with the apply section available."""
    return FileResponse(STATIC_DIR / "multitasking360.html")


@router.get("/multitasking360/editorial", include_in_schema=False)
async def multitasking360_editorial_page():
    """Serve the Ultra-Luxury Editorial design variant."""
    return FileResponse(STATIC_DIR / "multitasking360-editorial.html")


@router.get("/multitasking360/corporate", include_in_schema=False)
async def multitasking360_corporate_page():
    """Serve the Corporate Premium design variant."""
    return FileResponse(STATIC_DIR / "multitasking360-corporate.html")


@router.get("/api/offers")
async def get_offer_catalog():
    """Return the offer stack for the info product funnel"""
    return ApiResponse(
        success=True,
        message="Offer catalog retrieved",
        data={"offers": funnel.get_offer_catalog()},
    )


@router.get("/api/offers/{offer_slug}/downloads")
async def get_offer_downloads(offer_slug: str):
    """Return downloadable files for a specific offer tier."""
    downloads = funnel.get_tier_downloads(offer_slug)
    if not downloads:
        raise HTTPException(status_code=404, detail="No downloadable bundle configured for this offer tier")

    return ApiResponse(
        success=True,
        message="Offer downloads retrieved",
        data={"offer_slug": offer_slug, "downloads": downloads},
    )


@router.get("/api/tools/sales-tracker")
async def sales_tracker(request: Request):
    """Return sales tracker metrics for dashboard."""
    _require_dashboard_auth(request)
    try:
        data = get_sales_tracker()
        return ApiResponse(success=True, message="Sales tracker loaded", data=data)
    except Exception as e:
        logger.error(f"Sales tracker read error: {e}")
        raise HTTPException(status_code=500, detail="Error loading sales tracker")


@router.post("/api/tools/sales-tracker")
async def update_sales_tracker(request: Request):
    """Record sales events (click or sold) for offer tiers."""
    _require_dashboard_auth(request)
    try:
        body = await request.json()
        data = save_sales_event(
            {
                "offer_slug": body.get("offer_slug"),
                "price": body.get("price", 0),
                "event_type": body.get("event_type", "click"),
            }
        )
        return ApiResponse(success=True, message="Sales tracker updated", data=data)
    except Exception as e:
        logger.error(f"Sales tracker update error: {e}")
        raise HTTPException(status_code=500, detail="Error updating sales tracker")


@router.post("/api/applications")
async def submit_application(application: InfoProductApplicationRequest):
    """Capture a lead and score it for the right high-ticket offer"""
    try:
        result = funnel.process_application(application)
        lead_payload = {
            "source": "multitasking360_site",
            "name": application.name,
            "email": application.email,
            "instagram_handle": application.instagram_handle,
            "audience_size": application.audience_size,
            "monthly_revenue": application.monthly_revenue,
            "biggest_goal": application.biggest_goal,
            "biggest_block": application.biggest_block,
            "budget_range": application.budget_range,
            "interested_offer": application.interested_offer,
        }

        notification_sent = False
        try:
            notification_sent = _send_multitasking360_notification(
                lead_payload=lead_payload,
                record_id=result.get("application_id", ""),
            )
        except Exception as notify_err:
            logger.error(f"Application saved but email notification failed: {notify_err}")

        return ApiResponse(
            success=True,
            message="Application captured",
            data={
                **result,
                "notification_sent": notification_sent,
            },
        )
    except Exception as e:
        logger.error(f"Error capturing application: {e}")
        raise HTTPException(status_code=500, detail="Error capturing application")


@router.post("/api/multitasking360/applications")
async def submit_multitasking360_application(request: Request):
    """Capture public MultiTasking360 applications from the standalone site."""
    # deploy-marker: multitasking360-email-endpoint
    try:
        body = await request.json()
        full_name = f"{(body.get('first_name') or '').strip()} {(body.get('last_name') or '').strip()}".strip()
        if not full_name:
            full_name = (body.get("name") or "").strip()

        email = (body.get("email") or "").strip()
        if not full_name or not email:
            raise HTTPException(status_code=400, detail="Name and email are required")

        lead_payload = {
            "source": "multitasking360_site",
            "name": full_name,
            "email": email,
            "phone": (body.get("phone") or "").strip(),
            "industry": (body.get("industry") or "").strip(),
            "program": (body.get("program") or "").strip(),
            "goal": (body.get("goal") or "").strip(),
        }

        result = save_lead_crm_record(
            lead_id=body.get("lead_id", str(uuid.uuid4())),
            lead=lead_payload,
        )

        notification_sent = False
        try:
            notification_sent = _send_multitasking360_notification(
                lead_payload=lead_payload,
                record_id=result.get("record_id", ""),
            )
        except Exception as notify_err:
            logger.error(f"Application saved but email notification failed: {notify_err}")

        return ApiResponse(
            success=True,
            message="Application captured",
            data={
                **result,
                "notification_sent": notification_sent,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error capturing MultiTasking360 application: {e}")
        raise HTTPException(status_code=500, detail="Error capturing application")


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

@router.get("/api/admin/stats")
async def admin_dashboard_stats(request: Request):
    """Aggregated stats for the admin dashboard."""
    _require_dashboard_auth(request)
    try:
        stats = get_admin_stats()
        return ApiResponse(success=True, message="Admin stats loaded", data=stats)
    except Exception as e:
        logger.error(f"Error loading admin stats: {e}")
        raise HTTPException(status_code=500, detail="Error loading admin stats")


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
