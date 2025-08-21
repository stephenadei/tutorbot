#!/usr/bin/env python3
"""
Intake Handlers for TutorBot

This module contains intake flow handlers and utilities.
"""

from typing import Dict, Any
from datetime import datetime

# Import dependencies
from modules.utils.cw_api import (
    get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs
)
from modules.utils.text_helpers import (
    send_text_with_duplicate_check, t, send_admin_warning
)
from modules.handlers.planning import start_planning_flow
from modules.utils.mapping import (
    map_school_level, map_topic, is_prefill_sufficient_for_trial_lesson
)
from modules.utils.language import detect_language_from_message
from modules.integrations.openai_service import (
    analyze_preferences_with_openai,
    prefill_intake_from_message
)
from modules.utils.text_helpers import send_input_select_only, send_handoff_message, t, send_text_with_duplicate_check
from modules.utils.menu_guard import match_menu_selection
from modules.utils.mapping import get_appropriate_tariffs_key
from modules.handlers.menu import show_info_menu
from modules.handlers.planning import start_planning_flow
from modules.utils.attribute_manager import update_contact_attrs, add_labels_safe, remove_labels_safe

def start_intake_flow(cid, contact_id, lang):
    """Start the intake flow with choice between step-by-step and free text"""
    print(f"📋 Starting intake flow for conversation {cid}")
    
    # Set conversation attributes for intake
    set_conv_attrs(cid, {
        "pending_intent": "intake_choice",
        "intake_completed": False
    })
    
    # Offer both options: step-by-step or free text
    intro_text = t("intake_intro", lang)
    send_text_with_duplicate_check(cid, intro_text)
    
    # Show choice menu
    choice_options = [
        (t("intake_choice_step_by_step", lang), "step_by_step"),
        (t("intake_choice_free_text", lang), "free_text"),
        (t("intake_choice_handoff", lang), "handoff")
    ]
    send_input_select_only(cid, t("intake_choice_title", lang), choice_options)
    print(f"📋 Intake choice menu shown")


def show_prefill_action_menu(cid, contact_id, lang):
    """Show action menu after prefill confirmation"""
    try:
        set_conv_attrs(cid, {"pending_intent": "prefill_action"})
    except Exception:
        pass

    # If we have enough info, proactively show tariffs once before the action menu
    contact_attrs = get_contact_attrs(contact_id)
    school_level = contact_attrs.get("school_level", "")
    is_adult = contact_attrs.get("is_adult", False)
    if school_level:
        age_over_20 = is_adult or ("university" in str(school_level).lower()) or ("hbo" in str(school_level).lower())
        tariffs_key = get_appropriate_tariffs_key(school_level, age_over_20)
        if tariffs_key:
            try:
                send_text_with_duplicate_check(cid, t(tariffs_key, lang), persist=False)
            except Exception:
                pass

    # Options for both trial-first and urgent session
    # Brief explanation so users understand the two options
    try:
        send_text_with_duplicate_check(cid, t("prefill_action_menu_text", lang), persist=False)
    except Exception:
        pass

    action_menu_title = t("prefill_action_menu_title", lang)
    action_menu_options = [
        (t("prefill_action_trial_first", lang), "plan_trial_lesson"),
        (t("prefill_action_urgent_session", lang), "urgent_session"),
        (t("prefill_action_main_menu", lang), "go_to_main_menu"),
        (t("prefill_action_handoff", lang), "handoff"),
    ]
    send_input_select_only(cid, action_menu_title, action_menu_options)

def handle_intake_step(cid, contact_id, msg_content, lang):
    """Handle intake flow steps - moved from main.py"""
    conv_attrs = get_conv_attrs(cid)
    pending_intent = conv_attrs.get("pending_intent")
    intake_step = conv_attrs.get("intake_step")
    
    print(f"📋 Processing intake - pending_intent: {pending_intent}, step: {intake_step}")
    
    # Handle intake choice
    if pending_intent == "intake_choice":
        handle_intake_choice(cid, contact_id, msg_content, lang)
    # Handle free text intake
    elif pending_intent == "intake_free_text":
        handle_intake_free_text(cid, contact_id, msg_content, lang)
    # Handle free text confirmation
    elif pending_intent == "intake_free_text_confirm":
        handle_intake_free_text_confirm(cid, contact_id, msg_content, lang)
    # Handle step-by-step flow
    elif pending_intent == "intake" and intake_step:
        if intake_step == "for_who":
            handle_for_who_step(cid, contact_id, msg_content, lang)
        elif intake_step == "name":
            handle_name_step(cid, contact_id, msg_content, lang)
        elif intake_step == "school_level":
            handle_school_level_step(cid, contact_id, msg_content, lang)
        elif intake_step == "topic":
            handle_topic_step(cid, contact_id, msg_content, lang)
        elif intake_step == "preferences":
            handle_preferences_step(cid, contact_id, msg_content, lang)
        else:
            print(f"❌ Unknown intake step: {intake_step}")
            # Fallback to start
            start_intake_flow(cid, contact_id, lang)
    else:
        print(f"❌ Unknown intake state: pending_intent={pending_intent}, step={intake_step}")
        # Fallback to start
        start_intake_flow(cid, contact_id, lang)

def handle_intake_choice(cid, contact_id, msg_content, lang):
    """Handle intake choice between step-by-step and free text"""
    print(f"📋 Processing intake choice: '{msg_content}'")
    
    # Normalize the message content for matching
    normalized_content = msg_content.lower().strip()
    
    if msg_content == "step_by_step" or "stap-voor-stap" in normalized_content:
        print(f"📋 User chose step-by-step intake")
        # Start step-by-step flow
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "intake_step": "for_who"
        })
        
        # Show for_who options with buttons
        for_who_options = [
            (t("intake_for_who_self", lang), "self"),
            (t("intake_for_who_child", lang), "child"),
            (t("intake_for_who_other", lang), "other")
        ]
        send_input_select_only(cid, t("intake_for_who", lang), for_who_options)
        print(f"📋 Intake step: for_who (with buttons)")
        
    elif msg_content == "free_text" or "vrije tekst" in normalized_content:
        print(f"📋 User chose free text intake")
        # Start free text flow
        set_conv_attrs(cid, {
            "pending_intent": "intake_free_text"
        })
        
        # Ask for free text input with focus on key points
        free_text_prompt = t("intake_free_text_prompt", lang)
        send_text_with_duplicate_check(cid, free_text_prompt)
        print(f"📋 Free text intake started")
        
    elif msg_content == "handoff" or "stephen spreken" in normalized_content or "stephen" in normalized_content:
        print(f"📋 User chose handoff")
        send_handoff_message(cid, t("handoff_teacher", lang))
        
    else:
        print(f"❌ Invalid intake choice: '{msg_content}'")
        # Show choice menu again
        start_intake_flow(cid, contact_id, lang)

def handle_intake_free_text(cid, contact_id, msg_content, lang):
    """Handle free text intake with OpenAI analysis"""
    print(f"📋 Processing free text intake: '{msg_content}'")
    
    try:
        # Analyze with OpenAI
        analysis = prefill_intake_from_message(msg_content, cid)
        
        if analysis:
            # Show what was detected
            detected_info = []
            if analysis.get("learner_name"):
                detected_info.append(f"👤 **{t('name_label', lang)}**: {analysis['learner_name']}")
            if analysis.get("school_level"):
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
                level_text = level_display.get(analysis['school_level'], analysis['school_level'])
                detected_info.append(f"🎓 **{t('level_label', lang)}**: {level_text}")
            if analysis.get("topic_primary"):
                detected_info.append(f"📚 **{t('subject_label', lang)}**: {analysis['topic_primary']}")
            if analysis.get("goals"):
                detected_info.append(f"🎯 **{t('goals_label', lang)}**: {analysis['goals']}")
            if analysis.get("preferred_times"):
                detected_info.append(f"⏰ **{t('preferred_times_label', lang)}**: {analysis['preferred_times']}")
            
            if detected_info:
                summary_msg = f"📋 **{t('intake_free_text_detected', lang)}**\n\n" + "\n".join(detected_info)
                send_text_with_duplicate_check(cid, summary_msg)
                
                # Ask for confirmation
                confirm_options = [
                    (t("intake_free_text_confirm", lang), "confirm"),
                    (t("intake_free_text_correct", lang), "correct"),
                    (t("intake_free_text_handoff", lang), "handoff")
                ]
                set_conv_attrs(cid, {"pending_intent": "intake_free_text_confirm", "analysis": analysis})
                send_input_select_only(cid, t("intake_free_text_confirm_title", lang), confirm_options)
            else:
                # No information detected
                send_text_with_duplicate_check(cid, t("intake_free_text_no_info", lang))
                start_intake_flow(cid, contact_id, lang)
        else:
            # Analysis failed
            send_text_with_duplicate_check(cid, t("intake_free_text_failed", lang))
            start_intake_flow(cid, contact_id, lang)
            
    except Exception as e:
        print(f"❌ Error in free text intake: {e}")
        send_text_with_duplicate_check(cid, t("intake_free_text_error", lang))
        start_intake_flow(cid, contact_id, lang)

def handle_intake_free_text_confirm(cid, contact_id, msg_content, lang):
    """Handle free text intake confirmation"""
    print(f"📋 Processing free text confirmation: '{msg_content}'")
    
    conv_attrs = get_conv_attrs(cid)
    analysis = conv_attrs.get("analysis", {})
    
    if msg_content == "confirm":
        print(f"📋 User confirmed free text analysis")
        # Store the analyzed data
        if analysis.get("learner_name"):
            set_conv_attrs(cid, {"student_name": analysis["learner_name"]})
        if analysis.get("school_level"):
            set_conv_attrs(cid, {"school_level": analysis["school_level"]})
        if analysis.get("topic_primary"):
            set_conv_attrs(cid, {"topic": analysis["topic_primary"]})
        if analysis.get("goals"):
            set_conv_attrs(cid, {"preferences": analysis["goals"]})
        if analysis.get("preferred_times"):
            set_conv_attrs(cid, {"preferred_times": analysis["preferred_times"]})
        
        # Mark intake as completed
        set_conv_attrs(cid, {
            "intake_completed": True,
            "pending_intent": None,
            "analysis": None
        })
        
        # Show action menu
        show_prefill_action_menu(cid, contact_id, lang)
        
    elif msg_content == "correct":
        print(f"📋 User wants to correct free text analysis")
        # Start step-by-step flow to correct
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "intake_step": "for_who",
            "analysis": None
        })
        
        # Show for_who options with buttons
        for_who_options = [
            (t("intake_for_who_self", lang), "self"),
            (t("intake_for_who_child", lang), "child"),
            (t("intake_for_who_other", lang), "other")
        ]
        send_input_select_only(cid, t("intake_for_who", lang), for_who_options)
        
    elif msg_content == "handoff":
        print(f"📋 User chose handoff from free text confirmation")
        send_handoff_message(cid, t("handoff_teacher", lang))
        
    else:
        print(f"❌ Invalid free text confirmation: '{msg_content}'")
        # Show confirmation options again
        confirm_options = [
            (t("intake_free_text_confirm", lang), "confirm"),
            (t("intake_free_text_correct", lang), "correct"),
            (t("intake_free_text_handoff", lang), "handoff")
        ]
        send_input_select_only(cid, t("intake_free_text_confirm_title", lang), confirm_options)

def handle_for_who_step(cid, contact_id, msg_content, lang):
    """Handle 'for who' step - moved from main.py"""
    print(f"📋 Processing 'for_who' step: '{msg_content}'")
    
    # Map the response to for_who
    for_who = None
    if msg_content.lower() in ["mezelf", "mij", "ik", "zelf", "me", "myself"]:
        for_who = "self"
    elif msg_content.lower() in ["mijn kind", "mijn dochter", "mijn zoon", "kind", "dochter", "zoon", "my child", "my daughter", "my son"]:
        for_who = "child"
    elif msg_content.lower() in ["iemand anders", "ander", "other", "someone else"]:
        for_who = "other"
    
    if for_who:
        # Store the for_who value
        set_conv_attrs(cid, {"for_who": for_who, "intake_step": "name"})
        
        # Ask for name with personalized message
        if for_who == "self":
            name_question = t("intake_name_self", lang)
        else:
            name_question = t("intake_name_student", lang)
        
        send_text_with_duplicate_check(cid, name_question)
        print(f"📋 Intake step: name (for_who: {for_who})")
    else:
        # Invalid response, ask again
        send_text_with_duplicate_check(cid, t("intake_for_who_invalid", lang))
        print(f"❌ Invalid for_who response: '{msg_content}'")

def handle_name_step(cid, contact_id, msg_content, lang):
    """Handle name step - moved from main.py"""
    print(f"📋 Processing 'name' step: '{msg_content}'")
    
    # Store the name
    set_conv_attrs(cid, {"student_name": msg_content, "intake_step": "school_level"})
    
    # Ask for school level
    send_text_with_duplicate_check(cid, t("intake_school_level", lang))
    print(f"📋 Intake step: school_level")

def handle_school_level_step(cid, contact_id, msg_content, lang):
    """Handle school level step - moved from main.py"""
    print(f"📋 Processing 'school_level' step: '{msg_content}'")
    
    # Map school level
    school_level = map_school_level(msg_content)
    
    if school_level:
        # Store the school level
        set_conv_attrs(cid, {"school_level": school_level, "intake_step": "topic"})
        
        # Ask for topic with buttons
        topic_options = [
            (t("topic_math", lang), "math"),
            (t("topic_stats", lang), "stats"),
            (t("topic_english", lang), "english"),
            (t("topic_programming", lang), "programming"),
            (t("topic_science", lang), "science"),
            (t("topic_chemistry", lang), "chemistry"),
            (t("topic_other", lang), "other")
        ]
        send_input_select_only(cid, t("intake_topic", lang), topic_options)
        print(f"📋 Intake step: topic (school_level: {school_level})")
    else:
        # Invalid response, ask again with buttons
        school_level_options = [
            (t("level_po", lang), "po"),
            ("VMBO", "vmbo"),
            ("HAVO", "havo"),
            ("VWO", "vwo"),
            ("MBO", "mbo"),
            (t("level_university_wo", lang), "university_wo"),
            (t("level_university_hbo", lang), "university_hbo"),
            (t("level_adult", lang), "adult")
        ]
        send_input_select_only(cid, t("intake_school_level_invalid", lang), school_level_options)
        print(f"❌ Invalid school_level response: '{msg_content}' - showing buttons")

def handle_topic_step(cid, contact_id, msg_content, lang):
    """Handle topic step - moved from main.py"""
    print(f"📋 Processing 'topic' step: '{msg_content}'")
    
    # Map topic
    topic = map_topic(msg_content)
    
    if topic:
        # Store the topic
        set_conv_attrs(cid, {"topic": topic, "intake_step": "preferences"})
        
        # Ask for preferences with focus on key points
        preferences_text = t("intake_preferences", lang)
        send_text_with_duplicate_check(cid, preferences_text)
        print(f"📋 Intake step: preferences (topic: {topic})")
    else:
        # Invalid response, ask again with buttons
        topic_options = [
            (t("topic_math", lang), "math"),
            (t("topic_stats", lang), "stats"),
            (t("topic_english", lang), "english"),
            (t("topic_programming", lang), "programming"),
            (t("topic_science", lang), "science"),
            (t("topic_chemistry", lang), "chemistry"),
            (t("topic_other", lang), "other")
        ]
        send_input_select_only(cid, t("intake_topic_invalid", lang), topic_options)
        print(f"❌ Invalid topic response: '{msg_content}' - showing buttons")

def handle_preferences_step(cid, contact_id, msg_content, lang):
    """Handle preferences step - moved from main.py"""
    print(f"📋 Processing 'preferences' step: '{msg_content}'")
    
    try:
        # Analyze preferences with OpenAI
        analysis = analyze_preferences_with_openai(msg_content)
        
        # Store preferences and analysis
        set_conv_attrs(cid, {
            "preferences": msg_content,
            "preferences_analysis": analysis,
            "intake_completed": True,
            "pending_intent": None
        })
        
        # Mark contact as having completed intake
        set_contact_attrs(contact_id, {"has_completed_intake": True})
        
        print(f"✅ Intake completed successfully")
        
        # Show completion message and next steps
        send_text_with_duplicate_check(cid, t("intake_completed", lang))
        
        # Show planning options
        start_planning_flow(cid, contact_id, lang)
        
    except Exception as e:
        print(f"❌ Error analyzing preferences: {e}")
        send_admin_warning(f"Error analyzing preferences: {e}")
        
        # Fallback - store preferences without analysis
        set_conv_attrs(cid, {
            "preferences": msg_content,
            "intake_completed": True,
            "pending_intent": None
        })
        
        send_text_with_duplicate_check(cid, t("intake_completed_fallback", lang))
        
        # Show planning options
        start_planning_flow(cid, contact_id, lang)

# NOTE: Confirmation entrypoint is handled via show_prefill_confirmation_menu();
# this module exposes show_prefill_action_menu (defined earlier) strictly for
# the post-confirmation action choices.

def show_prefill_confirmation_menu(cid, contact_id, lang, prefill_info):
    """Show prefill confirmation menu - moved from main.py"""
    print(f"📋 Showing prefill confirmation menu")
    
    # Format the extracted information
    info_summary = format_prefill_info_summary(prefill_info, lang)
    
    # Send confirmation message
    confirmation_msg = t("prefill_confirmation", lang).format(
        info_summary=info_summary
    )
    
    send_text_with_duplicate_check(cid, confirmation_msg)
    
    # Set pending intent for confirmation
    set_conv_attrs(cid, {"pending_intent": "prefill_confirmation"})

def show_insufficient_prefill_message(cid, contact_id, lang, prefill_info):
    """Show insufficient prefill message - moved from main.py"""
    print(f"📋 Showing insufficient prefill message")
    
    # Get insufficient prefill message
    from helpers import get_insufficient_prefill_message
    message = get_insufficient_prefill_message(prefill_info, lang)
    
    send_text_with_duplicate_check(cid, message)
    
    # Start normal intake flow
    start_intake_flow(cid, contact_id, lang)

def format_prefill_info_summary(prefill_info, lang):
    """Format prefill info summary - moved from main.py"""
    from helpers import format_detected_info_summary
    return format_detected_info_summary(prefill_info, lang)

def handle_prefill_confirmation(cid, contact_id, msg_content, lang):
    """Handle prefill confirmation - moved from main.py"""
    print(f"✅ Processing prefill confirmation: '{msg_content}'")
    
    # Check for confirm_all (from menu button) and various confirmation words
    confirm_words = ["ja", "klopt", "correct", "yes", "✅", "ja dat klopt", "dat klopt", "klopt helemaal", "ja helemaal", "correct", "juist", "precies", "inderdaad"]
    deny_words = ["nee", "niet", "fout", "no", "❌", "nee dat klopt niet", "dat klopt niet", "niet correct", "fout", "verkeerd", "deels", "sommige", "partially", "🤔", "deels correct", "sommige kloppen", "niet alles"]
    
    msg_lower = msg_content.lower().strip()
    
    if msg_content == "confirm_all" or any(word in msg_lower for word in confirm_words):
        handle_prefill_confirmation_yes(cid, contact_id, lang)
    elif msg_content == "correct_all" or any(word in msg_lower for word in deny_words):
        handle_prefill_confirmation_no(cid, contact_id, lang)
    else:
        # Invalid response, ask again
        send_text_with_duplicate_check(cid, t("prefill_confirmation_invalid", lang))
        print(f"❌ Invalid prefill confirmation response: '{msg_content}'")

def handle_prefill_confirmation_yes(cid, contact_id, lang):
    """Handle prefill confirmation yes - moved from main.py"""
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
        current_contact_attrs["customer_since"] = datetime.now().isoformat()
        
        # Save updated contact attributes
        update_contact_attrs(contact_id, current_contact_attrs, cid,
                             note="✅ Prefill bevestigd – contactattributen bijgewerkt")
        print(f"✅ Applied prefilled info to contact: {list(prefilled_info.keys())}")
    
    # Clear pending intent
    set_conv_attrs(cid, {"pending_intent": None})
    
    print(f"✅ Prefill confirmed - intake completed")
    
    # Show completion message
    send_text_with_duplicate_check(cid, t("prefill_confirmed_message", lang))

    # Labels based on level/topic
    labels = []
    level = prefilled_info.get("school_level")
    if level:
        mapping = {
            "po": "audience:po",
            "vmbo": "audience:vmbo",
            "havo": "audience:havo",
            "vwo": "audience:vwo",
            "mbo": "audience:mbo",
            "university_wo": "audience:university:wo",
            "university_hbo": "audience:university:hbo",
            "adult": "audience:adult",
        }
        labels.append(mapping.get(level, "audience:adult"))
    topic = prefilled_info.get("topic_primary")
    if topic:
        topic_map = {
            "math": "subject:math",
            "stats": "subject:stats",
            "english": "subject:english",
            "programming": "subject:programming",
            "science": "subject:science",
            "chemistry": "subject:chemistry",
        }
        if topic_map.get(topic):
            labels.append(topic_map[topic])
    labels.append("source_whatsapp")
    labels.append("service_trial")
    add_labels_safe(cid, labels)
    
    # Show action menu (trial, urgent session, info, handoff)
    show_prefill_action_menu(cid, contact_id, lang)

def handle_prefill_action_selection(cid, contact_id, msg_content, lang):
    """Handle selection from the prefill action menu."""
    raw = (msg_content or "").strip().lower()
    # Map to canonical values using guard (handles numbers, emojis, spacing)
    chosen = match_menu_selection(raw, [
        "plan_trial_lesson",
        "urgent_session",
        "go_to_main_menu",
        "handoff",
    ])
    selection = chosen or raw

    if selection in ("plan_trial_lesson", t("prefill_action_trial_first", lang).lower()):
        set_conv_attrs(cid, {"pending_intent": ""})
        start_planning_flow(cid, contact_id, lang)
        return

    if selection in ("urgent_session", t("prefill_action_urgent_session", lang).lower()):
        set_conv_attrs(cid, {"urgent_session": True, "session_duration": 120, "pending_intent": ""})
        start_planning_flow(cid, contact_id, lang)
        return

    if selection in ("go_to_main_menu", t("prefill_action_main_menu", lang).lower()):
        set_conv_attrs(cid, {"pending_intent": ""})
        show_info_menu(cid, lang)
        return

    if selection in ("handoff", t("prefill_action_handoff", lang).lower()):
        set_conv_attrs(cid, {"pending_intent": ""})
        send_handoff_message(cid, t("handoff_teacher", lang))
        return

    # Fallback: keyword routing if platform sends label text instead of payload
    if "proefles" in raw or "trial" in raw:
        set_conv_attrs(cid, {"pending_intent": ""})
        start_planning_flow(cid, contact_id, lang)
        return
    if "urgent" in raw or "spoed" in raw:
        set_conv_attrs(cid, {"urgent_session": True, "session_duration": 120, "pending_intent": ""})
        start_planning_flow(cid, contact_id, lang)
        return

def handle_prefill_confirmation_no(cid, contact_id, lang):
    """Handle prefill confirmation no - moved from main.py"""
    print(f"❌ User rejected prefill")
    
    # Clear prefill info and start normal intake
    set_conv_attrs(cid, {
        "pending_intent": None
    })
    
    send_text_with_duplicate_check(cid, t("prefill_rejected", lang))
    
    # Start normal intake flow
    start_intake_flow(cid, contact_id, lang)

def handle_corrected_prefill_confirmation(cid, contact_id, msg_content, lang):
    """Handle corrected prefill confirmation - moved from main.py"""
    print(f"✅ Processing corrected prefill confirmation: '{msg_content}'")
    
    if msg_content.upper() in ["JA", "YES", "CONFIRM", "BEVESTIG"]:
        handle_corrected_prefill_confirmation_yes(cid, contact_id, lang)
    elif msg_content.upper() in ["NEE", "NO", "CANCEL", "ANNULEREN"]:
        handle_corrected_prefill_confirmation_no(cid, contact_id, lang)
    else:
        # Invalid response, ask again
        send_text_with_duplicate_check(cid, t("prefill_confirmation_invalid", lang))
        print(f"❌ Invalid corrected prefill confirmation response: '{msg_content}'")

def handle_corrected_prefill_confirmation_yes(cid, contact_id, lang):
    """Handle corrected prefill confirmation yes - moved from main.py"""
    print(f"✅ User confirmed corrected prefill")
    
    conv_attrs = get_conv_attrs(cid)
    corrected_info = conv_attrs.get("corrected_prefill_info", {})
    
    # Store the corrected info as intake data
    set_conv_attrs(cid, {
        "intake_completed": True,
        "pending_intent": None,
        "for_who": corrected_info.get("for_who"),
        "student_name": corrected_info.get("student_name"),
        "school_level": corrected_info.get("school_level"),
        "topic": corrected_info.get("topic"),
        "preferences": corrected_info.get("preferences", "")
    })
    
    # Mark contact as having completed intake
    set_contact_attrs(contact_id, {"has_completed_intake": True})
    
    print(f"✅ Corrected prefill confirmed - intake completed")
    
    # Show completion message
    send_text_with_duplicate_check(cid, t("prefill_corrected_confirmed", lang))
    
    # Show planning options
    start_planning_flow(cid, contact_id, lang)

def handle_corrected_prefill_confirmation_no(cid, contact_id, lang):
    """Handle corrected prefill confirmation no - moved from main.py"""
    print(f"❌ User rejected corrected prefill")
    
    # Clear corrected prefill info and start normal intake
    set_conv_attrs(cid, {
        "corrected_prefill_info": None,
        "pending_intent": None
    })
    
    send_text_with_duplicate_check(cid, t("prefill_corrected_rejected", lang))
    
    # Start normal intake flow
    start_intake_flow(cid, contact_id, lang)
