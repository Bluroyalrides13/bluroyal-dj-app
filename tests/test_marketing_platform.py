"""Tests for the DJ Blu Bloods info product funnel."""

from pathlib import Path

from src.marketing.funnel import InfoProductFunnel
from src.models.database import DatabaseManager
from src.models.schemas import InfoProductApplicationRequest


def test_score_application_routes_high_intent_lead():
    funnel = InfoProductFunnel()
    request = InfoProductApplicationRequest(
        name="Jordan Rivers",
        email="jordan@example.com",
        instagram_handle="@jordancreates",
        audience_size="25k_plus",
        monthly_revenue="5000_plus",
        biggest_goal="I want a high-ticket offer and better DM conversion.",
        biggest_block="I need a clearer sales system and booking flow.",
        budget_range="5000_plus",
        interested_offer="VIP",
    )

    result = funnel.score_application(request)

    assert result["overall_score"] >= 75
    assert result["recommended_offer"] == "VIP Blueprint Intensive"
    assert result["status"] == "vip_review"


def test_database_persists_info_product_application(tmp_path: Path):
    db_path = tmp_path / "platform.db"
    db = DatabaseManager(f"sqlite:///{db_path}")

    application_id = db.create_info_product_application(
        {
            "id": "app_123",
            "name": "Avery Blue",
            "email": "avery@example.com",
            "instagram_handle": "@averyblue",
            "audience_size": "10k_25k",
            "monthly_revenue": "2500_5000",
            "biggest_goal": "Sell more premium offers.",
            "biggest_block": "Need a better funnel.",
            "budget_range": "1500_5000",
            "interested_offer": "Accelerator",
            "overall_score": 82,
            "recommended_offer": "Content-to-Client Accelerator",
            "status": "qualified",
            "notes": "Premium fit",
        }
    )

    assert application_id == "app_123"
    recent = db.get_recent_info_product_applications(limit=1)
    assert recent[0]["email"] == "avery@example.com"
    assert recent[0]["recommended_offer"] == "Content-to-Client Accelerator"
