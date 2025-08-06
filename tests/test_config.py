#!/usr/bin/env python3
"""
Test configuration and mock data for TutorBot tests
"""

import os
from unittest.mock import Mock

# Mock environment variables for testing
TEST_ENV_VARS = {
    "CW_URL": "https://test-chatwoot.example.com",
    "CW_ACC_ID": "1",
    "CW_TOKEN": "test_token",
    "CW_ADMIN_TOKEN": "test_admin_token",
    "CW_HMAC_SECRET": "test_hmac_secret",
    "STRIPE_WEBHOOK_SECRET": "test_stripe_secret",
    "STANDARD_PRICE_ID_60": "price_test_60",
    "STANDARD_PRICE_ID_90": "price_test_90",
    "WEEKEND_PRICE_ID_60": "price_weekend_60",
    "WEEKEND_PRICE_ID_90": "price_weekend_90",
    "GCAL_SERVICE_ACCOUNT_JSON": "{}",
    "GCAL_CALENDAR_ID": "test_calendar",
    "OPENAI_API_KEY": "test_openai_key",
    "OPENAI_MODEL": "gpt-4o-mini"
}

# Test data for conversations
TEST_CONVERSATION_DATA = {
    "conversation": {
        "id": 123,
        "status": "open",
        "created_at": "2024-01-01T12:00:00Z"
    },
    "contact": {
        "id": 456,
        "name": "Test User",
        "phone": "+31612345678",
        "email": "test@example.com"
    },
    "sender": {
        "id": 456,
        "type": "contact"
    },
    "event": "message_created",
    "message_type": "incoming",
    "content": "Hallo, ik ben John en zit in 6V. Ik heb moeite met wiskunde B."
}

# Test data for contact attributes
TEST_CONTACT_ATTRS = {
    "language": "nl",
    "segment": "new",
    "is_adult": True,
    "is_student": False,
    "school_level": "",
    "topic_primary": "",
    "topic_secondary": "",
    "goals": "",
    "preferred_times": "",
    "lesson_mode": "",
    "referral_source": "",
    "has_completed_intake": False,
    "trial_lesson_completed": False,
    "has_paid_lesson": False,
    "lesson_booked": False
}

# Test data for conversation attributes
TEST_CONVERSATION_ATTRS = {
    "language_prompted": False,
    "intake_completed": False,
    "order_id": None,
    "pending_intent": "",
    "intake_step": "",
    "learner_name": "",
    "school_level": "",
    "topic_primary": "",
    "topic_secondary": "",
    "goals": "",
    "preferred_times": "",
    "lesson_mode": "",
    "referral_source": "",
    "is_adult": None,
    "for_who": "",
    "relationship_to_learner": "",
    "contact_name": "",
    "has_been_prefilled": False,
    "prefill_processed_for_message": "",
    "prefill_confirmation_sent": False,
    "original_message_processed": "",
    "last_processed_message": "",
    "last_bot_message": "",
    "planning_profile": "",
    "lesson_type": "",
    "payment_status": "",
    "trial_status": "",
    "prefill_unclear_count": 0
}

# Test OpenAI analysis responses
TEST_OPENAI_ANALYSIS = {
    "is_adult": True,
    "for_who": "self",
    "learner_name": "John",
    "school_level": "vwo",
    "topic_primary": "math",
    "topic_secondary": "wiskunde B",
    "goals": "eindexamen wiskunde B",
    "preferred_times": "maandag 19:00, woensdag 20:00",
    "lesson_mode": "online",
    "toolset": "none",
    "program": "none",
    "relationship_to_learner": "self",
    "referral_source": "google_search",
    "school_name": "Test School",
    "current_grade": "6.5",
    "location_preference": "online",
    "contact_name": "John",
    "urgency": "gemiddeld"
}

# Test planning slots
TEST_PLANNING_SLOTS = [
    {
        "start": "2024-01-02T14:00:00+02:00",
        "end": "2024-01-02T15:00:00+02:00",
        "label": "Tue 02 Jan 14:00–15:00"
    },
    {
        "start": "2024-01-02T15:00:00+02:00",
        "end": "2024-01-02T16:00:00+02:00",
        "label": "Tue 02 Jan 15:00–16:00"
    },
    {
        "start": "2024-01-03T14:00:00+02:00",
        "end": "2024-01-03T15:00:00+02:00",
        "label": "Wed 03 Jan 14:00–15:00"
    }
]

# Test payment data
TEST_PAYMENT_DATA = {
    "order_id": "SPL-20240101-0123",
    "amount": 6000,  # 60 EUR in cents
    "currency": "eur",
    "status": "pending",
    "payment_link": "https://checkout.stripe.com/pay/test_link"
}

# Mock functions for testing
def mock_get_contact_attrs(contact_id):
    """Mock function to get contact attributes"""
    return TEST_CONTACT_ATTRS.copy()

def mock_set_contact_attrs(contact_id, attrs):
    """Mock function to set contact attributes"""
    TEST_CONTACT_ATTRS.update(attrs)
    return True

def mock_get_conv_attrs(conversation_id):
    """Mock function to get conversation attributes"""
    return TEST_CONVERSATION_ATTRS.copy()

def mock_set_conv_attrs(conversation_id, attrs):
    """Mock function to set conversation attributes"""
    TEST_CONVERSATION_ATTRS.update(attrs)
    return True

def mock_send_text(conversation_id, text):
    """Mock function to send text message"""
    return True

def mock_add_conv_labels(conversation_id, labels):
    """Mock function to add conversation labels"""
    return True

def mock_remove_conv_labels(conversation_id, labels):
    """Mock function to remove conversation labels"""
    return True

# Test messages for different scenarios
TEST_MESSAGES = {
    "dutch_greeting": "Hallo, ik ben John en zit in 6V. Ik heb moeite met wiskunde B.",
    "english_greeting": "Hello, I'm John and I'm in 6V. I have trouble with mathematics B.",
    "parent_message": "Hallo, ik ben de moeder van Maria. Ze zit in Havo 5 en heeft hulp nodig met wiskunde.",
    "existing_customer": "Hallo Stephen, ik wil graag weer een les inplannen.",
    "weekend_request": "Hallo, ik ben geïnteresseerd in de weekend programma's.",
    "info_request": "Ik wil graag meer informatie over de tarieven.",
    "planning_request": "Ik wil graag een proefles inplannen.",
    "handoff_request": "Ik wil graag met Stephen spreken."
}

# Test user responses
TEST_USER_RESPONSES = {
    "confirm_prefill": "Ja, dat klopt helemaal",
    "deny_prefill": "Nee, dat klopt niet",
    "partial_prefill": "Deels correct",
    "language_dutch": "🇳🇱 Nederlands",
    "language_english": "🇬🇧 English",
    "for_self": "👤 Voor mezelf",
    "for_other": "👥 Voor iemand anders",
    "age_adult": "✅ Ja",
    "age_minor": "❌ Nee",
    "school_level_vwo": "VWO",
    "school_level_havo": "HAVO",
    "subject_math": "Wiskunde",
    "subject_stats": "Statistiek",
    "mode_online": "💻 Online",
    "mode_inperson": "🏠 Fysiek",
    "referral_google": "🔍 Google zoekopdracht",
    "planning_slot": "Tue 02 Jan 14:00–15:00",
    "valid_email": "test@example.com",
    "invalid_email": "invalid-email"
}

# Test error scenarios
TEST_ERROR_SCENARIOS = {
    "duplicate_message": "Same message content",
    "invalid_slot_format": "Invalid time format",
    "api_error": "API connection error",
    "openai_error": "OpenAI API error",
    "webhook_error": "Webhook verification failed"
}

def setup_test_environment():
    """Setup test environment variables"""
    for key, value in TEST_ENV_VARS.items():
        os.environ[key] = value

def cleanup_test_environment():
    """Cleanup test environment variables"""
    for key in TEST_ENV_VARS.keys():
        if key in os.environ:
            del os.environ[key]

def reset_test_data():
    """Reset test data to initial state"""
    global TEST_CONTACT_ATTRS, TEST_CONVERSATION_ATTRS
    
    TEST_CONTACT_ATTRS = {
        "language": "nl",
        "segment": "new",
        "is_adult": True,
        "is_student": False,
        "school_level": "",
        "topic_primary": "",
        "topic_secondary": "",
        "goals": "",
        "preferred_times": "",
        "lesson_mode": "",
        "referral_source": "",
        "has_completed_intake": False,
        "trial_lesson_completed": False,
        "has_paid_lesson": False,
        "lesson_booked": False
    }
    
    TEST_CONVERSATION_ATTRS = {
        "language_prompted": False,
        "intake_completed": False,
        "order_id": None,
        "pending_intent": "",
        "intake_step": "",
        "learner_name": "",
        "school_level": "",
        "topic_primary": "",
        "topic_secondary": "",
        "goals": "",
        "preferred_times": "",
        "lesson_mode": "",
        "referral_source": "",
        "is_adult": None,
        "for_who": "",
        "relationship_to_learner": "",
        "contact_name": "",
        "has_been_prefilled": False,
        "prefill_processed_for_message": "",
        "prefill_confirmation_sent": False,
        "original_message_processed": "",
        "last_processed_message": "",
        "last_bot_message": "",
        "planning_profile": "",
        "lesson_type": "",
        "payment_status": "",
        "trial_status": "",
        "prefill_unclear_count": 0
    } 