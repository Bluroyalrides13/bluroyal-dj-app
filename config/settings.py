"""
Configuration settings for Luxury Ride Share Agent
Loads from environment variables with sensible defaults
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Dashboard Access Control
    DASHBOARD_USERNAME: str = os.getenv("DASHBOARD_USERNAME", "djadmin")
    DASHBOARD_PASSWORD: str = os.getenv("DASHBOARD_PASSWORD", "change-this-now")
    ACADEMY_APP_USERNAME: str = os.getenv("ACADEMY_APP_USERNAME", "academyadmin")
    ACADEMY_APP_PASSWORD: str = os.getenv("ACADEMY_APP_PASSWORD", "change-this-now")

    # Payment Link Configuration
    STARTER_PAYMENT_LINK: str = os.getenv("STARTER_PAYMENT_LINK", "")
    GUIDED_PAYMENT_LINK: str = os.getenv("GUIDED_PAYMENT_LINK", "")
    VIP_PAYMENT_LINK: str = os.getenv("VIP_PAYMENT_LINK", "")
    POST_PURCHASE_LOGIN_URL: str = os.getenv(
        "POST_PURCHASE_LOGIN_URL",
        "https://app.bluroyaladventures.com/academy/login",
    )
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "")
    
    # Claude AI Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    
    # LangChain Configuration
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_ENABLED: bool = os.getenv("LANGCHAIN_ENABLED", "true").lower() == "true"
    
    # Square Payment Configuration
    SQUARE_ACCESS_TOKEN: str = os.getenv("SQUARE_ACCESS_TOKEN", "")
    SQUARE_ENVIRONMENT: str = os.getenv("SQUARE_ENVIRONMENT", "sandbox")
    SQUARE_API_VERSION: str = os.getenv("SQUARE_API_VERSION", "2024-03-20")
    
    # Wix Integration Configuration
    WIX_API_KEY: str = os.getenv("WIX_API_KEY", "")
    WIX_SITE_ID: str = os.getenv("WIX_SITE_ID", "")
    WIX_WEBHOOK_SECRET: str = os.getenv("WIX_WEBHOOK_SECRET", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./luxury_rideshare.db")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://bluroyaladventures.com",
        "https://www.bluroyaladventures.com",
        "https://app.bluroyaladventures.com",
        "https://*.wix.com",
        "https://*.wixpress.com",
    ]
    
    # Service Tiers Configuration
    SERVICE_TIERS: dict = {
        "executive": {
            "name": "Executive",
            "description": "Professional rides for business travel",
            "base_rate": 35.00,
            "per_mile": 3.50,
            "per_minute": 0.65,
            "amenities": ["Professional driver", "Climate control", "WiFi streaming"],
            "min_advance_booking": 120,  # minutes
        },
        "premier": {
            "name": "Premier",
            "description": "Premium luxury experience",
            "base_rate": 50.00,
            "per_mile": 4.50,
            "per_minute": 0.85,
            "amenities": ["Premium driver", "Climate control", "Premium beverage", "WiFi", "Phone charger"],
            "min_advance_booking": 120,
        },
        "vip": {
            "name": "VIP",
            "description": "Ultimate luxury experience",
            "base_rate": 75.00,
            "per_mile": 6.00,
            "per_minute": 1.25,
            "amenities": ["Concierge driver", "Advanced climate", "Premium beverages", "WiFi", "Phone charger", "Champagne"],
            "min_advance_booking": 120,
        },
    }
    
    # Geographic Configuration
    SUPPORTED_CITIES: List[str] = [
        "New York City, NY",
        "Los Angeles, CA",
        "Chicago, IL",
        "Miami, FL",
    ]
    
    # Lead Qualification Thresholds
    LEAD_SCORING: dict = {
        "budget_weight": 0.25,
        "frequency_weight": 0.25,
        "location_weight": 0.20,
        "service_preference_weight": 0.20,
        "engagement_weight": 0.10,
        "high_quality_threshold": 70,  # Score out of 100
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True
