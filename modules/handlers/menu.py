#!/usr/bin/env python3
"""
Menu Handlers for TutorBot

This module contains menu selection handlers and utilities.
"""

from typing import Dict, Any

# Import dependencies
from modules.utils.cw_api import (
    get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs,
    remove_conv_labels
)
from modules.utils.text_helpers import (
    send_text_with_duplicate_check, t, send_admin_warning, send_input_select_only,
    get_contact_id_from_conversation, send_handoff_menu, assign_conversation, send_handoff_message
)
from modules.utils.menu_guard import match_menu_selection
from modules.utils.mapping import detect_segment
from modules.core.config import HANDOFF_AGENT_ID

# Optional import for detailed info menu (defined in main.py in current architecture)
try:
    from main import show_detailed_info_menu as _show_detailed_info_menu
    show_detailed_info_menu = _show_detailed_info_menu  # re-export locally
except Exception:
    # During certain test runs, main may not be importable; handlers still lint
    def show_detailed_info_menu(*args, **kwargs):  # type: ignore
        raise NameError("show_detailed_info_menu is not available in this context")


def _show_detailed_info_menu_safe(cid, lang):
    """Safely show the detailed info menu, with runtime import and fallback."""
    try:
        # Lazy import to avoid circular import during module load
        from main import show_detailed_info_menu as _shim
        return _shim(cid, lang)
    except Exception:
        # Minimal fallback using local translations to avoid breaking the flow
        send_input_select_only(cid, t("detailed_info_menu_text", lang), [
            (t("menu_personal_background", lang), "personal_background"),
            (t("menu_didactic_methods", lang), "didactic_methods"),
            (t("menu_technology_tools", lang), "technology_tools"),
            (t("menu_results_success", lang), "results_success"),
            (t("menu_workshops_creative", lang), "workshops_creative"),
            (t("menu_workshops_academic", lang), "workshops_academic"),
            (t("menu_consultancy", lang), "consultancy"),
            (t("menu_back_to_main", lang), "back_to_main_info"),
        ])
        return None

def show_main_menu(cid, contact_id, lang):
    """Show main menu - moved from main.py"""
    print(f"📋 Showing main menu for conversation {cid}")
    
    # Get segment
    segment = detect_segment(contact_id)
    
    # Show segment-specific menu
    show_segment_menu(cid, contact_id, segment, lang)

def show_segment_menu(cid, contact_id, segment, lang):
    """Show segment-specific menu - moved from main.py"""
    print(f"📋 Showing segment menu: {segment}")
    
    # Set pending intent for menu selection
    set_conv_attrs(cid, {"pending_intent": "menu_selection"})
    
    # Send segment-specific interactive menu (match refactor)
    try:
        if segment == "new":
            send_input_select_only(cid, t("menu_new", lang), [
                (t("menu_option_trial_lesson", lang), "plan_lesson"),
                (t("menu_option_info", lang), "info"),
                (t("menu_option_handoff", lang), "contact")
            ])
        elif segment == "existing":
            send_input_select_only(cid, t("menu_existing", lang), [
                (t("menu_option_plan_lesson", lang), "plan_lesson"),
                (t("menu_option_same_preferences", lang), "same_preferences"),
                (t("menu_option_info", lang), "info")
            ])
        elif segment == "returning_broadcast":
            send_input_select_only(cid, t("menu_returning_broadcast", lang), [
                (t("menu_option_plan_lesson", lang), "plan_lesson"),
                (t("menu_option_old_preferences", lang), "old_preferences"),
                (t("menu_option_info", lang), "info")
            ])
        elif segment == "weekend":
            send_input_select_only(cid, t("menu_weekend", lang), [
                (t("menu_option_plan_lesson", lang), "plan_lesson"),
                (t("menu_option_info", lang), "info")
            ])
        else:
            send_input_select_only(cid, t("menu_new", lang), [
                (t("menu_option_trial_lesson", lang), "plan_lesson"),
                (t("menu_option_info", lang), "info"),
                (t("menu_option_handoff", lang), "contact")
            ])
    except Exception as e:
        print(f"❌ Failed to send main menu input_select: {e}")


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


def show_info_follow_up_menu(cid, contact_id, lang, just_showed=None):
    """Show follow-up menu after displaying information"""
    print(f"📄 Showing info follow-up menu in {lang}")
    set_conv_attrs(cid, {"pending_intent": "info_follow_up"})
    
    # Get contact attributes to check if they have completed a trial lesson
    contact_attrs = get_contact_attrs(contact_id)
    has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
    
    # Show follow-up menu with options based on what was just shown
    # Don't show the same option again if user just saw it
    follow_up_options = []
    
    # Show tariffs option based on what was just shown
    if just_showed == "vmbo_tariffs":
        # If VMBO specific tariffs were shown, offer to see all tariffs
        follow_up_options.append((t("menu_all_tariffs", lang), "show_all_tariffs"))
    elif just_showed != "tariffs":
        # If no tariffs or other tariffs were shown, offer basic tariffs
        follow_up_options.append((t("menu_tariffs", lang), "show_all_tariffs"))
    
    # Always show these options
    follow_up_options.extend([
        (t("menu_more_info", lang), "back_to_info"),
        (t("menu_option_handoff", lang), "handoff")
    ])
    
    # Add planning option if they have completed a trial lesson
    if has_completed_trial:
        follow_up_options.insert(1, (t("menu_option_plan_lesson", lang), "plan_lesson"))
        print(f"✅ Adding 'Les inplannen' option - trial completed")
    else:
        print(f"❌ Not showing 'Les inplannen' option - no trial completed")
    
    send_input_select_only(cid, t("info_follow_up_new", lang), follow_up_options)


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
        assign_conversation(cid, HANDOFF_AGENT_ID)  # Use configurable agent ID
        
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

def handle_menu_selection(cid, contact_id, msg_content, lang):
    """Handle menu selection - moved from main.py"""
    print(f"📋 Processing menu selection: '{msg_content}'")
    
    # Check if we're in intake choice flow - if so, handle it directly
    conv_attrs = get_conv_attrs(cid)
    if conv_attrs.get("pending_intent") == "intake_choice":
        print(f"📋 In intake choice flow - delegating to intake handler")
        from modules.handlers.intake import handle_intake_step
        handle_intake_step(cid, contact_id, msg_content, lang)
        return
    
    # Map menu selection to action
    selection = (msg_content or "").lower().strip()

    # First try strict matching against known option values (works for clickable menus and numbers)
    chosen = match_menu_selection(selection, [
        "plan_lesson",
        "trial_lesson",
        "info",
        "contact",
        "handoff",
        "same_preferences",
        "old_preferences"
    ])
    if chosen:
        if chosen in ("plan_lesson", "same_preferences", "old_preferences"):
            print(f"📋 Matched via guard: {chosen} -> start_planning_flow")
            from modules.handlers.planning import start_planning_flow
            start_planning_flow(cid, contact_id, lang)
            return
        if chosen in ("trial_lesson",):
            print(f"📋 Matched via guard: {chosen} -> start_intake_flow")
            from modules.handlers.intake import start_intake_flow
            start_intake_flow(cid, contact_id, lang)
            return
        if chosen in ("info",):
            print(f"📋 Matched via guard: info -> show_info_menu")
            show_info_menu(cid, lang)
            return
        if chosen in ("contact", "handoff"):
            print(f"📋 Matched via guard: handoff -> show_handoff_menu")
            show_handoff_menu(cid, contact_id, lang)
            return
    
    if selection in ["1", "proefles", "trial", "trial lesson"]:
        print(f"📋 User selected: Trial lesson")
        from modules.handlers.intake import start_intake_flow
        start_intake_flow(cid, contact_id, lang)
    elif selection in ["2", "info", "information", "meer info"]:
        print(f"📋 User selected: Information")
        show_info_menu(cid, lang)
    elif selection in ["3", "contact", "handoff", "mensen"]:
        print(f"📋 User selected: Contact human")
        show_handoff_menu(cid, contact_id, lang)
    elif selection in ["4", "faq", "veelgestelde vragen"]:
        print(f"📋 User selected: FAQ")
        show_faq_menu(cid, contact_id, lang)
    elif selection in ["back", "menu", "terug", "back_to_main"]:
        print(f"📋 User selected: Back to main menu")
        show_main_menu(cid, contact_id, lang)
    else:
        # Invalid selection -> show friendly fallback with two options
        title = (
            "❓ Sorry, ik begrijp je niet helemaal. Kies alsjeblieft:" if (lang == "nl")
            else "❓ Sorry, I didn't quite get that. Please choose:"
        )
        try:
            send_input_select_only(cid, title, [
                (t("menu_option_handoff", lang), "handoff"),
                (t("menu_back_to_main", lang), "back_to_main"),
            ])
        except Exception:
            # Fallback to plain text if input_select fails
            send_text_with_duplicate_check(cid, title + ("\n- Stephen spreken\n- Terug naar het hoofdmenu" if lang == "nl" else "\n- Talk to Stephen\n- Back to main menu"))
        print(f"❌ Invalid menu selection: '{msg_content}'")

def show_info_menu(cid, lang):
    """Show info menu - moved from main.py"""
    print(f"ℹ️ Showing info menu")
    
    # Set pending intent for info menu selection
    set_conv_attrs(cid, {"pending_intent": "info_menu_selection"})
    
    # Present a compact interactive menu for information
    try:
        send_input_select_only(cid, t("info_menu_question", lang), [
            (t("menu_tariffs", lang), "tariffs"),
            (t("menu_work_method", lang), "work_method"),
            (t("menu_services", lang), "services"),
            (t("menu_more_info", lang), "more_info"),
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_handoff", lang), "handoff"),
            (t("menu_back_to_main", lang), "back_to_main"),
        ])
    except Exception as e:
        print(f"❌ Failed to send info menu input_select: {e}")
        # Fallback to plain text if input_select fails
        send_text_with_duplicate_check(cid, t("info_menu", lang))

def handle_info_menu_selection(cid, contact_id, msg_content, lang):
    """Handle info menu selection - moved from main.py"""
    print(f"ℹ️ Processing info menu selection: '{msg_content}'")
    
    # Map info menu selection to action
    selection = (msg_content or "").lower().strip()

    # Guard-based matching on known option values from the interactive menu
    chosen = match_menu_selection(selection, [
        "info",  # Add generic info option for synonyms
        "tariffs",
        "work_method",
        "services",
        "workshops",
        "how_lessons_work",
        "travel_costs",
        "conditions",
        "weekend_programs",
        "short_version",
        "more_info",
        "plan_lesson",
        "handoff",
        "back",
        "back_to_main"
    ])
    if chosen:
        if chosen in ("plan_lesson",):
            from modules.handlers.planning import start_planning_flow
            start_planning_flow(cid, contact_id, lang)
            return
        if chosen == "info":
            # Show the info menu again for generic info requests
            show_info_menu(cid, lang)
            return
        if chosen == "tariffs":
            show_smart_pricing_info(cid, contact_id, lang)
            return
        if chosen == "work_method":
            show_work_method_info(cid, lang)
            return
        if chosen == "services":
            show_services_info(cid, lang)
            return
        if chosen in ("workshops", "how_lessons_work"):
            if chosen == "workshops":
                show_workshops_info(cid, lang)
            else:
                send_text_with_duplicate_check(cid, t("info_how_lessons_work", lang))
                show_info_follow_up_menu(cid, contact_id, lang)
            return
        if chosen == "travel_costs":
            send_text_with_duplicate_check(cid, t("info_travel_costs", lang))
            show_info_follow_up_menu(cid, contact_id, lang)
            return
        if chosen == "conditions":
            send_text_with_duplicate_check(cid, t("info_conditions", lang))
            show_info_follow_up_menu(cid, contact_id, lang)
            return
        if chosen == "weekend_programs":
            send_text_with_duplicate_check(cid, t("info_weekend_programs", lang))
            show_info_follow_up_menu(cid, contact_id, lang)
            return
        if chosen == "short_version":
            send_text_with_duplicate_check(cid, t("info_short_version", lang))
            show_info_follow_up_menu(cid, contact_id, lang)
            return
        if chosen == "more_info":
            show_detailed_info_menu(cid, lang)
            return
        if chosen in ("back", "back_to_main"):
            show_main_menu(cid, contact_id, lang)
            return
    
    # If no exact match, try to analyze with OpenAI for free text input
    if len(msg_content.strip()) > 10:  # Only analyze substantial text
        print(f"🤖 Analyzing free text question: '{msg_content}'")
        
        try:
            # Import OpenAI analysis function
            from modules.integrations.openai_service import analyze_info_request_with_openai
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
                        show_smart_pricing_info(cid, contact_id, lang)
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
                else:
                    print(f"⚠️ Low confidence analysis ({confidence}) - falling back to menu")
        except Exception as e:
            print(f"❌ Error analyzing info request: {e}")
            # Continue to fallback below
    
    # Fallback to traditional menu matching
    if selection in ["1", "tarieven", "prijzen", "pricing", "alle tarieven bekijken", "💰 alle tarieven bekijken"]:
        print(f"ℹ️ User selected: Pricing")
        show_smart_pricing_info(cid, contact_id, lang)
    elif selection in ["2", "werkwijze", "methode", "method"]:
        print(f"ℹ️ User selected: Work method")
        show_work_method_info(cid, lang)
    elif selection in ["3", "diensten", "services"]:
        print(f"ℹ️ User selected: Services")
        show_services_info(cid, lang)
    elif selection in ["4", "workshops", "cursussen"]:
        print(f"ℹ️ User selected: Workshops")
        show_workshops_info(cid, lang)
    elif selection in ["5", "terug", "back", "menu"]:
        print(f"ℹ️ User selected: Back to menu")
        show_main_menu(cid, contact_id, lang)
    else:
        # Invalid selection -> friendly fallback
        title = (
            "❓ Sorry, ik begrijp je niet helemaal. Kies alsjeblieft:" if (lang == "nl")
            else "❓ Sorry, I didn't quite get that. Please choose:"
        )
        try:
            send_input_select_only(cid, title, [
                (t("menu_option_handoff", lang), "handoff"),
                (t("menu_back_to_main", lang), "back_to_main"),
            ])
        except Exception:
            send_text_with_duplicate_check(cid, title + ("\n- Stephen spreken\n- Terug naar het hoofdmenu" if lang == "nl" else "\n- Talk to Stephen\n- Back to main menu"))
        print(f"❌ Invalid info menu selection: '{msg_content}'")

def show_pricing_info(cid, lang):
    """Show pricing information - moved from main.py"""
    print(f"💰 Showing pricing info")
    # Show complete tariffs with option to show all
    send_text_with_duplicate_check(cid, t("info_tariffs_complete", lang))
    # Show follow-up menu
    show_info_follow_up_menu(cid, None, lang, just_showed="complete_tariffs")

def show_work_method_info(cid, lang):
    """Show work method information - moved from main.py"""
    print(f"🔧 Showing work method info")
    # Use canonical translation key
    send_text_with_duplicate_check(cid, t("info_work_method", lang))
    # Show info menu again after displaying work method
    show_info_menu(cid, lang)

def show_services_info(cid, lang):
    """Show services information - moved from main.py"""
    print(f"🛠️ Showing services info")
    # Use canonical translation key
    send_text_with_duplicate_check(cid, t("info_services", lang))
    # Show info menu again after displaying services
    show_info_menu(cid, lang)

def show_workshops_info(cid, lang):
    """Show workshops information - moved from main.py"""
    print(f"🎓 Showing workshops info")
    # Default to creative workshops overview (no generic key exists)
    send_text_with_duplicate_check(cid, t("info_workshops_creative", lang))
    # Show info menu again after displaying workshops
    show_info_menu(cid, lang)

def show_handoff_menu(cid, contact_id, lang):
    """Show handoff menu - moved from main.py"""
    print(f"🤝 Showing handoff menu")
    
    # Set pending intent for handoff menu selection
    set_conv_attrs(cid, {"pending_intent": "handoff_menu_selection"})
    
    send_text_with_duplicate_check(cid, t("handoff_menu", lang))

def handle_handoff_menu_selection(cid, contact_id, msg_content, lang):
    """Handle handoff menu selection - moved from main.py"""
    print(f"🤝 Processing handoff menu selection: '{msg_content}'")
    
    # Map handoff menu selection to action
    selection = msg_content.lower().strip()
    
    if selection in ["1", "telefoon", "phone", "bellen"]:
        print(f"🤝 User selected: Phone contact")
        send_text_with_duplicate_check(cid, t("handoff_phone", lang))
        # TODO: Implement phone handoff
    elif selection in ["2", "email", "mail"]:
        print(f"🤝 User selected: Email contact")
        send_text_with_duplicate_check(cid, t("handoff_email", lang))
        # TODO: Implement email handoff
    elif selection in ["3", "terug", "back", "menu", "back_to_main"]:
        print(f"🤝 User selected: Back to menu")
        show_main_menu(cid, contact_id, lang)
    else:
        # Invalid selection -> friendly fallback
        title = (
            "❓ Sorry, ik begrijp je niet helemaal. Kies alsjeblieft:" if (lang == "nl")
            else "❓ Sorry, I didn't quite get that. Please choose:"
        )
        try:
            send_input_select_only(cid, title, [
                (t("menu_option_handoff", lang), "handoff"),
                (t("menu_back_to_main", lang), "back_to_main"),
            ])
        except Exception:
            send_text_with_duplicate_check(cid, title + ("\n- Stephen spreken\n- Terug naar het hoofdmenu" if lang == "nl" else "\n- Talk to Stephen\n- Back to main menu"))
        print(f"❌ Invalid handoff menu selection: '{msg_content}'")

def show_faq_menu(cid, contact_id, lang):
    """Show FAQ menu - moved from main.py"""
    print(f"❓ Showing FAQ menu")
    
    # Set pending intent for FAQ request
    set_conv_attrs(cid, {"pending_intent": "faq_request"})
    
    send_text_with_duplicate_check(cid, t("faq_menu", lang))

def handle_faq_request(cid, contact_id, msg_content, lang):
    """Handle FAQ request - moved from main.py"""
    print(f"❓ Processing FAQ request: '{msg_content}'")
    
    # Map FAQ request to response
    question = msg_content.lower().strip()
    
    if "prijs" in question or "kosten" in question or "tarief" in question:
        send_text_with_duplicate_check(cid, t("faq_pricing", lang))
    elif "duur" in question or "lengte" in question or "tijd" in question:
        send_text_with_duplicate_check(cid, t("faq_duration", lang))
    elif "locatie" in question or "waar" in question or "plaats" in question:
        send_text_with_duplicate_check(cid, t("faq_location", lang))
    elif "online" in question or "digitaal" in question or "zoom" in question:
        send_text_with_duplicate_check(cid, t("faq_online", lang))
    elif "materiaal" in question or "boeken" in question or "spullen" in question:
        send_text_with_duplicate_check(cid, t("faq_materials", lang))
    elif "annuleren" in question or "afzeggen" in question or "cancel" in question:
        send_text_with_duplicate_check(cid, t("faq_cancellation", lang))
    else:
        # Generic FAQ response
        send_text_with_duplicate_check(cid, t("faq_generic", lang))
    
    # Clear pending intent
    set_conv_attrs(cid, {"pending_intent": None})

def show_smart_pricing_info(cid, contact_id, lang):
    """Show pricing information based on user's level and age"""
    print(f"💰 Showing smart pricing info")
    
    # Get contact attributes to determine appropriate tariffs
    contact_attrs = get_contact_attrs(contact_id)
    school_level = contact_attrs.get("school_level", "")
    is_adult = contact_attrs.get("is_adult", False)
    
    # Determine if over 20 (adults are typically over 20)
    age_over_20 = is_adult or school_level in ["university_hbo", "university_wo"]
    
    # Get appropriate tariffs key
    from modules.utils.mapping import get_appropriate_tariffs_key
    tariffs_key = get_appropriate_tariffs_key(school_level, age_over_20)
    print(f"💰 Using tariffs key: {tariffs_key} for school_level: {school_level}, age_over_20: {age_over_20}")
    
    # Show the appropriate tariffs
    send_text_with_duplicate_check(cid, t(tariffs_key, lang))
    
    # Show follow-up menu with option to see all tariffs
    show_tariffs_follow_up_menu(cid, contact_id, lang, tariffs_key)

def show_tariffs_follow_up_menu(cid, contact_id, lang, shown_tariffs_key):
    """Show follow-up menu after showing specific tariffs"""
    print(f"💰 Showing tariffs follow-up menu")
    
    # Create menu options
    options = [
        (t("show_all_tariffs", lang), "show_all_tariffs"),
        (t("plan_lesson_button", lang), "plan_lesson"),
        (t("back_to_info", lang), "back_to_info"),
        (t("handoff_to_stephen", lang), "handoff")
    ]
    
    title = t("tariffs_follow_up_title", lang)
    
    try:
        send_input_select_only(cid, title, options)
        # Set the pending intent
        set_conv_attrs(cid, {"pending_intent": "tariffs_follow_up", "shown_tariffs": shown_tariffs_key})
    except Exception as e:
        print(f"❌ Error showing tariffs follow-up menu: {e}")
        # Fallback to text menu
        send_text_with_duplicate_check(cid, title + "\n- " + "\n- ".join([option[0] for option in options]))

def handle_tariffs_follow_up_selection(cid, contact_id, msg_content, lang):
    """Handle tariffs follow-up menu selections"""
    print(f"💰 Processing tariffs follow-up selection: '{msg_content}'")
    
    # Map tariffs follow-up menu selection to action
    selection = (msg_content or "").lower().strip()
    
    # Use menu guard for selection mapping
    from modules.utils.menu_guard import match_menu_selection
    chosen = match_menu_selection(selection, [
        "show_all_tariffs",
        "plan_lesson", 
        "back_to_info",
        "handoff"
    ])
    
    # Clear pending intent
    set_conv_attrs(cid, {"pending_intent": None})
    
    if chosen:
        if chosen == "show_all_tariffs":
            print(f"💰 User selected: Show all tariffs")
            send_text_with_duplicate_check(cid, t("info_tariffs", lang))
            show_info_follow_up_menu(cid, contact_id, lang)
            return
        elif chosen == "plan_lesson":
            print(f"📅 User selected: Plan lesson")
            from modules.handlers.planning import start_planning_flow
            start_planning_flow(cid, contact_id, lang)
            return
        elif chosen == "back_to_info":
            print(f"📖 User selected: Back to info")
            show_info_menu(cid, lang)
            return
        elif chosen == "handoff":
            print(f"👨‍🏫 User selected: Handoff")
            send_handoff_message(cid, t("handoff_teacher", lang))
            return
    
    # Fallback to traditional menu matching
    print(f"🔍 Debug: selection='{selection}', msg_content='{msg_content}'")
    if selection in ["1", "tarieven", "prijzen", "pricing", "show_all_tariffs", "alle tarieven bekijken", "alle tarieven", "💰 alle tarieven bekijken"]:
        print(f"💰 User selected: Show all tariffs")
        send_text_with_duplicate_check(cid, t("info_tariffs", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
    elif selection in ["2", "info", "information", "back_to_info", "meer informatie", "meer info", "📖 meer informatie"]:
        print(f"📖 User selected: Back to info")
        show_info_menu(cid, lang)
    elif selection in ["3", "plan", "plan_lesson", "les inplannen", "📅 les inplannen"]:
        print(f"📅 User selected: Plan lesson")
        from modules.handlers.planning import start_planning_flow
        start_planning_flow(cid, contact_id, lang)
    elif selection in ["4", "handoff", "stephen", "stephen spreken", "👨‍🏫 stephen spreken"]:
        print(f"👨‍🏫 User selected: Handoff")
        send_handoff_message(cid, t("handoff_teacher", lang))
    else:
        # Fallback - show info menu
        print(f"❌ Invalid tariffs follow-up selection: '{msg_content}'")
        show_info_menu(cid, lang)

def handle_info_follow_up_selection(cid, contact_id, msg_content, lang):
    """Handle info follow-up menu selections"""
    print(f"📄 Processing info follow-up selection: '{msg_content}'")
    
    # Map info follow-up menu selection to action
    selection = (msg_content or "").lower().strip()

    # Guard-based matching on known option values
    chosen = match_menu_selection(selection, [
        "show_all_tariffs",
        "back_to_info",
        "plan_lesson",
        "handoff"
    ])
    
    if chosen:
        if chosen == "show_all_tariffs":
            print(f"💰 User selected: Show all tariffs")
            # Show complete tariffs information
            send_text_with_duplicate_check(cid, t("info_tariffs", lang))
            show_info_follow_up_menu(cid, contact_id, lang)
            return
        if chosen == "back_to_info":
            print(f"📖 User selected: Back to info")
            show_info_menu(cid, lang)
            return
        if chosen == "plan_lesson":
            print(f"📅 User selected: Plan lesson")
            from modules.handlers.planning import start_planning_flow
            start_planning_flow(cid, contact_id, lang)
            return
        if chosen == "handoff":
            print(f"👨‍🏫 User selected: Handoff")
            send_handoff_message(cid, t("handoff_teacher", lang))
            return
    
    # Fallback to traditional menu matching
    if selection in ["1", "tarieven", "prijzen", "pricing", "show_all_tariffs"]:
        print(f"💰 User selected: Show all tariffs")
        send_text_with_duplicate_check(cid, t("info_tariffs", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
    elif selection in ["2", "info", "information", "back_to_info", "meer informatie", "meer info"]:
        print(f"📖 User selected: Back to info")
        show_info_menu(cid, lang)
    elif selection in ["3", "plan", "plan_lesson"]:
        print(f"📅 User selected: Plan lesson")
        from modules.handlers.planning import start_planning_flow
        start_planning_flow(cid, contact_id, lang)
    elif selection in ["4", "handoff", "stephen"]:
        print(f"👨‍🏫 User selected: Handoff")
        send_handoff_message(cid, t("handoff_teacher", lang))
    else:
        # Invalid selection -> friendly fallback
        title = (
            "❓ Sorry, ik begrijp je niet helemaal. Kies alsjeblieft:" if (lang == "nl")
            else "❓ Sorry, I didn't quite get that. Please choose:"
        )
        try:
            send_input_select_only(cid, title, [
                (t("menu_option_handoff", lang), "handoff"),
                (t("menu_back_to_main", lang), "back_to_main"),
            ])
        except Exception:
            send_text_with_duplicate_check(cid, title + ("\n- Stephen spreken\n- Terug naar het hoofdmenu" if lang == "nl" else "\n- Talk to Stephen\n- Back to main menu"))
        print(f"❌ Invalid info follow-up selection: '{msg_content}'")
