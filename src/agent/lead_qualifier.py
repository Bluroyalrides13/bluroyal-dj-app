"""
Lead Qualification Agent
Analyzes conversations and scores leads based on budget, frequency, location, and preferences
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from anthropic import Anthropic

from config.settings import Settings
from config.prompts import LEAD_QUALIFICATION_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LeadQualifier:
    """AI-powered lead qualification engine"""
    
    def __init__(self):
        self.settings = Settings()
        self.client = Anthropic()
        self.model = self.settings.CLAUDE_MODEL
        self.scoring_weights = self.settings.LEAD_SCORING
    
    def qualify_lead(self, conversation_history: list) -> Dict:
        """
        Analyze conversation and generate lead score
        
        Args:
            conversation_history: List of message dicts with role/content
            
        Returns:
            Dict with lead scores and recommendation
        """
        try:
            # Build conversation context
            context = self._build_context(conversation_history)
            
            # Call Claude to analyze and score
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"{LEAD_QUALIFICATION_PROMPT}\n\n{context}"
                    }
                ]
            )
            
            analysis = response.content[0].text
            scores = self._extract_scores(analysis)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error qualifying lead: {e}")
            return self._default_scores()
    
    def calculate_overall_score(self, individual_scores: Dict) -> float:
        """Calculate weighted overall score from individual dimensions"""
        
        overall = (
            individual_scores.get("budget_score", 0) * self.scoring_weights["budget_weight"] +
            individual_scores.get("frequency_score", 0) * self.scoring_weights["frequency_weight"] +
            individual_scores.get("location_score", 0) * self.scoring_weights["location_weight"] +
            individual_scores.get("service_preference_score", 0) * self.scoring_weights["service_preference_weight"] +
            individual_scores.get("engagement_score", 0) * self.scoring_weights["engagement_weight"]
        )
        
        return round(overall, 2)
    
    def is_high_quality_lead(self, overall_score: float) -> bool:
        """Determine if lead is high quality based on score"""
        return overall_score >= self.scoring_weights["high_quality_threshold"]
    
    def get_recommendation(self, scores: Dict) -> Dict:
        """Generate recommendation based on scores"""
        overall = self.calculate_overall_score(scores)
        
        if overall >= 85:
            recommendation = {
                "status": "qualified",
                "priority": "high",
                "message": "Excellent lead - high conversion potential",
                "suggested_tier": "vip"
            }
        elif overall >= 70:
            recommendation = {
                "status": "qualified",
                "priority": "medium",
                "message": "Good lead - schedule follow-up",
                "suggested_tier": "premier"
            }
        elif overall >= 50:
            recommendation = {
                "status": "qualified",
                "priority": "low",
                "message": "Moderate interest - nurture lead",
                "suggested_tier": "executive"
            }
        else:
            recommendation = {
                "status": "unqualified",
                "priority": "none",
                "message": "Low conversion probability",
                "suggested_tier": "executive"
            }
        
        return recommendation
    
    def _build_context(self, conversation_history: list) -> str:
        """Convert conversation history to readable context"""
        context = "Recent Conversation:\n\n"
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            context += f"{role}: {content}\n"
        
        return context
    
    def _extract_scores(self, analysis: str) -> Dict:
        """
        Extract numerical scores from Claude's analysis
        Parses response to find budget, frequency, location, preference scores
        """
        # Parse scores from Claude's response
        # This is a simple implementation - in production, use structured output
        
        scores = {
            "budget_score": self._extract_number(analysis, "budget", 50),
            "frequency_score": self._extract_number(analysis, "frequency", 50),
            "location_score": self._extract_number(analysis, "location", 50),
            "service_preference_score": self._extract_number(analysis, "preference|tier|service", 50),
            "engagement_score": self._extract_number(analysis, "engagement|professional", 50),
        }
        
        scores["overall_score"] = self.calculate_overall_score(scores)
        
        return scores
    
    def _extract_number(self, text: str, keyword: str, default: int = 0) -> float:
        """Extract numerical score from text by keyword"""
        import re
        
        # Look for patterns like "budget score: 85" or "budget: 85/100"
        pattern = rf"{keyword}[\s\w:]*(\d+)"
        match = re.search(pattern, text.lower())
        
        if match:
            score = float(match.group(1))
            return min(100, max(0, score))  # Clamp between 0-100
        
        return float(default)
    
    def _default_scores(self) -> Dict:
        """Return default neutral scores"""
        return {
            "budget_score": 50,
            "frequency_score": 50,
            "location_score": 50,
            "service_preference_score": 50,
            "engagement_score": 50,
            "overall_score": 50
        }
