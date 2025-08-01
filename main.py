from flask import Flask, request, jsonify
import os, hmac, hashlib, requests, json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re
from cw_api import ChatwootAPI, get_contact_attrs, set_contact_attrs, get_conv_attrs, set_conv_attrs, add_conv_labels, send_text

# Config variables
CW = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID")
TOK = os.getenv("CW_TOKEN")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN")
SIG = os.getenv("CW_HMAC_SECRET")
TZ = ZoneInfo("Europe/Amsterdam")

# Stripe configuration
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STANDARD_PRICE_ID_60 = os.getenv("STANDARD_PRICE_ID_60")
STANDARD_PRICE_ID_90 = os.getenv("STANDARD_PRICE_ID_90")
WEEKEND_PRICE_ID_60 = os.getenv("WEEKEND_PRICE_ID_60")
WEEKEND_PRICE_ID_90 = os.getenv("WEEKEND_PRICE_ID_90")

# Google Calendar configuration
GCAL_SERVICE_ACCOUNT_JSON = os.getenv("GCAL_SERVICE_ACCOUNT_JSON")
GCAL_CALENDAR_ID = os.getenv("GCAL_CALENDAR_ID", "primary")

app = Flask(__name__)

# Comprehensive translation function
def t(key, lang="nl", **kwargs):
    """Comprehensive translation function"""
    translations = {
        # Language selection
        "language_question": {
            "nl": "🌍 In welke taal wil je communiceren? 🇳🇱 Nederlands · 🇬🇧 English",
            "en": "🌍 In which language would you like to communicate? 🇳🇱 Dutch · 🇬🇧 English"
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
        
        # Segment-specific menus
        "menu_new": {
            "nl": "Waarmee kan ik helpen?",
            "en": "How can I help?"
        },
        "menu_existing": {
            "nl": "Welkom terug! Zal ik plannen op basis van eerdere voorkeuren?",
            "en": "Welcome back! Should I schedule based on your previous preferences?"
        },
        "menu_returning_broadcast": {
            "nl": "Hi! Nieuw nummer met assistent om sneller te plannen.",
            "en": "Hi! New number with assistant for faster scheduling."
        },
        "menu_weekend": {
            "nl": "Beschikbaarheid komend weekend (10:00–18:00):",
            "en": "Availability this weekend (10:00–18:00):"
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
            "nl": "Deadlines of doelen (optioneel)?",
            "en": "Deadlines or goals (optional)?"
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
            "nl": "Mijn tarieven beginnen bij €50/uur. Interesse in een gratis proefles (30 min)?",
            "en": "My rates start at €50/hour. Interested in a free trial lesson (30 minutes)?"
        },
        "info_menu_question": {
            "nl": "📄 Waarover wil je informatie?",
            "en": "📄 What information would you like?"
        },
        "info_tariffs": {
            "nl": "💰 **Uitgebreide Tarieven** (versie 31 juli 2025)\n\n📚 **Hoger onderwijs:**\n• Enkel (1 les): €80\n• Twee (2 lessen): €135\n• Vier (4 lessen): €250\n\n🎓 **Voortgezet onderwijs 20+:**\n• Enkel: €75\n• Twee: €130\n• Vier: €230\n\n🎓 **Voortgezet onderwijs 20-:**\n• Enkel: €60\n• Twee: €100\n• Vier: €200\n\n👥 **Groepslessen:**\n• €45-65 per persoon (afhankelijk van groepsgrootte)\n\n🎯 **MBO Rekentrajecten:**\n• Spoedpakket (1 week, 4 uur): €275\n• Korte cursus (4 weken, 4 uur): €225\n• Volledig Commit (12 weken, 13-14 uur): €550\n• Volledig Flex (12 weken, 13-14 uur): €690 (3 termijnen)\n\n🌅 **Weekend programma's (Zuidoost):**\n• 50% korting: €30/uur i.p.v. €60\n• Gratis proefles van 30 minuten",
            "en": "💰 **Comprehensive Rates** (version July 31, 2025)\n\n📚 **Higher education:**\n• Single (1 lesson): €80\n• Two (2 lessons): €135\n• Four (4 lessons): €250\n\n🎓 **Secondary education 20+:**\n• Single: €75\n• Two: €130\n• Four: €230\n\n🎓 **Secondary education 20-:**\n• Single: €60\n• Two: €100\n• Four: €200\n\n👥 **Group lessons:**\n• €45-65 per person (depending on group size)\n\n🎯 **MBO Math trajectories:**\n• Emergency package (1 week, 4 hours): €275\n• Short course (4 weeks, 4 hours): €225\n• Full Commit (12 weeks, 13-14 hours): €550\n• Full Flex (12 weeks, 13-14 hours): €690 (3 installments)\n\n🌅 **Weekend programs (Southeast):**\n• 50% discount: €30/hour instead of €60\n• Free trial lesson of 30 minutes"
        },
        "info_travel_costs": {
            "nl": "🚗 **Reiskosten (Amsterdam e.o.):**\n\n• VU/UvA (niet Science Park): €15\n• Bij jou thuis (Amsterdam e.o.): €40\n• Science Park: €0",
            "en": "🚗 **Travel costs (Amsterdam area):**\n\n• VU/UvA (not Science Park): €15\n• At your home (Amsterdam area): €40\n• Science Park: €0"
        },
        "info_last_minute": {
            "nl": "⏰ **Last-minute toeslagen (op het standaardtarief):**\n\n• Geboekt < 24 uur vooraf: +20%\n• Geboekt < 12 uur vooraf: +50%",
            "en": "⏰ **Last-minute surcharges (on standard rate):**\n\n• Booked < 24 hours in advance: +20%\n• Booked < 12 hours in advance: +50%"
        },
        "info_conditions": {
            "nl": "📋 **Pakketvoorwaarden:**\n\n⏱️ **Geldigheid:**\n• Pakket van 2 lessen: geldig 2 weken na aankoopdatum\n• Pakket van 4 lessen: geldig 1 maand na aankoopdatum\n• Bij directe planning: geldigheid loopt vanaf eerste lesdatum\n\n🎯 **Flex-premium (alleen bij niet-direct plannen):**\n• Pakket van 2 lessen: +€15\n• Pakket van 4 lessen: +€30\n\n💳 **Betaling & factuur:**\n• Factuur na elke les\n• Termijn: 14 dagen\n\n❌ **Annuleren/verzetten:**\n• ≥24u vooraf: kosteloos\n• <24u vooraf: 100% van het tarief",
            "en": "📋 **Package conditions:**\n\n⏱️ **Validity:**\n• Package of 2 lessons: valid 2 weeks after purchase date\n• Package of 4 lessons: valid 1 month after purchase date\n• With direct scheduling: validity runs from first lesson date\n\n🎯 **Flex-premium (only when not scheduling directly):**\n• Package of 2 lessons: +€15\n• Package of 4 lessons: +€30\n\n💳 **Payment & invoice:**\n• Invoice after each lesson\n• Term: 14 days\n\n❌ **Cancel/reschedule:**\n• ≥24h in advance: free\n• <24h in advance: 100% of the rate"
        },
        "info_work_method": {
            "nl": "🎯 **Mijn Werkwijze & Aanpak**\n\n👨‍🏫 **Persoonlijke Achtergrond:**\n• Stephen Adei: Masterstudent uit Amsterdam met 10+ jaar ervaring\n• Persoonlijke reis: Van wiskunde-uitdagingen (gemiddelde 5) naar excellente resultaten (gemiddelde 10)\n• Expertise: Programmeren, wiskunde, statistiek, data-analyse\n\n🎯 **Kernwaarden:**\n• **Persoonlijke Aanpak**: Elke student is uniek - lessen aangepast aan individuele leerstijl\n• **Brede Expertise**: Multidisciplinaire achtergrond voor diverse perspectieven\n• **Flexibel Leren**: Flexibele planning en WhatsApp-ondersteuning\n• **Technologie-integratie**: iPad-aantekeningen, AI-tools, digitale ondersteuning\n\n📚 **Lesaanpak:**\n• **Persoonlijke begeleiding**: Afgestemd op individuele behoeften\n• **Interactieve lessen**: Combinatie van theorie, praktijk en real-world toepassingen\n• **Ongoing support**: 7 dagen WhatsApp-ondersteuning na elke les\n• **Differentiatie**: Scaffolding en andere technieken voor verschillende leerstijlen\n\n⏰ **Lesorganisatie:**\n• **Flexibele planning**: Online en fysiek mogelijk\n• **Duur**: 60-90 minuten (aanpasbaar)\n• **Frequentie**: Wekelijks (aanpasbaar)\n• **Locaties**: Science Park 904, Douwe Egberts (Zuidoost), aan huis\n\n🏆 **Kwaliteitsborging:**\n• **Gratis proefles**: Kennismaking met werkwijze\n• **Regelmatige evaluaties**: Voortgangsmonitoring\n• **Feedback-systeem**: Continue verbetering van methoden\n• **98% studenttevredenheid** en **gemiddelde beoordeling: 4.9/5**",
            "en": "🎯 **My Work Method & Approach**\n\n👨‍🏫 **Personal Background:**\n• Stephen Adei: Master's student from Amsterdam with 10+ years of experience\n• Personal journey: From math challenges (average 5) to excellent results (average 10)\n• Expertise: Programming, mathematics, statistics, data analysis\n\n🎯 **Core Values:**\n• **Personal Approach**: Every student is unique - lessons adapted to individual learning style\n• **Broad Expertise**: Multidisciplinary background for diverse perspectives\n• **Flexible Learning**: Flexible scheduling and WhatsApp support\n• **Technology Integration**: iPad notes, AI tools, digital support\n\n📚 **Lesson Approach:**\n• **Personal guidance**: Tailored to individual needs\n• **Interactive lessons**: Combination of theory, practice and real-world applications\n• **Ongoing support**: 7 days WhatsApp support after each lesson\n• **Differentiation**: Scaffolding and other techniques for different learning styles\n\n⏰ **Lesson Organization:**\n• **Flexible scheduling**: Online and in-person possible\n• **Duration**: 60-90 minutes (adjustable)\n• **Frequency**: Weekly (adjustable)\n• **Locations**: Science Park 904, Douwe Egberts (Southeast), at home\n\n🏆 **Quality Assurance:**\n• **Free trial lesson**: Introduction to work method\n• **Regular evaluations**: Progress monitoring\n• **Feedback system**: Continuous improvement of methods\n• **98% student satisfaction** and **average rating: 4.9/5**"
        },
        "info_services": {
            "nl": "📚 **Mijn Diensten & Aanbod**\n\n🎓 **1. Privélessen & Bijles**\n**Vakken:**\n• **Basisonderwijs**: Rekenen, Taal\n• **Voortgezet Onderwijs**: Wiskunde A/B/C/D, Natuurkunde, Scheikunde, Engels\n• **Hoger Onderwijs**: Bedrijfsstatistiek, Calculus, Economie, Statistiek, Kansberekening, Lineaire Algebra, Verzamelingenleer\n• **Programmeren**: Python, Java, C#, C++, HTML, CSS, JavaScript, React, SQL, MATLAB, SPSS, R\n\n🎯 **2. MBO Rekenondersteuning**\n• **95% slagingspercentage** MBO-rekentoets\n• **500+ studenten** geholpen\n• **Gemiddelde beoordeling: 8.9/10**\n• Bewezen methoden en effectieve lesmaterialen\n\n📝 **3. Scriptiebegeleiding**\n• Methodologie en onderzoeksopzet\n• Statistische analyse (SPSS, R, Python)\n• Data-analyse en interpretatie\n• Structuur en planning\n• Eindredactie\n\n🎨 **4. Creatieve Workshops**\n• Muziekproductie & DJ (3 uur)\n• Analoge fotografie & bewerking (4 uur)\n• Visuele storytelling & design (3 uur)\n• Creatief coderen: Kunst & animatie (2 uur, 4 sessies)\n• AI & creativiteit (3 uur)\n• Escape room design (4 uur, 2 sessies)\n• Wiskundige kunst & patronen (3 uur)\n• Wiskundig verhalen vertellen (2.5 uur)\n• Wiskundige podcasting (3 uur, 2 sessies)\n• Educatieve wiskundevideo's (4 uur, 3 sessies)\n\n🎓 **5. Academische Workshops**\n• Statistiek project cursus (90 min, 6 sessies)\n• Wiskunde docenten innovatie (3 uur, 4 sessies)\n• AI & wiskunde (2 uur, 3 sessies)\n• Data visualisatie met Python (3 uur, 3 sessies)\n• Wiskundige spelontwikkeling (3 uur)\n• 3D wiskundig modelleren (3 uur, 4 sessies)\n• Innovatieve wiskundetoetsing (3 uur, 2 sessies)\n• Differentiatie in wiskundeonderwijs (3 uur, 3 sessies)\n• Mindfulness in wiskunde (2 uur)\n\n🧘 **6. Wellness Workshops**\n• Mindfulness (2 uur)\n• Tijdmanagement (2.5 uur)\n• Examenvoorbereiding (3 uur, 3 sessies)\n\n💼 **7. Consultancy & Advies**\n• Data-analyse en statistische modellering\n• Onderzoeksmethodologie\n• Machine learning en AI\n• Software ontwikkeling",
            "en": "📚 **My Services & Offerings**\n\n🎓 **1. Private Lessons & Tutoring**\n**Subjects:**\n• **Primary Education**: Math, Language\n• **Secondary Education**: Math A/B/C/D, Physics, Chemistry, English\n• **Higher Education**: Business Statistics, Calculus, Economics, Statistics, Probability, Linear Algebra, Set Theory\n• **Programming**: Python, Java, C#, C++, HTML, CSS, JavaScript, React, SQL, MATLAB, SPSS, R\n\n🎯 **2. MBO Math Support**\n• **95% pass rate** MBO math test\n• **500+ students** helped\n• **Average rating: 8.9/10**\n• Proven methods and effective teaching materials\n\n📝 **3. Thesis Guidance**\n• Methodology and research design\n• Statistical analysis (SPSS, R, Python)\n• Data analysis and interpretation\n• Structure and planning\n• Final editing\n\n🎨 **4. Creative Workshops**\n• Music production & DJ (3 hours)\n• Analog photography & editing (4 hours)\n• Visual storytelling & design (3 hours)\n• Creative coding: Art & animation (2 hours, 4 sessions)\n• AI & creativity (3 hours)\n• Escape room design (4 hours, 2 sessions)\n• Mathematical art & patterns (3 hours)\n• Mathematical storytelling (2.5 hours)\n• Mathematical podcasting (3 hours, 2 sessions)\n• Educational math videos (4 hours, 3 sessions)\n\n🎓 **5. Academic Workshops**\n• Statistics project course (90 min, 6 sessions)\n• Math teacher innovation (3 hours, 4 sessions)\n• AI & mathematics (2 hours, 3 sessions)\n• Data visualization with Python (3 hours, 3 sessions)\n• Mathematical game development (3 hours)\n• 3D mathematical modeling (3 hours, 4 sessions)\n• Innovative math testing (3 hours, 2 sessions)\n• Differentiation in math education (3 hours, 3 sessions)\n• Mindfulness in mathematics (2 hours)\n\n🧘 **6. Wellness Workshops**\n• Mindfulness (2 hours)\n• Time management (2.5 hours)\n• Exam preparation (3 hours, 3 sessions)\n\n💼 **7. Consultancy & Advice**\n• Data analysis and statistical modeling\n• Research methodology\n• Machine learning and AI\n• Software development"
        },
        "info_weekend_programs": {
            "nl": "🌅 **Weekend Programma's (Amsterdam Zuidoost)**\n\n🇬🇭 **Boa me na menboa mo (Ghanese gemeenschap):**\n• **50% korting** voor Ghanese jongeren: €30/uur i.p.v. €60\n• **Locatie**: Douwe Egberts (Dubbelink 2) of aan huis in Gein\n• **Tijden**: Zaterdag en zondag, flexibele tijden\n• **Gratis proefles** van 30 minuten\n\n🌅 **Weekend Bijles Zuidoost:**\n• **50% korting**: €30/uur i.p.v. €60\n• **Zelfde locaties** en tijden\n• **Voor alle bewoners** van Zuidoost\n\n📍 **Locaties:**\n• Douwe Egberts (Dubbelink 2, Amsterdam Zuidoost)\n• Aan huis in Gein en omgeving\n• Bijlmerplein 888, 1102 MG Amsterdam\n\n⏰ **Beschikbaarheid:**\n• Zaterdag: 10:00–18:00\n• Zondag: 10:00–18:00\n• Flexibele tijden mogelijk\n\n🎯 **Speciale Kenmerken:**\n• **Community focus**: Toegankelijke tarieven voor verschillende doelgroepen\n• **Ervaring met speciale behoeften**: Ervaring met leerlingen met lichte autisme\n• **Gestructureerde en geduldige leeromgeving**\n• **Aanpassing aan specifieke behoeften**\n\n📞 **Contact:**\n• Telefoon: +31 6 47357426\n• Email: info@stephenadei.nl\n• Website: stephensprivelessen.nl",
            "en": "🌅 **Weekend Programs (Amsterdam Southeast)**\n\n🇬🇭 **Boa me na menboa mo (Ghanaian community):**\n• **50% discount** for Ghanaian youth: €30/hour instead of €60\n• **Location**: Douwe Egberts (Dubbelink 2) or at home in Gein\n• **Times**: Saturday and Sunday, flexible times\n• **Free trial lesson** of 30 minutes\n\n🌅 **Weekend Tutoring Southeast:**\n• **50% discount**: €30/hour instead of €60\n• **Same locations** and times\n• **For all residents** of Southeast\n\n📍 **Locations:**\n• Douwe Egberts (Dubbelink 2, Amsterdam Southeast)\n• At home in Gein and surrounding area\n• Bijlmerplein 888, 1102 MG Amsterdam\n\n⏰ **Availability:**\n• Saturday: 10:00–18:00\n• Sunday: 10:00–18:00\n• Flexible times possible\n\n🎯 **Special Features:**\n• **Community focus**: Accessible rates for different target groups\n• **Experience with special needs**: Experience with students with mild autism\n• **Structured and patient learning environment**\n• **Adaptation to specific needs**\n\n📞 **Contact:**\n• Phone: +31 6 47357426\n• Email: info@stephenadei.nl\n• Website: stephensprivelessen.nl"
        },
        "info_short_version": {
            "nl": "📝 **Korte versie:**\n\nHO: 1× €80 • 2× €135 • 4× €250\nVO 20+: 1× €75 • 2× €130 • 4× €230\nVO 20-: 1× €60 • 2× €100 • 4× €200\n\nReiskosten: VU/UvA (niet SP) €15 • Thuis (AMS e.o.) €40 • Science Park €0\n\nLast-minute: <24u +20% • <12u +50%\n\nPakketten: 2× geldig 2 weken • 4× geldig 1 maand; bij directe planning loopt geldigheid vanaf 1e les. Flex-premium (alleen bij niet-direct plannen): +€15 (2×) / +€30 (4×).\n\n🌅 Weekend programma's: 50% korting (€30/uur) in Zuidoost",
            "en": "📝 **Short version:**\n\nHE: 1× €80 • 2× €135 • 4× €250\nSE 20+: 1× €75 • 2× €130 • 4× €230\nSE 20-: 1× €60 • 2× €100 • 4× €200\n\nTravel: VU/UvA (not SP) €15 • Home (AMS area) €40 • Science Park €0\n\nLast-minute: <24h +20% • <12h +50%\n\nPackages: 2× valid 2 weeks • 4× valid 1 month; with direct scheduling validity runs from 1st lesson. Flex-premium (only when not scheduling directly): +€15 (2×) / +€30 (4×).\n\n🌅 Weekend programs: 50% discount (€30/hour) in Southeast"
        },
        "menu_tariffs": {
            "nl": "💰 Tarieven",
            "en": "💰 Rates"
        },
        "menu_work_method": {
            "nl": "🎯 Werkwijze",
            "en": "🎯 Work Method"
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
        
        # Handoff
        "handoff_teacher": {
            "nl": "Ik verbind je door met Stephen. Een moment geduld...",
            "en": "I'm connecting you with Stephen. One moment please..."
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
            "nl": "📅 Zelfde vak/voorkeuren",
            "en": "📅 Same subject/preferences"
        },
        "menu_option_different": {
            "nl": "🆕 Iets anders",
            "en": "🆕 Something else"
        },
        "menu_option_old_preferences": {
            "nl": "📅 Plannen met oude voorkeuren",
            "en": "📅 Plan with old preferences"
        },
        "menu_option_new_intake": {
            "nl": "🆕 Intake opnieuw doen",
            "en": "🆕 Do intake again"
        },
        "menu_option_trial_lesson": {
            "nl": "🎯 Proefles inplannen",
            "en": "🎯 Schedule trial lesson"
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
            "nl": "🎯 Proefles inplannen",
            "en": "🎯 Schedule trial lesson"
        },
        "planning_regular_lesson": {
            "nl": "📅 Les inplannen",
            "en": "📅 Schedule lesson"
        },
        "trial_lesson_confirmed": {
            "nl": "✅ Je proefles is gepland! Stephen neemt contact op voor bevestiging.",
            "en": "✅ Your trial lesson is scheduled! Stephen will contact you for confirmation."
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
        "numbered_fallback_instruction": {
            "nl": "Typ het nummer van je keuze (bijv. '1' of '2')",
            "en": "Type the number of your choice (e.g. '1' or '2')"
        }
    }
    
    if key in translations and lang in translations[key]:
        text = translations[key][lang]
        return text.format(**kwargs) if kwargs else text
    else:
        return key

# API functions with duplicate detection
def send_text_with_duplicate_check(conversation_id, text):
    """Send text message with duplicate detection"""
    # Check for duplicate messages
    conv_attrs = get_conv_attrs(conversation_id)
    last_message = conv_attrs.get("last_bot_message", "")
    
    if text == last_message:
        print(f"🔄 Duplicate message detected: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print(f"🚨 Auto-handoff triggered due to duplicate message")
        
        # Send handoff message
        handoff_text = t("handoff_duplicate_error", "nl")  # Default to Dutch for error messages
        send_handoff_message(conversation_id, handoff_text)
        return False
    
    # Store this message as the last sent message (preserve pending_intent)
    current_attrs = get_conv_attrs(conversation_id)
    current_attrs["last_bot_message"] = text
    set_conv_attrs(conversation_id, current_attrs)
    
    # Use the new API client
    success = send_text(conversation_id, text)
    if success:
        print(f"✅ Text message sent: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    else:
        print(f"❌ Text message failed")
    return success

def assign_conversation(conversation_id, assignee_id):
    """Assign a conversation to a specific Chatwoot user"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/assignments"
    headers = {
        "api_access_token": TOK,
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
        "api_access_token": TOK,
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
            set_conv_attrs(conversation_id, {"pending_intent": "handoff"})
            # Assign to Stephen (user_id=2)
            assign_conversation(conversation_id, 2)
            return True
        else:
            print(f"⚠️ Handoff message failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ Handoff message error: {e}")
        return False

def send_quick_replies(conversation_id, text, options):
    """Send Chatwoot quick replies using input_select format"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": TOK,
        "Content-Type": "application/json"
    }
    
    # Use Chatwoot's input_select format for quick replies
    items = []
    for label, value in options:
        items.append({
            "title": label,
            "value": value
        })
    
    data = {
        "content": text,
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
            print(f"✅ Quick replies sent successfully ({len(options)} options)")
        else:
            print(f"⚠️ Quick replies failed: {response.status_code} - {response.text[:100]}")
            # Fallback to text message if quick replies fail
            print(f"🔄 Falling back to text message")
            return send_text_with_duplicate_check(conversation_id, text + "\n\n" + "\n".join([f"• {label}" for label, _ in options]))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Quick replies error: {e}")
        # Fallback to text message
        return send_text_with_duplicate_check(conversation_id, text + "\n\n" + "\n".join([f"• {label}" for label, _ in options]))

def send_interactive_menu(conversation_id, text, options):
    """Send interactive menu using Chatwoot input_select format with duplicate detection"""
    # Check for duplicate messages (but allow first message in new conversation)
    conv_attrs = get_conv_attrs(conversation_id)
    last_message = conv_attrs.get("last_bot_message", "")
    pending_intent = conv_attrs.get("pending_intent", "")
    menu_sent = conv_attrs.get("menu_sent", False)
    
    # Don't check for duplicates if conversation is in handoff state
    if pending_intent == "handoff":
        print(f"👨‍🏫 Conversation is in handoff state - not sending duplicate message")
        return False

    # Removed menu_sent check - using last_bot_message for duplicate detection instead

    # For new conversations, disable duplicate detection completely
    if not last_message or last_message.strip() == "":
        print(f"🆕 New conversation detected - disabling duplicate detection")
        # Don't store last_bot_message for new conversations to prevent false duplicates
        return send_input_select_fallback_no_duplicate_check(conversation_id, text, options)
    
    # Only check for duplicates if we've already sent a message AND it's the exact same text
    if last_message and text.strip() == last_message.strip():
        print(f"🔄 Duplicate interactive message detected: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print(f"🚨 Auto-handoff triggered due to duplicate interactive message")
        
        # Send handoff message
        handoff_text = t("handoff_duplicate_error", "nl")  # Default to Dutch for error messages
        send_handoff_message(conversation_id, handoff_text)
        return False

    # Store this message as the last sent message (preserve pending_intent)
    current_attrs = get_conv_attrs(conversation_id)
    current_attrs["last_bot_message"] = text
    set_conv_attrs(conversation_id, current_attrs)
    
    # Use input_select format directly (no WhatsApp button fallback)
    return send_input_select_fallback_no_duplicate_check(conversation_id, text, options)

def send_input_select_fallback_no_duplicate_check(conversation_id, text, options):
    """Fallback to input_select format without duplicate detection (for use by send_interactive_menu)"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    
    # Use Chatwoot's official input_select format
    items = []
    for label, value in options:
        items.append({
            "title": label,
            "value": value
        })
    
    data = {
        "content": text,
        "content_type": "input_select",
        "content_attributes": {
            "items": items
        },
        "message_type": "outgoing",
        "private": False
    }
    
    try:
        print(f"🔄 Trying input_select fallback...")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Chatwoot input_select fallback sent successfully ({len(options)} options)")
            return True
        else:
            print(f"⚠️ Chatwoot input_select fallback failed: {response.status_code} - {response.text[:100]}")
            # Final fallback to numbered text
            return send_numbered_fallback(conversation_id, text, options)
    except Exception as e:
        print(f"❌ Chatwoot input_select fallback error: {e}")
        # Final fallback to numbered text
        return send_numbered_fallback(conversation_id, text, options)

def send_input_select_fallback(conversation_id, text, options):
    """Fallback to input_select format if WhatsApp buttons fail"""
    # Check for duplicate messages (but allow first message in new conversation)
    conv_attrs = get_conv_attrs(conversation_id)
    last_message = conv_attrs.get("last_bot_message", "")
    pending_intent = conv_attrs.get("pending_intent", "")
    
    # Don't check for duplicates if conversation is in handoff state
    if pending_intent == "handoff":
        print(f"👨‍🏫 Conversation is in handoff state - not sending duplicate message")
        return False

    # For new conversations, clear any old last_bot_message to prevent false duplicates
    if not last_message or last_message.strip() == "":
        print(f"🆕 New conversation detected - clearing old message history")
        set_conv_attrs(conversation_id, {"last_bot_message": ""})
        last_message = ""
    
    # Only check for duplicates if we've already sent a message AND it's the exact same text
    if last_message and text.strip() == last_message.strip():
        print(f"🔄 Duplicate input_select fallback message detected: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print(f"🚨 Auto-handoff triggered due to duplicate input_select fallback message")
        
        # Send handoff message
        handoff_text = t("handoff_duplicate_error", "nl")  # Default to Dutch for error messages
        send_handoff_message(conversation_id, handoff_text)
        return False

    # Store this message as the last sent message (preserve pending_intent)
    current_attrs = get_conv_attrs(conversation_id)
    current_attrs["last_bot_message"] = text
    set_conv_attrs(conversation_id, current_attrs)
    
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": TOK,
        "Content-Type": "application/json"
    }
    
    # Use Chatwoot's official input_select format
    items = []
    for label, value in options:
        items.append({
            "title": label,
            "value": value
        })
    
    data = {
        "content": text,
        "content_type": "input_select",
        "content_attributes": {
            "items": items
        },
        "message_type": "outgoing",
        "private": False
    }
    
    try:
        print(f"🔄 Trying input_select fallback...")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Chatwoot input_select fallback sent successfully ({len(options)} options)")
            return True
        else:
            print(f"⚠️ Chatwoot input_select fallback failed: {response.status_code} - {response.text[:100]}")
            # Final fallback to numbered options
            return send_numbered_fallback(conversation_id, text, options)
    except Exception as e:
        print(f"❌ Chatwoot input_select fallback error: {e}")
        # Final fallback to numbered options
        return send_numbered_fallback(conversation_id, text, options)

def send_numbered_fallback(conversation_id, text, options):
    """Final fallback: send numbered options as plain text with duplicate detection"""
    numbered_text = text + "\n\n"
    for i, (label, value) in enumerate(options, 1):
        numbered_text += f"{i}. {label}\n"
    
    numbered_text += "\n" + t("numbered_fallback_instruction", "nl")  # Default to Dutch for fallback
    
    print(f"📝 Sending numbered fallback: {len(options)} options")
    return send_text_with_duplicate_check(conversation_id, numbered_text)

def send_intake_form(conversation_id, lang):
    """Send comprehensive intake form using Chatwoot form content_type with fallback"""
    url = f"{CW}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": ADMIN_TOK,
        "Content-Type": "application/json"
    }
    
    # Create form items based on language
    if lang == "en":
        form_items = [
            {
                "name": "learner_name",
                "placeholder": "Enter student's full name",
                    "type": "text",
                "label": "Student Name",
                "required": True
            },
            {
                "name": "school_level",
                "label": "Education Level",
                    "type": "select",
                "required": True,
                    "options": [
                    {"label": "Primary School (PO)", "value": "po"},
                        {"label": "VMBO", "value": "vmbo"},
                        {"label": "HAVO", "value": "havo"},
                        {"label": "VWO", "value": "vwo"},
                        {"label": "MBO", "value": "mbo"},
                    {"label": "University (WO)", "value": "university_wo"},
                    {"label": "University of Applied Sciences (HBO)", "value": "university_hbo"},
                    {"label": "Adult Education", "value": "adult"}
                    ]
                },
                {
                    "name": "subject",
                "label": "Subject/Topic",
                    "type": "select",
                "required": True,
                    "options": [
                    {"label": "Mathematics", "value": "subject:math"},
                    {"label": "Statistics", "value": "subject:stats"},
                    {"label": "English", "value": "subject:english"},
                    {"label": "Programming", "value": "subject:programming"},
                    {"label": "Physics", "value": "subject:science"},
                    {"label": "Chemistry", "value": "subject:science"},
                    {"label": "Other", "value": "other"}
                ]
            },
            {
                "name": "goals",
                "placeholder": "Describe learning goals, deadlines, or specific topics",
                "type": "text_area",
                "label": "Learning Goals (Optional)",
                "required": False
            },
            {
                "name": "preferred_times",
                "placeholder": "e.g., Monday 19:00, Wednesday 20:00",
                "type": "text_area",
                "label": "Preferred Lesson Times",
                "required": True
            },
            {
                "name": "lesson_mode",
                "label": "Lesson Format",
                    "type": "select",
                "required": True,
                    "options": [
                    {"label": "💻 Online", "value": "online"},
                    {"label": "🏠 In-person", "value": "in_person"},
                    {"label": "🔀 Hybrid", "value": "hybrid"}
                ]
            }
        ]
        form_content = "Please fill in the student information:"
    else:
        # Dutch version
        form_items = [
            {
                "name": "learner_name",
                "placeholder": "Vul de volledige naam van de leerling in",
                "type": "text",
                "label": "Naam Leerling",
                "required": True
            },
            {
                "name": "school_level",
                "label": "Onderwijsniveau",
                "type": "select",
                "required": True,
                "options": [
                    {"label": "Primair Onderwijs (PO)", "value": "po"},
                    {"label": "VMBO", "value": "vmbo"},
                    {"label": "HAVO", "value": "havo"},
                    {"label": "VWO", "value": "vwo"},
                    {"label": "MBO", "value": "mbo"},
                    {"label": "Universiteit (WO)", "value": "university_wo"},
                    {"label": "Hogeschool (HBO)", "value": "university_hbo"},
                    {"label": "Volwassenenonderwijs", "value": "adult"}
                ]
            },
            {
                "name": "subject",
                "label": "Vak/Onderwerp",
                "type": "select",
                "required": True,
                "options": [
                    {"label": "Wiskunde", "value": "subject:math"},
                    {"label": "Statistiek", "value": "subject:stats"},
                    {"label": "Engels", "value": "subject:english"},
                    {"label": "Programmeren", "value": "subject:programming"},
                    {"label": "Natuurkunde", "value": "subject:science"},
                    {"label": "Scheikunde", "value": "subject:science"},
                    {"label": "Anders", "value": "other"}
                ]
            },
            {
                "name": "goals",
                "placeholder": "Beschrijf leerdoelen, deadlines of specifieke onderwerpen",
                    "type": "text_area",
                "label": "Leerdoelen (Optioneel)",
                "required": False
            },
            {
                "name": "preferred_times",
                "placeholder": "bijv. maandag 19:00, woensdag 20:00",
                "type": "text_area",
                "label": "Voorkeurslesmomenten",
                "required": True
            },
            {
                "name": "lesson_mode",
                "label": "Lesvorm",
                "type": "select",
                "required": True,
                "options": [
                    {"label": "💻 Online", "value": "online"},
                    {"label": "🏠 Fysiek", "value": "in_person"},
                    {"label": "🔀 Hybride", "value": "hybrid"}
                ]
            }
        ]
        form_content = "Vul de gegevens van de leerling in:"
    
    # Try form first
    data = {
        "content": form_content,
        "content_type": "form",
        "content_attributes": {
            "items": form_items
        },
        "message_type": "outgoing",
        "private": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Intake form sent successfully")
            return True
        else:
            print(f"⚠️ Intake form failed: {response.status_code} - {response.text[:100]}")
            print(f"🔄 Falling back to interactive menu approach")
            return send_intake_fallback(conversation_id, lang)
    except Exception as e:
        print(f"❌ Intake form error: {e}")
        print(f"🔄 Falling back to interactive menu approach")
        return send_intake_fallback(conversation_id, lang)

def send_intake_fallback(conversation_id, lang):
    """Fallback: send intake as interactive menu instead of form"""
    print(f"📋 Starting interactive intake flow")
    
    # Set the intake step to start with learner_name
    set_conv_attrs(conversation_id, {
        "pending_intent": "intake",
        "intake_step": "learner_name"
    })
    
    # Send the first question
    if lang == "en":
        send_text_with_duplicate_check(conversation_id, "What is the student's full name?")
    else:
        send_text_with_duplicate_check(conversation_id, "Wat is de volledige naam van de leerling?")
    
    return True

# Note: All API functions are now imported from cw_api module
# The old functions have been replaced with the new ChatwootAPI class

# Segment detection
def detect_segment(contact_id):
    """Detect segment based on contact attributes and history"""
    contact_attrs = get_contact_attrs(contact_id)
    
    # 1. Weekend segment (whitelist check)
    if contact_attrs.get("weekend_whitelisted"):
        return "weekend"
    
    # 2. Returning broadcast (begin school year list)
    # This would check against a broadcast list - for now, we'll use a flag
    if contact_attrs.get("returning_broadcast"):
        return "returning_broadcast"
    
    # 3. Existing customer - check multiple indicators
    if (contact_attrs.get("customer_since") or 
        contact_attrs.get("has_paid_lesson") or
        contact_attrs.get("has_completed_intake") or
        contact_attrs.get("trial_lesson_completed") or
        contact_attrs.get("lesson_booked")):
        return "existing"
    
    # 4. Default to new
    return "new"

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
    }
}

# Calendar integration (mock implementation)
def suggest_slots(conversation_id, profile_name):
    """Suggest available slots based on planning profile"""
    profile = PLANNING_PROFILES.get(profile_name, PLANNING_PROFILES["new"])
    
    # Mock implementation - in real implementation, this would query Google Calendar
    now = datetime.now(TZ)
    slots = []
    
    for i in range(profile["days_ahead"]):
        date = now + timedelta(days=i)
        
        # Skip weekends if exclude_weekends is True
        if profile["exclude_weekends"] and date.weekday() >= 5:
            continue
            
        # Skip non-allowed weekdays for weekend profile
        if profile.get("allowed_weekdays") and date.weekday() not in profile["allowed_weekdays"]:
            continue
        
        # Generate slots for this day
        for hour in range(profile["earliest_hour"], profile["latest_hour"]):
            start_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=profile["duration_minutes"])
            
            # Check if slot is in the future and meets minimum lead time
            if start_time > now + timedelta(minutes=profile["min_lead_minutes"]):
                slot_label = f"{start_time.strftime('%a %d %b %H:%M')}–{end_time.strftime('%H:%M')}"
                slots.append({
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "label": slot_label
                })
    
    # Return first 6-10 slots
    return slots[:8]

def book_slot(conversation_id, start_time, end_time, title, description):
    """Book a slot in Google Calendar"""
    # Mock implementation - in real implementation, this would create a Google Calendar event
    print(f"📅 Booking slot: {start_time} - {end_time}")
    print(f"📅 Title: {title}")
    print(f"📅 Description: {description}")
    
    # Return mock event ID
    return {
        "id": f"mock_event_{conversation_id}_{int(datetime.now().timestamp())}",
        "htmlLink": "https://calendar.google.com/event?eid=mock"
    }

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
    message_content = data.get("content", "")[:50] + "..." if len(data.get("content", "")) > 50 else data.get("content", "")
    event_str = event.upper() if event else "UNKNOWN"

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
        print(f"🌍 Prompting for language selection")
        send_interactive_menu(cid, t("language_question", "nl"), [
            ("🇳🇱 Nederlands", "lang_nl"),
            ("🇬🇧 English", "lang_en")
        ])
        set_conv_attrs(cid, {"language_prompted": True})
    else:
        # Show appropriate menu based on segment
        print(f"📋 Showing segment menu for {segment}")
        show_segment_menu(cid, contact_id, segment, contact_attrs.get("language", "nl"))

def handle_message_created(data):
    """Handle new message"""
    conversation = data.get("conversation", {})
    sender = data.get("sender", {})
    
    cid = conversation.get("id")
    contact_id = sender.get("id")
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
    
    # Check for duplicate message processing
    conv_attrs = get_conv_attrs(cid)
    last_processed_message = conv_attrs.get("last_processed_message", "")
    if msg_content == last_processed_message:
        print(f"🔄 Duplicate message detected: '{msg_content[:50]}{'...' if len(msg_content) > 50 else ''}' - skipping")
        return
    
    # Mark this message as processed immediately to prevent race conditions
    set_conv_attrs(cid, {"last_processed_message": msg_content})
    
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
    
    # Skip processing if conversation is in handoff state
    if conv_attrs.get("pending_intent") == "handoff":
        print(f"👨‍🏫 Conversation is in handoff state - ignoring message")
        return
    
    # Handle language selection FIRST (including input_select values and numbers)
    if msg_content.lower() in ["🇳🇱 nederlands", "nl", "nederlands", "dutch", "🇳🇱", "lang_nl", "nederlands", "1", "1.", "🇳🇱 nederlands"] or "🇳🇱" in msg_content:
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
    
    if msg_content.lower() in ["🇬🇧 english", "en", "english", "engels", "🇬🇧", "lang_en", "english", "2", "2.", "🇬🇧 english"] or "🇬🇧" in msg_content:
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
    
    # Check if language needs to be prompted (for existing conversations)
    if not contact_attrs.get("language") and not conv_attrs.get("language_prompted"):
        print(f"🌍 Prompting for language selection (existing conversation)")
        send_interactive_menu(cid, t("language_question", "nl"), [
            ("🇳🇱 Nederlands", "lang_nl"),
            ("🇬🇧 English", "lang_en")
        ])
        set_conv_attrs(cid, {"language_prompted": True})
        return
    
    # If language is already set, don't ask again
    if contact_attrs.get("language"):
        print(f"✅ Language already set to: {contact_attrs.get('language')}")
        # Continue with normal flow
    
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
    
    # Handle info menu selections
    if conv_attrs.get("pending_intent") == "info_menu":
        print(f"📄 Processing info menu selection")
        handle_info_menu_selection(cid, contact_id, msg_content, lang)
        return
    
    # Handle main menu selections
    print(f"🔘 Processing menu selection")
    handle_menu_selection(cid, contact_id, msg_content, lang)

def show_info_menu(cid, lang):
    """Show information menu with detailed options"""
    print(f"📄 Showing info menu in {lang}")
    print(f"🔧 Setting pending_intent to 'info_menu' for conversation {cid}")
    set_conv_attrs(cid, {"pending_intent": "info_menu"})
    print(f"🔧 Pending intent set, now sending interactive menu")
    send_interactive_menu(cid, t("info_menu_question", lang), [
        (t("menu_option_plan_lesson", lang), "plan_lesson"),
        (t("menu_tariffs", lang), "tariffs"),
        (t("menu_work_method", lang), "work_method"),
        (t("menu_services", lang), "services"),
        (t("menu_travel_costs", lang), "travel_costs"),
        (t("menu_last_minute", lang), "last_minute"),
        (t("menu_conditions", lang), "conditions"),
        (t("menu_weekend_programs", lang), "weekend_programs"),
        (t("menu_short_version", lang), "short_version"),
        (t("menu_option_handoff", lang), "handoff")
    ])

def handle_info_menu_selection(cid, contact_id, msg_content, lang):
    """Handle info menu selections"""
    print(f"📄 Info menu selection: '{msg_content}'")
    
    # Handle lesson planning
    if msg_content.lower() in ["plan_lesson", "les inplannen", "1"] or "📅" in msg_content:
        print(f"📅 Lesson planning requested from info menu")
        start_planning_flow(cid, contact_id, lang)
        return
    
    # Handle tariffs
    if msg_content.lower() in ["tariffs", "tarieven", "2"] or "💰" in msg_content:
        print(f"💰 Showing tariffs")
        send_text_with_duplicate_check(cid, t("info_tariffs", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle work method
    if msg_content.lower() in ["work_method", "werkwijze", "3"] or "🎯" in msg_content:
        print(f"🎯 Showing work method")
        send_text_with_duplicate_check(cid, t("info_work_method", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle services
    if msg_content.lower() in ["services", "diensten", "4"] or "📚" in msg_content:
        print(f"📚 Showing services")
        send_text_with_duplicate_check(cid, t("info_services", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle travel costs
    if msg_content.lower() in ["travel_costs", "reiskosten", "5"] or "🚗" in msg_content:
        print(f"🚗 Showing travel costs")
        send_text_with_duplicate_check(cid, t("info_travel_costs", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle last-minute
    if msg_content.lower() in ["last_minute", "last-minute", "6"] or "⏰" in msg_content:
        print(f"⏰ Showing last-minute surcharges")
        send_text_with_duplicate_check(cid, t("info_last_minute", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle conditions
    if msg_content.lower() in ["conditions", "voorwaarden", "7"] or "📋" in msg_content:
        print(f"📋 Showing conditions")
        send_text_with_duplicate_check(cid, t("info_conditions", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle weekend programs
    if msg_content.lower() in ["weekend_programs", "weekend programma's", "8"] or "🌅" in msg_content:
        print(f"🌅 Showing weekend programs")
        send_text_with_duplicate_check(cid, t("info_weekend_programs", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle short version
    if msg_content.lower() in ["short_version", "korte versie", "9"] or "📝" in msg_content:
        print(f"📝 Showing short version")
        send_text_with_duplicate_check(cid, t("info_short_version", lang))
        show_info_menu(cid, lang)
        return
    
    # Handle handoff
    if msg_content.lower() in ["handoff", "stephen spreken", "10"] or "👨‍🏫" in msg_content:
        print(f"👨‍🏫 Handoff to Stephen requested")
        send_text_with_duplicate_check(cid, t("handoff_teacher", lang))
        add_conv_labels(cid, ["intent_handoff_teacher"])
        set_conv_attrs(cid, {"pending_intent": "handoff"})
        return
    
    # If no valid option, show the info menu again
    print(f"❓ Unknown info menu option: '{msg_content}' - showing info menu")
    show_info_menu(cid, lang)

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
    
    # No need for menu_sent flag anymore - using last_bot_message for duplicate detection
    
    if segment == "new":
        send_interactive_menu(cid, t("menu_new", lang), [
            (t("menu_option_trial_lesson", lang), "plan_lesson"),
            (t("menu_option_info", lang), "info"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "existing":
        send_interactive_menu(cid, t("menu_existing", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_same_preferences", lang), "same_preferences"),
            (t("menu_option_different", lang), "different"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "returning_broadcast":
        send_interactive_menu(cid, t("menu_returning_broadcast", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_old_preferences", lang), "old_preferences"),
            (t("menu_option_new_intake", lang), "new_intake"),
            (t("menu_option_handoff", lang), "handoff")
        ])
    elif segment == "weekend":
        send_interactive_menu(cid, t("menu_weekend", lang), [
            (t("menu_option_plan_lesson", lang), "plan_lesson"),
            (t("menu_option_info", lang), "info"),
            (t("menu_option_handoff", lang), "handoff")
        ])

def handle_menu_selection(cid, contact_id, msg_content, lang):
    """Handle main menu selections"""
    contact_attrs = get_contact_attrs(contact_id)
    segment = contact_attrs.get("segment", "new")
    
    print(f"🔘 Menu selection: '{msg_content}' for {segment} customer")
    
    # Handle lesson planning (trial for new customers, regular for existing)
    if (msg_content.lower() in ["plan_lesson", "les inplannen", "1"] or 
        "📅" in msg_content or 
        "🎯 proefles inplannen" in msg_content.lower() or
        "🎯 schedule trial lesson" in msg_content.lower()):
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
        send_text_with_duplicate_check(cid, t("handoff_teacher", lang))
        add_conv_labels(cid, ["intent_handoff_teacher"])
        set_conv_attrs(cid, {"pending_intent": "handoff"})
        return
    
    # If no valid menu option, show the menu again
    print(f"❓ Unknown menu option: '{msg_content}' - showing menu")
    show_segment_menu(cid, contact_id, segment, lang)
    
def is_existing_customer(contact_attrs):
    """Check if contact is an existing customer (student or parent)"""
    return (contact_attrs.get("is_student") or 
            contact_attrs.get("is_parent") or
            contact_attrs.get("has_completed_intake") or
            contact_attrs.get("trial_lesson_completed") or
            contact_attrs.get("has_paid_lesson") or
            contact_attrs.get("lesson_booked"))

def start_planning_flow(cid, contact_id, lang):
    """Start planning flow - determines if trial or regular lesson"""
    contact_attrs = get_contact_attrs(contact_id)
    
    # Detect current segment
    current_segment = detect_segment(contact_id)
    
    if is_existing_customer(contact_attrs):
        print(f"📅 Existing customer - planning regular lesson")
        # Existing customer gets direct planning for regular lesson
        set_conv_attrs(cid, {
            "planning_profile": current_segment,
            "lesson_type": "regular"
        })
        send_text_with_duplicate_check(cid, t("planning_regular_lesson", lang))
        suggest_available_slots(cid, current_segment, lang)
    else:
        print(f"🎯 New customer - starting intake for trial lesson")
        # New customer gets intake flow for trial lesson
        set_conv_attrs(cid, {"lesson_type": "trial"})
        start_intake_flow(cid, contact_id, lang)

def start_intake_flow(cid, contact_id, lang):
    """Start the intake flow"""
    print(f"📋 Starting intake flow for Conv:{cid}")
    set_conv_attrs(cid, {
        "pending_intent": "intake",
        "intake_step": "for_who"
    })
    
    send_interactive_menu(cid, t("intake_for_who", lang), [
        (t("intake_option_self", lang), "self"),
        (t("intake_option_other", lang), "other")
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
            send_interactive_menu(cid, t("intake_age_check", lang), [
                ("✅ Ja", "yes"),
                ("❌ Nee", "no")
            ])
        elif msg_content.lower() in ["other", "voor iemand anders", "2"] or "👥" in msg_content:
            set_conv_attrs(cid, {
                "pending_intent": "intake", 
                "intake_step": "relationship",
                "for_who": "other"
            })
            send_interactive_menu(cid, t("intake_relationship", lang), [
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
            print(f"[DEBUG] Age check: Starting intake form")
            # Send comprehensive intake form (with fallback)
            send_intake_form(cid, lang)
        # Check for various ways to say no
        elif (msg_content.lower() in ["no", "nee", "2", "nee.", "no."] or 
              "❌" in msg_content or 
              msg_content.strip().lower() in ["nee", "no"]):
            print(f"❌ Age check: Minor confirmed")
            set_contact_attrs(contact_id, {"is_adult": False})
            set_conv_attrs(cid, {"pending_intent": "intake", "intake_step": "guardian_name"})
            send_text_with_duplicate_check(cid, t("intake_guardian_info", lang))
        else:
            print(f"❓ Age check: Unknown response '{msg_content}' - asking again")
            send_interactive_menu(cid, t("intake_age_check", lang), [
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
        send_interactive_menu(cid, t("intake_level", lang), [
            ("PO", "po"),
            ("VMBO", "vmbo"),
            ("HAVO", "havo"),
            ("VWO", "vwo"),
            ("MBO", "mbo"),
            ("WO", "university_wo"),
            ("HBO", "university_hbo"),
            ("Adult", "adult")
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
        send_interactive_menu(cid, t("intake_level", lang), [
            ("PO", "po"),
            ("VMBO", "vmbo"),
            ("HAVO", "havo"),
            ("VWO", "vwo"),
            ("MBO", "mbo"),
            ("WO", "university_wo"),
            ("HBO", "university_hbo"),
            ("Adult", "adult")
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
        send_interactive_menu(cid, t("intake_subject", lang), [
            ("Wiskunde", "subject:math"),
            ("Statistiek", "subject:stats"),
            ("Engels", "subject:english"),
            ("Programmeren", "subject:programming"),
            ("Natuurkunde", "subject:science"),
            ("Scheikunde", "subject:science"),
            ("Anders", "other")
        ])
    
    elif step == "subject":
        if msg_content.lower() != "other":
            add_conv_labels(cid, [msg_content])
        set_conv_attrs(cid, {"pending_intent": "intake", "intake_step": "goals"})
        print(f"[DEBUG] Intake: subject ingevuld, door naar goals. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_text_with_duplicate_check(cid, t("intake_goals", lang))
    
    elif step == "goals":
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "topic_secondary": msg_content,
            "intake_step": "preferred_times"
        })
        print(f"[DEBUG] Intake: goals ingevuld, door naar preferred_times. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_text_with_duplicate_check(cid, t("intake_preferred_times", lang))
    
    elif step == "preferred_times":
        set_conv_attrs(cid, {
            "pending_intent": "intake",
            "preferred_times": msg_content,
            "intake_step": "mode"
        })
        print(f"[DEBUG] Intake: preferred_times ingevuld, door naar mode. pending_intent={get_conv_attrs(cid).get('pending_intent')}, intake_step={get_conv_attrs(cid).get('intake_step')}")
        send_interactive_menu(cid, t("intake_mode", lang), [
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
            "lesson_mode": msg_content,
            "intake_completed": True,
            "pending_intent": "planning"
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
        send_text_with_duplicate_check(cid, t("no_slots_available", lang))
        return
    
    print(f"✅ Found {len(slots)} available slots")
    
    # Create quick reply options
    options = []
    for slot in slots:
        options.append((slot["label"], slot["start"]))
    
    options.append((t("planning_more_options", lang), "more_options"))
    
    lesson_text = "Beschikbare tijden voor proefles:" if lesson_type == "trial" else "Beschikbare tijden voor les:"
    send_interactive_menu(cid, lesson_text, options)

def handle_planning_selection(cid, contact_id, msg_content, lang):
    """Handle planning slot selection"""
    if msg_content == "more_options":
        # Suggest more options (extend time horizon)
        conv_attrs = get_conv_attrs(cid)
        profile_name = conv_attrs.get("planning_profile", "new")
        suggest_available_slots(cid, profile_name, lang)
        return
    
    # Check if this is a slot selection (format: "2025-08-05T12:00:00+02:00")
    if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', msg_content):
        # Book the slot
        conv_attrs = get_conv_attrs(cid)
        learner_name = conv_attrs.get("learner_name", "Student")
        
        # Create tentative booking
        event = book_slot(
            cid,
            msg_content,
            msg_content,  # End time would be calculated
            f"Stephen's Privélessen — Pending confirmation",
            f"Trial lesson for {learner_name}"
        )
        
        # Confirm booking
        send_text_with_duplicate_check(cid, t("planning_confirm", lang, slot=msg_content))
        
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
            set_conv_attrs(cid, {"pending_intent": ""})
            send_text_with_duplicate_check(cid, t("trial_lesson_confirmed", lang))
        else:
            # This is a regular lesson, create payment link
            create_payment_request(cid, contact_id, lang)

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
    
    # Add payment labels
    add_conv_labels(cid, ["status:awaiting_pay"])
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
    
    # Update conversation labels
    remove_conv_labels(conversation_id, ["status:awaiting_pay"])
    add_conv_labels(conversation_id, ["payment:paid", "status:booked"])
    
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True) 