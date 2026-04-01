"""
Wix Integration
Connects to Wix for chat, contacts, and payments
"""

import logging
import hmac
import hashlib
from typing import Dict, Optional
import requests

from config.settings import Settings

logger = logging.getLogger(__name__)


class WixConnector:
    """Handles integration with Wix site"""
    
    def __init__(self):
        self.settings = Settings()
        self.api_key = self.settings.WIX_API_KEY
        self.site_id = self.settings.WIX_SITE_ID
        self.webhook_secret = self.settings.WIX_WEBHOOK_SECRET
        self.base_url = "https://www.wixapis.com/v1"
    
    def verify_webhook_signature(self, signature: str, body_string: str) -> bool:
        """
        Verify that a webhook came from Wix
        
        Args:
            signature: The signature header from Wix
            body_string: The raw webhook body
            
        Returns:
            True if signature is valid
        """
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            body_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def send_chat_message(self, contact_id: str, message: str) -> bool:
        """
        Send a chat message to a Wix contact
        
        Args:
            contact_id: Wix contact ID
            message: Message to send
            
        Returns:
            True if successful
        """
        
        try:
            endpoint = f"{self.base_url}/contacts/{contact_id}/send-message"
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": {
                    "content": message,
                    "type": "TEXT"
                }
            }
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Message sent to contact {contact_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending message to Wix: {e}")
            return False
    
    def create_contact(self, contact_data: Dict) -> Optional[str]:
        """
        Create a contact in Wix
        
        Args:
            contact_data: Dict with name, email, phone
            
        Returns:
            Contact ID if successful
        """
        
        try:
            endpoint = f"{self.base_url}/contacts"
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "contact": {
                    "name": {
                        "first": contact_data.get("first_name", ""),
                        "last": contact_data.get("last_name", "")
                    },
                    "emails": [contact_data.get("email")] if contact_data.get("email") else [],
                    "phones": [contact_data.get("phone")] if contact_data.get("phone") else [],
                }
            }
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            contact = response.json()
            contact_id = contact.get("contact", {}).get("id")
            
            logger.info(f"Contact created in Wix: {contact_id}")
            return contact_id
        
        except Exception as e:
            logger.error(f"Error creating contact in Wix: {e}")
            return None
    
    def update_contact(self, contact_id: str, updates: Dict) -> bool:
        """Update a Wix contact"""
        
        try:
            endpoint = f"{self.base_url}/contacts/{contact_id}"
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {"contact": updates}
            
            response = requests.patch(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Contact updated in Wix: {contact_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating contact in Wix: {e}")
            return False
    
    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """Get contact details from Wix"""
        
        try:
            endpoint = f"{self.base_url}/contacts/{contact_id}"
            headers = {"Authorization": self.api_key}
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            
            contact = response.json().get("contact", {})
            return {
                "id": contact.get("id"),
                "name": contact.get("name", {}).get("first", ""),
                "email": contact.get("emails", [{}])[0] if contact.get("emails") else None,
                "phone": contact.get("phones", [{}])[0] if contact.get("phones") else None,
            }
        
        except Exception as e:
            logger.error(f"Error fetching contact from Wix: {e}")
            return None
    
    def get_web_form_submission(self, form_id: str, submission_id: str) -> Optional[Dict]:
        """
        Get web form submission data from Wix
        Useful for retrieving booking inquiry form submissions
        """
        
        try:
            endpoint = f"{self.base_url}/web-modules/{form_id}/submissions/{submission_id}"
            headers = {"Authorization": self.api_key}
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error fetching form submission: {e}")
            return None
    
    def add_contact_label(self, contact_id: str, label: str) -> bool:
        """Add a label/tag to a Wix contact"""
        
        try:
            endpoint = f"{self.base_url}/contacts/{contact_id}"
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            updates = {
                "labels": [label]
            }
            
            return self.update_contact(contact_id, updates)
        
        except Exception as e:
            logger.error(f"Error adding label to contact: {e}")
            return False


class WixWebhookHandler:
    """Handles incoming Wix webhooks"""
    
    def __init__(self, wix: WixConnector):
        self.wix = wix
    
    def handle_chat_message(self, webhook_data: Dict) -> Dict:
        """
        Handle incoming chat message from Wix
        
        Args:
            webhook_data: The webhook payload
            
        Returns:
            Dict with processing result
        """
        
        try:
            # Extract relevant data
            contact_id = webhook_data.get("data", {}).get("authorId")
            message = webhook_data.get("data", {}).get("body")
            message_id = webhook_data.get("data", {}).get("id")
            
            logger.info(f"Received chat message from {contact_id}")
            
            return {
                "success": True,
                "contact_id": contact_id,
                "message_id": message_id,
                "message": message
            }
        
        except Exception as e:
            logger.error(f"Error handling chat webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_contact_created(self, webhook_data: Dict) -> Dict:
        """Handle when a new contact is created in Wix"""
        
        try:
            contact_id = webhook_data.get("data", {}).get("contactId")
            logger.info(f"New contact created: {contact_id}")
            
            return {
                "success": True,
                "contact_id": contact_id
            }
        
        except Exception as e:
            logger.error(f"Error handling contact creation webhook: {e}")
            return {"success": False, "error": str(e)}
