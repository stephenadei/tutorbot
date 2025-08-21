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

# Local imports - Handler modules (for backward compatibility)
from modules.handlers.conversation import handle_message_created as _handle_message_created_mod

from modules.handlers.intake import (
    start_intake_flow as _start_intake_flow_mod,
    handle_intake_step as _handle_intake_step_mod,
    handle_prefill_confirmation as _handle_prefill_confirmation_mod,
    handle_corrected_prefill_confirmation as _handle_corrected_prefill_confirmation_mod,
    show_prefill_action_menu as _show_prefill_action_menu_mod,
)

from modules.handlers.planning import (
    start_planning_flow as _start_planning_flow_mod,
    handle_planning_selection as _handle_planning_selection_mod,
    handle_trial_lesson_mode_selection as _handle_trial_lesson_mode_selection_mod,
    ask_trial_lesson_mode as _ask_trial_lesson_mode_mod,
    ask_for_preferences_and_suggest_slots as _ask_for_preferences_and_suggest_slots_mod,
    suggest_available_slots as _suggest_available_slots_mod,
    handle_email_request as _handle_email_request_mod,
    check_trial_booking_time_and_show_menu as _check_trial_booking_time_and_show_menu_mod,
    show_post_trial_menu as _show_post_trial_menu_mod,
    create_payment_request as _create_payment_request_mod,
)

from modules.handlers.menu import (
    show_main_menu as _show_main_menu_mod,
    show_segment_menu as _show_segment_menu_mod,
    handle_menu_selection as _handle_menu_selection_mod,
    show_info_menu as _show_info_menu_mod,
    handle_info_menu_selection as _handle_info_menu_selection_mod,
    show_work_method_info as _show_work_method_info_mod,
    show_services_info as _show_services_info_mod,
    show_workshops_info as _show_workshops_info_mod,
    show_handoff_menu as _show_handoff_menu_mod,
    handle_handoff_menu_selection as _handle_handoff_menu_selection_mod,
    handle_faq_request as _faq,
)

from modules.handlers.payment import (
    create_payment_link as _create_payment_link,
    verify_stripe_webhook as _verify_stripe_webhook,
)

from modules.handlers.webhook import verify_webhook as _verify_webhook

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
    PLANNING_PROFILES
)

# =============================================================================
# FLASK APP INITIALIZATION
# =============================================================================
app = Flask(__name__)



# REMOVED: analyze_preferences_with_openai moved to modules/integrations/openai_service.py



def create_child_contact(analysis: Dict[str, Any], conversation_id: int, parent_contact_id: int = None) -> int:
    """Create a separate contact for the child when a parent is writing"""
    try:
        # Get the parent contact ID from the conversation if not provided
        if not parent_contact_id:
            parent_contact_id = get_contact_id_from_conversation(conversation_id)
            if not parent_contact_id:
                print("❌ Could not get parent contact ID")
                return None
        
        # Create child contact with comprehensive info
        child_name = analysis.get("learner_name", "Onbekende leerling")
        child_attrs = {
            "language": "nl",
            "segment": "student",
            "is_adult": False,
            "is_student": True,
            "parent_contact_id": str(parent_contact_id),
            "created_by_parent": True,
            "name": child_name
        }
        
        # Add all available child information
        child_fields = [
            "school_level", "topic_primary", "topic_secondary", "goals",
            "preferred_times", "lesson_mode", "toolset", "program", "urgency"
        ]
        
        for field in child_fields:
            if analysis.get(field):
                if field == "school_level":
                    child_attrs[field] = map_school_level(analysis[field])
                else:
                    child_attrs[field] = analysis[field]
        
        # Create the child contact using ChatwootAPI
        # Try different inbox IDs - WhatsApp is usually 1 or 2
        for inbox_id in [1, 2]:
            try:
                child_contact = ChatwootAPI.create_contact(
                    inbox_id=inbox_id,
                    name=child_name,
                    phone="",  # No phone number for now
                    attrs=child_attrs
                )
                if child_contact:
                    break
            except Exception as e:
                print(f"⚠️ Failed to create contact with inbox_id {inbox_id}: {e}")
                continue
        
        if child_contact:
            child_contact_id = child_contact.get("id") or child_contact.get("payload", {}).get("contact", {}).get("id")
            if child_contact_id:
                print(f"👶 Created child contact {child_contact_id} for {child_name}")
                return child_contact_id
            else:
                print(f"❌ No child contact ID in response: {child_contact}")
                return None
        else:
            print("❌ Failed to create child contact")
            return None
            
    except Exception as e:
        print(f"❌ Error creating child contact: {e}")
        return None



# REMOVED: get_contact_id_from_conversation - now using module version from modules.utils.text_helpers





# REMOVED: send_input_select_only - now using module version from modules.utils.text_helpers










# REMOVED: Planning profiles moved to modules/core/config.py

# Calendar integration with real Google Calendar
def suggest_slots(conversation_id, profile_name):
    """Suggest available slots based on real calendar availability"""
    try:
        from calendar_integration import get_available_slots
        
        # Get user preferences from conversation attributes
        conv_attrs = get_conv_attrs(conversation_id)
        preferred_times = conv_attrs.get("preferred_times", "").lower()
        lesson_type = conv_attrs.get("lesson_type", "trial")
        
        # Parse preferred times into list
        preferred_time_list = []
        if preferred_times:
            # Extract specific times mentioned
            import re
            time_pattern = r'\b(\d{1,2}):?(\d{2})?\b'
            times = re.findall(time_pattern, preferred_times)
            for hour, minute in times:
                if minute:
                    preferred_time_list.append(f"{hour.zfill(2)}:{minute}")
                else:
                    preferred_time_list.append(f"{hour.zfill(2)}:00")
            
            # Add general time preferences
            if "avond" in preferred_times or "evening" in preferred_times:
                preferred_time_list.extend(["17:00", "18:00", "19:00"])
            if "middag" in preferred_times or "afternoon" in preferred_times:
                preferred_time_list.extend(["14:00", "15:00", "16:00"])
            if "ochtend" in preferred_times or "morning" in preferred_times:
                preferred_time_list.extend(["09:00", "10:00", "11:00"])
        
        # Get date range
        now = datetime.now(TZ)
        start_date = now + timedelta(days=1)  # Start from tomorrow
        end_date = now + timedelta(days=14)   # Look ahead 2 weeks
        
        # Get available slots from calendar
        available_slots = get_available_slots(
            start_date=start_date,
            end_date=end_date,
            preferred_times=preferred_time_list if preferred_time_list else None,
            lesson_type=lesson_type
        )
        
        # Convert to expected format
        slots = []
        for slot in available_slots:
            slots.append({
                "start": slot["start_iso"],
                "end": slot["end_iso"],
                "label": slot["label"]
            })
        
        # Return appropriate number of slots
        if profile_name == "premium":
            return slots[:15]  # More options for premium
        else:
            return slots[:6]   # Standard number for others
            
    except Exception as e:
        print(f"❌ Error getting calendar slots: {e}")
        # Fallback to mock implementation
        return suggest_slots_mock(conversation_id, profile_name)

def suggest_slots_mock(conversation_id, profile_name):
    """Fallback mock implementation"""
    profile = PLANNING_PROFILES.get(profile_name, PLANNING_PROFILES["new"])
    
    # Get user preferences from conversation attributes
    conv_attrs = get_conv_attrs(conversation_id)
    preferred_times = conv_attrs.get("preferred_times", "").lower()
    lesson_type = conv_attrs.get("lesson_type", "trial")
    
    # Dummy agenda implementation for testing
    now = datetime.now(TZ)
    slots = []
    
    # Generate slots for more days for premium service
    days_to_generate = profile.get("days_ahead", 14)
    for i in range(days_to_generate):
        date = now + timedelta(days=i)
        
        # Skip weekends if exclude_weekends is True
        if profile["exclude_weekends"] and date.weekday() >= 5:
            continue
            
        # Skip non-allowed weekdays for weekend profile
        if profile.get("allowed_weekdays") and date.weekday() not in profile["allowed_weekdays"]:
            continue
        
        # Check if this day matches user preferences
        day_name = date.strftime('%A').lower()
        if preferred_times:
            # Simple preference matching
            if "woensdag" in preferred_times and day_name != "wednesday":
                continue
            if "donderdag" in preferred_times and day_name != "thursday":
                continue
            if "vrijdag" in preferred_times and day_name != "friday":
                continue
            if "zaterdag" in preferred_times and day_name != "saturday":
                continue
            if "zondag" in preferred_times and day_name != "sunday":
                continue
            if "maandag" in preferred_times and day_name != "monday":
                continue
            if "dinsdag" in preferred_times and day_name != "tuesday":
                continue
        
        # Generate slots for this day with proper step intervals
        for hour in range(profile["earliest_hour"], profile["latest_hour"]):
            for minute in range(0, 60, profile["slot_step_minutes"]):
                start_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Adjust duration based on lesson type
                if lesson_type == "trial":
                    duration_minutes = 30  # Trial lessons are 30 minutes
                else:
                    duration_minutes = profile["duration_minutes"]  # Use profile duration for other lessons
                
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                # Check if slot is in the future and meets minimum lead time
                if start_time > now + timedelta(minutes=profile["min_lead_minutes"]):
                    
                    # SPECIAL RULE: Trial lessons only on weekdays 17:00-19:00
                    if lesson_type == "trial":
                        # Only allow weekdays (Monday = 0, Friday = 4)
                        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                            continue
                        # Only allow 17:00-19:00 for trial lessons
                        if start_time.hour < 17 or start_time.hour >= 19:
                            continue
                    
                    # Check if this time matches user preferences
                    if preferred_times:
                        if "middag" in preferred_times and start_time.hour < 12:
                            continue
                        if "avond" in preferred_times and start_time.hour < 18:
                            continue
                        if "ochtend" in preferred_times and start_time.hour >= 12:
                            continue
                    
                    # Create a readable label
                    slot_label = f"{start_time.strftime('%a %d %b %H:%M')}–{end_time.strftime('%H:%M')}"
                    slots.append({
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "label": slot_label
                    })
    
    # Return more slots for premium service, fewer for others
    if profile_name == "premium":
        return slots[:15]  # More options for premium
    else:
        return slots[:6]  # Standard number for others

def book_slot(conversation_id, start_time, end_time, title, description):
    """Book a slot in Google Calendar and send to dashboard"""
    print(f"📅 Booking slot: {start_time} - {end_time}")
    print(f"📅 Title: {title}")
    print(f"📅 Description: {description}")
    
    # Parse the start time to create a readable format
    try:
        if isinstance(start_time, str):
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = start_time
        
        # Create a readable event ID
        event_id = f"dummy_event_{conversation_id}_{start_dt.strftime('%Y%m%d_%H%M')}"
        
        print(f"✅ Successfully booked dummy slot: {event_id}")
        
        # Send lesson to dashboard
        try:
            from dashboard_integration import create_lesson_data, send_lesson_to_dashboard
            
            # Get conversation and contact data
            conv_attrs = get_conv_attrs(conversation_id)
            contact_id = conv_attrs.get("contact_id")
            contact_attrs = get_contact_attrs(contact_id) if contact_id else {}
            
            # Create lesson data
            lesson_data = create_lesson_data(
                student_name=conv_attrs.get("learner_name", "Unknown Student"),
                student_email=contact_attrs.get("email", ""),
                start_time=start_time,
                end_time=end_time,
                lesson_type=conv_attrs.get("lesson_type", "regular"),
                chatwoot_contact_id=contact_id,
                chatwoot_conversation_id=str(conversation_id),
                notes=description,
                location="Online",
                program=conv_attrs.get("program"),
                topic_primary=conv_attrs.get("topic_primary"),
                topic_secondary=conv_attrs.get("topic_secondary"),
                toolset=conv_attrs.get("toolset"),
                lesson_mode="ONLINE",
                is_adult=conv_attrs.get("is_adult", False),
                relationship_to_learner=conv_attrs.get("relationship_to_learner")
            )
            
            # Send to dashboard
            dashboard_success = send_lesson_to_dashboard(lesson_data)
            if dashboard_success:
                print(f"✅ Lesson sent to dashboard successfully")
            else:
                print(f"⚠️ Failed to send lesson to dashboard")
                
        except Exception as e:
            print(f"⚠️ Error sending to dashboard: {e}")
        
        return {
            "id": event_id,
            "htmlLink": f"https://calendar.google.com/event?eid={event_id}",
            "start": start_time,
            "end": end_time,
            "title": title,
            "description": description
        }
    except Exception as e:
        print(f"❌ Error booking slot: {e}")
        return None

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


def show_info_menu(cid, lang):
    """Show information menu with detailed options"""
    print(f"📄 Showing info menu in {lang}")
    print(f"🔧 Setting pending_intent to 'info_menu' for conversation {cid}")
    set_conv_attrs(cid, {"pending_intent": "info_menu"})
    print(f"🔧 Pending intent set, now sending interactive menu")
    
    # Get contact attributes to check if they have completed a trial lesson
    contact_id = get_contact_id_from_conversation(cid)
    contact_attrs = get_contact_attrs(contact_id)
    has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
    
    # Build menu options based on trial completion
    menu_options = [
        (t("menu_option_trial_lesson", lang), "trial_lesson"),
        (t("menu_tariffs", lang), "tariffs"),
        (t("menu_work_method", lang), "work_method"),
        (t("menu_how_lessons_work", lang), "how_lessons_work"),
        (t("menu_services", lang), "services"),
        (t("menu_travel_costs", lang), "travel_costs"),
        (t("menu_conditions", lang), "conditions"),
        (t("menu_weekend_programs", lang), "weekend_programs"),
        (t("menu_short_version", lang), "short_version"),
        (t("menu_more_info", lang), "more_info"),
        (t("menu_option_handoff", lang), "handoff")
    ]
    
    # Add "Les inplannen" option only if they have completed a trial lesson
    if has_completed_trial:
        menu_options.insert(1, (t("menu_option_plan_lesson", lang), "plan_lesson"))
        print(f"✅ Adding 'Les inplannen' option - trial completed")
    else:
        print(f"❌ Not showing 'Les inplannen' option - no trial completed")
    
    send_input_select_only(cid, t("info_menu_question", lang), menu_options)

def handle_prefill_confirmation(cid, contact_id, msg_content, lang):
    """Handle prefill confirmation from user"""
    print(f"🤖 Prefill confirmation: '{msg_content}'")
    
    # Check if this is the original message being re-processed
    conv_attrs = get_conv_attrs(cid)
    original_message = conv_attrs.get("original_message_processed", "")
    
    if msg_content == original_message:
        print(f"🔄 Original message detected in prefill confirmation - skipping")
        return
    
    # Update last_processed_message to the user's response and clear prefill tracking
    set_conv_attrs(cid, {
        "last_processed_message": msg_content,
        "prefill_processed_for_message": "",  # Clear so we can process new messages
        "prefill_confirmation_sent": False,   # Clear confirmation sent flag
        "original_message_processed": ""      # Clear original message flag
    })
    
    # Check user's response - improved recognition
    print(f"🔍 Analyzing prefill confirmation response: '{msg_content}'")
    
    # More comprehensive confirmation detection
    confirm_words = ["ja", "klopt", "correct", "yes", "✅", "ja dat klopt", "dat klopt", "klopt helemaal", "ja helemaal", "correct", "juist", "precies", "inderdaad"]
    deny_words = ["nee", "niet", "fout", "no", "❌", "nee dat klopt niet", "dat klopt niet", "niet correct", "fout", "verkeerd", "deels", "sommige", "partially", "🤔", "deels correct", "sommige kloppen", "niet alles"]
    
    msg_lower = msg_content.lower().strip()
    
    if msg_content == "confirm_all" or any(word in msg_lower for word in confirm_words):
        print(f"✅ User confirmed prefill information")
        
        # Get the prefilled information from conversation attributes
        conv_attrs = get_conv_attrs(cid)
        prefilled_info = {}
        
        # Extract ALL available information from conversation attributes
        info_fields = [
            "learner_name", "school_level", "topic_primary", "topic_secondary", 
            "goals", "referral_source", "is_adult", "for_who", "contact_name",
            "preferred_times", "location_preference", "toolset", "lesson_mode",
            "relationship_to_learner", "urgency", "contact_email", "contact_phone"
        ]
        
        for field in info_fields:
            if conv_attrs.get(field) is not None:
                prefilled_info[field] = conv_attrs[field]
        
        print(f"📋 Available information: {list(prefilled_info.keys())}")
        
        # Apply prefilled information to contact attributes
        if prefilled_info:
            current_contact_attrs = get_contact_attrs(contact_id)
            
            # Determine contact type and update accordingly
            for_who = prefilled_info.get("for_who", "self")
            learner_name = prefilled_info.get("learner_name", "")
            contact_name = prefilled_info.get("contact_name", "")
            
            if for_who == "self":
                # Student writing for themselves
                if learner_name:
                    current_contact_attrs["name"] = learner_name
                    current_contact_attrs["is_student"] = True
                    current_contact_attrs["is_adult"] = prefilled_info.get("is_adult", True)
                    print(f"✅ Set contact as student: {learner_name}")
            elif for_who == "child":
                # Parent writing for their child
                if contact_name:
                    current_contact_attrs["name"] = contact_name
                    current_contact_attrs["is_parent"] = True
                    current_contact_attrs["is_adult"] = True
                    current_contact_attrs["relationship_to_learner"] = prefilled_info.get("relationship_to_learner", "parent")
                    print(f"✅ Set contact as parent: {contact_name}")
                
                # Create child contact
                if learner_name:
                    child_contact_id = create_child_contact(prefilled_info, cid, contact_id)
                    if child_contact_id:
                        current_contact_attrs["child_contact_id"] = child_contact_id
                        print(f"👶 Created child contact: {child_contact_id} for {learner_name}")
                    else:
                        print(f"⚠️ Failed to create child contact for {learner_name}")
            else:
                # Other cases (friend, etc.)
                if contact_name:
                    current_contact_attrs["name"] = contact_name
                    current_contact_attrs["relationship_to_learner"] = prefilled_info.get("relationship_to_learner", "other")
                    print(f"✅ Set contact as other: {contact_name}")
            
            # Update all other prefilled information
            current_contact_attrs.update(prefilled_info)
            
            # Set intake completion flag
            current_contact_attrs["has_completed_intake"] = True
            current_contact_attrs["customer_since"] = datetime.now(TZ).isoformat()
            
            # Save updated contact attributes
            set_contact_attrs(contact_id, current_contact_attrs)
            print(f"✅ Applied prefilled info to contact: {list(prefilled_info.keys())}")
        
        # Use smart extraction check to determine flow
        smart_check_result = smart_extraction_check(prefilled_info)
        
        # 1. Detect and set segment
        detected_segment = detect_segment(contact_id)
        print(f"🎯 Detected segment: {detected_segment}")
        
        # 2. Set planning profile based on segment
        set_conv_attrs(cid, {"planning_profile": detected_segment})
        
        # 3. Set appropriate labels based on extracted information
        labels_to_add = []
        
        # Audience label based on school_level
        school_level = prefilled_info.get("school_level", "")
        if school_level:
            audience_mapping = {
                "po": "audience_po",
                "vmbo": "audience_vmbo", 
                "havo": "audience_havo",
                "vwo": "audience_vwo",
                "mbo": "audience_mbo",
                "university_wo": "audience_university_wo",
                "university_hbo": "audience_university_hbo",
                "adult": "audience_adult"
            }
            audience_label = audience_mapping.get(school_level)
            if audience_label:
                labels_to_add.append(audience_label)
        
        # Subject label based on topic_primary
        topic_primary = prefilled_info.get("topic_primary", "")
        if topic_primary:
            subject_mapping = {
                "math": "subject_math",
                "stats": "subject_stats",
                "science": "subject_science", 
                "english": "subject_english",
                "programming": "subject_programming"
            }
            subject_label = subject_mapping.get(topic_primary)
            if subject_label:
                labels_to_add.append(subject_label)
        
        # Service label for trial lesson
        labels_to_add.append("service_trial")
        
        # Source label
        labels_to_add.append("source_whatsapp")
        
        # Add all labels
        if labels_to_add:
            add_conv_labels(cid, labels_to_add)
            print(f"🏷️ Added labels: {labels_to_add}")
        
        # 4. Set customer status attributes
        current_time = datetime.now().isoformat()
        
        # Set customer_since if this is their first interaction
        if not current_contact_attrs.get("customer_since"):
            current_contact_attrs["customer_since"] = current_time
        
        # Set has_completed_intake
        current_contact_attrs["has_completed_intake"] = True
        
        # Update contact attributes
        set_contact_attrs(contact_id, current_contact_attrs)
        print(f"✅ Updated customer status attributes")
        
        # Mark that prefill has been confirmed
        set_conv_attrs(cid, {
            "prefill_confirmation_sent": True,
            "prefill_confirmation_time": datetime.now(TZ).isoformat(),
            "use_prefill": True  # Flag to use prefill in planning flow
        })
        
        # Always show the action menu after confirmation
        print(f"🎯 Showing action menu after confirmation")
        show_prefill_action_menu_after_confirmation(cid, contact_id, lang)

    
    elif msg_content == "correct_all" or any(word in msg_lower for word in deny_words):
        print(f"❌ User indicates information is incorrect - asking for corrections")
        
        # Ask user to provide correct information
        correction_text = t("ask_for_corrections", lang)
        send_text_with_duplicate_check(cid, correction_text)
        
        # Set conversation state to wait for corrections
        set_conv_attrs(cid, {
            "waiting_for_corrections": True,
            "prefill_correction_count": conv_attrs.get("prefill_correction_count", 0) + 1
        })
        
    else:
        # Unclear response, check if this is a repeat attempt
        conv_attrs = get_conv_attrs(cid)
        unclear_count = conv_attrs.get("prefill_unclear_count", 0)
        
        if unclear_count >= 2:
            # After 2 unclear responses, proceed with prefill anyway
            print(f"⚠️ Multiple unclear responses ({unclear_count}), proceeding with prefill")
            send_text_with_duplicate_check(cid, t("prefill_assume_correct", lang))
            
            # Clear the unclear count and proceed with confirmation
            set_conv_attrs(cid, {"prefill_unclear_count": 0})
            
            # Simulate a confirmation by calling the confirmation logic
            # Get the prefilled information and apply it
            prefilled_info = {}
            if conv_attrs.get("learner_name"):
                prefilled_info["learner_name"] = conv_attrs["learner_name"]
            if conv_attrs.get("school_level"):
                prefilled_info["school_level"] = conv_attrs["school_level"]
            if conv_attrs.get("topic_primary"):
                prefilled_info["topic_primary"] = conv_attrs["topic_primary"]
            if conv_attrs.get("topic_secondary"):
                prefilled_info["topic_secondary"] = conv_attrs["topic_secondary"]
            if conv_attrs.get("goals"):
                prefilled_info["goals"] = conv_attrs["goals"]
            if conv_attrs.get("referral_source"):
                prefilled_info["referral_source"] = conv_attrs["referral_source"]
            if conv_attrs.get("is_adult") is not None:
                prefilled_info["is_adult"] = conv_attrs["is_adult"]
            if conv_attrs.get("for_who"):
                prefilled_info["for_who"] = conv_attrs["for_who"]
            
            # Apply prefilled information to contact attributes
            if prefilled_info:
                current_contact_attrs = get_contact_attrs(contact_id)
                current_contact_attrs.update(prefilled_info)
                
                # If this is for themselves and we have a learner name, set it as the contact name
                for_who = prefilled_info.get("for_who", "self")
                learner_name = prefilled_info.get("learner_name", "")
                if for_who == "self" and learner_name:
                    current_contact_attrs["name"] = learner_name
                    current_contact_attrs["is_student"] = True
                    print(f"✅ Set contact name to learner name: {learner_name}")
                
                set_contact_attrs(contact_id, current_contact_attrs)
                print(f"✅ Applied prefilled info to contact: {list(prefilled_info.keys())}")
            
            # Check if we have sufficient information for a trial lesson
            if is_prefill_sufficient_for_trial_lesson(prefilled_info):
                # We have good information, proceed to trial lesson planning
                contact_name = prefilled_info.get("contact_name", "")
                learner_name = prefilled_info.get("learner_name", "")
                topic = prefilled_info.get("topic_secondary", "")
                
                print(f"🔍 Debug greeting: contact_name='{contact_name}', for_who='{prefilled_info.get('for_who')}', learner_name='{learner_name}'")
                
                if contact_name and prefilled_info.get("for_who") == "child":
                    # Parent writing for child - use parent's name
                    confirmation_msg = f"Perfect {contact_name}! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                    print(f"✅ Using contact_name: {contact_name}")
                elif learner_name:
                    # Student writing for themselves - use their name
                    confirmation_msg = f"Perfect {learner_name}! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                    print(f"✅ Using learner_name: {learner_name}")
                else:
                    confirmation_msg = f"Perfect! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                    print(f"✅ Using generic greeting")
                
                send_text_with_duplicate_check(cid, confirmation_msg)
                
                # Clear pending intent and go to planning flow
                set_conv_attrs(cid, {"pending_intent": ""})
                
                # Start planning flow directly
                start_planning_flow(cid, contact_id, lang)
                
            else:
                # Information is incomplete, go to main menu
                learner_name = prefilled_info.get("learner_name", "")
                if learner_name:
                    confirmation_msg = f"Bedankt {learner_name}! Ik heb een deel van je informatie kunnen verwerken.\n\n{t('general_greeting_tip', lang)}\n\nLaten we verder gaan met de intake om alles goed in te vullen."
                else:
                    confirmation_msg = f"Bedankt! Ik heb een deel van je informatie kunnen verwerken.\n\n{t('general_greeting_tip', lang)}\n\nLaten we verder gaan met de intake om alles goed in te vullen."
                
                send_text_with_duplicate_check(cid, confirmation_msg)
                
                # Clear pending intent and go to main menu
                set_conv_attrs(cid, {"pending_intent": ""})
                
                # Show main menu
                show_info_menu(cid, lang)
        else:
            # First or second unclear response, ask for clarification with interactive menu
            print(f"❓ Unclear prefill confirmation response (attempt {unclear_count + 1})")
            set_conv_attrs(cid, {"prefill_unclear_count": unclear_count + 1})
            
            # Send interactive menu for clarification
            send_input_select_only(cid, "❓ Sorry, ik begrijp je antwoord niet helemaal. Kun je kiezen uit:", [
                (t("prefill_confirm_all", lang), "confirm_all"),
                (t("prefill_correct_all", lang), "correct_all")
            ])

def handle_info_menu_selection(cid, contact_id, msg_content, lang):
    """Handle info menu selections"""
    print(f"📄 Info menu selection: '{msg_content}'")
    
    # Handle lesson planning
    if msg_content.lower() in ["plan_lesson", "les inplannen", "1"] or "📅" in msg_content:
        print(f"📅 Lesson planning requested from info menu")
        start_planning_flow(cid, contact_id, lang)
        return
    
    # Handle greetings first
    greeting_words = ["hi", "hello", "hey", "hallo", "hoi", "goedemorgen", "goedemiddag", "goedenavond", "good morning", "good afternoon", "good evening"]
    if msg_content.lower().strip() in greeting_words:
        print(f"👋 Greeting detected: '{msg_content}'")
        greeting_msg = t("greeting_response", lang)
        send_text_with_duplicate_check(cid, greeting_msg)
        return
    
    # Smart analysis for free text questions
    # If the message doesn't match any menu options, try to analyze it as a question
    if not any([
        msg_content.lower() in ["tariffs", "tarieven", "2"] or "💰" in msg_content,
        msg_content.lower() in ["work_method", "werkwijze", "3"] or "🎯" in msg_content,
        msg_content.lower() in ["services", "diensten", "4"] or "📚" in msg_content,
        msg_content.lower() in ["travel_costs", "reiskosten", "5"] or "🚗" in msg_content,
        msg_content.lower() in ["last_minute", "last-minute", "6"] or "⏰" in msg_content,
        msg_content.lower() in ["conditions", "voorwaarden", "7"] or "📋" in msg_content,
        msg_content.lower() in ["weekend_programs", "weekend programma's", "8"] or "🌅" in msg_content,
        msg_content.lower() in ["short_version", "korte versie", "9"] or "📝" in msg_content,
        msg_content.lower() in ["personal_background", "persoonlijke achtergrond", "11"] or "👨‍🏫 persoonlijke" in msg_content.lower(),
        msg_content.lower() in ["didactic_methods", "didactische methoden", "12"] or "📚 didactische" in msg_content.lower(),
        msg_content.lower() in ["technology_tools", "technologie tools", "13"] or "💻 technologie" in msg_content.lower(),
        msg_content.lower() in ["results_success", "resultaten succes", "14"] or "🏆 resultaten" in msg_content.lower(),
        msg_content.lower() in ["workshops_creative", "creatieve workshops", "15"] or "🎨 creatieve" in msg_content.lower(),
        msg_content.lower() in ["workshops_academic", "academische workshops", "16"] or "🎓 academische" in msg_content.lower(),
        msg_content.lower() in ["consultancy", "advies", "17"] or "💼 consultancy" in msg_content.lower(),
        msg_content.lower() in ["back_to_main", "terug naar hoofdmenu", "0"] or "⬅️" in msg_content
    ]):
        print(f"🤖 Analyzing free text question: '{msg_content}'")
        
        # Use OpenAI to analyze the question
        analysis = analyze_info_request_with_openai(msg_content, cid)
        
        if analysis and analysis.get("primary_category"):
            primary_category = analysis.get("primary_category")
            confidence = analysis.get("confidence", 0.0)
            
            print(f"🎯 Analyzed question: {primary_category} (confidence: {confidence})")
            
            # If confidence is high enough, provide the relevant information
            if confidence >= 0.7:
                # Map the category to the appropriate info
                if primary_category == "tariffs":
                    print(f"💰 Smart detection: Showing tariffs")
                    # Get contact info to determine appropriate tariffs
                    contact_attrs = get_contact_attrs(contact_id)
                    school_level = contact_attrs.get("school_level", "")
                    is_adult = contact_attrs.get("is_adult", False)
                    
                    # Determine if over 20 (adults are typically over 20)
                    age_over_20 = is_adult or school_level in ["university_hbo", "university_wo"]
                    
                    # Get appropriate tariffs key
                    tariffs_key = get_appropriate_tariffs_key(school_level, age_over_20)
                    print(f"💰 Using tariffs key: {tariffs_key} for school_level: {school_level}, age_over_20: {age_over_20}")
                    
                    send_text_with_duplicate_check(cid, t(tariffs_key, lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "work_method":
                    print(f"🎯 Smart detection: Showing work method")
                    send_text_with_duplicate_check(cid, t("info_work_method", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "services":
                    print(f"📚 Smart detection: Showing services")
                    send_text_with_duplicate_check(cid, t("info_services", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "travel_costs":
                    print(f"🚗 Smart detection: Showing travel costs")
                    send_text_with_duplicate_check(cid, t("info_travel_costs", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "last_minute":
                    print(f"⏰ Smart detection: Showing last-minute surcharges")
                    send_text_with_duplicate_check(cid, t("info_last_minute", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "conditions":
                    print(f"📋 Smart detection: Showing conditions")
                    send_text_with_duplicate_check(cid, t("info_conditions", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "weekend_programs":
                    print(f"🌅 Smart detection: Showing weekend programs")
                    send_text_with_duplicate_check(cid, t("info_weekend_programs", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "short_version":
                    print(f"📝 Smart detection: Showing short version")
                    send_text_with_duplicate_check(cid, t("info_short_version", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "personal_background":
                    print(f"👨‍🏫 Smart detection: Showing personal background")
                    send_text_with_duplicate_check(cid, t("info_personal_background", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "didactic_methods":
                    print(f"📚 Smart detection: Showing didactic methods")
                    send_text_with_duplicate_check(cid, t("info_didactic_methods", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "technology_tools":
                    print(f"💻 Smart detection: Showing technology tools")
                    send_text_with_duplicate_check(cid, t("info_technology_tools", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "results_success":
                    print(f"🏆 Smart detection: Showing results and success")
                    send_text_with_duplicate_check(cid, t("info_results_success", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "workshops_creative":
                    print(f"🎨 Smart detection: Showing creative workshops")
                    send_text_with_duplicate_check(cid, t("info_workshops_creative", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "workshops_academic":
                    print(f"🎓 Smart detection: Showing academic workshops")
                    send_text_with_duplicate_check(cid, t("info_workshops_academic", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
                elif primary_category == "consultancy":
                    print(f"💼 Smart detection: Showing consultancy")
                    send_text_with_duplicate_check(cid, t("info_consultancy", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
                    return
            
            # If confidence is low or no category found, try FAQ handler
            print(f"❓ Low confidence or no category found, trying FAQ handler")
            if handle_faq_request(cid, contact_id, msg_content, lang):
                return
            else:
                # If FAQ handler also didn't match, show the menu again
                send_text_with_duplicate_check(cid, t("error_unclear_question", lang))
                show_info_menu(cid, lang)
                return
    
    # Handle tariffs
    if msg_content.lower() in ["tariffs", "tarieven", "2"] or "💰" in msg_content:
        print(f"💰 Showing tariffs")
        # Get contact info to determine appropriate tariffs
        contact_attrs = get_contact_attrs(contact_id)
        school_level = contact_attrs.get("school_level", "")
        is_adult = contact_attrs.get("is_adult", False)
        
        # Determine if over 20 (adults are typically over 20)
        age_over_20 = is_adult or school_level in ["university_hbo", "university_wo"]
        
        # Get appropriate tariffs key
        tariffs_key = get_appropriate_tariffs_key(school_level, age_over_20)
        print(f"💰 Using tariffs key: {tariffs_key} for school_level: {school_level}, age_over_20: {age_over_20}")
        
        send_text_with_duplicate_check(cid, t(tariffs_key, lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle work method
    if msg_content.lower() in ["work_method", "werkwijze", "3"] or "🎯" in msg_content:
        print(f"🎯 Showing work method")
        send_text_with_duplicate_check(cid, t("info_work_method", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle services
    if msg_content.lower() in ["services", "diensten", "4"] or "📚" in msg_content:
        print(f"📚 Showing services")
        send_text_with_duplicate_check(cid, t("info_services", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle how lessons work
    if (msg_content.lower() in ["how_lessons_work", "how lessons work", "hoe lessen werken", "5"] or 
        "📚 hoe lessen" in msg_content.lower() or
        "how do lessons work" in msg_content.lower() or
        "hoe werken lessen" in msg_content.lower()):
        print(f"📚 Showing how lessons work")
        send_text_with_duplicate_check(cid, t("info_how_lessons_work", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle travel costs
    if msg_content.lower() in ["travel_costs", "reiskosten", "6"] or "🚗" in msg_content:
        print(f"🚗 Showing travel costs")
        send_text_with_duplicate_check(cid, t("info_travel_costs", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle last-minute
    if msg_content.lower() in ["last_minute", "last-minute", "7"] or "⏰" in msg_content:
        print(f"⏰ Showing last-minute surcharges")
        send_text_with_duplicate_check(cid, t("info_last_minute", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle conditions
    if msg_content.lower() in ["conditions", "voorwaarden", "8"] or "📋" in msg_content:
        print(f"📋 Showing conditions")
        send_text_with_duplicate_check(cid, t("info_conditions", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle weekend programs
    if msg_content.lower() in ["weekend_programs", "weekend programma's", "9"] or "🌅" in msg_content:
        print(f"🌅 Showing weekend programs")
        send_text_with_duplicate_check(cid, t("info_weekend_programs", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle short version
    if msg_content.lower() in ["short_version", "korte versie", "10"] or "📝" in msg_content:
        print(f"📝 Showing short version")
        send_text_with_duplicate_check(cid, t("info_short_version", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle personal background
    if msg_content.lower() in ["personal_background", "persoonlijke achtergrond", "11"] or "👨‍🏫 persoonlijke" in msg_content.lower():
        print(f"👨‍🏫 Showing personal background")
        send_text_with_duplicate_check(cid, t("info_personal_background", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle didactic methods
    if msg_content.lower() in ["didactic_methods", "didactische methoden", "12"] or "📚 didactische" in msg_content.lower():
        print(f"📚 Showing didactic methods")
        send_text_with_duplicate_check(cid, t("info_didactic_methods", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle technology tools
    if msg_content.lower() in ["technology_tools", "technologie tools", "13"] or "💻 technologie" in msg_content.lower():
        print(f"💻 Showing technology tools")
        send_text_with_duplicate_check(cid, t("info_technology_tools", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle results success
    if msg_content.lower() in ["results_success", "resultaten succes", "14"] or "🏆 resultaten" in msg_content.lower():
        print(f"🏆 Showing results and success")
        send_text_with_duplicate_check(cid, t("info_results_success", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle creative workshops
    if msg_content.lower() in ["workshops_creative", "creatieve workshops", "15"] or "🎨 creatieve" in msg_content.lower():
        print(f"🎨 Showing creative workshops")
        send_text_with_duplicate_check(cid, t("info_workshops_creative", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle academic workshops
    if msg_content.lower() in ["workshops_academic", "academische workshops", "16"] or "🎓 academische" in msg_content.lower():
        print(f"🎓 Showing academic workshops")
        send_text_with_duplicate_check(cid, t("info_workshops_academic", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle consultancy
    if msg_content.lower() in ["consultancy", "advies", "17"] or "💼 consultancy" in msg_content.lower():
        print(f"💼 Showing consultancy")
        send_text_with_duplicate_check(cid, t("info_consultancy", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle back to main info menu
    if msg_content.lower() in ["back_to_main_info", "terug naar hoofdmenu", "⬅️"] or "⬅️ terug" in msg_content.lower():
        print(f"⬅️ Returning to main info menu")
        show_info_menu(cid, lang)
        return
    
    # Handle more info
    if msg_content.lower() in ["more_info", "meer informatie", "📖"] or "📖 meer" in msg_content.lower():
        print(f"📖 Showing detailed info menu")
        show_detailed_info_menu(cid, lang)
        return
    
    # Handle handoff
    if msg_content.lower() in ["handoff", "stephen spreken", "10"] or "👨‍🏫" in msg_content:
        print(f"👨‍🏫 Handoff to Stephen requested")
        send_handoff_message(cid, t("handoff_teacher", lang))
        return
    
    # If no valid option, show the info menu again
    print(f"❓ Unknown info menu option: '{msg_content}' - showing info menu")
    show_info_menu(cid, lang)

def show_prefill_action_menu(cid, contact_id, lang):
    """
    🎯 CRITICAL FLOW: Show confirmation menu asking user if the extracted information is correct
    
    This function is the PRIMARY entry point for prefill confirmation flow.
    It sends:
    1. A confirmation question text message
    2. An input_select menu with confirmation options
    
    FLOW: User sends message → OpenAI extracts info → This function shows confirmation menu
    → User confirms → show_prefill_action_menu_after_confirmation() is called
    
    IMPORTANT: This function MUST use send_input_select_only() to ensure the menu appears
    correctly in WhatsApp. Direct text messages don't show interactive buttons.
    """
    print(f"🎯 Showing prefill confirmation menu in {lang}")
    
    try:
        set_conv_attrs(cid, {"pending_intent": "prefill_confirmation"})
    except Exception as e:
        print(f"⚠️ SSL error setting pending_intent: {e}")
        # Continue anyway - not critical
    
    # Step 1: Send the confirmation question as text (do not persist to avoid conv-attr write here)
    confirmation_text = t("prefill_confirmation_question", lang)
    try:
        send_text_with_duplicate_check(cid, confirmation_text, persist=False)
        print(f"✅ Confirmation question sent successfully")
    except Exception as e:
        print(f"⚠️ Failed to send confirmation question: {e}")
        # Continue anyway - the menu buttons are more important
    
    # Step 2: Send the confirmation menu using input_select (CRITICAL FOR MENU BUTTONS)
    menu_title = t("prefill_confirmation_menu_title", lang)
    menu_options = [
        (t("prefill_confirm_all", lang), "confirm_all"),
        (t("prefill_correct_all", lang), "correct_all")
    ]
    
    # CRITICAL: Use input_select_only for WhatsApp menu buttons
    # This ensures the menu appears as interactive buttons, not just text
    try:
        result = send_input_select_only(cid, menu_title, menu_options)
        print(f"🎯 Prefill confirmation menu send result: {result}")
    except Exception as e:
        print(f"❌ Failed to send confirmation menu: {e}")
        # Fallback: send as text with options
        fallback_text = f"{menu_title}\n\n" + "\n".join([f"• {option[0]}" for option in menu_options])
        send_text_with_duplicate_check(cid, fallback_text, persist=False)
        print(f"📝 Sent fallback text menu due to input_select failure")

def show_prefill_action_menu_after_confirmation(cid, contact_id, lang, show_explanation=True):
    """Show action menu after prefill confirmation - what does user want to do next?"""
    print(f"🎯 Showing prefill action menu after confirmation in {lang}")
    
    # Get contact attributes to determine age and show appropriate tariffs
    contact_attrs = get_contact_attrs(contact_id)
    conv_attrs = get_conv_attrs(cid)
    
    # Only show tariffs if we have sufficient information about age/level
    # Don't show tariffs for simple greetings like "Hello Stephen, i found you online"
    is_adult = contact_attrs.get('is_adult', False)
    school_level = contact_attrs.get('school_level', '')
    learner_name = contact_attrs.get('learner_name', '')
    topic = contact_attrs.get('topic_primary', '') or contact_attrs.get('topic_secondary', '')
    
    # Check if we have meaningful information beyond just "for_who"
    # We need to check if any meaningful information was actually detected
    has_meaningful_info = (
        school_level or          # Has school level
        learner_name or          # Has name
        topic                    # Has subject
    )
    
    # Check if this is a parent writing for their child
    for_who = contact_attrs.get('for_who', '')
    is_parent = contact_attrs.get('is_parent', False)
    
    if has_meaningful_info:
        # Show appropriate tariffs based on age/level
        # If parent is writing for child, use child's school level
        # If adult is writing for themselves, use their level
        if (is_parent and for_who == 'child') or (not is_parent and for_who == 'self'):
            # Use the learner's school level for tariff determination
            age_over_20 = is_adult or 'university' in school_level.lower() or 'hbo' in school_level.lower()
            tariffs_key = get_appropriate_tariffs_key(school_level, age_over_20)
            print(f"💰 Showing tariffs for learner level: {tariffs_key}")
            send_text_with_duplicate_check(cid, t(tariffs_key, lang))
        else:
            # Fallback to contact's is_adult status
            age_over_20 = is_adult or 'university' in school_level.lower() or 'hbo' in school_level.lower()
            tariffs_key = get_appropriate_tariffs_key(school_level, age_over_20)
            print(f"💰 Showing tariffs for contact level: {tariffs_key}")
            send_text_with_duplicate_check(cid, t(tariffs_key, lang))
    else:
        print(f"💰 Skipping tariffs - insufficient information detected (simple greeting)")
    
    # Check if they have completed a trial lesson (this is the key criteria)
    has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
    
    # For new customers, check if preferences are still current (only if significant time has passed)
    if not has_completed_trial:
        preferred_times = contact_attrs.get("preferred_times", "")
        location_preference = contact_attrs.get("location_preference", "")
        
        # Check if preferences were recently confirmed (within last hour)
        prefill_confirmation_time = conv_attrs.get("prefill_confirmation_time", "")
        current_time = datetime.now(TZ)
        
        if prefill_confirmation_time:
            try:
                confirmation_dt = datetime.fromisoformat(prefill_confirmation_time.replace('Z', '+00:00'))
                time_diff = current_time - confirmation_dt
                
                # Only check preferences if more than 1 hour has passed
                if time_diff.total_seconds() < 3600:  # 1 hour = 3600 seconds
                    print(f"⏰ Preferences recently confirmed ({time_diff.total_seconds()/60:.1f} minutes ago) - skipping check")
                else:
                    print(f"⏰ Preferences confirmed {time_diff.total_seconds()/3600:.1f} hours ago - checking if still current")
                    if preferred_times and location_preference:
                        # Show current preferences and ask if they're still correct
                        preferences_msg = t("preferences_share_current", lang, 
                                          preferred_times=preferred_times, 
                                          location_preference=location_preference)
                        send_text_with_duplicate_check(cid, preferences_msg)
                        
                        # Show preferences check menu
                        preferences_options = [
                            (t("preferences_check_yes", lang), "preferences_same"),
                            (t("preferences_check_no", lang), "preferences_changed")
                        ]
                        
                        set_conv_attrs(cid, {"pending_intent": "preferences_check"})
                        send_input_select_only(cid, t("preferences_check_title", lang), preferences_options)
                        return
            except Exception as e:
                print(f"⚠️ Error checking prefill confirmation time: {e}")
                # Continue without preferences check if there's an error
        else:
            print(f"⏰ No prefill confirmation time found - skipping preferences check")
    
    # Send explanation text first (only if not already shown)
    if show_explanation:
        explanation_text = t("prefill_action_menu_text", lang)
        send_text_with_duplicate_check(cid, explanation_text, persist=False)
    
    # Send appropriate menu based on trial completion
    action_menu_title = t("prefill_action_menu_title", lang)
    
    if has_completed_trial:
        # Customers who completed trial get the option to plan all lessons
        action_menu_options = [
            (t("prefill_action_all_lessons", lang), "plan_all_lessons"),
            (t("prefill_action_trial_first", lang), "plan_trial_lesson"),
            (t("prefill_action_main_menu", lang), "go_to_main_menu"),
            (t("prefill_action_handoff", lang), "handoff")
        ]
    else:
        # All customers without trial get trial lesson and urgent session options
        action_menu_options = [
            (t("prefill_action_trial_first", lang), "plan_trial_lesson"),
            (t("prefill_action_urgent_session", lang), "urgent_session"),
            (t("prefill_action_main_menu", lang), "go_to_main_menu"),
            (t("prefill_action_handoff", lang), "handoff")
        ]
    
    print(f"🎯 Action menu title: '{action_menu_title}'")
    print(f"🎯 Action menu options: {action_menu_options}")
    print(f"🎯 Customer type: {'with trial' if has_completed_trial else 'without trial'}")
    
    try:
        set_conv_attrs(cid, {"pending_intent": "prefill_action"})
    except Exception as e:
        print(f"⚠️ SSL error setting pending_intent: {e}")
        # Continue anyway - not critical
    
    # Use input_select_only for consistent menu formatting
    result = send_input_select_only(cid, action_menu_title, action_menu_options)
    print(f"🎯 Menu send result: {result}")



def show_info_follow_up_menu(cid, contact_id, lang):
    """Show follow-up menu after displaying information"""
    print(f"📄 Showing info follow-up menu in {lang}")
    set_conv_attrs(cid, {"pending_intent": "info_follow_up"})
    
    # Get contact attributes to check if they have completed a trial lesson
    contact_attrs = get_contact_attrs(contact_id)
    has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
    
    if has_completed_trial:
        # Customers who completed trial get plan lesson option
        send_input_select_only(cid, t("info_follow_up_existing", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_more_info", lang), "more_info"),
            (t("menu_option_handoff", lang), "handoff"),
            (t("menu_back_to_main", lang), "back_to_main")
        ])
    else:
        # Customers without trial get trial lesson option
        send_input_select_only(cid, t("info_follow_up_new", lang), [
            (t("menu_option_trial_lesson", lang), "trial_lesson"),
            (t("menu_more_info", lang), "more_info"),
            (t("menu_option_handoff", lang), "handoff"),
            (t("menu_back_to_main", lang), "back_to_main")
        ])

def show_detailed_info_menu(cid, lang):
    """Show detailed information menu with all submenu options"""
    print(f"📖 Showing detailed info menu in {lang}")
    print(f"🔧 Setting pending_intent to 'info_menu' for conversation {cid}")
    set_conv_attrs(cid, {"pending_intent": "info_menu"})
    print(f"🔧 Pending intent set, now sending interactive menu")
    send_input_select_only(cid, t("detailed_info_menu_text", lang), [
        (t("menu_personal_background", lang), "personal_background"),
        (t("menu_didactic_methods", lang), "didactic_methods"),
        (t("menu_technology_tools", lang), "technology_tools"),
        (t("menu_results_success", lang), "results_success"),
        (t("menu_workshops_creative", lang), "workshops_creative"),
        (t("menu_workshops_academic", lang), "workshops_academic"),
        (t("menu_consultancy", lang), "consultancy"),
        (t("menu_back_to_main", lang), "back_to_main_info")
    ])

def handle_handoff_menu_selection(cid, contact_id, msg_content, lang):
    """Handle handoff menu selections"""
    print(f"👨‍🏫 Handoff menu selection: '{msg_content}'")
    
    # Handle return to bot
    if msg_content.lower() in ["return_to_bot", "terug naar bot", "bot", "🤖"] or "🤖 terug" in msg_content.lower():
        print(f"🤖 Returning to bot")
        
        # Remove handoff labels to stop notifications to Stephen
        remove_conv_labels(cid, ["intent_handoff_duplicate", "intent_handoff_auto", "intent_handoff"])
        
        # Clear handoff state completely
        set_conv_attrs(cid, {
            "pending_intent": "none",
            "handoff_state": "none"
        })
        
        # Unassign from Stephen (assign back to bot)
        assign_conversation(cid, 1)  # Bot user_id=1
        
        # Send confirmation message
        send_text_with_duplicate_check(cid, t("handoff_return_to_bot", lang))
        
        # Show main menu
        contact_attrs = get_contact_attrs(contact_id)
        segment = detect_segment(contact_id)
        show_segment_menu(cid, contact_id, segment, lang)
        return
    
    # Handle stay with Stephen
    if msg_content.lower() in ["stay_with_stephen", "blijf bij stephen", "stephen", "👨‍🏫"] or "👨‍🏫 blijf" in msg_content.lower():
        print(f"👨‍🏫 Staying with Stephen")
        send_text_with_duplicate_check(cid, t("handoff_stay_with_stephen", lang))
        return
    
    # If no valid option, show the handoff menu again
    print(f"❓ Unknown handoff menu option: '{msg_content}' - showing handoff menu again")
    send_handoff_menu(cid)

def show_segment_menu(cid, contact_id, segment, lang):
    """Show appropriate menu based on segment"""
    print(f"📋 Showing {segment} menu in {lang}")
    
    # Check if we have a name and greet the client
    contact_attrs = get_contact_attrs(contact_id)
    print(f"🔍 Contact attrs in show_segment_menu: {contact_attrs}")
    contact_name = contact_attrs.get("name", "")
    print(f"🔍 Contact name found: {contact_name}")
    
    # Re-detect segment to ensure we have the latest status
    current_segment = detect_segment(contact_id)
    if current_segment != segment:
        print(f"🔄 Segment changed from {segment} to {current_segment}")
        segment = current_segment
        set_contact_attrs(contact_id, {"segment": segment})
    
    if contact_name:
        # Extract first name from full name
        first_name = contact_name.split()[0] if contact_name else ""
        if first_name:
            greeting = t("greeting_with_name", lang).format(name=first_name)
            print(f"👋 Greeting client: {first_name}")
            send_text_with_duplicate_check(cid, greeting)
    
    # Send the menu immediately
    print(f"📋 Sending menu for {segment} segment")
    
    # Set menu_shown flag to indicate we've shown a menu to the user
    set_conv_attrs(cid, {"menu_shown": True})
    
    if segment == "new":
        send_input_select_only(cid, t("menu_new", lang), [
            (t("menu_option_trial_lesson", lang), "plan_lesson"),
            (t("menu_option_info", lang), "info"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "existing":
        send_input_select_only(cid, t("menu_existing", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_same_preferences", lang), "same_preferences"),
            (t("menu_option_different", lang), "different"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "returning_broadcast":
        send_input_select_only(cid, t("menu_returning_broadcast", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_old_preferences", lang), "old_preferences"),
            (t("menu_option_new_intake", lang), "new_intake"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "weekend":
        send_input_select_only(cid, t("menu_weekend", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_info", lang), "info"),
            (t("menu_option_handoff", lang), "handoff")
        ])

  
# REMOVED: is_existing_customer - now using module version from modules.handlers.conversation

# REMOVED: has_completed_intake - now using module version from modules.handlers.conversation

def ask_trial_lesson_mode(cid, contact_id, lang):
    """Ask user for trial lesson mode (online vs fysiek)"""
    print(f"📱 Asking for trial lesson mode")
    
    # Set conversation state to wait for mode selection
    set_conv_attrs(cid, {
        "pending_intent": "trial_lesson_mode_selection"
    })
    
    # Send mode selection question with input select
    mode_options = [
        (t("trial_lesson_online", lang), "online"),
        (t("trial_lesson_fysiek", lang), "fysiek")
    ]
    
    send_input_select_only(cid, t("trial_lesson_mode_question", lang), mode_options)

def handle_trial_lesson_mode_selection(cid, contact_id, msg_content, lang):
    """Handle trial lesson mode selection"""
    print(f"📱 Trial lesson mode selection: '{msg_content}'")
    
    if msg_content == "online":
        mode_display = t("trial_lesson_online", lang)
        lesson_mode = "online"
        print(f"💻 User selected online trial lesson")
    elif msg_content == "fysiek":
        mode_display = t("trial_lesson_fysiek", lang)
        lesson_mode = "fysiek"
        print(f"🏫 User selected fysiek trial lesson (Science Park only)")
    else:
        # Invalid selection
        print(f"⚠️ Invalid mode selection: '{msg_content}'")
        send_text_with_duplicate_check(cid, t("error_invalid_selection", lang))
        ask_trial_lesson_mode(cid, contact_id, lang)
        return
    
    # Store the lesson mode
    conv_attrs = get_conv_attrs(cid)
    current_segment = conv_attrs.get("planning_profile", "new")
    
    set_conv_attrs(cid, {
        "lesson_mode": lesson_mode,
        "pending_intent": "planning"
    })
    
    # Update contact attributes
    contact_attrs = get_contact_attrs(contact_id)
    contact_attrs["lesson_mode"] = lesson_mode
    set_contact_attrs(contact_id, contact_attrs)
    
    # Confirm mode selection
    confirmation_msg = t("trial_lesson_mode_confirmed", lang, mode=mode_display)
    send_text_with_duplicate_check(cid, confirmation_msg)
    
    # Check if user has preferences, if not ask for them
    if not conv_attrs.get("user_preferences"):
        ask_for_preferences_and_suggest_slots(cid, current_segment, lang)
    else:
        suggest_available_slots(cid, current_segment, lang)



def ask_for_preferences_and_suggest_slots(cid, profile_name, lang):
    """Ask user for preferences and suggest slots based on OpenAI analysis"""
    print(f"🤔 Asking for preferences for profile: {profile_name}")
    
    # Ask user for preferences
    preference_text = t("ask_for_preferences", lang)
    send_text_with_duplicate_check(cid, preference_text)
    
    # Set conversation state to wait for preferences
    set_conv_attrs(cid, {
        "waiting_for_preferences": True,
        "planning_profile": profile_name
    })

def suggest_available_slots(cid, profile_name, lang):
    """Suggest available slots"""
    print(f"📅 Suggesting slots for profile: {profile_name}")
    conv_attrs = get_conv_attrs(cid)
    lesson_type = conv_attrs.get("lesson_type", "trial")
    lesson_mode = conv_attrs.get("lesson_mode", "online")
    
    # For fysiek lessons, only show Science Park slots
    if lesson_mode == "fysiek":
        print(f"🏫 Fysiek lesson requested - filtering for Science Park only")
        # Set location preference to Science Park for fysiek lessons
        set_conv_attrs(cid, {"location_preference": "Science Park"})
    
    slots = suggest_slots(cid, profile_name)
    
    if not slots:
        print(f"⚠️ No available slots found for {profile_name}")
        
        # Check if this is a trial lesson and show specific message
        if lesson_type == "trial":
            send_text_with_duplicate_check(cid, t("no_trial_slots_available", lang))
        else:
            send_text_with_duplicate_check(cid, t("no_slots_available", lang))
        return
    
    print(f"✅ Found {len(slots)} available slots")
    
    # Create quick reply options
    options = []
    for slot in slots:
        options.append((slot["label"], slot["start"]))
        print(f"📅 Slot option: '{slot['label']}' -> '{slot['start']}'")
    
    options.append((t("planning_more_options", lang), "more_options"))
    print(f"📅 More options: '{t('planning_more_options', lang)}' -> 'more_options'")
    
    # Set pending intent to planning so we can handle slot selections
    set_conv_attrs(cid, {"pending_intent": "planning"})
    
    # Determine lesson text based on type
    if lesson_type == "premium":
        lesson_text = t("planning_premium_slots", lang)
    elif lesson_type == "trial":
        lesson_text = t("planning_trial_slots", lang)
    else:
        lesson_text = t("planning_regular_slots", lang)
    
    print(f"📅 Sending {len(options)} options with text: '{lesson_text}'")
    send_input_select_only(cid, lesson_text, options)

def process_corrections_and_reconfirm(cid, contact_id, corrections_text, lang):
    """Process user corrections and ask for reconfirmation"""
    print(f"🔧 Processing corrections: {corrections_text}")
    
    # Analyze corrections with OpenAI
    analysis = analyze_first_message_with_openai(corrections_text, cid, send_admin_warning)
    
    if not analysis:
        print(f"⚠️ Failed to analyze corrections - asking for manual input")
        send_text_with_duplicate_check(cid, t("correction_analysis_failed", lang))
        return
    
    # Update conversation attributes with corrected information
    conv_attrs = get_conv_attrs(cid)
    updated_info = {}
    
    # Map OpenAI analysis to conversation attributes
    if analysis.get("learner_name"):
        updated_info["learner_name"] = analysis["learner_name"]
    if analysis.get("school_level"):
        updated_info["school_level"] = analysis["school_level"]
    if analysis.get("topic_primary"):
        updated_info["topic_primary"] = analysis["topic_primary"]
    if analysis.get("topic_secondary"):
        updated_info["topic_secondary"] = analysis["topic_secondary"]
    if analysis.get("goals"):
        updated_info["goals"] = analysis["goals"]
    if analysis.get("for_who"):
        updated_info["for_who"] = analysis["for_who"]
    if analysis.get("contact_name"):
        updated_info["contact_name"] = analysis["contact_name"]
    if analysis.get("is_adult"):
        updated_info["is_adult"] = analysis["is_adult"]
    if analysis.get("relationship_to_learner"):
        updated_info["relationship_to_learner"] = analysis["relationship_to_learner"]
    
    # Update conversation attributes
    conv_attrs.update(updated_info)
    set_conv_attrs(cid, conv_attrs)
    
    print(f"✅ Updated with corrections: {list(updated_info.keys())}")
    
    # Show corrected information for confirmation
    show_prefill_summary_with_corrections(cid, contact_id, lang, updated_info)

def show_prefill_summary_with_corrections(cid, contact_id, lang, updated_info):
    """Show corrected prefill information for confirmation"""
    print(f"📋 Showing corrected prefill summary")
    
    # Get current conversation attributes
    conv_attrs = get_conv_attrs(cid)
    
    # Build summary text with corrections highlighted
    summary_parts = []
    summary_parts.append(t("prefill_corrected_summary_title", lang))
    summary_parts.append("")
    
    # Show corrected information
    if updated_info.get("learner_name"):
        summary_parts.append(f"👤 {t('prefill_learner_name', lang)}: {updated_info['learner_name']}")
    if updated_info.get("school_level"):
        school_level_display = get_school_level_display(updated_info["school_level"], lang)
        summary_parts.append(f"🎓 {t('prefill_school_level', lang)}: {school_level_display}")
    if updated_info.get("topic_primary"):
        summary_parts.append(f"📚 {t('prefill_topic_primary', lang)}: {updated_info['topic_primary']}")
    if updated_info.get("topic_secondary"):
        summary_parts.append(f"📖 {t('prefill_topic_secondary', lang)}: {updated_info['topic_secondary']}")
    if updated_info.get("goals"):
        summary_parts.append(f"🎯 {t('prefill_goals', lang)}: {updated_info['goals']}")
    if updated_info.get("for_who"):
        for_who_display = t(f"prefill_for_who_{updated_info['for_who']}", lang)
        summary_parts.append(f"👥 {t('prefill_for_who', lang)}: {for_who_display}")
    
    summary_parts.append("")
    summary_parts.append(t("prefill_corrected_confirmation_prompt", lang))
    
    # Create input select options for confirmation
    options = [
        (t("prefill_confirm_yes", lang), "confirm_yes"),
        (t("prefill_confirm_no", lang), "confirm_no")
    ]
    
    # Send combined message with text and input select menu
    summary_text = "\n".join(summary_parts)
    send_input_select_only(cid, summary_text, options)
    
    # Set conversation state for confirmation
    set_conv_attrs(cid, {
        "waiting_for_corrections": False,
        "waiting_for_corrected_confirmation": True,
        "corrected_info": updated_info,
        "pending_intent": "prefill_confirmation"
    })

def handle_corrected_prefill_confirmation(cid, contact_id, msg_content, lang):
    """Handle confirmation of corrected prefill information"""
    print(f"🤖 Corrected prefill confirmation: '{msg_content}'")
    
    # Check for input select responses first
    if msg_content == "confirm_yes":
        print(f"✅ User confirmed corrected prefill information via input select")
        handle_prefill_confirmation_yes(cid, contact_id, lang)
        return
    elif msg_content == "confirm_no":
        print(f"❌ User denied corrected prefill information via input select")
        handle_prefill_confirmation_no(cid, contact_id, lang)
        return
    
    # Check user's text response (fallback)
    confirm_words = ["ja", "klopt", "correct", "yes", "✅", "ja dat klopt", "dat klopt", "klopt helemaal", "ja helemaal", "correct", "juist", "precies", "inderdaad"]
    deny_words = ["nee", "niet", "fout", "no", "❌", "nee dat klopt niet", "dat klopt niet", "niet correct", "fout", "verkeerd", "deels", "sommige", "partially", "🤔", "deels correct", "sommige kloppen", "niet alles"]
    
    msg_lower = msg_content.lower().strip()
    
    if any(word in msg_lower for word in confirm_words):
        print(f"✅ User confirmed corrected prefill information")
        
        # Get corrected information
        conv_attrs = get_conv_attrs(cid)
        corrected_info = conv_attrs.get("corrected_info", {})
        
        # Apply corrected information to contact attributes
        if corrected_info:
            current_contact_attrs = get_contact_attrs(contact_id)
            current_contact_attrs.update(corrected_info)
            current_contact_attrs["has_completed_intake"] = True
            set_contact_attrs(contact_id, current_contact_attrs)
            print(f"✅ Applied corrected info to contact")
        
        # Clear correction state and proceed with normal flow
        set_conv_attrs(cid, {
            "waiting_for_corrected_confirmation": False,
            "corrected_info": None,
            "prefill_confirmation_sent": True,
            "use_prefill": True
        })
        
        # Show action menu
        show_prefill_action_menu_after_confirmation(cid, contact_id, lang)
        
    elif any(word in msg_lower for word in deny_words):
        print(f"❌ User still indicates information is incorrect")
        
        # Check correction count
        conv_attrs = get_conv_attrs(cid)
        correction_count = conv_attrs.get("prefill_correction_count", 0)
        
        if correction_count >= 2:
            # After 2 correction attempts, disable bot and handoff to Stephen
            print(f"🚫 Maximum correction attempts reached ({correction_count}) - disabling bot")
            
            # Disable bot for this conversation
            set_conv_attrs(cid, {
                "bot_disabled": True,
                "bot_disabled_reason": "max_correction_attempts",
                "bot_disabled_time": datetime.now(TZ).isoformat()
            })
            
            # Send handoff message
            handoff_text = t("handoff_max_corrections", lang)
            send_handoff_message(cid, handoff_text)
            
        else:
            # Ask for more corrections
            correction_text = t("ask_for_more_corrections", lang)
            send_text_with_duplicate_check(cid, correction_text)
            
            # Set state to wait for more corrections
            set_conv_attrs(cid, {
                "waiting_for_corrections": True,
                "waiting_for_corrected_confirmation": False,
                "corrected_info": None
            })
    
    else:
        # Unclear response
        unclear_text = t("prefill_unclear_response", lang)
        send_text_with_duplicate_check(cid, unclear_text)

def handle_prefill_confirmation_yes(cid, contact_id, lang):
    """Handle positive confirmation of corrected prefill information"""
    print(f"✅ User confirmed corrected prefill information")
    
    # Get corrected information
    conv_attrs = get_conv_attrs(cid)
    corrected_info = conv_attrs.get("corrected_info", {})
    
    # Apply corrected information to contact attributes
    if corrected_info:
        current_contact_attrs = get_contact_attrs(contact_id)
        current_contact_attrs.update(corrected_info)
        current_contact_attrs["has_completed_intake"] = True
        set_contact_attrs(contact_id, current_contact_attrs)
        print(f"✅ Applied corrected info to contact")
    
    # Clear correction state and proceed with normal flow
    set_conv_attrs(cid, {
        "waiting_for_corrected_confirmation": False,
        "corrected_info": None,
        "prefill_confirmation_sent": True,
        "use_prefill": True,
        "pending_intent": None
    })
    
    # Show action menu
    show_prefill_action_menu_after_confirmation(cid, contact_id, lang)

def handle_prefill_confirmation_no(cid, contact_id, lang):
    """Handle negative confirmation of corrected prefill information"""
    print(f"❌ User still indicates information is incorrect")
    
    # Check correction count
    conv_attrs = get_conv_attrs(cid)
    correction_count = conv_attrs.get("prefill_correction_count", 0)
    
    if correction_count >= 2:
        # After 2 correction attempts, disable bot and handoff to Stephen
        print(f"🚫 Maximum correction attempts reached ({correction_count}) - disabling bot")
        
        # Disable bot for this conversation
        set_conv_attrs(cid, {
            "bot_disabled": True,
            "bot_disabled_reason": "max_correction_attempts",
            "bot_disabled_time": datetime.now(TZ).isoformat(),
            "pending_intent": None
        })
        
        # Send handoff message
        handoff_text = t("handoff_max_corrections", lang)
        send_handoff_message(cid, handoff_text)
        
    else:
        # Ask for more corrections
        correction_text = t("ask_for_more_corrections", lang)
        send_text_with_duplicate_check(cid, correction_text)
        
        # Set state to wait for more corrections
        set_conv_attrs(cid, {
            "waiting_for_corrections": True,
            "waiting_for_corrected_confirmation": False,
            "corrected_info": None,
            "pending_intent": None
        })

def process_preferences_and_suggest_slots(cid, preferences_text, lang):
    """Process user preferences with AI and suggest real calendar slots"""
    print(f"🤖 Processing preferences: {preferences_text}")
    
    # Analyze preferences with OpenAI to extract time preferences
    analysis = analyze_preferences_with_openai(preferences_text, cid)
    
    # Store preferences in conversation attributes
    set_conv_attrs(cid, {
        "preferred_days": analysis.get("preferred_days", []),
        "preferred_times": analysis.get("preferred_times", []),
        "user_preferences": preferences_text,
        "waiting_for_preferences": False
    })
    
    # Get real calendar slots based on preferences
    conv_attrs = get_conv_attrs(cid)
    profile_name = conv_attrs.get("planning_profile", "new")
    lesson_type = conv_attrs.get("lesson_type", "trial")
    
    # Convert AI analysis to preferred times string
    preferred_times_parts = []
    
    # Add preferred days
    if analysis.get("preferred_days"):
        preferred_times_parts.extend(analysis["preferred_days"])
    
    # Add preferred times
    if analysis.get("preferred_times"):
        preferred_times_parts.extend(analysis["preferred_times"])
    
    # Combine into single string for calendar integration
    preferred_times_str = " ".join(preferred_times_parts)
    set_conv_attrs(cid, {"preferred_times": preferred_times_str})
    
    print(f"📅 Using preferences: {preferred_times_str}")
    
    # Get available slots from real calendar
    try:
        from calendar_integration import get_available_slots
        
        now = datetime.now(TZ)
        start_date = now + timedelta(days=1)
        end_date = now + timedelta(days=14)
        
        # Parse preferred times for calendar
        preferred_time_list = []
        if preferred_times_str:
            # Extract specific times
            import re
            time_pattern = r'\b(\d{1,2}):?(\d{2})?\b'
            times = re.findall(time_pattern, preferred_times_str)
            for hour, minute in times:
                if minute:
                    preferred_time_list.append(f"{hour.zfill(2)}:{minute}")
                else:
                    preferred_time_list.append(f"{hour.zfill(2)}:00")
            
            # Add general time preferences
            if "avond" in preferred_times_str or "evening" in preferred_times_str:
                preferred_time_list.extend(["17:00", "18:00", "19:00"])
            if "middag" in preferred_times_str or "afternoon" in preferred_times_str:
                preferred_time_list.extend(["14:00", "15:00", "16:00"])
            if "ochtend" in preferred_times_str or "morning" in preferred_times_str:
                preferred_time_list.extend(["09:00", "10:00", "11:00"])
        
        # Get real calendar slots
        available_slots = get_available_slots(
            start_date=start_date,
            end_date=end_date,
            preferred_times=preferred_time_list if preferred_time_list else None,
            lesson_type=lesson_type
        )
        
        if available_slots:
            # Create quick reply options from real calendar
            options = []
            for slot in available_slots[:8]:  # Limit to 8 slots
                options.append((slot["label"], slot["start_iso"]))
                print(f"📅 Real calendar slot: '{slot['label']}'")
            
            options.append((t("planning_more_options", lang), "more_options"))
            
            # Set pending intent to planning
            set_conv_attrs(cid, {"pending_intent": "planning"})
            
            # Get appropriate text
            if lesson_type == "premium":
                lesson_text = t("planning_premium_slots_real", lang)
            elif lesson_type == "trial":
                lesson_text = t("planning_trial_slots_real", lang)
            else:
                lesson_text = t("planning_regular_slots_real", lang)
            
            print(f"📅 Sending {len(options)} real calendar options")
            send_input_select_only(cid, lesson_text, options)
            return
            
    except Exception as e:
        print(f"❌ Error getting real calendar slots: {e}")
    
    # Fallback to default slot suggestion
    print(f"⚠️ Using fallback slot suggestion")
    suggest_available_slots(cid, profile_name, lang)


def handle_email_request(cid, contact_id, msg_content, lang):
    """Handle email request for trial lesson invoice"""
    print(f"📧 Email request: '{msg_content}'")
    
    # Smart email extraction
    import re
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find email in message
    email_match = re.search(email_pattern, msg_content)
    
    if email_match:
        # Valid email found
        email = email_match.group(0).strip()
        
        # Store email in contact attributes
        set_contact_attrs(contact_id, {"email": email})
        
        # Mark contact as existing customer after email confirmation
        # This completes the intake loop - they are now existing customers
        set_contact_attrs(contact_id, {
            "segment": "existing",  # Mark as existing customer
            "intake_completed": True,  # Mark intake as completed
            "customer_status": "active"  # Mark as active customer
        })
        
        # Send confirmation and show next steps
        confirmation_msg = f"📧 {t('email_thanks', lang, email=email)}\n\n{t('email_confirmation', lang)}"
        send_text_with_duplicate_check(cid, confirmation_msg)
        
        # Mark conversation as complete and show main menu
        set_conv_attrs(cid, {
            "pending_intent": "",
            "trial_booking_complete": True,
            "trial_booking_time": datetime.now(TZ).isoformat()
        })
        
        # Show main menu to allow further interaction
        show_info_menu(cid, lang)
        
        print(f"✅ Trial lesson booking complete - showing main menu")
        
        print(f"✅ Email extracted and stored: {email}")
    else:
        # No valid email found
        error_msg = t("email_invalid", lang)
        send_text_with_duplicate_check(cid, error_msg)
        print(f"❌ No valid email found in: {msg_content}")
        
        # Keep pending_intent as "ask_email" so user can try again

def check_trial_booking_time_and_show_menu(cid, contact_id, lang):
    """Check if enough time has passed since trial booking to show post-trial menu"""
    conv_attrs = get_conv_attrs(cid)
    contact_attrs = get_contact_attrs(contact_id)
    
    # Check if trial booking is complete
    if not conv_attrs.get("trial_booking_complete"):
        return False
    
    # Check if trial lesson time has passed
    trial_booking_time = conv_attrs.get("trial_booking_time")
    if not trial_booking_time:
        return False
    
    try:
        # Parse the booking time
        booking_dt = datetime.fromisoformat(trial_booking_time.replace('Z', '+00:00'))
        current_dt = datetime.now(TZ)
        
        # Calculate time difference
        time_diff = current_dt - booking_dt
        hours_passed = time_diff.total_seconds() / 3600
        
        print(f"⏰ Trial booking time: {booking_dt}, Current time: {current_dt}, Hours passed: {hours_passed:.1f}")
        
        # Only show menu if at least 6 hours have passed
        if hours_passed >= 6:
            print(f"✅ 6+ hours passed since trial booking - showing post-trial menu")
            show_post_trial_menu(cid, contact_id, lang)
            return True
        else:
            print(f"⏳ Only {hours_passed:.1f} hours passed - post-trial menu not ready yet")
            return False
            
    except Exception as e:
        print(f"❌ Error checking trial booking time: {e}")
        return False

def show_post_trial_menu(cid, contact_id, lang):
    """Show menu after trial lesson completion"""
    print(f"🎯 Showing post-trial menu in {lang}")
    
    # Send post-trial message
    send_text_with_duplicate_check(cid, t("post_trial_message", lang))
    
    # Show menu with options
    menu_title = t("post_trial_menu_title", lang)
    menu_options = [
        (t("post_trial_plan_all_lessons", lang), "plan_all_lessons"),
        (t("post_trial_plan_single_lesson", lang), "plan_single_lesson"),
        (t("post_trial_main_menu", lang), "go_to_main_menu"),
        (t("post_trial_handoff", lang), "handoff")
    ]
    
    try:
        set_conv_attrs(cid, {"pending_intent": "post_trial_action"})
    except Exception as e:
        print(f"⚠️ SSL error setting pending_intent: {e}")
    
    result = send_input_select_only(cid, menu_title, menu_options)
    print(f"🎯 Post-trial menu send result: {result}")

def create_payment_request(cid, contact_id, lang):
    """Create payment request"""
    conv_attrs = get_conv_attrs(cid)
    contact_attrs = get_contact_attrs(contact_id)
    
    # Generate order ID
    order_id = f"SPL-{datetime.now().strftime('%Y%m%d')}-{cid:04d}"
    set_conv_attrs(cid, {"order_id": order_id})
    
    # Create payment link via module handler
    payment_link = _create_payment_link(
        contact_attrs.get("segment", "new"),
        60,  # minutes
        order_id,
        cid,
        conv_attrs.get("learner_name", "Student"),
        "1on1",
        contact_attrs.get("school_level", "adult"),
        conv_attrs.get("program", "none")
    )
    
    # Add payment labels and status
    add_conv_labels(cid, ["status:awaiting_pay"])
    set_conv_attrs(cid, {"payment_status": "pending"})
    if contact_attrs.get("segment") == "weekend":
        add_conv_labels(cid, ["price_custom"])
    
    # Send payment link
    send_text_with_duplicate_check(cid, t("payment_link", lang, link=payment_link))
    set_conv_attrs(cid, {"pending_intent": ""})

# Stripe webhook is handled in modules.routes.stripe

# Payment success handling is now in modules.handlers.payment

def handle_faq_request(cid, contact_id, msg_content, lang):
    return _faq(cid, contact_id, msg_content, lang)

# -----------------------------------------------------------------------------
# Delegate remaining core handler functions to modules (backward-compatibility)
# This ensures any internal references call the modular implementations.
# -----------------------------------------------------------------------------
handle_message_created = _handle_message_created_mod

start_intake_flow = _start_intake_flow_mod
handle_intake_step = _handle_intake_step_mod
handle_prefill_confirmation = _handle_prefill_confirmation_mod
handle_corrected_prefill_confirmation = _handle_corrected_prefill_confirmation_mod
show_prefill_action_menu = _show_prefill_action_menu_mod

start_planning_flow = _start_planning_flow_mod
handle_planning_selection = _handle_planning_selection_mod
handle_trial_lesson_mode_selection = _handle_trial_lesson_mode_selection_mod
ask_trial_lesson_mode = _ask_trial_lesson_mode_mod
ask_for_preferences_and_suggest_slots = _ask_for_preferences_and_suggest_slots_mod
suggest_available_slots = _suggest_available_slots_mod
handle_email_request = _handle_email_request_mod
check_trial_booking_time_and_show_menu = _check_trial_booking_time_and_show_menu_mod
show_post_trial_menu = _show_post_trial_menu_mod
create_payment_request = _create_payment_request_mod

show_main_menu = _show_main_menu_mod
show_segment_menu = _show_segment_menu_mod
handle_menu_selection = _handle_menu_selection_mod
show_info_menu = _show_info_menu_mod
handle_info_menu_selection = _handle_info_menu_selection_mod
show_work_method_info = _show_work_method_info_mod
show_services_info = _show_services_info_mod
show_workshops_info = _show_workshops_info_mod
show_handoff_menu = _show_handoff_menu_mod
handle_handoff_menu_selection = _handle_handoff_menu_selection_mod

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True) 