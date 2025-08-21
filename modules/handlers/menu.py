#!/usr/bin/env python3
"""
Menu Handlers for TutorBot

This module contains menu selection handlers and utilities.
"""

from typing import Dict, Any

# Import dependencies
from modules.utils.cw_api import (
    get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs
)
from modules.utils.text_helpers import (
    send_text_with_duplicate_check, t, send_admin_warning, send_input_select_only
)
from modules.utils.menu_guard import match_menu_selection
from modules.utils.mapping import detect_segment

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
            show_pricing_info(cid, lang)
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
                show_info_menu(cid, lang)
            return
        if chosen == "travel_costs":
            send_text_with_duplicate_check(cid, t("info_travel_costs", lang))
            show_info_menu(cid, lang)
            return
        if chosen == "conditions":
            send_text_with_duplicate_check(cid, t("info_conditions", lang))
            show_info_menu(cid, lang)
            return
        if chosen == "weekend_programs":
            send_text_with_duplicate_check(cid, t("info_weekend_programs", lang))
            show_info_menu(cid, lang)
            return
        if chosen == "short_version":
            send_text_with_duplicate_check(cid, t("info_short_version", lang))
            show_info_menu(cid, lang)
            return
        if chosen == "more_info":
            show_detailed_info_menu(cid, lang)
            return
        if chosen in ("back", "back_to_main"):
            show_main_menu(cid, contact_id, lang)
            return
    
    if selection in ["1", "tarieven", "prijzen", "pricing"]:
        print(f"ℹ️ User selected: Pricing")
        show_pricing_info(cid, lang)
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
    # Use canonical translation key
    send_text_with_duplicate_check(cid, t("info_tariffs", lang))
    # Show info menu again after displaying pricing
    show_info_menu(cid, lang)

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
