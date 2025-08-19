# =============================================================================
# TUTORBOT - CHATWOOT + WHATSAPP INTEGRATION
# =============================================================================
# 
# 🎯 CRITICAL FLOW: Prefill Confirmation System
# 
# This system ensures users can confirm information extracted from their messages.
# The prefill confirmation flow is CRITICAL for proper WhatsApp menu functionality.
# 
# Key Functions:
# - show_prefill_action_menu(): Primary entry point for confirmation flow
# - send_input_select_only(): Sends interactive WhatsApp menu buttons
# - ChatwootAPI.send_message(): SSL-safe API communication
# 
# IMPORTANT: This flow was recently fixed to prevent SSL errors and ensure
# proper WhatsApp menu display. See docs/ARCHITECTURE/PREFILL_CONFIRMATION_FLOW.md
# 
# =============================================================================
# IMPORTS
# =============================================================================
from flask import Flask, request, jsonify
import openai
from typing import Dict, Any
import os, hmac, hashlib, requests, json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re
from scripts.cw_api import ChatwootAPI, get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs, add_conv_labels, remove_conv_labels, send_text

def safe_set_conv_attrs(conversation_id, attrs):
    """Safely set conversation attributes with error handling"""
    try:
        success = set_conv_attrs(conversation_id, attrs)
        if not success:
            print(f"⚠️ Failed to set conversation attributes for conv {conversation_id}")
        return success
    except Exception as e:
        print(f"⚠️ SSL/Connection error in set_conv_attrs: {e}")
        # Return True to prevent blocking the flow - attributes are not critical
        return True

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Chatwoot Configuration
CW = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID")
TOK = os.getenv("CW_TOKEN")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN")
SIG = os.getenv("CW_HMAC_SECRET")
TZ = ZoneInfo("Europe/Amsterdam")

# Stripe Configuration
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STANDARD_PRICE_ID_60 = os.getenv("STANDARD_PRICE_ID_60")
STANDARD_PRICE_ID_90 = os.getenv("STANDARD_PRICE_ID_90")
WEEKEND_PRICE_ID_60 = os.getenv("WEEKEND_PRICE_ID_60")
WEEKEND_PRICE_ID_90 = os.getenv("WEEKEND_PRICE_ID_90")

# Google Calendar Configuration
GCAL_SERVICE_ACCOUNT_JSON = os.getenv("GCAL_SERVICE_ACCOUNT_JSON")
GCAL_CALENDAR_ID = os.getenv("GCAL_CALENDAR_ID", "primary")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# =============================================================================
# FLASK APP INITIALIZATION
# =============================================================================
app = Flask(__name__)

# Comprehensive translation function
def t(key, lang="nl", **kwargs):
    """Comprehensive translation function"""
    translations = {
        # Language selection
        "language_question": {
            "nl": "🌍 In welke taal wil je communiceren?",
            "en": "🌍 In which language would you like to communicate?"
        },
        "language_set_nl": {
            "nl": "We gaan verder in het Nederlands.",
            "en": "We'll continue in Dutch."
        },
        "language_set_en": {
            "nl": "We'll continue in English.",
            "en": "Great, we'll continue in English."
        },
        "greeting_with_name": {
            "nl": "Hallo {name}! 👋",
            "en": "Hello {name}! 👋"
        },
        "greeting_response": {
            "nl": "Hallo! 👋 Hoe kan ik je vandaag helpen?",
            "en": "Hello! 👋 How can I help you today?"
        },
        
        # Bot introduction messages
        "bot_introduction": {
            "nl": "🤖 *Hoi! Ik ben de TutorBot van Stephen* 👋\n\nIk help je graag met het plannen van bijlessen en het beantwoorden van vragen over onze diensten.\n\n💡 *Tip:* Je kunt ook gewoon je verhaal uittypen en dan help ik je verder. Of je kunt deze informatie direct met Stephen delen:\n\n• Naam en niveau van de leerling\n• Vak of onderwerp\n• Deadlines of doelen\n• Voorkeursdagen/-tijden\n• Online of fysiek\n\nIk heb je bericht geanalyseerd en denk dat je {detected_lang} spreekt. Als je liever {other_lang} wilt gebruiken, typ dan '{other_lang}'.",
            "en": "🤖 *Hi! I'm Stephen's TutorBot* 👋\n\nI'm happy to help you schedule tutoring sessions and answer questions about our services.\n\n💡 *Tip:* You can also just type out your story and I'll help you further. Or you can share this information directly with Stephen:\n\n• Name and level of the student\n• Subject or topic\n• Deadlines or goals\n• Preferred days/times\n• Online or in-person\n\nI've analyzed your message and think you speak {detected_lang}. If you'd prefer to use {other_lang}, just type '{other_lang}'."
        },
        "bot_introduction_detected_nl": {
            "nl": "Nederlands",
            "en": "Dutch"
        },
        "bot_introduction_detected_en": {
            "nl": "Engels", 
            "en": "English"
        },
        "bot_introduction_enhanced": {
            "nl": "🤖 *Hoi! Ik ben de TutorBot van Stephen* 👋\n\nIk help je graag met het plannen van bijlessen en het beantwoorden van vragen over onze diensten.\n\n💡 *Tip:* Je kunt ook gewoon je verhaal uittypen en dan help ik je verder. Of je kunt deze informatie direct met Stephen delen:\n\n• Naam en niveau van de leerling\n• Vak of onderwerp\n• Deadlines of doelen\n• Voorkeursdagen/-tijden\n• Online of fysiek\n\nIk heb je bericht geanalyseerd en denk dat je {detected_lang} spreekt. Als je liever {other_lang} wilt gebruiken, typ dan '{other_lang}'.",
            "en": "🤖 *Hi! I'm Stephen's TutorBot* 👋\n\nI'm happy to help you schedule tutoring sessions and answer questions about our services.\n\n💡 *Tip:* You can also just type out your story and I'll help you further. Or you can share this information directly with Stephen:\n\n• Name and level of the student\n• Subject or topic\n• Deadlines or goals\n• Preferred days/times\n• Online or in-person\n\nI've analyzed your message and think you speak {detected_lang}. If you'd prefer to use {other_lang}, just type '{other_lang}'."
        },
        "bot_introduction_detailed": {
            "nl": "🤖 *Hoi! Ik ben de TutorBot van Stephen* 👋\n\nIk help je graag met het plannen van bijlessen en het beantwoorden van vragen over onze diensten.\n\nIk heb je bericht geanalyseerd en denk dat je {detected_lang} spreekt. Als je liever {other_lang} wilt gebruiken, typ dan '{other_lang}'.",
            "en": "🤖 *Hi! I'm Stephen's TutorBot* 👋\n\nI'm happy to help you schedule tutoring sessions and answer questions about our services.\n\nI've analyzed your message and think you speak {detected_lang}. If you'd prefer to use {other_lang}, just type '{other_lang}'."
        },
        
        # Segment-specific menus
        "menu_new": {
            "nl": "*Waarmee kan ik je helpen?* 🤔\n\nHier zijn je opties:",
            "en": "*How can I help you?* 🤔\n\nHere are your options:"
        },
        "menu_existing": {
            "nl": "*Welkom terug!* 👋\n\nZal ik plannen op basis van je eerdere voorkeuren?",
            "en": "*Welcome back!* 👋\n\nShould I schedule based on your previous preferences?"
        },
        "menu_returning_broadcast": {
            "nl": "*Hi!* 👋\n\nNieuw nummer met assistent om sneller te plannen.",
            "en": "*Hi!* 👋\n\nNew number with assistant for faster scheduling."
        },
        "menu_weekend": {
            "nl": "*Weekend Beschikbaarheid* 🌅\n\nKomend weekend (10:00–18:00):",
            "en": "*Weekend Availability* 🌅\n\nThis weekend (10:00–18:00):"
        },
        
        # Intake questions
        "intake_for_who": {
            "nl": "Is de proefles 👤 voor jezelf of 👥 voor iemand anders?",
            "en": "Is the trial lesson 👤 for yourself or 👥 for someone else?"
        },
        "intake_self_18": {
            "nl": "Ben je 18+? ✅ Ja / ❌ Nee",
            "en": "Are you 18+? ✅ Yes / ❌ No"
        },
        "intake_relationship": {
            "nl": "Wat is je relatie tot de leerling?",
            "en": "What is your relationship to the student?"
        },
        "intake_learner_name": {
            "nl": "Naam van de leerling?",
            "en": "Name of the student?"
        },
        "intake_level": {
            "nl": "Welk niveau?",
            "en": "What level?"
        },
        "intake_subject": {
            "nl": "Welk vak/onderwerp?",
            "en": "Which subject/topic?"
        },
        "intake_goals": {
            "nl": "Wat zijn je leerdoelen, deadlines of specifieke toetsen/examens waar je naartoe werkt? (bijv. 'eindexamen wiskunde B', 'tentamen statistiek volgende week', 'MBO-rekentoets')",
            "en": "What are your learning goals, deadlines or specific tests/exams you're working towards? (e.g. 'math B final exam', 'statistics test next week', 'MBO math test')"
        },
        "intake_times": {
            "nl": "Voorkeursdagen/tijden?",
            "en": "Preferred days/times?"
        },
        "intake_mode": {
            "nl": "Online, fysiek of hybride?",
            "en": "Online, in-person or hybrid?"
        },
        
        # Planning
        "planning_confirm": {
            "nl": "Gekozen: {slot}. Ik zet 'm voorlopig vast.",
            "en": "Booked tentatively: {slot}."
        },
        "planning_invalid_selection": {
            "nl": "Ik begrijp je keuze niet. Kies een van de beschikbare tijden uit de lijst hieronder:",
            "en": "I don't understand your selection. Please choose one of the available times from the list below:"
        },
        "referral_question": {
            "nl": "Hoe ben je bij ons terechtgekomen?",
            "en": "How did you hear about us?"
        },
        "referral_options": {
            "nl": "Kies een optie:",
            "en": "Choose an option:"
        },
        "planning_more_options": {
            "nl": "Meer opties",
            "en": "More options"
        },
        "planning_weekend_only": {
            "nl": "Voor deze planning zijn slots op za/zo tussen 10:00–18:00 beschikbaar. Zal ik opties sturen?",
            "en": "For this scheduling, slots are available on Sat/Sun between 10:00–18:00. Should I send options?"
        },
        
        # Payment
        "payment_link": {
            "nl": "Hier is je betaalverzoek: {link}. Na betaling is je plek bevestigd.",
            "en": "Here's your payment link: {link}. Once paid, your slot is confirmed."
        },
        "payment_overdue": {
            "nl": "Je betaling is nog niet ontvangen. Hier is je betaalverzoek opnieuw: {link}",
            "en": "Your payment hasn't been received yet. Here's your payment link again: {link}"
        },
        
        # Info
        "info_rates": {
            "nl": "Mijn tarieven beginnen bij €50/uur. Interesse in een gratis proefles van 30 minuten?",
            "en": "My rates start at €50/hour. Interested in a free trial lesson of 30 minutes?"
        },
        "info_menu_question": {
            "nl": "*📄 Informatie*\n\nWaarover wil je meer weten?\n\n💡 *Tip:* Je kunt ook gewoon je verhaal uittypen en dan help ik je verder.",
            "en": "*📄 Information*\n\nWhat would you like to know more about?\n\n💡 *Tip:* You can also just type out your story and I'll help you further."
        },
        "info_tariffs": {
            "nl": "💰 *Tarieven*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n🎓 *Voortgezet onderwijs 20+:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €230\n\n🎓 *Voortgezet onderwijs 20-:*\n• 1 les (1 uur): €75\n• 2 lessen (2 uur): €130\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n🎯 *MBO Rekentrajecten (alleen online, 18+):*\n• Spoedpakket: 1 week, 4 uur (€275)\n• Korte cursus: 4 weken, 4 uur (€225)\n• Volledig Commit: 12 weken, 13-14 uur (€550)\n• Volledig Flex: 12 weken, 13-14 uur (€690 in 3 termijnen)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n🎓 *Secondary education 20+:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €230\n\n🎓 *Secondary education 20-:*\n• 1 lesson (1 hour): €75\n• 2 lessons (2 hours): €130\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n🎯 *MBO Math trajectories (online only, 18+):*\n• Emergency: 1 week, 4 hours (€275)\n• Short course: 4 weeks, 4 hours (€225)\n• Full Commit: 12 weeks, 13-14 hours (€550)\n• Full Flex: 12 weeks, 13-14 hours (€690 in 3 installments)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        },
        "info_tariffs_under_20": {
            "nl": "💰 *Tarieven (Onder 20 jaar)*\n\n🎓 *Voortgezet onderwijs:*\n• 1 les (1 uur): €75\n• 2 lessen (2 uur): €130\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €55 (1u) • €110 (2u) • €165 (4u)\n• 3-4 personen: €45 (1u) • €80 (2u) • €125 (4u)",
            "en": "💰 *Rates (Under 20 years)*\n\n🎓 *Secondary education:*\n• 1 lesson (1 hour): €75\n• 2 lessons (2 hours): €130\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €55 (1h) • €110 (2h) • €165 (4h)\n• 3-4 persons: €45 (1h) • €80 (2h) • €125 (4h)"
        },
        "info_tariffs_over_20": {
            "nl": "💰 *Tarieven (20 jaar en ouder)*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n🎓 *Voortgezet onderwijs:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €230\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n🎯 *MBO Rekentrajecten:*\n• Spoedpakket: 1 week, 4 uur (€275)\n• Korte cursus: 4 weken, 4 uur (€225)\n• Volledig Commit: 12 weken, 13-14 uur (€550)\n• Volledig Flex: 12 weken, 13-14 uur (€690 in 3 termijnen)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates (20 years and older)*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n🎓 *Secondary education:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €230\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n🎯 *MBO Math trajectories:*\n• Emergency: 1 week, 4 hours (€275)\n• Short course: 4 weeks, 4 hours (€225)\n• Full Commit: 12 weeks, 13-14 hours (€550)\n• Full Flex: 12 weeks, 13-14 hours (€690 in 3 installments)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        },
        "info_travel_costs": {
            "nl": "🚗 *Reiskosten:*\n\n• VU/UvA: €15\n• Thuis (Amsterdam): €40\n• Science Park: €0",
            "en": "🚗 *Travel costs:*\n\n• VU/UvA: €15\n• Home (Amsterdam): €40\n• Science Park: €0"
        },
        "info_last_minute": {
            "nl": "⏰ *Last-minute toeslagen:*\n\n• < 24 uur: +20%\n• < 12 uur: +50%",
            "en": "⏰ *Last-minute surcharges:*\n\n• < 24 hours: +20%\n• < 12 hours: +50%"
        },
        "info_conditions": {
            "nl": "📋 *Pakketvoorwaarden:*\n\n⏱️ *Geldigheid:*\n• 2 lessen: 2 weken\n• 4 lessen: 1 maand\n\n🎯 *Flex-premium:*\n• 2 lessen: +€15\n• 4 lessen: +€30\n\n💳 *Betaling:*\n• Factuur na les\n• Termijn: 14 dagen\n\n❌ *Annuleren:*\n• ≥24u: gratis\n• <24u: 100%",
            "en": "📋 *Package conditions:*\n\n⏱️ *Validity:*\n• 2 lessons: 2 weeks\n• 4 lessons: 1 month\n\n🎯 *Flex-premium:*\n• 2 lessons: +€15\n• 4 lessons: +€30\n\n💳 *Payment:*\n• Invoice after lesson\n• Term: 14 days\n\n❌ *Cancel:*\n• ≥24h: free\n• <24h: 100%"
        },
        "info_work_method": {
            "nl": "🎯 *Mijn Werkwijze*\n\n👨‍🏫 *Achtergrond:*\n• MSc Data Science (UvA)\n• 10+ jaar ervaring\n• Expertise: Wiskunde, programmeren, statistiek\n\n🎯 *Aanpak:*\n• *Persoonlijk*: Elke student uniek\n• *Diagnostisch*: Start met intake\n• *Flexibel*: Online en fysiek\n• *Technologie*: iPad, AI, WhatsApp\n\n📚 *Lesmethode:*\n• Leerdoelgericht\n• Activerende didactiek\n• Formatieve evaluatie\n• Inclusiviteit (autisme, ADHD, NT2)\n\n💻 *Tools:*\n• iPad-aantekeningen\n• AI-ondersteuning\n• WhatsApp 7 dagen\n• Online whiteboards\n\n🏆 *Resultaten:*\n• 500+ studenten\n• 98% tevredenheid\n• 4.9/5 beoordeling\n• 95% slagingspercentage",
            "en": "🎯 *My Work Method*\n\n👨‍🏫 *Background:*\n• MSc Data Science (UvA)\n• 10+ years experience\n• Expertise: Math, programming, statistics\n\n🎯 *Approach:*\n• *Personal*: Every student unique\n• *Diagnostic*: Start with intake\n• *Flexible*: Online and in-person\n• *Technology*: iPad, AI, WhatsApp\n\n📚 *Teaching Method:*\n• Goal-oriented\n• Activating didactics\n• Formative evaluation\n• Inclusivity (autism, ADHD, NT2)\n\n💻 *Tools:*\n• iPad notes\n• AI support\n• WhatsApp 7 days\n• Online whiteboards\n\n🏆 *Results:*\n• 500+ students\n• 98% satisfaction\n• 4.9/5 rating\n• 95% pass rate"
        },
        "info_personal_background": {
            "nl": "👨‍🏫 *Persoonlijke Achtergrond*\n\n*Stephen Adei - MSc Mathematics*\n• **MSc Mathematics** (Gespecialiseerd in quantum informatie en discrete wiskunde)\n• **Master Leraar** (Eerstegraads bevoegdheid in één keer)\n• 10+ jaar ervaring in onderwijs sinds 2012\n• Persoonlijke reis: Van wiskunde-uitdagingen naar excellente resultaten\n• Multidisciplinaire achtergrond: Wiskunde, programmeren, muziek, fotografie\n• Visie: Onderwijs moet empoweren, niet alleen kennis overdragen\n\n*Expertise:*\n• **Wiskunde**: Alle niveaus (basisonderwijs t/m universiteit)\n• **Quantum informatie**: Geavanceerde wiskundige concepten\n• **Discrete wiskunde**: Combinatoriek, grafentheorie, algoritmen\n• **Statistiek & data-analyse**: Praktische toepassingen\n• **Programmeren**: Python, R, SQL, Java, C#\n• **Onderwijskunde**: Evidence-based didactiek\n• **Eerstegraads bevoegdheid**: Volledige lesbevoegdheid\n\n*Motivatie:*\n• Ik weet hoe het voelt om vast te lopen in wiskunde\n• Persoonlijke begeleiding maakte het verschil voor mij\n• Nu help ik anderen om hun potentieel te bereiken\n• **Academische achtergrond** gecombineerd met **praktische onderwijservaring**",
            "en": "👨‍🏫 *Personal Background*\n\n*Stephen Adei - MSc Mathematics*\n• **MSc Mathematics** (Specialized in quantum information and discrete mathematics)\n• **Master Teacher** (First-degree teaching qualification in one go)\n• 10+ years of teaching experience since 2012\n• Personal journey: From math challenges to excellent results\n• Multidisciplinary background: Math, programming, music, photography\n• Vision: Education should empower, not just transfer knowledge\n\n*Expertise:*\n• **Mathematics**: All levels (primary education to university)\n• **Quantum information**: Advanced mathematical concepts\n• **Discrete mathematics**: Combinatorics, graph theory, algorithms\n• **Statistics & data analysis**: Practical applications\n• **Programming**: Python, R, SQL, Java, C#\n• **Educational science**: Evidence-based didactics\n• **First-degree qualification**: Full teaching qualification\n\n*Motivation:*\n• I know how it feels to get stuck in math\n• Personal guidance made the difference for me\n• Now I help others reach their potential\n• **Academic background** combined with **practical teaching experience**"
        },
        "info_didactic_methods": {
            "nl": "📚 *Didactische Methoden*\n\n*Diagnostisch Werken:*\n• Start altijd met intake om niveau, leerstijl en doelen te bepalen\n• Analyse van voorkennis en eventuele belemmeringen\n• Persoonlijk leertraject op maat\n\n*Leerdoelgericht Onderwijs:*\n• Elke les heeft een concreet, meetbaar doel\n• Afgestemd op de individuele leerling\n• Regelmatige evaluatie van voortgang\n\n*Activerende Didactiek:*\n• Samen oefenen en uitleggen aan elkaar\n• Realistische voorbeelden uit de praktijk\n• Reflectie en zelfevaluatie\n• Interactieve werkvormen\n\n*Differentiatie & Scaffolding:*\n• Stapsgewijze opbouw van complexiteit\n• Aangepaste uitleg per leerling\n• Ondersteuning waar nodig, uitdaging waar mogelijk\n\n*Zelfregulatie Stimuleren:*\n• Leerlingen leren plannen en reflecteren\n• Eigen leerproces monitoren\n• Doelen stellen en evalueren\n\n*Feedbackcultuur:*\n• Directe, constructieve feedback\n• Digitale evaluatieformulieren na elke les\n• Continue verbetering van methoden",
            "en": "📚 *Didactic Methods*\n\n*Diagnostic Work:*\n• Always start with intake to determine level, learning style and goals\n• Analysis of prior knowledge and potential obstacles\n• Personalized learning trajectory\n\n*Goal-Oriented Education:*\n• Each lesson has a concrete, measurable objective\n• Tailored to the individual student\n• Regular evaluation of progress\n\n*Activating Didactics:*\n• Practice together and explain to each other\n• Realistic examples from practice\n• Reflection and self-evaluation\n• Interactive teaching methods\n\n*Differentiation & Scaffolding:*\n• Step-by-step build-up of complexity\n• Adapted explanation per student\n• Support where needed, challenge where possible\n\n*Stimulating Self-Regulation:*\n• Students learn to plan and reflect\n• Monitor their own learning process\n• Set goals and evaluate\n\n*Feedback Culture:*\n• Direct, constructive feedback\n• Digital evaluation forms after each lesson\n• Continuous improvement of methods"
        },
        "info_technology_tools": {
            "nl": "💻 *Technologie & Tools*\n\n*iPad-Aantekeningen:*\n• Digitale aantekeningen gedeeld na elke les\n• Overzichtelijke structuur en duidelijke uitleg\n• Altijd beschikbaar voor herhaling\n\n*AI-Tools:*\n• ChatGPT voor conceptverduidelijking\n• Gepersonaliseerde oefeningen en uitleg\n• Hulpmiddel bij huiswerk en voorbereiding\n\n*Apps & Platforms:*\n• GoodNotes voor digitale aantekeningen\n• Notion voor organisatie en planning\n• Google Classroom voor materiaal delen\n\n*Online Ondersteuning:*\n• Interactieve whiteboards voor afstandslessen\n• Scherm delen en video-opnames op verzoek\n• WhatsApp-ondersteuning: 7 dagen na elke les\n• Reactie binnen 24 uur op vragen\n\n*Digitale Materialen:*\n• Extra oefenmateriaal en video's\n• Online kennisbank voor veelgestelde vragen\n• Gepersonaliseerde leermiddelen",
            "en": "💻 *Technology & Tools*\n\n*iPad Notes:*\n• Digital notes shared after each lesson\n• Clear structure and explanation\n• Always available for review\n\n*AI Tools:*\n• ChatGPT for concept clarification\n• Personalized exercises and explanations\n• Help with homework and preparation\n\n*Apps & Platforms:*\n• GoodNotes for digital notes\n• Notion for organization and planning\n• Google Classroom for sharing materials\n\n*Online Support:*\n• Interactive whiteboards for distance lessons\n• Screen sharing and video recordings on request\n• WhatsApp support: 7 days after each lesson\n• Response within 24 hours to questions\n\n*Digital Materials:*\n• Extra practice materials and videos\n• Online knowledge base for frequently asked questions\n• Personalized learning materials"
        },
        "info_results_success": {
            "nl": "🏆 *Resultaten & Succes*\n\n*Kwantitatieve Resultaten:*\n• 500+ studenten geholpen sinds 2012\n• 98% studenttevredenheid\n• Gemiddelde beoordeling: 4.9/5\n• 95% slagingspercentage MBO-rekentoets\n• Aantoonbare cijferstijging bij de meeste leerlingen\n\n*Succesverhalen:*\n• Leerlingen die van onvoldoende naar voldoende gingen\n• Succesvolle CCVX-examens voor universitaire toelating\n• Verbeterd zelfvertrouwen en motivatie\n• Studenten die hun studie succesvol hebben afgerond\n\n*Kwalitatieve Impact:*\n• Meer zelfvertrouwen in wiskunde\n• Betere studievaardigheden en planning\n• Verhoogde motivatie en doorzettingsvermogen\n• Succesvolle doorstroom naar vervolgopleidingen\n\n*Testimonials:*\n• Positieve feedback van ouders en leerlingen\n• Aanbevelingen van tevreden klanten\n• Langdurige relaties met terugkerende studenten",
            "en": "🏆 *Results & Success*\n\n*Quantitative Results:*\n• 500+ students helped since 2012\n• 98% student satisfaction\n• Average rating: 4.9/5\n• 95% pass rate MBO math test\n• Demonstrable grade improvement for most students\n\n*Success Stories:*\n• Students who went from failing to passing\n• Successful CCVX exams for university admission\n• Improved confidence and motivation\n• Students who successfully completed their studies\n\n*Qualitative Impact:*\n• More confidence in mathematics\n• Better study skills and planning\n• Increased motivation and perseverance\n• Successful progression to further education\n\n*Testimonials:*\n• Positive feedback from parents and students\n• Recommendations from satisfied customers\n• Long-term relationships with returning students"
        },
        "info_workshops_creative": {
            "nl": "🎨 *Creatieve Workshops*\n\n*Fotografie & Visuele Communicatie:*\n• Basisprincipes van fotografie en compositie\n• Digitale bewerking en storytelling\n• Praktische opdrachten en feedback\n\n*Muziek & Creativiteit:*\n• Muziektheorie en praktische toepassing\n• Creatieve expressie en improvisatie\n• Samenwerking en performance\n\n*Interdisciplinaire Projecten:*\n• Combinatie van wiskunde en creativiteit\n• Projectmatig werken aan realistische opdrachten\n• Ontwikkeling van probleemoplossende vaardigheden\n\n*Doelgroep:*\n• Leerlingen die creatief willen leren\n• Groepen van 3-8 personen\n• Flexibele planning en locaties\n\n*Resultaten:*\n• Praktische vaardigheden en portfolio\n• Verhoogde creativiteit en zelfexpressie\n• Betere samenwerking en communicatie",
            "en": "🎨 *Creative Workshops*\n\n*Photography & Visual Communication:*\n• Basic principles of photography and composition\n• Digital editing and storytelling\n• Practical assignments and feedback\n\n*Music & Creativity:*\n• Music theory and practical application\n• Creative expression and improvisation\n• Collaboration and performance\n\n*Interdisciplinary Projects:*\n• Combination of mathematics and creativity\n• Project-based work on realistic assignments\n• Development of problem-solving skills\n\n*Target Group:*\n• Students who want to learn creatively\n• Groups of 3-8 people\n• Flexible scheduling and locations\n\n*Results:*\n• Practical skills and portfolio\n• Increased creativity and self-expression\n• Better collaboration and communication"
        },
        "info_workshops_academic": {
            "nl": "🎓 *Academische Workshops*\n\n*Wiskunde & Statistiek:*\n• Geavanceerde wiskundige concepten\n• Statistische analyse en interpretatie\n• Praktische toepassingen in onderzoek\n\n*Programmeren & Data Science:*\n• Python, R, SQL voor data-analyse\n• Machine learning en AI-basis\n• Projectmatig werken aan datasets\n\n*Onderzoeksmethoden:*\n• Wetenschappelijke methodologie\n• Dataverzameling en -analyse\n• Presentatie en rapportage\n\n*Doelgroep:*\n• Studenten in het hoger onderwijs\n• Onderzoekers en professionals\n• Groepen van 2-6 personen\n\n*Resultaten:*\n• Praktische vaardigheden en certificaten\n• Onderzoeksprojecten en publicaties\n• Carrière-ontwikkeling en netwerken",
            "en": "🎓 *Academic Workshops*\n\n*Mathematics & Statistics:*\n• Advanced mathematical concepts\n• Statistical analysis and interpretation\n• Practical applications in research\n\n*Programming & Data Science:*\n• Python, R, SQL for data analysis\n• Machine learning and AI basics\n• Project-based work on datasets\n\n*Research Methods:*\n• Scientific methodology\n• Data collection and analysis\n• Presentation and reporting\n\n*Target Group:*\n• Students in higher education\n• Researchers and professionals\n• Groups of 2-6 people\n\n*Results:*\n• Practical skills and certificates\n• Research projects and publications\n• Career development and networking"
        },
        "info_consultancy": {
            "nl": "💼 *Consultancy & Advies*\n\n*Onderwijsadvies:*\n• Analyse van leerprocessen en -methoden\n• Advies over didactische aanpak\n• Ontwikkeling van leermaterialen\n\n*Data-analyse & Statistiek:*\n• Statistische analyse van onderzoeksdata\n• Interpretatie en rapportage van resultaten\n• Ondersteuning bij wetenschappelijke publicaties\n\n*Technologie-implementatie:*\n• Advies over educatieve technologie\n• Implementatie van digitale tools\n• Training en ondersteuning\n\n*Doelgroep:*\n• Onderwijsinstellingen en docenten\n• Onderzoekers en studenten\n• Bedrijven en organisaties\n\n*Werkwijze:*\n• Intake en analyse van behoeften\n• Maatwerk oplossingen en advies\n• Implementatie en follow-up\n• Continue ondersteuning en evaluatie",
            "en": "💼 *Consultancy & Advice*\n\n*Educational Advice:*\n• Analysis of learning processes and methods\n• Advice on didactic approach\n• Development of learning materials\n\n*Data Analysis & Statistics:*\n• Statistical analysis of research data\n• Interpretation and reporting of results\n• Support for scientific publications\n\n*Technology Implementation:*\n• Advice on educational technology\n• Implementation of digital tools\n• Training and support\n\n*Target Group:*\n• Educational institutions and teachers\n• Researchers and students\n• Companies and organizations\n\n*Working Method:*\n• Intake and analysis of needs\n• Custom solutions and advice\n• Implementation and follow-up\n• Continuous support and evaluation"
        },
        "info_services": {
            "nl": "📚 *Mijn Diensten & Aanbod*\n\n🎓 *1. Privélessen & Bijles*\n*Vakken:*\n• *Basisonderwijs*: Rekenen, Taal\n• *Voortgezet Onderwijs*: Wiskunde A/B/C/D, Natuurkunde, Scheikunde, Engels\n• *Hoger Onderwijs*: Bedrijfsstatistiek, Calculus, Economie, Statistiek, Kansberekening, Lineaire Algebra, Verzamelingenleer\n• *Programmeren*: Python, Java, C#, C++, HTML, CSS, JavaScript, React, SQL, MATLAB, SPSS, R\n\n🎯 *2. MBO Rekenondersteuning (alleen online, 18+)*\n• *95% slagingspercentage* MBO-rekentoets\n• *500+ studenten* geholpen\n• *Gemiddelde beoordeling: 8.9/10*\n• Bewezen methoden en effectieve lesmaterialen\n• *Online trajecten* voor volwassen MBO-studenten\n\n*Rekentrajecten:*\n• **Spoedpakket**: 1 week, 4 uur (€275)\n• **Korte cursus**: 4 weken, 4 uur (€225)\n• **Volledig Commit**: 12 weken, 13-14 uur (€550)\n• **Volledig Flex**: 12 weken, 13-14 uur (€690 in 3 termijnen)\n\n📝 *3. Scriptiebegeleiding*\n• Methodologie en onderzoeksopzet\n• Statistische analyse (SPSS, R, Python)\n• Data-analyse en interpretatie\n• Structuur en planning\n• Eindredactie\n\n🎨 *4. Creatieve Workshops*\n• Muziekproductie & DJ (3 uur)\n• Analoge fotografie & bewerking (4 uur)\n• Visuele storytelling & design (3 uur)\n• Creatief coderen: Kunst & animatie (2 uur, 4 sessies)\n• AI & creativiteit (3 uur)\n• Escape room design (4 uur, 2 sessies)\n• Wiskundige kunst & patronen (3 uur)\n• Wiskundig verhalen vertellen (2.5 uur)\n• Wiskundige podcasting (3 uur, 2 sessies)\n• Educatieve wiskundevideo's (4 uur, 3 sessies)\n\n🎓 *5. Academische Workshops*\n• Statistiek project cursus (90 min, 6 sessies)\n• Wiskunde docenten innovatie (3 uur, 4 sessies)\n• AI & wiskunde (2 uur, 3 sessies)\n• Data visualisatie met Python (3 uur, 3 sessies)\n• Wiskundige spelontwikkeling (3 uur)\n• 3D wiskundig modelleren (3 uur, 4 sessies)\n• Innovatieve wiskundetoetsing (3 uur, 2 sessies)\n• Differentiatie in wiskundeonderwijs (3 uur, 3 sessies)\n• Mindfulness in wiskunde (2 uur)\n\n🧘 *6. Wellness Workshops*\n• Mindfulness (2 uur)\n• Tijdmanagement (2.5 uur)\n• Examenvoorbereiding (3 uur, 3 sessies)\n\n💼 *7. Consultancy & Advies*\n• Data-analyse en statistische modellering\n• Onderzoeksmethodologie\n• Machine learning en AI\n• Software ontwikkeling",
            "en": "📚 *My Services & Offerings*\n\n🎓 *1. Private Lessons & Tutoring*\n*Subjects:*\n• *Primary Education*: Math, Language\n• *Secondary Education*: Math A/B/C/D, Physics, Chemistry, English\n• *Higher Education*: Business Statistics, Calculus, Economics, Statistics, Probability, Linear Algebra, Set Theory\n• *Programming*: Python, Java, C#, C++, HTML, CSS, JavaScript, React, SQL, MATLAB, SPSS, R\n\n🎯 *2. MBO Math Support (online only, 18+)*\n• *95% pass rate* MBO math test\n• *500+ students* helped\n• *Average rating: 8.9/10*\n• Proven methods and effective teaching materials\n• *Online trajectories* for adult MBO students\n\n*Math trajectories:*\n• **Emergency**: 1 week, 4 hours (€275)\n• **Short course**: 4 weeks, 4 hours (€225)\n• **Full Commit**: 12 weeks, 13-14 hours (€550)\n• **Full Flex**: 12 weeks, 13-14 hours (€690 in 3 installments)\n\n📝 *3. Thesis Guidance*\n• Methodology and research design\n• Statistical analysis (SPSS, R, Python)\n• Data analysis and interpretation\n• Structure and planning\n• Final editing\n\n🎨 *4. Creative Workshops*\n• Music production & DJ (3 hours)\n• Analog photography & editing (4 hours)\n• Visual storytelling & design (3 hours)\n• Creative coding: Art & animation (2 hours, 4 sessions)\n• AI & creativity (3 hours)\n• Escape room design (4 hours, 2 sessions)\n• Mathematical art & patterns (3 hours)\n• Mathematical storytelling (2.5 hours)\n• Mathematical podcasting (3 hours, 2 sessions)\n• Educational math videos (4 hours, 3 sessions)\n\n🎓 *5. Academic Workshops*\n• Statistics project course (90 min, 6 sessions)\n• Math teacher innovation (3 hours, 4 sessions)\n• AI & mathematics (2 hours, 3 sessions)\n• Data visualization with Python (3 hours, 3 sessions)\n• Mathematical game development (3 hours)\n• 3D mathematical modeling (3 hours, 4 sessions)\n• Innovative math testing (3 hours, 2 sessions)\n• Differentiation in math education (3 hours, 3 sessions)\n• Mindfulness in mathematics (2 hours)\n\n🧘 *6. Wellness Workshops*\n• Mindfulness (2 hours)\n• Time management (2.5 hours)\n• Exam preparation (3 hours, 3 sessions)\n\n💼 *7. Consultancy & Advice*\n• Data analysis and statistical modeling\n• Research methodology\n• Machine learning and AI\n• Software development"
        },
        "info_weekend_programs": {
            "nl": "🌅 **Weekend Programma's (Amsterdam Zuidoost)**\n\n🇬🇭 **Boa me na menboa mo (Ghanese gemeenschap):**\n• **50% korting** voor Ghanese jongeren: €30/uur i.p.v. €60\n• **Locatie**: Douwe Egberts (Dubbelink 2) of aan huis in Gein\n• **Tijden**: Zaterdag en zondag, flexibele tijden\n• **Gratis proefles** van 30 minuten\n\n🌅 **Weekend Bijles Zuidoost:**\n• **50% korting**: €30/uur i.p.v. €60\n• **Zelfde locaties** en tijden\n• **Voor alle bewoners** van Zuidoost\n\n📍 **Locaties:**\n• Douwe Egberts (Dubbelink 2, Amsterdam Zuidoost)\n• Aan huis in Gein en omgeving\n• Bijlmerplein 888, 1102 MG Amsterdam\n\n⏰ **Beschikbaarheid:**\n• Zaterdag: 10:00–18:00\n• Zondag: 10:00–18:00\n• Flexibele tijden mogelijk\n\n🎯 **Speciale Kenmerken:**\n• **Community focus**: Toegankelijke tarieven voor verschillende doelgroepen\n• **Ervaring met speciale behoeften**: Ervaring met leerlingen met lichte autisme\n• **Gestructureerde en geduldige leeromgeving**\n• **Aanpassing aan specifieke behoeften**\n\n📞 **Contact:**\n• Telefoon: +31 6 47357426\n• Email: info@stephenadei.nl\n• Website: stephensprivelessen.nl",
            "en": "🌅 **Weekend Programs (Amsterdam Southeast)**\n\n🇬🇭 **Boa me na menboa mo (Ghanaian community):**\n• **50% discount** for Ghanaian youth: €30/hour instead of €60\n• **Location**: Douwe Egberts (Dubbelink 2) or at home in Gein\n• **Times**: Saturday and Sunday, flexible times\n• **Free trial lesson** of 30 minutes\n\n🌅 **Weekend Tutoring Southeast:**\n• **50% discount**: €30/hour instead of €60\n• **Same locations** and times\n• **For all residents** of Southeast\n\n📍 **Locations:**\n• Douwe Egberts (Dubbelink 2, Amsterdam Southeast)\n• At home in Gein and surrounding area\n• Bijlmerplein 888, 1102 MG Amsterdam\n\n⏰ **Availability:**\n• Saturday: 10:00–18:00\n• Sunday: 10:00–18:00\n• Flexible times possible\n\n🎯 **Special Features:**\n• **Community focus**: Accessible rates for different target groups\n• **Experience with special needs**: Experience with students with mild autism\n• **Structured and patient learning environment**\n• **Adaptation to specific needs**\n\n📞 **Contact:**\n• Phone: +31 6 47357426\n• Email: info@stephenadei.nl\n• Website: stephensprivelessen.nl"
        },
        "info_short_version": {
            "nl": "📝 **Korte versie:**\n\nHO: 1× €90 • 2× €140 • 4× €250\nVO 20+: 1× €80 • 2× €135 • 4× €230\nVO 20-: 1× €75 • 2× €130 • 4× €200\n\nReiskosten: VU/UvA (niet SP) €15 • Thuis (AMS e.o.) €40 • Science Park €0\n\nLast-minute: <24u +20% • <12u +50%\n\nPakketten: 2× geldig 2 weken • 4× geldig 1 maand; bij directe planning loopt geldigheid vanaf 1e les. Flex-premium (alleen bij niet-direct plannen): +€15 (2×) / +€30 (4×).",
            "en": "📝 **Short version:**\n\nHE: 1× €90 • 2× €140 • 4× €250\nSE 20+: 1× €80 • 2× €135 • 4× €230\nSE 20-: 1× €75 • 2× €130 • 4× €200\n\nTravel: VU/UvA (not SP) €15 • Home (AMS area) €40 • Science Park €0\n\nLast-minute: <24h +20% • <12h +50%\n\nPackages: 2× valid 2 weeks • 4× valid 1 month; with direct scheduling validity runs from 1st lesson. Flex-premium (only when not scheduling directly): +€15 (2×) / +€30 (4×)."
        },
        "info_personal_background": {
            "nl": "👨‍🏫 **Persoonlijke Achtergrond & Motivatie**\n\n**Stephen Adei** - MSc Mathematics (Gespecialiseerd in quantum informatie en discrete wiskunde)\n• **Master Leraar** (Eerstegraads bevoegdheid in één keer)\n• **10+ jaar ervaring** sinds 2012 in onderwijs en begeleiding\n• **Persoonlijke reis**: Van wiskunde-uitdagingen (gemiddelde 5 in 3e jaar) naar excellente resultaten (gemiddelde 10 in 4e/5e jaar)\n• **Expertise**: Wiskunde, quantum informatie, discrete wiskunde, statistiek, data-analyse, multidisciplinaire achtergrond\n• **Passie**: Deze ervaring inspireerde tot het helpen van anderen met vergelijkbare uitdagingen\n\n**Visie & Filosofie:**\n• **Onderwijs moet empoweren**, niet alleen kennis overdragen\n• **Elke student kan leren**, mits de juiste begeleiding en motivatie\n• **Persoonlijke groei** staat centraal in mijn aanpak\n• **Zelfvertrouwen** is de basis voor succesvol leren\n\n**Academische Kwalificaties:**\n• **MSc Mathematics**: Gespecialiseerd in quantum informatie en discrete wiskunde\n• **Master Leraar**: Eerstegraads bevoegdheid (volledige lesbevoegdheid)\n• **Evidence-based didactiek**: Wetenschappelijk onderbouwde onderwijsmethoden\n• **Academische achtergrond** gecombineerd met **praktische onderwijservaring**\n\n**Multidisciplinaire Achtergrond:**\n• **Wiskunde & Statistiek**: Academische achtergrond en praktische toepassingen\n• **Quantum informatie**: Geavanceerde wiskundige concepten en algoritmen\n• **Discrete wiskunde**: Combinatoriek, grafentheorie, algoritmen\n• **Programmeren**: Python, Java, C#, C++, web development\n• **Muziek & Creativiteit**: Muziekproductie, DJ, creatieve workshops\n• **Fotografie & Design**: Analoge fotografie, visuele storytelling\n• **AI & Innovatie**: Integratie van moderne technologie in onderwijs\n\n**Community Focus:**\n• **Ghanese gemeenschap**: Speciale programma's en ondersteuning\n• **Amsterdam Zuidoost**: Weekend programma's met toegankelijke tarieven\n• **Inclusiviteit**: Ervaring met diverse leerstijlen en speciale behoeften",
            "en": "👨‍🏫 **Personal Background & Motivation**\n\n**Stephen Adei** - MSc Mathematics (Specialized in quantum information and discrete mathematics)\n• **Master Teacher** (First-degree teaching qualification in one go)\n• **10+ years of experience** since 2012 in education and guidance\n• **Personal journey**: From math challenges (average 5 in 3rd year) to excellent results (average 10 in 4th/5th year)\n• **Expertise**: Mathematics, quantum information, discrete mathematics, statistics, data analysis, multidisciplinary background\n• **Passion**: This experience inspired helping others with similar challenges\n\n**Vision & Philosophy:**\n• **Education should empower**, not just transfer knowledge\n• **Every student can learn**, given the right guidance and motivation\n• **Personal growth** is central to my approach\n• **Self-confidence** is the foundation for successful learning\n\n**Academic Qualifications:**\n• **MSc Mathematics**: Specialized in quantum information and discrete mathematics\n• **Master Teacher**: First-degree teaching qualification (full teaching qualification)\n• **Evidence-based didactics**: Scientifically supported teaching methods\n• **Academic background** combined with **practical teaching experience**\n\n**Multidisciplinary Background:**\n• **Mathematics & Statistics**: Academic background and practical applications\n• **Quantum information**: Advanced mathematical concepts and algorithms\n• **Discrete mathematics**: Combinatorics, graph theory, algorithms\n• **Programming**: Python, Java, C#, C++, web development\n• **Music & Creativity**: Music production, DJ, creative workshops\n• **Photography & Design**: Analog photography, visual storytelling\n• **AI & Innovation**: Integration of modern technology in education\n\n**Community Focus:**\n• **Ghanaian community**: Special programs and support\n• **Amsterdam Southeast**: Weekend programs with accessible rates\n• **Inclusivity**: Experience with diverse learning styles and special needs"
        },
        "info_didactic_methods": {
            "nl": "📚 **Didactische Aanpak & Methodiek**\n\n**Diagnostisch Werken:**\n• **Intake gesprek**: Start altijd met een uitgebreide intake om niveau, leerstijl en doelen te bepalen\n• **Leerdoelanalyse**: Identificeer specifieke uitdagingen en sterke punten\n• **Voorkennis assessment**: Bepaal het startniveau en voorkennis\n• **Leerstijl bepaling**: Visueel, auditief, kinesthetisch of combinatie\n\n**Leerdoelgericht Onderwijs:**\n• **SMART doelen**: Specifieke, meetbare, haalbare, relevante en tijdsgebonden doelen\n• **Stapsgewijze opbouw**: Complexe stof opdelen in behapbare stappen\n• **Voortgangsmonitoring**: Regelmatige evaluatie van leerdoelen\n• **Aanpassing**: Flexibele aanpassing van doelen op basis van voortgang\n\n**Activerende Didactiek:**\n• **Samen oefenen**: Interactieve oefeningen en samenwerking\n• **Uitleggen aan elkaar**: Peer teaching en kennis delen\n• **Real-life voorbeelden**: Praktische toepassingen en context\n• **Reflectie**: Regelmatige reflectie op leerproces en resultaten\n• **Probleemgestuurd leren**: Uitdagende problemen als startpunt\n\n**Formatieve Evaluatie:**\n• **Korte toetsmomenten**: Regelmatige korte assessments\n• **Directe feedback**: Onmiddellijke feedback tijdens lessen\n• **Zelfevaluatie**: Stimuleren van zelfreflectie bij leerlingen\n• **Ouderbetrokkenheid**: Regelmatige updates en feedback\n\n**Zelfregulatie & Metacognitie:**\n• **Planningsvaardigheden**: Leren plannen en organiseren\n• **Zelfmonitoring**: Eigen voortgang bijhouden en evalueren\n• **Strategieontwikkeling**: Ontwikkelen van eigen leerstrategieën\n• **Motivatiebehoud**: Technieken voor het behouden van motivatie\n\n**Differentiatie & Inclusiviteit:**\n• **Scaffolding**: Ondersteuning die geleidelijk wordt afgebouwd\n• **Tempo-aanpassing**: Verschillende snelheden per leerling\n• **Materiaal-aanpassing**: Verschillende werkvormen en materialen\n• **Ervaring met speciale behoeften**: Autisme, dyscalculie, ADHD, NT2\n• **Visuele, auditieve en kinesthetische leermiddelen**",
            "en": "📚 **Didactic Approach & Methodology**\n\n**Diagnostic Work:**\n• **Intake conversation**: Always start with comprehensive intake to determine level, learning style and goals\n• **Learning goal analysis**: Identify specific challenges and strengths\n• **Prior knowledge assessment**: Determine starting level and prior knowledge\n• **Learning style determination**: Visual, auditory, kinesthetic or combination\n\n**Goal-Oriented Education:**\n• **SMART goals**: Specific, measurable, achievable, relevant and time-bound goals\n• **Step-by-step building**: Breaking complex material into manageable steps\n• **Progress monitoring**: Regular evaluation of learning goals\n• **Adaptation**: Flexible adjustment of goals based on progress\n\n**Activating Didactics:**\n• **Practice together**: Interactive exercises and collaboration\n• **Explain to each other**: Peer teaching and knowledge sharing\n• **Real-life examples**: Practical applications and context\n• **Reflection**: Regular reflection on learning process and results\n• **Problem-based learning**: Challenging problems as starting point\n\n**Formative Evaluation:**\n• **Short test moments**: Regular short assessments\n• **Direct feedback**: Immediate feedback during lessons\n• **Self-evaluation**: Encouraging self-reflection in students\n• **Parent involvement**: Regular updates and feedback\n\n**Self-Regulation & Metacognition:**\n• **Planning skills**: Learning to plan and organize\n• **Self-monitoring**: Tracking and evaluating own progress\n• **Strategy development**: Developing own learning strategies\n• **Motivation maintenance**: Techniques for maintaining motivation\n\n**Differentiation & Inclusivity:**\n• **Scaffolding**: Support that is gradually reduced\n• **Pace adjustment**: Different speeds per student\n• **Material adaptation**: Different work forms and materials\n• **Experience with special needs**: Autism, dyscalculia, ADHD, NT2\n• **Visual, auditory and kinesthetic learning materials**"
        },
        "info_technology_tools": {
            "nl": "💻 **Technologie & Tools**\n\n**Digitale Aantekeningen & Organisatie:**\n• **iPad met Apple Pencil**: Digitale aantekeningen tijdens lessen\n• **GoodNotes**: Professionele notitie-app met OCR en organisatie\n• **Notion**: Kennisbank en organisatie van lesmaterialen\n• **Google Classroom**: Delen van materialen en opdrachten\n• **Digitale aantekeningen**: Na elke les gedeeld met leerlingen\n\n**AI & Innovatie:**\n• **ChatGPT**: Conceptverduidelijking en gepersonaliseerde uitleg\n• **AI-tools**: Voor oefenmateriaal en adaptieve leerpaden\n• **Gepersonaliseerde oefening**: AI-gestuurde aanbevelingen\n• **Huiswerk ondersteuning**: AI als hulpmiddel bij vragen\n\n**Online Lesgeven:**\n• **Zoom/Google Meet**: Professionele videoconferentie\n• **Online whiteboards**: Interactieve uitleg en samenwerking\n• **Scherm delen**: Demonstraties en presentaties\n• **Video-opnames**: Van uitleg op verzoek beschikbaar\n• **Chat functionaliteit**: Real-time vragen en antwoorden\n\n**Communicatie & Ondersteuning:**\n• **WhatsApp**: 7 dagen ondersteuning na elke les\n• **Reactietijd**: Binnen 24 uur op alle vragen\n• **Check-ins**: Korte motivatie- en planningsgesprekken\n• **FAQ systeem**: Kennisbank voor veelgestelde vragen\n• **Ouder communicatie**: Regelmatige updates en feedback\n\n**Praktische Tools:**\n• **Online boekingssysteem**: Eenvoudige planning en reminders\n• **Betaling integratie**: Veilige online betalingen\n• **Voortgangsmonitoring**: Digitale tracking van resultaten\n• **Evaluatieformulieren**: Anonieme feedback verzameling\n• **Kalender integratie**: Automatische herinneringen\n\n**Materiaal & Bronnen:**\n• **Digitale bibliotheek**: Uitgebreide collectie oefenmateriaal\n• **Video tutorials**: Stap-voor-stap uitleg van concepten\n• **Interactieve oefeningen**: Online quizzes en assessments\n• **E-books**: Digitale lesmaterialen en handleidingen\n• **Podcasts**: Audio content voor verschillende leerstijlen",
            "en": "💻 **Technology & Tools**\n\n**Digital Notes & Organization:**\n• **iPad with Apple Pencil**: Digital notes during lessons\n• **GoodNotes**: Professional note app with OCR and organization\n• **Notion**: Knowledge base and organization of teaching materials\n• **Google Classroom**: Sharing materials and assignments\n• **Digital notes**: Shared with students after each lesson\n\n**AI & Innovation:**\n• **ChatGPT**: Concept clarification and personalized explanation\n• **AI tools**: For practice materials and adaptive learning paths\n• **Personalized practice**: AI-driven recommendations\n• **Homework support**: AI as aid for questions\n\n**Online Teaching:**\n• **Zoom/Google Meet**: Professional video conferencing\n• **Online whiteboards**: Interactive explanation and collaboration\n• **Screen sharing**: Demonstrations and presentations\n• **Video recordings**: Available on request\n• **Chat functionality**: Real-time questions and answers\n\n**Communication & Support:**\n• **WhatsApp**: 7 days support after each lesson\n• **Response time**: Within 24 hours on all questions\n• **Check-ins**: Short motivation and planning conversations\n• **FAQ system**: Knowledge base for frequently asked questions\n• **Parent communication**: Regular updates and feedback\n\n**Practical Tools:**\n• **Online booking system**: Easy planning and reminders\n• **Payment integration**: Secure online payments\n• **Progress monitoring**: Digital tracking of results\n• **Evaluation forms**: Anonymous feedback collection\n• **Calendar integration**: Automatic reminders\n\n**Materials & Resources:**\n• **Digital library**: Extensive collection of practice materials\n• **Video tutorials**: Step-by-step explanation of concepts\n• **Interactive exercises**: Online quizzes and assessments\n• **E-books**: Digital teaching materials and manuals\n• **Podcasts**: Audio content for different learning styles"
        },
        "info_results_success": {
            "nl": "🏆 **Resultaten & Succesverhalen**\n\n**Kwantitatieve Resultaten:**\n• **500+ studenten** geholpen sinds 2012\n• **98% studenttevredenheid** op evaluaties\n• **Gemiddelde beoordeling: 4.9/5** sterren\n• **95% slagingspercentage** MBO-rekentoets\n• **Gemiddelde cijferstijging**: Aantoonbare verbetering in resultaten\n• **Succesvolle CCVX-examens**: Hoge slagingspercentages\n\n**Kwalitatieve Impact:**\n• **Zelfvertrouwen**: Significante toename in zelfvertrouwen bij leerlingen\n• **Motivatie**: Verbeterde motivatie en betrokkenheid\n• **Zelfstandigheid**: Ontwikkeling van zelfstandige leerstrategieën\n• **Doorzettingsvermogen**: Betere coping met uitdagingen\n• **Toekomstperspectief**: Duidelijkere visie op studie- en carrièrekeuzes\n\n**Specifieke Succesverhalen:**\n• **MBO-studenten**: Van onvoldoende naar voldoende op rekentoets\n• **Havo/Vwo leerlingen**: Van 4-5 naar 7-8 gemiddeld\n• **Hoger onderwijs**: Succesvolle afronding van moeilijke vakken\n• **CCVX-examens**: Hoge slagingspercentages voor universitaire toelating\n• **Scriptiebegeleiding**: Succesvolle afronding van onderzoeken\n\n**Community Impact:**\n• **Ghanese gemeenschap**: Toegankelijk onderwijs voor jongeren\n• **Amsterdam Zuidoost**: Betaalbare kwaliteitsonderwijs\n• **Speciale behoeften**: Inclusief onderwijs voor diverse leerlingen\n• **Ouderbetrokkenheid**: Positieve feedback van ouders\n\n**Langetermijn Resultaten:**\n• **Studievoortgang**: Verbeterde studieprestaties op langere termijn\n• **Carrière ontwikkeling**: Betere voorbereiding op vervolgstudies\n• **Leerhouding**: Duurzame verandering in leerattitude\n• **Netwerk**: Opbouw van ondersteunende netwerken\n\n**Testimonials & Ervaringen:**\n• **Leerling testimonials**: Persoonlijke verhalen van vooruitgang\n• **Ouder feedback**: Positieve ervaringen van ouders\n• **School feedback**: Samenwerking met scholen en docenten\n• **Peer reviews**: Erkenning van collega's in het onderwijsveld",
            "en": "🏆 **Results & Success Stories**\n\n**Quantitative Results:**\n• **500+ students** helped since 2012\n• **98% student satisfaction** on evaluations\n• **Average rating: 4.9/5** stars\n• **95% pass rate** MBO math test\n• **Average grade improvement**: Demonstrable improvement in results\n• **Successful CCVX exams**: High pass rates\n\n**Qualitative Impact:**\n• **Self-confidence**: Significant increase in student confidence\n• **Motivation**: Improved motivation and engagement\n• **Independence**: Development of independent learning strategies\n• **Perseverance**: Better coping with challenges\n• **Future perspective**: Clearer vision of study and career choices\n\n**Specific Success Stories:**\n• **MBO students**: From insufficient to sufficient on math test\n• **Havo/Vwo students**: From 4-5 to 7-8 average\n• **Higher education**: Successful completion of difficult subjects\n• **CCVX exams**: High pass rates for university admission\n• **Thesis guidance**: Successful completion of research\n\n**Community Impact:**\n• **Ghanaian community**: Accessible education for youth\n• **Amsterdam Southeast**: Affordable quality education\n• **Special needs**: Inclusive education for diverse students\n• **Parent involvement**: Positive feedback from parents\n\n**Long-term Results:**\n• **Study progress**: Improved academic performance in the long term\n• **Career development**: Better preparation for further studies\n• **Learning attitude**: Sustainable change in learning attitude\n• **Network**: Building supportive networks\n\n**Testimonials & Experiences:**\n• **Student testimonials**: Personal stories of progress\n• **Parent feedback**: Positive experiences from parents\n• **School feedback**: Collaboration with schools and teachers\n• **Peer reviews**: Recognition from colleagues in education"
        },
        "info_workshops_creative": {
            "nl": "🎨 **Creatieve Workshops & Cursussen**\n\n**Muziek & Audio:**\n• **Muziekproductie & DJ** (3 uur)\n  - Basis van muziekproductie en DJ-technieken\n  - Praktische ervaring met apparatuur\n  - Creatieve expressie door muziek\n\n• **Wiskundige podcasting** (3 uur, 2 sessies)\n  - Combineren van wiskunde en storytelling\n  - Audio editing en productie\n  - Educatieve content creatie\n\n**Fotografie & Visuele Kunsten:**\n• **Analoge fotografie & bewerking** (4 uur)\n  - Traditionele fotografie technieken\n  - Darkroom processen en bewerking\n  - Artistieke visuele expressie\n\n• **Visuele storytelling & design** (3 uur)\n  - Verhalen vertellen door beeld\n  - Design principes en creativiteit\n  - Digitale en analoge technieken\n\n**Creatief Coderen & Technologie:**\n• **Creatief coderen: Kunst & animatie** (2 uur, 4 sessies)\n  - Programmeren voor artistieke doeleinden\n  - Animaties en visuele effecten\n  - Interactieve kunstinstallaties\n\n• **AI & creativiteit** (3 uur)\n  - Kunstmatige intelligentie in creatieve processen\n  - AI-tools voor kunst en design\n  - Toekomst van creatieve technologie\n\n**Wiskundige Kunst & Patronen:**\n• **Wiskundige kunst & patronen** (3 uur)\n  - Wiskunde als basis voor kunst\n  - Geometrische patronen en fractals\n  - Wiskundige schoonheid in kunst\n\n• **Wiskundig verhalen vertellen** (2.5 uur)\n  - Verhalen met wiskundige concepten\n  - Educatieve storytelling\n  - Wiskunde toegankelijk maken\n\n**Interactieve & Gamification:**\n• **Escape room design** (4 uur, 2 sessies)\n  - Puzzel design en logica\n  - Interactieve ervaringen\n  - Teamwork en probleemoplossing\n\n• **Educatieve wiskundevideo's** (4 uur, 3 sessies)\n  - Video productie voor onderwijs\n  - Visuele uitleg van concepten\n  - Digitale content creatie\n\n**Workshop Kenmerken:**\n• **Kleine groepen**: Persoonlijke aandacht en begeleiding\n• **Praktisch gericht**: Hands-on ervaring en experimenteren\n• **Interdisciplinair**: Combineren van verschillende vakgebieden\n• **Creatieve vrijheid**: Ruimte voor eigen interpretatie en expressie\n• **Technologie integratie**: Moderne tools en technieken\n• **Community focus**: Samenwerking en kennis delen",
            "en": "🎨 **Creative Workshops & Courses**\n\n**Music & Audio:**\n• **Music production & DJ** (3 hours)\n  - Basics of music production and DJ techniques\n  - Practical experience with equipment\n  - Creative expression through music\n\n• **Mathematical podcasting** (3 hours, 2 sessions)\n  - Combining mathematics and storytelling\n  - Audio editing and production\n  - Educational content creation\n\n**Photography & Visual Arts:**\n• **Analog photography & editing** (4 hours)\n  - Traditional photography techniques\n  - Darkroom processes and editing\n  - Artistic visual expression\n\n• **Visual storytelling & design** (3 hours)\n  - Storytelling through images\n  - Design principles and creativity\n  - Digital and analog techniques\n\n**Creative Coding & Technology:**\n• **Creative coding: Art & animation** (2 hours, 4 sessions)\n  - Programming for artistic purposes\n  - Animations and visual effects\n  - Interactive art installations\n\n• **AI & creativity** (3 hours)\n  - Artificial intelligence in creative processes\n  - AI tools for art and design\n  - Future of creative technology\n\n**Mathematical Art & Patterns:**\n• **Mathematical art & patterns** (3 hours)\n  - Mathematics as basis for art\n  - Geometric patterns and fractals\n  - Mathematical beauty in art\n\n• **Mathematical storytelling** (2.5 hours)\n  - Stories with mathematical concepts\n  - Educational storytelling\n  - Making mathematics accessible\n\n**Interactive & Gamification:**\n• **Escape room design** (4 hours, 2 sessions)\n  - Puzzle design and logic\n  - Interactive experiences\n  - Teamwork and problem solving\n\n• **Educational math videos** (4 hours, 3 sessions)\n  - Video production for education\n  - Visual explanation of concepts\n  - Digital content creation\n\n**Workshop Features:**\n• **Small groups**: Personal attention and guidance\n• **Practical focus**: Hands-on experience and experimentation\n• **Interdisciplinary**: Combining different fields\n• **Creative freedom**: Space for own interpretation and expression\n• **Technology integration**: Modern tools and techniques\n• **Community focus**: Collaboration and knowledge sharing"
        },
        "info_workshops_academic": {
            "nl": "🎓 **Academische Workshops & Cursussen**\n\n**Statistiek & Data Analyse:**\n• **Statistiek project cursus** (90 min, 6 sessies)\n  - Praktische statistische analyses\n  - Project-gebaseerd leren\n  - Real-world data toepassingen\n\n• **Data visualisatie met Python** (3 uur, 3 sessies)\n  - Python voor data analyse\n  - Visuele presentatie van data\n  - Interactieve grafieken en dashboards\n\n**Wiskunde & Onderwijs:**\n• **Wiskunde docenten innovatie** (3 uur, 4 sessies)\n  - Nieuwe didactische methoden\n  - Technologie in wiskundeonderwijs\n  - Differentiatie en inclusiviteit\n\n• **AI & wiskunde** (2 uur, 3 sessies)\n  - Kunstmatige intelligentie in wiskunde\n  - AI-tools voor wiskundeonderwijs\n  - Toekomst van wiskundeonderwijs\n\n• **Wiskundige spelontwikkeling** (3 uur)\n  - Games voor wiskundeonderwijs\n  - Gamification van leren\n  - Interactieve wiskunde\n\n**3D & Modellering:**\n• **3D wiskundig modelleren** (3 uur, 4 sessies)\n  - 3D visualisatie van wiskundige concepten\n  - Moderne modelleringstechnieken\n  - Praktische toepassingen\n\n**Onderwijs Innovatie:**\n• **Innovatieve wiskundetoetsing** (3 uur, 2 sessies)\n  - Moderne toetsmethoden\n  - Formatief toetsen\n  - Technologie in toetsing\n\n• **Differentiatie in wiskundeonderwijs** (3 uur, 3 sessies)\n  - Individuele aanpak in groepen\n  - Scaffolding technieken\n  - Inclusief onderwijs\n\n• **Mindfulness in wiskunde** (2 uur)\n  - Stress reductie bij wiskunde\n  - Focus en concentratie\n  - Positieve leerhouding\n\n**Wellness & Studievaardigheden:**\n• **Mindfulness** (2 uur)\n  - Meditatie en bewustzijn\n  - Stress management\n  - Emotionele balans\n\n• **Tijdmanagement** (2.5 uur)\n  - Studieplanning en organisatie\n  - Prioriteiten stellen\n  - Effectief leren\n\n• **Examenvoorbereiding** (3 uur, 3 sessies)\n  - Strategieën voor examens\n  - Angst en stress management\n  - Optimale voorbereiding\n\n**Workshop Kenmerken:**\n• **Evidence-based**: Gebaseerd op wetenschappelijk onderzoek\n• **Praktisch toepasbaar**: Direct bruikbaar in onderwijs\n• **Interactief**: Actieve deelname en discussie\n• **Flexibel**: Aanpasbaar aan verschillende niveaus\n• **Ondersteunend materiaal**: Handouts, digitale bronnen, oefeningen\n• **Follow-up**: Vervolg ondersteuning en coaching\n\n**Doelgroepen:**\n• **Docenten**: Professionalisering en innovatie\n• **Studenten**: Studievaardigheden en zelfvertrouwen\n• **Ouders**: Ondersteuning bij begeleiding\n• **Professionals**: Werkgerelateerde vaardigheden",
            "en": "🎓 **Academic Workshops & Courses**\n\n**Statistics & Data Analysis:**\n• **Statistics project course** (90 min, 6 sessions)\n  - Practical statistical analyses\n  - Project-based learning\n  - Real-world data applications\n\n• **Data visualization with Python** (3 hours, 3 sessions)\n  - Python for data analysis\n  - Visual presentation of data\n  - Interactive graphs and dashboards\n\n**Mathematics & Education:**\n• **Math teacher innovation** (3 hours, 4 sessions)\n  - New didactic methods\n  - Technology in mathematics education\n  - Differentiation and inclusivity\n\n• **AI & mathematics** (2 hours, 3 sessions)\n  - Artificial intelligence in mathematics\n  - AI tools for mathematics education\n  - Future of mathematics education\n\n• **Mathematical game development** (3 hours)\n  - Games for mathematics education\n  - Gamification of learning\n  - Interactive mathematics\n\n**3D & Modeling:**\n• **3D mathematical modeling** (3 hours, 4 sessions)\n  - 3D visualization of mathematical concepts\n  - Modern modeling techniques\n  - Practical applications\n\n**Educational Innovation:**\n• **Innovative mathematics testing** (3 hours, 2 sessions)\n  - Modern testing methods\n  - Formative assessment\n  - Technology in testing\n\n• **Differentiation in mathematics education** (3 hours, 3 sessions)\n  - Individual approach in groups\n  - Scaffolding techniques\n  - Inclusive education\n\n• **Mindfulness in mathematics** (2 hours)\n  - Stress reduction in mathematics\n  - Focus and concentration\n  - Positive learning attitude\n\n**Wellness & Study Skills:**\n• **Mindfulness** (2 hours)\n  - Meditation and awareness\n  - Stress management\n  - Emotional balance\n\n• **Time management** (2.5 hours)\n  - Study planning and organization\n  - Setting priorities\n  - Effective learning\n\n• **Exam preparation** (3 hours, 3 sessions)\n  - Strategies for exams\n  - Anxiety and stress management\n  - Optimal preparation\n\n**Workshop Features:**\n• **Evidence-based**: Based on scientific research\n• **Practically applicable**: Directly usable in education\n• **Interactive**: Active participation and discussion\n• **Flexible**: Adaptable to different levels\n• **Supporting materials**: Handouts, digital resources, exercises\n• **Follow-up**: Continued support and coaching\n\n**Target Groups:**\n• **Teachers**: Professionalization and innovation\n• **Students**: Study skills and self-confidence\n• **Parents**: Support in guidance\n• **Professionals**: Work-related skills"
        },
        "info_consultancy": {
            "nl": "💼 **Consultancy & Advies**\n\n**Data-analyse & Statistische Modellering:**\n• **Statistische analyses**: Uitgebreide data-analyse en interpretatie\n• **Predictive modeling**: Voorspellende modellen en trends\n• **Data visualisatie**: Interactieve dashboards en rapporten\n• **Kwaliteitscontrole**: Statistische kwaliteitsborging\n• **Onderzoeksdesign**: Experimentele opzet en methodologie\n\n**Onderzoeksmethodologie:**\n• **Onderzoeksopzet**: Design van wetenschappelijke studies\n• **Steekproefmethoden**: Representatieve dataverzameling\n• **Validatie**: Betrouwbaarheid en validiteit van onderzoek\n• **Ethiek**: Onderzoeksethiek en privacybescherming\n• **Rapportage**: Wetenschappelijke rapportage en presentatie\n\n**Machine Learning & AI:**\n• **Algoritme ontwikkeling**: Custom machine learning modellen\n• **Data preprocessing**: Data cleaning en feature engineering\n• **Model evaluatie**: Performance assessment en validatie\n• **AI implementatie**: Praktische toepassingen van AI\n• **Ethische AI**: Verantwoorde AI ontwikkeling\n\n**Software Ontwikkeling:**\n• **Web development**: Frontend en backend ontwikkeling\n• **Database design**: Data architectuur en optimalisatie\n• **API ontwikkeling**: Integratie en systeemkoppeling\n• **Testing & QA**: Kwaliteitsborging en debugging\n• **Deployment**: Implementatie en onderhoud\n\n**Consultancy Aanpak:**\n\n**1. Eerste Gesprek & Behoefteanalyse**\n• Intake gesprek om doelen en uitdagingen te begrijpen\n• Analyse van huidige situatie en wensen\n• Bepaling van scope en verwachtingen\n• Opstellen van projectplan en tijdlijn\n\n**2. Data-evaluatie & Assessment**\n• Analyse van beschikbare data en systemen\n• Identificatie van verbeterpunten en kansen\n• Assessment van technische infrastructuur\n• Benchmarking tegen best practices\n\n**3. Oplossing Ontwerp**\n• Ontwikkeling van maatwerk oplossingen\n• Technische specificaties en architectuur\n• Implementatie strategie en planning\n• Risico analyse en mitigatie\n\n**4. Implementatie & Begeleiding**\n• Stapsgewijze implementatie van oplossingen\n• Training en kennisoverdracht\n• Monitoring en evaluatie van resultaten\n• Continue ondersteuning en optimalisatie\n\n**5. Kennisoverdracht & Ondersteuning**\n• Documentatie en handleidingen\n• Training van medewerkers\n• Best practices en procedures\n• Langdurige ondersteuning en onderhoud\n\n**Sectoren & Toepassingen:**\n• **Onderwijs**: Onderwijstechnologie en data-analyse\n• **Healthcare**: Medische data-analyse en statistiek\n• **Finance**: Financiële modellering en risico-analyse\n• **Marketing**: Customer analytics en targeting\n• **Research**: Wetenschappelijk onderzoek en publicaties\n\n**Deliverables:**\n• **Rapporten**: Uitgebreide analyses en aanbevelingen\n• **Dashboards**: Interactieve data visualisaties\n• **Modellen**: Machine learning en statistische modellen\n• **Software**: Custom applicaties en tools\n• **Training**: Workshops en kennisoverdracht\n• **Ondersteuning**: Continue begeleiding en optimalisatie",
            "en": "💼 **Consultancy & Advice**\n\n**Data Analysis & Statistical Modeling:**\n• **Statistical analyses**: Comprehensive data analysis and interpretation\n• **Predictive modeling**: Predictive models and trends\n• **Data visualization**: Interactive dashboards and reports\n• **Quality control**: Statistical quality assurance\n• **Research design**: Experimental design and methodology\n\n**Research Methodology:**\n• **Research design**: Design of scientific studies\n• **Sampling methods**: Representative data collection\n• **Validation**: Reliability and validity of research\n• **Ethics**: Research ethics and privacy protection\n• **Reporting**: Scientific reporting and presentation\n\n**Machine Learning & AI:**\n• **Algorithm development**: Custom machine learning models\n• **Data preprocessing**: Data cleaning and feature engineering\n• **Model evaluation**: Performance assessment and validation\n• **AI implementation**: Practical applications of AI\n• **Ethical AI**: Responsible AI development\n\n**Software Development:**\n• **Web development**: Frontend and backend development\n• **Database design**: Data architecture and optimization\n• **API development**: Integration and system coupling\n• **Testing & QA**: Quality assurance and debugging\n• **Deployment**: Implementation and maintenance\n\n**Consultancy Approach:**\n\n**1. Initial Conversation & Needs Analysis**\n• Intake conversation to understand goals and challenges\n• Analysis of current situation and wishes\n• Determination of scope and expectations\n• Development of project plan and timeline\n\n**2. Data Evaluation & Assessment**\n• Analysis of available data and systems\n• Identification of improvement points and opportunities\n• Assessment of technical infrastructure\n• Benchmarking against best practices\n\n**3. Solution Design**\n• Development of custom solutions\n• Technical specifications and architecture\n• Implementation strategy and planning\n• Risk analysis and mitigation\n\n**4. Implementation & Guidance**\n• Step-by-step implementation of solutions\n• Training and knowledge transfer\n• Monitoring and evaluation of results\n• Continuous support and optimization\n\n**5. Knowledge Transfer & Support**\n• Documentation and manuals\n• Staff training\n• Best practices and procedures\n• Long-term support and maintenance\n\n**Sectors & Applications:**\n• **Education**: Educational technology and data analysis\n• **Healthcare**: Medical data analysis and statistics\n• **Finance**: Financial modeling and risk analysis\n• **Marketing**: Customer analytics and targeting\n• **Research**: Scientific research and publications\n\n**Deliverables:**\n• **Reports**: Comprehensive analyses and recommendations\n• **Dashboards**: Interactive data visualizations\n• **Models**: Machine learning and statistical models\n• **Software**: Custom applications and tools\n• **Training**: Workshops and knowledge transfer\n• **Support**: Continuous guidance and optimization"
        },
        "info_how_lessons_work": {
            "nl": "📚 **Hoe Lessen Werken**\n\n**🎯 Lesopzet & Structuur:**\n• **Intake gesprek**: Eerste les start altijd met een uitgebreide intake\n• **Diagnostische toets**: Bepaling van huidig niveau en leerdoelen\n• **Persoonlijk plan**: Op maat gemaakt leertraject op basis van intake\n• **Flexibele duur**: 60-90 minuten afhankelijk van behoefte\n\n**💻 Lesvormen & Locaties:**\n• **Online lessen**: Via Zoom/Google Meet met interactieve whiteboards\n• **Fysieke lessen**: Thuis, op school, of op locatie (Amsterdam)\n• **Hybride optie**: Combinatie van online en fysiek mogelijk\n• **Locaties**: Science Park (gratis), VU/UvA (€15), thuis (€40)\n• **MBO trajecten**: Alleen online beschikbaar\n\n**📱 Technologie & Tools:**\n• **iPad aantekeningen**: Digitale notities gedeeld na elke les\n• **Online whiteboards**: Interactieve uitleg en samenwerking\n• **AI ondersteuning**: ChatGPT voor conceptverduidelijking\n• **WhatsApp support**: 7 dagen na elke les beschikbaar\n\n**📋 Lesverloop:**\n• **Voorbereiding**: Student bereidt vragen/voorbereiding voor\n• **Uitleg**: Stapsgewijze uitleg van concepten\n• **Samen oefenen**: Interactieve oefeningen en samenwerking\n• **Feedback**: Directe feedback en tips\n• **Huiswerk**: Gepersonaliseerde opdrachten en oefeningen\n• **Evaluatie**: Korte evaluatie van voortgang en doelen\n\n**🎓 Specifieke Vakken:**\n• **Wiskunde**: Alle niveaus (basisonderwijs t/m universiteit)\n• **Programmeren**: Python, Java, C#, web development\n• **Statistiek**: SPSS, R, data-analyse, onderzoek\n• **Scriptiebegeleiding**: Methodologie, analyse, structuur\n• **MBO trajecten**: Alleen voor volwassenen (18+), online trajecten\n\n**⏰ Planning & Beschikbaarheid:**\n• **Flexibele tijden**: Maandag t/m zondag, 9:00-22:00\n• **Last-minute**: Mogelijk met toeslag (<24u +20%, <12u +50%)\n• **Pakketten**: 2 of 4 lessen met verschillende geldigheid\n• **Proefles**: Gratis 30 minuten intake en kennismaking\n\n**📞 Ondersteuning:**\n• **WhatsApp**: 7 dagen na elke les voor vragen\n• **Reactietijd**: Binnen 24 uur op alle vragen\n• **Check-ins**: Korte motivatie- en planningsgesprekken\n• **Ouder communicatie**: Regelmatige updates en feedback",
            "en": "📚 **How Lessons Work**\n\n**🎯 Lesson Structure & Setup:**\n• **Intake conversation**: First lesson always starts with comprehensive intake\n• **Diagnostic test**: Assessment of current level and learning goals\n• **Personal plan**: Custom learning trajectory based on intake\n• **Flexible duration**: 60-90 minutes depending on needs\n\n**💻 Lesson Formats & Locations:**\n• **Online lessons**: Via Zoom/Google Meet with interactive whiteboards\n• **In-person lessons**: At home, at school, or on location (Amsterdam)\n• **Hybrid option**: Combination of online and in-person possible\n• **Locations**: Science Park (free), VU/UvA (€15), home (€40)\n• **MBO trajectories**: Online only\n\n**📱 Technology & Tools:**\n• **iPad notes**: Digital notes shared after each lesson\n• **Online whiteboards**: Interactive explanation and collaboration\n• **AI support**: ChatGPT for concept clarification\n• **WhatsApp support**: Available 7 days after each lesson\n\n**📋 Lesson Flow:**\n• **Preparation**: Student prepares questions/preparation\n• **Explanation**: Step-by-step explanation of concepts\n• **Practice together**: Interactive exercises and collaboration\n• **Feedback**: Direct feedback and tips\n• **Homework**: Personalized assignments and exercises\n• **Evaluation**: Brief evaluation of progress and goals\n\n**🎓 Specific Subjects:**\n• **Mathematics**: All levels (primary education to university)\n• **Programming**: Python, Java, C#, web development\n• **Statistics**: SPSS, R, data analysis, research\n• **Thesis guidance**: Methodology, analysis, structure\n• **MBO trajectories**: Adults only (18+), online trajectories\n\n**⏰ Scheduling & Availability:**\n• **Flexible times**: Monday to Sunday, 9:00-22:00\n• **Last-minute**: Possible with surcharge (<24h +20%, <12h +50%)\n• **Packages**: 2 or 4 lessons with different validity\n• **Trial lesson**: Free 30 minutes intake and introduction\n\n**📞 Support:**\n• **WhatsApp**: 7 days after each lesson for questions\n• **Response time**: Within 24 hours on all questions\n• **Check-ins**: Short motivation and planning conversations\n• **Parent communication**: Regular updates and feedback"
        },
        "menu_tariffs": {
            "nl": "💰 Tarieven",
            "en": "💰 Rates"
        },
        "menu_work_method": {
            "nl": "🎯 Werkwijze",
            "en": "🎯 Work Method"
        },
        "menu_how_lessons_work": {
            "nl": "📚 Hoe lessen werken",
            "en": "📚 How lessons work"
        },
        "menu_services": {
            "nl": "📚 Diensten",
            "en": "📚 Services"
        },
        "menu_travel_costs": {
            "nl": "🚗 Reiskosten",
            "en": "🚗 Travel Costs"
        },
        "menu_last_minute": {
            "nl": "⏰ Last-minute",
            "en": "⏰ Last-minute"
        },
        "menu_conditions": {
            "nl": "📋 Voorwaarden",
            "en": "📋 Conditions"
        },
        "menu_weekend_programs": {
            "nl": "🌅 Weekend programma's",
            "en": "🌅 Weekend Programs"
        },
        "menu_short_version": {
            "nl": "📝 Korte versie",
            "en": "📝 Short version"
        },
        "menu_personal_background": {
            "nl": "👨‍🏫 Persoonlijke Achtergrond",
            "en": "👨‍🏫 Personal Background"
        },
        "menu_didactic_methods": {
            "nl": "📚 Didactische Methoden",
            "en": "📚 Didactic Methods"
        },
        "menu_technology_tools": {
            "nl": "💻 Technologie & Tools",
            "en": "💻 Technology & Tools"
        },
        "menu_results_success": {
            "nl": "🏆 Resultaten & Succes",
            "en": "🏆 Results & Success"
        },
        "menu_workshops_creative": {
            "nl": "🎨 Creatieve Workshops",
            "en": "🎨 Creative Workshops"
        },
        "menu_workshops_academic": {
            "nl": "🎓 Academische Workshops",
            "en": "🎓 Academic Workshops"
        },
        "menu_consultancy": {
            "nl": "💼 Consultancy & Advies",
            "en": "💼 Consultancy & Advice"
        },
        "menu_more_info": {
            "nl": "📖 Meer informatie",
            "en": "📖 More information"
        },
        "detailed_info_menu_text": {
            "nl": "📖 Kies een onderwerp voor meer details:",
            "en": "📖 Choose a topic for more details:"
        },
        "menu_back_to_main": {
            "nl": "⬅️ Terug naar hoofdmenu",
            "en": "⬅️ Back to main menu"
        },
        "menu_didactic_methods": {
            "nl": "📚 Didactische Methoden",
            "en": "📚 Didactic Methods"
        },
        "menu_technology_tools": {
            "nl": "💻 Technologie & Tools",
            "en": "💻 Technology & Tools"
        },
        "menu_results_success": {
            "nl": "🏆 Resultaten & Succes",
            "en": "🏆 Results & Success"
        },
        "menu_workshops_creative": {
            "nl": "🎨 Creatieve Workshops",
            "en": "🎨 Creative Workshops"
        },
        "menu_workshops_academic": {
            "nl": "🎓 Academische Workshops",
            "en": "🎓 Academic Workshops"
        },
        "menu_consultancy": {
            "nl": "💼 Consultancy & Advies",
            "en": "💼 Consultancy & Advice"
        },
        
        # Handoff
        "handoff_teacher": {
            "nl": "Ik verbind je door met Stephen. Een moment geduld...",
            "en": "I'm connecting you with Stephen. One moment please..."
        },
        "handoff_menu_text": {
            "nl": "🤖 Wil je terug naar de bot of liever met Stephen blijven praten?",
            "en": "🤖 Do you want to return to the bot or prefer to continue talking with Stephen?"
        },
        "menu_return_to_bot": {
            "nl": "🤖 Terug naar bot",
            "en": "🤖 Return to bot"
        },
        "menu_stay_with_stephen": {
            "nl": "👨‍🏫 Blijf bij Stephen",
            "en": "👨‍🏫 Stay with Stephen"
        },
        "handoff_stay_with_stephen": {
            "nl": "👨‍🏫 Perfect! Stephen neemt het gesprek over. Je kunt hem direct vragen stellen.",
            "en": "👨‍🏫 Perfect! Stephen will take over the conversation. You can ask him questions directly."
        },
        "handoff_return_to_bot": {
            "nl": "🤖 *Terug naar de bot!* Ik help je verder.",
            "en": "🤖 *Back to the bot!* I'll help you further."
        },
        
        # Menu options
        "menu_option_info": {
            "nl": "ℹ️ Informatie",
            "en": "ℹ️ Information"
        },
        "menu_option_trial": {
            "nl": "🎯 Proefles plannen",
            "en": "🎯 Plan trial lesson"
        },
        "menu_option_handoff": {
            "nl": "👨‍🏫 Stephen spreken",
            "en": "👨‍🏫 Speak to Stephen"
        },
        "menu_option_plan_lesson": {
            "nl": "📅 Les inplannen",
            "en": "📅 Plan lesson"
        },
        "menu_option_same_preferences": {
            "nl": "📅 Zelfde voorkeuren",
            "en": "📅 Same preferences"
        },
        "menu_option_different": {
            "nl": "🆕 Iets anders",
            "en": "🆕 Something else"
        },
        "menu_option_old_preferences": {
            "nl": "📅 Oude voorkeuren",
            "en": "📅 Old preferences"
        },
        "menu_option_new_intake": {
            "nl": "🆕 Nieuwe intake",
            "en": "🆕 New intake"
        },
        "menu_option_trial_lesson": {
            "nl": "🎯 Gratis proefles",
            "en": "🎯 Free trial lesson"
        },
        "info_follow_up_new": {
            "nl": "📄 Wat wil je doen?",
            "en": "📄 What would you like to do?"
        },
        "info_follow_up_existing": {
            "nl": "📄 Wat wil je doen?",
            "en": "📄 What would you like to do?"
        },
        
        # Intake options
        "intake_option_self": {
            "nl": "👤 Voor mezelf",
            "en": "👤 For myself"
        },
        "intake_option_other": {
            "nl": "👥 Voor iemand anders",
            "en": "👥 For someone else"
        },
        "intake_age_check": {
            "nl": "Ben je volwassen? (18+)",
            "en": "Are you an adult? (18+)"
        },
        "intake_guardian_info": {
            "nl": "👨‍👩‍👧‍👦 Voor leerlingen onder de 18 heb ik toestemming van een ouder/verzorger nodig. Kun je de naam en telefoonnummer van je ouder/verzorger delen?",
            "en": "👨‍👩‍👧‍👦 For students under 18, I need permission from a parent/guardian. Can you share the name and phone number of your parent/guardian?"
        },
        "intake_guardian_name": {
            "nl": "Naam ouder/verzorger:",
            "en": "Parent/guardian name:"
        },
        "intake_guardian_phone": {
            "nl": "Telefoonnummer ouder/verzorger:",
            "en": "Parent/guardian phone number:"
        },
        "intake_child_info": {
            "nl": "Nu heb ik de onderwijsgegevens van het kind nodig. Wat is de naam van de leerling?",
            "en": "Now I need the educational information of the child. What is the name of the student?"
        },
        "intake_preferred_times": {
            "nl": "Wat zijn je geprefereerde lesmomenten? (bijv. 'maandag 19:00, woensdag 20:00')",
            "en": "What are your preferred lesson times? (e.g. 'Monday 19:00, Wednesday 20:00')"
        },
        "planning_trial_lesson": {
            "nl": "🎯 Gratis proefles inplannen",
            "en": "🎯 Schedule free trial lesson"
        },
        "planning_regular_lesson": {
            "nl": "📅 Les inplannen",
            "en": "📅 Schedule lesson"
        },
        "trial_lesson_confirmed": {
            "nl": "✅ Je gratis proefles is gepland! Stephen neemt contact op voor bevestiging.",
            "en": "✅ Your free trial lesson is scheduled! Stephen will contact you for confirmation."
        },
        "regular_lesson_confirmed": {
            "nl": "✅ Je les is gepland! Hier is de betalingslink:",
            "en": "✅ Your lesson is scheduled! Here is the payment link:"
        },
        "intake_relationship_parent": {
            "nl": "Ouder/Voogd",
            "en": "Parent/Guardian"
        },
        "intake_relationship_family": {
            "nl": "Familie",
            "en": "Family"
        },
        "intake_relationship_teacher": {
            "nl": "Docent/School",
            "en": "Teacher/School"
        },
        "intake_relationship_other": {
            "nl": "Anders",
            "en": "Other"
        },
        "handoff_duplicate_error": {
            "nl": "Ik zie dat er een probleem is met de conversatie. Laat me je doorverbinden met Stephen zodat hij je kan helpen.",
            "en": "I see there's an issue with the conversation. Let me connect you with Stephen so he can help you."
        },
        "no_slots_available": {
            "nl": "Geen beschikbare slots gevonden. Probeer een andere tijd of neem contact op met Stephen.",
            "en": "No available slots found. Try a different time or contact Stephen."
        },
        "no_trial_slots_available": {
            "nl": "❌ Geen proefles tijden beschikbaar in de komende dagen (doordeweeks 17:00-19:00).\n\n💡 Je kunt:\n• Later opnieuw proberen\n• Een reguliere les boeken (meer flexibiliteit)\n• Met Stephen spreken voor andere opties",
            "en": "❌ No trial lesson times available in the coming days (weekdays 17:00-19:00).\n\n💡 You can:\n• Try again later\n• Book a regular lesson (more flexibility)\n• Speak with Stephen for other options"
        },
        "numbered_fallback_instruction": {
            "nl": "Typ het nummer van je keuze (bijv. '1' of '2')",
            "en": "Type the number of your choice (e.g. '1' or '2')"
        },
        "email_request": {
            "nl": "📧 Voor de bevestiging heb ik nog je e-mailadres nodig. Kun je dat delen?",
            "en": "📧 For the confirmation, I still need your email address. Can you share that?"
        },
        "email_confirmation": {
            "nl": "📧 Bedankt! Ik heb je e-mailadres opgeslagen voor de bevestiging.\n\n🎯 Je gratis proefles is volledig bevestigd. Tot dan!",
            "en": "📧 Thank you! I've saved your email address for the confirmation.\n\n🎯 Your free trial lesson is fully confirmed. See you then!"
        },
        "email_invalid": {
            "nl": "❌ Dat lijkt geen geldig e-mailadres. Kun je het opnieuw proberen? (bijvoorbeeld: naam@email.com)",
            "en": "❌ That doesn't look like a valid email address. Can you try again? (for example: name@email.com)"
        },
        
        # Prefill action menu
        "prefill_action_trial_lesson": {
            "nl": "📅 Proefles plannen",
            "en": "📅 Plan trial lesson"
        },
        "prefill_action_main_menu": {
            "nl": "📖 Meer informatie",
            "en": "📖 More information"
        },
        "prefill_action_handoff": {
            "nl": "👨‍🏫 Stephen spreken",
            "en": "👨‍🏫 Speak with Stephen"
        },
        "prefill_action_all_lessons": {
            "nl": "📅 Alle lessen inplannen",
            "en": "📅 Schedule all lessons"
        },
        "prefill_action_trial_first": {
            "nl": "🎯 Gratis proefles (1 uur)",
            "en": "🎯 Free trial lesson (1 hour)"
        },
        "prefill_action_urgent_session": {
            "nl": "🚨 Spoed: 2-uurs sessie (€120)",
            "en": "🚨 Urgent: 2-hour session (€120)"
        },
        "prefill_action_menu_text": {
            "nl": "✅ *Perfect!* Ik heb je informatie verwerkt en met Stephen gedeeld zodat hij je zo goed mogelijk kan helpen.\n\n*Opties:*\n• **Gratis proefles**: Kennismaking zonder verplichting\n• **Spoedles**: Directe hulp met betaling\n• **Meer info**: Over Stephen en zijn aanpak\n• **Stephen spreken**: Direct contact",
            "en": "✅ *Perfect!* I've processed your information and shared it with Stephen so he can help you as best as possible.\n\n*Options:*\n• **Free trial lesson**: Introduction without obligation\n• **Urgent session**: Immediate help with payment\n• **More info**: About Stephen and his approach\n• **Speak to Stephen**: Direct contact"
        },
        "prefill_action_menu_title": {
            "nl": "✅ Perfect! Kies je optie:",
            "en": "✅ Perfect! Choose your option:"
        },
        "preferences_check_title": {
            "nl": "⏰ Zijn je voorkeuren qua lesmomenten nog hetzelfde?",
            "en": "⏰ Are your lesson time preferences still the same?"
        },
        "preferences_check_yes": {
            "nl": "✅ Ja, nog hetzelfde",
            "en": "✅ Yes, still the same"
        },
        "preferences_check_no": {
            "nl": "🔄 Nee, zijn veranderd",
            "en": "🔄 No, they have changed"
        },
        "preferences_share_current": {
            "nl": "📋 Hier zijn je huidige voorkeuren:\n\n⏰ **Voorkeur tijd**: {preferred_times}\n📍 **Locatie**: {location_preference}\n\nZijn deze nog correct?",
            "en": "📋 Here are your current preferences:\n\n⏰ **Preferred time**: {preferred_times}\n📍 **Location**: {location_preference}\n\nAre these still correct?"
        },
        "preferences_update_request": {
            "nl": "🔄 Geef je nieuwe voorkeuren qua lesmomenten:\n\n• Wanneer ben je beschikbaar? (bijv. 'maandag 19:00, woensdag 20:00')\n• Waar wil je les hebben? (thuis, Science Park, VU/UvA)\n• Andere voorkeuren?",
            "en": "🔄 Please provide your new lesson time preferences:\n\n• When are you available? (e.g. 'Monday 19:00, Wednesday 20:00')\n• Where do you want lessons? (home, Science Park, VU/UvA)\n• Other preferences?"
        },
        "prefill_confirmation_header": {
            "nl": "📋 *Wat ik van je bericht begrepen heb:*",
            "en": "📋 *What I understood from your message:*"
        },
        "prefill_confirmation_footer": {
            "nl": "❓ *Klopt dit allemaal?*",
            "en": "❓ *Is this all correct?*"
        },
        
        # Prefill confirmation field labels
        "level_label": {
            "nl": "Niveau",
            "en": "Level"
        },
                "level_po": {
                    "nl": "Basisschool",
                    "en": "Primary School"
                },
                "level_university_wo": {
                    "nl": "Universiteit (WO)",
                    "en": "University (WO)"
                },
                "level_university_hbo": {
                    "nl": "Universiteit (HBO)",
                    "en": "University (HBO)"
                },
                "level_adult": {
                    "nl": "Volwassenenonderwijs",
                    "en": "Adult Education"
                },
                "subject_label": {
                    "nl": "Vak",
                    "en": "Subject"
                },
                "subject_math": {
                    "nl": "Wiskunde",
                    "en": "Mathematics"
                },
                "subject_stats": {
                    "nl": "Statistiek",
                    "en": "Statistics"
                },
                "subject_english": {
                    "nl": "Engels",
                    "en": "English"
                },
                "subject_programming": {
                    "nl": "Programmeren",
                    "en": "Programming"
                },
                "subject_science": {
                    "nl": "Natuurkunde",
                    "en": "Physics"
                },
                "subject_chemistry": {
                    "nl": "Scheikunde",
                    "en": "Chemistry"
                },
                "goals_label": {
                    "nl": "Leerdoelen",
                    "en": "Learning Goals"
                },
                "preferred_times_label": {
                    "nl": "Voorkeur tijd",
                    "en": "Preferred Time"
                },
                "location_preference_label": {
                    "nl": "Locatie voorkeur",
                    "en": "Location Preference"
                },
                "contact_person_label": {
                    "nl": "Contactpersoon",
                    "en": "Contact Person"
                },
                "for_who_label": {
                    "nl": "Voor wie",
                    "en": "For whom"
                },
                "for_who_self": {
                    "nl": "Voor mij",
                    "en": "For me"
                },
                "for_who_child": {
                    "nl": "Voor iemand anders",
                    "en": "For someone else"
                },
                "for_who_student": {
                    "nl": "Voor iemand anders",
                    "en": "For someone else"
                },
                "for_who_other": {
                    "nl": "Voor iemand anders",
                    "en": "For someone else"
                },
                "relationship_label": {
                    "nl": "Relatie",
                    "en": "Relationship"
                },
                "relationship_self": {
                    "nl": "Zichzelf",
                    "en": "Self"
                },
                "relationship_parent": {
                    "nl": "Ouder",
                    "en": "Parent"
                },
                "relationship_teacher": {
                    "nl": "Docent",
                    "en": "Teacher"
                },
                "relationship_other": {
                    "nl": "Anders",
                    "en": "Other"
                },
                "name_label": {
                    "nl": "Naam leerling",
                    "en": "Student name"
                },
        
        # Prefill confirmation options
        "prefill_confirmation_question": {
            "nl": "Klopt deze informatie?",
            "en": "Is this information correct?"
        },
        "prefill_confirmation_menu_title": {
            "nl": "Bevestig de informatie:",
            "en": "Confirm the information:"
        },
        "prefill_confirm_all": {
            "nl": "✅ Ja, klopt!",
            "en": "✅ Yes, correct!"
        },
        "prefill_correct_all": {
            "nl": "❌ Nee, aanpassen",
            "en": "❌ No, change"
        },
        "prefill_correct_partial": {
            "nl": "🤔 Deels correct",
            "en": "🤔 Partly correct"
        },
        "prefill_confirmed_message": {
            "nl": "✅ Perfect! Ik heb je informatie verwerkt. Wat wil je nu doen?",
            "en": "✅ Perfect! I've processed your information. What would you like to do now?"
        },
        
        # General greeting tip
        "general_greeting_tip": {
            "nl": "💡 *Tip:* Je kunt ook gewoon je verhaal uittypen en dan help ik je verder.",
            "en": "💡 *Tip:* You can also just type out your story and I'll help you further."
        },
        
        # FAQ Translations
        "faq_1_question": {
            "nl": "Wat inspireerde ons om bijles en onderwijs aan te bieden?",
            "en": "What inspired us to offer tutoring and education?"
        },
        "faq_1_answer": {
            "nl": "Onze passie voor bijles en onderwijs komt voort uit de persoonlijke ervaringen van Stephen. Zijn reis door uitdagingen in wiskunde op de middelbare school leidde tot een diep begrip van het vak en een sterke motivatie om anderen te helpen. Als team delen wij deze passie en zien wij het als een kans om een positieve impact te maken op het leven van onze studenten.",
            "en": "Our passion for tutoring and education stems from Stephen's personal experiences. His journey through challenges in high school mathematics led to a deep understanding of the subject and a strong motivation to help others. As a team, we share this passion and see it as an opportunity to make a positive impact on our students' lives."
        },
        "faq_2_question": {
            "nl": "Hoe omschrijven wij onze onderwijsaanpak en -methoden?",
            "en": "How do we describe our teaching approach and methods?"
        },
        "faq_2_answer": {
            "nl": "Onze onderwijsaanpak is sterk gericht op persoonlijke begeleiding en maatwerk. We gebruiken technologie zoals iPad-aantekeningen en bieden tot zeven dagen na de les ondersteuning via WhatsApp. Ons doel is om een leeromgeving te creëren waarin studenten op hun eigen tempo kunnen groeien en bloeien.",
            "en": "Our teaching approach is strongly focused on personal guidance and customization. We use technology such as iPad notes and offer support via WhatsApp for up to seven days after the lesson. Our goal is to create a learning environment where students can grow and flourish at their own pace."
        },
        "faq_3_question": {
            "nl": "Wat maakt onze bijlessen uniek in vergelijking met andere aanbieders?",
            "en": "What makes our tutoring unique compared to other providers?"
        },
        "faq_3_answer": {
            "nl": "Onze bijlessen onderscheiden zich door de veelzijdigheid en brede achtergrond van ons team. We hebben een multidisciplinaire aanpak die ons helpt complexe onderwerpen op een begrijpelijke manier te benaderen. We focussen ook sterk op de persoonlijke groei van onze studenten.",
            "en": "Our tutoring stands out due to the versatility and broad background of our team. We have a multidisciplinary approach that helps us tackle complex topics in an understandable way. We also have a strong focus on the personal growth of our students."
        },
        "faq_4_question": {
            "nl": "Hoe gaan wij om met verschillende leerstijlen en -niveaus van studenten?",
            "en": "How do we handle different learning styles and levels of students?"
        },
        "faq_4_answer": {
            "nl": "Wij passen onze lessen aan op de specifieke leerstijl van elke student. Onze lessen zijn interactief en dynamisch, met een combinatie van theoretische uitleg, praktische oefeningen en toepassingen in de echte wereld. We gebruiken differentiatie technieken zoals scaffolding om effectief in te spelen op verschillende leerstijlen.",
            "en": "We adapt our lessons to each student's specific learning style. Our lessons are interactive and dynamic, combining theoretical explanation, practical exercises, and real-world applications. We use differentiation techniques such as scaffolding to effectively cater to different learning styles."
        },
        "faq_5_question": {
            "nl": "Welke resultaten en successen hebben wij gezien bij onze studenten?",
            "en": "What results and successes have we seen with our students?"
        },
        "faq_5_answer": {
            "nl": "Onze bijlessen hebben veel studenten geholpen om hun academische prestaties te verbeteren en hun zelfvertrouwen te vergroten. We hebben talloze succesverhalen, waaronder een volwassen student die het CCVX-examen succesvol aflegde en zijn universitaire studie hervatte.",
            "en": "Our tutoring has helped many students improve their academic performance and increase their confidence. We have numerous success stories, including an adult student who successfully passed the CCVX exam and resumed his university studies."
        },
        "faq_6_question": {
            "nl": "Hoe worden de bijlessen georganiseerd?",
            "en": "How are the tutoring sessions organized?"
        },
        "faq_6_answer": {
            "nl": "Onze bijlessen kunnen zowel online als fysiek plaatsvinden. Voor online lessen gebruiken we tools zoals Zoom en Google Meet. De lessen worden gepland op basis van de beschikbaarheid van de student en de bijlesgever, met flexibele tijden om aan verschillende schema's te voldoen.",
            "en": "Our tutoring sessions can take place both online and in person. For online lessons, we use tools like Zoom and Google Meet. The lessons are scheduled based on the availability of the student and the tutor, with flexible times to accommodate different schedules."
        },
        "faq_7_question": {
            "nl": "Wat zijn de kosten van de bijlessen?",
            "en": "What are the costs of the tutoring sessions?"
        },
        "faq_7_answer": {
            "nl": "De kosten variëren afhankelijk van het vak en het onderwijsniveau. We bieden concurrerende tarieven en verschillende pakketten. Neem contact met ons op voor een op maat gemaakte offerte die past bij jouw specifieke behoeften.",
            "en": "The costs vary depending on the subject and educational level. We offer competitive rates and various packages. Contact us for a customized quote that fits your specific needs."
        },
        "faq_8_question": {
            "nl": "Hoe kan ik me aanmelden voor bijles?",
            "en": "How can I sign up for tutoring?"
        },
        "faq_8_answer": {
            "nl": "Je kunt je aanmelden door ons online formulier op de website in te vullen of door contact met ons op te nemen via telefoon of e-mail. We bespreken graag jouw specifieke behoeften en hoe we je het beste kunnen helpen.",
            "en": "You can sign up by filling out our online form on the website or by contacting us via phone or email. We'd be happy to discuss your specific needs and how we can best help you."
        },
        "faq_9_question": {
            "nl": "Hoe verloopt de betalingsprocedure?",
            "en": "How does the payment procedure work?"
        },
        "faq_9_answer": {
            "nl": "Betalingen kunnen worden gedaan per les of per pakket, via bankoverschrijving of online betalingen zoals iDEAL. Facturen worden doorgaans aan het einde van de maand verzonden, afhankelijk van de gemaakte afspraken.",
            "en": "Payments can be made per lesson or per package, via bank transfer or online payments such as iDEAL. Invoices are typically sent at the end of the month, depending on the arrangements made."
        },
        "faq_10_question": {
            "nl": "Is er een mogelijkheid tot een proefles?",
            "en": "Is there an option for a trial lesson?"
        },
        "faq_10_answer": {
            "nl": "Ja, we bieden een gratis proefles aan zodat je kunt kennismaken met onze werkwijze en de bijlesgever. Dit is een goede gelegenheid om te ervaren hoe de lessen worden gegeven en om te bepalen of onze aanpak bij je past.",
            "en": "Yes, we offer a free trial lesson so you can get acquainted with our methods and the tutor. This is a good opportunity to experience how the lessons are given and to determine if our approach suits you."
        },
        "faq_general_help": {
            "nl": "Ik kan je helpen met veelgestelde vragen! Hier zijn enkele onderwerpen waar je naar kunt vragen:\n\n• Inspiratie en achtergrond\n• Onze onderwijsaanpak\n• Wat ons uniek maakt\n• Leerstijlen en niveaus\n• Resultaten en successen\n• Organisatie van lessen\n• Kosten en tarieven\n• Aanmelden en proefles\n• Betalingen\n• Beroepsspecifieke vakken\n• AI en technologie\n• Soft skills\n• Leerproblemen\n• Motivatie\n• Feedback\n• Bedrijven en instellingen\n• Contact\n• Materialen en tools\n• Frequentie en duur\n\nStel gewoon je vraag en ik help je verder!",
            "en": "I can help you with frequently asked questions! Here are some topics you can ask about:\n\n• Inspiration and background\n• Our teaching approach\n• What makes us unique\n• Learning styles and levels\n• Results and successes\n• Lesson organization\n• Costs and rates\n• Signing up and trial lessons\n• Payments\n• Profession-specific subjects\n• AI and technology\n• Soft skills\n• Learning difficulties\n• Motivation\n• Feedback\n• Companies and institutions\n• Contact\n• Materials and tools\n• Frequency and duration\n\nJust ask your question and I'll help you further!"
        },
        "intake_student_name": {
            "nl": "Wat is de volledige naam van de leerling?",
            "en": "What is the student's full name?"
        },
        "prefill_step_by_step": {
            "nl": "Geen probleem! Laten we het stap voor stap doorlopen. Ik stel je een paar vragen om je zo goed mogelijk te kunnen helpen.",
            "en": "No problem! Let's go through it step by step. I'll ask you a few questions to help you as best as possible."
        },
        "prefill_check_info": {
            "nl": "Begrijpelijk! Laten we de informatie stap voor stap controleren. Ik stel je een paar vragen om alles goed in te vullen.",
            "en": "Understandable! Let's check the information step by step. I'll ask you a few questions to fill everything in properly."
        },
        "prefill_assume_correct": {
            "nl": "Ik ga ervan uit dat de informatie klopt en ga verder met de intake. Je kunt later altijd nog dingen aanpassen.",
            "en": "I'll assume the information is correct and continue with the intake. You can always adjust things later."
        },
        "planning_trial_lesson_intro": {
            "nl": "🎯 Perfect! Laten we een gratis proefles van 30 minuten inplannen. Ik heb een paar vragen om de les goed voor te bereiden.",
            "en": "🎯 Perfect! Let's schedule a free 30-minute trial lesson. I have a few questions to prepare the lesson well."
        },
        "planning_premium_service": {
            "nl": "📅 Perfect! Laten we alle lessen inplannen. Ik ga je helpen met het plannen van een volledig pakket.",
            "en": "📅 Perfect! Let's schedule all lessons. I'll help you plan a complete package."
        },
        "planning_urgent_session": {
            "nl": "🚨 Perfect! Laten we een spoed 2-uurs sessie inplannen voor €120. Na het selecteren van een tijd krijg je direct een betaallink.",
            "en": "🚨 Perfect! Let's schedule an urgent 2-hour session for €120. After selecting a time, you'll get a payment link immediately."
        },
        "planning_premium_slots": {
            "nl": "Beschikbare tijden voor volledig pakket:",
            "en": "Available times for complete package:"
        },
        "planning_trial_slots": {
            "nl": "📅 Beschikbare tijden voor gratis proefles (doordeweeks 17:00-19:00):",
            "en": "📅 Available times for free trial lesson (weekdays 17:00-19:00):"
        },
        "planning_regular_slots": {
            "nl": "Beschikbare tijden voor les:",
            "en": "Available times for lesson:"
        },
        "post_trial_message": {
            "nl": "🎉 Geweldig! Je proefles is ingepland. Na de proefles kun je kiezen wat je wilt doen.",
            "en": "🎉 Great! Your trial lesson is scheduled. After the trial lesson, you can choose what you'd like to do."
        },
        "post_trial_menu_title": {
            "nl": "Wat wil je na de proefles doen?",
            "en": "What would you like to do after the trial lesson?"
        },
        "post_trial_plan_all_lessons": {
            "nl": "📅 Alle lessen inplannen",
            "en": "📅 Schedule all lessons"
        },
        "post_trial_plan_single_lesson": {
            "nl": "📅 Eén les inplannen",
            "en": "📅 Schedule one lesson"
        },
        "post_trial_main_menu": {
            "nl": "📋 Meer informatie",
            "en": "📋 More information"
        },
        "post_trial_handoff": {
            "nl": "👨‍🏫 Met Stephen spreken",
            "en": "👨‍🏫 Speak with Stephen"
        },
        "error_unclear_question": {
            "nl": "❓ Ik begrijp je vraag niet helemaal. Kun je een van de opties hieronder kiezen?",
            "en": "❓ I don't quite understand your question. Can you choose one of the options below?"
        },
        "error_invalid_time": {
            "nl": "❌ Ik begrijp de tijd niet. Kies een van de beschikbare tijden.",
            "en": "❌ I don't understand the time. Please choose one of the available times."
        },
        "error_time_processing": {
            "nl": "❌ Er is een fout opgetreden bij het verwerken van de tijd. Probeer het opnieuw.",
            "en": "❌ An error occurred while processing the time. Please try again."
        },
        "error_planning_failed": {
            "nl": "❌ Er is een fout opgetreden bij het inplannen. Probeer het later opnieuw.",
            "en": "❌ An error occurred while scheduling. Please try again later."
        }
    }
    
    if key in translations and lang in translations[key]:
        text = translations[key][lang]
        return text.format(**kwargs) if kwargs else text
    else:
        return key

# API functions with duplicate detection
def send_text_with_duplicate_check(conversation_id, text, persist: bool = True):
    """Send text message with duplicate detection"""
    # Check for duplicate messages
    conv_attrs = get_conv_attrs(conversation_id)
    last_message = conv_attrs.get("last_bot_message", "")
    
    print(f"🔍 Duplicate check - Current: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    print(f"🔍 Duplicate check - Last: '{last_message[:50]}{'...' if len(last_message) > 50 else ''}'")
    
    if text == last_message:
        print(f"🔄 Duplicate message detected: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print(f"🚨 Skipping duplicate message to prevent spam")
        return False  # Don't send handoff, just skip the duplicate
    
    # Use the new API client
    success = send_text(conversation_id, text)
    if success:
        print(f"✅ Text message sent: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        if persist:
            # Store this message as the last sent message AFTER successful send
            try:
                current_attrs = get_conv_attrs(conversation_id)
                current_attrs["last_bot_message"] = text
                attrs_success = safe_set_conv_attrs(conversation_id, current_attrs)
                if not attrs_success:
                    print(f"⚠️ Failed to update conversation attributes after message send")
            except Exception as e:
                print(f"⚠️ Skipping last_bot_message persist due to error: {e}")
    else:
        print(f"❌ Text message failed")
    return success

def assign_conversation(conversation_id, assignee_id):
    """Assign a conversation to a specific Chatwoot user"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/assignments"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    data = {"assignee_id": assignee_id}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Conversation {conversation_id} assigned to user {assignee_id}")
        else:
            print(f"⚠️ Failed to assign conversation: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"❌ Assignment error: {e}")

def send_handoff_message(conversation_id, text):
    """Send handoff message and set labels"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    data = {
        "content": text,
        "message_type": "outgoing"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"👨‍🏫 Handoff message sent: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            # Add handoff labels
            add_conv_labels(conversation_id, ["intent_handoff_duplicate", "intent_handoff_auto"])
            safe_set_conv_attrs(conversation_id, {"pending_intent": "handoff"})
            # Assign to Stephen (user_id=2)
            assign_conversation(conversation_id, 2)
            
            # Send menu with option to return to main menu
            send_handoff_menu(conversation_id)
            return True
        else:
            print(f"⚠️ Handoff message failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Handoff message error: {e}")
        return False

def send_handoff_menu(conversation_id):
    """Send menu with option to return to main menu after handoff"""
    # Get contact language
    contact_id = get_contact_id_from_conversation(conversation_id)
    contact_attrs = get_contact_attrs(contact_id)
    lang = contact_attrs.get("language", "nl")
    
    # Send menu with return option - use direct API call to avoid handoff state blocking
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    
    # Create menu items
    items = [
        {
            "title": t("menu_return_to_bot", lang),
            "value": "return_to_bot"
        },
        {
            "title": t("menu_stay_with_stephen", lang),
            "value": "stay_with_stephen"
        }
    ]
    
    data = {
        "content": t("handoff_menu_text", lang),
        "content_type": "input_select",
        "content_attributes": {
            "items": items
        },
        "message_type": "outgoing",
        "private": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Handoff menu sent successfully")
            return True
        else:
            print(f"❌ Handoff menu failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Handoff menu error: {e}")
        return False

def send_admin_warning(conversation_id: int, warning_message: str):
    """Send an admin-only warning message"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    
    data = {
        "content": f"🚨 ADMIN WARNING: {warning_message}",
        "message_type": "outgoing",
        "private": True  # This makes it admin-only
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Admin warning sent: {warning_message}")
            return True
        else:
            print(f"❌ Failed to send admin warning: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Admin warning error: {e}")
        return False

# OpenAI prefill functions
def analyze_first_message_with_openai(message: str, conversation_id: int = None) -> Dict[str, Any]:
    """Analyze first message using OpenAI to extract intake information"""
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not available, skipping prefill")
        if conversation_id:
            send_admin_warning(conversation_id, "OpenAI API key not configured - prefill disabled")
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
    - **"adult"**: Alleen voor volwassenen die middelbare school stof moeten beheersen (niet universiteit/HBO)
    - **"mbo"**: Voor MBO studenten
    - **"vwo/havo/vmbo"**: Voor middelbare scholieren
    - **"po"**: Voor basisschool leerlingen
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
    - "Ik ben volwassen en moet middelbare school wiskunde leren" → school_level: "adult"
    - "Ik zit in 6V" → school_level: "vwo"
    - "Ik doe MBO niveau 4" → school_level: "mbo"
    
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
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        try:
            result = json.loads(content)
            print(f"✅ OpenAI prefill analysis completed")
            return result
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse OpenAI response: {e}")
            return {}
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        
        # Send admin warning about API failure
        if conversation_id:
            error_details = str(e)
            if "quota" in error_details.lower() or "insufficient_quota" in error_details.lower():
                warning_message = "OpenAI API quota exceeded - please check billing"
            elif "rate_limit" in error_details.lower():
                warning_message = "OpenAI API rate limit exceeded"
            elif "authentication" in error_details.lower() or "invalid_api_key" in error_details.lower():
                warning_message = "OpenAI API authentication failed - check API key"
            else:
                warning_message = f"OpenAI API error: {error_details[:100]}"
            
            send_admin_warning(conversation_id, warning_message)
        
        return {}

def map_school_level(level_text: str) -> str:
    """Map school level text to standardized values"""
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
        
        # Adult Education
        "volwassenenonderwijs": "adult", "adult": "adult", "volwassenen": "adult",
        "werkende": "adult", "professional": "adult"
    }
    return level_mapping.get(level_text.lower(), "adult")

def detect_language_from_message(message: str) -> str:
    """Detect language from message content"""
    # Simple Dutch detection based on common words
    dutch_indicators = [
        "ik", "je", "jij", "hij", "zij", "wij", "ons", "mijn", "jouw", "zijn", "haar", "hun",
        "ben", "bent", "is", "zijn", "hebben", "heeft", "hebt", "heb",
        "met", "van", "naar", "voor", "door", "uit", "in", "op", "aan", "bij", "tegen",
        "en", "of", "maar", "want", "omdat", "als", "wanneer", "waar", "hoe", "wat", "wie",
        "graag", "alstublieft", "dankjewel", "bedankt", "hallo", "dag", "doei",
        "moeite", "probleem", "vraag", "antwoord", "les", "lesgeven", "leren", "studeren",
        "school", "universiteit", "student", "docent", "leraar", "professor",
        "wiskunde", "nederlands", "engels", "natuurkunde", "scheikunde", "biologie",
        "examen", "toets", "tentamen", "cijfer", "voldoende", "onvoldoende"
    ]
    
    # Strong Dutch indicators (single words that strongly indicate Dutch)
    strong_dutch_indicators = ["hallo", "dag", "doei", "dankjewel", "bedankt", "alstublieft", "graag", "nederlands"]
    
    message_lower = message.lower().strip()
    
    # Check for strong Dutch indicators first
    if any(word in message_lower for word in strong_dutch_indicators):
        return "nl"
    
    # Count Dutch words
    dutch_word_count = sum(1 for word in dutch_indicators if word in message_lower)
    
    # Check for strong English indicators
    strong_english_indicators = ["hello", "hi", "hey", "thanks", "thank you", "please", "engels"]
    if any(word in message_lower for word in strong_english_indicators):
        return "en"
    
    # If we find multiple Dutch words, it's likely Dutch
    if dutch_word_count >= 2:  # Reduced from 3 to 2
        return "nl"
    else:
        return "en"  # Default to English

def analyze_info_request_with_openai(message: str, conversation_id: int = None) -> Dict[str, Any]:
    """Analyze information request using OpenAI to determine what info the user wants"""
    if not OPENAI_API_KEY:
        print("⚠️ OpenAI API key not available, skipping info analysis")
        return {}
    
    system_prompt = """
    Je bent een AI assistent die informatie vragen analyseert om te bepalen welke informatie de gebruiker zoekt.
    
    Over Stephen's diensten:
    - **Tarieven**: Verschillende prijzen voor verschillende niveaus (hoger onderwijs, voortgezet onderwijs, MBO, etc.)
    - **Werkwijze**: Hoe Stephen lesgeeft, methoden, aanpak
    - **Diensten**: Verschillende vakken en diensten (wiskunde, statistiek, programmeren, etc.)
    - **Reiskosten**: Kosten voor reizen naar de leerling
    - **Last-minute**: Extra kosten voor spoedlessen
    - **Voorwaarden**: Algemene voorwaarden en regels
    - **Weekend programma's**: Speciale weekend diensten
    - **Korte versie**: Samenvatting van alle informatie
    - **Persoonlijke achtergrond**: Stephen's ervaring en kwalificaties
    - **Didactische methoden**: Specifieke lesmethoden
    - **Technologie tools**: Tools die gebruikt worden
    - **Resultaten en succes**: Voorbeelden van succesverhalen
    - **Creatieve workshops**: Workshop diensten
    - **Academische workshops**: Academische workshop diensten
    - **Consultancy**: Adviesdiensten
    
    Analyseer de vraag en bepaal welke informatie categorie(ën) het beste passen:
    
    - **tariffs**: Vragen over prijzen, kosten, tarieven, betalingen
    - **work_method**: Vragen over hoe Stephen werkt, methoden, aanpak
    - **services**: Vragen over welke vakken/diensten beschikbaar zijn
    - **travel_costs**: Vragen over reiskosten, locatie, afstand
    - **last_minute**: Vragen over spoedlessen, urgentie, snelheid
    - **conditions**: Vragen over voorwaarden, regels, afspraken
    - **weekend_programs**: Vragen over weekend diensten
    - **short_version**: Vragen om samenvatting, overzicht
    - **personal_background**: Vragen over Stephen's ervaring, kwalificaties
    - **didactic_methods**: Vragen over lesmethoden, didactiek
    - **technology_tools**: Vragen over tools, technologie
    - **results_success**: Vragen over resultaten, succesverhalen
    - **workshops_creative**: Vragen over creatieve workshops
    - **workshops_academic**: Vragen over academische workshops
    - **consultancy**: Vragen over adviesdiensten
    
    Geef een JSON response met:
    {
        "primary_category": "string", // Hoofdcategorie (meest relevant)
        "secondary_categories": ["string"], // Extra categorieën die ook relevant zijn
        "confidence": "float", // Zekerheid (0.0-1.0)
        "is_general_question": "boolean", // Is het een algemene vraag die meerdere categorieën raakt?
        "suggested_response": "string" // Korte suggestie voor antwoord
    }
    
    Voorbeelden:
    - "Wat kosten de lessen?" → primary_category: "tariffs"
    - "Hoe werkt Stephen?" → primary_category: "work_method"
    - "Welke vakken geeft Stephen?" → primary_category: "services"
    - "Wat zijn de reiskosten?" → primary_category: "travel_costs"
    - "Kan ik morgen al een les hebben?" → primary_category: "last_minute"
    - "Wat zijn de voorwaarden?" → primary_category: "conditions"
    - "Geeft Stephen ook weekend lessen?" → primary_category: "weekend_programs"
    - "Kun je een samenvatting geven?" → primary_category: "short_version"
    - "Wat is Stephen's achtergrond?" → primary_category: "personal_background"
    - "Hoe geeft Stephen les?" → primary_category: "didactic_methods"
    - "Welke tools gebruikt Stephen?" → primary_category: "technology_tools"
    - "Wat zijn de resultaten?" → primary_category: "results_success"
    - "Geeft Stephen workshops?" → primary_category: "workshops_creative"
    - "Kan Stephen advies geven?" → primary_category: "consultancy"
    
    Geef alleen de JSON response, geen extra tekst.
    """
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyseer deze informatie vraag: {message}"}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        print(f"🤖 Info analysis result: {result}")
        
        # Parse JSON response
        import json
        analysis = json.loads(result)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing info request: {e}")
        if conversation_id:
            send_admin_warning(conversation_id, f"Info analysis failed: {str(e)[:100]}")
        
        return {}

def map_topic(topic_text: str) -> str:
    """Map topic text to standardized values"""
    topic_mapping = {
        # Mathematics
        "wiskunde": "math", "mathematics": "math", "math": "math",
        "wiskunde a": "math", "wiskunde b": "math", "wiskunde c": "math", "wiskunde d": "math",
        "calculus": "math", "algebra": "math", "geometry": "math",
        "mbo rekenen": "math", "rekenen 2f": "math", "rekenen 3f": "math",
        
        # Statistics & Data Science
        "statistiek": "stats", "statistics": "stats", "stats": "stats",
        "data science": "stats", "data science": "stats", "spss": "stats", "r": "stats",
        "regression": "stats", "hypothesis testing": "stats", "mixed models": "stats",
        
        # Programming
        "programmeren": "programming", "programming": "programming",
        "python": "programming", "javascript": "programming", "java": "programming",
        "coding": "programming", "software development": "programming",
        
        # Languages
        "engels": "english", "english": "english", "ib english": "english",
        "cambridge english": "english", "ielts": "english", "toefl": "english",
        
        # Sciences
        "natuurkunde": "science", "physics": "science", "fysica": "science",
        "scheikunde": "chemistry", "chemistry": "chemistry", "chemie": "chemistry",
        
        # Thesis & Research
        "scriptie": "other", "thesis": "other", "research": "other",
        "onderzoek": "other", "paper": "other", "dissertation": "other"
    }
    return topic_mapping.get(topic_text.lower(), "other")

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
            max_tokens=200,
            temperature=0.3
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
            send_admin_warning(conversation_id, f"Preferences analysis failed: {str(e)[:100]}")
        
        return {
            "preferred_times": "",
            "location_preference": "",
            "other_preferences": "",
            "confidence": 0.0
        }

def is_prefill_sufficient_for_trial_lesson(prefilled_info: Dict[str, Any]) -> bool:
    """Check if the prefilled information is sufficient to proceed to trial lesson planning"""
    # Minimum required information for a trial lesson
    required_fields = ["learner_name", "school_level", "topic_secondary"]
    
    # Check if we have the essential information
    has_required = all(prefilled_info.get(field) for field in required_fields)
    
    if not has_required:
        return False
    
    # Additional checks for quality
    learner_name = prefilled_info.get("learner_name", "")
    topic_secondary = prefilled_info.get("topic_secondary", "")
    
    # Name should be reasonable length
    if len(learner_name) < 2 or len(learner_name) > 50:
        return False
    
    # Topic should be a valid subject
    valid_subjects = [
        "wiskunde", "math", "mathematics", "calculus", "algebra", "geometry",
        "statistiek", "statistics", "data science", "spss", "regression",
        "engels", "english", "ib", "cambridge", "ielts", "toefl",
        "programmeren", "programming", "python", "javascript", "coding",
        "natuurkunde", "physics", "fysica", "scheikunde", "chemistry", "chemie",
        "mbo rekenen", "rekenen 2f", "rekenen 3f", "scriptie", "thesis", "research"
    ]
    topic_lower = topic_secondary.lower()
    has_valid_subject = any(subject in topic_lower for subject in valid_subjects)
    
    return has_valid_subject

def smart_extraction_check(prefilled_info: Dict[str, Any]) -> str:
    """Smart check for extraction - skip confirmation for obvious cases"""
    # If lesson is for the learner themselves
    if prefilled_info.get("for_who") == "self":
        # Automatically assume relationship = "self"
        # No need to confirm relationship
        # Go directly to prefill action menu
        print(f"🎯 Smart check: Lesson for self, skipping relationship confirmation")
        return "direct_to_action_menu"
    
    # If lesson is for someone else
    else:
        # Need to confirm relationship
        # Normal confirmation flow
        print(f"🎯 Smart check: Lesson for someone else, normal confirmation flow")
        return "normal_confirmation_flow"

def create_child_contact(analysis: Dict[str, Any], conversation_id: int) -> int:
    """Create a separate contact for the child when a parent is writing"""
    try:
        # Get the parent contact ID from the conversation
        parent_contact_id = get_contact_id_from_conversation(conversation_id)
        if not parent_contact_id:
            print("❌ Could not get parent contact ID")
            return None
        
        # Create child contact with basic info
        child_name = analysis.get("learner_name", "Onbekende leerling")
        child_attrs = {
            "language": "nl",
            "segment": "student",
            "is_adult": False,
            "is_student": True,
            "parent_contact_id": str(parent_contact_id),
            "created_by_parent": True
        }
        
        # Add school level if available
        if analysis.get("school_level"):
            child_attrs["school_level"] = map_school_level(analysis["school_level"])
        
        # Create the child contact using ChatwootAPI
        child_contact = ChatwootAPI.create_contact(
            inbox_id=2,  # WhatsApp inbox
            name=child_name,
            phone="",  # No phone number for now
            attrs=child_attrs
        )
        
        if child_contact:
            child_contact_id = child_contact.get("id") or child_contact.get("payload", {}).get("contact", {}).get("id")
            if child_contact_id:
                print(f"👶 Created child contact {child_contact_id} for {child_name}")
                return child_contact_id
            else:
                print(f"❌ No child contact ID in response: {child_contact}")
                return None
        else:
            print("❌ Failed to create child contact")
            return None
            
    except Exception as e:
        print(f"❌ Error creating child contact: {e}")
        return None

def prefill_intake_from_message(message: str, conversation_id: int = None) -> Dict[str, Any]:
    """Prefill intake information from the first message"""
    print(f"🔍 Analyzing first message for prefill: {message[:100]}{'...' if len(message) > 100 else ''}")
    
    analysis = analyze_first_message_with_openai(message, conversation_id)
    if not analysis:
        return {}
    
    # Map and validate the extracted information
    prefilled = {}
    
    # Basic information
    if analysis.get("is_adult") is not None:
        prefilled["is_adult"] = analysis["is_adult"]
    
    if analysis.get("for_who"):
        prefilled["for_who"] = analysis["for_who"]
    
    if analysis.get("learner_name"):
        prefilled["learner_name"] = analysis["learner_name"]
    
    if analysis.get("relationship_to_learner"):
        prefilled["relationship_to_learner"] = analysis["relationship_to_learner"]
    
    # School level
    if analysis.get("school_level"):
        prefilled["school_level"] = map_school_level(analysis["school_level"])
    
    # Topic
    if analysis.get("topic_primary"):
        prefilled["topic_primary"] = map_topic(analysis["topic_primary"])
    
    if analysis.get("topic_secondary"):
        prefilled["topic_secondary"] = analysis["topic_secondary"]
    
    # Goals
    if analysis.get("goals"):
        prefilled["goals"] = analysis["goals"]
    
    # Preferences
    if analysis.get("preferred_times"):
        prefilled["preferred_times"] = analysis["preferred_times"]
    
    if analysis.get("lesson_mode"):
        prefilled["lesson_mode"] = analysis["lesson_mode"]
    
    if analysis.get("toolset"):
        prefilled["toolset"] = analysis["toolset"]
    
    if analysis.get("program"):
        prefilled["program"] = analysis["program"]
    
    # referral_source wordt handmatig ingevuld, niet automatisch
    # if analysis.get("referral_source"):
    #     prefilled["referral_source"] = analysis["referral_source"]
    
    # Additional information
    if analysis.get("location_preference"):
        prefilled["location_preference"] = analysis["location_preference"]
    
    if analysis.get("contact_name"):
        prefilled["contact_name"] = analysis["contact_name"]
    
    if analysis.get("urgency"):
        prefilled["urgency"] = analysis["urgency"]
    
    # Note: Child contact creation is postponed until after prefill confirmation
    # This prevents the "Could not get parent contact ID" error for new contacts
    if analysis.get("for_who") == "child" and analysis.get("learner_name"):
        print(f"👶 Child contact creation postponed until after prefill confirmation for {analysis['learner_name']}")
    
    print(f"📋 Prefilled information: {prefilled}")
    return prefilled

def get_contact_id_from_conversation(conversation_id):
    """Get contact ID from conversation ID"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("contact_inbox", {}).get("contact_id")
        else:
            print(f"⚠️ Failed to get conversation details: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting conversation details: {e}")
        return None





def send_input_select_only(conversation_id, text, options):
    """
    🎯 CRITICAL FUNCTION: Send input_select format only - no fallbacks with strict WhatsApp formatting rules
    
    This function is ESSENTIAL for showing interactive menu buttons in WhatsApp.
    It uses the ChatwootAPI.send_message() function to ensure proper SSL handling
    and prevent the SSL errors that were causing menu failures.
    
    IMPORTANT: This function MUST be used for all menu interactions in WhatsApp.
    Direct HTTP requests were causing SSL errors and menu failures.
    
    Args:
        conversation_id: Chatwoot conversation ID
        text: Menu title/description text
        options: List of (label, value) tuples for menu options
    
    Returns:
        bool: True if menu was sent successfully, False otherwise
    """
    # STRICT WHATSAPP FORMATTING RULES TO PREVENT #131009 ERRORS:
    # • Max rows: ≤ 10 items total
    # • Row title length: ≤ 24 characters (emoji count as 2+ code points)
    # • Button text: ≤ 20 characters
    # • Body text: ≤ 1024 characters
    # • Unique row IDs: ≤ 200 chars, no newlines/markup
    # • No markdown in titles: *bold*, newlines, tabs, etc.
    
    # Limit to max 10 items
    if len(options) > 10:
        print(f"⚠️ Truncating options from {len(options)} to 10 (WhatsApp limit)")
        options = options[:10]
    
    # Process items with strict formatting
    items = []
    for i, (label, value) in enumerate(options):
        # Keep markdown formatting but clean newlines and tabs
        clean_title = label.replace("\n", " ").replace("\t", " ")
        
        # Truncate title to 24 characters (emoji count as 2+ code points)
        if len(clean_title) > 24:
            clean_title = clean_title[:21] + "..."
        
        # Clean and truncate value to 200 characters
        clean_value = str(value).replace("\n", " ").replace("\t", " ")
        if len(clean_value) > 200:
            clean_value = clean_value[:197] + "..."
        
        items.append({
            "title": clean_title,
            "value": clean_value
        })
    
    # Truncate body text to 1024 characters
    if len(text) > 1024:
        text = text[:1020] + "..."
    
    # Use the cw_api send_message function instead of direct HTTP request
    content_attributes = {
        "items": items
    }
    
    try:
        print(f"📤 Sending input_select menu with {len(items)} items...")
        print(f"📤 First few items: {items[:3] if items else 'None'}")
        print(f"📤 Menu title: '{text}'")
        
        # Use the imported send_message function from cw_api
        success = ChatwootAPI.send_message(
            conversation_id, 
            text, 
            "input_select", 
            content_attributes
        )
        
        if success:
            print(f"✅ Chatwoot input_select sent successfully ({len(options)} options)")
            return True
        else:
            print(f"❌ Chatwoot input_select failed")
            return False
    except Exception as e:
        print(f"❌ Chatwoot input_select error: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False








# Note: All API functions are now imported from cw_api module
# The old functions have been replaced with the new ChatwootAPI class

# Segment detection
def detect_segment(contact_id):
    """Detect segment based on contact attributes and history"""
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
          contact_attrs.get("trial_lesson_completed") or
          contact_attrs.get("lesson_booked")):
        segment = "existing"
    # 4. Default to new
    else:
        segment = "new"
    
    # Store the detected segment
    set_contact_attrs(contact_id, {"segment": segment})
    return segment

# Planning profiles
PLANNING_PROFILES = {
    "new": {
        "duration_minutes": 60,
        "earliest_hour": 10,
        "latest_hour": 20,
        "min_lead_minutes": 720,
        "buffer_before_min": 15,
        "buffer_after_min": 15,
        "days_ahead": 10,
        "slot_step_minutes": 30,
        "exclude_weekends": True
    },
    "existing": {
        "duration_minutes": 60,
        "earliest_hour": 9,
        "latest_hour": 21,
        "min_lead_minutes": 360,
        "buffer_before_min": 10,
        "buffer_after_min": 10,
        "days_ahead": 14,
        "slot_step_minutes": 30,
        "exclude_weekends": True
    },
    "returning_broadcast": {
        "duration_minutes": 60,
        "earliest_hour": 9,
        "latest_hour": 21,
        "min_lead_minutes": 360,
        "buffer_before_min": 10,
        "buffer_after_min": 10,
        "days_ahead": 14,
        "slot_step_minutes": 30,
        "exclude_weekends": True
    },
    "weekend": {
        "duration_minutes": 60,
        "earliest_hour": 10,
        "latest_hour": 18,
        "min_lead_minutes": 180,
        "buffer_before_min": 10,
        "buffer_after_min": 10,
        "days_ahead": 7,
        "slot_step_minutes": 30,
        "exclude_weekends": False,
        "allowed_weekdays": [5, 6]  # Saturday, Sunday
    },
    "premium": {
        "duration_minutes": 90,  # Longer lessons for premium
        "earliest_hour": 8,
        "latest_hour": 22,
        "min_lead_minutes": 240,  # 4 hours notice
        "buffer_before_min": 20,
        "buffer_after_min": 20,
        "days_ahead": 21,  # 3 weeks ahead
        "slot_step_minutes": 30,
        "exclude_weekends": False  # Premium includes weekends
    }
}

# Calendar integration (mock implementation)
def suggest_slots(conversation_id, profile_name):
    """Suggest available slots based on planning profile and user preferences"""
    profile = PLANNING_PROFILES.get(profile_name, PLANNING_PROFILES["new"])
    
    # Get user preferences from conversation attributes
    conv_attrs = get_conv_attrs(conversation_id)
    preferred_times = conv_attrs.get("preferred_times", "").lower()
    lesson_type = conv_attrs.get("lesson_type", "trial")
    
    # Dummy agenda implementation for testing
    now = datetime.now(TZ)
    slots = []
    
    # Generate slots for more days for premium service
    days_to_generate = profile.get("days_ahead", 14)
    for i in range(days_to_generate):
        date = now + timedelta(days=i)
        
        # Skip weekends if exclude_weekends is True
        if profile["exclude_weekends"] and date.weekday() >= 5:
            continue
            
        # Skip non-allowed weekdays for weekend profile
        if profile.get("allowed_weekdays") and date.weekday() not in profile["allowed_weekdays"]:
            continue
        
        # Check if this day matches user preferences
        day_name = date.strftime('%A').lower()
        if preferred_times:
            # Simple preference matching
            if "woensdag" in preferred_times and day_name != "wednesday":
                continue
            if "donderdag" in preferred_times and day_name != "thursday":
                continue
            if "vrijdag" in preferred_times and day_name != "friday":
                continue
            if "zaterdag" in preferred_times and day_name != "saturday":
                continue
            if "zondag" in preferred_times and day_name != "sunday":
                continue
            if "maandag" in preferred_times and day_name != "monday":
                continue
            if "dinsdag" in preferred_times and day_name != "tuesday":
                continue
        
        # Generate slots for this day with proper step intervals
        for hour in range(profile["earliest_hour"], profile["latest_hour"]):
            for minute in range(0, 60, profile["slot_step_minutes"]):
                start_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=profile["duration_minutes"])
                
                # Check if slot is in the future and meets minimum lead time
                if start_time > now + timedelta(minutes=profile["min_lead_minutes"]):
                    
                    # SPECIAL RULE: Trial lessons only on weekdays 17:00-19:00
                    if lesson_type == "trial":
                        # Only allow weekdays (Monday = 0, Friday = 4)
                        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                            continue
                        # Only allow 17:00-19:00 for trial lessons
                        if start_time.hour < 17 or start_time.hour >= 19:
                            continue
                    
                    # Check if this time matches user preferences
                    if preferred_times:
                        if "middag" in preferred_times and start_time.hour < 12:
                            continue
                        if "avond" in preferred_times and start_time.hour < 18:
                            continue
                        if "ochtend" in preferred_times and start_time.hour >= 12:
                            continue
                    
                    # Create a readable label
                    slot_label = f"{start_time.strftime('%a %d %b %H:%M')}–{end_time.strftime('%H:%M')}"
                    slots.append({
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "label": slot_label
                    })
    
    # Return more slots for premium service, fewer for others
    if profile_name == "premium":
        return slots[:12]  # More options for premium
    else:
        return slots[:8]  # Standard number for others

def book_slot(conversation_id, start_time, end_time, title, description):
    """Book a slot in Google Calendar"""
    # Dummy implementation for testing
    print(f"📅 Booking slot: {start_time} - {end_time}")
    print(f"📅 Title: {title}")
    print(f"📅 Description: {description}")
    
    # Parse the start time to create a readable format
    try:
        if isinstance(start_time, str):
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = start_time
        
        # Create a readable event ID
        event_id = f"dummy_event_{conversation_id}_{start_dt.strftime('%Y%m%d_%H%M')}"
        
        print(f"✅ Successfully booked dummy slot: {event_id}")
        
        return {
            "id": event_id,
            "htmlLink": f"https://calendar.google.com/event?eid={event_id}",
            "start": start_time,
            "end": end_time,
            "title": title,
            "description": description
        }
    except Exception as e:
        print(f"❌ Error booking slot: {e}")
        return None

# Payment integration (mock implementation)
def create_payment_link(segment, minutes, order_id, conversation_id, student_name, service, audience, program):
    """Create Stripe payment link"""
    # Determine price ID based on segment
    if segment == "weekend":
        price_id = WEEKEND_PRICE_ID_60 if minutes == 60 else WEEKEND_PRICE_ID_90
    else:
        price_id = STANDARD_PRICE_ID_60 if minutes == 60 else STANDARD_PRICE_ID_90
    
    # Mock implementation - in real implementation, this would call Stripe API
    print(f"💳 Creating payment link for segment: {segment}")
    print(f"💳 Price ID: {price_id}")
    print(f"💳 Order ID: {order_id}")
    
    # Return mock payment link
    return f"https://checkout.stripe.com/pay/mock_{order_id}"

def verify_stripe_webhook(payload, signature):
    """Verify Stripe webhook signature"""
    if not STRIPE_WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
    
    try:
        expected = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
    except:
        return False

# Webhook verification
def verify_webhook(request):
    """Verify Chatwoot webhook signature"""
    if not SIG:
        print("⚠️ No HMAC secret configured - allowing all requests")
        return True
    
    signature = request.headers.get('X-Chatwoot-Signature')
    if not signature:
        print("⚠️ No signature found in headers - allowing request")
        return True  # Temporarily allow requests without signature for testing
    
    expected = hmac.new(
        SIG.encode(),
        request.get_data(),
        hashlib.sha256
    ).hexdigest()
    
    is_valid = hmac.compare_digest(signature, expected)
    if not is_valid:
        print(f"⚠️ Signature mismatch - expected: {expected[:10]}..., received: {signature[:10]}...")
    
    return is_valid

# Main webhook handler
@app.post("/cw")
def cw():
    """Main webhook handler for Chatwoot"""
    if not verify_webhook(request):
        print("❌ Webhook unauthorized - signature verification failed")
        return "Unauthorized", 401
    
    data = request.get_json()
    event = data.get("event")
    msg_type = data.get("message_type")
    conversation_id = data.get("conversation", {}).get("id", "unknown")
    contact_id = data.get("contact", {}).get("id") or data.get("sender", {}).get("id", "unknown")
    content = data.get("content", "")
    message_content = content[:50] + "..." if content and len(content) > 50 else content or ""
    event_str = event.upper() if event else "UNKNOWN"
    
    # Create a unique webhook ID for idempotency
    message_id = data.get("id") or data.get("message", {}).get("id")
    webhook_id = f"{conversation_id}_{message_id}_{event}"
    
    # Check if we've already processed this exact webhook
    import hashlib
    webhook_hash = hashlib.md5(webhook_id.encode()).hexdigest()
    
    # Use a simple in-memory cache for webhook deduplication
    if not hasattr(cw, 'processed_webhooks'):
        cw.processed_webhooks = set()
    
    if webhook_hash in cw.processed_webhooks:
        print(f"🔄 Duplicate webhook detected: {webhook_id} - skipping")
        return "OK", 200
    
    # Add to processed set (keep last 1000 webhooks)
    cw.processed_webhooks.add(webhook_hash)
    if len(cw.processed_webhooks) > 1000:
        cw.processed_webhooks.clear()  # Reset to prevent memory leaks

    # Log all webhook events for debugging
    print(f"📨 Webhook received: {event_str} | Type: {msg_type} | Conv:{conversation_id} | Contact:{contact_id} | ID:{message_id}")

    # Only process incoming user messages
    if event != "message_created" or msg_type != "incoming":
        if msg_type == "outgoing":
            print(f"🤖 [BOT OUT] Conv:{conversation_id} Contact:{contact_id} | {message_content}")
        else:
            print(f"⏭️ Skipping event: {event_str} type: {msg_type}")
        return "OK", 200
    
    print(f"💬 [USER IN] Conv:{conversation_id} Contact:{contact_id} | {message_content}")

    # Handle only incoming user messages
    try:
        handle_message_created(data)
    except Exception as e:
        print(f"❌ Error processing {event}: {str(e)}")
        return "Internal Server Error", 500
    return "OK", 200

def handle_conversation_created(data):
    """Handle new conversation creation"""
    conversation = data.get("conversation", {})
    contact = data.get("contact", {})
    
    cid = conversation.get("id")
    contact_id = contact.get("id")
    
    if not cid or not contact_id:
        print("❌ Missing conversation_id or contact_id")
        return
    
    print(f"🆕 New conversation - Conv:{cid} Contact:{contact_id}")
    
    # Initialize conversation attributes
    set_conv_attrs(cid, {
        "language_prompted": False,
        "intake_completed": False,
        "order_id": None
    })
    
    # Detect segment and set contact attribute
    segment = detect_segment(contact_id)
    set_contact_attrs(contact_id, {"segment": segment})
    print(f"🏷️ Segment detected: {segment}")
    
    # Check if language needs to be prompted
    contact_attrs = get_contact_attrs(contact_id)
    if not contact_attrs.get("language") and not get_conv_attrs(cid).get("language_prompted"):
        # Don't prompt for language immediately - wait for first message
        # This allows prefill to run first
        print(f"🌍 Waiting for first message before language selection")
    else:
        # Show appropriate menu based on segment
        print(f"📋 Showing segment menu for {segment}")
        show_segment_menu(cid, contact_id, segment, contact_attrs.get("language", "nl"))

def handle_message_created(data):
    """Handle new message"""
    conversation = data.get("conversation", {})
    sender = data.get("sender", {})
    
    cid = conversation.get("id")
    contact_id = sender.get("id") or data.get("contact", {}).get("id")
    msg_content = data.get("content", "").strip()
    
    # Check for interactive button payloads
    content_attributes = data.get("content_attributes", {})
    if content_attributes:
        print(f"🔘 Interactive payload detected: {content_attributes}")
        # Extract payload from interactive buttons
        if "payload" in content_attributes:
            msg_content = content_attributes["payload"]
            print(f"📦 Extracted payload: '{msg_content}'")
    
    if not cid or not contact_id:
        print("❌ Missing conversation_id or contact_id")
        return
    
    # Check for duplicate message processing (but allow responses to bot prompts)
    conv_attrs = get_conv_attrs(cid)
    last_processed_message = conv_attrs.get("last_processed_message", "")
    last_bot_message = conv_attrs.get("last_bot_message", "")
    pending_intent = conv_attrs.get("pending_intent", "")
    
    # Check for duplicate user message (but allow responses to bot prompts)
    if msg_content == last_processed_message and not pending_intent:
        print(f"🔄 Duplicate message detected: '{msg_content[:50]}{'...' if len(msg_content) > 50 else ''}' - skipping")
        return
    
    # Mark this message as processed immediately to prevent race conditions
    # BUT: if we're in prefill_confirmation state, don't update last_processed_message
    # because we want to allow the user to respond to the confirmation
    if pending_intent != "prefill_confirmation":
        set_conv_attrs(cid, {"last_processed_message": msg_content})
    else:
        print(f"🔍 In prefill_confirmation state - allowing response to confirmation")
    
    # Add a small delay to prevent race conditions with Chatwoot's duplicate webhooks
    import time
    time.sleep(0.1)
    
    # Get attributes
    contact_attrs = get_contact_attrs(contact_id)
    conv_attrs = get_conv_attrs(cid)
    lang = contact_attrs.get("language", "nl")
    
    # Detect segment dynamically (don't rely on stored segment)
    segment = detect_segment(contact_id)
    
    # Update contact attributes with current segment if it changed
    if contact_attrs.get("segment") != segment:
        set_contact_attrs(contact_id, {"segment": segment})
        print(f"🔄 Segment updated from {contact_attrs.get('segment', 'none')} to {segment}")
    
    # If we just set language in this conversation, force refresh contact attrs
    if conv_attrs.get("language_just_set"):
        print(f"🔄 Force refreshing contact attributes after language set")
        contact_attrs = get_contact_attrs(contact_id)  # Refresh
        lang = contact_attrs.get("language", "nl")
        # Clear the flag
        set_conv_attrs(cid, {"language_just_set": False})
    
    # Refresh conv_attrs to get the latest state
    conv_attrs = get_conv_attrs(cid)
    
    print(f"💬 Message from Conv:{cid} Contact:{contact_id} | Lang:{lang} Segment:{segment}")
    print(f"🔍 Contact attrs: {contact_attrs}")
    print(f"🔍 Conv attrs: {conv_attrs}")
    print(f"📝 Content: '{msg_content}'")
    print(f"🎯 Pending intent: {conv_attrs.get('pending_intent', 'none')}")
    
    # Check for admin commands (WIPECONTACTS) - MUST BE FIRST!
    if msg_content.upper() == "WIPECONTACTS":
        print(f"🧹 ADMIN COMMAND: WIPECONTACTS detected from contact {contact_id}")
        
        # Send confirmation message
        send_text_with_duplicate_check(cid, "🧹 *ADMIN COMMAND DETECTED*\n\n⚠️ Je staat op het punt om ALLE contacten en gesprekken te verwijderen!\n\nDit is een gevaarlijke actie die niet ongedaan kan worden gemaakt.\n\nType 'JA WIPE' om te bevestigen of 'ANNULEREN' om te stoppen.")
        
        # Set pending intent for wipe confirmation
        set_conv_attrs(cid, {"pending_intent": "wipe_confirmation"})
        return
    
    # Handle handoff menu selections
    if conv_attrs.get("pending_intent") == "handoff":
        print(f"👨‍🏫 Processing handoff menu selection")
        handle_handoff_menu_selection(cid, contact_id, msg_content, lang)
        return
    
    # Handle language selection (removed numbers to avoid conflicts with menu options)
    if msg_content.lower() in ["🇳🇱 nederlands", "nl", "nederlands", "dutch", "🇳🇱", "lang_nl", "nederlands"] or "🇳🇱" in msg_content:
        print(f"🇳🇱 Language set to Dutch")
        set_contact_attrs(contact_id, {"language": "nl"})
        set_conv_attrs(cid, {"language_just_set": True})
        send_text_with_duplicate_check(cid, t("language_set_nl", "nl"))
        # Force refresh attributes here!
        contact_attrs = get_contact_attrs(contact_id)
        conv_attrs = get_conv_attrs(cid)
        segment = detect_segment(contact_id)
        show_segment_menu(cid, contact_id, segment, "nl")
        return
    
    if msg_content.lower() in ["🇬🇧 english", "english", "engels", "🇬🇧", "lang_en"] or "🇬🇧" in msg_content:
        print(f"🇬🇧 Language set to English")
        set_contact_attrs(contact_id, {"language": "en"})
        set_conv_attrs(cid, {"language_just_set": True})
        send_text_with_duplicate_check(cid, t("language_set_en", "en"))
        # Force refresh attributes here!
        contact_attrs = get_contact_attrs(contact_id)
        conv_attrs = get_conv_attrs(cid)
        segment = detect_segment(contact_id)
        show_segment_menu(cid, contact_id, segment, "en")
        return
    
    # Check if language needs to be prompted (ONLY ONCE per conversation)
    if not contact_attrs.get("language") and not conv_attrs.get("language_prompted"):
        # Auto-detect language from message (ONLY ONCE)
        detected_lang = detect_language_from_message(msg_content)
        print(f"🌍 Auto-detected language (first time): {detected_lang}")
        
        # Set the detected language
        set_contact_attrs(contact_id, {"language": detected_lang})
        set_conv_attrs(cid, {"language_prompted": True, "language_detection_disabled": True})
        
        # Update lang variable for rest of processing
        lang = detected_lang
        print(f"✅ Language set to: {lang} (detection disabled)")
    
    # If language detection is disabled, don't auto-detect anymore
    if conv_attrs.get("language_detection_disabled"):
        print(f"🚫 Language detection disabled - only manual language switching allowed")
    
    # If language is already set, don't ask again
    if contact_attrs.get("language"):
        print(f"✅ Language already set to: {contact_attrs.get('language')}")
        # Continue with normal flow
    
    # Check if this is the first message in the conversation and we have OpenAI available
    # AND we're not already in prefill_confirmation state (to prevent re-processing)
    # AND we haven't already processed this exact message for prefill
    # AND this is not a response to a prefill confirmation
    if (not conv_attrs.get("has_been_prefilled") and 
        not conv_attrs.get("pending_intent") == "prefill_confirmation" and 
        not conv_attrs.get("prefill_processed_for_message") == msg_content and
        not conv_attrs.get("prefill_confirmation_sent") and
        OPENAI_API_KEY):
        # Check if this is a detailed message (not just a greeting)
        # Look for common greeting words and check if there's substantial content beyond that
        greeting_words = ["hallo", "hello", "hi", "hey", "goedemorgen", "goedemiddag", "goedenavond", "good morning", "good afternoon", "good evening"]
        msg_lower = msg_content.lower().strip()
        
        # Check if message contains greeting words (use word boundaries to avoid false matches)
        has_greeting = any(f" {word} " in f" {msg_lower} " for word in greeting_words) or msg_lower in greeting_words
        
        # If it's just a greeting (short message with only greeting words), skip prefill
        if has_greeting and len(msg_content.strip()) < 30:
            print(f"👋 Short greeting detected - skipping prefill, will show bot introduction")
        elif len(msg_content.strip()) >= 30:
            # For longer messages, always do prefill regardless of greeting words
            print(f"📝 Long message detected - proceeding with prefill analysis")
            
            # For detailed messages, detect language first if not already set
            if not contact_attrs.get("language"):
                detected_lang = detect_language_from_message(msg_content)
                print(f"🌍 Auto-detected language for prefill: {detected_lang}")
                set_contact_attrs(contact_id, {"language": detected_lang})
                lang = detected_lang
            else:
                lang = contact_attrs.get("language")
            
            print(f"🤖 Attempting to prefill intake from first message in {lang}...")
            prefilled = prefill_intake_from_message(msg_content, cid)
            
            if prefilled:
                # Apply prefilled information to conversation attributes
                current_attrs = get_conv_attrs(cid)
                current_attrs.update(prefilled)
                current_attrs["has_been_prefilled"] = True
                current_attrs["prefill_processed_for_message"] = msg_content  # Mark this message as processed
                
                # If we created a child contact, also store the child contact ID
                if prefilled.get("child_contact_id"):
                    current_attrs["child_contact_id"] = prefilled["child_contact_id"]
                    print(f"📝 Stored child contact ID {prefilled['child_contact_id']} in conversation attributes")
                
                set_conv_attrs(cid, current_attrs)
                
                # Also set contact attributes if we have a contact
                contact_attrs = get_contact_attrs(contact_id)
                contact_attrs.update(prefilled)
                set_contact_attrs(contact_id, contact_attrs)
                
                # Show user what was detected with comprehensive confirmation
                detected_info = []
                
                # Basic information
                if prefilled.get("learner_name"):
                    detected_info.append(f"👤 *{t('name_label', lang)}*: {prefilled['learner_name']}")
                
                if prefilled.get("school_level"):
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
                    level_text = level_display.get(prefilled['school_level'], prefilled['school_level'])
                    detected_info.append(f"🎓 *{t('level_label', lang)}*: {level_text}")
                
                # Subject information - show only the specific variant if available
                if prefilled.get("topic_secondary"):
                    detected_info.append(f"📚 *{t('subject_label', lang)}*: {prefilled['topic_secondary']}")
                elif prefilled.get("topic_primary"):
                    topic_display = {
                        "math": t("subject_math", lang),
                        "stats": t("subject_stats", lang), 
                        "english": t("subject_english", lang),
                        "programming": t("subject_programming", lang),
                        "science": t("subject_science", lang),
                        "chemistry": t("subject_chemistry", lang)
                    }
                    topic_text = topic_display.get(prefilled['topic_primary'], prefilled['topic_primary'])
                    detected_info.append(f"📚 *{t('subject_label', lang)}*: {topic_text}")
                
                # Additional information
                if prefilled.get("goals"):
                    detected_info.append(f"🎯 *{t('goals_label', lang)}*: {prefilled['goals']}")
                
                if prefilled.get("preferred_times"):
                    detected_info.append(f"⏰ *{t('preferred_times_label', lang)}*: {prefilled['preferred_times']}")
                
                if prefilled.get("location_preference"):
                    detected_info.append(f"📍 *{t('location_preference_label', lang)}*: {prefilled['location_preference']}")
                
                if prefilled.get("contact_name") and prefilled.get("for_who") != "self":
                    detected_info.append(f"👤 *{t('contact_person_label', lang)}*: {prefilled['contact_name']}")
                
                if prefilled.get("for_who"):
                    for_who_display = {
                        "self": t("for_who_self", lang),
                        "child": t("for_who_child", lang),
                        "student": t("for_who_student", lang),
                        "other": t("for_who_other", lang)
                    }
                    for_who_text = for_who_display.get(prefilled['for_who'], prefilled['for_who'])
                    detected_info.append(f"👥 *{t('for_who_label', lang)}*: {for_who_text}")
                
                # Show detected information and ask for confirmation
                if detected_info:
                    # Always show all detected information, don't truncate
                    # This helps users see what was actually detected
                    print(f"📋 Showing {len(detected_info)} detected fields: {[info.split(':')[0] for info in detected_info]}")
                    
                    # Create the summary message
                    summary_msg = f"📋 *Wat ik van je bericht begrepen heb:*\n\n" + "\n".join(detected_info)
                    
                    # Send welcome message first
                    if len(msg_content.strip()) > 30:
                        # Detailed message - use shorter introduction
                        welcome_msg = t("bot_introduction_detailed", lang, detected_lang=lang, other_lang="English" if lang == "nl" else "Nederlands")
                    else:
                        # Short greeting - use full introduction with tip
                        welcome_msg = t("bot_introduction_enhanced", lang, detected_lang=lang, other_lang="English" if lang == "nl" else "Nederlands")
                    
                    # Send welcome without persisting last_bot_message to avoid attribute write during critical flow
                    send_text_with_duplicate_check(cid, welcome_msg, persist=False)
                    
                    # Send the prefill summary without persisting last_bot_message to avoid attribute write during critical flow
                    send_text_with_duplicate_check(cid, summary_msg, persist=False)
                    
                    # 🎯 CRITICAL: Show prefill confirmation menu with interactive buttons
                    # This function sends both the confirmation text AND the menu buttons
                    # It uses send_input_select_only() to ensure proper WhatsApp menu display
                    show_prefill_action_menu(cid, contact_id, lang)
                    
                    # Mark that confirmation was sent and store the original message (best-effort)
                    safe_set_conv_attrs(cid, {
                        "prefill_confirmation_sent": True,
                        "prefill_confirmation_time": datetime.now(TZ).isoformat(),
                        "original_message_processed": msg_content
                    })
                    return
                else:
                    print(f"⚠️ No information detected from prefill - falling back to normal flow")
            else:
                print(f"⚠️ Prefill failed - falling back to normal flow")
        else:
            # For detailed messages, detect language first if not already set
            if not contact_attrs.get("language"):
                detected_lang = detect_language_from_message(msg_content)
                print(f"🌍 Auto-detected language for prefill: {detected_lang}")
                set_contact_attrs(contact_id, {"language": detected_lang})
                lang = detected_lang
            else:
                lang = contact_attrs.get("language")
            
            print(f"🤖 Attempting to prefill intake from first message in {lang}...")
            prefilled = prefill_intake_from_message(msg_content, cid)
            
            if prefilled:
                # Apply prefilled information to conversation attributes
                current_attrs = get_conv_attrs(cid)
                current_attrs.update(prefilled)
                current_attrs["has_been_prefilled"] = True
                current_attrs["prefill_processed_for_message"] = msg_content  # Mark this message as processed
                
                # If we created a child contact, also store the child contact ID
                if prefilled.get("child_contact_id"):
                    current_attrs["child_contact_id"] = prefilled["child_contact_id"]
                    print(f"📝 Stored child contact ID {prefilled['child_contact_id']} in conversation attributes")
                
                set_conv_attrs(cid, current_attrs)
                
                # Also set contact attributes if we have a contact
                contact_attrs = get_contact_attrs(contact_id)
                contact_attrs.update(prefilled)
                set_contact_attrs(contact_id, contact_attrs)
                
                # Show user what was detected with comprehensive confirmation
                detected_info = []
                
                # Basic information
                if prefilled.get("learner_name"):
                    detected_info.append(f"👤 *{t('name_label', lang)}*: {prefilled['learner_name']}")
                
                if prefilled.get("school_level"):
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
                    level_text = level_display.get(prefilled['school_level'], prefilled['school_level'])
                    detected_info.append(f"🎓 *{t('level_label', lang)}*: {level_text}")
                
                # Subject information - show only the specific variant if available
                if prefilled.get("topic_secondary"):
                    detected_info.append(f"📚 *{t('subject_label', lang)}*: {prefilled['topic_secondary']}")
                elif prefilled.get("topic_primary"):
                    topic_display = {
                        "math": t("subject_math", lang),
                        "stats": t("subject_stats", lang), 
                        "english": t("subject_english", lang),
                        "programming": t("subject_programming", lang),
                        "science": t("subject_science", lang),
                        "chemistry": t("subject_chemistry", lang)
                    }
                    topic_text = topic_display.get(prefilled['topic_primary'], prefilled['topic_primary'])
                    detected_info.append(f"📚 *{t('subject_label', lang)}*: {topic_text}")
                
                # Additional information
                if prefilled.get("goals"):
                    detected_info.append(f"🎯 *{t('goals_label', lang)}*: {prefilled['goals']}")
                
                if prefilled.get("preferred_times"):
                    detected_info.append(f"⏰ *{t('preferred_times_label', lang)}*: {prefilled['preferred_times']}")
                
                if prefilled.get("location_preference"):
                    detected_info.append(f"📍 *{t('location_preference_label', lang)}*: {prefilled['location_preference']}")
                
                if prefilled.get("contact_name") and prefilled.get("for_who") != "self":
                    detected_info.append(f"👤 *{t('contact_person_label', lang)}*: {prefilled['contact_name']}")
                
                if prefilled.get("for_who"):
                    for_who_display = {
                        "self": t("for_who_self", lang),
                        "child": t("for_who_child", lang),
                        "student": t("for_who_student", lang),
                        "other": t("for_who_other", lang)
                    }
                    for_who_text = for_who_display.get(prefilled['for_who'], prefilled['for_who'])
                    detected_info.append(f"👥 *{t('for_who_label', lang)}*: {for_who_text}")
                
                # Show detected information and ask for confirmation
                if detected_info:
                    # Always show all detected information, don't truncate
                    # This helps users see what was actually detected
                    print(f"📋 Showing {len(detected_info)} detected fields: {[info.split(':')[0] for info in detected_info]}")
                    
                    # Calculate approximate length of confirmation text
                    base_text = t("prefill_confirmation_header", lang) + "\n\n"
                    footer_text = "\n\n" + t("prefill_confirmation_footer", lang)
                    max_info_length = 1024 - len(base_text) - len(footer_text) - 50  # 50 chars buffer
                    
                    # Only truncate if absolutely necessary
                    if len("\n".join(detected_info)) > max_info_length:
                        truncated_info = []
                        current_length = 0
                        for info in detected_info:
                            if current_length + len(info) + 1 <= max_info_length:  # +1 for newline
                                truncated_info.append(info)
                                current_length += len(info) + 1
                            else:
                                break
                        
                        if len(truncated_info) < len(detected_info):
                            truncated_info.append("...")
                        
                        detected_info = truncated_info
                        print(f"⚠️ Truncated to {len(detected_info)} fields due to length limit")
                    
                    # First send a welcome message - choose based on message type
                    # For detailed messages (prefill), use shorter introduction without tip
                    # For short greetings, use full introduction with tip
                    if len(msg_content.strip()) > 30:
                        # Detailed message - use shorter introduction
                        welcome_msg = t("bot_introduction_detailed", lang, detected_lang=lang, other_lang="English" if lang == "nl" else "Nederlands")
                    else:
                        # Short greeting - use full introduction with tip
                        welcome_msg = t("bot_introduction_enhanced", lang, detected_lang=lang, other_lang="English" if lang == "nl" else "Nederlands")
                    
                    send_text_with_duplicate_check(cid, welcome_msg)
                    
                    # Then show the confirmation menu with interactive buttons
                    # Always use the unified helper to avoid skipping the menu
                    show_prefill_action_menu(cid, contact_id, lang)
                    
                    # Mark that confirmation was sent and store the original message (best-effort)
                    safe_set_conv_attrs(cid, {
                        "prefill_confirmation_sent": True,
                        "prefill_confirmation_time": datetime.now(TZ).isoformat(),
                        "original_message_processed": msg_content
                    })
                    return
                
                print(f"✅ Applied prefill: {list(prefilled.keys())}")
                
                # Refresh attributes after prefill
                contact_attrs = get_contact_attrs(contact_id)
                conv_attrs = get_conv_attrs(cid)
    
    # Handle wipe confirmation
    if conv_attrs.get("pending_intent") == "wipe_confirmation":
        print(f"🧹 Processing wipe confirmation: '{msg_content}'")
        
        if msg_content.upper() in ["JA WIPE", "JA", "YES", "CONFIRM"]:
            print(f"🧹 User confirmed wipe - starting contact deletion...")
            
            # Send status message
            send_text_with_duplicate_check(cid, "🧹 *WIPE GESTART*\n\nBezig met verwijderen van alle contacten en gesprekken...")
            
            try:
                # Import the wipe functionality
                import requests
                
                # Configuration
                CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
                ACC_ID = os.getenv("CW_ACC_ID", "1")
                ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")
                
                if not ADMIN_TOKEN:
                    send_text_with_duplicate_check(cid, "❌ *WIPE FAILED*\n\nADMIN_TOKEN niet geconfigureerd.")
                    set_conv_attrs(cid, {"pending_intent": None})
                    return
                
                headers = {
                    "api_access_token": ADMIN_TOKEN,
                    "Content-Type": "application/json"
                }
                
                # Get all contacts
                url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    send_text_with_duplicate_check(cid, f"❌ *WIPE FAILED*\n\nKon contacten niet ophalen: {response.status_code}")
                    set_conv_attrs(cid, {"pending_intent": None})
                    return
                
                contacts = response.json().get("payload", [])
                print(f"📋 Found {len(contacts)} contacts to delete")
                
                # Delete each contact
                deleted_count = 0
                for contact in contacts:
                    contact_id_to_delete = contact.get("id")
                    if contact_id_to_delete:
                        delete_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts/{contact_id_to_delete}"
                        delete_response = requests.delete(delete_url, headers=headers)
                        
                        if delete_response.status_code == 200:
                            print(f"✅ Deleted contact {contact_id_to_delete}")
                            deleted_count += 1
                        else:
                            print(f"❌ Failed to delete contact {contact_id_to_delete}: {delete_response.status_code}")
                
                # Send completion message
                completion_msg = f"🎉 *WIPE VOLTOOID*\n\n✅ {deleted_count} contacten en gesprekken verwijderd\n\n⚠️ Alle data is permanent verwijderd!"
                send_text_with_duplicate_check(cid, completion_msg)
                
                print(f"🎉 WhatsApp wipe completed: {deleted_count} contacts deleted")
                
            except Exception as e:
                error_msg = f"❌ *WIPE ERROR*\n\nEr is een fout opgetreden: {str(e)}"
                send_text_with_duplicate_check(cid, error_msg)
                print(f"❌ Error during WhatsApp wipe: {e}")
            
            # Clear pending intent
            set_conv_attrs(cid, {"pending_intent": None})
            return
        
        elif msg_content.upper() in ["ANNULEREN", "CANCEL", "NEE", "NO", "STOP"]:
            print(f"🧹 User cancelled wipe")
            send_text_with_duplicate_check(cid, "✅ *WIPE GEANNULEERD*\n\nGeen contacten verwijderd.")
            set_conv_attrs(cid, {"pending_intent": None})
            return
        else:
            print(f"🧹 Invalid wipe confirmation response: '{msg_content}'")
            send_text_with_duplicate_check(cid, "❓ *ONBEKEND ANTWOORD*\n\nType 'JA WIPE' om te bevestigen of 'ANNULEREN' om te stoppen.")
            return
    
    # Handle intake flow
    if conv_attrs.get("pending_intent") == "intake":
        print(f"📋 Processing intake step")
        print(f"🔍 Intake step: {conv_attrs.get('intake_step')}")
        print(f"🔍 Message content: '{msg_content}'")
        print(f"🔍 Full conv_attrs: {conv_attrs}")
        handle_intake_step(cid, contact_id, msg_content, lang)
        return
    else:
        print(f"🔍 Not in intake flow - pending_intent: {conv_attrs.get('pending_intent')}")
    
    # Handle planning flow
    if conv_attrs.get("pending_intent") == "planning":
        print(f"📅 Processing planning selection")
        handle_planning_selection(cid, contact_id, msg_content, lang)
        return
    
    # Handle prefill confirmation
    if conv_attrs.get("pending_intent") == "prefill_confirmation":
        print(f"🤖 Processing prefill confirmation")
        handle_prefill_confirmation(cid, contact_id, msg_content, lang)
        return
    
    # Handle email request for trial lesson
    if conv_attrs.get("pending_intent") == "ask_email":
        print(f"📧 Processing email request")
        handle_email_request(cid, contact_id, msg_content, lang)
        return
    
    # Handle info menu selections
    if conv_attrs.get("pending_intent") == "info_menu":
        print(f"📄 Processing info menu selection")
        handle_info_menu_selection(cid, contact_id, msg_content, lang)
        return
    
    # Handle prefill action selections (after confirmation)
    if conv_attrs.get("pending_intent") == "prefill_action":
        print(f"🎯 Processing prefill action menu selection")
        
        # Handle trial lesson planning
        if msg_content.lower() in ["plan_trial_lesson", "proefles plannen", "plan trial lesson", "1"] or "📅" in msg_content:
            print(f"📅 User wants to plan trial lesson")
            set_conv_attrs(cid, {"pending_intent": ""})
            start_planning_flow(cid, contact_id, lang)
            return
        
        # Handle go to main menu
        if msg_content.lower() in ["go_to_main_menu", "meer informatie", "more information", "2"] or "📋" in msg_content:
            print(f"📋 User wants to go to main menu")
            set_conv_attrs(cid, {"pending_intent": ""})
            show_info_menu(cid, lang)
            return
        
        # Handle handoff
        if msg_content.lower() in ["handoff", "met stephen spreken", "3"] or "👨‍🏫" in msg_content:
            print(f"👨‍🏫 User wants to speak with Stephen")
            set_conv_attrs(cid, {"pending_intent": ""})
            send_handoff_message(cid, t("handoff_teacher", lang))
            return
        
        # If no valid option, show the action menu again
        print(f"❓ Unknown prefill action option: '{msg_content}' - showing action menu again")
        action_menu_title = t("prefill_action_menu_title", lang)
        action_menu_options = [
            (t("prefill_action_trial_lesson", lang), "plan_trial_lesson"),
            (t("prefill_action_main_menu", lang), "go_to_main_menu"),
            (t("prefill_action_handoff", lang), "handoff")
        ]
        send_input_select_only(cid, action_menu_title, action_menu_options)
        return
        print(f"🧹 Processing wipe confirmation: '{msg_content}'")
        
        if msg_content.upper() in ["JA WIPE", "JA", "YES", "CONFIRM"]:
            print(f"🧹 User confirmed wipe - starting contact deletion...")
            
            # Send status message
            send_text_with_duplicate_check(cid, "🧹 *WIPE GESTART*\n\nBezig met verwijderen van alle contacten en gesprekken...")
            
            try:
                # Import the wipe functionality
                import requests
                
                # Configuration
                CW_URL = os.getenv("CW_URL", "https://crm.stephenadei.nl")
                ACC_ID = os.getenv("CW_ACC_ID", "1")
                ADMIN_TOKEN = os.getenv("CW_ADMIN_TOKEN")
                
                if not ADMIN_TOKEN:
                    send_text_with_duplicate_check(cid, "❌ *WIPE FAILED*\n\nADMIN_TOKEN niet geconfigureerd.")
                    set_conv_attrs(cid, {"pending_intent": None})
                    return
                
                headers = {
                    "api_access_token": ADMIN_TOKEN,
                    "Content-Type": "application/json"
                }
                
                # Get all contacts
                url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    send_text_with_duplicate_check(cid, f"❌ *WIPE FAILED*\n\nKon contacten niet ophalen: {response.status_code}")
                    set_conv_attrs(cid, {"pending_intent": None})
                    return
                
                contacts = response.json().get("payload", [])
                print(f"📋 Found {len(contacts)} contacts to delete")
                
                # Delete each contact
                deleted_count = 0
                for contact in contacts:
                    contact_id_to_delete = contact.get("id")
                    if contact_id_to_delete:
                        delete_url = f"{CW_URL}/api/v1/accounts/{ACC_ID}/contacts/{contact_id_to_delete}"
                        delete_response = requests.delete(delete_url, headers=headers)
                        
                        if delete_response.status_code == 200:
                            print(f"✅ Deleted contact {contact_id_to_delete}")
                            deleted_count += 1
                        else:
                            print(f"❌ Failed to delete contact {contact_id_to_delete}: {delete_response.status_code}")
                
                # Send completion message
                completion_msg = f"🎉 *WIPE VOLTOOID*\n\n✅ {deleted_count} contacten en gesprekken verwijderd\n\n⚠️ Alle data is permanent verwijderd!"
                send_text_with_duplicate_check(cid, completion_msg)
                
                print(f"🎉 WhatsApp wipe completed: {deleted_count} contacts deleted")
                
            except Exception as e:
                error_msg = f"❌ *WIPE ERROR*\n\nEr is een fout opgetreden: {str(e)}"
                send_text_with_duplicate_check(cid, error_msg)
                print(f"❌ Error during WhatsApp wipe: {e}")
            
            # Clear pending intent
            set_conv_attrs(cid, {"pending_intent": None})
            return
        
        elif msg_content.upper() in ["ANNULEREN", "CANCEL", "NEE", "NO", "STOP"]:
            print(f"🧹 User cancelled wipe")
            send_text_with_duplicate_check(cid, "✅ *WIPE GEANNULEERD*\n\nGeen contacten verwijderd.")
            set_conv_attrs(cid, {"pending_intent": None})
            return
        else:
            print(f"🧹 Invalid wipe confirmation response: '{msg_content}'")
            send_text_with_duplicate_check(cid, "❓ *ONBEKEND ANTWOORD*\n\nType 'JA WIPE' om te bevestigen of 'ANNULEREN' om te stoppen.")
            return
    
    # Check if this is a general greeting or unclear message
    # If no pending intent and message doesn't match any menu options, show the bot introduction
    # Only do this if we haven't already processed prefill and no language is set
    if not conv_attrs.get("pending_intent") and not conv_attrs.get("has_been_prefilled") and not contact_attrs.get("language"):
        # Check if this looks like a general greeting or unclear message
        greeting_words = ["hallo", "hello", "hi", "hey", "goedemorgen", "goedemiddag", "goedenavond", "good morning", "good afternoon", "good evening"]
        msg_lower = msg_content.lower().strip()
        
        # Check if this is just a greeting (short message with only greeting words)
        # Use word boundaries to avoid false matches (e.g., "how" containing "hi")
        has_greeting = any(f" {word} " in f" {msg_lower} " for word in greeting_words) or msg_lower in greeting_words
        is_short_message = len(msg_content.strip()) < 30
        
        if has_greeting and is_short_message:
            print(f"👋 Short greeting detected - showing segment menu")
            
            # Detect language from the message
            detected_lang = detect_language_from_message(msg_content)
            print(f"🌍 Detected language: {detected_lang}")
            
            # Set the detected language as contact attribute
            set_contact_attrs(contact_id, {"language": detected_lang})
            
            # Send bot introduction
            welcome_msg = t("bot_introduction_enhanced", detected_lang, detected_lang=detected_lang, other_lang="English" if detected_lang == "nl" else "Nederlands")
            send_text_with_duplicate_check(cid, welcome_msg)
            
            # Show segment menu for short greetings (like normal flow)
            segment = detect_segment(contact_id)
            show_segment_menu(cid, contact_id, segment, detected_lang)
            return
    
    # Only handle menu selection if we've already shown a menu to the user
    # This prevents treating the first message as a menu selection
    if conv_attrs.get("menu_shown") or conv_attrs.get("pending_intent"):
        print(f"🔘 Handling menu selection for existing conversation")
        handle_menu_selection(cid, contact_id, msg_content, lang)

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

def handle_prefill_confirmation(cid, contact_id, msg_content, lang):
    """Handle prefill confirmation from user"""
    print(f"🤖 Prefill confirmation: '{msg_content}'")
    
    # Check if this is the original message being re-processed
    conv_attrs = get_conv_attrs(cid)
    original_message = conv_attrs.get("original_message_processed", "")
    
    if msg_content == original_message:
        print(f"🔄 Original message detected in prefill confirmation - skipping")
        return
    
    # Update last_processed_message to the user's response and clear prefill tracking
    set_conv_attrs(cid, {
        "last_processed_message": msg_content,
        "prefill_processed_for_message": "",  # Clear so we can process new messages
        "prefill_confirmation_sent": False,   # Clear confirmation sent flag
        "original_message_processed": ""      # Clear original message flag
    })
    
    # Check user's response - improved recognition
    print(f"🔍 Analyzing prefill confirmation response: '{msg_content}'")
    
    # More comprehensive confirmation detection
    confirm_words = ["ja", "klopt", "correct", "yes", "✅", "ja dat klopt", "dat klopt", "klopt helemaal", "ja helemaal", "correct", "juist", "precies", "inderdaad"]
    deny_words = ["nee", "niet", "fout", "no", "❌", "nee dat klopt niet", "dat klopt niet", "niet correct", "fout", "verkeerd"]
    partial_words = ["deels", "sommige", "partially", "🤔", "deels correct", "sommige kloppen", "niet alles"]
    
    msg_lower = msg_content.lower().strip()
    
    if msg_content == "confirm_all" or any(word in msg_lower for word in confirm_words):
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
            current_contact_attrs.update(prefilled_info)
            
            # If this is for themselves and we have a learner name, set it as the contact name
            for_who = prefilled_info.get("for_who", "self")
            learner_name = prefilled_info.get("learner_name", "")
            if for_who == "self" and learner_name:
                current_contact_attrs["name"] = learner_name
                current_contact_attrs["is_student"] = True
                print(f"✅ Set contact name to learner name: {learner_name}")
            
            set_contact_attrs(contact_id, current_contact_attrs)
            print(f"✅ Applied prefilled info to contact: {list(prefilled_info.keys())}")
        
        # Create child contact if this is a parent writing for their child
        if prefilled_info.get("for_who") == "child" and prefilled_info.get("learner_name"):
            child_contact_id = create_child_contact(prefilled_info, cid)
            if child_contact_id:
                prefilled_info["child_contact_id"] = child_contact_id
                print(f"👶 Created child contact: {child_contact_id} for {prefilled_info['learner_name']}")
                # Update contact attributes with child contact ID
                current_contact_attrs["child_contact_id"] = child_contact_id
                set_contact_attrs(contact_id, current_contact_attrs)
        
        # Use smart extraction check to determine flow
        smart_check_result = smart_extraction_check(prefilled_info)
        
        # 1. Detect and set segment
        detected_segment = detect_segment(contact_id)
        print(f"🎯 Detected segment: {detected_segment}")
        
        # 2. Set planning profile based on segment
        set_conv_attrs(cid, {"planning_profile": detected_segment})
        
        # 3. Set appropriate labels based on extracted information
        labels_to_add = []
        
        # Audience label based on school_level
        school_level = prefilled_info.get("school_level", "")
        if school_level:
            audience_mapping = {
                "po": "audience_po",
                "vmbo": "audience_vmbo", 
                "havo": "audience_havo",
                "vwo": "audience_vwo",
                "mbo": "audience_mbo",
                "university_wo": "audience_university_wo",
                "university_hbo": "audience_university_hbo",
                "adult": "audience_adult"
            }
            audience_label = audience_mapping.get(school_level)
            if audience_label:
                labels_to_add.append(audience_label)
        
        # Subject label based on topic_primary
        topic_primary = prefilled_info.get("topic_primary", "")
        if topic_primary:
            subject_mapping = {
                "math": "subject_math",
                "stats": "subject_stats",
                "science": "subject_science", 
                "english": "subject_english",
                "programming": "subject_programming"
            }
            subject_label = subject_mapping.get(topic_primary)
            if subject_label:
                labels_to_add.append(subject_label)
        
        # Service label for trial lesson
        labels_to_add.append("service_trial")
        
        # Source label
        labels_to_add.append("source_whatsapp")
        
        # Add all labels
        if labels_to_add:
            add_conv_labels(cid, labels_to_add)
            print(f"🏷️ Added labels: {labels_to_add}")
        
        # 4. Set customer status attributes
        from datetime import datetime
        current_time = datetime.now().isoformat()
        
        # Set customer_since if this is their first interaction
        if not current_contact_attrs.get("customer_since"):
            current_contact_attrs["customer_since"] = current_time
        
        # Set has_completed_intake
        current_contact_attrs["has_completed_intake"] = True
        
        # Update contact attributes
        set_contact_attrs(contact_id, current_contact_attrs)
        print(f"✅ Updated customer status attributes")
        
        # Mark that prefill has been confirmed
        set_conv_attrs(cid, {
            "prefill_confirmation_sent": True,
            "prefill_confirmation_time": datetime.now(TZ).isoformat(),
            "use_prefill": True  # Flag to use prefill in planning flow
        })
        
        # Check if we have sufficient information for a trial lesson
        if is_prefill_sufficient_for_trial_lesson(prefilled_info):
            # We have good information, proceed directly to trial lesson planning
            contact_name = prefilled_info.get("contact_name", "")
            learner_name = prefilled_info.get("learner_name", "")
            topic = prefilled_info.get("topic_secondary", "")
            
            print(f"🔍 Debug greeting: contact_name='{contact_name}', for_who='{prefilled_info.get('for_who')}', learner_name='{learner_name}'")
            
            if contact_name and prefilled_info.get("for_who") == "child":
                # Parent writing for child - use parent's name
                confirmation_msg = f"Perfect {contact_name}! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                print(f"✅ Using contact_name: {contact_name}")
            elif learner_name:
                # Student writing for themselves - use their name
                confirmation_msg = f"Perfect {learner_name}! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                print(f"✅ Using learner_name: {learner_name}")
            else:
                confirmation_msg = f"Perfect! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                print(f"✅ Using generic greeting")
            
            send_text_with_duplicate_check(cid, confirmation_msg)
            
            # Clear pending intent and go directly to planning flow
            set_conv_attrs(cid, {"pending_intent": ""})
            start_planning_flow(cid, contact_id, lang)
        else:
            # Not enough information, show action menu to get more info
            print(f"🎯 Not enough info for trial lesson - showing action menu")
            show_prefill_action_menu_after_confirmation(cid, contact_id, lang)

    
    elif msg_content == "correct_all" or any(word in msg_lower for word in deny_words):
        print(f"❌ User indicates information is incorrect - initiating immediate handoff to Stephen")
        # Immediate handoff to Stephen
        handoff_text = t("handoff_teacher", lang)
        send_handoff_message(cid, handoff_text)
        # Set pending intent to handoff
        safe_set_conv_attrs(cid, {"pending_intent": "handoff"})
        
    elif msg_content == "correct_partial" or any(word in msg_lower for word in partial_words):
        print(f"🤔 User indicates information is only partially correct - initiating immediate handoff to Stephen")
        # Immediate handoff as well (treat partial as not correct)
        handoff_text = t("handoff_teacher", lang)
        send_handoff_message(cid, handoff_text)
        safe_set_conv_attrs(cid, {"pending_intent": "handoff"})
        
    else:
        # Unclear response, check if this is a repeat attempt
        conv_attrs = get_conv_attrs(cid)
        unclear_count = conv_attrs.get("prefill_unclear_count", 0)
        
        if unclear_count >= 2:
            # After 2 unclear responses, proceed with prefill anyway
            print(f"⚠️ Multiple unclear responses ({unclear_count}), proceeding with prefill")
            send_text_with_duplicate_check(cid, t("prefill_assume_correct", lang))
            
            # Clear the unclear count and proceed with confirmation
            set_conv_attrs(cid, {"prefill_unclear_count": 0})
            
            # Simulate a confirmation by calling the confirmation logic
            # Get the prefilled information and apply it
            prefilled_info = {}
            if conv_attrs.get("learner_name"):
                prefilled_info["learner_name"] = conv_attrs["learner_name"]
            if conv_attrs.get("school_level"):
                prefilled_info["school_level"] = conv_attrs["school_level"]
            if conv_attrs.get("topic_primary"):
                prefilled_info["topic_primary"] = conv_attrs["topic_primary"]
            if conv_attrs.get("topic_secondary"):
                prefilled_info["topic_secondary"] = conv_attrs["topic_secondary"]
            if conv_attrs.get("goals"):
                prefilled_info["goals"] = conv_attrs["goals"]
            if conv_attrs.get("referral_source"):
                prefilled_info["referral_source"] = conv_attrs["referral_source"]
            if conv_attrs.get("is_adult") is not None:
                prefilled_info["is_adult"] = conv_attrs["is_adult"]
            if conv_attrs.get("for_who"):
                prefilled_info["for_who"] = conv_attrs["for_who"]
            
            # Apply prefilled information to contact attributes
            if prefilled_info:
                current_contact_attrs = get_contact_attrs(contact_id)
                current_contact_attrs.update(prefilled_info)
                
                # If this is for themselves and we have a learner name, set it as the contact name
                for_who = prefilled_info.get("for_who", "self")
                learner_name = prefilled_info.get("learner_name", "")
                if for_who == "self" and learner_name:
                    current_contact_attrs["name"] = learner_name
                    current_contact_attrs["is_student"] = True
                    print(f"✅ Set contact name to learner name: {learner_name}")
                
                set_contact_attrs(contact_id, current_contact_attrs)
                print(f"✅ Applied prefilled info to contact: {list(prefilled_info.keys())}")
            
            # Check if we have sufficient information for a trial lesson
            if is_prefill_sufficient_for_trial_lesson(prefilled_info):
                # We have good information, proceed to trial lesson planning
                contact_name = prefilled_info.get("contact_name", "")
                learner_name = prefilled_info.get("learner_name", "")
                topic = prefilled_info.get("topic_secondary", "")
                
                print(f"🔍 Debug greeting: contact_name='{contact_name}', for_who='{prefilled_info.get('for_who')}', learner_name='{learner_name}'")
                
                if contact_name and prefilled_info.get("for_who") == "child":
                    # Parent writing for child - use parent's name
                    confirmation_msg = f"Perfect {contact_name}! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                    print(f"✅ Using contact_name: {contact_name}")
                elif learner_name:
                    # Student writing for themselves - use their name
                    confirmation_msg = f"Perfect {learner_name}! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                    print(f"✅ Using learner_name: {learner_name}")
                else:
                    confirmation_msg = f"Perfect! Ik zie dat je hulp zoekt met {topic}. Laten we direct een gratis proefles inplannen zodat je kunt ervaren hoe ik je kan helpen."
                    print(f"✅ Using generic greeting")
                
                send_text_with_duplicate_check(cid, confirmation_msg)
                
                # Clear pending intent and go to planning flow
                set_conv_attrs(cid, {"pending_intent": ""})
                
                # Start planning flow directly
                start_planning_flow(cid, contact_id, lang)
                
            else:
                # Information is incomplete, go to main menu
                learner_name = prefilled_info.get("learner_name", "")
                if learner_name:
                    confirmation_msg = f"Bedankt {learner_name}! Ik heb een deel van je informatie kunnen verwerken.\n\n{t('general_greeting_tip', lang)}\n\nLaten we verder gaan met de intake om alles goed in te vullen."
                else:
                    confirmation_msg = f"Bedankt! Ik heb een deel van je informatie kunnen verwerken.\n\n{t('general_greeting_tip', lang)}\n\nLaten we verder gaan met de intake om alles goed in te vullen."
                
                send_text_with_duplicate_check(cid, confirmation_msg)
                
                # Clear pending intent and go to main menu
                set_conv_attrs(cid, {"pending_intent": ""})
                
                # Show main menu
                show_info_menu(cid, lang)
        else:
            # First or second unclear response, ask for clarification with interactive menu
            print(f"❓ Unclear prefill confirmation response (attempt {unclear_count + 1})")
            set_conv_attrs(cid, {"prefill_unclear_count": unclear_count + 1})
            
            # Send interactive menu for clarification
            send_input_select_only(cid, "❓ Sorry, ik begrijp je antwoord niet helemaal. Kun je kiezen uit:", [
                (t("prefill_confirm_all", lang), "confirm_all"),
                (t("prefill_correct_all", lang), "correct_all"),
                (t("prefill_correct_partial", lang), "correct_partial")
            ])

def handle_info_menu_selection(cid, contact_id, msg_content, lang):
    """Handle info menu selections"""
    print(f"📄 Info menu selection: '{msg_content}'")
    
    # Handle lesson planning
    if msg_content.lower() in ["plan_lesson", "les inplannen", "1"] or "📅" in msg_content:
        print(f"📅 Lesson planning requested from info menu")
        start_planning_flow(cid, contact_id, lang)
        return
    
    # Handle greetings first
    greeting_words = ["hi", "hello", "hey", "hallo", "hoi", "goedemorgen", "goedemiddag", "goedenavond", "good morning", "good afternoon", "good evening"]
    if msg_content.lower().strip() in greeting_words:
        print(f"👋 Greeting detected: '{msg_content}'")
        greeting_msg = t("greeting_response", lang)
        send_text_with_duplicate_check(cid, greeting_msg)
        return
    
    # Smart analysis for free text questions
    # If the message doesn't match any menu options, try to analyze it as a question
    if not any([
        msg_content.lower() in ["tariffs", "tarieven", "2"] or "💰" in msg_content,
        msg_content.lower() in ["work_method", "werkwijze", "3"] or "🎯" in msg_content,
        msg_content.lower() in ["services", "diensten", "4"] or "📚" in msg_content,
        msg_content.lower() in ["travel_costs", "reiskosten", "5"] or "🚗" in msg_content,
        msg_content.lower() in ["last_minute", "last-minute", "6"] or "⏰" in msg_content,
        msg_content.lower() in ["conditions", "voorwaarden", "7"] or "📋" in msg_content,
        msg_content.lower() in ["weekend_programs", "weekend programma's", "8"] or "🌅" in msg_content,
        msg_content.lower() in ["short_version", "korte versie", "9"] or "📝" in msg_content,
        msg_content.lower() in ["personal_background", "persoonlijke achtergrond", "11"] or "👨‍🏫 persoonlijke" in msg_content.lower(),
        msg_content.lower() in ["didactic_methods", "didactische methoden", "12"] or "📚 didactische" in msg_content.lower(),
        msg_content.lower() in ["technology_tools", "technologie tools", "13"] or "💻 technologie" in msg_content.lower(),
        msg_content.lower() in ["results_success", "resultaten succes", "14"] or "🏆 resultaten" in msg_content.lower(),
        msg_content.lower() in ["workshops_creative", "creatieve workshops", "15"] or "🎨 creatieve" in msg_content.lower(),
        msg_content.lower() in ["workshops_academic", "academische workshops", "16"] or "🎓 academische" in msg_content.lower(),
        msg_content.lower() in ["consultancy", "advies", "17"] or "💼 consultancy" in msg_content.lower(),
        msg_content.lower() in ["back_to_main", "terug naar hoofdmenu", "0"] or "⬅️" in msg_content
    ]):
        print(f"🤖 Analyzing free text question: '{msg_content}'")
        
        # Use OpenAI to analyze the question
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
                    send_text_with_duplicate_check(cid, t("info_tariffs", lang))
                    show_info_follow_up_menu(cid, contact_id, lang)
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
            
            # If confidence is low or no category found, try FAQ handler
            print(f"❓ Low confidence or no category found, trying FAQ handler")
            if handle_faq_request(cid, contact_id, msg_content, lang):
                return
            else:
                # If FAQ handler also didn't match, show the menu again
                send_text_with_duplicate_check(cid, t("error_unclear_question", lang))
                show_info_menu(cid, lang)
                return
    
    # Handle tariffs
    if msg_content.lower() in ["tariffs", "tarieven", "2"] or "💰" in msg_content:
        print(f"💰 Showing tariffs")
        send_text_with_duplicate_check(cid, t("info_tariffs", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle work method
    if msg_content.lower() in ["work_method", "werkwijze", "3"] or "🎯" in msg_content:
        print(f"🎯 Showing work method")
        send_text_with_duplicate_check(cid, t("info_work_method", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle services
    if msg_content.lower() in ["services", "diensten", "4"] or "📚" in msg_content:
        print(f"📚 Showing services")
        send_text_with_duplicate_check(cid, t("info_services", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle how lessons work
    if (msg_content.lower() in ["how_lessons_work", "how lessons work", "hoe lessen werken", "5"] or 
        "📚 hoe lessen" in msg_content.lower() or
        "how do lessons work" in msg_content.lower() or
        "hoe werken lessen" in msg_content.lower()):
        print(f"📚 Showing how lessons work")
        send_text_with_duplicate_check(cid, t("info_how_lessons_work", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle travel costs
    if msg_content.lower() in ["travel_costs", "reiskosten", "6"] or "🚗" in msg_content:
        print(f"🚗 Showing travel costs")
        send_text_with_duplicate_check(cid, t("info_travel_costs", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle last-minute
    if msg_content.lower() in ["last_minute", "last-minute", "7"] or "⏰" in msg_content:
        print(f"⏰ Showing last-minute surcharges")
        send_text_with_duplicate_check(cid, t("info_last_minute", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle conditions
    if msg_content.lower() in ["conditions", "voorwaarden", "8"] or "📋" in msg_content:
        print(f"📋 Showing conditions")
        send_text_with_duplicate_check(cid, t("info_conditions", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle weekend programs
    if msg_content.lower() in ["weekend_programs", "weekend programma's", "9"] or "🌅" in msg_content:
        print(f"🌅 Showing weekend programs")
        send_text_with_duplicate_check(cid, t("info_weekend_programs", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle short version
    if msg_content.lower() in ["short_version", "korte versie", "10"] or "📝" in msg_content:
        print(f"📝 Showing short version")
        send_text_with_duplicate_check(cid, t("info_short_version", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle personal background
    if msg_content.lower() in ["personal_background", "persoonlijke achtergrond", "11"] or "👨‍🏫 persoonlijke" in msg_content.lower():
        print(f"👨‍🏫 Showing personal background")
        send_text_with_duplicate_check(cid, t("info_personal_background", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle didactic methods
    if msg_content.lower() in ["didactic_methods", "didactische methoden", "12"] or "📚 didactische" in msg_content.lower():
        print(f"📚 Showing didactic methods")
        send_text_with_duplicate_check(cid, t("info_didactic_methods", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle technology tools
    if msg_content.lower() in ["technology_tools", "technologie tools", "13"] or "💻 technologie" in msg_content.lower():
        print(f"💻 Showing technology tools")
        send_text_with_duplicate_check(cid, t("info_technology_tools", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle results success
    if msg_content.lower() in ["results_success", "resultaten succes", "14"] or "🏆 resultaten" in msg_content.lower():
        print(f"🏆 Showing results and success")
        send_text_with_duplicate_check(cid, t("info_results_success", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle creative workshops
    if msg_content.lower() in ["workshops_creative", "creatieve workshops", "15"] or "🎨 creatieve" in msg_content.lower():
        print(f"🎨 Showing creative workshops")
        send_text_with_duplicate_check(cid, t("info_workshops_creative", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle academic workshops
    if msg_content.lower() in ["workshops_academic", "academische workshops", "16"] or "🎓 academische" in msg_content.lower():
        print(f"🎓 Showing academic workshops")
        send_text_with_duplicate_check(cid, t("info_workshops_academic", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle consultancy
    if msg_content.lower() in ["consultancy", "advies", "17"] or "💼 consultancy" in msg_content.lower():
        print(f"💼 Showing consultancy")
        send_text_with_duplicate_check(cid, t("info_consultancy", lang))
        show_info_follow_up_menu(cid, contact_id, lang)
        return
    
    # Handle back to main info menu
    if msg_content.lower() in ["back_to_main_info", "terug naar hoofdmenu", "⬅️"] or "⬅️ terug" in msg_content.lower():
        print(f"⬅️ Returning to main info menu")
        show_info_menu(cid, lang)
        return
    
    # Handle more info
    if msg_content.lower() in ["more_info", "meer informatie", "📖"] or "📖 meer" in msg_content.lower():
        print(f"📖 Showing detailed info menu")
        show_detailed_info_menu(cid, lang)
        return
    
    # Handle handoff
    if msg_content.lower() in ["handoff", "stephen spreken", "10"] or "👨‍🏫" in msg_content:
        print(f"👨‍🏫 Handoff to Stephen requested")
        send_handoff_message(cid, t("handoff_teacher", lang))
        return
    
    # If no valid option, show the info menu again
    print(f"❓ Unknown info menu option: '{msg_content}' - showing info menu")
    show_info_menu(cid, lang)

def show_prefill_action_menu(cid, contact_id, lang):
    """
    🎯 CRITICAL FLOW: Show confirmation menu asking user if the extracted information is correct
    
    This function is the PRIMARY entry point for prefill confirmation flow.
    It sends:
    1. A confirmation question text message
    2. An input_select menu with confirmation options
    
    FLOW: User sends message → OpenAI extracts info → This function shows confirmation menu
    → User confirms → show_prefill_action_menu_after_confirmation() is called
    
    IMPORTANT: This function MUST use send_input_select_only() to ensure the menu appears
    correctly in WhatsApp. Direct text messages don't show interactive buttons.
    """
    print(f"🎯 Showing prefill confirmation menu in {lang}")
    
    try:
        set_conv_attrs(cid, {"pending_intent": "prefill_confirmation"})
    except Exception as e:
        print(f"⚠️ SSL error setting pending_intent: {e}")
        # Continue anyway - not critical
    
    # Step 1: Send the confirmation question as text (do not persist to avoid conv-attr write here)
    confirmation_text = t("prefill_confirmation_question", lang)
    try:
        send_text_with_duplicate_check(cid, confirmation_text, persist=False)
        print(f"✅ Confirmation question sent successfully")
    except Exception as e:
        print(f"⚠️ Failed to send confirmation question: {e}")
        # Continue anyway - the menu buttons are more important
    
    # Step 2: Send the confirmation menu using input_select (CRITICAL FOR MENU BUTTONS)
    menu_title = t("prefill_confirmation_menu_title", lang)
    menu_options = [
        (t("prefill_confirm_all", lang), "confirm_all"),
        (t("prefill_correct_all", lang), "correct_all"),
        (t("prefill_correct_partial", lang), "correct_partial")
    ]
    
    # CRITICAL: Use input_select_only for WhatsApp menu buttons
    # This ensures the menu appears as interactive buttons, not just text
    try:
        result = send_input_select_only(cid, menu_title, menu_options)
        print(f"🎯 Prefill confirmation menu send result: {result}")
    except Exception as e:
        print(f"❌ Failed to send confirmation menu: {e}")
        # Fallback: send as text with options
        fallback_text = f"{menu_title}\n\n" + "\n".join([f"• {option[0]}" for option in menu_options])
        send_text_with_duplicate_check(cid, fallback_text, persist=False)
        print(f"📝 Sent fallback text menu due to input_select failure")

def show_prefill_action_menu_after_confirmation(cid, contact_id, lang):
    """Show action menu after prefill confirmation - what does user want to do next?"""
    print(f"🎯 Showing prefill action menu after confirmation in {lang}")
    
    # Get contact attributes to determine age and show appropriate tariffs
    contact_attrs = get_contact_attrs(contact_id)
    conv_attrs = get_conv_attrs(cid)
    
    # Only show tariffs if we have sufficient information about age/level
    # Don't show tariffs for simple greetings like "Hello Stephen, i found you online"
    is_adult = contact_attrs.get('is_adult', False)
    school_level = contact_attrs.get('school_level', '')
    learner_name = contact_attrs.get('learner_name', '')
    topic = contact_attrs.get('topic_primary', '') or contact_attrs.get('topic_secondary', '')
    
    # Check if we have meaningful information beyond just "for_who"
    # We need to check if any meaningful information was actually detected
    has_meaningful_info = (
        school_level or          # Has school level
        learner_name or          # Has name
        topic                    # Has subject
    )
    
    # Only consider is_adult if it was explicitly set (not the default False)
    # We can't easily detect if it was explicitly set, so we'll rely on other fields
    
    if has_meaningful_info:
        # Show appropriate tariffs based on age/level
        if is_adult or 'university' in school_level.lower() or 'hbo' in school_level.lower():
            # Over 20 or higher education
            print(f"💰 Showing tariffs for over 20/higher education")
            send_text_with_duplicate_check(cid, t("info_tariffs_over_20", lang))
        else:
            # Under 20 or secondary education
            print(f"💰 Showing tariffs for under 20/secondary education")
            send_text_with_duplicate_check(cid, t("info_tariffs_under_20", lang))
    else:
        print(f"💰 Skipping tariffs - insufficient information detected (simple greeting)")
    
    # Check if they have completed a trial lesson (this is the key criteria)
    has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
    
    # For new customers, check if preferences are still current (only if significant time has passed)
    if not has_completed_trial:
        preferred_times = contact_attrs.get("preferred_times", "")
        location_preference = contact_attrs.get("location_preference", "")
        
        # Check if preferences were recently confirmed (within last hour)
        prefill_confirmation_time = conv_attrs.get("prefill_confirmation_time", "")
        current_time = datetime.now(TZ)
        
        if prefill_confirmation_time:
            try:
                confirmation_dt = datetime.fromisoformat(prefill_confirmation_time.replace('Z', '+00:00'))
                time_diff = current_time - confirmation_dt
                
                # Only check preferences if more than 1 hour has passed
                if time_diff.total_seconds() < 3600:  # 1 hour = 3600 seconds
                    print(f"⏰ Preferences recently confirmed ({time_diff.total_seconds()/60:.1f} minutes ago) - skipping check")
                else:
                    print(f"⏰ Preferences confirmed {time_diff.total_seconds()/3600:.1f} hours ago - checking if still current")
                    if preferred_times and location_preference:
                        # Show current preferences and ask if they're still correct
                        preferences_msg = t("preferences_share_current", lang, 
                                          preferred_times=preferred_times, 
                                          location_preference=location_preference)
                        send_text_with_duplicate_check(cid, preferences_msg)
                        
                        # Show preferences check menu
                        preferences_options = [
                            (t("preferences_check_yes", lang), "preferences_same"),
                            (t("preferences_check_no", lang), "preferences_changed")
                        ]
                        
                        set_conv_attrs(cid, {"pending_intent": "preferences_check"})
                        send_input_select_only(cid, t("preferences_check_title", lang), preferences_options)
                        return
            except Exception as e:
                print(f"⚠️ Error checking prefill confirmation time: {e}")
                # Continue without preferences check if there's an error
        else:
            print(f"⏰ No prefill confirmation time found - skipping preferences check")
    
    # Send explanation text first
    explanation_text = t("prefill_action_menu_text", lang)
    send_text_with_duplicate_check(cid, explanation_text, persist=False)
    
    # Send appropriate menu based on trial completion
    action_menu_title = t("prefill_action_menu_title", lang)
    
    if has_completed_trial:
        # Customers who completed trial get the option to plan all lessons
        action_menu_options = [
            (t("prefill_action_all_lessons", lang), "plan_all_lessons"),
            (t("prefill_action_trial_first", lang), "plan_trial_lesson"),
            (t("prefill_action_main_menu", lang), "go_to_main_menu"),
            (t("prefill_action_handoff", lang), "handoff")
        ]
    else:
        # All customers without trial get trial lesson and urgent session options
        action_menu_options = [
            (t("prefill_action_trial_first", lang), "plan_trial_lesson"),
            (t("prefill_action_urgent_session", lang), "urgent_session"),
            (t("prefill_action_main_menu", lang), "go_to_main_menu"),
            (t("prefill_action_handoff", lang), "handoff")
        ]
    
    print(f"🎯 Action menu title: '{action_menu_title}'")
    print(f"🎯 Action menu options: {action_menu_options}")
    print(f"🎯 Customer type: {'with trial' if has_completed_trial else 'without trial'}")
    
    try:
        set_conv_attrs(cid, {"pending_intent": "prefill_action"})
    except Exception as e:
        print(f"⚠️ SSL error setting pending_intent: {e}")
        # Continue anyway - not critical
    
    # Use input_select_only for consistent menu formatting
    result = send_input_select_only(cid, action_menu_title, action_menu_options)
    print(f"🎯 Menu send result: {result}")



def show_info_follow_up_menu(cid, contact_id, lang):
    """Show follow-up menu after displaying information"""
    print(f"📄 Showing info follow-up menu in {lang}")
    set_conv_attrs(cid, {"pending_intent": "info_follow_up"})
    
    # Get contact attributes to check if they have completed a trial lesson
    contact_attrs = get_contact_attrs(contact_id)
    has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
    
    if has_completed_trial:
        # Customers who completed trial get plan lesson option
        send_input_select_only(cid, t("info_follow_up_existing", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_more_info", lang), "more_info"),
            (t("menu_option_handoff", lang), "handoff"),
            (t("menu_back_to_main", lang), "back_to_main")
        ])
    else:
        # Customers without trial get trial lesson option
        send_input_select_only(cid, t("info_follow_up_new", lang), [
            (t("menu_option_trial_lesson", lang), "trial_lesson"),
            (t("menu_more_info", lang), "more_info"),
            (t("menu_option_handoff", lang), "handoff"),
            (t("menu_back_to_main", lang), "back_to_main")
        ])

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
        assign_conversation(cid, 1)  # Bot user_id=1
        
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

def show_segment_menu(cid, contact_id, segment, lang):
    """Show appropriate menu based on segment"""
    print(f"📋 Showing {segment} menu in {lang}")
    
    # Check if we have a name and greet the client
    contact_attrs = get_contact_attrs(contact_id)
    print(f"🔍 Contact attrs in show_segment_menu: {contact_attrs}")
    contact_name = contact_attrs.get("name", "")
    print(f"🔍 Contact name found: {contact_name}")
    
    # Re-detect segment to ensure we have the latest status
    current_segment = detect_segment(contact_id)
    if current_segment != segment:
        print(f"🔄 Segment changed from {segment} to {current_segment}")
        segment = current_segment
        set_contact_attrs(contact_id, {"segment": segment})
    
    if contact_name:
        # Extract first name from full name
        first_name = contact_name.split()[0] if contact_name else ""
        if first_name:
            greeting = t("greeting_with_name", lang).format(name=first_name)
            print(f"👋 Greeting client: {first_name}")
            send_text_with_duplicate_check(cid, greeting)
    
    # Send the menu immediately
    print(f"📋 Sending menu for {segment} segment")
    
    # Set menu_shown flag to indicate we've shown a menu to the user
    set_conv_attrs(cid, {"menu_shown": True})
    
    if segment == "new":
        send_input_select_only(cid, t("menu_new", lang), [
            (t("menu_option_trial_lesson", lang), "plan_lesson"),
            (t("menu_option_info", lang), "info"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "existing":
        send_input_select_only(cid, t("menu_existing", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_same_preferences", lang), "same_preferences"),
            (t("menu_option_different", lang), "different"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "returning_broadcast":
        send_input_select_only(cid, t("menu_returning_broadcast", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_old_preferences", lang), "old_preferences"),
            (t("menu_option_new_intake", lang), "new_intake"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "weekend":
        send_input_select_only(cid, t("menu_weekend", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_info", lang), "info"),
            (t("menu_option_handoff", lang), "handoff")
        ])

def handle_menu_selection(cid, contact_id, msg_content, lang):
    """Handle main menu selections"""
    contact_attrs = get_contact_attrs(contact_id)
    conv_attrs = get_conv_attrs(cid)
    segment = contact_attrs.get("segment", "new")
    
    print(f"🔘 Menu selection: '{msg_content}' for {segment} customer")
    
    # Handle prefill confirmation menu selections
    if conv_attrs.get("pending_intent") == "prefill_confirmation":
        print(f"🤖 Handling prefill confirmation menu selection")
        handle_prefill_confirmation(cid, contact_id, msg_content, lang)
        return
    
    # Handle preferences check menu selections
    if conv_attrs.get("pending_intent") == "preferences_check":
        print(f"⏰ Handling preferences check menu selection")
        if msg_content == "preferences_same" or msg_content == t("preferences_check_yes", lang):
            print(f"✅ Preferences still the same - proceeding with current info")
            # Continue with current preferences, show action menu
            show_prefill_action_menu_after_confirmation(cid, contact_id, lang)
            return
        elif msg_content == "preferences_changed" or msg_content == t("preferences_check_no", lang):
            print(f"🔄 Preferences have changed - requesting new preferences")
            # Ask for new preferences
            send_text_with_duplicate_check(cid, t("preferences_update_request", lang))
            set_conv_attrs(cid, {"pending_intent": "preferences_update"})
            return
        else:
            print(f"❓ Unknown preferences check action: '{msg_content}'")
            return
    
    # Handle preferences update (AI analysis)
    if conv_attrs.get("pending_intent") == "preferences_update":
        print(f"🔄 Handling preferences update with AI analysis")
        # Use AI to analyze the new preferences
        analysis = analyze_preferences_with_openai(msg_content, cid)
        
        if analysis:
            # Update contact attributes with new preferences
            set_contact_attrs(contact_id, {
                "preferred_times": analysis.get("preferred_times", ""),
                "location_preference": analysis.get("location_preference", ""),
                "preferences_updated": True
            })
            
            # Confirm the updated preferences
            confirmation_msg = f"✅ Perfect! Ik heb je nieuwe voorkeuren opgeslagen:\n\n⏰ **Voorkeur tijd**: {analysis.get('preferred_times', '')}\n📍 **Locatie**: {analysis.get('location_preference', '')}\n\nNu kunnen we verder met de planning!"
            send_text_with_duplicate_check(cid, confirmation_msg)
            
            # Show action menu
            show_prefill_action_menu_after_confirmation(cid, contact_id, lang)
            return
        else:
            # If AI analysis failed, ask for clarification
            send_text_with_duplicate_check(cid, "❓ Ik begrijp je voorkeuren niet helemaal. Kun je het duidelijker omschrijven?")
            return
    
    # Handle prefill action menu selections
    if conv_attrs.get("pending_intent") == "prefill_action":
        print(f"🎯 Handling prefill action menu selection")
        if msg_content == "plan_all_lessons" or msg_content == t("prefill_action_all_lessons", lang):
            print(f"📅 All lessons planning requested from prefill")
            # Set flag to indicate premium service (all lessons)
            set_conv_attrs(cid, {"premium_service": True, "planning_profile": "premium"})
            start_planning_flow(cid, contact_id, lang)
            return
        elif msg_content == "plan_trial_lesson" or msg_content == t("prefill_action_trial_first", lang):
            print(f"📅 Trial lesson planning requested from prefill")
            start_planning_flow(cid, contact_id, lang)
            return
        elif msg_content == "urgent_session" or msg_content == t("prefill_action_urgent_session", lang):
            print(f"🚨 Urgent 2-hour session requested from prefill")
            # Set urgent session flag and start planning with immediate payment
            set_conv_attrs(cid, {"urgent_session": True, "session_duration": 120})
            start_planning_flow(cid, contact_id, lang)
            return
        elif msg_content == "go_to_main_menu" or msg_content == t("prefill_action_main_menu", lang):
            print(f"📋 Main menu requested from prefill")
            show_segment_menu(cid, contact_id, segment, lang)
            return
        elif msg_content == "handoff" or msg_content == t("prefill_action_handoff", lang):
            print(f"👨‍🏫 Handoff requested from prefill")
            send_handoff_message(cid, t("handoff_teacher", lang))
            return
        else:
            print(f"❓ Unknown prefill action: '{msg_content}'")
            return
    
    # Handle info menu selections
    if conv_attrs.get("pending_intent") == "info_menu":
        print(f"📄 Handling info menu selection")
        handle_info_menu_selection(cid, contact_id, msg_content, lang)
        return
    
    # Handle info follow-up menu selections
    if conv_attrs.get("pending_intent") == "info_follow_up":
        print(f"📄 Handling info follow-up menu selection")
        if msg_content == "plan_lesson" or msg_content == t("menu_option_plan_lesson", lang):
            print(f"📅 Lesson planning requested from info follow-up")
            start_planning_flow(cid, contact_id, lang)
            return
        elif msg_content == "trial_lesson" or msg_content == t("menu_option_trial_lesson", lang):
            print(f"🎯 Trial lesson planning requested from info follow-up")
            start_planning_flow(cid, contact_id, lang)
            return
        elif msg_content == "more_info" or msg_content == t("menu_more_info", lang):
            print(f"📖 More info requested from info follow-up")
            show_detailed_info_menu(cid, lang)
            return
        elif msg_content == "handoff" or msg_content == t("menu_option_handoff", lang):
            print(f"👨‍🏫 Handoff requested from info follow-up")
            send_handoff_message(cid, t("handoff_teacher", lang))
            return
        elif msg_content == "back_to_main" or msg_content == t("menu_back_to_main", lang):
            print(f"⬅️ Back to main menu requested from info follow-up")
            show_segment_menu(cid, contact_id, segment, lang)
            return
        else:
            print(f"❓ Unknown info follow-up action: '{msg_content}'")
            return
    
    # Handle post-trial action menu selections
    if conv_attrs.get("pending_intent") == "post_trial_action":
        print(f"🎯 Handling post-trial action menu selection")
        if msg_content == "plan_all_lessons" or msg_content == t("post_trial_plan_all_lessons", lang):
            print(f"📅 All lessons planning requested after trial")
            # Set flag to indicate premium service (all lessons)
            set_conv_attrs(cid, {"premium_service": True, "planning_profile": "premium"})
            start_planning_flow(cid, contact_id, lang)
            return
        elif msg_content == "plan_single_lesson" or msg_content == t("post_trial_plan_single_lesson", lang):
            print(f"📅 Single lesson planning requested after trial")
            start_planning_flow(cid, contact_id, lang)
            return
        elif msg_content == "go_to_main_menu" or msg_content == t("post_trial_main_menu", lang):
            print(f"📋 Main menu requested after trial")
            show_segment_menu(cid, contact_id, segment, lang)
            return
        elif msg_content == "handoff" or msg_content == t("post_trial_handoff", lang):
            print(f"👨‍🏫 Handoff requested after trial")
            send_handoff_message(cid, t("handoff_teacher", lang))
            return
        else:
            print(f"❓ Unknown post-trial action: '{msg_content}'")
            return
    
    # Handle lesson planning (trial for new customers, regular for existing)
    if (msg_content.lower() in ["plan_lesson", "les inplannen", "1"] or 
        "📅" in msg_content or 
        "🎯" in msg_content or
        "🎯 proefles inplannen" in msg_content.lower() or
        "🎯 schedule trial lesson" in msg_content.lower() or
        "🎯 gratis proefles" in msg_content.lower() or
        "🎯 free trial lesson" in msg_content.lower()):
        print(f"📅 Lesson planning requested")
        start_planning_flow(cid, contact_id, lang)
        return
    
    # Handle info request
    if (msg_content.lower() in ["info", "informatie", "2"] or 
        "ℹ️" in msg_content or
        "ℹ️ informatie" in msg_content.lower() or
        "ℹ️ information" in msg_content.lower()):
        print(f"ℹ️ Info requested")
        show_info_menu(cid, lang)
        return
    
    # Handle same preferences (existing/returning)
    if (msg_content.lower() in ["same_preferences", "zelfde vak/voorkeuren", "old_preferences", "plannen met oude voorkeuren"] or 
        "📅" in msg_content or
        "📅 zelfde vak/voorkeuren" in msg_content.lower() or
        "📅 same subject/preferences" in msg_content.lower() or
        "📅 plannen met oude voorkeuren" in msg_content.lower() or
        "📅 plan with old preferences" in msg_content.lower()):
        print(f"📅 Same preferences - quick planning")
        set_conv_attrs(cid, {"planning_profile": segment})
        suggest_available_slots(cid, segment, lang)
        return
    
    # Handle different/new intake
    if (msg_content.lower() in ["different", "iets anders", "new_intake", "intake opnieuw doen"] or 
        "🆕" in msg_content or
        "🆕 iets anders" in msg_content.lower() or
        "🆕 something else" in msg_content.lower() or
        "🆕 intake opnieuw doen" in msg_content.lower() or
        "🆕 do intake again" in msg_content.lower()):
        print(f"🆕 Different preferences - starting intake")
        start_intake_flow(cid, contact_id, lang)
        return
    
    # Handle handoff
    if (msg_content.lower() in ["handoff", "stephen spreken", "3"] or 
        "👨‍🏫" in msg_content or
        "👨‍🏫 stephen spreken" in msg_content.lower() or
        "👨‍🏫 speak to stephen" in msg_content.lower()):
        print(f"👨‍🏫 Handoff to Stephen requested")
        send_handoff_message(cid, t("handoff_teacher", lang))
        return
    
    # If no valid menu option, show the menu again
    print(f"❓ Unknown menu option: '{msg_content}' - showing help menu")
    show_segment_menu(cid, contact_id, segment, lang)
    
def is_existing_customer(contact_attrs):
    """Check if contact is an existing customer (student or parent)"""
    return (contact_attrs.get("is_student") or 
            contact_attrs.get("is_parent") or
            contact_attrs.get("has_completed_intake") or
            contact_attrs.get("trial_lesson_completed") or
            contact_attrs.get("has_paid_lesson") or
            contact_attrs.get("lesson_booked"))

def has_completed_intake(conv_attrs):
    """Check if conversation has completed intake"""
    return conv_attrs.get("intake_completed", False)

def start_planning_flow(cid, contact_id, lang):
    """Start planning flow - determines if trial or regular lesson"""
    contact_attrs = get_contact_attrs(contact_id)
    conv_attrs = get_conv_attrs(cid)
    
    # Detect current segment
    current_segment = detect_segment(contact_id)
    
    # Check if this is a premium service request (all lessons)
    is_premium = conv_attrs.get("premium_service", False)
    
    # Check if this is an urgent session request
    is_urgent = conv_attrs.get("urgent_session", False)
    
    if is_urgent:
        print(f"🚨 Urgent 2-hour session requested - direct planning with payment")
        set_conv_attrs(cid, {
            "planning_profile": current_segment,
            "lesson_type": "urgent",
            "urgent_session": True,
            "session_duration": 120
        })
        send_text_with_duplicate_check(cid, t("planning_urgent_session", lang))
        suggest_available_slots(cid, current_segment, lang)
        return
    
    if is_premium:
        print(f"💎 Premium service requested - planning all lessons")
        set_conv_attrs(cid, {
            "planning_profile": "premium",
            "lesson_type": "premium",
            "premium_service": True
        })
        send_text_with_duplicate_check(cid, t("planning_premium_service", lang))
        suggest_available_slots(cid, "premium", lang)
        return
    
    # Check if this is a new customer who just completed intake for a trial lesson
    has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
    
    if has_completed_intake(conv_attrs) and not has_completed_trial:
        print(f"🎯 New customer with completed intake - planning trial lesson")
        set_conv_attrs(cid, {
            "planning_profile": current_segment,
            "lesson_type": "trial"
        })
        send_text_with_duplicate_check(cid, t("planning_trial_lesson_intro", lang))
        suggest_available_slots(cid, current_segment, lang)
    elif is_existing_customer(contact_attrs):
        print(f"📅 Existing customer - planning regular lesson")
        # Check if existing customer has completed trial lesson
        has_completed_trial = contact_attrs.get("trial_lesson_completed", False)
        
        if has_completed_trial:
            # Existing customer who completed trial - show post-trial menu
            print(f"🎯 Existing customer with completed trial - showing post-trial menu")
            show_post_trial_menu(cid, contact_id, lang)
            return
        else:
            # Existing customer without trial - direct planning
            set_conv_attrs(cid, {
                "planning_profile": current_segment,
                "lesson_type": "regular"
            })
            send_text_with_duplicate_check(cid, t("planning_regular_lesson", lang))
            suggest_available_slots(cid, current_segment, lang)
    else:
        print(f"🎯 New customer - starting intake for free trial lesson")
        # New customer gets intake flow for free trial lesson
        # Check if we have confirmed prefill information
        # Check if we have prefill information that can be used
        if conv_attrs.get("learner_name") and conv_attrs.get("school_level"):
            print(f"✅ Found prefill information - using for trial lesson")
            set_conv_attrs(cid, {
                "lesson_type": "trial",
                "use_prefill": True,  # Flag to use prefill info
                "planning_profile": current_segment
            })
            send_text_with_duplicate_check(cid, t("planning_trial_lesson_intro", lang))
            suggest_available_slots(cid, current_segment, lang)
        else:
            print(f"🔄 No prefill information - starting intake flow")
            set_conv_attrs(cid, {
                "lesson_type": "trial",
                "has_been_prefilled": False,  # Clear prefill flag to start fresh
                "prefill_processed_for_message": "",  # Clear prefill tracking
                "prefill_confirmation_sent": False  # Clear confirmation flag
            })
            send_text_with_duplicate_check(cid, t("planning_trial_lesson_intro", lang))
            start_intake_flow(cid, contact_id, lang)

def start_intake_flow(cid, contact_id, lang):
    """Start the intake flow with prefill support"""
    print(f"📋 Starting intake flow for Conv:{cid}")
    
    conv_attrs = get_conv_attrs(cid)
    contact_attrs = get_contact_attrs(contact_id)
    
    # Check if we should use prefill information
    lesson_type = conv_attrs.get("lesson_type", "")
    use_prefill = conv_attrs.get("use_prefill", False)
    
    if lesson_type == "trial" and use_prefill:
        print(f"✅ Trial lesson with confirmed prefill - using prefill to skip steps")
        # Keep prefill information to skip steps
        # Don't clear anything - we want to use the confirmed prefill info
    elif lesson_type == "trial":
        print(f"🎯 Trial lesson requested - checking for prefill data")
        # Check if we have prefill data that should be preserved
        if conv_attrs.get("learner_name") and conv_attrs.get("school_level"):
            print(f"✅ Found prefill data - preserving for trial lesson")
            # Keep prefill data but mark as not confirmed yet
            set_conv_attrs(cid, {
                "has_been_prefilled": True,
                "prefill_processed_for_message": "",
                "prefill_confirmation_sent": False,
                "use_prefill": True  # Use prefill data
            })
        else:
            print(f"🔄 No prefill data found - starting fresh intake")
            # Clear any prefill information to start fresh
            set_conv_attrs(cid, {
                "has_been_prefilled": False,
                "prefill_processed_for_message": "",
                "prefill_confirmation_sent": False,
                "learner_name": "",
                "school_level": "",
                "topic_primary": "",
                "topic_secondary": "",
                "goals": "",
                "preferred_times": "",
                "lesson_mode": "",
                "toolset": "",
                "for_who": "",
                "relationship_to_learner": "",
                "contact_name": "",
                "location_preference": ""
            })
            # Also clear contact attributes
            set_contact_attrs(contact_id, {
                "learner_name": "",
                "school_level": "",
                "topic_primary": "",
                "topic_secondary": "",
                "goals": "",
                "preferred_times": "",
                "lesson_mode": "",
                "toolset": "",
                "for_who": "",
                "relationship_to_learner": "",
                "contact_name": "",
                "location_preference": ""
            })
        # Refresh attributes after clearing
    conv_attrs = get_conv_attrs(cid)
    contact_attrs = get_contact_attrs(contact_id)
    
    # Check what's already prefilled (check both conversation and contact attributes)
    prefilled_steps = []
    
    # Basic information
    if conv_attrs.get("for_who") or contact_attrs.get("for_who"):
        prefilled_steps.append("for_who")
    if conv_attrs.get("relationship_to_learner") or contact_attrs.get("relationship_to_learner"):
        prefilled_steps.append("relationship")
    if conv_attrs.get("is_adult") is not None or contact_attrs.get("is_adult") is not None:
        prefilled_steps.append("age_check")
    if conv_attrs.get("learner_name") or contact_attrs.get("learner_name"):
        prefilled_steps.append("learner_name")
    
    # Academic information
    if conv_attrs.get("school_level") or contact_attrs.get("school_level"):
        prefilled_steps.append("level")
    if conv_attrs.get("topic_primary") or contact_attrs.get("topic_primary"):
        prefilled_steps.append("subject")
    if conv_attrs.get("goals") or contact_attrs.get("goals"):
        prefilled_steps.append("goals")
    
    # Preferences
    if conv_attrs.get("preferred_times") or contact_attrs.get("preferred_times"):
        prefilled_steps.append("preferred_times")
    if conv_attrs.get("lesson_mode") or contact_attrs.get("lesson_mode"):
        prefilled_steps.append("mode")
    # referral_source is removed from intake process
    
    # Toolset is only relevant for programming subjects
    topic_primary = conv_attrs.get("topic_primary") or contact_attrs.get("topic_primary")
    if topic_primary in ["programming", "python", "coding"] and (conv_attrs.get("toolset") or contact_attrs.get("toolset")):
        prefilled_steps.append("toolset")
    
    # Additional information (optional but useful)
    if conv_attrs.get("location_preference") or contact_attrs.get("location_preference"):
        prefilled_steps.append("location_preference")
    
    print(f"📋 Prefilled steps: {prefilled_steps}")
    
    # Determine the first step to ask
    if "for_who" not in prefilled_steps:
        first_step = "for_who"
    elif "relationship" not in prefilled_steps and conv_attrs.get("for_who") == "other":
        # Only ask relationship if for_who is "other" (not for self/child)
        first_step = "relationship"
    elif "age_check" not in prefilled_steps:
        first_step = "age_check"
    elif "learner_name" not in prefilled_steps:
        first_step = "learner_name"
    elif "level" not in prefilled_steps:
        first_step = "level"
    elif "subject" not in prefilled_steps:
        first_step = "subject"
    elif "goals" not in prefilled_steps:
        first_step = "goals"
    elif "preferred_times" not in prefilled_steps:
        first_step = "preferred_times"
    elif "mode" not in prefilled_steps:
        first_step = "mode"
    elif "toolset" not in prefilled_steps and (conv_attrs.get("topic_primary") or contact_attrs.get("topic_primary")) in ["programming", "python", "coding"]:
        first_step = "toolset"
    # Note: location_preference is optional and doesn't block intake completion
    # Note: toolset is only relevant for programming subjects
    else:
        # All steps are prefilled, complete intake
        set_conv_attrs(cid, {
            "intake_completed": True,
            "trial_status": "completed",
            "pending_intent": "planning"
        })
        start_planning_flow(cid, contact_id, lang)
        return
    
    # Start with the first missing step
    set_conv_attrs(cid, {
        "pending_intent": "intake",
        "intake_step": first_step,
        "trial_status": "scheduled"
    })
    
    # Send the appropriate question
    if first_step == "for_who":
        send_input_select_only(cid, t("intake_for_who", lang), [
            (t("intake_option_self", lang), "self"),
            (t("intake_option_other", lang), "other")
        ])
    elif first_step == "age_check":
        send_input_select_only(cid, t("intake_age_check", lang), [
            ("✅ Ja", "yes"),
            ("❌ Nee", "no")
        ])
    elif first_step == "learner_name":
        send_text_with_duplicate_check(cid, t("intake_learner_name", lang))
    elif first_step == "level":
        send_input_select_only(cid, t("intake_level", lang), [
            ("Basisschool", "po"),
            ("VMBO", "vmbo"),
            ("HAVO", "havo"),
            ("VWO", "vwo"),
            ("MBO", "mbo"),
            ("Universiteit (WO)", "university_wo"),
            ("Universiteit (HBO)", "university_hbo"),
            ("Volwassenenonderwijs", "adult")
        ])
    elif first_step == "subject":
        send_input_select_only(cid, t("intake_subject", lang), [
            ("Wiskunde", "math"),
            ("Statistiek", "stats"),
            ("Engels", "english"),
            ("Programmeren", "programming"),
            ("Natuurkunde", "science"),
            ("Scheikunde", "chemistry"),
            ("Anders", "other")
        ])
    elif first_step == "goals":
        send_text_with_duplicate_check(cid, t("intake_goals", lang))
    elif first_step == "toolset":
        send_input_select_only(cid, "Welke tools gebruik je graag?", [
            ("Geen specifieke tools", "none"),
            ("Python", "python"),
            ("Excel", "excel"),
            ("SPSS", "spss"),
            ("R", "r"),
            ("Anders", "other")
        ])
    elif first_step == "preferred_times":
        send_text_with_duplicate_check(cid, t("intake_preferred_times", lang))
    elif first_step == "mode":
        send_input_select_only(cid, t("intake_mode", lang), [
            ("💻 Online", "online"),
            ("🏠 Fysiek", "in_person"),
            ("🔀 Hybride", "hybrid")
        ])

def handle_intake_step(cid, contact_id, msg_content, lang):
    """Handle intake flow steps"""
    conv_attrs = get_conv_attrs(cid)
    step = conv_attrs.get("intake_step")
    
    if step == "for_who":
        if msg_content.lower() in ["self", "voor mezelf", "1"] or "👤" in msg_content:
            set_conv_attrs(cid, {
                "pending_intent": "intake", 
                "intake_step": "age_check",
                "for_who": "self"
            })
            send_input_select_only(cid, t("intake_age_check", lang), [
                ("✅ Ja", "yes"),
                ("❌ Nee", "no")
            ])
        elif msg_content.lower() in ["other", "voor iemand anders", "2"] or "👥" in msg_content:
            set_conv_attrs(cid, {
                "pending_intent": "intake", 
                "intake_step": "relationship",
                "for_who": "other"
            })
            send_input_select_only(cid, t("intake_relationship", lang), [
                (t("intake_relationship_parent", lang), "parent"),
                (t("intake_relationship_family", lang), "family"),
                (t("intake_relationship_teacher", lang), "teacher"),
                (t("intake_relationship_other", lang), "other")
            ])
    
    elif step == "age_check":
        print(f"🔍 Age check step - received: '{msg_content}'")
        # Check for various ways to say yes
        if (msg_content.lower() in ["yes", "ja", "1", "ja.", "yes."] or 
            "✅" in msg_content or 
            msg_content.strip().lower() in ["ja", "yes"]):
            print(f"✅ Age check: Adult confirmed")
            set_contact_attrs(contact_id, {"is_adult": True})
            set_conv_attrs(cid, {"is_adult": True})
            print(f"[DEBUG] Age check: Starting step-by-step intake")
            
            # Check if learner name is already available from prefill
            conv_attrs = get_conv_attrs(cid)
            contact_attrs = get_contact_attrs(contact_id)
            learner_name = conv_attrs.get("learner_name") or contact_attrs.get("learner_name")
            
            if learner_name:
                print(f"✅ Learner name already available: {learner_name}")
                
                # If this is for themselves, update the contact name
                for_who = conv_attrs.get("for_who", "self")
                if for_who == "self":
                    set_contact_attrs(contact_id, {"name": learner_name})
                    set_contact_attrs(contact_id, {"is_student": True})
                    print(f"✅ Updated contact name to: {learner_name}")
                
                # Skip learner name step and go directly to level
                set_conv_attrs(cid, {
                    "pending_intent": "intake",
                    "intake_step": "level"
                })
                send_input_select_only(cid, t("intake_level", lang), [
                    ("Basisschool", "po"),
                    ("VMBO", "vmbo"),
                    ("HAVO", "havo"),
                    ("VWO", "vwo"),
                    ("MBO", "mbo"),
                    ("Universiteit (WO)", "university_wo"),
                    ("Universiteit (HBO)", "university_hbo"),
                    ("Volwassenenonderwijs", "adult")
                ])
            else:
                # Start step-by-step intake for consistency
                set_conv_attrs(cid, {
                    "pending_intent": "intake",
                    "intake_step": "learner_name"
                })
                send_text_with_duplicate_check(cid, t("intake_learner_name", lang))
        # Check for various ways to say no
        elif (msg_content.lower() in ["no", "nee", "2", "nee.", "no."] or 
              "❌" in msg_content or 
              msg_content.strip().lower() in ["nee", "no"]):
            print(f"❌ Age check: Minor confirmed")
            set_contact_attrs(contact_id, {"is_adult": False})
            set_conv_attrs(cid, {"is_adult": False, "pending_intent": "intake", "intake_step": "guardian_name"})
            send_text_with_duplicate_check(cid, t("intake_guardian_info", lang))
        else:
            print(f"❓ Age check: Unknown response '{msg_content}' - asking again")
            send_input_select_only(cid, t("intake_age_check", lang), [
                ("✅ Ja", "yes"),
                ("❌ Nee", "no")
            ])
    
    elif step == "relationship":
        # Save the relationship in contact attributes
        if msg_content == "parent":
            set_contact_attrs(contact_id, {"is_parent": True})
        elif msg_content == "teacher":
            set_contact_attrs(contact_id, {"is_teacher": True})
        else:
            set_contact_attrs(contact_id, {"relationship_type": msg_content})
        
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "relationship_to_learner": msg_content,
            "intake_step": "child_info"
        })
        print(f"✅ Saved relationship: {msg_content}")
        send_text_with_duplicate_check(cid, t("intake_child_info", lang))
    
    elif step == "guardian_name":
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "guardian_name": msg_content,
            "intake_step": "guardian_phone"
        })
        send_text_with_duplicate_check(cid, t("intake_guardian_phone", lang))
    
    elif step == "guardian_phone":
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "guardian_phone": msg_content,
            "intake_step": "child_info"
        })
        send_text_with_duplicate_check(cid, t("intake_child_info", lang))
    
    elif step == "child_info":
        # Save the learner name
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "learner_name": msg_content,
            "intake_step": "level"
        })
        print(f"✅ Saved learner name: {msg_content}")
        print(f"[DEBUG] Intake: child_info ingevuld, door naar level. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_input_select_only(cid, t("intake_level", lang), [
            ("Basisschool", "po"),
            ("VMBO", "vmbo"),
            ("HAVO", "havo"),
            ("VWO", "vwo"),
            ("MBO", "mbo"),
            ("Universiteit (WO)", "university_wo"),
            ("Universiteit (HBO)", "university_hbo"),
            ("Volwassenenonderwijs", "adult")
        ])
    

    
    elif step == "learner_name":
        # Check if this is for themselves or someone else
        conv_attrs = get_conv_attrs(cid)
        for_who = conv_attrs.get("for_who", "self")  # Default to self if not set
        
        if for_who == "self":
            # Update the contact's own name
            set_contact_attrs(contact_id, {"name": msg_content})
            set_contact_attrs(contact_id, {"is_student": True})
            print(f"✅ Updated contact name to: {msg_content}")
        else:
            # This is for someone else, save the learner name
            set_conv_attrs(cid, {"learner_name": msg_content})
            print(f"✅ Saved learner name: {msg_content}")
        
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "intake_step": "level"
        })
        print(f"[DEBUG] Intake: learner_name ingevuld, door naar level. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_input_select_only(cid, t("intake_level", lang), [
            ("Basisschool", "po"),
            ("VMBO", "vmbo"),
            ("HAVO", "havo"),
            ("VWO", "vwo"),
            ("MBO", "mbo"),
            ("Universiteit (WO)", "university_wo"),
            ("Universiteit (HBO)", "university_hbo"),
            ("Volwassenenonderwijs", "adult")
        ])
    
    elif step == "level":
        level_mapping = {
            "po": "audience:po",
            "vmbo": "audience:vmbo",
            "havo": "audience:havo",
            "vwo": "audience:vwo",
            "mbo": "audience:mbo",
            "university_wo": "audience:university:wo",
            "university_hbo": "audience:university:hbo",
            "adult": "audience:adult"
        }
        set_contact_attrs(contact_id, {"school_level": msg_content})
        add_conv_labels(cid, [level_mapping.get(msg_content, "audience:adult")])
        set_conv_attrs(cid, {"pending_intent": "intake", "intake_step": "subject"})
        print(f"[DEBUG] Intake: level ingevuld, door naar subject. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_input_select_only(cid, t("intake_subject", lang), [
            ("Wiskunde", "math"),
            ("Statistiek", "stats"),
            ("Engels", "english"),
            ("Programmeren", "programming"),
            ("Natuurkunde", "science"),
            ("Scheikunde", "chemistry"),
            ("Anders", "other")
        ])
    
    elif step == "subject":
        if msg_content.lower() != "other":
            # Convert simple values back to subject: format for labels
            subject_mapping = {
                "math": "subject:math",
                "stats": "subject:stats", 
                "english": "subject:english",
                "programming": "subject:programming",
                "science": "subject:science",
                "chemistry": "subject:chemistry"
            }
            label_value = subject_mapping.get(msg_content, msg_content)
            add_conv_labels(cid, [label_value])
            # Store primary topic for lesson planning
            set_conv_attrs(cid, {"topic_primary": msg_content})
        
        # Check if we need to ask for specific program
        if msg_content == "math" or msg_content == "stats":
            set_conv_attrs(cid, {"pending_intent": "intake", "intake_step": "program"})
            send_input_select_only(cid, "Welk specifiek programma?", [
                ("Geen specifiek programma", "none"),
                ("MBO Rekenen 2F", "mbo_rekenen_2f"),
                ("MBO Rekenen 3F", "mbo_rekenen_3f"),
                ("IB Math SL", "ib_math_sl"),
                ("IB Math HL", "ib_math_hl"),
                ("Cambridge", "cambridge")
            ])
        else:
            # Check if goals are already available from prefill
            conv_attrs = get_conv_attrs(cid)
            contact_attrs = get_contact_attrs(contact_id)
            goals = conv_attrs.get("goals") or contact_attrs.get("goals")
            
            if goals:
                print(f"✅ Goals already available from prefill: {goals}")
                # Skip goals step and go directly to toolset
                set_conv_attrs(cid, {
                    "pending_intent": "intake",
                    "intake_step": "toolset"
                })
                send_input_select_only(cid, "Welke tools gebruik je graag?", [
                    ("Geen specifieke tools", "none"),
                    ("Python", "python"),
                    ("Excel", "excel"),
                    ("SPSS", "spss"),
                    ("R", "r"),
                    ("Anders", "other")
                ])
            else:
                set_conv_attrs(cid, {"pending_intent": "intake", "intake_step": "goals"})
                print(f"[DEBUG] Intake: subject ingevuld, door naar goals. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
                send_text_with_duplicate_check(cid, t("intake_goals", lang))
    
    elif step == "program":
        set_conv_attrs(cid, {
            "program": msg_content,
            "pending_intent": "intake"
        })
        
        # Check if goals are already available from prefill
        conv_attrs = get_conv_attrs(cid)
        contact_attrs = get_contact_attrs(contact_id)
        goals = conv_attrs.get("goals") or contact_attrs.get("goals")
        
        if goals:
            print(f"✅ Goals already available from prefill: {goals}")
            # Skip goals step and go directly to toolset
            set_conv_attrs(cid, {
                "pending_intent": "intake",
                "intake_step": "toolset"
            })
            send_input_select_only(cid, "Welke tools gebruik je graag?", [
                ("Geen specifieke tools", "none"),
                ("Python", "python"),
                ("Excel", "excel"),
                ("SPSS", "spss"),
                ("R", "r"),
                ("Anders", "other")
            ])
        else:
            set_conv_attrs(cid, {"pending_intent": "intake", "intake_step": "goals"})
            print(f"[DEBUG] Intake: program ingevuld, door naar goals. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
            send_text_with_duplicate_check(cid, t("intake_goals", lang))
    
    elif step == "goals":
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "goals": msg_content,  # Store actual goals, not topic_secondary
            "intake_step": "toolset"
        })
        print(f"[DEBUG] Intake: goals ingevuld, door naar toolset. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_input_select_only(cid, "Welke tools gebruik je graag?", [
            ("Geen specifieke tools", "none"),
            ("Python", "python"),
            ("Excel", "excel"),
            ("SPSS", "spss"),
            ("R", "r"),
            ("Anders", "other")
        ])
    
    elif step == "toolset":
        set_conv_attrs(cid, {
            "toolset": msg_content,
            "pending_intent": "intake",
            "intake_step": "preferred_times"
        })
        print(f"[DEBUG] Intake: toolset ingevuld, door naar preferred_times. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_text_with_duplicate_check(cid, t("intake_preferred_times", lang))
    
    elif step == "preferred_times":
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "preferred_times": msg_content,
            "intake_step": "mode"
        })
        print(f"[DEBUG] Intake: preferred_times ingevuld, door naar mode. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_input_select_only(cid, t("intake_mode", lang), [
            ("💻 Online", "online"),
            ("🏠 Fysiek", "in_person"),
            ("🔀 Hybride", "hybrid")
        ])
    
    elif step == "mode":
        # Handle emoji-based mode selection
        if "💻" in msg_content:
            msg_content = "online"
        elif "🏠" in msg_content:
            msg_content = "in_person"
        elif "🔀" in msg_content:
            msg_content = "hybrid"
            
        set_conv_attrs(cid, {
            "intake_completed": True,
            "trial_status": "completed",
            "pending_intent": "planning",
            "lesson_mode": msg_content
        })
        print(f"[DEBUG] Intake: mode ingevuld, intake afgerond. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        
        # Set planning profile based on segment
        contact_attrs = get_contact_attrs(contact_id)
        segment = contact_attrs.get("segment", "new")
        set_conv_attrs(cid, {"planning_profile": segment})
        
        # Suggest available slots
        suggest_available_slots(cid, segment, lang)

def suggest_available_slots(cid, profile_name, lang):
    """Suggest available slots"""
    print(f"📅 Suggesting slots for profile: {profile_name}")
    conv_attrs = get_conv_attrs(cid)
    lesson_type = conv_attrs.get("lesson_type", "trial")
    
    slots = suggest_slots(cid, profile_name)
    
    if not slots:
        print(f"⚠️ No available slots found for {profile_name}")
        
        # Check if this is a trial lesson and show specific message
        if lesson_type == "trial":
            send_text_with_duplicate_check(cid, t("no_trial_slots_available", lang))
        else:
            send_text_with_duplicate_check(cid, t("no_slots_available", lang))
        return
    
    print(f"✅ Found {len(slots)} available slots")
    
    # Create quick reply options
    options = []
    for slot in slots:
        options.append((slot["label"], slot["start"]))
        print(f"📅 Slot option: '{slot['label']}' -> '{slot['start']}'")
    
    options.append((t("planning_more_options", lang), "more_options"))
    print(f"📅 More options: '{t('planning_more_options', lang)}' -> 'more_options'")
    
    # Set pending intent to planning so we can handle slot selections
    set_conv_attrs(cid, {"pending_intent": "planning"})
    
    # Determine lesson text based on type
    if lesson_type == "premium":
        lesson_text = t("planning_premium_slots", lang)
    elif lesson_type == "trial":
        lesson_text = t("planning_trial_slots", lang)
    else:
        lesson_text = t("planning_regular_slots", lang)
    
    print(f"📅 Sending {len(options)} options with text: '{lesson_text}'")
    send_input_select_only(cid, lesson_text, options)

def handle_planning_selection(cid, contact_id, msg_content, lang):
    """Handle planning slot selection"""
    print(f"🔍 Planning selection: '{msg_content}'")
    print(f"🔍 Planning selection type: {type(msg_content)}")
    print(f"🔍 Planning selection length: {len(msg_content) if msg_content else 0}")
    
    if msg_content == "more_options" or msg_content == "Meer opties":
        # Suggest more options (extend time horizon)
        conv_attrs = get_conv_attrs(cid)
        profile_name = conv_attrs.get("planning_profile", "new")
        suggest_available_slots(cid, profile_name, lang)
        return
    
    # Check if this is a slot selection (format: "2025-08-05T12:00:00+02:00" or "Wed 13 Aug 14:00–15:00")
    if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', msg_content):
        # Direct ISO timestamp format
        iso_timestamp = msg_content
    elif re.match(r'[A-Za-z]{3} \d{1,2} [A-Za-z]{3} \d{2}:\d{2}–\d{2}:\d{2}', msg_content):
        # Format: "Wed 13 Aug 14:00–15:00" - extract start time
        try:
            # Parse the readable format to get start time
            # Example: "Wed 13 Aug 14:00–15:00" -> extract "13 Aug 14:00"
            match = re.match(r'[A-Za-z]{3} (\d{1,2}) ([A-Za-z]{3}) (\d{2}:\d{2})–\d{2}:\d{2}', msg_content)
            if match:
                day = match.group(1)
                month = match.group(2)
                time = match.group(3)
                
                # Convert month name to number
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                month_num = month_map.get(month, '08')  # Default to August
                
                # Create ISO timestamp for current year
                current_year = datetime.now().year
                iso_timestamp = f"{current_year}-{month_num}-{day.zfill(2)}T{time}:00+02:00"
                print(f"🔍 Converted '{msg_content}' to ISO timestamp: {iso_timestamp}")
            else:
                print(f"⚠️ Could not parse readable time format: '{msg_content}'")
                send_text_with_duplicate_check(cid, t("error_invalid_time", lang))
                return
        except Exception as e:
            print(f"❌ Error parsing readable time format: {e}")
            send_text_with_duplicate_check(cid, t("error_time_processing", lang))
            return
    else:
        # Invalid input - provide helpful response
        print(f"⚠️ Invalid planning selection: '{msg_content}'")
        conv_attrs = get_conv_attrs(cid)
        profile_name = conv_attrs.get("planning_profile", "new")
        
        # Resend available slots with explanation
        send_text_with_duplicate_check(cid, t("planning_invalid_selection", lang))
        suggest_available_slots(cid, profile_name, lang)
        return
    
    # Book the slot using the ISO timestamp
    conv_attrs = get_conv_attrs(cid)
    learner_name = conv_attrs.get("learner_name", "Student")
    lesson_type = conv_attrs.get("lesson_type", "trial")
    is_urgent = conv_attrs.get("urgent_session", False)
    
    # Calculate end time based on lesson type
    try:
        start_dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        
        if is_urgent:
            # 2-hour session for urgent bookings
            end_dt = start_dt + timedelta(minutes=120)
            lesson_title = f"Stephen's Privélessen — Spoed Sessie"
            lesson_description = f"Spoed 2-uurs sessie voor {learner_name}"
        else:
            # 1-hour session for regular bookings
            end_dt = start_dt + timedelta(minutes=60)
            lesson_title = f"Stephen's Privélessen — Proefles"
            lesson_description = f"Proefles voor {learner_name}"
        
        end_time = end_dt.isoformat()
        
        # Create a readable slot description
        slot_description = f"{start_dt.strftime('%A %d %B %H:%M')} - {end_dt.strftime('%H:%M')}"
        
        print(f"📅 Booking slot: {slot_description} (type: {lesson_type}, urgent: {is_urgent})")
        
        # Create tentative booking
        event = book_slot(
            cid,
            iso_timestamp,
            end_time,
            lesson_title,
            lesson_description
        )
        
        if event:
            if is_urgent:
                # For urgent sessions, create payment link immediately
                print(f"🚨 Urgent session booked - creating payment link")
                contact_attrs = get_contact_attrs(contact_id)
                segment = contact_attrs.get("segment", "new")
                
                # Create payment link for 2-hour session (€120)
                payment_link = create_payment_link(
                    segment=segment,
                    minutes=120,
                    order_id=f"urgent_{cid}_{int(time.time())}",
                    conversation_id=cid,
                    student_name=learner_name,
                    service="urgent_session",
                    audience="secondary_under_20",
                    program="none"
                )
                
                if payment_link:
                    confirmation_msg = f"✅ Perfect! Ik heb een spoed 2-uurs sessie ingepland op {slot_description}.\n\n💳 **Direct betalen:** {payment_link}\n\n📧 Voor de bevestiging heb ik nog je e-mailadres nodig. Kun je dat delen?"
                    send_text_with_duplicate_check(cid, confirmation_msg)
                else:
                    confirmation_msg = f"✅ Perfect! Ik heb een spoed 2-uurs sessie ingepland op {slot_description}.\n\n📧 Voor de bevestiging heb ik nog je e-mailadres nodig. Kun je dat delen?"
                    send_text_with_duplicate_check(cid, confirmation_msg)
            else:
                # For regular trial lessons, ask for email
                confirmation_msg = f"✅ Perfect! Ik heb een proefles ingepland op {slot_description}.\n\n📧 Voor de bevestiging heb ik nog je e-mailadres nodig. Kun je dat delen?"
                send_text_with_duplicate_check(cid, confirmation_msg)
        else:
            send_text_with_duplicate_check(cid, t("error_planning_failed", lang))
            return
            
    except Exception as e:
        print(f"❌ Error parsing slot time: {e}")
        send_text_with_duplicate_check(cid, t("error_time_processing", lang))
        return
    
    # Check lesson type and handle accordingly
    lesson_type = conv_attrs.get("lesson_type", "trial")
    
    if lesson_type == "trial":
        # This is a trial lesson, no payment needed
        # Mark contact as having completed intake and trial lesson
        set_contact_attrs(contact_id, {
            "has_completed_intake": True,
            "trial_lesson_completed": True,
            "lesson_booked": True,
            "customer_since": datetime.now(TZ).isoformat()
        })
        set_conv_attrs(cid, {"pending_intent": "ask_email"})
        
        # Ask for email for invoice purposes
        email_request_msg = f"✅ Perfect! Je proefles is ingepland op {slot_description}.\n\n{t('email_request', lang)}"
        send_text_with_duplicate_check(cid, email_request_msg)
        
        print(f"📧 Email request sent - waiting for email address")
    elif lesson_type == "regular":
        # This is a regular lesson, create payment link immediately
        print(f"📅 Regular lesson booked - creating payment link")
        create_payment_request(cid, contact_id, lang)
    else:
        # Default to trial lesson behavior
        print(f"⚠️ Unknown lesson type '{lesson_type}' - treating as trial lesson")
        set_contact_attrs(contact_id, {
            "has_completed_intake": True,
            "trial_lesson_completed": True,
            "lesson_booked": True,
            "customer_since": datetime.now(TZ).isoformat()
        })
        set_conv_attrs(cid, {"pending_intent": "ask_email"})
        
        # Ask for email for invoice purposes
        email_request_msg = f"✅ Perfect! Je proefles is ingepland op {slot_description}.\n\n{t('email_request', lang)}"
        send_text_with_duplicate_check(cid, email_request_msg)
        
        print(f"📧 Email request sent - waiting for email address")

def handle_email_request(cid, contact_id, msg_content, lang):
    """Handle email request for trial lesson invoice"""
    print(f"📧 Email request: '{msg_content}'")
    
    # Smart email extraction
    import re
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find email in message
    email_match = re.search(email_pattern, msg_content)
    
    if email_match:
        # Valid email found
        email = email_match.group(0).strip()
        
        # Store email in contact attributes
        set_contact_attrs(contact_id, {"email": email})
        
        # Send confirmation
        confirmation_msg = f"📧 Bedankt! Ik heb je e-mailadres ({email}) opgeslagen voor de bevestiging.\n\n{t('email_confirmation', lang)}"
        send_text_with_duplicate_check(cid, confirmation_msg)
        
        # Reset pending intent
        set_conv_attrs(cid, {"pending_intent": ""})
        
        # Show post-trial menu with option to plan all lessons
        show_post_trial_menu(cid, contact_id, lang)
        
        print(f"✅ Email extracted and stored: {email}")
    else:
        # No valid email found
        error_msg = t("email_invalid", lang)
        send_text_with_duplicate_check(cid, error_msg)
        print(f"❌ No valid email found in: {msg_content}")
        
        # Keep pending_intent as "ask_email" so user can try again

def show_post_trial_menu(cid, contact_id, lang):
    """Show menu after trial lesson completion"""
    print(f"🎯 Showing post-trial menu in {lang}")
    
    # Send post-trial message
    send_text_with_duplicate_check(cid, t("post_trial_message", lang))
    
    # Show menu with options
    menu_title = t("post_trial_menu_title", lang)
    menu_options = [
        (t("post_trial_plan_all_lessons", lang), "plan_all_lessons"),
        (t("post_trial_plan_single_lesson", lang), "plan_single_lesson"),
        (t("post_trial_main_menu", lang), "go_to_main_menu"),
        (t("post_trial_handoff", lang), "handoff")
    ]
    
    try:
        set_conv_attrs(cid, {"pending_intent": "post_trial_action"})
    except Exception as e:
        print(f"⚠️ SSL error setting pending_intent: {e}")
    
    result = send_input_select_only(cid, menu_title, menu_options)
    print(f"🎯 Post-trial menu send result: {result}")

def create_payment_request(cid, contact_id, lang):
    """Create payment request"""
    conv_attrs = get_conv_attrs(cid)
    contact_attrs = get_contact_attrs(contact_id)
    
    # Generate order ID
    order_id = f"SPL-{datetime.now().strftime('%Y%m%d')}-{cid:04d}"
    set_conv_attrs(cid, {"order_id": order_id})
    
    # Create payment link
    payment_link = create_payment_link(
        contact_attrs.get("segment", "new"),
        60,  # minutes
        order_id,
        cid,
        conv_attrs.get("learner_name", "Student"),
        "1on1",
        contact_attrs.get("school_level", "adult"),
        conv_attrs.get("program", "none")
    )
    
    # Add payment labels and status
    add_conv_labels(cid, ["status:awaiting_pay"])
    set_conv_attrs(cid, {"payment_status": "pending"})
    if contact_attrs.get("segment") == "weekend":
        add_conv_labels(cid, ["price_custom"])
    
    # Send payment link
    send_text_with_duplicate_check(cid, t("payment_link", lang, link=payment_link))
    set_conv_attrs(cid, {"pending_intent": ""})

# Stripe webhook handler
@app.post("/webhook/payments")
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    if not verify_stripe_webhook(payload, signature):
        return "Unauthorized", 401
    
    event = request.get_json()
    event_type = event.get("type")
    
    if event_type == "checkout.session.completed":
        handle_payment_success(event)
    elif event_type == "payment_intent.succeeded":
        handle_payment_success(event)
    
    return "OK", 200

def handle_payment_success(event):
    """Handle successful payment"""
    # Extract conversation ID from metadata
    metadata = event.get("data", {}).get("object", {}).get("metadata", {})
    conversation_id = metadata.get("chatwoot_conversation_id")
    order_id = metadata.get("order_id")
    
    if not conversation_id:
        return
    
    # Get contact ID from conversation
    conv_url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}"
    headers = {"api_access_token": ADMIN_TOK}
    
    try:
        conv_response = requests.get(conv_url, headers=headers)
        if conv_response.status_code == 200:
            conv_data = conv_response.json()
            contact_id = conv_data.get("contact_inbox", {}).get("contact_id")
            
            if contact_id:
                # Mark contact as having paid for a lesson
                set_contact_attrs(contact_id, {
                    "has_paid_lesson": True,
                    "has_completed_intake": True,
                    "lesson_booked": True,
                    "customer_since": datetime.now(TZ).isoformat()
                })
    except:
        pass
    
    # Update conversation labels and payment status
    remove_conv_labels(conversation_id, ["status:awaiting_pay"])
    add_conv_labels(conversation_id, ["payment:paid", "status:booked"])
    set_conv_attrs(conversation_id, {"payment_status": "paid"})
    
    # Add note with payment details
    amount = event.get("data", {}).get("object", {}).get("amount_total", 0)
    currency = event.get("data", {}).get("object", {}).get("currency", "eur")
    
    note_text = f"Payment received: {amount/100} {currency.upper()}\nOrder ID: {order_id}"
    
    # Add note to conversation
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/notes"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    data = {"content": note_text}
    
    try:
        requests.post(url, headers=headers, json=data)
    except:
        pass

def handle_faq_request(cid, contact_id, msg_content, lang):
    """Handle FAQ requests and provide relevant answers"""
    print(f"📚 FAQ request: '{msg_content}'")
    
    # Common FAQ keywords and their corresponding FAQ numbers
    faq_keywords = {
        # Main FAQ keywords
        "inspiratie": 1, "inspiration": 1, "waarom": 1, "why": 1,
        "aanpak": 2, "approach": 2, "methoden": 2, "methods": 2,
        "uniek": 3, "unique": 3, "verschil": 3, "difference": 3,
        "leerstijlen": 4, "learning styles": 4, "niveaus": 4, "levels": 4,
        "resultaten": 5, "results": 5, "successen": 5, "success": 5,
        "organisatie": 6, "organization": 6, "online": 6, "fysiek": 6,
        "kosten": 7, "costs": 7, "prijzen": 7, "prices": 7, "tarieven": 7,
        "aanmelden": 8, "sign up": 8, "registreren": 8, "register": 8,
        "betaling": 9, "payment": 9, "factuur": 9, "invoice": 9,
        "proefles": 10, "trial": 10, "gratis": 10, "free": 10
    }
    
    # Check if the message contains FAQ keywords
    msg_lower = msg_content.lower()
    matched_faq = None
    
    for keyword, faq_number in faq_keywords.items():
        if keyword in msg_lower:
            matched_faq = faq_number
            break
    
    if matched_faq:
        # Get the FAQ answer
        answer_key = f"faq_{matched_faq}_answer"
        answer = t(answer_key, lang)
        
        # Send the FAQ answer
        send_text_with_duplicate_check(cid, answer)
        return True
    
    # If no specific FAQ matched, offer general FAQ help
    faq_help_msg = t("faq_general_help", lang)
    send_text_with_duplicate_check(cid, faq_help_msg)
    return False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True) 