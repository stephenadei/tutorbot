"""
Centralized configuration for TutorBot.

This module unifies environment variable access across the codebase and
exposes commonly used settings in one place. It also provides a single
timezone instance for consistent datetime handling.
"""

from __future__ import annotations

import os
from zoneinfo import ZoneInfo

def get_env_or_default(key: str, default: str) -> str:
    """Get environment variable or return default value"""
    return os.getenv(key, default)

def get_env_int_or_default(key: str, default: str) -> int:
    """Get environment variable as int or return default value"""
    return int(get_env_or_default(key, default))

def get_env_bool_or_default(key: str, default: str) -> bool:
    """Get environment variable as bool or return default value"""
    return get_env_or_default(key, default).lower() == "true"

# Chatwoot configuration (support both legacy and new env names)
CW_URL: str = os.getenv("CW_URL") or os.getenv("CHATWOOT_URL")
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
GCAL_CALENDAR_ID: str = os.getenv("GCAL_CALENDAR_ID")

# OpenAI configuration
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")

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

def _get_planning_profiles():
    """Get planning profiles with test defaults when environment variables are not set"""
    # Check if we're in a test environment (no environment variables set)
    if not os.getenv("PLANNING_NEW_DURATION"):
        # Return test defaults for development/testing
        return {
            "new": {
                "duration_minutes": 60,
                "earliest_hour": 10,
                "latest_hour": 20,
                "min_lead_minutes": 60,
                "buffer_before_min": 15,
                "buffer_after_min": 15,
                "days_ahead": 14,
                "slot_step_minutes": 30,
                "exclude_weekends": True
            },
            "existing": {
                "duration_minutes": 60,
                "earliest_hour": 9,
                "latest_hour": 21,
                "min_lead_minutes": 30,
                "buffer_before_min": 10,
                "buffer_after_min": 10,
                "days_ahead": 21,
                "slot_step_minutes": 15,
                "exclude_weekends": False
            },
            "returning_broadcast": {
                "duration_minutes": 60,
                "earliest_hour": 9,
                "latest_hour": 21,
                "min_lead_minutes": 30,
                "buffer_before_min": 10,
                "buffer_after_min": 10,
                "days_ahead": 21,
                "slot_step_minutes": 15,
                "exclude_weekends": False
            },
            "weekend": {
                "duration_minutes": 90,
                "earliest_hour": 10,
                "latest_hour": 18,
                "min_lead_minutes": 120,
                "buffer_before_min": 30,
                "buffer_after_min": 30,
                "days_ahead": 28,
                "slot_step_minutes": 60,
                "exclude_weekends": False,
                "allowed_weekdays": [5, 6]  # Saturday, Sunday
            },
            "premium": {
                "duration_minutes": 90,
                "earliest_hour": 8,
                "latest_hour": 22,
                "min_lead_minutes": 15,
                "buffer_before_min": 5,
                "buffer_after_min": 5,
                "days_ahead": 30,
                "slot_step_minutes": 15,
                "exclude_weekends": False
            }
        }
    else:
        # Return production values from environment variables
        return {
            "new": {
                "duration_minutes": int(os.getenv("PLANNING_NEW_DURATION")),
                "earliest_hour": int(os.getenv("PLANNING_NEW_EARLIEST")),
                "latest_hour": int(os.getenv("PLANNING_NEW_LATEST")),
                "min_lead_minutes": int(os.getenv("PLANNING_NEW_LEAD")),
                "buffer_before_min": int(os.getenv("PLANNING_NEW_BUFFER_BEFORE")),
                "buffer_after_min": int(os.getenv("PLANNING_NEW_BUFFER_AFTER")),
                "days_ahead": int(os.getenv("PLANNING_NEW_DAYS")),
                "slot_step_minutes": int(os.getenv("PLANNING_NEW_STEP")),
                "exclude_weekends": os.getenv("PLANNING_NEW_EXCLUDE_WEEKENDS").lower() == "true"
            },
            "existing": {
                "duration_minutes": int(os.getenv("PLANNING_EXISTING_DURATION")),
                "earliest_hour": int(os.getenv("PLANNING_EXISTING_EARLIEST")),
                "latest_hour": int(os.getenv("PLANNING_EXISTING_LATEST")),
                "min_lead_minutes": int(os.getenv("PLANNING_EXISTING_LEAD")),
                "buffer_before_min": int(os.getenv("PLANNING_EXISTING_BUFFER_BEFORE")),
                "buffer_after_min": int(os.getenv("PLANNING_EXISTING_BUFFER_AFTER")),
                "days_ahead": int(os.getenv("PLANNING_EXISTING_DAYS")),
                "slot_step_minutes": int(os.getenv("PLANNING_EXISTING_STEP")),
                "exclude_weekends": os.getenv("PLANNING_EXISTING_EXCLUDE_WEEKENDS").lower() == "true"
            },
            "returning_broadcast": {
                "duration_minutes": int(os.getenv("PLANNING_RETURNING_DURATION")),
                "earliest_hour": int(os.getenv("PLANNING_RETURNING_EARLIEST")),
                "latest_hour": int(os.getenv("PLANNING_RETURNING_LATEST")),
                "min_lead_minutes": int(os.getenv("PLANNING_RETURNING_LEAD")),
                "buffer_before_min": int(os.getenv("PLANNING_RETURNING_BUFFER_BEFORE")),
                "buffer_after_min": int(os.getenv("PLANNING_RETURNING_BUFFER_AFTER")),
                "days_ahead": int(os.getenv("PLANNING_RETURNING_DAYS")),
                "slot_step_minutes": int(os.getenv("PLANNING_RETURNING_STEP")),
                "exclude_weekends": os.getenv("PLANNING_RETURNING_EXCLUDE_WEEKENDS").lower() == "true"
            },
            "weekend": {
                "duration_minutes": int(os.getenv("PLANNING_WEEKEND_DURATION")),
                "earliest_hour": int(os.getenv("PLANNING_WEEKEND_EARLIEST")),
                "latest_hour": int(os.getenv("PLANNING_WEEKEND_LATEST")),
                "min_lead_minutes": int(os.getenv("PLANNING_WEEKEND_LEAD")),
                "buffer_before_min": int(os.getenv("PLANNING_WEEKEND_BUFFER_BEFORE")),
                "buffer_after_min": int(os.getenv("PLANNING_WEEKEND_BUFFER_AFTER")),
                "days_ahead": int(os.getenv("PLANNING_WEEKEND_DAYS")),
                "slot_step_minutes": int(os.getenv("PLANNING_WEEKEND_STEP")),
                "exclude_weekends": os.getenv("PLANNING_WEEKEND_EXCLUDE_WEEKENDS").lower() == "true",
                "allowed_weekdays": [5, 6]  # Saturday, Sunday
            },
            "premium": {
                "duration_minutes": int(os.getenv("PLANNING_PREMIUM_DURATION")),
                "earliest_hour": int(os.getenv("PLANNING_PREMIUM_EARLIEST")),
                "latest_hour": int(os.getenv("PLANNING_PREMIUM_LATEST")),
                "min_lead_minutes": int(os.getenv("PLANNING_PREMIUM_LEAD")),
                "buffer_before_min": int(os.getenv("PLANNING_PREMIUM_BUFFER_BEFORE")),
                "buffer_after_min": int(os.getenv("PLANNING_PREMIUM_BUFFER_AFTER")),
                "days_ahead": int(os.getenv("PLANNING_PREMIUM_DAYS")),
                "slot_step_minutes": int(os.getenv("PLANNING_PREMIUM_STEP")),
                "exclude_weekends": os.getenv("PLANNING_PREMIUM_EXCLUDE_WEEKENDS").lower() == "true"
            }
        }

# Planning profiles for different customer segments
PLANNING_PROFILES = _get_planning_profiles()

