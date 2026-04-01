"""
Square Payment Integration
Handles payment processing through Square
"""

import logging
from typing import Dict, Optional
from squareup.client import Client
from squareup.api.payments_api import PaymentsApi
from squareup.models import Money

from config.settings import Settings

logger = logging.getLogger(__name__)


class SquarePaymentProcessor:
    """Handles payment processing with Square"""
    
    def __init__(self):
        self.settings = Settings()
        self.client = self._init_square_client()
    
    def _init_square_client(self) -> Client:
        """Initialize Square API client"""
        return Client(
            access_token=self.settings.SQUARE_ACCESS_TOKEN,
            environment=self.settings.SQUARE_ENVIRONMENT
        )
    
    def create_payment(self, 
                      amount_cents: int,
                      source_id: str,
                      booking_id: str,
                      customer_email: str,
                      idempotency_key: str) -> Dict:
        """
        Create a payment through Square
        
        Args:
            amount_cents: Amount in cents
            source_id: Payment source ID (card, wallet, etc)
            booking_id: Associated booking ID
            customer_email: Customer email for receipt
            idempotency_key: Unique key to prevent duplicate charges
            
        Returns:
            Dict with payment result
        """
        
        try:
            payments_api = PaymentsApi(self.client)
            
            body = {
                "source_id": source_id,
                "amount_money": {
                    "amount": amount_cents,
                    "currency": "USD"
                },
                "idempotency_key": idempotency_key,
                "receipt_email": customer_email,
                "note": f"Booking: {booking_id}",
                "customer_id": booking_id,
                "app_fee_money": {
                    "amount": int(amount_cents * 0.03),  # 3% app fee
                    "currency": "USD"
                }
            }
            
            result = payments_api.create_payment(body)
            
            if result.is_success():
                payment = result.result
                logger.info(f"Payment processed successfully: {payment.id}")
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "amount": amount_cents,
                    "status": payment.status,
                    "receipt_url": payment.receipt_url
                }
            elif result.is_client_error():
                logger.error(f"Client error: {result.errors}")
                return {
                    "success": False,
                    "error": str(result.errors)
                }
            else:
                logger.error(f"Server error: {result.errors}")
                return {
                    "success": False,
                    "error": "Payment processing error"
                }
        
        except Exception as e:
            logger.error(f"Exception creating payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def refund_payment(self, payment_id: str, amount_cents: Optional[int] = None) -> Dict:
        """
        Refund a payment (full or partial)
        
        Args:
            payment_id: The Square payment ID to refund
            amount_cents: Amount to refund (None = full refund)
            
        Returns:
            Dict with refund result
        """
        
        try:
            refunds_api = self.client.refunds
            
            body = {
                "payment_id": payment_id,
            }
            
            if amount_cents:
                body["amount_money"] = {
                    "amount": amount_cents,
                    "currency": "USD"
                }
            
            result = refunds_api.refund_payment(body)
            
            if result.is_success():
                refund = result.result
                logger.info(f"Refund processed: {refund.id}")
                return {
                    "success": True,
                    "refund_id": refund.id,
                    "status": refund.status
                }
            else:
                logger.error(f"Refund error: {result.errors}")
                return {
                    "success": False,
                    "error": str(result.errors)
                }
        
        except Exception as e:
            logger.error(f"Exception refunding payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment(self, payment_id: str) -> Optional[Dict]:
        """Get payment details from Square"""
        
        try:
            payments_api = PaymentsApi(self.client)
            result = payments_api.get_payment(payment_id)
            
            if result.is_success():
                payment = result.result
                return {
                    "id": payment.id,
                    "amount": payment.amount_money.amount,
                    "currency": payment.amount_money.currency,
                    "status": payment.status,
                    "receipt_url": payment.receipt_url,
                    "created_at": payment.created_at
                }
            else:
                logger.error(f"Error fetching payment: {result.errors}")
                return None
        
        except Exception as e:
            logger.error(f"Exception getting payment: {e}")
            return None
    
    def create_customer(self, customer_data: Dict) -> Optional[str]:
        """
        Create a customer profile in Square
        
        Returns:
            Customer ID if successful, None otherwise
        """
        
        try:
            customers_api = self.client.customers
            
            body = {
                "given_name": customer_data.get("first_name"),
                "family_name": customer_data.get("last_name"),
                "email_address": customer_data.get("email"),
                "phone_number": customer_data.get("phone"),
            }
            
            result = customers_api.create_customer(body)
            
            if result.is_success():
                customer = result.result
                logger.info(f"Customer created in Square: {customer.id}")
                return customer.id
            else:
                logger.error(f"Error creating customer: {result.errors}")
                return None
        
        except Exception as e:
            logger.error(f"Exception creating customer: {e}")
            return None
