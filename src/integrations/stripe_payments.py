"""
Stripe payment integration for MultiTasking360 offers.
"""

import logging
from typing import Dict, Optional

import stripe

from config.settings import Settings

logger = logging.getLogger(__name__)


class StripePaymentProcessor:
    """Handles Stripe Checkout Session creation."""

    def __init__(self):
        self.settings = Settings()
        stripe.api_key = self.settings.STRIPE_SECRET_KEY

    def create_checkout_session(
        self,
        amount_cents: int,
        product_name: str,
        success_url: str,
        cancel_url: str,
        offer_slug: str,
        customer_email: Optional[str] = None,
    ) -> Dict:
        """Create a Stripe Checkout session for a one-time payment."""
        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": product_name,
                            },
                            "unit_amount": amount_cents,
                        },
                        "quantity": 1,
                    }
                ],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "offer_slug": offer_slug,
                },
                customer_email=customer_email,
            )

            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url,
            }
        except Exception as e:
            logger.error(f"Stripe checkout session error: {e}")
            return {
                "success": False,
                "error": str(e),
            }
