from __future__ import annotations

from typing import List, Optional
import re
import unicodedata


def _normalize(text: str) -> str:
    value = (text or "").strip().lower()
    # Remove explicit information symbol before normalization to avoid leftover 'i'
    value = value.replace("ℹ️", "").replace("ℹ", "")
    # Normalize unicode to separate combining marks (e.g., keycap digits)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    # Strip standalone symbol-emoji characters (e.g., ℹ, ✅, etc.) that can precede labels
    # Keep currency/math/connector punctuation; remove only "Other Symbols" (So)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "So")
    # Remove common emoji prefixes/suffixes and extra spaces
    for ch in [
        "✅", "❌", "🎯", "📅", "📖", "👨‍🏫", "🌅", "📝", "💰", "⏰", "📋", "💻", "🏆", "🎨", "🎓", "💼", "⬅️",
        # Keycap decorations and variation selectors that sometimes sneak in
        "️", "⃣"
    ]:
        value = value.replace(ch, "")
    return " ".join(value.split())


def match_menu_selection(message_text: str, option_values_in_order: List[str]) -> Optional[str]:
    """
    Match a user's message against a list of menu option values.

    The function supports:
    - Numeric selection ("1", "2", ...) mapped to the index of the options list
    - Exact match against an option value (case-insensitive)
    - Simple normalized match (underscores and spaces treated equally)
    """
    if not message_text:
        return None

    normalized = _normalize(message_text)

    # 1) Numeric selection (support formats like "1", "1.", "1)", "1️⃣", "optie 1", "keuze 1")
    number_match = re.match(r"^(?:optie|keuze)?\s*(\d+)", normalized)
    if number_match:
        index = int(number_match.group(1)) - 1
        if 0 <= index < len(option_values_in_order):
            return option_values_in_order[index]

    # 2) Direct match to any value
    normalized_values = [
        _normalize(v).replace("_", " ") for v in option_values_in_order
    ]
    needle = normalized.replace("_", " ")

    # Exact match on normalized values
    for idx, nv in enumerate(normalized_values):
        if needle == nv:
            return option_values_in_order[idx]

    # 3) Synonym/alias mapping to canonical intents
    synonyms = {
        # Generic
        "info": "info", "informatie": "info", "meer info": "info", "more info": "info", "meer informatie": "info", "information": "info",
        "contact": "handoff", "stephen": "handoff", "spreken": "handoff", "mens": "handoff", "mensen": "handoff", "persoon": "handoff",
        # Trial / planning
        "proefles": "trial_lesson", "gratis proefles": "trial_lesson", "trial": "trial_lesson",
        "trial lesson": "trial_lesson", "trial les": "trial_lesson", "free trial lesson": "trial_lesson",
        "plan les": "plan_lesson", "les inplannen": "plan_lesson", "plan": "plan_lesson",
        "inplannen": "plan_lesson", "plan les afspraak": "plan_lesson",
        # Info submenus
        "werkwijze": "work_method", "methode": "work_method", "method": "work_method",
        "hoe werkt": "work_method", "hoe werkt stephen": "work_method",
        "tarieven": "tariffs", "prijzen": "tariffs", "pricing": "tariffs",
        "diensten": "services", "service": "services",
        # Preferences-based quick actions
        "zelfde voorkeuren": "same_preferences", "same preferences": "same_preferences",
        "oude voorkeuren": "old_preferences", "old preferences": "old_preferences",
        # Handoff
        "stephen spreken": "handoff", "spreek met stephen": "handoff", "menselijk": "handoff",
    }
    alias = synonyms.get(needle)
    if alias and alias in option_values_in_order:
        return alias

    return None


