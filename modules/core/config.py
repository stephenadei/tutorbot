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

# Server configuration
FLASK_PORT: int = int(os.getenv("FLASK_PORT", "8000"))
FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# OpenAI configuration
OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "30"))
OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "200"))
OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# Timezone
TZ: ZoneInfo = ZoneInfo("Europe/Amsterdam")

# Planning profiles for different customer segments
PLANNING_PROFILES = {
    "new": {
        "duration_minutes": int(os.getenv("PLANNING_NEW_DURATION", "60")),
        "earliest_hour": int(os.getenv("PLANNING_NEW_EARLIEST", "10")),
        "latest_hour": int(os.getenv("PLANNING_NEW_LATEST", "20")),
        "min_lead_minutes": int(os.getenv("PLANNING_NEW_LEAD", "720")),
        "buffer_before_min": int(os.getenv("PLANNING_NEW_BUFFER_BEFORE", "15")),
        "buffer_after_min": int(os.getenv("PLANNING_NEW_BUFFER_AFTER", "15")),
        "days_ahead": int(os.getenv("PLANNING_NEW_DAYS", "10")),
        "slot_step_minutes": int(os.getenv("PLANNING_NEW_STEP", "60")),
        "exclude_weekends": os.getenv("PLANNING_NEW_EXCLUDE_WEEKENDS", "True").lower() == "true"
    },
    "existing": {
        "duration_minutes": int(os.getenv("PLANNING_EXISTING_DURATION", "60")),
        "earliest_hour": int(os.getenv("PLANNING_EXISTING_EARLIEST", "9")),
        "latest_hour": int(os.getenv("PLANNING_EXISTING_LATEST", "21")),
        "min_lead_minutes": int(os.getenv("PLANNING_EXISTING_LEAD", "360")),
        "buffer_before_min": int(os.getenv("PLANNING_EXISTING_BUFFER_BEFORE", "10")),
        "buffer_after_min": int(os.getenv("PLANNING_EXISTING_BUFFER_AFTER", "10")),
        "days_ahead": int(os.getenv("PLANNING_EXISTING_DAYS", "14")),
        "slot_step_minutes": int(os.getenv("PLANNING_EXISTING_STEP", "60")),
        "exclude_weekends": os.getenv("PLANNING_EXISTING_EXCLUDE_WEEKENDS", "True").lower() == "true"
    },
    "returning_broadcast": {
        "duration_minutes": int(os.getenv("PLANNING_RETURNING_DURATION", "60")),
        "earliest_hour": int(os.getenv("PLANNING_RETURNING_EARLIEST", "9")),
        "latest_hour": int(os.getenv("PLANNING_RETURNING_LATEST", "21")),
        "min_lead_minutes": int(os.getenv("PLANNING_RETURNING_LEAD", "360")),
        "buffer_before_min": int(os.getenv("PLANNING_RETURNING_BUFFER_BEFORE", "10")),
        "buffer_after_min": int(os.getenv("PLANNING_RETURNING_BUFFER_AFTER", "10")),
        "days_ahead": int(os.getenv("PLANNING_RETURNING_DAYS", "14")),
        "slot_step_minutes": int(os.getenv("PLANNING_RETURNING_STEP", "60")),
        "exclude_weekends": os.getenv("PLANNING_RETURNING_EXCLUDE_WEEKENDS", "True").lower() == "true"
    },
    "weekend": {
        "duration_minutes": int(os.getenv("PLANNING_WEEKEND_DURATION", "60")),
        "earliest_hour": int(os.getenv("PLANNING_WEEKEND_EARLIEST", "10")),
        "latest_hour": int(os.getenv("PLANNING_WEEKEND_LATEST", "18")),
        "min_lead_minutes": int(os.getenv("PLANNING_WEEKEND_LEAD", "180")),
        "buffer_before_min": int(os.getenv("PLANNING_WEEKEND_BUFFER_BEFORE", "10")),
        "buffer_after_min": int(os.getenv("PLANNING_WEEKEND_BUFFER_AFTER", "10")),
        "days_ahead": int(os.getenv("PLANNING_WEEKEND_DAYS", "7")),
        "slot_step_minutes": int(os.getenv("PLANNING_WEEKEND_STEP", "60")),
        "exclude_weekends": os.getenv("PLANNING_WEEKEND_EXCLUDE_WEEKENDS", "False").lower() == "true",
        "allowed_weekdays": [5, 6]  # Saturday, Sunday
    },
    "premium": {
        "duration_minutes": int(os.getenv("PLANNING_PREMIUM_DURATION", "90")),
        "earliest_hour": int(os.getenv("PLANNING_PREMIUM_EARLIEST", "8")),
        "latest_hour": int(os.getenv("PLANNING_PREMIUM_LATEST", "22")),
        "min_lead_minutes": int(os.getenv("PLANNING_PREMIUM_LEAD", "240")),
        "buffer_before_min": int(os.getenv("PLANNING_PREMIUM_BUFFER_BEFORE", "20")),
        "buffer_after_min": int(os.getenv("PLANNING_PREMIUM_BUFFER_AFTER", "20")),
        "days_ahead": int(os.getenv("PLANNING_PREMIUM_DAYS", "21")),
        "slot_step_minutes": int(os.getenv("PLANNING_PREMIUM_STEP", "60")),
        "exclude_weekends": os.getenv("PLANNING_PREMIUM_EXCLUDE_WEEKENDS", "False").lower() == "true"
    }
}

