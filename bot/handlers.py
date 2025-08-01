# Main handler functions for the TutorBot

from tutorbot.bot.api import send_text, send_select, set_contact_attrs, set_conv_attrs, add_conv_labels
from tutorbot.bot.helpers import now_ams, parse_dt, is_contact_age_valid, is_weekend_now
from tutorbot.bot.translations import t
from tutorbot.config import TZ, AGE_TTL_DAYS

def setup_chatwoot_attributes():
    """Setup Chatwoot custom attributes if not already done"""
    global setup_completed
    if setup_completed:
        return
    
    print("🔧 Setting up Chatwoot custom attributes...")
    
    # Contact attributes
    contact_attrs = {
        "language": "",
        "school_level": "",
        "segment": "",
        "first_name": "",
        "is_adult": None,
        "guardian_consent": False,
        "guardian_name": "",
        "guardian_phone": "",
        "guardian_verified_at": "",
        "is_student": False,
        "is_parent": False,
        "student_since": "",
        "parent_since": "",
        "education_level": "",
        "subject": "",
        "year": "",
        "format_preference": "",
        "welcome_done": False,
        "first_contact_at": "",
        "name_asked_at": "",
        "age_verified_at": "",
        "wknd_eligible": False
    }
    
    # Conversation attributes
    conversation_attrs = {
        "program": "none",
        "topic_primary": "",
        "topic_secondary": "",
        "toolset": "",
        "lesson_mode": "",
        "is_adult": None,
        "language_prompted": False,
        "intake_completed": False,
        "age_verified": False,
        "pending_intent": None
    }
    
    print("✅ Chatwoot attributes configured")
    setup_completed = True

def ensure_contact_attributes(contact_id, attrs):
    """Ensure all required contact attributes exist"""
    if not contact_id:
        return attrs
    
    # Default attributes
    default_attrs = {
        "language": "",
        "school_level": "",
        "segment": "",
        "first_name": "",
        "is_adult": None,
        "guardian_consent": False,
        "guardian_name": "",
        "guardian_phone": "",
        "guardian_verified_at": "",
        "is_student": False,
        "is_parent": False,
        "student_since": "",
        "parent_since": "",
        "education_level": "",
        "subject": "",
        "year": "",
        "format_preference": "",
        "welcome_done": False,
        "first_contact_at": "",
        "name_asked_at": "",
        "age_verified_at": "",
        "wknd_eligible": False
    }
    
    # Merge with existing attributes
    if attrs:
        default_attrs.update(attrs)
    
    return default_attrs

def mark_age_verified(adult: bool, contact_id: int, cid: int):
    """Mark age verification for both contact and conversation"""
    set_contact_attrs(contact_id, {
        "is_adult": adult,
        "age_verified_at": now_ams().isoformat()
    })
    set_conv_attrs(cid, {"age_verified": True, "pending_intent": None})
    add_conv_labels(cid, ["age_verified"] if adult else ["minor"])

def ensure_age_for_planning(contact_attrs, convo_attrs, contact_id, cid, lang="nl") -> bool:
    """Return True als plannen mag; False als we eerst iets moeten uitvragen."""
    # 0) Reeds voor dit gesprek geverifieerd?
    if convo_attrs.get("age_verified") is True:
        return True
    
    # 1) Contact heeft geldige leeftijd?
    if is_contact_age_valid(contact_attrs):
        # Mark as verified for this conversation
        set_conv_attrs(cid, {"age_verified": True})
        return True
    
    # 2) Moeten leeftijd uitvragen
    send_text(cid, t("age_question", lang))
    send_select(cid, "", [
        (t("age_yes", lang), "age_yes"),
        (t("age_no", lang), "age_no")
    ])
    set_conv_attrs(cid, {"pending_intent": "age_verification"})
    return False

def proceed_planning(cid, attrs=None, lang="nl"):
    """Proceed with lesson planning"""
    send_text(cid, t("planning_intro", lang))
    # Add planning logic here

def ensure_first_seen(contact_id, attrs):
    """Ensure first_contact_at is set"""
    if not attrs.get("first_contact_at"):
        attrs["first_contact_at"] = now_ams().isoformat()
        set_contact_attrs(contact_id, {"first_contact_at": attrs["first_contact_at"]})

def label_new_or_returning(cid, attrs):
    """Add new/returning labels based on first_contact_at"""
    if attrs.get("first_contact_at"):
        first_contact = parse_dt(attrs["first_contact_at"])
        if first_contact and (now_ams() - first_contact).days < 7:
            add_conv_labels(cid, ["new_contact"])
        else:
            add_conv_labels(cid, ["returning_contact"])

def maybe_label_needs_guardian(cid, attrs):
    """Add guardian label if needed"""
    if attrs.get("is_adult") is False:
        add_conv_labels(cid, ["needs_guardian"])

def maybe_label_weekend_discount(cid, attrs):
    """Add weekend discount label if applicable"""
    if is_weekend_now() and attrs.get("wknd_eligible", False):
        add_conv_labels(cid, ["weekend_discount"])

def handle_pay_intent(cid, lang="nl"):
    """Handle payment intent"""
    send_text(cid, t("payment_restriction", lang))

def handle_trial_intent(cid, lang="nl"):
    """Handle trial lesson intent"""
    send_text(cid, t("trial_info", lang))

def mark_as_student(contact_id, cid, lang="nl"):
    """Mark contact as student"""
    set_contact_attrs(contact_id, {
        "is_student": True,
        "student_since": now_ams().isoformat()
    })
    add_conv_labels(cid, ["student"])

def mark_as_parent(contact_id, cid, lang="nl"):
    """Mark contact as parent"""
    set_contact_attrs(contact_id, {
        "is_parent": True,
        "parent_since": now_ams().isoformat()
    })
    add_conv_labels(cid, ["parent"])

def start_education_info_collection(cid, contact_id, cattrs, lang="nl"):
    """Start collecting education information"""
    send_text(cid, t("education_info_start", lang))
    send_text(cid, t("education_level_question", lang))
    send_select(cid, "", [
        (t("education_po", lang), "po"),
        (t("education_vmbo", lang), "vmbo"),
        (t("education_havo", lang), "havo"),
        (t("education_vwo", lang), "vwo"),
        (t("education_mbo", lang), "mbo"),
        (t("education_hbo", lang), "hbo"),
        (t("education_wo", lang), "wo"),
        (t("education_adult", lang), "adult")
    ])
    set_conv_attrs(cid, {"pending_intent": "education_info"})

def handle_education_info(cid, msg, contact_id, cattrs, lang="nl"):
    """Handle education level response"""
    education_map = {
        "po": "po", "vmbo": "vmbo", "havo": "havo", "vwo": "vwo",
        "mbo": "mbo", "hbo": "hbo", "wo": "wo", "adult": "adult"
    }
    
    if msg in education_map:
        set_contact_attrs(contact_id, {"school_level": education_map[msg]})
        send_text(cid, t("subject_question", lang))
        send_select(cid, "", [
            (t("subject_math", lang), "math"),
            (t("subject_english", lang), "english"),
            (t("subject_science", lang), "science"),
            (t("subject_programming", lang), "programming"),
            (t("subject_other", lang), "other")
        ])
        set_conv_attrs(cid, {"pending_intent": "subject_info"})
    else:
        send_text(cid, t("education_level_question", lang))

def handle_subject_info(cid, msg, contact_id, cattrs, lang="nl"):
    """Handle subject response"""
    subject_map = {
        "math": "math", "english": "english", "science": "science",
        "programming": "programming", "other": "other"
    }
    
    if msg in subject_map:
        set_contact_attrs(contact_id, {"subject": subject_map[msg]})
        send_text(cid, t("year_question", lang))
        send_select(cid, "", [
            (t("year_1", lang), "1"),
            (t("year_2", lang), "2"),
            (t("year_3", lang), "3"),
            (t("year_4", lang), "4"),
            (t("year_5", lang), "5"),
            (t("year_6", lang), "6"),
            (t("year_other", lang), "other")
        ])
        set_conv_attrs(cid, {"pending_intent": "year_info"})
    else:
        send_text(cid, t("subject_question", lang))

def handle_year_info(cid, msg, contact_id, cattrs, lang="nl"):
    """Handle year response"""
    if msg in ["1", "2", "3", "4", "5", "6", "other"]:
        set_contact_attrs(contact_id, {"year": msg})
        send_text(cid, t("format_question", lang))
        send_select(cid, "", [
            (t("format_online", lang), "online"),
            (t("format_in_person", lang), "in_person"),
            (t("format_hybrid", lang), "hybrid")
        ])
        set_conv_attrs(cid, {"pending_intent": "format_info"})
    else:
        send_text(cid, t("year_question", lang))

def handle_format_info(cid, msg, contact_id, cattrs, lang="nl"):
    """Handle format response"""
    format_map = {"online": "online", "in_person": "in_person", "hybrid": "hybrid"}
    
    if msg in format_map:
        set_contact_attrs(contact_id, {"format_preference": format_map[msg]})
        set_conv_attrs(cid, {"intake_completed": True, "pending_intent": None})
        
        if cattrs.get("is_adult"):
            send_text(cid, t("adult_proceed", lang))
        else:
            send_text(cid, t("minor_parent_contact", lang))
    else:
        send_text(cid, t("format_question", lang))

def start_parent_child_info_collection(cid, contact_id, cattrs, lang="nl"):
    """Start collecting parent/child information"""
    send_text(cid, t("parent_detected", lang))
    set_conv_attrs(cid, {"pending_intent": "child_name"})

def handle_info_intent(cid, lang="nl"):
    """Handle information request"""
    send_text(cid, t("info_menu_question", lang))
    send_select(cid, "", [
        (t("info_prices", lang), "prices"),
        (t("info_schedule", lang), "schedule"),
        (t("info_subjects", lang), "subjects"),
        (t("info_location", lang), "location"),
        (t("info_contact", lang), "contact"),
        (t("info_back", lang), "back_to_menu")
    ])

def handle_human_intent(cid, lang="nl"):
    """Handle human contact request"""
    # First, try to assign conversation to Stephen (agent ID 2)
    try:
        api(f"/api/v1/accounts/{ACC}/conversations/{cid}/assignments",
            assignee_id=2)
        send_text(cid, t("human_contacting", lang))
    except:
        send_text(cid, t("human_contacted", lang))

def handle_faq_response(cid, msg, lang="nl"):
    """Handle FAQ response"""
    faq_responses = {
        "what_is": t("faq_what_is_answer", lang),
        "how_much": t("faq_how_much_answer", lang),
        "how_long": t("faq_how_long_answer", lang),
        "where": t("faq_where_answer", lang),
        "when": t("faq_when_answer", lang)
    }
    
    if msg in faq_responses:
        send_text(cid, faq_responses[msg])
        send_select(cid, "", [(t("back_to_menu", lang), "back_to_menu")])
    else:
        send_text(cid, t("faq_menu", lang))

def main_menu(cid, attrs=None, is_new_contact=False, lang="nl"):
    """Show main menu"""
    if is_new_contact:
        send_text(cid, t("welcome_new", lang))
    else:
        name = attrs.get("first_name", "") if attrs else ""
        if name:
            send_text(cid, t("welcome_return", lang, name=name))
        else:
            send_text(cid, t("greeting_no_name", lang))
    
    send_text(cid, t("main_menu", lang))
    send_select(cid, "", [
        (t("menu_plan", lang), "plan"),
        (t("menu_info", lang), "info"),
        (t("menu_human", lang), "human"),
        (t("menu_faq", lang), "faq")
    ])

def handle_name_input(cid, msg, contact_id, attrs, lang="nl"):
    """Handle name input"""
    if is_valid_name(msg):
        set_contact_attrs(contact_id, {"first_name": msg})
        send_text(cid, t("name_confirmed", lang, name=msg))
        main_menu(cid, attrs, lang=lang)
    else:
        send_text(cid, t("ask_name_again", lang))

def handle_guardian_consent(cid, msg, contact_id, attrs, lang="nl"):
    """Handle guardian consent"""
    if msg == "age_yes":
        mark_age_verified(True, contact_id, cid)
        main_menu(cid, attrs, lang=lang)
    elif msg == "age_no":
        mark_age_verified(False, contact_id, cid)
        send_text(cid, t("guardian_consent_needed_named", lang, name=attrs.get("first_name", "")))
        set_conv_attrs(cid, {"pending_intent": "guardian_info"})
    else:
        send_text(cid, t("age_question", lang)) 