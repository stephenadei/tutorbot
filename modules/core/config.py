"""
Centralized configuration for TutorBot.

This module unifies environment variable access across the codebase and
exposes commonly used settings in one place. It also provides a single
timezone instance for consistent datetime handling.
"""

from __future__ import annotations

import os
from zoneinfo import ZoneInfo

# Chatwoot configuration (support both legacy and new env names)
CW_URL: str = os.getenv("CW_URL") or os.getenv("CHATWOOT_URL", "https://crm.stephenadei.nl")
CW_ACC_ID: str | None = os.getenv("CW_ACC_ID") or os.getenv("CHATWOOT_ACCOUNT_ID")
CW_TOKEN: str | None = os.getenv("CW_TOKEN") or os.getenv("CHATWOOT_TOKEN")
CW_ADMIN_TOKEN: str | None = os.getenv("CW_ADMIN_TOKEN") or os.getenv("CHATWOOT_ADMIN_TOKEN")
CW_HMAC_SECRET: str | None = os.getenv("CW_HMAC_SECRET") or os.getenv("CHATWOOT_HMAC_SECRET")

# Stripe configuration
STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")
STANDARD_PRICE_ID_60: str | None = os.getenv("STANDARD_PRICE_ID_60")
STANDARD_PRICE_ID_90: str | None = os.getenv("STANDARD_PRICE_ID_90")
WEEKEND_PRICE_ID_60: str | None = os.getenv("WEEKEND_PRICE_ID_60")
WEEKEND_PRICE_ID_90: str | None = os.getenv("WEEKEND_PRICE_ID_90")

# Calendar configuration
GCAL_SERVICE_ACCOUNT_JSON: str | None = os.getenv("GCAL_SERVICE_ACCOUNT_JSON")
GCAL_CALENDAR_ID: str = os.getenv("GCAL_CALENDAR_ID", "primary")

# OpenAI configuration
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Agent configuration
HANDOFF_AGENT_ID: int = int(os.getenv("HANDOFF_AGENT_ID", "1"))

# Timezone
TZ: ZoneInfo = ZoneInfo("Europe/Amsterdam")

# Planning profiles for different customer segments
PLANNING_PROFILES = {
    "new": {
        "duration_minutes": 60,
        "earliest_hour": 10,
        "latest_hour": 20,
        "min_lead_minutes": 720,
        "buffer_before_min": 15,
        "buffer_after_min": 15,
        "days_ahead": 10,
        "slot_step_minutes": 60,
        "exclude_weekends": True
    },
    "existing": {
        "duration_minutes": 60,
        "earliest_hour": 9,
        "latest_hour": 21,
        "min_lead_minutes": 360,
        "buffer_before_min": 10,
        "buffer_after_min": 10,
        "days_ahead": 14,
        "slot_step_minutes": 60,
        "exclude_weekends": True
    },
    "returning_broadcast": {
        "duration_minutes": 60,
        "earliest_hour": 9,
        "latest_hour": 21,
        "min_lead_minutes": 360,
        "buffer_before_min": 10,
        "buffer_after_min": 10,
        "days_ahead": 14,
        "slot_step_minutes": 60,
        "exclude_weekends": True
    },
    "weekend": {
        "duration_minutes": 60,
        "earliest_hour": 10,
        "latest_hour": 18,
        "min_lead_minutes": 180,
        "buffer_before_min": 10,
        "buffer_after_min": 10,
        "days_ahead": 7,
        "slot_step_minutes": 60,
        "exclude_weekends": False,
        "allowed_weekdays": [5, 6]  # Saturday, Sunday
    },
    "premium": {
        "duration_minutes": 90,  # Longer lessons for premium
        "earliest_hour": 8,
        "latest_hour": 22,
        "min_lead_minutes": 240,  # 4 hours notice
        "buffer_before_min": 20,
        "buffer_after_min": 20,
        "days_ahead": 21,  # 3 weeks ahead
        "slot_step_minutes": 60,
        "exclude_weekends": False  # Premium includes weekends
    }
}

