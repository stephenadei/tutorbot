#!/usr/bin/env python3
"""
Mapping and Data Processing Utilities for TutorBot

This module contains functions for mapping and processing various data types
like school levels, topics, and other educational metadata.
"""

from typing import Dict, Any

def map_school_level(level_text: str) -> str:
    """
    Map school level text to standardized values.
    
    Args:
        level_text (str): Raw school level text from user input
    
    Returns:
        str: Standardized school level code
    """
    level_mapping = {
        # Primary Education
        "basisschool": "po", "primary school": "po", "po": "po", "primary": "po",
        "speciaal onderwijs": "po", "special education": "po", "so": "po",
        
        # Secondary Education (Dutch)
        "vmbo": "vmbo", "vmbo-tl": "vmbo", "vmbo-gl": "vmbo", "vmbo-bl": "vmbo", "vmbo-kl": "vmbo",
        "havo": "havo", "vwo": "vwo", "gymnasium": "vwo", "atheneum": "vwo",
        
        # International Curricula
        "ib": "vwo", "international baccalaureate": "vwo", "ib diploma": "vwo",
        "cambridge": "vwo", "cambridge international": "vwo", "igcse": "vwo",
        "international school": "vwo", "internationale school": "vwo",
        
        # Vocational Education
        "mbo": "mbo", "mbo niveau 1": "mbo", "mbo niveau 2": "mbo", "mbo niveau 3": "mbo", "mbo niveau 4": "mbo",
        
        # Higher Education
        "hbo": "university_hbo", "wo": "university_wo", "universiteit": "university_wo",
        "universiteit hbo": "university_hbo", "universiteit wo": "university_wo",
        "hogeschool": "university_hbo", "university": "university_wo",
        "rijksuniversiteit": "university_wo", "uva": "university_wo", "vu": "university_wo", "tu": "university_wo",
        "bachelor": "university_wo", "master": "university_wo", "bsc": "university_wo", "msc": "university_wo",
        "bachelor student": "university_wo", "master student": "university_wo", "universiteitsstudent": "university_wo",
        "2e jaars": "university_wo", "3e jaars": "university_wo", "eerste jaar": "university_wo", "tweede jaar": "university_wo", "derde jaar": "university_wo",
        
        # Adult Education
        "volwassenenonderwijs": "adult", "adult": "adult", "volwassenen": "adult",
        "werkende": "adult", "professional": "adult"
    }
    return level_mapping.get(level_text.lower(), "adult")

def get_school_level_display(level_code: str, lang: str = "nl") -> str:
    """
    Convert internal school level codes to readable display text.
    
    Args:
        level_code (str): Internal school level code
        lang (str): Language for display ("nl" or "en")
    
    Returns:
        str: Human-readable school level text
    """
    display_mapping = {
        "po": {"nl": "Basisschool", "en": "Primary School"},
        "vmbo": {"nl": "VMBO", "en": "VMBO"},
        "havo": {"nl": "HAVO", "en": "HAVO"},
        "vwo": {"nl": "VWO", "en": "VWO"},
        "mbo": {"nl": "MBO", "en": "MBO"},
        "university_hbo": {"nl": "HBO", "en": "HBO"},
        "university_wo": {"nl": "Universiteit (WO)", "en": "University (WO)"},
        "adult": {"nl": "Volwassenenonderwijs", "en": "Adult Education"}
    }
    
    return display_mapping.get(level_code, {}).get(lang, level_code)

def get_appropriate_tariffs_key(school_level: str, age_over_20: bool = False) -> str:
    """
    Get the appropriate tariffs key based on school level and age.
    
    Args:
        school_level (str): School level code
        age_over_20 (bool): Whether the person is over 20
    
    Returns:
        str: Tariffs key for pricing information
    """
    # Map specific school levels to their tariff categories
    if school_level == "po":
        return "info_tariffs_po"
    elif school_level == "vmbo":
        return "info_tariffs_vmbo"
    elif school_level in ["havo", "vwo"]:
        return "info_tariffs_havo_vwo"
    elif school_level == "mbo":
        return "info_tariffs_mbo"
    elif school_level in ["university_hbo", "university_wo"]:
        return "info_tariffs_university"
    elif school_level == "adult":
        return "info_tariffs_adult"
    else:
        # Default fallback for unknown levels
        return "info_tariffs_adult"

def map_topic(topic_text: str) -> str:
    """
    Map topic/subject text to standardized values.
    
    Args:
        topic_text (str): Raw topic text from user input
    
    Returns:
        str: Standardized topic code
    """
    topic_mapping = {
        # Mathematics
        "wiskunde": "math", "math": "math", "mathematics": "math", "maths": "math",
        "rekenen": "math", "algebra": "math", "calculus": "math", "geometry": "math",
        "wiskunde a": "math", "wiskunde b": "math", "wiskunde c": "math", "wiskunde d": "math",
        
        # Statistics
        "statistiek": "stats", "statistics": "stats", "stats": "stats", "data": "stats",
        "kansrekening": "stats", "probability": "stats",
        
        # Sciences  
        "natuurkunde": "science", "physics": "science", "fysica": "science",
        "scheikunde": "chemistry", "chemistry": "chemistry", "chemie": "chemistry",
        "biologie": "science", "biology": "science",
        
        # Languages
        "engels": "english", "english": "english", "engels taal": "english",
        "nederlands": "other", "dutch": "other",
        
        # Programming
        "programmeren": "programming", "programming": "programming", "coding": "programming",
        "python": "programming", "java": "programming", "javascript": "programming",
        "r": "programming", "matlab": "programming", "c++": "programming",
        
        # Other subjects
        "economie": "other", "economics": "other", "bedrijfseconomie": "other",
        "geschiedenis": "other", "history": "other", "aardrijkskunde": "other", "geography": "other"
    }
    
    return topic_mapping.get(topic_text.lower(), "other")

def is_prefill_sufficient_for_trial_lesson(prefilled_info: Dict[str, Any]) -> bool:
    """Lenient sufficiency check used to decide whether to ask for confirmation.

    We consider prefill sufficient when:
    - school_level is present, and
    - a topic is present (topic_secondary OR topic_primary), and
    - some identity cue exists (learner_name OR student_name OR contact_name OR for_who)
    """
    if not prefilled_info:
        print("❌ Prefill empty")
        return False

    has_level = bool(prefilled_info.get("school_level"))
    has_topic = bool(prefilled_info.get("topic_secondary") or prefilled_info.get("topic_primary"))
    has_identity = bool(
        prefilled_info.get("learner_name")
        or prefilled_info.get("student_name")
        or prefilled_info.get("contact_name")
        or prefilled_info.get("for_who")
    )

    if has_level and has_topic and has_identity:
        print("✅ Prefill sufficient for confirmation")
        return True

    if not has_level:
        print("❌ Missing school_level for trial lesson prefill")
    if not has_topic:
        print("❌ Missing topic (primary/secondary) for trial lesson prefill")
    if not has_identity:
        print("❌ Missing identity (name/for_who) for trial lesson prefill")
    return False

def smart_extraction_check(prefilled_info: Dict[str, Any]) -> str:
    """
    Perform smart check on extracted information quality.
    
    Args:
        prefilled_info (Dict[str, Any]): Dictionary with prefilled information
    
    Returns:
        str: Quality assessment ("sufficient", "partial", "insufficient")
    """
    if not prefilled_info:
        return "insufficient"
    
    # Count meaningful fields (not None, not empty string)
    meaningful_fields = {k: v for k, v in prefilled_info.items() 
                        if v is not None and str(v).strip() != ""}
    
    field_count = len(meaningful_fields)
    
    if field_count >= 4:
        return "sufficient"
    elif field_count >= 2:
        return "partial"
    else:
        return "insufficient"

def get_topic_display_mapping(lang: str = "nl") -> Dict[str, str]:
    """
    Get topic display mapping for UI.
    
    Args:
        lang (str): Language code ("nl" or "en")
    
    Returns:
        Dict[str, str]: Mapping of topic codes to display names
    """
    if lang == "nl":
        return {
            "math": "Wiskunde",
            "stats": "Statistiek", 
            "english": "Engels",
            "programming": "Programmeren",
            "science": "Natuurkunde",
            "chemistry": "Scheikunde",
            "other": "Overig"
        }
    else:  # English
        return {
            "math": "Mathematics",
            "stats": "Statistics",
            "english": "English", 
            "programming": "Programming",
            "science": "Physics",
            "chemistry": "Chemistry",
            "other": "Other"
        }

def get_relationship_display_mapping(lang: str = "nl") -> Dict[str, str]:
    """
    Get relationship display mapping for UI.
    
    Args:
        lang (str): Language code ("nl" or "en")
    
    Returns:
        Dict[str, str]: Mapping of relationship codes to display names
    """
    if lang == "nl":
        return {
            "self": "Voor mezelf",
            "child": "Voor mijn kind",
            "student": "Voor een student", 
            "other": "Voor iemand anders",
            "parent": "Ouder",
            "teacher": "Docent"
        }
    else:  # English
        return {
            "self": "For myself",
            "child": "For my child",
            "student": "For a student",
            "other": "For someone else", 
            "parent": "Parent",
            "teacher": "Teacher"
        }

def detect_segment(contact_id):
    """Detect segment based on contact attributes and history"""
    from modules.utils.text_helpers import get_contact_attrs, set_contact_attrs
    
    contact_attrs = get_contact_attrs(contact_id)
    
    # Check if segment is already set
    existing_segment = contact_attrs.get("segment")
    if existing_segment:
        return existing_segment
    
    # 1. Weekend segment (whitelist check)
    if contact_attrs.get("weekend_whitelisted"):
        segment = "weekend"
    # 2. Returning broadcast (begin school year list)
    elif contact_attrs.get("returning_broadcast"):
        segment = "returning_broadcast"
    # 3. Existing customer - check multiple indicators
    elif (contact_attrs.get("customer_since") or 
          contact_attrs.get("has_paid_lesson") or
          contact_attrs.get("has_completed_intake") or
          contact_attrs.get("intake_completed") or
          contact_attrs.get("trial_lesson_completed") or
          contact_attrs.get("lesson_booked") or
          contact_attrs.get("customer_status") == "active"):
        segment = "existing"
    # 4. Default to new
    else:
        segment = "new"
    
    # Store the detected segment
    set_contact_attrs(contact_id, {"segment": segment})
    return segment
