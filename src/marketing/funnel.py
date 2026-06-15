"""Offer strategy and qualification logic for the Blu Royal Academy sales funnel."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import re
import uuid

from config.settings import Settings
from src.models.database import DatabaseManager
from src.models.schemas import InfoProductApplicationRequest


@dataclass(frozen=True)
class OfferTier:
    slug: str
    name: str
    price: int
    access_level: str
    promise: str
    outcome: str


OFFER_TIERS: List[OfferTier] = [
    OfferTier(
        slug="vault",
        name="Basic Curriculum Kit",
        price=497,
        access_level="starter",
        promise="A foundational planning system with school-year themes, weekly templates, and ready-to-print learning activities.",
        outcome="Launch a reliable curriculum offer that helps teachers prep faster.",
    ),
    OfferTier(
        slug="accelerator",
        name="Intermediate Growth Kit",
        price=1500,
        access_level="guided",
        promise="An expanded curriculum and implementation package with deeper themed units and parent-facing resources.",
        outcome="Scale from scattered materials to a complete education product suite.",
    ),
    OfferTier(
        slug="vip",
        name="Full Program Implementation",
        price=3500,
        access_level="vip",
        promise="A premium done-with-you launch package combining full-year curriculum assets with high-ticket positioning support.",
        outcome="Sell a complete premium program through Instagram with confidence.",
    ),
    OfferTier(
        slug="fine_motor_skills",
        name="Fine Motor Skills Mega Pack",
        price=17,
        access_level="starter",
        promise="A compact, affordable printable bundle focused on grip strength, tracing, cutting, and coordination.",
        outcome="Help children build fine motor confidence fast with ready-to-use practice pages.",
    ),
]


TIER_FILE_BUNDLES: Dict[str, List[str]] = {
    # $497: foundational starter files only
    "vault": [
        "School-Year Theme Map Starter Pack",
        "Weekly Lesson Plan Templates",
        "Core Classroom Activity PDF Printables",
        "Parent Take-Home Practice Sheets",
        "Instagram Starter Promotion Copy",
    ],
    # $1500: starter + growth systems
    "accelerator": [
        "Everything in $497 Basic Kit",
        "Seasonal and Monthly Unit Plan Expansion",
        "Assessment Checklists and Tracking Sheets",
        "Advanced Parent Communication Templates",
        "Upsell and Bundle Offer Scripts",
        "Instagram DM Conversion Prompts",
    ],
    # $3500: complete package
    "vip": [
        "Everything in $1500 Intermediate Kit",
        "Full-Year Curriculum Blueprint",
        "Premium Printable Bundle Library",
        "High-Ticket Offer Positioning Framework",
        "Instagram Launch and Sales Sequence",
        "Done-with-you implementation playbook",
    ],
    "fine_motor_skills": [
        "Little Learners Worksheets",
        "Preschool Alphabet Workbook - Vol. 2",
        "Activities Coloring Book",
        "Activities Coloring Book - Vol. 2",
        "Ocean Animal Worksheets",
        "Jungle Adventure Activity Book",
    ],
}


class InfoProductFunnel:
    """Manages offer catalog, application scoring, and persistence."""

    def __init__(self) -> None:
        self.settings = Settings()
        self.db = DatabaseManager(self.settings.DATABASE_URL)

    def get_offer_catalog(self) -> List[Dict]:
        payment_links = {
            "vault": self.settings.STARTER_PAYMENT_LINK,
            "accelerator": self.settings.GUIDED_PAYMENT_LINK,
            "vip": self.settings.VIP_PAYMENT_LINK,
            "fine_motor_skills": self.settings.FINE_MOTOR_SKILLS_PAYMENT_LINK,
        }

        return [
            {
                "slug": tier.slug,
                "name": tier.name,
                "price": tier.price,
                "access_level": tier.access_level,
                "promise": tier.promise,
                "outcome": tier.outcome,
                "included_files": TIER_FILE_BUNDLES.get(tier.slug, []),
                "purchase_link": payment_links.get(tier.slug, ""),
                "post_purchase_login_url": self.settings.POST_PURCHASE_LOGIN_URL,
            }
            for tier in OFFER_TIERS
        ]

    def process_application(self, application: InfoProductApplicationRequest) -> Dict:
        evaluation = self.score_application(application)
        application_id = str(uuid.uuid4())

        payload = {
            "id": application_id,
            "name": application.name,
            "email": application.email,
            "instagram_handle": application.instagram_handle,
            "audience_size": application.audience_size,
            "monthly_revenue": application.monthly_revenue,
            "biggest_goal": application.biggest_goal,
            "biggest_block": application.biggest_block,
            "budget_range": application.budget_range,
            "interested_offer": application.interested_offer,
            "overall_score": evaluation["overall_score"],
            "recommended_offer": evaluation["recommended_offer"],
            "status": evaluation["status"],
            "notes": evaluation["notes"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self.db.create_info_product_application(payload)

        return {
            "application_id": application_id,
            "overall_score": evaluation["overall_score"],
            "recommended_offer": evaluation["recommended_offer"],
            "status": evaluation["status"],
            "next_step": evaluation["next_step"],
            "notes": evaluation["notes"],
        }

    def score_application(self, application: InfoProductApplicationRequest) -> Dict:
        score = 25
        notes: List[str] = []

        if application.budget_range in {"1500_5000", "5000_plus"}:
            score += 30
            notes.append("Budget fits a premium offer.")
        elif application.budget_range == "500_1500":
            score += 18
            notes.append("Budget fits an entry premium offer.")
        else:
            score += 8
            notes.append("Budget is early-stage but still qualified for nurture.")

        audience_score = self._score_audience(application.audience_size)
        score += audience_score
        notes.append(f"Audience contribution: +{audience_score}.")

        revenue_score = self._score_revenue(application.monthly_revenue)
        score += revenue_score
        notes.append(f"Revenue contribution: +{revenue_score}.")

        text_blob = " ".join(
            [
                application.biggest_goal or "",
                application.biggest_block or "",
                application.interested_offer or "",
            ]
        ).lower()
        intent_score = self._score_intent(text_blob)
        score += intent_score
        notes.append(f"Intent contribution: +{intent_score}.")

        overall_score = max(0, min(100, score))
        recommended_offer = self._recommend_offer(overall_score, application.budget_range)

        if overall_score >= 75:
            status = "vip_review"
            next_step = "Send them the VIP booking link and move to call booking."
        elif overall_score >= 55:
            status = "qualified"
            next_step = "Send the accelerator offer and invite them to book a strategy call."
        else:
            status = "nurture"
            next_step = "Send the resource vault and a short nurture sequence before a call."

        return {
            "overall_score": overall_score,
            "recommended_offer": recommended_offer,
            "status": status,
            "next_step": next_step,
            "notes": " ".join(notes),
        }

    def _score_audience(self, audience_size: str | None) -> int:
        if not audience_size:
            return 6

        audience_size = audience_size.lower()
        if audience_size in {"25k_plus", "10k_25k"}:
            return 18
        if audience_size in {"5k_10k", "1k_5k"}:
            return 12
        return 6

    def _score_revenue(self, monthly_revenue: str | None) -> int:
        if not monthly_revenue:
            return 4

        monthly_revenue = monthly_revenue.lower()
        if monthly_revenue in {"5000_plus", "2500_5000"}:
            return 16
        if monthly_revenue in {"1000_2500", "500_1000"}:
            return 10
        return 4

    def _score_intent(self, text_blob: str) -> int:
        score = 0
        high_intent_patterns = [r"high[- ]ticket", r"book more", r"convert", r"scale", r"premium"]
        medium_intent_patterns = [r"content", r"offer", r"instagram", r"dm", r"sales"]

        for pattern in high_intent_patterns:
            if re.search(pattern, text_blob):
                score += 6

        for pattern in medium_intent_patterns:
            if re.search(pattern, text_blob):
                score += 3

        return min(score, 22)

    def _recommend_offer(self, overall_score: int, budget_range: str | None) -> str:
        if overall_score >= 75 or budget_range == "5000_plus":
            return OFFER_TIERS[2].name
        if overall_score >= 55 or budget_range == "1500_5000":
            return OFFER_TIERS[1].name
        return OFFER_TIERS[0].name
