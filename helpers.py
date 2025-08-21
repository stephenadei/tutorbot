#!/usr/bin/env python3
"""
Helper functions for TutorBot
"""

def format_detected_info_summary(prefilled, lang):
    """
    Format detected information for display in messages
    
    Args:
        prefilled (dict): Dictionary with detected information
        lang (str): Language code ('nl' or 'en')
    
    Returns:
        str: Formatted summary of detected information
    """
    detected_summary = []
    
    # Topic/subject information
    if prefilled.get("topic_primary"):
        topic_display = {
            "math": "wiskunde" if lang == "nl" else "math",
            "stats": "statistiek" if lang == "nl" else "statistics", 
            "english": "Engels" if lang == "nl" else "English",
            "programming": "programmeren" if lang == "nl" else "programming",
            "science": "natuurkunde" if lang == "nl" else "physics",
            "chemistry": "scheikunde" if lang == "nl" else "chemistry"
        }
        topic_text = topic_display.get(prefilled['topic_primary'], prefilled['topic_primary'])
        detected_summary.append(f"vak: {topic_text}" if lang == "nl" else f"subject: {topic_text}")
    
    # For who information
    if prefilled.get("for_who") == "self":
        detected_summary.append("voor jezelf" if lang == "nl" else "for yourself")
    elif prefilled.get("for_who") == "child":
        detected_summary.append("voor je kind" if lang == "nl" else "for your child")
    
    # School level information
    if prefilled.get("school_level"):
        level_display = {
            "po": "basisschool" if lang == "nl" else "primary school",
            "vmbo": "VMBO",
            "havo": "HAVO", 
            "vwo": "VWO",
            "mbo": "MBO",
            "university_wo": "universiteit (WO)" if lang == "nl" else "university (WO)",
            "university_hbo": "universiteit (HBO)" if lang == "nl" else "university (HBO)",
            "adult": "volwassenenonderwijs" if lang == "nl" else "adult education"
        }
        level_text = level_display.get(prefilled['school_level'], prefilled['school_level'])
        detected_summary.append(f"niveau: {level_text}" if lang == "nl" else f"level: {level_text}")
    
    # Learning goals
    if prefilled.get("goals"):
        goals_text = prefilled["goals"]
        detected_summary.append(f"doel: {goals_text}" if lang == "nl" else f"goals: {goals_text}")
    
    if detected_summary:
        if lang == "nl":
            return f" Ik heb gedetecteerd: {', '.join(detected_summary)}."
        else:
            return f" I detected: {', '.join(detected_summary)}."
    else:
        return ""

def get_insufficient_prefill_message(prefilled, lang, general_greeting_tip=""):
    """
    Get the message for insufficient prefill information
    
    Args:
        prefilled (dict): Dictionary with detected information
        lang (str): Language code ('nl' or 'en')
        general_greeting_tip (str): Optional greeting tip to include
    
    Returns:
        str: Formatted message
    """
    detected_text = format_detected_info_summary(prefilled, lang)
    
    if lang == "nl":
        base_msg = f"Bedankt! Ik heb een deel van je informatie kunnen verwerken.{detected_text}"
        if general_greeting_tip:
            base_msg += f"\n\n{general_greeting_tip}"
        base_msg += "\n\nLaten we verder gaan met de intake om alles goed in te vullen."
        return base_msg
    else:
        base_msg = f"Thank you! I was able to process some of your information.{detected_text}"
        if general_greeting_tip:
            base_msg += f"\n\n{general_greeting_tip}"
        base_msg += "\n\nLet's continue with the intake to fill in everything properly."
        return base_msg
