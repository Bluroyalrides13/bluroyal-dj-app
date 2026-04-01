"""
Chat Interface Agent
Manages multi-turn conversations with Claude, tracks conversation state and extracted data
"""

import logging
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from anthropic import Anthropic

from config.settings import Settings
from config.prompts import SYSTEM_PROMPT
from src.models.schemas import ChatMessage, ChatResponse
from src.models.database import DatabaseManager
from src.agent.lead_qualifier import LeadQualifier

logger = logging.getLogger(__name__)


class ChatInterface:
    """Manages conversations with customers"""
    
    def __init__(self):
        self.settings = Settings()
        self.client = Anthropic()
        self.model = self.settings.CLAUDE_MODEL
        self.db = DatabaseManager(self.settings.DATABASE_URL)
        self.lead_qualifier = LeadQualifier()
        self.conversation_states = {}  # Track active conversations
    
    def process_message(self, chat_msg: ChatMessage) -> ChatResponse:
        """
        Process incoming chat message and generate response
        
        Args:
            chat_msg: ChatMessage with user's message and session_id
            
        Returns:
            ChatResponse with agent's reply and metadata
        """
        session_id = chat_msg.session_id
        user_message = chat_msg.message
        
        try:
            # Get or initialize conversation state
            if session_id not in self.conversation_states:
                self.conversation_states[session_id] = {
                    "messages": [],
                    "extracted_data": {},
                    "state": "greeting"
                }
            
            state = self.conversation_states[session_id]
            
            # Add user message to history
            state["messages"].append({
                "role": "user",
                "content": user_message
            })
            
            # Generate Claude response
            response_text = self._call_claude(state["messages"])
            
            # Add assistant message to history
            state["messages"].append({
                "role": "assistant",
                "content": response_text
            })
            
            # Extract any booking/customer data from conversation
            extracted = self._extract_booking_data(state["messages"])
            state["extracted_data"].update(extracted)
            
            # Determine conversation state
            state["state"] = self._determine_state(state["messages"], extracted)
            
            # Calculate lead score if enough context
            lead_score = None
            if len(state["messages"]) >= 4:
                scores = self.lead_qualifier.qualify_lead(state["messages"])
                lead_score = scores.get("overall_score")
            
            return ChatResponse(
                response=response_text,
                session_id=session_id,
                extracted_data=extracted,
                lead_score=lead_score,
                conversation_state=state["state"]
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                response="I apologize, but I encountered an error. Please try again.",
                session_id=session_id,
                conversation_state="error"
            )
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get full conversation history for a session"""
        return self.conversation_states.get(session_id, {}).get("messages", [])
    
    def end_conversation(self, session_id: str) -> Optional[str]:
        """
        End conversation and optionally create lead record
        
        Returns:
            Lead ID if high-quality lead was created, None otherwise
        """
        if session_id not in self.conversation_states:
            return None
        
        state = self.conversation_states[session_id]
        messages = state["messages"]
        extracted = state["extracted_data"]
        
        # Score the lead
        scores = self.lead_qualifier.qualify_lead(messages)
        overall = scores.get("overall_score", 0)
        
        # Create lead if qualified
        if self.lead_qualifier.is_high_quality_lead(overall):
            lead_id = str(uuid.uuid4())
            lead_data = {
                "id": lead_id,
                "source": "chat",
                "name": extracted.get("name", "Unknown"),
                "email": extracted.get("email"),
                "phone": extracted.get("phone"),
                "initial_message": messages[0].get("content", "") if messages else "",
                "budget_score": scores.get("budget_score", 0),
                "frequency_score": scores.get("frequency_score", 0),
                "location_score": scores.get("location_score", 0),
                "preference_score": scores.get("service_preference_score", 0),
                "engagement_score": scores.get("engagement_score", 0),
                "overall_score": overall,
                "status": "qualified",
                "recommended_tier": scores.get("recommended_tier"),
            }
            
            self.db.create_lead(lead_data)
            
            # Clean up state
            del self.conversation_states[session_id]
            
            return lead_id
        
        # Clean up state
        del self.conversation_states[session_id]
        return None
    
    def _call_claude(self, messages: List[Dict]) -> str:
        """Call Claude API with conversation history"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        return response.content[0].text
    
    def _extract_booking_data(self, messages: List[Dict]) -> Dict:
        """Extract booking-relevant data from conversation"""
        extracted = {}
        
        # Simple pattern matching for common data points
        full_text = " ".join([msg.get("content", "") for msg in messages]).lower()
        
        # Look for location mentions
        cities = self.settings.SUPPORTED_CITIES
        for city in cities:
            if city.lower() in full_text:
                extracted["location"] = city
                break
        
        # Look for service tier preferences
        if "vip" in full_text or "premium" in full_text:
            extracted["preferred_tier"] = "vip"
        elif "premier" in full_text:
            extracted["preferred_tier"] = "premier"
        elif "executive" in full_text:
            extracted["preferred_tier"] = "executive"
        
        # Look for passenger count
        import re
        passenger_match = re.search(r"(\d+)\s*(?:passenger|person|people|traveler)", full_text)
        if passenger_match:
            extracted["passenger_count"] = int(passenger_match.group(1))
        
        return extracted
    
    def _determine_state(self, messages: List[Dict], extracted: Dict) -> str:
        """Determine current conversation state"""
        if len(messages) < 2:
            return "greeting"
        
        if extracted.get("passenger_count") and extracted.get("preferred_tier"):
            return "booking"
        
        if extracted.get("location"):
            return "qualifying"
        
        return "greeting"
