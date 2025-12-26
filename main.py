# =============================================================================
# TUTORBOT - CHATWOOT + WHATSAPP INTEGRATION
# =============================================================================
# 
# 🎯 MODULAR ARCHITECTURE: Handler-based System
# 
# This application has been refactored into a modular architecture with:
# - Core functionality moved to modules/handlers/
# - Utility functions in modules/utils/
# - Route handlers in modules/routes/
# - Integration services in modules/integrations/
# 
# Key Functions (now imported from modules):
# - show_prefill_action_menu(): Primary entry point for confirmation flow
# - send_input_select_only(): Sends interactive WhatsApp menu buttons
# - ChatwootAPI.send_message(): SSL-safe API communication
# 
# IMPORTANT: All core functions are now imported from their respective modules
# for better maintainability and organization.
# 
# =============================================================================
# IMPORTS
# =============================================================================
# Standard library imports
import os
import re
import json
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from zoneinfo import ZoneInfo

# Third-party imports
from flask import Flask, request, jsonify
import openai

# Local imports - Core modules
from modules.utils.cw_api import (
    ChatwootAPI, 
    get_contact_attrs, 
    set_contact_attrs, 
    get_conv_attrs, 
    set_conv_attrs, 
    add_conv_labels, 
    remove_conv_labels, 
    send_text
)

# Local imports - Route modules
from modules.routes import health as route_health
from modules.routes import webhook as route_webhook
from modules.routes import stripe as route_stripe

# Local imports - Integration modules
from modules.integrations.openai_service import (
    analyze_preferences_with_openai,
    analyze_first_message_with_openai, 
    analyze_info_request_with_openai,
    prefill_intake_from_message
)

# Local imports - Utility modules
from modules.utils.text_helpers import (
    safe_set_conv_attrs,
    t,
    send_text_with_duplicate_check,
    assign_conversation,
    send_handoff_message,
    send_handoff_menu,
    send_admin_warning,
    get_contact_id_from_conversation,
    send_input_select_only
)

from modules.utils.language import (
    detect_language_from_message
)

from modules.utils.mapping import (
    map_school_level,
    get_school_level_display,
    get_appropriate_tariffs_key,
    map_topic,
    is_prefill_sufficient_for_trial_lesson,
    smart_extraction_check,
    detect_segment
)

# Local imports - Helper modules
from helpers import get_insufficient_prefill_message

# Local imports - Handler modules
from modules.handlers.conversation import handle_message_created
from modules.handlers.contact import create_child_contact
from modules.handlers.menu import (
    show_info_menu,
    show_info_follow_up_menu,
    show_detailed_info_menu,
    handle_handoff_menu_selection
)
from modules.handlers.intake import (
    handle_prefill_confirmation,
    show_prefill_action_menu,
    show_prefill_action_menu_after_confirmation,
    process_corrections_and_reconfirm,
    show_prefill_summary_with_corrections,
    handle_prefill_confirmation_yes,
    handle_prefill_confirmation_no,
    start_intake_flow,
    handle_intake_step,
    handle_corrected_prefill_confirmation
)

# Local imports - Integration modules
from modules.integrations.calendar_integration import (
    suggest_slots,
    suggest_slots_mock,
    book_slot
)

from modules.handlers.planning import (
    start_planning_flow,
    handle_planning_selection,
    handle_trial_lesson_mode_selection,
    ask_trial_lesson_mode,
    ask_for_preferences_and_suggest_slots,
    suggest_available_slots,
    process_preferences_and_suggest_slots,
    handle_email_request,
    check_trial_booking_time_and_show_menu,
    show_post_trial_menu,
    create_payment_request
)

from modules.handlers.menu import (
    show_main_menu,
    show_segment_menu,
    handle_menu_selection,
    handle_info_menu_selection,
    show_work_method_info,
    show_services_info,
    show_workshops_info,
    show_handoff_menu,
    handle_faq_request
)

from modules.handlers.payment import (
    create_payment_link,
    verify_stripe_webhook
)

from modules.handlers.webhook import verify_webhook

# =============================================================================
# CONFIGURATION (imported from modules/core/config.py)
# =============================================================================
from modules.core.config import (
    CW_URL as CW,
    CW_ACC_ID as ACC, 
    CW_TOKEN as TOK,
    CW_ADMIN_TOKEN as ADMIN_TOK,
    CW_HMAC_SECRET as SIG,
    TZ,
    STRIPE_WEBHOOK_SECRET,
    STANDARD_PRICE_ID_60,
    STANDARD_PRICE_ID_90,
    WEEKEND_PRICE_ID_60,
    WEEKEND_PRICE_ID_90,
    GCAL_SERVICE_ACCOUNT_JSON,
    GCAL_CALENDAR_ID,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    HANDOFF_AGENT_ID,
    FLASK_PORT,
    FLASK_HOST,
    FLASK_DEBUG,
    PLANNING_PROFILES
)

# =============================================================================
# FLASK APP INITIALIZATION
# =============================================================================
app = Flask(__name__)



# REMOVED: analyze_preferences_with_openai moved to modules/integrations/openai_service.py



# REMOVED: create_child_contact moved to modules/handlers/contact.py



# REMOVED: get_contact_id_from_conversation - now using module version from modules.utils.text_helpers





# REMOVED: send_input_select_only - now using module version from modules.utils.text_helpers










# REMOVED: Planning profiles moved to modules/core/config.py

# REMOVED: Calendar integration functions moved to modules/integrations/calendar_integration.py

# Payment integration (mock implementation)
def create_payment_link(segment, minutes, order_id, conversation_id, student_name, service, audience, program):
    from modules.handlers.payment import create_payment_link as _create_payment_link
    return _create_payment_link(segment, minutes, order_id, conversation_id, student_name, service, audience, program)

def verify_stripe_webhook(payload, signature):
    from modules.handlers.payment import verify_stripe_webhook as _verify
    return _verify(payload, signature)

# Webhook verification
def verify_webhook(request):
    from modules.handlers.webhook import verify_webhook as _verify
    return _verify(request)

"""
Route registration: delegate Flask routes to modules.routes.*
"""
route_health.register(app)
route_webhook.register(app)
route_stripe.register(app)



def is_bot_disabled(cid):
    """Check if bot is disabled for this conversation"""
    conv_attrs = get_conv_attrs(cid)
    return conv_attrs.get("bot_disabled", False)


# REMOVED: show_info_menu moved to modules/handlers/menu.py

# REMOVED: handle_prefill_confirmation moved to modules/handlers/intake.py

# REMOVED: handle_info_menu_selection moved to modules/handlers/menu.py

# REMOVED: show_prefill_action_menu and show_prefill_action_menu_after_confirmation moved to modules/handlers/intake.py



# REMOVED: show_info_follow_up_menu, show_detailed_info_menu, handle_handoff_menu_selection moved to modules/handlers/menu.py

# REMOVED: show_segment_menu moved to modules/handlers/menu.py

  
# REMOVED: is_existing_customer - now using module version from modules.handlers.conversation

# REMOVED: has_completed_intake - now using module version from modules.handlers.conversation

# REMOVED: ask_trial_lesson_mode, handle_trial_lesson_mode_selection, ask_for_preferences_and_suggest_slots, suggest_available_slots moved to modules/handlers/planning.py

# REMOVED: process_corrections_and_reconfirm, show_prefill_summary_with_corrections, handle_corrected_prefill_confirmation, handle_prefill_confirmation_yes, handle_prefill_confirmation_no moved to modules/handlers/intake.py

# REMOVED: process_preferences_and_suggest_slots moved to modules/handlers/planning.py


# REMOVED: handle_email_request, check_trial_booking_time_and_show_menu, show_post_trial_menu, create_payment_request moved to modules/handlers/planning.py

# Stripe webhook is handled in modules.routes.stripe

# Payment success handling is now in modules.handlers.payment

# REMOVED: handle_faq_request moved to modules/handlers/menu.py

# -----------------------------------------------------------------------------
# Delegate remaining core handler functions to modules (backward-compatibility)
# This ensures any internal references call the modular implementations.
# All functions now imported directly from modules - no aliases needed!
# All functions now imported directly from modules - no aliases needed!

# All functions now imported directly from modules - no aliases needed!

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG) 