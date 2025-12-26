#!/usr/bin/env python3
"""
Text Helper Utilities for TutorBot

This module contains utility functions for text processing, messaging,
and conversation management.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Import dependencies (these will need to be available)
from modules.utils.cw_api import ChatwootAPI, get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs

# Configuration (these should eventually move to a config module)
TZ = "Europe/Amsterdam"
CW = os.getenv("CHATWOOT_URL")
ACC = os.getenv("CHATWOOT_ACCOUNT_ID")
ADMIN_TOK = os.getenv("CHATWOOT_ADMIN_TOKEN")
BOT_USER_ID = os.getenv("CHATWOOT_BOT_USER_ID")

def safe_set_conv_attrs(conversation_id, attrs):
    """Safely set conversation attributes with error handling"""
    try:
        set_conv_attrs(conversation_id, attrs)
        return True
    except Exception as e:
        print(f"❌ Failed to set conversation attributes for {conversation_id}: {e}")
        return False

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
        
        # New intake flow translations
        "intake_intro": {
            "nl": "📋 *Welkom bij de intake!* 👋\n\nIk ga je helpen om de juiste informatie te verzamelen voor je proefles. Je kunt kiezen uit twee manieren:",
            "en": "📋 *Welcome to the intake!* 👋\n\nI'll help you collect the right information for your trial lesson. You can choose from two methods:"
        },
        "intake_choice_title": {
            "nl": "Hoe wil je de intake doorlopen?",
            "en": "How would you like to complete the intake?"
        },
        "intake_choice_step_by_step": {
            "nl": "📝 Stap-voor-stap",
            "en": "📝 Step-by-step"
        },
        "intake_choice_free_text": {
            "nl": "💬 Vrije tekst",
            "en": "💬 Free text"
        },
        "intake_choice_handoff": {
            "nl": "👨‍🏫 Stephen spreken",
            "en": "👨‍🏫 Talk to Stephen"
        },
        "intake_for_who_self": {
            "nl": "👤 Voor mezelf",
            "en": "👤 For myself"
        },
        "intake_for_who_child": {
            "nl": "👶 Voor mijn kind",
            "en": "👶 For my child"
        },
        "intake_for_who_other": {
            "nl": "👥 Voor iemand anders",
            "en": "👥 For someone else"
        },
        "intake_free_text_prompt": {
            "nl": "💬 *Vertel me alles over je situatie!* 📝\n\nJe kunt gewoon je verhaal uittypen. Focus op deze kernpunten:\n\n• *👤 Naam* van de leerling\n• *🎓 School niveau* (PO, VMBO, HAVO, VWO, MBO, Universiteit, etc.)\n• *📚 Vak/onderwerp* (wiskunde, statistiek, Engels, etc.)\n• *🎯 Doelen* (eindexamen, tentamen, algemene verbetering)\n• *⏰ Voorkeursdagen/tijden*\n\nIk ga dan met AI je informatie analyseren en bevestigen! 🤖",
            "en": "💬 *Tell me everything about your situation!* 📝\n\nYou can just type out your story. Focus on these key points:\n\n• *👤 Name* of the student\n• *🎓 School level* (Primary, VMBO, HAVO, VWO, MBO, University, etc.)\n• *📚 Subject/topic* (math, statistics, English, etc.)\n• *🎯 Goals* (final exam, test, general improvement)\n• *⏰ Preferred days/times*\n\nI'll then analyze your information with AI and confirm it! 🤖"
        },
        "intake_free_text_detected": {
            "nl": "*Ik heb de volgende informatie gedetecteerd:*",
            "en": "*I detected the following information:*"
        },
        "intake_free_text_confirm_title": {
            "nl": "Klopt deze informatie?",
            "en": "Is this information correct?"
        },
        "intake_free_text_confirm": {
            "nl": "✅ Ja, klopt!",
            "en": "✅ Yes, correct!"
        },
        "intake_free_text_correct": {
            "nl": "🔧 Aanpassen",
            "en": "🔧 Adjust"
        },
        "intake_free_text_handoff": {
            "nl": "👨‍🏫 Stephen spreken",
            "en": "👨‍🏫 Talk to Stephen"
        },
        "intake_free_text_no_info": {
            "nl": "⚠️ Ik kon geen duidelijke informatie uit je bericht halen. Laten we het stap-voor-stap proberen!",
            "en": "⚠️ I couldn't extract clear information from your message. Let's try step-by-step!"
        },
        "intake_free_text_failed": {
            "nl": "❌ Er ging iets mis bij het analyseren. Laten we het stap-voor-stap proberen!",
            "en": "❌ Something went wrong with the analysis. Let's try step-by-step!"
        },
        "intake_free_text_error": {
            "nl": "❌ Er is een technische fout opgetreden. Laten we het stap-voor-stap proberen!",
            "en": "❌ A technical error occurred. Let's try step-by-step!"
        },
        "intake_completed": {
            "nl": "✅ Intake voltooid! Je informatie is opgeslagen.",
            "en": "✅ Intake completed! Your information has been saved."
        },
        "intake_completed_fallback": {
            "nl": "✅ Intake voltooid! Laten we verder gaan.",
            "en": "✅ Intake completed! Let's continue."
        },
        "intake_for_who_invalid": {
            "nl": "❓ Ik begrijp je niet helemaal. Kies alsjeblieft:",
            "en": "❓ I don't quite understand. Please choose:"
        },
        "intake_school_level_invalid": {
            "nl": "❓ Ik begrijp je niet helemaal. Kies alsjeblieft je school niveau:",
            "en": "❓ I don't quite understand. Please choose your school level:"
        },
        "intake_topic_invalid": {
            "nl": "❓ Ik begrijp je niet helemaal. Kies alsjeblieft een vak:",
            "en": "❓ I don't quite understand. Please choose a subject:"
        },
        "intake_name_self": {
            "nl": "Wat is je naam?",
            "en": "What is your name?"
        },
        "intake_name_student": {
            "nl": "Wat is de naam van de leerling?",
            "en": "What is the name of the student?"
        },
        "intake_school_level": {
            "nl": "Welk school niveau heeft de leerling?",
            "en": "What school level does the student have?"
        },
        "intake_topic": {
            "nl": "Welk vak of onderwerp wil je behandelen?",
            "en": "Which subject or topic do you want to cover?"
        },
        "intake_preferences": {
            "nl": "🎯 *Vertel me over je doelen en voorkeuren!* 📝\n\nBijvoorbeeld:\n• Wat wil je bereiken? (eindexamen, tentamen, algemene verbetering)\n• Wanneer heb je deadlines?\n• Welke dagen/tijden komen je het beste uit?\n• Heb je specifieke wensen voor de les?\n\nIk ga dan de beste momenten voor je proefles voorstellen! 🚀",
            "en": "🎯 *Tell me about your goals and preferences!* 📝\n\nFor example:\n• What do you want to achieve? (final exam, test, general improvement)\n• When do you have deadlines?\n• Which days/times work best for you?\n• Do you have specific wishes for the lesson?\n\nI'll then suggest the best moments for your trial lesson! 🚀"
        },
        "name_label": {
            "nl": "Naam",
            "en": "Name"
        },
        "level_label": {
            "nl": "School niveau",
            "en": "School level"
        },
        "subject_label": {
            "nl": "Vak",
            "en": "Subject"
        },
        "goals_label": {
            "nl": "Doelen",
            "en": "Goals"
        },
        "preferred_times_label": {
            "nl": "Voorkeursdagen/tijden",
            "en": "Preferred days/times"
        },
        "level_po": {
            "nl": "Basisonderwijs (PO)",
            "en": "Primary Education (PO)"
        },
        "level_university_wo": {
            "nl": "Universiteit (WO)",
            "en": "University (WO)"
        },
        "level_university_hbo": {
            "nl": "HBO",
            "en": "HBO"
        },
        "level_adult": {
            "nl": "Volwassenen",
            "en": "Adults"
        },
        "topic_math": {
            "nl": "Wiskunde",
            "en": "Mathematics"
        },
        "topic_stats": {
            "nl": "Statistiek",
            "en": "Statistics"
        },
        "topic_english": {
            "nl": "Engels",
            "en": "English"
        },
        "topic_programming": {
            "nl": "Programmeren",
            "en": "Programming"
        },
        "topic_science": {
            "nl": "Natuurwetenschappen",
            "en": "Science"
        },
        "topic_chemistry": {
            "nl": "Scheikunde",
            "en": "Chemistry"
        },
        "topic_other": {
            "nl": "Anders",
            "en": "Other"
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
        "urgent_session_booked": {
            "nl": "Super! Ik heb een spoed 2-uurs sessie ingepland op {slot}.\n\n💳 *Direct betalen:* {payment_link}\n\n📧 Voor de bevestiging heb ik nog je e-mailadres nodig. Kun je dat delen?",
            "en": "Great! I've scheduled an urgent 2-hour session on {slot}.\n\n💳 *Pay now:* {payment_link}\n\n📧 For confirmation, I still need your email address. Can you share that?"
        },
        "urgent_session_booked_no_payment": {
            "nl": "Gelukt! Ik heb een spoed 2-uurs sessie ingepland op {slot}.\n\n📧 Voor de bevestiging heb ik nog je e-mailadres nodig. Kun je dat delen?",
            "en": "Done! I've scheduled an urgent 2-hour session on {slot}.\n\n📧 For confirmation, I still need your email address. Can you share that?"
        },
        "trial_lesson_booked": {
            "nl": "Helemaal goed! Ik heb een proefles ingepland op {slot}.",
            "en": "Excellent! I've scheduled a trial lesson on {slot}."
        },
        "trial_lesson_confirmed": {
            "nl": "Klaar! Je proefles is ingepland op {slot}.",
            "en": "All set! Your trial lesson is scheduled on {slot}."
        },
        "email_thanks": {
            "nl": "Bedankt! Ik heb je e-mailadres ({email}) opgeslagen voor de bevestiging.",
            "en": "Thank you! I've saved your email address ({email}) for confirmation."
        },
        "ask_for_preferences": {
            "nl": "🤔 Wat zijn je voorkeuren voor de les?\n\nVertel me bijvoorbeeld:\n• Welke dagen je voorkeur hebt (maandag, woensdag, etc.)\n• Welke tijden je het beste uitkomen (ochtend, middag, avond)\n• Of je specifieke tijden hebt (bijv. 'om 15:00')\n\nIk ga dan 3 momenten voorstellen die bij je passen!",
            "en": "🤔 What are your preferences for the lesson?\n\nTell me for example:\n• Which days you prefer (Monday, Wednesday, etc.)\n• Which times work best for you (morning, afternoon, evening)\n• If you have specific times (e.g. 'at 3:00 PM')\n\nI'll then suggest 3 moments that suit you!"
        },
        "planning_trial_slots_ai": {
            "nl": "🎯 Ik heb 3 momenten voor je proefles geselecteerd op basis van je voorkeuren:\n\nKies een moment dat je uitkomt:",
            "en": "🎯 I've selected 3 moments for your trial lesson based on your preferences:\n\nChoose a moment that works for you:"
        },
        "planning_regular_slots_ai": {
            "nl": "📅 Ik heb 3 momenten voor je les geselecteerd op basis van je voorkeuren:\n\nKies een moment dat je uitkomt:",
            "en": "📅 I've selected 3 moments for your lesson based on your preferences:\n\nChoose a moment that works for you:"
        },
        "planning_premium_slots_ai": {
            "nl": "💎 Ik heb 3 momenten voor je premium service geselecteerd op basis van je voorkeuren:\n\nKies een moment dat je uitkomt:",
            "en": "💎 I've selected 3 moments for your premium service based on your preferences:\n\nChoose a moment that works for you:"
        },
        "planning_trial_slots_real": {
            "nl": "🎯 Ik heb beschikbare momenten voor je proefles gevonden in de agenda:\n\nKies een moment dat je uitkomt:",
            "en": "🎯 I've found available moments for your trial lesson in the calendar:\n\nChoose a moment that works for you:"
        },
        "planning_regular_slots_real": {
            "nl": "📅 Ik heb beschikbare momenten voor je les gevonden in de agenda:\n\nKies een moment dat je uitkomt:",
            "en": "📅 I've found available moments for your lesson in the calendar:\n\nChoose a moment that works for you:"
        },
        "planning_premium_slots_real": {
            "nl": "💎 Ik heb beschikbare momenten voor je premium service gevonden in de agenda:\n\nKies een moment dat je uitkomt:",
            "en": "💎 I've found available moments for your premium service in the calendar:\n\nChoose a moment that works for you:"
        },
        "ask_for_corrections": {
            "nl": "🔧 Ik begrijp dat de informatie niet helemaal klopt. Kun je me vertellen wat er aangepast moet worden?\n\nVertel me bijvoorbeeld:\n• De juiste naam\n• Het juiste schoolniveau\n• Het juiste onderwerp\n• Of andere details die niet kloppen\n\nIk ga dan de informatie aanpassen en opnieuw vragen om bevestiging.",
            "en": "🔧 I understand the information isn't quite right. Can you tell me what needs to be corrected?\n\nTell me for example:\n• The correct name\n• The correct school level\n• The correct subject\n• Or other details that are wrong\n\nI'll then adjust the information and ask for confirmation again."
        },
        "prefill_corrected_summary_title": {
            "nl": "📋 Gecorrigeerde Informatie",
            "en": "📋 Corrected Information"
        },
        "prefill_corrected_confirmation_prompt": {
            "nl": "Klopt deze informatie nu wel?",
            "en": "Is this information correct now?"
        },
        "prefill_confirm_yes": {
            "nl": "✅ Ja, klopt!",
            "en": "✅ Yes, correct!"
        },
        "prefill_confirm_no": {
            "nl": "❌ Nee, nog fouten",
            "en": "❌ No, still errors"
        },
        "correction_analysis_failed": {
            "nl": "⚠️ Ik kon je correcties niet goed verwerken. Kun je het nog een keer proberen met duidelijke informatie?",
            "en": "⚠️ I couldn't process your corrections properly. Can you try again with clear information?"
        },
        "ask_for_more_corrections": {
            "nl": "🔧 Nog steeds niet correct. Kun je me precies vertellen wat er aangepast moet worden?",
            "en": "🔧 Still not correct. Can you tell me exactly what needs to be adjusted?"
        },
        "handoff_max_corrections": {
            "nl": "🚫 Ik heb moeite om je informatie correct te verwerken. Ik schakel je door naar Stephen zodat hij je persoonlijk kan helpen.",
            "en": "🚫 I'm having trouble processing your information correctly. I'm transferring you to Stephen so he can help you personally."
        },
        "prefill_unclear_response": {
            "nl": "🤔 Ik begrijp je antwoord niet helemaal. Kun je 'ja' zeggen als de informatie klopt, of 'nee' als er nog fouten zijn?",
            "en": "🤔 I don't quite understand your answer. Can you say 'yes' if the information is correct, or 'no' if there are still errors?"
        },
        "main_menu_message": {
            "nl": "🎯 Wat wil je nu doen?",
            "en": "🎯 What would you like to do now?"
        },
        "main_menu_title": {
            "nl": "Kies een optie:",
            "en": "Choose an option:"
        },
        "main_menu_plan_lesson": {
            "nl": "📅 Les plannen",
            "en": "📅 Plan lesson"
        },
        "main_menu_info": {
            "nl": "📖 Meer informatie",
            "en": "📖 More information"
        },
        "main_menu_contact": {
            "nl": "👨‍🏫 Contact opnemen",
            "en": "👨‍🏫 Contact Stephen"
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
            "nl": "💰 *Tarieven*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n🎓 *Voortgezet onderwijs 20+:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €200\n\n🎓 *Voortgezet onderwijs 20-:*\n• 1 les (1 uur): €75\n• 2 lessen (2 uur): €130\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n🎯 *MBO Rekentrajecten (alleen online, 18+):*\n• Spoedpakket: 1 week, 4 uur (€275)\n• Korte cursus: 4 weken, 4 uur (€225)\n• Volledig Commit: 12 weken, 13-14 uur (€550)\n• Volledig Flex: 12 weken, 13-14 uur (€690 in 3 termijnen)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n🎓 *Secondary education 20+:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €200\n\n🎓 *Secondary education 20-:*\n• 1 lesson (1 hour): €75\n• 2 lessons (2 hours): €130\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n🎯 *MBO Math trajectories (online only, 18+):*\n• Emergency: 1 week, 4 hours (€275)\n• Short course: 4 weeks, 4 hours (€225)\n• Full Commit: 12 weeks, 13-14 hours (€550)\n• Full Flex: 12 weeks, 13-14 hours (€690 in 3 installments)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        },
        "info_tariffs_no_mbo": {
            "nl": "💰 *Tarieven*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n🎓 *Voortgezet onderwijs 20+:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €200\n\n🎓 *Voortgezet onderwijs 20-:*\n• 1 les (1 uur): €75\n• 2 lessen (2 uur): €130\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n🎓 *Secondary education 20+:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €200\n\n🎓 *Secondary education 20-:*\n• 1 lesson (1 hour): €75\n• 2 lessons (2 hours): €130\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        },
        "info_tariffs_under_20": {
            "nl": "💰 *Tarieven (Onder 20 jaar)*\n\n🎓 *Voortgezet onderwijs:*\n• 1 les (1 uur): €75\n• 2 lessen (2 uur): €130\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €45 (1u) • €90 (2u) • €135 (4u)\n• 3-4 personen: €40 (1u) • €70 (2u) • €120 (4u)",
            "en": "💰 *Rates (Under 20 years)*\n\n🎓 *Secondary education:*\n• 1 lesson (1 hour): €75\n• 2 lessons (2 hours): €130\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €45 (1h) • €90 (2h) • €135 (4h)\n• 3-4 persons: €40 (1h) • €70 (2h) • €120 (4h)"
        },
        "info_tariffs_over_20": {
            "nl": "💰 *Tarieven (20 jaar en ouder)*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n🎓 *Voortgezet onderwijs:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n🎯 *MBO Rekentrajecten:*\n• Spoedpakket: 1 week, 4 uur (€275)\n• Korte cursus: 4 weken, 4 uur (€225)\n• Volledig Commit: 12 weken, 13-14 uur (€550)\n• Volledig Flex: 12 weken, 13-14 uur (€690 in 3 termijnen)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates (20 years and older)*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n🎓 *Secondary education:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n🎯 *MBO Math trajectories:*\n• Emergency: 1 week, 4 hours (€275)\n• Short course: 4 weeks, 4 hours (€225)\n• Full Commit: 12 weeks, 13-14 hours (€550)\n• Full Flex: 12 weeks, 13-14 hours (€690 in 3 installments)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        },
        "info_tariffs_over_20_no_mbo": {
            "nl": "💰 *Tarieven (20 jaar en ouder)*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n🎓 *Voortgezet onderwijs:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates (20 years and older)*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n🎓 *Secondary education:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        },
        "info_tariffs_vmbo_onderbouw": {
            "nl": "💰 *Tarieven voor middelbare school onderbouw*\n\n🎓 *Individuele lessen:*\n• 1 les (1 uur): €75\n• 2 lessen (2 uur): €130\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen (populair bij VMBO):*\n• 2 personen: €45 (1u) • €90 (2u) • €135 (4u)\n• 3-4 personen: €40 (1u) • €70 (2u) • €120 (4u)\n\n📚 Alle lessen zijn geschikt voor VMBO-niveau en kunnen zowel online als op locatie.",
            "en": "💰 *Rates for lower secondary school*\n\n🎓 *Individual lessons:*\n• 1 lesson (1 hour): €75\n• 2 lessons (2 hours): €130\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons (popular with VMBO):*\n• 2 persons: €45 (1h) • €90 (2h) • €135 (4h)\n• 3-4 persons: €40 (1h) • €70 (2h) • €120 (4h)\n\n📚 All lessons are suitable for VMBO level and can be both online and on location."
        },
        "info_travel_costs": {
            "nl": "🚗 *Reiskosten:*\n\n• VU/UvA (niet SP): €20\n• Thuis (Amsterdam): €50\n• Science Park: €0",
            "en": "🚗 *Travel costs:*\n\n• VU/UvA (not SP): €20\n• Home (Amsterdam): €50\n• Science Park: €0"
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
            "nl": "👨‍🏫 *Persoonlijke Achtergrond*\n\n*Stephen Adei - MSc Mathematics*\n• *MSc Mathematics* (Gespecialiseerd in quantum informatie en discrete wiskunde)\n• *Master Leraar* (Eerstegraads bevoegdheid in één keer)\n• 10+ jaar ervaring in onderwijs sinds 2012\n• Persoonlijke reis: Van wiskunde-uitdagingen naar excellente resultaten\n• Multidisciplinaire achtergrond: Wiskunde, programmeren, muziek, fotografie\n• Visie: Onderwijs moet empoweren, niet alleen kennis overdragen\n\n*Expertise:*\n• *Wiskunde*: Alle niveaus (basisonderwijs t/m universiteit)\n• *Quantum informatie*: Geavanceerde wiskundige concepten\n• *Discrete wiskunde*: Combinatoriek, grafentheorie, algoritmen\n• *Statistiek & data-analyse*: Praktische toepassingen\n• *Programmeren*: Python, R, SQL, Java, C#\n• *Onderwijskunde*: Evidence-based didactiek\n• *Eerstegraads bevoegdheid*: Volledige lesbevoegdheid\n\n*Motivatie:*\n• Ik weet hoe het voelt om vast te lopen in wiskunde\n• Persoonlijke begeleiding maakte het verschil voor mij\n• Nu help ik anderen om hun potentieel te bereiken\n• *Academische achtergrond* gecombineerd met *praktische onderwijservaring*",
            "en": "👨‍🏫 *Personal Background*\n\n*Stephen Adei - MSc Mathematics*\n• *MSc Mathematics* (Specialized in quantum information and discrete mathematics)\n• *Master Teacher* (First-degree teaching qualification in one go)\n• 10+ years of teaching experience since 2012\n• Personal journey: From math challenges to excellent results\n• Multidisciplinary background: Math, programming, music, photography\n• Vision: Education should empower, not just transfer knowledge\n\n*Expertise:*\n• *Mathematics*: All levels (primary education to university)\n• *Quantum information*: Advanced mathematical concepts\n• *Discrete mathematics*: Combinatorics, graph theory, algorithms\n• *Statistics & data analysis*: Practical applications\n• *Programming*: Python, R, SQL, Java, C#\n• *Educational science*: Evidence-based didactics\n• *First-degree qualification*: Full teaching qualification\n\n*Motivation:*\n• I know how it feels to get stuck in math\n• Personal guidance made the difference for me\n• Now I help others reach their potential\n• *Academic background* combined with *practical teaching experience*"
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
            "nl": "📚 *Mijn Diensten & Aanbod*\n\n🎓 *1. Privélessen & Bijles*\n*Vakken:*\n• *Basisonderwijs*: Rekenen, Taal\n• *Voortgezet Onderwijs*: Wiskunde A/B/C/D, Natuurkunde, Scheikunde, Engels\n• *Hoger Onderwijs*: Bedrijfsstatistiek, Calculus, Economie, Statistiek, Kansberekening, Lineaire Algebra, Verzamelingenleer\n• *Programmeren*: Python, Java, C#, C++, HTML, CSS, JavaScript, React, SQL, MATLAB, SPSS, R\n\n🎯 *2. MBO Rekenondersteuning (alleen online, 18+)*\n• *95% slagingspercentage* MBO-rekentoets\n• *500+ studenten* geholpen\n• *Gemiddelde beoordeling: 8.9/10*\n• Bewezen methoden en effectieve lesmaterialen\n• *Online trajecten* voor volwassen MBO-studenten\n\n*Rekentrajecten:*\n• *Spoedpakket*: 1 week, 4 uur (€275)\n• *Korte cursus*: 4 weken, 4 uur (€225)\n• *Volledig Commit*: 12 weken, 13-14 uur (€550)\n• *Volledig Flex*: 12 weken, 13-14 uur (€690 in 3 termijnen)\n\n📝 *3. Scriptiebegeleiding*\n• Methodologie en onderzoeksopzet\n• Statistische analyse (SPSS, R, Python)\n• Data-analyse en interpretatie\n• Structuur en planning\n• Eindredactie\n\n🎨 *4. Creatieve Workshops*\n• Muziekproductie & DJ (3 uur)\n• Analoge fotografie & bewerking (4 uur)\n• Visuele storytelling & design (3 uur)\n• Creatief coderen: Kunst & animatie (2 uur, 4 sessies)\n• AI & creativiteit (3 uur)\n• Escape room design (4 uur, 2 sessies)\n• Wiskundige kunst & patronen (3 uur)\n• Wiskundig verhalen vertellen (2.5 uur)\n• Wiskundige podcasting (3 uur, 2 sessies)\n• Educatieve wiskundevideo's (4 uur, 3 sessies)\n\n🎓 *5. Academische Workshops*\n• Statistiek project cursus (90 min, 6 sessies)\n• Wiskunde docenten innovatie (3 uur, 4 sessies)\n• AI & wiskunde (2 uur, 3 sessies)\n• Data visualisatie met Python (3 uur, 3 sessies)\n• Wiskundige spelontwikkeling (3 uur)\n• 3D wiskundig modelleren (3 uur, 4 sessies)\n• Innovatieve wiskundetoetsing (3 uur, 2 sessies)\n• Differentiatie in wiskundeonderwijs (3 uur, 3 sessies)\n• Mindfulness in wiskunde (2 uur)\n\n🧘 *6. Wellness Workshops*\n• Mindfulness (2 uur)\n• Tijdmanagement (2.5 uur)\n• Examenvoorbereiding (3 uur, 3 sessies)\n\n💼 *7. Consultancy & Advies*\n• Data-analyse en statistische modellering\n• Onderzoeksmethodologie\n• Machine learning en AI\n• Software ontwikkeling",
            "en": "📚 *My Services & Offerings*\n\n🎓 *1. Private Lessons & Tutoring*\n*Subjects:*\n• *Primary Education*: Math, Language\n• *Secondary Education*: Math A/B/C/D, Physics, Chemistry, English\n• *Higher Education*: Business Statistics, Calculus, Economics, Statistics, Probability, Linear Algebra, Set Theory\n• *Programming*: Python, Java, C#, C++, HTML, CSS, JavaScript, React, SQL, MATLAB, SPSS, R\n\n🎯 *2. MBO Math Support (online only, 18+)*\n• *95% pass rate* MBO math test\n• *500+ students* helped\n• *Average rating: 8.9/10*\n• Proven methods and effective teaching materials\n• *Online trajectories* for adult MBO students\n\n*Math trajectories:*\n• *Emergency*: 1 week, 4 hours (€275)\n• *Short course*: 4 weeks, 4 hours (€225)\n• *Full Commit*: 12 weeks, 13-14 hours (€550)\n• *Full Flex*: 12 weeks, 13-14 hours (€690 in 3 installments)\n\n📝 *3. Thesis Guidance*\n• Methodology and research design\n• Statistical analysis (SPSS, R, Python)\n• Data analysis and interpretation\n• Structure and planning\n• Final editing\n\n🎨 *4. Creative Workshops*\n• Music production & DJ (3 hours)\n• Analog photography & editing (4 hours)\n• Visual storytelling & design (3 hours)\n• Creative coding: Art & animation (2 hours, 4 sessions)\n• AI & creativity (3 hours)\n• Escape room design (4 hours, 2 sessions)\n• Mathematical art & patterns (3 hours)\n• Mathematical storytelling (2.5 hours)\n• Mathematical podcasting (3 hours, 2 sessions)\n• Educational math videos (4 hours, 3 sessions)\n\n🎓 *5. Academic Workshops*\n• Statistics project course (90 min, 6 sessions)\n• Math teacher innovation (3 hours, 4 sessions)\n• AI & mathematics (2 hours, 3 sessions)\n• Data visualization with Python (3 hours, 3 sessions)\n• Mathematical game development (3 hours)\n• 3D mathematical modeling (3 hours, 4 sessions)\n• Innovative math testing (3 hours, 2 sessions)\n• Differentiation in math education (3 hours, 3 sessions)\n• Mindfulness in mathematics (2 hours)\n\n🧘 *6. Wellness Workshops*\n• Mindfulness (2 hours)\n• Time management (2.5 hours)\n• Exam preparation (3 hours, 3 sessions)\n\n💼 *7. Consultancy & Advice*\n• Data analysis and statistical modeling\n• Research methodology\n• Machine learning and AI\n• Software development"
        },
        "info_weekend_programs": {
            "nl": "🌅 *Weekend Programma's (Amsterdam Zuidoost)*\n\n🇬🇭 *Boa me na menboa mo (Ghanese gemeenschap):*\n• *50% korting* voor Ghanese jongeren: €30/uur i.p.v. €60\n• *Locatie*: Douwe Egberts (Dubbelink 2) of aan huis in Gein\n• *Tijden*: Zaterdag en zondag, flexibele tijden\n• *Gratis proefles* van 30 minuten\n\n🌅 *Weekend Bijles Zuidoost:*\n• *50% korting*: €30/uur i.p.v. €60\n• *Zelfde locaties* en tijden\n• *Voor alle bewoners* van Zuidoost\n\n📍 *Locaties:*\n• Douwe Egberts (Dubbelink 2, Amsterdam Zuidoost)\n• Aan huis in Gein en omgeving\n• Bijlmerplein 888, 1102 MG Amsterdam\n\n⏰ *Beschikbaarheid:*\n• Zaterdag: 10:00–18:00\n• Zondag: 10:00–18:00\n• Flexibele tijden mogelijk\n\n🎯 *Speciale Kenmerken:*\n• *Community focus*: Toegankelijke tarieven voor verschillende doelgroepen\n• *Ervaring met speciale behoeften*: Ervaring met leerlingen met lichte autisme\n• *Gestructureerde en geduldige leeromgeving*\n• *Aanpassing aan specifieke behoeften*\n\n📞 *Contact:*\n• Telefoon: +31 6 47357426\n• Email: info@stephenadei.nl\n• Website: stephensprivelessen.nl",
            "en": "🌅 *Weekend Programs (Amsterdam Southeast)*\n\n🇬🇭 *Boa me na menboa mo (Ghanaian community):*\n• *50% discount* for Ghanaian youth: €30/hour instead of €60\n• *Location*: Douwe Egberts (Dubbelink 2) or at home in Gein\n• *Times*: Saturday and Sunday, flexible times\n• *Free trial lesson* of 30 minutes\n\n🌅 *Weekend Tutoring Southeast:*\n• *50% discount*: €30/hour instead of €60\n• *Same locations* and times\n• *For all residents* of Southeast\n\n📍 *Locations:*\n• Douwe Egberts (Dubbelink 2, Amsterdam Southeast)\n• At home in Gein and surrounding area\n• Bijlmerplein 888, 1102 MG Amsterdam\n\n⏰ *Availability:*\n• Saturday: 10:00–18:00\n• Sunday: 10:00–18:00\n• Flexible times possible\n\n🎯 *Special Features:*\n• *Community focus*: Accessible rates for different target groups\n• *Experience with special needs*: Experience with students with mild autism\n• *Structured and patient learning environment*\n• *Adaptation to specific needs*\n\n📞 *Contact:*\n• Phone: +31 6 47357426\n• Email: info@stephenadei.nl\n• Website: stephensprivelessen.nl"
        },
        "info_short_version": {
            "nl": "📝 *Korte versie:*\n\nHO: 1× €90 • 2× €140 • 4× €250\nVO 20+: 1× €80 • 2× €135 • 4× €200\nVO 20-: 1× €75 • 2× €130 • 4× €200\n\nReiskosten: VU/UvA (niet SP) €20 • Thuis (AMS e.o.) €50 • Science Park €0\n\nLast-minute: <24u +20% • <12u +50%\n\nPakketten: 2× geldig 2 weken • 4× geldig 1 maand; bij directe planning loopt geldigheid vanaf 1e les. Flex-premium (alleen bij niet-direct plannen): +€15 (2×) / +€30 (4×).",
            "en": "📝 *Short version:*\n\nHE: 1× €90 • 2× €140 • 4× €250\nSE 20+: 1× €80 • 2× €135 • 4× €200\nSE 20-: 1× €75 • 2× €130 • 4× €200\n\nTravel: VU/UvA (not SP) €20 • Home (AMS area) €50 • Science Park €0\n\nLast-minute: <24h +20% • <12h +50%\n\nPackages: 2× valid 2 weeks • 4× valid 1 month; with direct scheduling validity runs from 1st lesson. Flex-premium (only when not scheduling directly): +€15 (2×) / +€30 (4×)."
        },
        "info_personal_background": {
            "nl": "👨‍🏫 *Persoonlijke Achtergrond & Motivatie*\n\n*Stephen Adei* - MSc Mathematics (Gespecialiseerd in quantum informatie en discrete wiskunde)\n• *Master Leraar* (Eerstegraads bevoegdheid in één keer)\n• *10+ jaar ervaring* sinds 2012 in onderwijs en begeleiding\n• *Persoonlijke reis*: Van wiskunde-uitdagingen (gemiddelde 5 in 3e jaar) naar excellente resultaten (gemiddelde 10 in 4e/5e jaar)\n• *Expertise*: Wiskunde, quantum informatie, discrete wiskunde, statistiek, data-analyse, multidisciplinaire achtergrond\n• *Passie*: Deze ervaring inspireerde tot het helpen van anderen met vergelijkbare uitdagingen\n\n*Visie & Filosofie:*\n• *Onderwijs moet empoweren*, niet alleen kennis overdragen\n• *Elke student kan leren*, mits de juiste begeleiding en motivatie\n• *Persoonlijke groei* staat centraal in mijn aanpak\n• *Zelfvertrouwen* is de basis voor succesvol leren\n\n*Academische Kwalificaties:*\n• *MSc Mathematics*: Gespecialiseerd in quantum informatie en discrete wiskunde\n• *Master Leraar*: Eerstegraads bevoegdheid (volledige lesbevoegdheid)\n• *Evidence-based didactiek*: Wetenschappelijk onderbouwde onderwijsmethoden\n• *Academische achtergrond* gecombineerd met *praktische onderwijservaring*\n\n*Multidisciplinaire Achtergrond:*\n• *Wiskunde & Statistiek*: Academische achtergrond en praktische toepassingen\n• *Quantum informatie*: Geavanceerde wiskundige concepten en algoritmen\n• *Discrete wiskunde*: Combinatoriek, grafentheorie, algoritmen\n• *Programmeren*: Python, Java, C#, C++, web development\n• *Muziek & Creativiteit*: Muziekproductie, DJ, creatieve workshops\n• *Fotografie & Design*: Analoge fotografie, visuele storytelling\n• *AI & Innovatie*: Integratie van moderne technologie in onderwijs\n\n*Community Focus:*\n• *Ghanese gemeenschap*: Speciale programma's en ondersteuning\n• *Amsterdam Zuidoost*: Weekend programma's met toegankelijke tarieven\n• *Inclusiviteit*: Ervaring met diverse leerstijlen en speciale behoeften",
            "en": "👨‍🏫 *Personal Background & Motivation*\n\n*Stephen Adei* - MSc Mathematics (Specialized in quantum information and discrete mathematics)\n• *Master Teacher* (First-degree teaching qualification in one go)\n• *10+ years of experience* since 2012 in education and guidance\n• *Personal journey*: From math challenges (average 5 in 3rd year) to excellent results (average 10 in 4th/5th year)\n• *Expertise*: Mathematics, quantum information, discrete mathematics, statistics, data analysis, multidisciplinary background\n• *Passion*: This experience inspired helping others with similar challenges\n\n*Vision & Philosophy:*\n• *Education should empower*, not just transfer knowledge\n• *Every student can learn*, given the right guidance and motivation\n• *Personal growth* is central to my approach\n• *Self-confidence* is the foundation for successful learning\n\n*Academic Qualifications:*\n• *MSc Mathematics*: Specialized in quantum information and discrete mathematics\n• *Master Teacher*: First-degree teaching qualification (full teaching qualification)\n• *Evidence-based didactics*: Scientifically supported teaching methods\n• *Academic background* combined with *practical teaching experience*\n\n*Multidisciplinary Background:*\n• *Mathematics & Statistics*: Academic background and practical applications\n• *Quantum information*: Advanced mathematical concepts and algorithms\n• *Discrete mathematics*: Combinatorics, graph theory, algorithms\n• *Programming*: Python, Java, C#, C++, web development\n• *Music & Creativity*: Music production, DJ, creative workshops\n• *Photography & Design*: Analog photography, visual storytelling\n• *AI & Innovation*: Integration of modern technology in education\n\n*Community Focus:*\n• *Ghanaian community*: Special programs and support\n• *Amsterdam Southeast*: Weekend programs with accessible rates\n• *Inclusivity*: Experience with diverse learning styles and special needs"
        },
        "info_didactic_methods": {
            "nl": "📚 *Didactische Aanpak & Methodiek*\n\n*Diagnostisch Werken:*\n• *Intake gesprek*: Start altijd met een uitgebreide intake om niveau, leerstijl en doelen te bepalen\n• *Leerdoelanalyse*: Identificeer specifieke uitdagingen en sterke punten\n• *Voorkennis assessment*: Bepaal het startniveau en voorkennis\n• *Leerstijl bepaling*: Visueel, auditief, kinesthetisch of combinatie\n\n*Leerdoelgericht Onderwijs:*\n• *SMART doelen*: Specifieke, meetbare, haalbare, relevante en tijdsgebonden doelen\n• *Stapsgewijze opbouw*: Complexe stof opdelen in behapbare stappen\n• *Voortgangsmonitoring*: Regelmatige evaluatie van leerdoelen\n• *Aanpassing*: Flexibele aanpassing van doelen op basis van voortgang\n\n*Activerende Didactiek:*\n• *Samen oefenen*: Interactieve oefeningen en samenwerking\n• *Uitleggen aan elkaar*: Peer teaching en kennis delen\n• *Real-life voorbeelden*: Praktische toepassingen en context\n• *Reflectie*: Regelmatige reflectie op leerproces en resultaten\n• *Probleemgestuurd leren*: Uitdagende problemen als startpunt\n\n*Formatieve Evaluatie:*\n• *Korte toetsmomenten*: Regelmatige korte assessments\n• *Directe feedback*: Onmiddellijke feedback tijdens lessen\n• *Zelfevaluatie*: Stimuleren van zelfreflectie bij leerlingen\n• *Ouderbetrokkenheid*: Regelmatige updates en feedback\n\n*Zelfregulatie & Metacognitie:*\n• *Planningsvaardigheden*: Leren plannen en organiseren\n• *Zelfmonitoring*: Eigen voortgang bijhouden en evalueren\n• *Strategieontwikkeling*: Ontwikkelen van eigen leerstrategieën\n• *Motivatiebehoud*: Technieken voor het behouden van motivatie\n\n*Differentiatie & Inclusiviteit:*\n• *Scaffolding*: Ondersteuning die geleidelijk wordt afgebouwd\n• *Tempo-aanpassing*: Verschillende snelheden per leerling\n• *Materiaal-aanpassing*: Verschillende werkvormen en materialen\n• *Ervaring met speciale behoeften*: Autisme, dyscalculie, ADHD, NT2\n• *Visuele, auditieve en kinesthetische leermiddelen*",
            "en": "📚 *Didactic Approach & Methodology*\n\n*Diagnostic Work:*\n• *Intake conversation*: Always start with comprehensive intake to determine level, learning style and goals\n• *Learning goal analysis*: Identify specific challenges and strengths\n• *Prior knowledge assessment*: Determine starting level and prior knowledge\n• *Learning style determination*: Visual, auditory, kinesthetic or combination\n\n*Goal-Oriented Education:*\n• *SMART goals*: Specific, measurable, achievable, relevant and time-bound goals\n• *Step-by-step building*: Breaking complex material into manageable steps\n• *Progress monitoring*: Regular evaluation of learning goals\n• *Adaptation*: Flexible adjustment of goals based on progress\n\n*Activating Didactics:*\n• *Practice together*: Interactive exercises and collaboration\n• *Explain to each other*: Peer teaching and knowledge sharing\n• *Real-life examples*: Practical applications and context\n• *Reflection*: Regular reflection on learning process and results\n• *Problem-based learning*: Challenging problems as starting point\n\n*Formative Evaluation:*\n• *Short test moments*: Regular short assessments\n• *Direct feedback*: Immediate feedback during lessons\n• *Self-evaluation*: Encouraging self-reflection in students\n• *Parent involvement*: Regular updates and feedback\n\n*Self-Regulation & Metacognition:*\n• *Planning skills*: Learning to plan and organize\n• *Self-monitoring*: Tracking and evaluating own progress\n• *Strategy development*: Developing own learning strategies\n• *Motivation maintenance*: Techniques for maintaining motivation\n\n*Differentiation & Inclusivity:*\n• *Scaffolding*: Support that is gradually reduced\n• *Pace adjustment*: Different speeds per student\n• *Material adaptation*: Different work forms and materials\n• *Experience with special needs*: Autism, dyscalculia, ADHD, NT2\n• *Visual, auditory and kinesthetic learning materials*"
        },
        "info_technology_tools": {
            "nl": "💻 *Technologie & Tools*\n\n*Digitale Aantekeningen & Organisatie:*\n• *iPad met Apple Pencil*: Digitale aantekeningen tijdens lessen\n• *GoodNotes*: Professionele notitie-app met OCR en organisatie\n• *Notion*: Kennisbank en organisatie van lesmaterialen\n• *Google Classroom*: Delen van materialen en opdrachten\n• *Digitale aantekeningen*: Na elke les gedeeld met leerlingen\n\n*AI & Innovatie:*\n• *ChatGPT*: Conceptverduidelijking en gepersonaliseerde uitleg\n• *AI-tools*: Voor oefenmateriaal en adaptieve leerpaden\n• *Gepersonaliseerde oefening*: AI-gestuurde aanbevelingen\n• *Huiswerk ondersteuning*: AI als hulpmiddel bij vragen\n\n*Online Lesgeven:*\n• *Zoom/Google Meet*: Professionele videoconferentie\n• *Online whiteboards*: Interactieve uitleg en samenwerking\n• *Scherm delen*: Demonstraties en presentaties\n• *Video-opnames*: Van uitleg op verzoek beschikbaar\n• *Chat functionaliteit*: Real-time vragen en antwoorden\n\n*Communicatie & Ondersteuning:*\n• *WhatsApp*: 7 dagen ondersteuning na elke les\n• *Reactietijd*: Binnen 24 uur op alle vragen\n• *Check-ins*: Korte motivatie- en planningsgesprekken\n• *FAQ systeem*: Kennisbank voor veelgestelde vragen\n• *Ouder communicatie*: Regelmatige updates en feedback\n\n*Praktische Tools:*\n• *Online boekingssysteem*: Eenvoudige planning en reminders\n• *Betaling integratie*: Veilige online betalingen\n• *Voortgangsmonitoring*: Digitale tracking van resultaten\n• *Evaluatieformulieren*: Anonieme feedback verzameling\n• *Kalender integratie*: Automatische herinneringen\n\n*Materiaal & Bronnen:*\n• *Digitale bibliotheek*: Uitgebreide collectie oefenmateriaal\n• *Video tutorials*: Stap-voor-stap uitleg van concepten\n• *Interactieve oefeningen*: Online quizzes en assessments\n• *E-books*: Digitale lesmaterialen en handleidingen\n• *Podcasts*: Audio content voor verschillende leerstijlen",
            "en": "💻 *Technology & Tools*\n\n*Digital Notes & Organization:*\n• *iPad with Apple Pencil*: Digital notes during lessons\n• *GoodNotes*: Professional note app with OCR and organization\n• *Notion*: Knowledge base and organization of teaching materials\n• *Google Classroom*: Sharing materials and assignments\n• *Digital notes*: Shared with students after each lesson\n\n*AI & Innovation:*\n• *ChatGPT*: Concept clarification and personalized explanation\n• *AI tools*: For practice materials and adaptive learning paths\n• *Personalized practice*: AI-driven recommendations\n• *Homework support*: AI as aid for questions\n\n*Online Teaching:*\n• *Zoom/Google Meet*: Professional video conferencing\n• *Online whiteboards*: Interactive explanation and collaboration\n• *Screen sharing*: Demonstrations and presentations\n• *Video recordings*: Available on request\n• *Chat functionality*: Real-time questions and answers\n\n*Communication & Support:*\n• *WhatsApp*: 7 days support after each lesson\n• *Response time*: Within 24 hours on all questions\n• *Check-ins*: Short motivation and planning conversations\n• *FAQ system*: Knowledge base for frequently asked questions\n• *Parent communication*: Regular updates and feedback\n\n*Practical Tools:*\n• *Online booking system*: Easy planning and reminders\n• *Payment integration*: Secure online payments\n• *Progress monitoring*: Digital tracking of results\n• *Evaluation forms*: Anonymous feedback collection\n• *Calendar integration*: Automatic reminders\n\n*Materials & Resources:*\n• *Digital library*: Extensive collection of practice materials\n• *Video tutorials*: Step-by-step explanation of concepts\n• *Interactive exercises*: Online quizzes and assessments\n• *E-books*: Digital teaching materials and manuals\n• *Podcasts*: Audio content for different learning styles"
        },
        "info_results_success": {
            "nl": "🏆 *Resultaten & Succesverhalen*\n\n*Kwantitatieve Resultaten:*\n• *500+ studenten* geholpen sinds 2012\n• *98% studenttevredenheid* op evaluaties\n• *Gemiddelde beoordeling: 4.9/5* sterren\n• *95% slagingspercentage* MBO-rekentoets\n• *Gemiddelde cijferstijging*: Aantoonbare verbetering in resultaten\n• *Succesvolle CCVX-examens*: Hoge slagingspercentages\n\n*Kwalitatieve Impact:*\n• *Zelfvertrouwen*: Significante toename in zelfvertrouwen bij leerlingen\n• *Motivatie*: Verbeterde motivatie en betrokkenheid\n• *Zelfstandigheid*: Ontwikkeling van zelfstandige leerstrategieën\n• *Doorzettingsvermogen*: Betere coping met uitdagingen\n• *Toekomstperspectief*: Duidelijkere visie op studie- en carrièrekeuzes\n\n*Specifieke Succesverhalen:*\n• *MBO-studenten*: Van onvoldoende naar voldoende op rekentoets\n• *Havo/Vwo leerlingen*: Van 4-5 naar 7-8 gemiddeld\n• *Hoger onderwijs*: Succesvolle afronding van moeilijke vakken\n• *CCVX-examens*: Hoge slagingspercentages voor universitaire toelating\n• *Scriptiebegeleiding*: Succesvolle afronding van onderzoeken\n\n*Community Impact:*\n• *Ghanese gemeenschap*: Toegankelijk onderwijs voor jongeren\n• *Amsterdam Zuidoost*: Betaalbare kwaliteitsonderwijs\n• *Speciale behoeften*: Inclusief onderwijs voor diverse leerlingen\n• *Ouderbetrokkenheid*: Positieve feedback van ouders\n\n*Langetermijn Resultaten:*\n• *Studievoortgang*: Verbeterde studieprestaties op langere termijn\n• *Carrière ontwikkeling*: Betere voorbereiding op vervolgstudies\n• *Leerhouding*: Duurzame verandering in leerattitude\n• *Netwerk*: Opbouw van ondersteunende netwerken\n\n*Testimonials & Ervaringen:*\n• *Leerling testimonials*: Persoonlijke verhalen van vooruitgang\n• *Ouder feedback*: Positieve ervaringen van ouders\n• *School feedback*: Samenwerking met scholen en docenten\n• *Peer reviews*: Erkenning van collega's in het onderwijsveld",
            "en": "🏆 *Results & Success Stories*\n\n*Quantitative Results:*\n• *500+ students* helped since 2012\n• *98% student satisfaction* on evaluations\n• *Average rating: 4.9/5* stars\n• *95% pass rate* MBO math test\n• *Average grade improvement*: Demonstrable improvement in results\n• *Successful CCVX exams*: High pass rates\n\n*Qualitative Impact:*\n• *Self-confidence*: Significant increase in student confidence\n• *Motivation*: Improved motivation and engagement\n• *Independence*: Development of independent learning strategies\n• *Perseverance*: Better coping with challenges\n• *Future perspective*: Clearer vision of study and career choices\n\n*Specific Success Stories:*\n• *MBO students*: From insufficient to sufficient on math test\n• *Havo/Vwo students*: From 4-5 to 7-8 average\n• *Higher education*: Successful completion of difficult subjects\n• *CCVX exams*: High pass rates for university admission\n• *Thesis guidance*: Successful completion of research\n\n*Community Impact:*\n• *Ghanaian community*: Accessible education for youth\n• *Amsterdam Southeast*: Affordable quality education\n• *Special needs*: Inclusive education for diverse students\n• *Parent involvement*: Positive feedback from parents\n\n*Long-term Results:*\n• *Study progress*: Improved academic performance in the long term\n• *Career development*: Better preparation for further studies\n• *Learning attitude*: Sustainable change in learning attitude\n• *Network*: Building supportive networks\n\n*Testimonials & Experiences:*\n• *Student testimonials*: Personal stories of progress\n• *Parent feedback*: Positive experiences from parents\n• *School feedback*: Collaboration with schools and teachers\n• *Peer reviews*: Recognition from colleagues in education"
        },
        "info_workshops_creative": {
            "nl": "🎨 *Creatieve Workshops & Cursussen*\n\n*Muziek & Audio:*\n• *Muziekproductie & DJ* (3 uur)\n  - Basis van muziekproductie en DJ-technieken\n  - Praktische ervaring met apparatuur\n  - Creatieve expressie door muziek\n\n• *Wiskundige podcasting* (3 uur, 2 sessies)\n  - Combineren van wiskunde en storytelling\n  - Audio editing en productie\n  - Educatieve content creatie\n\n*Fotografie & Visuele Kunsten:*\n• *Analoge fotografie & bewerking* (4 uur)\n  - Traditionele fotografie technieken\n  - Darkroom processen en bewerking\n  - Artistieke visuele expressie\n\n• *Visuele storytelling & design* (3 uur)\n  - Verhalen vertellen door beeld\n  - Design principes en creativiteit\n  - Digitale en analoge technieken\n\n*Creatief Coderen & Technologie:*\n• *Creatief coderen: Kunst & animatie* (2 uur, 4 sessies)\n  - Programmeren voor artistieke doeleinden\n  - Animaties en visuele effecten\n  - Interactieve kunstinstallaties\n\n• *AI & creativiteit* (3 uur)\n  - Kunstmatige intelligentie in creatieve processen\n  - AI-tools voor kunst en design\n  - Toekomst van creatieve technologie\n\n*Wiskundige Kunst & Patronen:*\n• *Wiskundige kunst & patronen* (3 uur)\n  - Wiskunde als basis voor kunst\n  - Geometrische patronen en fractals\n  - Wiskundige schoonheid in kunst\n\n• *Wiskundig verhalen vertellen* (2.5 uur)\n  - Verhalen met wiskundige concepten\n  - Educatieve storytelling\n  - Wiskunde toegankelijk maken\n\n*Interactieve & Gamification:*\n• *Escape room design* (4 uur, 2 sessies)\n  - Puzzel design en logica\n  - Interactieve ervaringen\n  - Teamwork en probleemoplossing\n\n• *Educatieve wiskundevideo's* (4 uur, 3 sessies)\n  - Video productie voor onderwijs\n  - Visuele uitleg van concepten\n  - Digitale content creatie\n\n*Workshop Kenmerken:*\n• *Kleine groepen*: Persoonlijke aandacht en begeleiding\n• *Praktisch gericht*: Hands-on ervaring en experimenteren\n• *Interdisciplinair*: Combineren van verschillende vakgebieden\n• *Creatieve vrijheid*: Ruimte voor eigen interpretatie en expressie\n• *Technologie integratie*: Moderne tools en technieken\n• *Community focus*: Samenwerking en kennis delen",
            "en": "🎨 *Creative Workshops & Courses*\n\n*Music & Audio:*\n• *Music production & DJ* (3 hours)\n  - Basics of music production and DJ techniques\n  - Practical experience with equipment\n  - Creative expression through music\n\n• *Mathematical podcasting* (3 hours, 2 sessions)\n  - Combining mathematics and storytelling\n  - Audio editing and production\n  - Educational content creation\n\n*Photography & Visual Arts:*\n• *Analog photography & editing* (4 hours)\n  - Traditional photography techniques\n  - Darkroom processes and editing\n  - Artistic visual expression\n\n• *Visual storytelling & design* (3 hours)\n  - Storytelling through images\n  - Design principles and creativity\n  - Digital and analog techniques\n\n*Creative Coding & Technology:*\n• *Creative coding: Art & animation* (2 hours, 4 sessions)\n  - Programming for artistic purposes\n  - Animations and visual effects\n  - Interactive art installations\n\n• *AI & creativity* (3 hours)\n  - Artificial intelligence in creative processes\n  - AI tools for art and design\n  - Future of creative technology\n\n*Mathematical Art & Patterns:*\n• *Mathematical art & patterns* (3 hours)\n  - Mathematics as basis for art\n  - Geometric patterns and fractals\n  - Mathematical beauty in art\n\n• *Mathematical storytelling* (2.5 hours)\n  - Stories with mathematical concepts\n  - Educational storytelling\n  - Making mathematics accessible\n\n*Interactive & Gamification:*\n• *Escape room design* (4 hours, 2 sessions)\n  - Puzzle design and logic\n  - Interactive experiences\n  - Teamwork and problem solving\n\n• *Educational math videos* (4 hours, 3 sessions)\n  - Video production for education\n  - Visual explanation of concepts\n  - Digital content creation\n\n*Workshop Features:*\n• *Small groups*: Personal attention and guidance\n• *Practical focus*: Hands-on experience and experimentation\n• *Interdisciplinary*: Combining different fields\n• *Creative freedom*: Space for own interpretation and expression\n• *Technology integration*: Modern tools and techniques\n• *Community focus*: Collaboration and knowledge sharing"
        },
        "info_workshops_academic": {
            "nl": "🎓 *Academische Workshops & Cursussen*\n\n*Statistiek & Data Analyse:*\n• *Statistiek project cursus* (90 min, 6 sessies)\n  - Praktische statistische analyses\n  - Project-gebaseerd leren\n  - Real-world data toepassingen\n\n• *Data visualisatie met Python* (3 uur, 3 sessies)\n  - Python voor data analyse\n  - Visuele presentatie van data\n  - Interactieve grafieken en dashboards\n\n*Wiskunde & Onderwijs:*\n• *Wiskunde docenten innovatie* (3 uur, 4 sessies)\n  - Nieuwe didactische methoden\n  - Technologie in wiskundeonderwijs\n  - Differentiatie en inclusiviteit\n\n• *AI & wiskunde* (2 uur, 3 sessies)\n  - Kunstmatige intelligentie in wiskunde\n  - AI-tools voor wiskundeonderwijs\n  - Toekomst van wiskundeonderwijs\n\n• *Wiskundige spelontwikkeling* (3 uur)\n  - Games voor wiskundeonderwijs\n  - Gamification van leren\n  - Interactieve wiskunde\n\n*3D & Modellering:*\n• *3D wiskundig modelleren* (3 uur, 4 sessies)\n  - 3D visualisatie van wiskundige concepten\n  - Moderne modelleringstechnieken\n  - Praktische toepassingen\n\n*Onderwijs Innovatie:*\n• *Innovatieve wiskundetoetsing* (3 uur, 2 sessies)\n  - Moderne toetsmethoden\n  - Formatief toetsen\n  - Technologie in toetsing\n\n• *Differentiatie in wiskundeonderwijs* (3 uur, 3 sessies)\n  - Individuele aanpak in groepen\n  - Scaffolding technieken\n  - Inclusief onderwijs\n\n• *Mindfulness in wiskunde* (2 uur)\n  - Stress reductie bij wiskunde\n  - Focus en concentratie\n  - Positieve leerhouding\n\n*Wellness & Studievaardigheden:*\n• *Mindfulness* (2 uur)\n  - Meditatie en bewustzijn\n  - Stress management\n  - Emotionele balans\n\n• *Tijdmanagement* (2.5 uur)\n  - Studieplanning en organisatie\n  - Prioriteiten stellen\n  - Effectief leren\n\n• *Examenvoorbereiding* (3 uur, 3 sessies)\n  - Strategieën voor examens\n  - Angst en stress management\n  - Optimale voorbereiding\n\n*Workshop Kenmerken:*\n• *Evidence-based*: Gebaseerd op wetenschappelijk onderzoek\n• *Praktisch toepasbaar*: Direct bruikbaar in onderwijs\n• *Interactief*: Actieve deelname en discussie\n• *Flexibel*: Aanpasbaar aan verschillende niveaus\n• *Ondersteunend materiaal*: Handouts, digitale bronnen, oefeningen\n• *Follow-up*: Vervolg ondersteuning en coaching\n\n*Doelgroepen:*\n• *Docenten*: Professionalisering en innovatie\n• *Studenten*: Studievaardigheden en zelfvertrouwen\n• *Ouders*: Ondersteuning bij begeleiding\n• *Professionals*: Werkgerelateerde vaardigheden",
            "en": "🎓 *Academic Workshops & Courses*\n\n*Statistics & Data Analysis:*\n• *Statistics project course* (90 min, 6 sessions)\n  - Practical statistical analyses\n  - Project-based learning\n  - Real-world data applications\n\n• *Data visualization with Python* (3 hours, 3 sessions)\n  - Python for data analysis\n  - Visual presentation of data\n  - Interactive graphs and dashboards\n\n*Mathematics & Education:*\n• *Math teacher innovation* (3 hours, 4 sessions)\n  - New didactic methods\n  - Technology in mathematics education\n  - Differentiation and inclusivity\n\n• *AI & mathematics* (2 hours, 3 sessions)\n  - Artificial intelligence in mathematics\n  - AI tools for mathematics education\n  - Future of mathematics education\n\n• *Mathematical game development* (3 hours)\n  - Games for mathematics education\n  - Gamification of learning\n  - Interactive mathematics\n\n*3D & Modeling:*\n• *3D mathematical modeling* (3 hours, 4 sessions)\n  - 3D visualization of mathematical concepts\n  - Modern modeling techniques\n  - Practical applications\n\n*Educational Innovation:*\n• *Innovative mathematics testing* (3 hours, 2 sessions)\n  - Modern testing methods\n  - Formative assessment\n  - Technology in testing\n\n• *Differentiation in mathematics education* (3 hours, 3 sessions)\n  - Individual approach in groups\n  - Scaffolding techniques\n  - Inclusive education\n\n• *Mindfulness in mathematics* (2 hours)\n  - Stress reduction in mathematics\n  - Focus and concentration\n  - Positive learning attitude\n\n*Wellness & Study Skills:*\n• *Mindfulness* (2 hours)\n  - Meditation and awareness\n  - Stress management\n  - Emotional balance\n\n• *Time management* (2.5 hours)\n  - Study planning and organization\n  - Setting priorities\n  - Effective learning\n\n• *Exam preparation* (3 hours, 3 sessions)\n  - Strategies for exams\n  - Anxiety and stress management\n  - Optimal preparation\n\n*Workshop Features:*\n• *Evidence-based*: Based on scientific research\n• *Practically applicable*: Directly usable in education\n• *Interactive*: Active participation and discussion\n• *Flexible*: Adaptable to different levels\n• *Supporting materials*: Handouts, digital resources, exercises\n• *Follow-up*: Continued support and coaching\n\n*Target Groups:*\n• *Teachers*: Professionalization and innovation\n• *Students*: Study skills and self-confidence\n• *Parents*: Support in guidance\n• *Professionals*: Work-related skills"
        },
        "info_consultancy": {
            "nl": "💼 *Consultancy & Advies*\n\n*Data-analyse & Statistische Modellering:*\n• *Statistische analyses*: Uitgebreide data-analyse en interpretatie\n• *Predictive modeling*: Voorspellende modellen en trends\n• *Data visualisatie*: Interactieve dashboards en rapporten\n• *Kwaliteitscontrole*: Statistische kwaliteitsborging\n• *Onderzoeksdesign*: Experimentele opzet en methodologie\n\n*Onderzoeksmethodologie:*\n• *Onderzoeksopzet*: Design van wetenschappelijke studies\n• *Steekproefmethoden*: Representatieve dataverzameling\n• *Validatie*: Betrouwbaarheid en validiteit van onderzoek\n• *Ethiek*: Onderzoeksethiek en privacybescherming\n• *Rapportage*: Wetenschappelijke rapportage en presentatie\n\n*Machine Learning & AI:*\n• *Algoritme ontwikkeling*: Custom machine learning modellen\n• *Data preprocessing*: Data cleaning en feature engineering\n• *Model evaluatie*: Performance assessment en validatie\n• *AI implementatie*: Praktische toepassingen van AI\n• *Ethische AI*: Verantwoorde AI ontwikkeling\n\n*Software Ontwikkeling:*\n• *Web development*: Frontend en backend ontwikkeling\n• *Database design*: Data architectuur en optimalisatie\n• *API ontwikkeling*: Integratie en systeemkoppeling\n• *Testing & QA*: Kwaliteitsborging en debugging\n• *Deployment*: Implementatie en onderhoud\n\n*Consultancy Aanpak:*\n\n*1. Eerste Gesprek & Behoefteanalyse*\n• Intake gesprek om doelen en uitdagingen te begrijpen\n• Analyse van huidige situatie en wensen\n• Bepaling van scope en verwachtingen\n• Opstellen van projectplan en tijdlijn\n\n*2. Data-evaluatie & Assessment*\n• Analyse van beschikbare data en systemen\n• Identificatie van verbeterpunten en kansen\n• Assessment van technische infrastructuur\n• Benchmarking tegen best practices\n\n*3. Oplossing Ontwerp*\n• Ontwikkeling van maatwerk oplossingen\n• Technische specificaties en architectuur\n• Implementatie strategie en planning\n• Risico analyse en mitigatie\n\n*4. Implementatie & Begeleiding*\n• Stapsgewijze implementatie van oplossingen\n• Training en kennisoverdracht\n• Monitoring en evaluatie van resultaten\n• Continue ondersteuning en optimalisatie\n\n*5. Kennisoverdracht & Ondersteuning*\n• Documentatie en handleidingen\n• Training van medewerkers\n• Best practices en procedures\n• Langdurige ondersteuning en onderhoud\n\n*Sectoren & Toepassingen:*\n• *Onderwijs*: Onderwijstechnologie en data-analyse\n• *Healthcare*: Medische data-analyse en statistiek\n• *Finance*: Financiële modellering en risico-analyse\n• *Marketing*: Customer analytics en targeting\n• *Research*: Wetenschappelijk onderzoek en publicaties\n\n*Deliverables:*\n• *Rapporten*: Uitgebreide analyses en aanbevelingen\n• *Dashboards*: Interactieve data visualisaties\n• *Modellen*: Machine learning en statistische modellen\n• *Software*: Custom applicaties en tools\n• *Training*: Workshops en kennisoverdracht\n• *Ondersteuning*: Continue begeleiding en optimalisatie",
            "en": "💼 *Consultancy & Advice*\n\n*Data Analysis & Statistical Modeling:*\n• *Statistical analyses*: Comprehensive data analysis and interpretation\n• *Predictive modeling*: Predictive models and trends\n• *Data visualization*: Interactive dashboards and reports\n• *Quality control*: Statistical quality assurance\n• *Research design*: Experimental design and methodology\n\n*Research Methodology:*\n• *Research design*: Design of scientific studies\n• *Sampling methods*: Representative data collection\n• *Validation*: Reliability and validity of research\n• *Ethics*: Research ethics and privacy protection\n• *Reporting*: Scientific reporting and presentation\n\n*Machine Learning & AI:*\n• *Algorithm development*: Custom machine learning models\n• *Data preprocessing*: Data cleaning and feature engineering\n• *Model evaluation*: Performance assessment and validation\n• *AI implementation*: Practical applications of AI\n• *Ethical AI*: Responsible AI development\n\n*Software Development:*\n• *Web development*: Frontend and backend development\n• *Database design*: Data architecture and optimization\n• *API development*: Integration and system coupling\n• *Testing & QA*: Quality assurance and debugging\n• *Deployment*: Implementation and maintenance\n\n*Consultancy Approach:*\n\n*1. Initial Conversation & Needs Analysis*\n• Intake conversation to understand goals and challenges\n• Analysis of current situation and wishes\n• Determination of scope and expectations\n• Development of project plan and timeline\n\n*2. Data Evaluation & Assessment*\n• Analysis of available data and systems\n• Identification of improvement points and opportunities\n• Assessment of technical infrastructure\n• Benchmarking against best practices\n\n*3. Solution Design*\n• Development of custom solutions\n• Technical specifications and architecture\n• Implementation strategy and planning\n• Risk analysis and mitigation\n\n*4. Implementation & Guidance*\n• Step-by-step implementation of solutions\n• Training and knowledge transfer\n• Monitoring and evaluation of results\n• Continuous support and optimization\n\n*5. Knowledge Transfer & Support*\n• Documentation and manuals\n• Staff training\n• Best practices and procedures\n• Long-term support and maintenance\n\n*Sectors & Applications:*\n• *Education*: Educational technology and data analysis\n• *Healthcare*: Medical data analysis and statistics\n• *Finance*: Financial modeling and risk analysis\n• *Marketing*: Customer analytics and targeting\n• *Research*: Scientific research and publications\n\n*Deliverables:*\n• *Reports*: Comprehensive analyses and recommendations\n• *Dashboards*: Interactive data visualizations\n• *Models*: Machine learning and statistical models\n• *Software*: Custom applications and tools\n• *Training*: Workshops and knowledge transfer\n• *Support*: Continuous guidance and optimization"
        },
        "info_how_lessons_work": {
            "nl": "📚 *Hoe Lessen Werken*\n\n*🎯 Lesopzet & Structuur:*\n• *Intake gesprek*: Eerste les start altijd met een uitgebreide intake\n• *Diagnostische toets*: Bepaling van huidig niveau en leerdoelen\n• *Persoonlijk plan*: Op maat gemaakt leertraject op basis van intake\n• *Flexibele duur*: 60-90 minuten afhankelijk van behoefte\n\n*💻 Lesvormen & Locaties:*\n• *Online lessen*: Via Zoom/Google Meet met interactieve whiteboards\n• *Fysieke lessen*: Thuis, op school, of op locatie (Amsterdam)\n• *Hybride optie*: Combinatie van online en fysiek mogelijk\n• *Locaties*: Science Park (gratis), VU/UvA (€20), thuis (€50)\n• *MBO trajecten*: Alleen online beschikbaar\n\n*📱 Technologie & Tools:*\n• *iPad aantekeningen*: Digitale notities gedeeld na elke les\n• *Online whiteboards*: Interactieve uitleg en samenwerking\n• *AI ondersteuning*: ChatGPT voor conceptverduidelijking\n• *WhatsApp support*: 7 dagen na elke les beschikbaar\n\n*📋 Lesverloop:*\n• *Voorbereiding*: Student bereidt vragen/voorbereiding voor\n• *Uitleg*: Stapsgewijze uitleg van concepten\n• *Samen oefenen*: Interactieve oefeningen en samenwerking\n• *Feedback*: Directe feedback en tips\n• *Huiswerk*: Gepersonaliseerde opdrachten en oefeningen\n• *Evaluatie*: Korte evaluatie van voortgang en doelen\n\n*🎓 Specifieke Vakken:*\n• *Wiskunde*: Alle niveaus (basisonderwijs t/m universiteit)\n• *Programmeren*: Python, Java, C#, web development\n• *Statistiek*: SPSS, R, data-analyse, onderzoek\n• *Scriptiebegeleiding*: Methodologie, analyse, structuur\n• *MBO trajecten*: Alleen voor volwassenen (18+), online trajecten\n\n*⏰ Planning & Beschikbaarheid:*\n• *Flexibele tijden*: Maandag t/m zondag, 9:00-22:00\n• *Last-minute*: Mogelijk met toeslag (<24u +20%, <12u +50%)\n• *Pakketten*: 2 of 4 lessen met verschillende geldigheid\n• *Proefles*: Gratis 30 minuten intake en kennismaking\n\n*📞 Ondersteuning:*\n• *WhatsApp*: 7 dagen na elke les voor vragen\n• *Reactietijd*: Binnen 24 uur op alle vragen\n• *Check-ins*: Korte motivatie- en planningsgesprekken\n• *Ouder communicatie*: Regelmatige updates en feedback",
            "en": "📚 *How Lessons Work*\n\n*🎯 Lesson Structure & Setup:*\n• *Intake conversation*: First lesson always starts with comprehensive intake\n• *Diagnostic test*: Assessment of current level and learning goals\n• *Personal plan*: Custom learning trajectory based on intake\n• *Flexible duration*: 60-90 minutes depending on needs\n\n*💻 Lesson Formats & Locations:*\n• *Online lessons*: Via Zoom/Google Meet with interactive whiteboards\n• *In-person lessons*: At home, at school, or on location (Amsterdam)\n• *Hybrid option*: Combination of online and in-person possible\n• *Locations*: Science Park (free), VU/UvA (€20), home (€50)\n• *MBO trajectories*: Online only\n\n*📱 Technology & Tools:*\n• *iPad notes*: Digital notes shared after each lesson\n• *Online whiteboards*: Interactive explanation and collaboration\n• *AI support*: ChatGPT for concept clarification\n• *WhatsApp support*: Available 7 days after each lesson\n\n*📋 Lesson Flow:*\n• *Preparation*: Student prepares questions/preparation\n• *Explanation*: Step-by-step explanation of concepts\n• *Practice together*: Interactive exercises and collaboration\n• *Feedback*: Direct feedback and tips\n• *Homework*: Personalized assignments and exercises\n• *Evaluation*: Brief evaluation of progress and goals\n\n*🎓 Specific Subjects:*\n• *Mathematics*: All levels (primary education to university)\n• *Programming*: Python, Java, C#, web development\n• *Statistics*: SPSS, R, data analysis, research\n• *Thesis guidance*: Methodology, analysis, structure\n• *MBO trajectories*: Adults only (18+), online trajectories\n\n*⏰ Scheduling & Availability:*\n• *Flexible times*: Monday to Sunday, 9:00-22:00\n• *Last-minute*: Possible with surcharge (<24h +20%, <12h +50%)\n• *Packages*: 2 or 4 lessons with different validity\n• *Trial lesson*: Free 30 minutes intake and introduction\n\n*📞 Support:*\n• *WhatsApp*: 7 days after each lesson for questions\n• *Response time*: Within 24 hours on all questions\n• *Check-ins*: Short motivation and planning conversations\n• *Parent communication*: Regular updates and feedback"
        },
        "menu_tariffs": {
            "nl": "💰 Tarieven",
            "en": "💰 Rates"
        },
        "menu_all_tariffs": {
            "nl": "💰 Alle tarieven bekijken",
            "en": "💰 View all rates"
        },
        "show_all_tariffs": {
            "nl": "💰 Alle tarieven bekijken",
            "en": "💰 View all rates"
        },
        "plan_lesson_button": {
            "nl": "📅 Les inplannen",
            "en": "📅 Schedule lesson"
        },
        "back_to_info": {
            "nl": "📖 Meer informatie",
            "en": "📖 More information"
        },
        "handoff_to_stephen": {
            "nl": "👨‍🏫 Stephen spreken",
            "en": "👨‍🏫 Speak to Stephen"
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
            "nl": "👨‍🏫 Goed! Stephen neemt het gesprek over. Je kunt hem direct vragen stellen.",
            "en": "👨‍🏫 Great! Stephen will take over the conversation. You can ask him questions directly."
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
            "nl": "🎯 Gratis proefles (30 min)",
            "en": "🎯 Free trial lesson (30 min)"
        },
        "prefill_action_urgent_session": {
            "nl": "🚨 Spoed: 2-uurs sessie (€120)",
            "en": "🚨 Urgent: 2-hour session (€120)"
        },
        "prefill_action_menu_text": {
            "nl": "✅ Helemaal goed! Ik heb je informatie verwerkt en met Stephen gedeeld zodat hij je zo goed mogelijk kan helpen.\n\nOpties:\n• Gratis proefles (30 min): Kennismaking zonder verplichting\n• Spoedles: Directe hulp met betaling\n• Meer info: Over Stephen en zijn aanpak\n• Stephen spreken: Direct contact",
            "en": "✅ Great! I've processed your information and shared it with Stephen so he can help you as best as possible.\n\nOptions:\n• Free trial lesson (30 min): Introduction without obligation\n• Urgent session: Immediate help with payment\n• More info: About Stephen and his approach\n• Speak to Stephen: Direct contact"
        },
        "prefill_action_menu_title": {
            "nl": "✅ Prima! Kies je optie:",
            "en": "✅ Great! Choose your option:"
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
            "nl": "📋 Hier zijn je huidige voorkeuren:\n\n⏰ *Voorkeur tijd*: {preferred_times}\n📍 *Locatie*: {location_preference}\n\nZijn deze nog correct?",
            "en": "📋 Here are your current preferences:\n\n⏰ *Preferred time*: {preferred_times}\n📍 *Location*: {location_preference}\n\nAre these still correct?"
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
                    "nl": "Voor een student",
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
        "prefill_confirmed_message": {
            "nl": "✅ Top! Ik heb je informatie verwerkt. Wat wil je nu doen?",
            "en": "✅ Excellent! I've processed your information. What would you like to do now?"
        },
        "prefill_rejected": {
            "nl": "✅ Geen probleem! Laten we de informatie stap voor stap invullen.",
            "en": "✅ No problem! Let's fill in the information step by step."
        },
        "prefill_corrected_confirmed": {
            "nl": "✅ Geweldig! Ik heb je gecorrigeerde informatie verwerkt. Wat wil je nu doen?",
            "en": "✅ Wonderful! I've processed your corrected information. What would you like to do now?"
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
            "nl": "🎯 Mooi! Laten we een gratis proefles van 30 minuten inplannen. Ik heb een paar vragen om de les goed voor te bereiden.",
            "en": "🎯 Excellent! Let's schedule a free 30-minute trial lesson. I have a few questions to prepare the lesson well."
        },
        "trial_lesson_mode_question": {
            "nl": "📱 Wil je de proefles online of fysiek doen?\n\n💻 *Online*: Via Zoom/Google Meet met interactieve whiteboards\n🏫 *Fysiek*: Alleen mogelijk op Science Park (Amsterdam)\n\nKies je voorkeur:",
            "en": "📱 Do you want the trial lesson online or in-person?\n\n💻 *Online*: Via Zoom/Google Meet with interactive whiteboards\n🏫 *In-person*: Only possible at Science Park (Amsterdam)\n\nChoose your preference:"
        },
        "trial_lesson_online": {
            "nl": "💻 Online proefles",
            "en": "💻 Online trial lesson"
        },
        "trial_lesson_fysiek": {
            "nl": "🏫 Fysiek op Science Park",
            "en": "🏫 In-person at Science Park"
        },
        "trial_lesson_mode_confirmed": {
            "nl": "✅ {mode} geselecteerd! Nu ga ik beschikbare tijden sturen.",
            "en": "✅ {mode} selected! Now I'll send available times."
        },
        "planning_premium_service": {
            "nl": "📅 Goed zo! Laten we alle lessen inplannen. Ik ga je helpen met het plannen van een volledig pakket.",
            "en": "📅 Great! Let's schedule all lessons. I'll help you plan a complete package."
        },
        "planning_urgent_session": {
            "nl": "🚨 Oké! Laten we een spoed 2-uurs sessie inplannen voor €120. Na het selecteren van een tijd krijg je direct een betaallink.",
            "en": "🚨 Got it! Let's schedule an urgent 2-hour session for €120. After selecting a time, you'll get a payment link immediately."
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
        },
        
        # Prefill field labels
        "prefill_learner_name": {
            "nl": "Naam leerling",
            "en": "Student name"
        },
        "prefill_school_level": {
            "nl": "Schoolniveau",
            "en": "School level"
        },
        "prefill_topic_primary": {
            "nl": "Hoofdvak",
            "en": "Primary subject"
        },
        "prefill_topic_secondary": {
            "nl": "Specifiek vak",
            "en": "Specific subject"
        },
        "prefill_goals": {
            "nl": "Leerdoelen",
            "en": "Learning goals"
        },
        "prefill_for_who": {
            "nl": "Voor wie",
            "en": "For whom"
        },
        "prefill_for_who_self": {
            "nl": "Voor mijzelf",
            "en": "For myself"
        },
        "prefill_for_who_child": {
            "nl": "Voor mijn kind",
            "en": "For my child"
        },
        "prefill_for_who_student": {
            "nl": "Voor een student",
            "en": "For a student"
        },
        "prefill_for_who_other": {
            "nl": "Voor iemand anders",
            "en": "For someone else"
        },
        "prefill_corrected_summary_title": {
            "nl": "📋 Gecorrigeerde Informatie",
            "en": "📋 Corrected Information"
        },
        "prefill_corrected_confirmation_prompt": {
            "nl": "Klopt deze informatie nu wel?",
            "en": "Is this information correct now?"
        },
        "prefill_confirm_yes": {
            "nl": "✅ Ja, klopt!",
            "en": "✅ Yes, correct!"
        },
        "prefill_confirm_no": {
            "nl": "❌ Nee, nog fouten",
            "en": "❌ No, still errors"
        },
        "info_tariffs_havo_vwo": {
            "nl": "💰 *Tarieven voor HAVO/VWO*\n\n🎓 *Individuele lessen:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €65 per uur\n• 3-4 personen: €55 per uur\n\n✨ *Inclusief: eindexamenvoorbereiding, oefentoetsen en studieplanning*",
            "en": "💰 *Rates for HAVO/VWO*\n\n🎓 *Individual lessons:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €65 per hour\n• 3-4 persons: €55 per hour\n\n✨ *Includes: final exam preparation, practice tests and study planning*"
        },
        "info_tariffs_adult": {
            "nl": "💰 *Tarieven (18+ jaar)*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n🎓 *Voortgezet onderwijs:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n🎯 *MBO Rekentrajecten (alleen online):*\n• Spoedpakket: 1 week, 4 uur (€275)\n• Korte cursus: 4 weken, 4 uur (€225)\n• Volledig Commit: 12 weken, 13-14 uur (€550)\n• Volledig Flex: 12 weken, 13-14 uur (€690 in 3 termijnen)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates (18+ years)*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n🎓 *Secondary education:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n🎯 *MBO Math trajectories (online only):*\n• Emergency: 1 week, 4 hours (€275)\n• Short course: 4 weeks, 4 hours (€225)\n• Full Commit: 12 weeks, 13-14 hours (€550)\n• Full Flex: 12 weeks, 13-14 hours (€690 in 3 installments)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        },
        "tariffs_follow_up_title": {
            "nl": "💰 *Tarieven*\n\nWat wil je weten over onze tarieven?",
            "en": "💰 *Rates*\n\nWhat would you like to know about our rates?"
        },
        "info_tariffs_po": {
            "nl": "💰 *Tarieven voor primair onderwijs*\n\n🎓 *Individuele lessen:*\n• 1 les (1 uur): €65\n• 2 lessen (2 uur): €120\n• 4 lessen (4 uur): €180\n\n👥 *Groepslessen:*\n• 2 personen: €40 (1u) • €80 (2u) • €120 (4u)\n• 3-4 personen: €35 (1u) • €65 (2u) • €100 (4u)",
            "en": "💰 *Rates for primary education*\n\n🎓 *Individual lessons:*\n• 1 lesson (1 hour): €65\n• 2 lessons (2 hours): €120\n• 4 lessons (4 hours): €180\n\n👥 *Group lessons:*\n• 2 persons: €40 (1h) • €80 (2h) • €120 (4h)\n• 3-4 persons: €35 (1h) • €65 (2h) • €100 (4h)"
        },
        "info_tariffs_vmbo": {
            "nl": "💰 *Tarieven voor VMBO*\n\n🎓 *Individuele lessen:*\n• 1 les (1 uur): €75\n• 2 lessen (2 uur): €130\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €45 (1u) • €90 (2u) • €135 (4u)\n• 3-4 personen: €40 (1u) • €70 (2u) • €120 (4u)",
            "en": "💰 *Rates for VMBO*\n\n🎓 *Individual lessons:*\n• 1 lesson (1 hour): €75\n• 2 lessons (2 hours): €130\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €45 (1h) • €90 (2h) • €135 (4h)\n• 3-4 persons: €40 (1h) • €70 (2h) • €120 (4h)"
        },
        "info_tariffs_mbo": {
            "nl": "💰 *Tarieven voor MBO*\n\n🎓 *Individuele lessen:*\n• 1 les (1 uur): €80\n• 2 lessen (2 uur): €135\n• 4 lessen (4 uur): €200\n\n👥 *Groepslessen:*\n• 2 personen: €50 (1u) • €100 (2u) • €150 (4u)\n• 3-4 personen: €45 (1u) • €85 (2u) • €130 (4u)\n\n🎯 *MBO Rekentrajecten (alleen online, 18+):*\n• Spoedpakket: 1 week, 4 uur (€275)\n• Korte cursus: 4 weken, 4 uur (€225)\n• Volledig Commit: 12 weken, 13-14 uur (€550)\n• Volledig Flex: 12 weken, 13-14 uur (€690 in 3 termijnen)",
            "en": "💰 *Rates for MBO*\n\n🎓 *Individual lessons:*\n• 1 lesson (1 hour): €80\n• 2 lessons (2 hours): €135\n• 4 lessons (4 hours): €200\n\n👥 *Group lessons:*\n• 2 persons: €50 (1h) • €100 (2h) • €150 (4h)\n• 3-4 persons: €45 (1h) • €85 (2h) • €130 (4h)\n\n🎯 *MBO Math trajectories (online only, 18+):*\n• Emergency: 1 week, 4 hours (€275)\n• Short course: 4 weeks, 4 hours (€225)\n• Full Commit: 12 weeks, 13-14 hours (€550)\n• Full Flex: 12 weeks, 13-14 hours (€690 in 3 installments)"
        },
        "info_tariffs_university": {
            "nl": "💰 *Tarieven voor hoger onderwijs*\n\n📚 *Hoger onderwijs:*\n• 1 les (1 uur): €90\n• 2 lessen (2 uur): €140\n• 4 lessen (4 uur): €250\n\n👥 *Groepslessen:*\n• 2 personen: €65 (1u) • €125 (2u) • €180 (4u)\n• 3-4 personen: €55 (1u) • €95 (2u) • €150 (4u)\n\n📊 *Scriptiebegeleiding:*\n• Statistiek & onderzoek: €90/uur\n• Data science & AI: €100/uur",
            "en": "💰 *Rates for higher education*\n\n📚 *Higher education:*\n• 1 lesson (1 hour): €90\n• 2 lessons (2 hours): €140\n• 4 lessons (4 hours): €250\n\n👥 *Group lessons:*\n• 2 persons: €65 (1h) • €125 (2h) • €180 (4h)\n• 3-4 persons: €55 (1h) • €95 (2h) • €150 (4h)\n\n📊 *Thesis guidance:*\n• Statistics & research: €90/hour\n• Data science & AI: €100/hour"
        }
    }
    
    if key in translations and lang in translations[key]:
        text = translations[key][lang]
        return text.format(**kwargs) if kwargs else text
    else:
        return key
def send_text_with_duplicate_check(conversation_id, text, persist: bool = True):
    """
    Send text message with duplicate checking to prevent spam.
    
    Args:
        conversation_id (int): Chatwoot conversation ID
        text (str): Message text to send
        persist (bool): Whether to store the message in duplicate check
    
    Returns:
        bool: True if message was sent, False if duplicate or error
    """
    try:
        # Simple duplicate check - in real implementation this would be more sophisticated
        api = ChatwootAPI()
        
        # Send the message
        success = api.send_message(conversation_id, text)
        
        if success and persist:
            # Store for duplicate checking (simplified)
            print(f"📤 Message sent to conversation {conversation_id}: {text[:50]}...")
        
        return success
    except Exception as e:
        print(f"❌ Failed to send message to conversation {conversation_id}: {e}")
        return False

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
        from modules.utils.cw_api import ChatwootAPI
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

def assign_conversation(conversation_id, assignee_id):
    """
    Assign conversation to a user.
    
    Args:
        conversation_id (int): Chatwoot conversation ID
        assignee_id (int): User ID to assign to
    
    Returns:
        bool: True if assigned successfully
    """
    try:
        url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/assignments"
        headers = {
            "api_access_token": ADMIN_TOK,
            "Content-Type": "application/json"
        }
        data = {"assignee_id": assignee_id}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Conversation {conversation_id} assigned to user {assignee_id}")
            return True
        else:
            print(f"❌ Failed to assign conversation: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error assigning conversation: {e}")
        return False

def send_handoff_message(conversation_id, text):
    """
    Send handoff message and assign to human agent.
    
    Args:
        conversation_id (int): Chatwoot conversation ID  
        text (str): Handoff message
    
    Returns:
        bool: True if handoff was successful
    """
    try:
        # Send handoff message
        success = send_text_with_duplicate_check(conversation_id, text)
        
        if success:
            # Import the handoff agent ID from config
            from modules.core.config import HANDOFF_AGENT_ID
            
            # Assign to human agent (using environment variable)
            assign_success = assign_conversation(conversation_id, HANDOFF_AGENT_ID)
            if assign_success:
                print(f"🤝 Handing off conversation {conversation_id} to human agent (ID: {HANDOFF_AGENT_ID})")
            else:
                print(f"⚠️ Failed to assign conversation {conversation_id} to human agent")
            
        return success
    except Exception as e:
        print(f"❌ Error in handoff: {e}")
        return False

def send_handoff_menu(conversation_id):
    """
    Send handoff menu with options.
    
    Args:
        conversation_id (int): Chatwoot conversation ID
    
    Returns:
        bool: True if menu was sent
    """
    try:
        text = "Wil je overgeschakeld worden naar een menselijke medewerker?"
        options = [
            ("Ja, schakel over naar mens", "handoff_yes"),
            ("Nee, ga door met bot", "handoff_no")
        ]
        
        return send_input_select_only(conversation_id, text, options)
    except Exception as e:
        print(f"❌ Error sending handoff menu: {e}")
        return False

def send_admin_warning(conversation_id: int, warning_message: str):
    """
    Send warning message to administrators.
    
    Args:
        conversation_id (int): Related conversation ID
        warning_message (str): Warning message to send
    """
    try:
        # In a real implementation, this would send to admin channels
        print(f"⚠️ ADMIN WARNING for conversation {conversation_id}: {warning_message}")
        
        # Could also send to admin conversation or notification system
        # For now, just log it
        
    except Exception as e:
        print(f"❌ Error sending admin warning: {e}")

def get_contact_id_from_conversation(conversation_id):
    """
    Get contact ID from conversation ID.
    
    Args:
        conversation_id (int): Chatwoot conversation ID
    
    Returns:
        int or None: Contact ID if found
    """
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
