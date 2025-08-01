from datetime import datetime, timedelta
from tutorbot.config import TZ, AGE_TTL_DAYS

def is_valid_name(name):
    """Check if a name is valid (not a weird WhatsApp name)"""
    if not name or len(name) < 2:
        return False
    
    # Check for common WhatsApp weird names
    weird_patterns = [
        "no name", "unknown", "anonymous", "user", "contact",
        "whatsapp", "wa", "bot", "test", "demo", "guest",
        "no-reply", "noreply", "system", "admin", "support"
    ]
    
    name_lower = name.lower().strip()
    
    # Check for weird patterns
    for pattern in weird_patterns:
        if pattern in name_lower:
            return False
    
    # Check for too many emojis or symbols
    emoji_count = sum(1 for char in name if ord(char) > 127)
    if emoji_count > len(name) * 0.5:  # More than 50% emojis
        return False
    
    # Check for too many numbers
    number_count = sum(1 for char in name if char.isdigit())
    if number_count > len(name) * 0.3:  # More than 30% numbers
        return False
    
    # Check for too many special characters
    special_count = sum(1 for char in name if not char.isalnum() and not char.isspace())
    if special_count > len(name) * 0.4:  # More than 40% special chars
        return False
    
    return True

def detect_language(text):
    """Detect if text is English or Dutch"""
    # Common English words that indicate English
    english_indicators = [
        "hello", "hi", "good", "morning", "afternoon", "evening", "thanks", "thank you",
        "please", "help", "information", "trial", "lesson", "student", "parent", "child",
        "online", "offline", "schedule", "payment", "contact", "direct", "speak", "talk",
        "math", "english", "science", "history", "geography", "chemistry", "physics",
        "economics", "study", "skills", "year", "grade", "level", "adult", "minor",
        "consent", "permission", "guardian", "free", "cost", "price", "available",
        "time", "day", "week", "month", "when", "where", "how", "what", "why"
    ]
    
    # Common Dutch words that indicate Dutch
    dutch_indicators = [
        "hallo", "hoi", "goed", "morgen", "middag", "avond", "dank", "dankje", "dank u",
        "alsjeblieft", "help", "informatie", "proefles", "les", "leerling", "ouder", "kind",
        "online", "offline", "plannen", "betaling", "contact", "direct", "spreken", "praten",
        "wiskunde", "nederlands", "engels", "natuurkunde", "scheikunde", "aardrijkskunde",
        "economie", "studie", "vaardigheden", "jaar", "klas", "niveau", "volwassen", "minderjarig",
        "toestemming", "permissie", "voogd", "gratis", "kosten", "prijs", "beschikbaar",
        "tijd", "dag", "week", "maand", "wanneer", "waar", "hoe", "wat", "waarom"
    ]
    
    text_lower = text.lower()
    
    english_count = sum(1 for word in english_indicators if word in text_lower)
    dutch_count = sum(1 for word in dutch_indicators if word in text_lower)
    
    if english_count > dutch_count:
        return "en"
    elif dutch_count > english_count:
        return "nl"
    else:
        return None  # Unknown, will ask user

def now_ams():
    return datetime.now(TZ)

def parse_dt(s):
    """Parse datetime string, return None if invalid"""
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def is_contact_age_valid(attrs: dict) -> bool:
    """True als contact.is_adult bekend en niet verlopen o.b.v. AGE_TTL_DAYS."""
    if "is_adult" not in attrs: 
        return False
    dt = parse_dt(attrs.get("age_verified_at", "")) or datetime(1970,1,1, tzinfo=TZ)
    return (now_ams() - dt) <= timedelta(days=AGE_TTL_DAYS)

def is_weekend_now():
    """Weekendkorting: vr >= 18:00 t/m zo 23:59 (Europe/Amsterdam)."""
    n = now_ams()
    if n.weekday() == 4 and n.hour >= 18:   # vrijdag
        return True
    return n.weekday() in (5, 6)
