#!/usr/bin/env python3
"""
Language Detection and Processing Utilities for TutorBot

This module contains functions for language detection, validation,
and language-related processing.
"""

def detect_language_from_message(message: str) -> str:
    """
    Detect language from message content.
    
    Args:
        message (str): Message text to analyze
    
    Returns:
        str: Language code ("nl" or "en")
    """
    # Simple Dutch detection based on common words
    dutch_indicators = [
        "ik", "je", "jij", "hij", "zij", "wij", "ons", "mijn", "jouw", "zijn", "haar", "hun",
        "ben", "bent", "is", "zijn", "hebben", "heeft", "hebt", "heb",
        "van", "in", "op", "aan", "bij", "met", "voor", "door", "over", "onder",
        "het", "de", "een", "en", "of", "als", "dat", "wat", "wie", "waar", "wanneer", "hoe",
        "goed", "slecht", "groot", "klein", "veel", "weinig", "meer", "minder",
        "hallo", "hoi", "dag", "goedemorgen", "goedemiddag", "goedenavond",
        "dank", "bedankt", "alsjeblieft", "graag", "sorry", "excuus",
        "wiskunde", "bijles", "hulp", "leren", "studeren", "school", "universiteit",
        "kan", "wil", "moet", "zou", "mag", "zal", "hoeft",
        "jaar", "uur", "dag", "week", "maand", "tijd",
        "thuis", "online", "fysiek", "locatie", "adres",
        "student", "leerling", "docent", "leraar", "tutor",
        "vwo", "havo", "vmbo", "mbo", "hbo", "wo",
        "wiskunde", "natuurkunde", "scheikunde", "biologie", "engels", "nederlands"
    ]
    
    # English indicators
    english_indicators = [
        "i", "you", "he", "she", "we", "they", "my", "your", "his", "her", "our", "their",
        "am", "are", "is", "was", "were", "have", "has", "had", "do", "does", "did",
        "the", "a", "an", "and", "or", "if", "that", "what", "who", "where", "when", "how",
        "good", "bad", "big", "small", "much", "little", "more", "less",
        "hello", "hi", "good morning", "good afternoon", "good evening",
        "thank", "thanks", "please", "sorry", "excuse",
        "math", "tutoring", "help", "learn", "study", "school", "university",
        "can", "will", "must", "would", "may", "shall", "should",
        "year", "hour", "day", "week", "month", "time",
        "home", "online", "physical", "location", "address",
        "student", "pupil", "teacher", "tutor", "instructor"
    ]
    
    # Convert message to lowercase for checking
    message_lower = message.lower()
    
    # Count Dutch and English indicators
    dutch_count = sum(1 for word in dutch_indicators if word in message_lower)
    english_count = sum(1 for word in english_indicators if word in message_lower)
    
    print(f"🔍 Language detection: Dutch indicators: {dutch_count}, English indicators: {english_count}")
    
    # Determine language based on counts
    if dutch_count > english_count:
        print(f"🇳🇱 Detected Dutch language")
        return "nl"
    elif english_count > dutch_count:
        print(f"🇬🇧 Detected English language") 
        return "en"
    else:
        # Default to Dutch if no clear indicators
        print(f"🤷 No clear language indicators, defaulting to Dutch")
        return "nl"

def validate_language_code(lang: str) -> str:
    """
    Validate and normalize language code.
    
    Args:
        lang (str): Language code to validate
    
    Returns:
        str: Validated language code ("nl" or "en")
    """
    valid_languages = ["nl", "en"]
    
    if lang and lang.lower() in valid_languages:
        return lang.lower()
    
    # Default to Dutch
    return "nl"

def get_opposite_language(lang: str) -> str:
    """
    Get the opposite language code.
    
    Args:
        lang (str): Current language code
    
    Returns:
        str: Opposite language code
    """
    if lang == "nl":
        return "en"
    elif lang == "en":
        return "nl"
    else:
        return "en"  # Default

def get_language_display_name(lang: str, display_lang: str = "nl") -> str:
    """
    Get the display name for a language.
    
    Args:
        lang (str): Language code to get display name for
        display_lang (str): Language to display the name in
    
    Returns:
        str: Display name for the language
    """
    language_names = {
        "nl": {
            "nl": "Nederlands",
            "en": "Engels"
        },
        "en": {
            "nl": "Dutch", 
            "en": "English"
        }
    }
    
    return language_names.get(display_lang, {}).get(lang, lang)

def is_supported_language(lang: str) -> bool:
    """
    Check if a language is supported by the bot.
    
    Args:
        lang (str): Language code to check
    
    Returns:
        bool: True if language is supported
    """
    supported_languages = ["nl", "en"]
    return lang in supported_languages
