#!/usr/bin/env python3
"""
Planning Handlers for TutorBot

This module contains planning flow handlers and utilities.
"""

from typing import Dict, Any

# Import dependencies
from modules.utils.cw_api import (
    get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs
)
from modules.utils.text_helpers import (
    send_text_with_duplicate_check, t, send_admin_warning, send_input_select_only
)
from modules.utils.mapping import detect_segment
from modules.integrations.openai_service import interpret_slot_selection_with_openai
from modules.core.config import TZ
from modules.utils.attribute_manager import update_contact_attrs, add_labels_safe
from modules.handlers.menu import show_main_menu

def start_planning_flow(cid, contact_id, lang):
    """Start the planning flow - moved from main.py"""
    print(f"📅 Starting planning flow for conversation {cid}")
    
    # Get segment
    segment = detect_segment(contact_id)
    
    # Check if urgent session
    conv_attrs = get_conv_attrs(cid)
    if conv_attrs.get("urgent_session"):
        print(f"🚨 Urgent session detected")
        handle_urgent_session(cid, contact_id, lang)
        return
    
    # Check if trial lesson mode
    if conv_attrs.get("trial_lesson_mode"):
        print(f"📱 Trial lesson mode detected")
        ask_trial_lesson_mode(cid, contact_id, lang)
        return
    
    # Normal planning flow
    print(f"📅 Normal planning flow")
    ask_for_preferences_and_suggest_slots(cid, segment, lang)

def handle_urgent_session(cid, contact_id, lang):
    """Handle urgent session - moved from main.py"""
    print(f"🚨 Handling urgent session")
    
    # Set urgent session attributes
    set_conv_attrs(cid, {
        "urgent_session": True,
        "session_duration": 120,  # 2 hours
        "pending_intent": "planning"
    })
    
    # Show urgent session message
    send_text_with_duplicate_check(cid, t("urgent_session_message", lang))
    
    # Start immediate planning
    ask_for_preferences_and_suggest_slots(cid, "new", lang)

def ask_trial_lesson_mode(cid, contact_id, lang):
    """Ask for trial lesson mode - moved from main.py"""
    print(f"📱 Asking for trial lesson mode")
    
    # Set pending intent for trial lesson mode selection
    set_conv_attrs(cid, {"pending_intent": "trial_lesson_mode_selection"})
    
    send_text_with_duplicate_check(cid, t("trial_lesson_mode_question", lang))

def handle_trial_lesson_mode_selection(cid, contact_id, msg_content, lang):
    """Handle trial lesson mode selection - moved from main.py"""
    print(f"📱 Processing trial lesson mode selection: '{msg_content}'")
    
    # Map selection to mode
    selection = msg_content.lower().strip()
    
    if selection in ["1", "online", "digitaal", "zoom"]:
        print(f"📱 User selected: Online trial lesson")
        set_conv_attrs(cid, {"trial_lesson_mode": "online", "lesson_mode": "online"})
        ask_for_preferences_and_suggest_slots(cid, "new", lang)
    elif selection in ["2", "offline", "fysiek", "in_person", "fysieke les", "locatie"]:
        print(f"📱 User selected: Offline trial lesson")
        # Enforce physical lesson constraints: Science Park only, weekdays only
        set_conv_attrs(cid, {
            "trial_lesson_mode": "fysiek",
            "lesson_mode": "fysiek",
            "location_preference": "Science Park",
            "allowed_weekdays": [0, 1, 2, 3, 4]  # Mon–Fri
        })
        ask_for_preferences_and_suggest_slots(cid, "new", lang)
    else:
        # Invalid selection
        send_text_with_duplicate_check(cid, t("trial_lesson_mode_invalid", lang))
        print(f"❌ Invalid trial lesson mode selection: '{msg_content}'")

def ask_for_preferences_and_suggest_slots(cid, profile_name, lang):
    """Ask for preferences and suggest slots - moved from main.py"""
    print(f"📅 Asking for preferences and suggesting slots")
    
    # Set pending intent for planning
    set_conv_attrs(cid, {"pending_intent": "planning"})
    
    # Ask for preferences
    send_text_with_duplicate_check(cid, t("ask_for_preferences", lang))

def suggest_available_slots(cid, profile_name, lang):
    """Suggest available slots - moved from main.py"""
    print(f"📅 Suggesting available slots")
    
    try:
        # Get available slots
        slots = suggest_slots(cid, profile_name)
        
        if not slots:
            print("⚠️ No real slots available - generating fallback suggestions")
            slots = generate_fallback_slots(cid, profile_name)
            # Let the user know we propose alternatives
            try:
                send_text_with_duplicate_check(cid, t("no_slots_available", lang))
            except Exception:
                pass

        # Persist the current proposals for later AI interpretation
        set_conv_attrs(cid, {"suggested_slots": slots, "pending_intent": "planning"})

        # Present as quick-reply input_select options
        options = []
        for slot in slots[:8]:
            label = slot.get("label") or slot.get("start")
            value = slot.get("start_iso") or slot.get("start")
            if label and value:
                options.append((label, value))
        if not options:
            # Fallback to plain text if nothing sensible
            slots_text = format_slots_for_display(slots, lang)
            send_text_with_duplicate_check(cid, slots_text)
        else:
            title = t("planning_regular_slots", lang)
            send_input_select_only(cid, title, options)
            
    except Exception as e:
        print(f"❌ Error suggesting slots: {e}")
        send_admin_warning(f"Error suggesting slots: {e}")
        send_text_with_duplicate_check(cid, t("slot_suggestion_error", lang))

def format_slots_for_display(slots, lang):
    """Format slots for display - moved from main.py"""
    # TODO: Implement slot formatting
    return t("slots_available", lang).format(slots="[Slot formatting not implemented yet]")

def suggest_slots(conversation_id, profile_name):
    """Suggest available slots - moved from main.py"""
    # TODO: Implement slot suggestion
    print(f"📅 Slot suggestion not implemented yet")
    return []

def generate_fallback_slots(conversation_id, profile_name):
    """Generate 6 reasonable fallback slots a few days in the future."""
    from datetime import datetime, timedelta
    conv = get_conv_attrs(conversation_id)
    lesson_type = conv.get("lesson_type", "trial")
    lesson_mode = conv.get("lesson_mode", "online")
    allowed_weekdays = conv.get("allowed_weekdays")  # optional list of ints 0=Mon

    slots = []
    now = datetime.now(TZ)
    days_ahead = 7
    # Trial lessons are 30 minutes between 17:00–19:00 on weekdays
    for i in range(1, days_ahead + 1):
        day = now + timedelta(days=i)
        if allowed_weekdays is not None and day.weekday() not in allowed_weekdays:
            continue
        # Skip weekends for trial lessons by default
        if lesson_type == "trial" and day.weekday() >= 5:
            continue
        # Choose hours based on type
        if lesson_type == "trial":
            candidate_hours = [17, 18]
            duration_min = 30
        else:
            candidate_hours = [14, 15, 16, 17, 18, 19]
            duration_min = 60
        for hour in candidate_hours:
            start_dt = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(minutes=duration_min)
            label = f"{start_dt.strftime('%a %d %b %H:%M')}–{end_dt.strftime('%H:%M')}"
            slots.append({
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "start_iso": start_dt.isoformat(),
                "label": label,
            })
            if len(slots) >= 6:
                return slots
    return slots

def handle_planning_selection(cid, contact_id, msg_content, lang):
    """Handle planning selection - moved from main.py"""
    print(f"📅 Processing planning selection: '{msg_content}'")
    
    # Map planning selection to action
    selection = msg_content.lower().strip()
    
    if selection in ["1", "boek", "book", "reserveer"]:
        print(f"📅 User selected: Book slot")
        handle_slot_booking(cid, contact_id, lang)
    elif selection in ["2", "meer", "more", "andere tijden"]:
        print(f"📅 User selected: More slots")
        suggest_available_slots(cid, "new", lang)
    elif selection in ["3", "email", "mail", "contact"]:
        print(f"📅 User selected: Email contact")
        handle_email_request(cid, contact_id, lang)
    elif selection in ["4", "terug", "back", "menu"]:
        print(f"📅 User selected: Back to menu")
        show_main_menu(cid, contact_id, lang)
    else:
        # Try OpenAI-assisted interpretation to map free text to a slot
        conv_attrs = get_conv_attrs(cid)
        profile_name = conv_attrs.get("planning_profile", "new")
        # Use the stored proposals if available
        slots = conv_attrs.get("suggested_slots") or suggest_slots(cid, profile_name) or []
        try:
            result = interpret_slot_selection_with_openai(msg_content, slots)
        except Exception as e:
            print(f"❌ Slot interpretation error: {e}")
            result = {"intent": "invalid"}
        if result.get("intent") == "more_options":
            suggest_available_slots(cid, profile_name, lang)
            return
        if result.get("intent") == "select" and result.get("chosen_iso"):
            # Simulate ISO timestamp handling path
            print(f"🤖 Interpreted selection -> {result['chosen_iso']}")
            handle_slot_booking(cid, contact_id, lang)
            return
        # Fallback invalid
        send_text_with_duplicate_check(cid, t("planning_invalid_selection", lang))
        print(f"❌ Invalid planning selection: '{msg_content}'")

def handle_slot_booking(cid, contact_id, lang):
    """Handle slot booking - moved from main.py"""
    print(f"📅 Handling slot booking")
    # Try to book the last interpreted selection or the first proposed slot as a placeholder
    conv = get_conv_attrs(cid)
    slots = conv.get("suggested_slots") or []
    if not slots:
        send_text_with_duplicate_check(cid, t("slot_suggestion_error", lang))
        return
    chosen = slots[0]
    start_iso = chosen.get("start_iso") or chosen.get("start")
    end_iso = chosen.get("end")
    if not start_iso or not end_iso:
        send_text_with_duplicate_check(cid, t("slot_suggestion_error", lang))
        return
    # Use main's booking helper if available
    try:
        from main import book_slot
        event = book_slot(
            cid,
            start_iso,
            end_iso,
            "Stephen's Privélessen — Proefles" if conv.get("lesson_type") == "trial" else "Stephen's Privélessen — Les",
            "Automatisch geboekt voorstel"
        )
        if event:
            # Update contact attributes to reflect booking
            update_contact_attrs(contact_id, {
                "lesson_booked": True,
                "has_completed_intake": True,
                "trial_lesson_completed": True if (conv.get("lesson_type") == "trial") else False,
                "lesson_mode": conv.get("lesson_mode", "online"),
            }, cid, note=f"📅 Slot geboekt: {chosen.get('label','')}")

            # Labels for status
            add_labels_safe(cid, ["status:booked"])
            send_text_with_duplicate_check(cid, t("trial_lesson_confirmed", lang, slot=chosen.get("label", "")))
            set_conv_attrs(cid, {"pending_intent": "ask_email"})
        else:
            send_text_with_duplicate_check(cid, t("slot_suggestion_error", lang))
    except Exception as e:
        print(f"❌ Error booking via main.book_slot: {e}")
        send_text_with_duplicate_check(cid, t("slot_suggestion_error", lang))

def handle_email_request(cid, contact_id, msg_content, lang):
    """Handle email request - moved from main.py"""
    print(f"📧 Processing email request: '{msg_content}'")
    
    # Set pending intent for email request
    set_conv_attrs(cid, {"pending_intent": "email_request"})
    
    # Ask for email
    send_text_with_duplicate_check(cid, t("email_request_question", lang))

def check_trial_booking_time_and_show_menu(cid, contact_id, lang):
    """Check trial booking time and show menu - moved from main.py"""
    print(f"📅 Checking trial booking time")
    
    # TODO: Implement trial booking time check
    show_post_trial_menu(cid, contact_id, lang)

def show_post_trial_menu(cid, contact_id, lang):
    """Show post trial menu - moved from main.py"""
    print(f"📅 Showing post trial menu")
    
    send_text_with_duplicate_check(cid, t("post_trial_menu", lang))

def create_payment_request(cid, contact_id, lang):
    """Create payment request - moved from main.py"""
    print(f"💳 Creating payment request")
    
    # TODO: Implement payment request creation
    send_text_with_duplicate_check(cid, t("payment_request_not_implemented", lang))
