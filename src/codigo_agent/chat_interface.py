"""
Chat Interface — Código de Poder 777 Sales Agent
Follows the same pattern as src/agent/chat_interface.py (the Blu Royal Rides
agent): Anthropic client + per-lead conversation state, adapted for the
Código sales brain and lead memory instead of ride bookings.
"""

import logging
import re
from typing import Optional

from anthropic import Anthropic

from config.settings import Settings

from src.codigo_agent.system_prompt import SYSTEM_PROMPT
from src.codigo_agent.lead_memory import LeadMemory

logger = logging.getLogger(__name__)

# Match the model your other agents already use, unless overridden.
DEFAULT_MODEL = "claude-sonnet-5"  # current model; Settings().CLAUDE_MODEL default was retired

_HANDOFF_PHRASE = "voy a pasar esto directamente con cindy"


class CodigoChatInterface:
    """Handles one turn of conversation for a Código de Poder lead."""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.client = Anthropic()
        self.model = model
        self.memory = LeadMemory()

    def process_message(self, lead_id: str, user_message: str) -> dict:
        """
        Process one incoming message from a lead (e.g. a ManyChat subscriber)
        and return the agent's reply plus the lead's updated status.

        Args:
            lead_id: stable identifier for this lead (ManyChat subscriber_id
                     or IG handle both work — just be consistent).
            user_message: the text the lead just sent.

        Returns:
            dict with: reply (str), lead_status (str), handoff (bool)
        """
        try:
            profile = self.memory.append_message(lead_id, "user", user_message)

            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in profile["messages"]
            ]

            reply_text = self._call_claude(messages, profile)

            self.memory.append_message(lead_id, "assistant", reply_text)

            handoff = _HANDOFF_PHRASE in reply_text.lower()
            new_status = "HUMAN_HANDOFF" if handoff else self._infer_status(reply_text, profile)
            self.memory.update_fields(lead_id, lead_status=new_status)

            return {
                "reply": reply_text,
                "lead_status": new_status,
                "handoff": handoff,
            }

        except Exception as e:
            logger.error(f"Error processing Código chat message for {lead_id}: {e}")
            return {
                "reply": (
                    "Perdón, tuve un problema técnico. "
                    "¿Puedes intentar de nuevo en un momento?"
                ),
                "lead_status": "ERROR",
                "handoff": False,
            }

    def _call_claude(self, messages: list, profile: dict) -> str:
        # Give the model the lead's known profile as context, so it doesn't
        # re-ask questions already answered in a prior session.
        context_note = (
            f"\n\n[PERFIL CONOCIDO DEL LEAD]\n"
            f"goal: {profile.get('goal')}\n"
            f"blocker: {profile.get('blocker')}\n"
            f"product_idea: {profile.get('product_idea')}\n"
            f"budget_signal: {profile.get('budget_signal')}\n"
            f"objections: {profile.get('objections')}\n"
            f"lead_status: {profile.get('lead_status')}\n"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=SYSTEM_PROMPT + context_note,
            messages=messages,
        )
        logger.info(
            f"Claude raw response: stop_reason={response.stop_reason}, "
            f"content_blocks={response.content}"
        )
        return "".join(
            block.text for block in response.content if block.type == "text"
        )

    def _infer_status(self, reply_text: str, profile: dict) -> str:
        """Very light heuristic — refine once you have real conversation data."""
        lowered = reply_text.lower()
        if "comprar ahora" in lowered or re.search(r"\$\d+", reply_text):
            return "CHECKOUT_SENT"
        if profile.get("recommended_product"):
            return "RECOMMENDED"
        if len(profile.get("messages", [])) >= 4:
            return "QUALIFYING"
        return "NEW"

