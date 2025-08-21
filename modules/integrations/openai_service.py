#!/usr/bin/env python3
"""
OpenAI Integration Service for TutorBot

This module contains all OpenAI-related functions for:
- Message analysis and prefill extraction
- Preference analysis for lesson scheduling
- Info request analysis
"""

import os
import json
import openai
from typing import Dict, Any

# Import from main.py dependencies
# send_admin_warning is still in main.py, will be imported later

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
from modules.core.config import OPENAI_MODEL, OPENAI_TIMEOUT, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE

def analyze_preferences_with_openai(message: str, conversation_id: int = None) -> Dict[str, Any]:
    """Analyze lesson preferences with OpenAI to extract structured information"""
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not available, skipping preferences analysis")
        return {
            "preferred_times": "",
            "location_preference": "",
            "other_preferences": "",
            "confidence": 0.0
        }
    
    system_prompt = """
    Je bent een AI assistent die lesvoorkeuren analyseert om gestructureerde informatie te extraheren.
    
    Analyseer de boodschap en extraheer:
    1. **Voorkeur tijden**: Wanneer is de persoon beschikbaar voor lessen?
    2. **Locatie voorkeur**: Waar wil de persoon les hebben?
    3. **Andere voorkeuren**: Eventuele andere relevante voorkeuren
    
    Geef een JSON response met:
    {
        "preferred_times": "string", // Beschikbare tijden (bijv. "maandag 19:00, woensdag 20:00")
        "location_preference": "string", // Locatie voorkeur (bijv. "thuis", "Science Park", "VU/UvA")
        "other_preferences": "string", // Andere voorkeuren
        "confidence": "float" // Zekerheid (0.0-1.0)
    }
    
    Voorbeelden:
    - "Ik ben beschikbaar op maandag en woensdag om 19:00" → preferred_times: "maandag 19:00, woensdag 19:00"
    - "Ik wil les thuis" → location_preference: "thuis"
    - "Ik heb les op Science Park" → location_preference: "Science Park"
    - "Ik ben flexibel met tijden" → preferred_times: "flexibel"
    
    Als de boodschap onduidelijk is of geen specifieke voorkeuren bevat, geef confidence: 0.0
    
    Geef alleen de JSON response, geen extra tekst.
    """
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyseer deze lesvoorkeuren: {message}"}
            ],
                    max_completion_tokens=OPENAI_MAX_TOKENS,
        temperature=OPENAI_TEMPERATURE
        )
        
        result = response.choices[0].message.content.strip()
        print(f"🤖 Preferences analysis result: {result}")
        
        # Parse JSON response
        import json
        analysis = json.loads(result)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing preferences: {e}")
        if conversation_id:
            # Import here to avoid circular imports
            from modules.utils.text_helpers import send_admin_warning
            send_admin_warning(conversation_id, f"Preferences analysis failed: {str(e)[:100]}")
        
        return {
            "preferred_times": "",
            "location_preference": "",
            "other_preferences": "",
            "confidence": 0.0
        }

def analyze_preferences_with_openai_v2(message: str, conversation_id: int = None) -> Dict[str, Any]:
    """Analyze user preferences for lesson scheduling using OpenAI"""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        system_prompt = """Je bent een assistent die voorkeuren voor lesplanning analyseert. 

Analyseer de voorkeuren van de gebruiker en geef 3 concrete lesmomenten voor de komende 2 weken.

BELANGRIJKE REGELS:
- Alleen weekdagen (maandag t/m vrijdag)
- Alleen tijden tussen 17:00-19:00 voor proeflessen
- Alleen tijden tussen 14:00-20:00 voor reguliere lessen
- Geef specifieke data en tijden
- Houd rekening met de voorkeuren van de gebruiker

VOORKEUREN ANALYSEREN:
- Dagen: maandag, dinsdag, woensdag, donderdag, vrijdag
- Tijden: ochtend (8:00-12:00), middag (12:00-17:00), avond (17:00-20:00)
- Specifieke tijden: "om 15:00", "rond 16:30", etc.

Geef je antwoord als JSON in dit formaat:
{
    "preferred_days": ["maandag", "woensdag"],
    "preferred_times": ["avond", "17:00"],
    "suggested_slots": [
        {
            "date": "2024-01-15",
            "time": "17:00",
            "day_name": "maandag",
            "reason": "Past bij voorkeur voor maandag avond"
        },
        {
            "date": "2024-01-17", 
            "time": "17:30",
            "day_name": "woensdag",
            "reason": "Past bij voorkeur voor woensdag avond"
        },
        {
            "date": "2024-01-22",
            "time": "18:00", 
            "day_name": "maandag",
            "reason": "Alternatief moment volgende week"
        }
    ]
}"""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voorkeuren van gebruiker: {preferences_text}"}
            ],
                    temperature=OPENAI_TEMPERATURE,
        max_completion_tokens=500
        )
        
        result = response.choices[0].message.content
        print(f"🤖 OpenAI preferences analysis: {result}")
        
        # Parse JSON response
        try:
            analysis = json.loads(result)
            return analysis
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse OpenAI JSON response: {e}")
            return {
                "preferred_days": [],
                "preferred_times": [],
                "suggested_slots": []
            }
            
    except Exception as e:
        print(f"❌ OpenAI preferences analysis failed: {e}")
        return {
            "preferred_days": [],
            "preferred_times": [],
            "suggested_slots": []
        }

def analyze_first_message_with_openai(message: str, conversation_id: int = None, send_admin_warning_func=None) -> Dict[str, Any]:
    """Analyze first message using OpenAI to extract intake information"""
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not available, skipping prefill")
        if conversation_id and send_admin_warning_func:
            send_admin_warning_func(conversation_id, "OpenAI API key not configured - prefill disabled")
        return {}
    
    system_prompt = """
    Je bent een AI assistent die het eerste bericht van een potentiële student analyseert om intake informatie te extraheren.
    
    Over Stephen (de tutor):
    - Master Wiskunde met specialisatie in quantuminformatica en dynamische systemen
    - Bevoegd docent wiskunde (ILO)
    - Expert in statistiek, data science, programmeren (Python/R/JavaScript)
    - Ervaring van vmbo tot universiteit, inclusief speciaal onderwijs
    - Tweetalig (Nederlands/Engels) + internationale curricula (IB/Cambridge)
    - Scriptiebegeleider voor psychologie, cybersecurity, statistiek
    - Ervaring met MBO-rekenen, alle wiskunde profielen (A/B/C/D)
    
    Analyseer het bericht en extraheer de volgende informatie:
    
    - **is_adult**: Boolean - Is de persoon 18+ jaar oud?
    - **for_who**: String - Voor wie is de les? ("self", "child", "student", "other")
    - **learner_name**: String - Naam van de leerling (roepnaam of volledige naam)
    - **school_level**: String - Onderwijsniveau ("po", "vmbo", "havo", "vwo", "mbo", "university_wo", "university_hbo", "adult")
    
    BELANGRIJKE REGELS VOOR SCHOOLNIVEAU:
    - **"university_wo"**: Voor universiteitsstudenten (WO), inclusief volwassenen die universiteitsvakken volgen
    - **"university_hbo"**: Voor HBO studenten, inclusief volwassenen die HBO vakken volgen  
    - **"adult"**: Voor volwassenen die middelbare school stof moeten leren (volwassenenonderwijs)
    - **"mbo"**: Voor MBO studenten
    - **"vwo/havo/vmbo"**: Voor middelbare scholieren
    - **"po"**: Voor basisschool leerlingen
    
    KRITIEKE REGEL: 
    - Als iemand studeert aan een universiteit (zoals Rijksuniversiteit Groningen, UvA, VU, etc.), 
      gebruik dan ALTIJD "university_wo", ook als ze volwassen zijn
    - "adult" is alleen voor volwassenen die middelbare school stof moeten leren (volwassenenonderwijs), 
      niet voor universiteitsstudenten
    - "Volwassenenonderwijs" = middelbare school niveau voor volwassenen (vmbo/havo/vwo stof)
    
    BELANGRIJKSTE REGEL: Als de tekst "universiteit", "university", "Rijksuniversiteit", "UvA", "VU", "TU", 
    "WO", "bachelor", "master", "BSc", "MSc", "2e jaars", "3e jaars", "eerste jaar", "tweede jaar", "derde jaar",
    "bachelor student", "master student", "universiteitsstudent", "universiteit student" bevat, dan is het ALTIJD "university_wo" of "university_hbo", 
    NOOIT "adult"!
    - **topic_primary**: String - Hoofdvak/onderwerp ("math", "stats", "english", "programming", "science", "chemistry", "other")
    - **topic_secondary**: String - Specifiek vak/onderwerp (bijv. "wiskunde B", "statistiek", "calculus")
    - **goals**: String - Leerdoelen, deadlines of specifieke toetsen/examens (bijv. "eindexamen wiskunde B", "tentamen statistiek volgende week", "MBO-rekentoets")
    - **preferred_times**: String - Voorkeur voor tijdstippen
    - **lesson_mode**: String - Lesmodus ("online", "in_person", "hybrid")
    - **toolset**: String - Tools die gebruikt worden ("none", "python", "excel", "spss", "r", "other")
    - **program**: String - Specifiek programma ("none", "mbo_rekenen_2f", "mbo_rekenen_3f", "ib_math_sl", "ib_math_hl", "cambridge")
    - **relationship_to_learner**: String - Relatie tot leerling ("self", "parent", "teacher", "other")
    - **referral_source**: String - Hoe heeft de persoon over ons gehoord? ("google_search", "social_media", "friend_recommendation", "school_recommendation", "advertisement", "website", "other")
    - **school_name**: String - Naam van de school (bijv. "Spinoza Lyceum")
    - **current_grade**: String - Huidige cijfer of prestatie (bijv. "5,2", "onvoldoende")
    - **location_preference**: String - Locatie voorkeur (bijv. "Science Park", "thuis", "online")
    - **contact_name**: String - Naam van de contactpersoon (degene die het bericht stuurt)
    - **urgency**: String - Urgentie van de aanvraag (bijv. "hoog", "gemiddeld", "laag", "examen volgende week")
    
    BELANGRIJKE REGELS VOOR "VOOR WIE" DETECTIE:
    - **"self"**: Als de persoon schrijft over zichzelf (bijv. "ik heb moeite met", "ik zit in", "mijn naam is")
    - **"child"**: Als de persoon schrijft over hun kind (bijv. "mijn dochter", "mijn zoon", "mijn kind")
    - **"student"**: Als de persoon schrijft over een student die ze begeleiden
    - **"other"**: Als de persoon schrijft over iemand anders (bijv. "mijn vriend", "mijn collega")
    
    BELANGRIJKE REGELS VOOR RELATIE DETECTIE:
    - **"self"**: Als het voor zichzelf is
    - **"parent"**: Als het een ouder is die voor hun kind schrijft
    - **"teacher"**: Als het een docent is die voor een student schrijft
    - **"other"**: Andere relaties (vriend, collega, etc.)
    
    BELANGRIJKE REGELS VOOR SCHOOLNIVEAU INTERPRETATIE:
    - **Nederlandse schoolniveau afkortingen correct interpreteren:**
      * "6V", "6v", "6 V", "6 v", "6e VWO", "6e vwo" = "vwo" (6e klas VWO)
      * "5V", "5v", "5 V", "5 v", "5e VWO", "5e vwo" = "vwo" (5e klas VWO)
      * "4V", "4v", "4 V", "4 v", "4e VWO", "4e vwo" = "vwo" (4e klas VWO)
      * "3H", "3h", "3 H", "3 h", "3e HAVO", "3e havo" = "havo" (3e klas HAVO)
      * "4H", "4h", "4 H", "4 h", "4e HAVO", "4e havo" = "havo" (4e klas HAVO)
      * "5H", "5h", "5 H", "5 h", "5e HAVO", "5e havo" = "havo" (5e klas HAVO)
      * "4M", "4m", "4 M", "4 m", "4e VMBO", "4e vmbo" = "vmbo" (4e klas VMBO)
      * "3M", "3m", "3 M", "3 m", "3e VMBO", "3e vmbo" = "vmbo" (3e klas VMBO)
      * "N&T", "N&G", "E&M", "C&M" = "vwo" (VWO profielen)
      * "TL", "GL", "BL", "KL" = "vmbo" (VMBO leerwegen)
    
    BELANGRIJKE REGELS VOOR WISKUNDE VAKKEN:
    - **Wiskunde A** → topic_primary: "math", topic_secondary: "wiskunde A" (meer praktisch, minder abstract)
    - **Wiskunde B** → topic_primary: "math", topic_secondary: "wiskunde B" (meer abstract, voor exacte studies)
    - **Wiskunde C** → topic_primary: "math", topic_secondary: "wiskunde C" (voor cultuurprofiel)
    - **Wiskunde D** → topic_primary: "math", topic_secondary: "wiskunde D" (voor exacte studies, extra vak)
    - **Statistiek** → topic_primary: "stats", topic_secondary: "statistiek"
    - **Calculus** → topic_primary: "math", topic_secondary: "calculus"
    - **IB Math SL** → topic_primary: "math", topic_secondary: "IB Math SL"
    - **IB Math HL** → topic_primary: "math", topic_secondary: "IB Math HL"
    - **MBO Rekenen 2F** → topic_primary: "math", topic_secondary: "MBO Rekenen 2F"
    - **MBO Rekenen 3F** → topic_primary: "math", topic_secondary: "MBO Rekenen 3F"
    
    VOORBEELDEN VAN "VOOR WIE" DETECTIE:
    - "Mijn naam is Simon, ik zit in 6V" → for_who: "self", learner_name: "Simon"
    - "Mijn dochter Maria zit in Havo 5" → for_who: "child", learner_name: "Maria", relationship_to_learner: "parent"
    - "Ik ben een docent en zoek hulp voor mijn student" → for_who: "student", relationship_to_learner: "teacher"
    - "Mijn vriend heeft problemen met wiskunde" → for_who: "other", relationship_to_learner: "other"
    
    VOORBEELDEN VAN SCHOOLNIVEAU:
    - "Ik studeer aan de Rijksuniversiteit Groningen" → school_level: "university_wo"
    - "Ik volg een HBO opleiding" → school_level: "university_hbo"  
    - "Ik ben volwassen en moet vmbo wiskunde leren" → school_level: "adult"
    - "Ik doe volwassenenonderwijs voor havo wiskunde" → school_level: "adult"
    - "Ik zit in 6V" → school_level: "vwo"
    - "Ik doe MBO niveau 4" → school_level: "mbo"
    - "Ik ben 25 en studeer aan de UvA" → school_level: "university_wo" (NIET "adult")
    - "Ik ben volwassen en moet middelbare school stof leren" → school_level: "adult"
    - "Ik zoek een tutor voor het vak aan de Rijksuniversiteit Groningen" → school_level: "university_wo" (NIET "adult")
    - "BSc International Economics aan de universiteit" → school_level: "university_wo" (NIET "adult")
    - "2e jaars wiskunde vak binnen de BSc International Economics" → school_level: "university_wo" (NIET "adult")
    - "Ik ben een bachelor student" → school_level: "university_wo"
    - "Ik doe een master" → school_level: "university_wo"
    - "Ik ben een universiteitsstudent" → school_level: "university_wo"
    - "Ik zit in mijn tweede jaar aan de universiteit" → school_level: "university_wo"
    
    Belangrijk: 
    - **topic_secondary** is het specifieke vak/onderwerp (bijv. "wiskunde B", "statistiek")
    - **goals** zijn de leerdoelen, deadlines of toetsen/examens waar naartoe gewerkt wordt (bijv. "eindexamen wiskunde B", "tentamen volgende week")
    - **contact_name** is de naam van degene die het bericht stuurt (niet de leerling)
    - **urgency** kan afgeleid worden uit woorden als "dringend", "spoed", "examen volgende week", etc.
    
    Als informatie niet expliciet wordt genoemd, gebruik dan null of een lege string.
    Geef alleen de JSON response, geen extra tekst.
    """
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyseer dit bericht: {message}"}
            ],
                    max_completion_tokens=500,
        timeout=OPENAI_TIMEOUT
        )
        
        content = response.choices[0].message.content.strip()
        print(f"🔍 OpenAI raw response: '{content}'")
        print(f"🔍 Response length: {len(content)}")
        
        if not content:
            print(f"❌ OpenAI returned empty response")
            return {}
            
        try:
            result = json.loads(content)
            print(f"✅ OpenAI prefill analysis completed")
            return result
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse OpenAI response: {e}")
            print(f"🔍 Raw content that failed to parse: '{content}'")
            return {}
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        
        # Send admin warning about API failure
        if conversation_id and send_admin_warning_func:
            error_details = str(e)
            if "quota" in error_details.lower() or "insufficient_quota" in error_details.lower():
                warning_message = "OpenAI API quota exceeded - please check billing"
            elif "rate_limit" in error_details.lower():
                warning_message = "OpenAI API rate limit exceeded"
            elif "authentication" in error_details.lower() or "invalid_api_key" in error_details.lower():
                warning_message = "OpenAI API authentication failed - check API key"
            elif "timeout" in error_details.lower():
                warning_message = "OpenAI API timeout - network issues"
            else:
                warning_message = f"OpenAI API error: {error_details[:100]}"
            
            send_admin_warning_func(conversation_id, warning_message)
        
        # Return empty result to continue with normal flow
        print(f"⚠️ Returning empty result due to OpenAI error - continuing with normal flow")
        return {}

def analyze_info_request_with_openai(message: str, conversation_id: int = None) -> Dict[str, Any]:
    """Analyze info request using OpenAI to extract specific information needs"""
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not available, skipping info analysis")
        return {}
    
    system_prompt = """
    Je bent een AI assistent die berichten analyseert om te bepalen welke informatie de gebruiker nodig heeft.
    
    Analyseer het bericht en bepaal:
    
    - **info_type**: String - Type informatie dat wordt gevraagd ("pricing", "availability", "location", "experience", "subjects", "other")
    - **urgency**: String - Urgentie van de vraag ("high", "medium", "low")
    - **specific_question**: String - Specifieke vraag die wordt gesteld
    - **context**: String - Context van de vraag (bijv. "voor mijn kind", "voor mezelf", "voor een student")
    
    Geef je antwoord als JSON in dit formaat:
    {
        "info_type": "pricing",
        "urgency": "medium", 
        "specific_question": "Wat kosten de lessen?",
        "context": "voor mijn dochter in 5V"
    }
    """
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyseer dit bericht: {message}"}
            ],
                    max_completion_tokens=OPENAI_MAX_TOKENS,
        timeout=OPENAI_TIMEOUT
        )
        
        content = response.choices[0].message.content.strip()
        print(f"🔍 OpenAI info request analysis: {content}")
        
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse OpenAI info request response: {e}")
            return {}
            
    except Exception as e:
        print(f"❌ OpenAI info request analysis failed: {e}")
        return {}

def prefill_intake_from_message(message: str, conversation_id: int = None, send_admin_warning_func=None) -> Dict[str, Any]:
    """Extract intake information from message using OpenAI"""
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not available, skipping prefill")
        return {}
    
    # Use the same analysis as first message
    return analyze_first_message_with_openai(message, conversation_id, send_admin_warning_func)

def interpret_slot_selection_with_openai(user_text: str, available_slots: list[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Interpret a user's free-text reply about scheduling and map it to one of the available slots.

    Returns a dict like:
      { "intent": "select" | "more_options" | "invalid", "chosen_iso": "YYYY-MM-DDTHH:MM:SS+TZ" }
    """
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not available, skipping slot interpretation")
        return {"intent": "invalid"}

    # Build a compact slot list for the prompt
    import json as _json
    slot_lines = []
    for idx, slot in enumerate(available_slots, 1):
        label = slot.get("label") or slot.get("start") or slot.get("start_iso") or "unknown"
        start_iso = slot.get("start_iso") or slot.get("start") or ""
        slot_lines.append(f"{idx}. {label} | {start_iso}")

    system_prompt = (
        "Je bent een assistent die een vrije tekst van de gebruiker koppelt aan één van de beschikbare tijdsloten."
        "\n\nRegels:"
        "\n- Kies de beste match op basis van datum/weekday/tijd."
        "\n- Als de gebruiker zegt 'meer opties' of iets vergelijkbaars, kies intent: 'more_options'."
        "\n- Als er geen duidelijke match is, kies intent: 'invalid'."
        "\n- Antwoord uitsluitend met JSON in dit formaat:"
        "\n{\n  \"intent\": \"select|more_options|invalid\",\n  \"chosen_iso\": \"YYYY-MM-DDTHH:MM:SS+TZ\"\n}"
    )

    user_prompt = (
        "Beschikbare slots (index | label | start_iso):\n" + "\n".join(slot_lines) +
        f"\n\nGebruikersantwoord: {user_text}\n"
    )

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
                    temperature=OPENAI_TEMPERATURE,
        max_completion_tokens=OPENAI_MAX_TOKENS,
        )
        content = resp.choices[0].message.content.strip()
        print(f"🤖 Slot interpretation raw: {content}")
        try:
            data = _json.loads(content)
            # Basic validation
            intent = data.get("intent")
            chosen_iso = data.get("chosen_iso")
            if intent not in ("select", "more_options", "invalid"):
                intent = "invalid"
            return {"intent": intent, "chosen_iso": chosen_iso}
        except Exception as e:
            print(f"❌ Failed to parse slot interpretation JSON: {e}")
            return {"intent": "invalid"}
    except Exception as e:
        print(f"❌ OpenAI slot interpretation failed: {e}")
        return {"intent": "invalid"}
