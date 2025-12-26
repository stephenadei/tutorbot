#!/usr/bin/env python3
"""
Conversation Handlers for TutorBot

This module contains conversation-related handlers and utilities.
"""

import os
import requests
from typing import Dict, Any

# Import dependencies
from modules.utils.cw_api import (
    get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs
)
from modules.utils.text_helpers import (
    send_text_with_duplicate_check, t, send_admin_warning
)
from modules.utils.mapping import detect_segment
from modules.utils.language import detect_language_from_message
from modules.handlers.intake import (
    handle_intake_step,
    handle_prefill_confirmation,
    handle_corrected_prefill_confirmation,
    start_intake_flow
)
from modules.handlers.menu import (
    handle_menu_selection,
    handle_info_menu_selection,
    handle_info_follow_up_selection,
    handle_handoff_menu_selection,
    handle_faq_request,
    handle_tariffs_follow_up_selection,
    show_main_menu
)
from modules.handlers.planning import (
    handle_planning_selection,
    handle_trial_lesson_mode_selection,
    handle_email_request,
    handle_different_preference_request,
    handle_new_time_preference
)
from modules.integrations.openai_service import prefill_intake_from_message

def is_bot_disabled(cid):
    """Check if bot is disabled for this conversation"""
    conv_attrs = get_conv_attrs(cid)
    return conv_attrs.get("bot_disabled", False)

def handle_message_created(data: Dict[str, Any]):
    """Main message processing handler - moved from main.py"""
    # Extract data from the webhook structure
    conversation = data.get("conversation", {})
    contact = data.get("contact", {})
    sender = data.get("sender", {})
    content = data.get("content", "")
    # Handle interactive button payloads (Chatwoot may send payload or submitted_values)
    message_obj = data.get("message") or {}
    content_attributes = data.get("content_attributes") or message_obj.get("content_attributes") or {}
    if isinstance(content_attributes, dict):
        if content_attributes.get("payload"):
            content = content_attributes.get("payload")
            print(f"🔘 Interactive payload detected -> content='{content}'")
        elif isinstance(content_attributes.get("submitted_values"), list) and content_attributes["submitted_values"]:
            sv = content_attributes["submitted_values"][0]
            # Prefer explicit value; fall back to title
            content = (sv.get("value") or sv.get("title") or content)
            print(f"🔘 Interactive submitted_values detected -> content='{content}'")
    
    # Try different possible locations for IDs
    cid = conversation.get("id")
    contact_id = contact.get("id") or sender.get("id")
    
    if not cid or not contact_id:
        print("❌ Missing conversation_id or contact_id in message data")
        print(f"🔍 Debug - conversation: {conversation}")
        print(f"🔍 Debug - contact: {contact}")
        print(f"🔍 Debug - sender: {sender}")
        print(f"🔍 Debug - full data: {data}")
        return
    
    print(f"📨 Processing message: '{content[:50]}...' in conversation {cid}")
    
    # Check if bot is disabled
    if is_bot_disabled(cid):
        print(f"🤖 Bot disabled for conversation {cid}")
        return
    
    # Get conversation and contact attributes
    conv_attrs = get_conv_attrs(cid)
    contact_attrs = get_contact_attrs(contact_id)
    
    # Detect language if not set
    lang = contact_attrs.get("language", "nl")
    
    # Check for admin commands (WIPECONTACTS) - MUST BE FIRST!
    if content.upper() == "WIPECONTACTS":
        print(f"🧹 ADMIN COMMAND: WIPECONTACTS detected from contact {contact_id}")
        send_text_with_duplicate_check(cid, "🧹 *ADMIN COMMAND DETECTED*\n\n⚠️ Dit zal alle contacten en gesprekken permanent verwijderen. Deze actie kan niet ongedaan kan worden gemaakt.\n\nType 'JA WIPE' om te bevestigen of 'ANNULEREN' om te stoppen.")
        # Set pending intent for wipe confirmation
        set_conv_attrs(cid, {"pending_intent": "wipe_confirmation"})
        return
    
    # Handle wipe confirmation
    if conv_attrs.get("pending_intent") == "wipe_confirmation":
        handle_wipe_confirmation(cid, contact_id, content, lang)
        return
    
    # Handle intake flow
    if conv_attrs.get("pending_intent") == "intake":
        print(f"📋 Processing intake step")
        print(f"🔍 Intake step: {conv_attrs.get('intake_step')}")
        print(f"🔍 Message content: '{content}'")
        print(f"🔍 Full conv_attrs: {conv_attrs}")
        handle_intake_step(cid, contact_id, content, lang)
        return
    else:
        print(f"🔍 Not in intake flow - pending_intent: {conv_attrs.get('pending_intent')}")
    
    # Handle planning flow
    if conv_attrs.get("pending_intent") == "planning":
        print(f"📅 Processing planning selection")
        handle_planning_selection(cid, contact_id, content, lang)
        return
    
    # Handle new time preference
    if conv_attrs.get("pending_intent") == "new_time_preference":
        print(f"📅 Processing new time preference")
        handle_new_time_preference(cid, contact_id, content, lang)
        return
    
    # Handle trial lesson mode selection
    if conv_attrs.get("pending_intent") == "trial_lesson_mode_selection":
        print(f"📱 Processing trial lesson mode selection")
        handle_trial_lesson_mode_selection(cid, contact_id, content, lang)
        return
    
    # Handle prefill confirmation
    if conv_attrs.get("pending_intent") == "prefill_confirmation":
        print(f"✅ Processing prefill confirmation")
        handle_prefill_confirmation(cid, contact_id, content, lang)
        return
    
    # Handle corrected prefill confirmation
    if conv_attrs.get("pending_intent") == "corrected_prefill_confirmation":
        print(f"✅ Processing corrected prefill confirmation")
        handle_corrected_prefill_confirmation(cid, contact_id, content, lang)
        return
    
    # Handle menu selections
    if conv_attrs.get("pending_intent") == "menu_selection":
        print(f"📋 Processing menu selection")
        handle_menu_selection(cid, contact_id, content, lang)
        return

    # Handle prefill action selections
    if conv_attrs.get("pending_intent") == "prefill_action":
        print(f"🎯 Processing prefill action selection")
        from modules.handlers.intake import handle_prefill_action_selection
        handle_prefill_action_selection(cid, contact_id, content, lang)
        return
    
    # Handle tariffs follow-up selections
    if conv_attrs.get("pending_intent") == "tariffs_follow_up":
        print(f"💰 Processing tariffs follow-up selection")
        handle_tariffs_follow_up_selection(cid, contact_id, content, lang)
        return
    
    # Handle info menu selections
    if conv_attrs.get("pending_intent") == "info_menu_selection":
        print(f"ℹ️ Processing info menu selection")
        handle_info_menu_selection(cid, contact_id, content, lang)
        return
    
    # Handle info follow-up menu selections
    if conv_attrs.get("pending_intent") == "info_follow_up":
        print(f"📄 Processing info follow-up selection")
        handle_info_follow_up_selection(cid, contact_id, content, lang)
        return
    
    # Handle handoff menu selections
    if conv_attrs.get("pending_intent") == "handoff_menu_selection":
        print(f"🤝 Processing handoff menu selection")
        handle_handoff_menu_selection(cid, contact_id, content, lang)
        return
    
    # Handle email request
    if conv_attrs.get("pending_intent") == "email_request":
        print(f"📧 Processing email request")
        handle_email_request(cid, contact_id, content, lang)
        return
    
    # Handle FAQ request
    if conv_attrs.get("pending_intent") == "faq_request":
        print(f"❓ Processing FAQ request")
        handle_faq_request(cid, contact_id, content, lang)
        return

    # If prefill was confirmed, prefer action menu flow
    if conv_attrs.get("use_prefill"):
        print(f"🎯 Prefill state detected before routing - showing prefill action menu")
        from modules.handlers.intake import show_prefill_action_menu
        show_prefill_action_menu(cid, contact_id, lang)
        return
    
    # Check if this is the first message in the conversation and we have OpenAI available
    # AND we're not already in prefill_confirmation state (to prevent re-processing)
    # AND we haven't already processed this exact message for prefill
    # AND this is not a response to a prefill confirmation
    if (not conv_attrs.get("has_been_prefilled") and 
        not conv_attrs.get("pending_intent") == "prefill_confirmation" and 
        not conv_attrs.get("prefill_processed_for_message") == content and
        not conv_attrs.get("prefill_confirmation_sent") and
        os.getenv("OPENAI_API_KEY")):
        
        # Check if this is a detailed message (not just a greeting)
        # Look for common greeting words and check if there's substantial content beyond that
        greeting_words = ["hallo", "hello", "hi", "hey", "goedemorgen", "goedemiddag", "goedenavond", "good morning", "good afternoon", "good evening"]
        msg_lower = content.lower().strip()
        
        # Check if message contains greeting words (use word boundaries to avoid false matches)
        has_greeting = any(f" {word} " in f" {msg_lower} " for word in greeting_words) or msg_lower in greeting_words
        
        # If it's just a greeting (short message with only greeting words), skip prefill
        if has_greeting and len(content.strip()) < 30:
            print(f"👋 Short greeting detected - skipping prefill, will show bot introduction")
            # Send bot introduction before proceeding with normal flow
            detected_lang = contact_attrs.get("language") or detect_language_from_message(content)
            other_lang = "English" if detected_lang == "nl" else "Nederlands"
            welcome_msg = t("bot_introduction_enhanced", detected_lang, detected_lang=detected_lang, other_lang=other_lang)
            try:
                send_text_with_duplicate_check(cid, welcome_msg)
            except Exception as e:
                print(f"⚠️ Failed to send bot introduction: {e}")
            # After greeting, show the main menu
            try:
                show_main_menu(cid, contact_id, detected_lang)
            except Exception as e:
                print(f"⚠️ Failed to show main menu after greeting: {e}")
                # Fallback to normal flow if menu fails
                process_new_message(cid, contact_id, content, detected_lang)
        elif len(content.strip()) >= 30:
            # For longer messages, always do prefill regardless of greeting words
            print(f"📝 Long message detected - proceeding with prefill analysis")
            
            # For detailed messages, detect language first if not already set
            if not contact_attrs.get("language"):
                detected_lang = detect_language_from_message(content)
                print(f"🌍 Auto-detected language for prefill: {detected_lang}")
                set_contact_attrs(contact_id, {"language": detected_lang})
                lang = detected_lang
            else:
                lang = contact_attrs.get("language")
            
            print(f"🤖 Attempting to prefill intake from first message in {lang}...")
            prefilled = prefill_intake_from_message(content, cid, send_admin_warning)
            
            if prefilled:
                # Apply prefilled information to conversation attributes
                current_attrs = get_conv_attrs(cid)
                current_attrs.update(prefilled)
                current_attrs["has_been_prefilled"] = True
                current_attrs["prefill_processed_for_message"] = content  # Mark this message as processed
                
                # If we created a child contact, also store the child contact ID
                if prefilled.get("child_contact_id"):
                    current_attrs["child_contact_id"] = prefilled["child_contact_id"]
                    print(f"📝 Stored child contact ID {prefilled['child_contact_id']} in conversation attributes")
                
                set_conv_attrs(cid, current_attrs)
                
                # Also set contact attributes if we have a contact
                contact_attrs = get_contact_attrs(contact_id)
                contact_attrs.update(prefilled)
                set_contact_attrs(contact_id, contact_attrs)
                
                # Show user what was detected with comprehensive confirmation
                detected_info = []
                
                # Basic information
                if prefilled.get("learner_name"):
                    detected_info.append(f"👤 *{t('name_label', lang)}*: {prefilled['learner_name']}")
                
                if prefilled.get("school_level"):
                    level_display = {
                        "po": t("level_po", lang),
                        "vmbo": "VMBO", 
                        "havo": "HAVO",
                        "vwo": "VWO",
                        "mbo": "MBO",
                        "university_wo": t("level_university_wo", lang),
                        "university_hbo": t("level_university_hbo", lang),
                        "adult": t("level_adult", lang)
                    }
                    level_text = level_display.get(prefilled['school_level'], prefilled['school_level'])
                    detected_info.append(f"🎓 *{t('level_label', lang)}*: {level_text}")
                
                # Subject information - show only the specific variant if available
                if prefilled.get("topic_secondary"):
                    detected_info.append(f"📚 *{t('subject_label', lang)}*: {prefilled['topic_secondary']}")
                elif prefilled.get("topic_primary"):
                    topic_display = {
                        "math": t("subject_math", lang),
                        "stats": t("subject_stats", lang), 
                        "english": t("subject_english", lang),
                        "programming": t("subject_programming", lang),
                        "science": t("subject_science", lang),
                        "chemistry": t("subject_chemistry", lang)
                    }
                    topic_text = topic_display.get(prefilled['topic_primary'], prefilled['topic_primary'])
                    detected_info.append(f"📚 *{t('subject_label', lang)}*: {topic_text}")
                
                # Additional information
                if prefilled.get("goals"):
                    detected_info.append(f"🎯 *{t('goals_label', lang)}*: {prefilled['goals']}")
                
                if prefilled.get("preferred_times"):
                    detected_info.append(f"⏰ *{t('preferred_times_label', lang)}*: {prefilled['preferred_times']}")
                
                if prefilled.get("location_preference"):
                    detected_info.append(f"📍 *{t('location_preference_label', lang)}*: {prefilled['location_preference']}")
                
                if prefilled.get("contact_name") and prefilled.get("for_who") != "self":
                    detected_info.append(f"👤 *{t('contact_person_label', lang)}*: {prefilled['contact_name']}")
                
                if prefilled.get("for_who"):
                    for_who_display = {
                        "self": t("for_who_self", lang),
                        "child": t("for_who_child", lang),
                        "student": t("for_who_student", lang),
                        "other": t("for_who_other", lang)
                    }
                    for_who_text = for_who_display.get(prefilled['for_who'], prefilled['for_who'])
                    detected_info.append(f"👥 *{t('for_who_label', lang)}*: {for_who_text}")
                
                # Show detected information and ask for confirmation
                if detected_info:
                    # Always show all detected information, don't truncate
                    # This helps users see what was actually detected
                    print(f"📋 Showing {len(detected_info)} detected fields: {[info.split(':')[0] for info in detected_info]}")
                    
                    # Send greeting/introduction first (do not persist to avoid attribute write here).
                    # Avoid duplicate "Perfect" messages later in flow.
                    try:
                        other_lang = "English" if lang == "nl" else "Nederlands"
                        welcome_msg = t("bot_introduction_detailed", lang, detected_lang=lang, other_lang=other_lang)
                        send_text_with_duplicate_check(cid, welcome_msg, persist=False)
                        print(f"✅ Greeting message sent successfully")
                    except Exception as e:
                        print(f"⚠️ Failed to send greeting message: {e}")

                    # Create the summary message
                    summary_msg = f"{t('prefill_confirmation_header', lang)}\n\n" + "\n".join(detected_info) + f"\n\n{t('prefill_confirmation_footer', lang)}"
                    
                    # Step 1: Send the summary as text first (do not persist to avoid conv-attr write here)
                    try:
                        send_text_with_duplicate_check(cid, summary_msg, persist=False)
                        print(f"✅ Summary message sent successfully")
                    except Exception as e:
                        print(f"⚠️ Failed to send summary message: {e}")
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
                        from modules.utils.text_helpers import send_input_select_only
                        result = send_input_select_only(cid, menu_title, menu_options)
                        print(f"🎯 Prefill confirmation menu send result: {result}")
                    except Exception as e:
                        print(f"❌ Failed to send confirmation menu: {e}")
                        # Fallback: send as text with options
                        fallback_text = f"{menu_title}\n\n" + "\n".join([f"• {option[0]}" for option in menu_options])
                        send_text_with_duplicate_check(cid, fallback_text, persist=False)
                        print(f"📝 Sent fallback text menu due to input_select failure")
                    
                    # Set pending intent for prefill confirmation (single path)
                    set_conv_attrs(cid, {"pending_intent": "prefill_confirmation", "prefill_confirmation_sent": True})
                    return
                else:
                    print(f"⚠️ No information detected from prefill - proceeding with normal flow")
                    process_new_message(cid, contact_id, content, lang)
            else:
                print(f"⚠️ Prefill returned empty - proceeding with normal flow")
                process_new_message(cid, contact_id, content, lang)
        else:
            # Short message or greeting - proceed with normal flow
            process_new_message(cid, contact_id, content, lang)
    else:
        # Not first message or already prefilled - proceed with normal flow
        process_new_message(cid, contact_id, content, lang)

def handle_wipe_confirmation(cid, contact_id, msg_content, lang):
    """Handle wipe confirmation - moved from main.py"""
    print(f"🧹 Processing wipe confirmation: '{msg_content}'")
    
    if msg_content.upper() in ["JA WIPE", "JA", "YES", "CONFIRM"]:
        print(f"🧹 User confirmed wipe - starting contact deletion...")
        
        # Send status message
        send_text_with_duplicate_check(cid, "🧹 *WIPE GESTART*\n\nBezig met verwijderen van alle contacten en gesprekken...")
        
        try:
            # Configuration
            CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
            ACC_ID = os.getenv("CW_ACC_ID", "1")
            ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")
            
            if not ADMIN_TOKEN:
                send_text_with_duplicate_check(cid, "❌ *WIPE FAILED*\n\nADMIN_TOKEN niet geconfigureerd.")
                set_conv_attrs(cid, {"pending_intent": None})
                return
            
            headers = {
                "api_access_token": ADMIN_TOKEN,
                "Content-Type": "application/json"
            }
            
            # Get all contacts
            url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                send_text_with_duplicate_check(cid, f"❌ *WIPE FAILED*\n\nKon contacten niet ophalen: {response.status_code}")
                set_conv_attrs(cid, {"pending_intent": None})
                return
            
            contacts = response.json().get("payload", [])
            print(f"📋 Found {len(contacts)} contacts to delete")
            
            # Delete each contact
            deleted_count = 0
            for contact in contacts:
                contact_id_to_delete = contact.get("id")
                if contact_id_to_delete:
                    delete_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts/{contact_id_to_delete}"
                    delete_response = requests.delete(delete_url, headers=headers)
                    
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted contact {contact_id_to_delete}")
                        deleted_count += 1
                    else:
                        print(f"❌ Failed to delete contact {contact_id_to_delete}: {delete_response.status_code}")
            
            # Send completion message
            completion_msg = f"🎉 *WIPE VOLTOOID*\n\n✅ {deleted_count} contacten en gesprekken verwijderd\n\n⚠️ Alle data is permanent verwijderd!"
            send_text_with_duplicate_check(cid, completion_msg)
            
            print(f"🎉 WhatsApp wipe completed: {deleted_count} contacts deleted")
            
        except Exception as e:
            error_msg = f"❌ *WIPE ERROR*\n\nEr is een fout opgetreden: {str(e)}"
            send_text_with_duplicate_check(cid, error_msg)
            print(f"❌ Error during WhatsApp wipe: {e}")
        
        # Clear pending intent
        set_conv_attrs(cid, {"pending_intent": None})
        return
    
    elif msg_content.upper() in ["ANNULEREN", "CANCEL", "NEE", "NO", "STOP"]:
        print(f"🧹 User cancelled wipe")
        send_text_with_duplicate_check(cid, "✅ *WIPE GEANNULEERD*\n\nGeen contacten verwijderd.")
        set_conv_attrs(cid, {"pending_intent": None})
        return
    else:
        print(f"🧹 Invalid wipe confirmation response: '{msg_content}'")
        send_text_with_duplicate_check(cid, "❓ *ONBEKEND ANTWOORD*\n\nType 'JA WIPE' om te bevestigen of 'ANNULEREN' om te stoppen.")
        return

def process_new_message(cid, contact_id, content, lang):
    """Process a new message - moved from main.py"""
    print(f"🆕 Processing new message in conversation {cid}")
    
    # Get conversation and contact attributes
    conv_attrs = get_conv_attrs(cid)
    contact_attrs = get_contact_attrs(contact_id)
    
    # Detect segment
    segment = detect_segment(contact_id)
    
    # Check if this is an existing customer
    if is_existing_customer(contact_attrs):
        print(f"👤 Existing customer detected")
        handle_existing_customer_message(cid, contact_id, content, lang, segment)
    else:
        print(f"🆕 New customer detected")
        handle_new_customer_message(cid, contact_id, content, lang, segment)

def is_existing_customer(contact_attrs):
    """Check if contact is an existing customer - moved from main.py"""
    return (contact_attrs.get("customer_since") or 
            contact_attrs.get("has_paid_lesson") or
            contact_attrs.get("has_completed_intake") or
            contact_attrs.get("intake_completed") or
            contact_attrs.get("trial_lesson_completed") or
            contact_attrs.get("lesson_booked") or
            contact_attrs.get("customer_status") == "active")

def has_completed_intake(conv_attrs):
    """Check if intake is completed - moved from main.py"""
    return conv_attrs.get("intake_completed", False)

def handle_existing_customer_message(cid, contact_id, content, lang, segment):
    """Handle message from existing customer - moved from main.py"""
    conv_attrs = get_conv_attrs(cid)
    
    # Check if intake is completed
    if has_completed_intake(conv_attrs):
        print(f"✅ Intake completed - showing main menu")
        show_main_menu(cid, contact_id, lang)
    else:
        print(f"📋 Intake not completed - starting intake flow")
        start_intake_flow(cid, contact_id, lang)

def handle_new_customer_message(cid, contact_id, content, lang, segment):
    """Handle message from new customer - moved from main.py"""
    print(f"🆕 New customer message")
    conv_attrs = get_conv_attrs(cid)
    
    # Check if we're in intake choice flow - if so, delegate to intake handler
    if conv_attrs.get("pending_intent") == "intake_choice":
        print(f"📋 In intake choice flow - delegating to intake handler")
        from modules.handlers.intake import handle_intake_step
        handle_intake_step(cid, contact_id, content, lang)
        return
    
    # If we already did prefill or just confirmed, show the action menu instead of restarting intake
    if conv_attrs.get("prefill_confirmation_sent") or conv_attrs.get("has_been_prefilled") or conv_attrs.get("use_prefill"):
        print(f"🎯 Prefill state detected (confirmation/menu). Showing action menu instead of intake")
        from modules.handlers.intake import show_prefill_action_menu
        show_prefill_action_menu(cid, contact_id, lang)
        return

    print(f"🆕 No prefill state - starting intake flow")
    start_intake_flow(cid, contact_id, lang)
