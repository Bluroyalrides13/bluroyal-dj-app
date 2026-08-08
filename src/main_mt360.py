"""Standalone MultiTasking360 app entrypoint.

This app serves only the MultiTasking360 pages and related application endpoint,
so it can be deployed independently from the DJ dashboard service.
"""

import logging
from pathlib import Path

import stripe
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import uvicorn

from config.settings import Settings
from src.integrations.email_notify import (
    send_applicant_confirmation,
    send_application_notification,
    send_checkout_failure_alert,
    send_vault_delivery_email,
)
from src.integrations.stripe_payments import StripePaymentProcessor
from src.integrations.vault_tokens import make_download_token, read_download_token
from src.marketing.funnel import InfoProductFunnel
from src.marketing.mt360_offers import MT360_OFFER_PRICING
from src.marketing.mt360_vault_products import MT360_VAULT_PRODUCTS
from src.models.schemas import (
    ApiResponse,
    InfoProductApplicationRequest,
    StripeCheckoutRequest,
)


class VaultCheckoutRequest(BaseModel):
    """Body for /api/vault/checkout — a buy click from the shop page."""

    slug: str
    customer_email: EmailStr | None = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = Settings()
funnel = InfoProductFunnel()
stripe_processor = StripePaymentProcessor()
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="MultiTasking360 Standalone",
    description="Standalone MultiTasking360 sales experience",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def log_storage_location():
    """Log where applications are stored and how many exist.

    SQLite on Render is wiped every deploy unless the file sits on a mounted
    disk. Printing the path and the row count at boot makes it obvious from
    the logs whether persistence is actually working: the count should hold
    across a redeploy, not reset to zero. Count only — no applicant data.
    """
    try:
        db_path = funnel.db.db_path
        count = funnel.db.count_info_product_applications()
        persisted = db_path.startswith("/var/data")
        logger.info(
            "Storage check -> db_path=%s applications=%d persisted_disk=%s",
            db_path,
            count,
            persisted,
        )
        if not persisted:
            logger.warning(
                "Applications are on ephemeral storage and will be lost on the "
                "next deploy. Set DATABASE_URL=sqlite:////var/data/mt360.db"
            )
    except Exception as exc:  # pragma: no cover - diagnostics must never block boot
        logger.error("Storage check failed: %s", exc)


@app.get("/", include_in_schema=False)
async def home_page():
    """Serve the primary MultiTasking360 page as root."""
    return FileResponse(STATIC_DIR / "multitasking360.html")


@app.get("/multitasking360", include_in_schema=False)
async def multitasking360_page():
    """Serve the primary MultiTasking360 page."""
    return FileResponse(STATIC_DIR / "multitasking360.html")


@app.get("/multitasking360/editorial", include_in_schema=False)
async def multitasking360_editorial_page():
    """Serve editorial variant."""
    return FileResponse(STATIC_DIR / "multitasking360-editorial.html")


@app.get("/multitasking360/corporate", include_in_schema=False)
async def multitasking360_corporate_page():
    """Serve corporate variant."""
    return FileResponse(STATIC_DIR / "multitasking360-corporate.html")


# Clean, brand-neutral aliases. The /multitasking360 paths above stay because
# Stripe checkout returns to them, but these are what we link publicly.
@app.get("/editorial", include_in_schema=False)
async def editorial_page():
    """Serve editorial variant at a clean path."""
    return FileResponse(STATIC_DIR / "multitasking360-editorial.html")


@app.get("/corporate", include_in_schema=False)
async def corporate_page():
    """Serve corporate variant at a clean path."""
    return FileResponse(STATIC_DIR / "multitasking360-corporate.html")


@app.get("/hidden-income-finder", include_in_schema=False)
async def hidden_income_finder_page():
    """Serve Hidden Income Finder page."""
    return FileResponse(STATIC_DIR / "hidden-income-finder.html")


@app.post("/api/applications")
async def submit_application(request: Request):
    """Capture MT360 applications from the standalone page form."""
    try:
        body = await request.json()

        first_name = (body.get("first_name") or "").strip()
        last_name = (body.get("last_name") or "").strip()
        name = (body.get("name") or f"{first_name} {last_name}".strip() or "Applicant").strip()

        instagram_handle = (body.get("instagram_handle") or "").strip()
        if len(instagram_handle) < 2:
            instagram_handle = "mt360_lead"

        app_request = InfoProductApplicationRequest(
            name=name,
            email=body.get("email"),
            instagram_handle=instagram_handle,
            biggest_goal=body.get("goal") or body.get("biggest_goal"),
            biggest_block=body.get("biggest_block"),
            interested_offer=body.get("program") or body.get("interested_offer"),
        )

        result = funnel.process_application(app_request)

        # Best-effort: the applicant already succeeded, so a mail failure is
        # logged and swallowed rather than surfaced as a form error.
        applicant = {
            "name": name,
            "email": body.get("email"),
            "instagram_handle": instagram_handle,
            "interested_offer": app_request.interested_offer,
            "biggest_goal": app_request.biggest_goal,
            "biggest_block": app_request.biggest_block,
        }
        try:
            send_application_notification(applicant, result)
        except Exception as notify_error:  # pragma: no cover - defensive
            logger.error(f"Lead notification raised unexpectedly: {notify_error}")

        # Independent try: a failed confirmation must not hide the fact that
        # the internal notification succeeded, or vice versa.
        try:
            send_applicant_confirmation(applicant)
        except Exception as confirm_error:  # pragma: no cover - defensive
            logger.error(f"Applicant confirmation raised unexpectedly: {confirm_error}")

        return ApiResponse(success=True, message="Application captured", data=result)
    except Exception as e:
        logger.error(f"Error capturing standalone MT360 application: {e}")
        raise HTTPException(status_code=500, detail="Error capturing application")


def _alert_checkout_failure(offer_slug: str, reason: str) -> None:
    """Fire the alert without letting a mail problem change the response."""
    try:
        send_checkout_failure_alert(offer_slug, reason)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Checkout failure alert raised unexpectedly: %s", exc)


@app.post("/api/payments/stripe/checkout")
async def create_stripe_checkout_session(payload: StripeCheckoutRequest):
    """Create a Stripe Checkout session for a selected offer.

    The buy buttons on the sales page have always called this path, but the
    standalone app never defined it — every purchase attempt 404'd. Mirrors
    the handler in src/api/routes.py and shares the same pricing table.
    """
    if not settings.STRIPE_SECRET_KEY:
        logger.error("Checkout attempted but STRIPE_SECRET_KEY is not set")
        _alert_checkout_failure(payload.offer_slug, "STRIPE_SECRET_KEY is not set")
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    offer = MT360_OFFER_PRICING.get(payload.offer_slug)
    if not offer:
        raise HTTPException(status_code=400, detail="Invalid offer")

    success_url = payload.success_url or "https://codigodepoder777.com/?checkout=success"
    cancel_url = payload.cancel_url or "https://codigodepoder777.com/?checkout=cancel"

    result = stripe_processor.create_checkout_session(
        amount_cents=offer["amount_cents"],
        product_name=offer["name"],
        success_url=success_url,
        cancel_url=cancel_url,
        offer_slug=payload.offer_slug,
        customer_email=payload.customer_email,
    )

    if not result.get("success"):
        # Log the provider's message, never return it. Stripe's client errors
        # can embed the Authorization header — i.e. the live secret key — and
        # this response body is public.
        logger.error("Stripe checkout failed for %s: %s", payload.offer_slug, result.get("error"))
        _alert_checkout_failure(payload.offer_slug, str(result.get("error"))[:300])
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

    return ApiResponse(
        success=True,
        message="Stripe checkout session created",
        data={
            "checkout_url": result.get("checkout_url"),
            "session_id": result.get("session_id"),
            "offer_slug": payload.offer_slug,
        },
    )


@app.get("/vault", include_in_schema=False)
async def vault_shop_page():
    """Serve the digital vault shop page (76-product catalog)."""
    return FileResponse(STATIC_DIR / "vault-shop.html")


@app.post("/api/vault/checkout")
async def create_vault_checkout_session(payload: VaultCheckoutRequest):
    """Create a Stripe Checkout session for one vault product.

    Mirrors /api/payments/stripe/checkout but reads from the 76-product
    vault catalog instead of the high-ticket MT360_OFFER_PRICING table, and
    tags the session so the webhook below knows which PDF to deliver.
    """
    if not settings.STRIPE_SECRET_KEY:
        logger.error("Vault checkout attempted but STRIPE_SECRET_KEY is not set")
        _alert_checkout_failure(payload.slug, "STRIPE_SECRET_KEY is not set")
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    product = MT360_VAULT_PRODUCTS.get(payload.slug)
    if not product:
        raise HTTPException(status_code=400, detail="Invalid product")

    if product["price_cents"] == 0:
        # Free lead magnet — no Stripe session needed. Deliver immediately
        # if we already have an email; otherwise the shop page should be
        # collecting one before calling this endpoint for a $0 item.
        if not payload.customer_email:
            raise HTTPException(status_code=400, detail="Email required for free download")
        token = make_download_token(payload.slug)
        download_url = f"https://codigodepoder777.com/vault/download/{token}"
        send_vault_delivery_email(payload.customer_email, product["name"], download_url)
        return ApiResponse(
            success=True,
            message="Free download sent",
            data={"free": True, "download_url": download_url},
        )

    success_url = f"https://codigodepoder777.com/vault?checkout=success&product={payload.slug}"
    cancel_url = "https://codigodepoder777.com/vault?checkout=cancel"

    result = stripe_processor.create_checkout_session(
        amount_cents=product["price_cents"],
        product_name=product["name"],
        success_url=success_url,
        cancel_url=cancel_url,
        offer_slug=f"vault:{payload.slug}",
        customer_email=payload.customer_email,
    )

    if not result.get("success"):
        logger.error("Vault checkout failed for %s: %s", payload.slug, result.get("error"))
        _alert_checkout_failure(payload.slug, str(result.get("error"))[:300])
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

    return ApiResponse(
        success=True,
        message="Stripe checkout session created",
        data={"checkout_url": result.get("checkout_url"), "session_id": result.get("session_id")},
    )


@app.post("/webhooks/stripe", include_in_schema=False)
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    """Handle Stripe events — this is what actually delivers a vault purchase.

    Without this endpoint, checkout succeeds but nothing ever emails the
    buyer their file: /api/vault/checkout only opens the payment page.
    Reads raw bytes (not parsed JSON) because signature verification is
    computed over the exact request body Stripe sent.
    """
    body = await request.body()

    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("Stripe webhook received but STRIPE_WEBHOOK_SECRET is not set — rejecting")
        raise HTTPException(status_code=500, detail="Webhook not configured")

    try:
        event = stripe.Webhook.construct_event(body, stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        logger.error("Stripe webhook signature verification failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        offer_slug = (session.get("metadata") or {}).get("offer_slug", "")
        buyer_email = session.get("customer_details", {}).get("email") or session.get("customer_email")

        if offer_slug.startswith("vault:") and buyer_email:
            slug = offer_slug.split("vault:", 1)[1]
            product = MT360_VAULT_PRODUCTS.get(slug)
            if product:
                token = make_download_token(slug)
                download_url = f"https://codigodepoder777.com/vault/download/{token}"
                sent = send_vault_delivery_email(buyer_email, product["name"], download_url)
                if not sent:
                    _alert_checkout_failure(slug, f"Payment succeeded but delivery email failed for {buyer_email}")
            else:
                logger.error("Webhook: unknown vault slug in metadata: %s", slug)
        elif offer_slug.startswith("vault:"):
            logger.error("Webhook: vault purchase with no buyer email, session %s", session.get("id"))
        # Non-vault offers (coaching/mentorship) keep the existing manual
        # follow-up process and are intentionally not handled here.

    return {"received": True}


@app.get("/vault/download/{token}", include_in_schema=False)
async def vault_download(token: str):
    """Serve a purchased PDF if the signed token is valid and unexpired."""
    try:
        slug = read_download_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    product = MT360_VAULT_PRODUCTS.get(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    file_path = STATIC_DIR / "vault" / product["file"]
    if not file_path.exists():
        logger.error("Vault file missing on disk: %s (slug=%s)", file_path, slug)
        raise HTTPException(status_code=404, detail="File not available yet — contact support")

    return FileResponse(file_path, filename=product["file"], media_type="application/pdf")


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Reports whether the application database sits on the mounted disk. This
    is public, so it exposes the path and a boolean only — never the lead
    count, which is business data.
    """
    try:
        db_path = funnel.db.db_path
        persisted = db_path.startswith("/var/data")
    except Exception:  # pragma: no cover - health must never fail
        db_path, persisted = "unknown", False

    return {
        "status": "healthy",
        "service": "multitasking360official",
        "version": "1.0.0",
        "storage": {"db_path": db_path, "persisted_disk": persisted},
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
