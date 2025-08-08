#!/usr/bin/env python3
"""
Setup FAQ Data for TutorBot
Integrates FAQ questions and answers into the bot's translation system
"""

import os
import sys
import yaml
import re
from typing import Dict, List, Any

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "docs/FAQ_DATA.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Error: Script must be run from the project root directory!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Expected project root: {project_root}")
        print(f"   Missing files: {', '.join(missing_files)}")
        print(f"\n💡 Solution: Run from the project root:")
        print(f"   cd {project_root}")
        print(f"   python3 scripts/setup_faq.py")
        sys.exit(1)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory before importing anything else
PROJECT_ROOT = ensure_project_root()

def parse_faq_data():
    """Parse FAQ data from the markdown file"""
    print("📖 Parsing FAQ data from docs/FAQ_DATA.md...")
    
    with open('docs/FAQ_DATA.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse main FAQ questions (1-20)
    main_faq = {}
    
    # Find all FAQ questions
    question_pattern = r'### (\d+)\. (.+?)\n\*\*NL:\*\* (.+?)\n\*\*EN:\*\* (.+?)\n\n\*\*NL:\*\* (.+?)\n\n\*\*EN:\*\* (.+?)(?=\n\n---|\n\n##|$)'
    matches = re.findall(question_pattern, content, re.DOTALL)
    
    for match in matches:
        number = int(match[0])
        question_en = match[1].strip()
        question_nl = match[2].strip()
        answer_nl = match[4].strip()
        answer_en = match[5].strip()
        
        main_faq[number] = {
            'question_nl': question_nl,
            'question_en': question_en,
            'answer_nl': answer_nl,
            'answer_en': answer_en
        }
    
    print(f"✅ Parsed {len(main_faq)} main FAQ questions")
    
    # Parse tutoring page FAQ (3 questions)
    tutoring_faq = {}
    
    # Find tutoring FAQ section
    tutoring_pattern = r'### (\d+)\. (.+?)\n\*\*NL:\*\* (.+?)\n\*\*EN:\*\* (.+?)\n\n\*\*NL:\*\* (.+?)\n\n\*\*EN:\*\* (.+?)(?=\n\n---|\n\n##|$)'
    tutoring_matches = re.findall(tutoring_pattern, content, re.DOTALL)
    
    for match in tutoring_matches:
        number = int(match[0])
        question_en = match[1].strip()
        question_nl = match[2].strip()
        answer_nl = match[4].strip()
        answer_en = match[5].strip()
        
        tutoring_faq[number] = {
            'question_nl': question_nl,
            'question_en': question_en,
            'answer_nl': answer_nl,
            'answer_en': answer_en
        }
    
    print(f"✅ Parsed {len(tutoring_faq)} tutoring FAQ questions")
    
    return main_faq, tutoring_faq

def generate_faq_translations(main_faq, tutoring_faq):
    """Generate FAQ translations for the bot"""
    print("🔧 Generating FAQ translations...")
    
    translations = {}
    
    # Add main FAQ translations
    for number, faq in main_faq.items():
        # Question translations
        translations[f"faq_{number}_question"] = {
            "nl": faq['question_nl'],
            "en": faq['question_en']
        }
        
        # Answer translations
        translations[f"faq_{number}_answer"] = {
            "nl": faq['answer_nl'],
            "en": faq['answer_en']
        }
    
    # Add tutoring FAQ translations
    for number, faq in tutoring_faq.items():
        # Question translations
        translations[f"tutoring_faq_{number}_question"] = {
            "nl": faq['question_nl'],
            "en": faq['question_en']
        }
        
        # Answer translations
        translations[f"tutoring_faq_{number}_answer"] = {
            "nl": faq['answer_nl'],
            "en": faq['answer_en']
        }
    
    # Add FAQ metadata
    translations.update({
        "faq_title": {
            "nl": "Veelgestelde Vragen",
            "en": "Frequently Asked Questions"
        },
        "faq_description": {
            "nl": "Vind antwoorden op veelvoorkomende vragen over onze privélessen.",
            "en": "Find answers to common questions about our private tutoring services."
        },
        "faq_search_placeholder": {
            "nl": "Zoeken...",
            "en": "Search..."
        },
        "faq_language_toggle": {
            "nl": "EN",
            "en": "NL"
        },
        "faq_scroll_to_top": {
            "nl": "Scroll naar boven",
            "en": "Scroll to top"
        }
    })
    
    print(f"✅ Generated {len(translations)} FAQ translations")
    return translations

def update_main_py_with_faq(translations):
    """Update main.py with FAQ translations"""
    print("📝 Updating main.py with FAQ translations...")
    
    # Read main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the translations dictionary
    # Look for the start of the translations dictionary
    start_pattern = r'def t\(key, lang="nl", \*\*kwargs\):\s*\n\s*"""Comprehensive translation function"""\s*\n\s*translations = \{'
    
    if not re.search(start_pattern, content):
        print("❌ Could not find translations dictionary in main.py")
        return False
    
    # Find the end of the translations dictionary (before the closing brace and the rest of the function)
    # Look for the pattern that ends the translations dictionary
    end_pattern = r'(\s*\}\s*\n\s*# Get language-specific translation)'
    
    # Create the new FAQ translations string
    faq_translations_str = "\n        # FAQ Translations\n"
    for key, value in translations.items():
        faq_translations_str += f'        "{key}": {{\n'
        faq_translations_str += f'            "nl": "{value["nl"]}",\n'
        faq_translations_str += f'            "en": "{value["en"]}"\n'
        faq_translations_str += f'        }},\n'
    
    # Insert FAQ translations before the closing brace of the translations dictionary
    # Find the pattern that ends the translations dictionary
    pattern = r'(\s*\}\s*\n\s*# Get language-specific translation)'
    
    if re.search(pattern, content):
        # Insert FAQ translations before the closing brace
        replacement = faq_translations_str + r'\1'
        new_content = re.sub(pattern, replacement, content)
        
        # Write back to main.py
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully updated main.py with FAQ translations")
        return True
    else:
        print("❌ Could not find the end of translations dictionary")
        return False

def create_faq_handler_function():
    """Create a FAQ handler function for the bot"""
    print("🤖 Creating FAQ handler function...")
    
    faq_handler = '''
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
        "proefles": 10, "trial": 10, "gratis": 10, "free": 10,
        "beroep": 11, "profession": 11, "scriptie": 11, "thesis": 11,
        "ai": 12, "technology": 12, "technologie": 12, "gpt": 12,
        "soft skills": 13, "communicatie": 13, "time management": 13,
        "leerproblemen": 14, "learning difficulties": 14, "autisme": 14, "autism": 14,
        "motivatie": 15, "motivation": 15, "gemotiveerd": 15,
        "feedback": 16, "suggesties": 16, "suggestions": 16,
        "bedrijven": 17, "companies": 17, "instellingen": 17, "institutions": 17,
        "contact": 18, "informatie": 18, "information": 18,
        "materialen": 19, "materials": 19, "tools": 19, "hulpmiddelen": 19,
        "frequentie": 20, "frequency": 20, "duur": 20, "duration": 20,
        
        # Tutoring FAQ keywords
        "lengte": "tutoring_1", "length": "tutoring_1", "uur": "tutoring_1", "hour": "tutoring_1",
        "docent": "tutoring_2", "tutor": "tutoring_2", "wisselen": "tutoring_2", "change": "tutoring_2",
        "online sessies": "tutoring_3", "online sessions": "tutoring_3"
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
        if isinstance(matched_faq, int):
            # Main FAQ
            answer_key = f"faq_{matched_faq}_answer"
        else:
            # Tutoring FAQ
            answer_key = f"{matched_faq}_answer"
        
        answer = t(answer_key, lang)
        
        # Send the FAQ answer
        send_text_with_duplicate_check(cid, answer)
        return True
    
    # If no specific FAQ matched, offer general FAQ help
    faq_help_msg = t("faq_general_help", lang)
    send_text_with_duplicate_check(cid, faq_help_msg)
    return False
'''
    
    # Read main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if FAQ handler already exists
    if 'def handle_faq_request(' in content:
        print("⚠️ FAQ handler function already exists in main.py")
        return True
    
    # Find a good place to insert the FAQ handler (before the last function)
    # Look for the last function definition
    lines = content.split('\n')
    
    # Find the last function definition
    last_func_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') and 'if __name__' not in line:
            last_func_index = i
    
    if last_func_index == -1:
        print("❌ Could not find a good place to insert FAQ handler")
        return False
    
    # Insert the FAQ handler before the last function
    lines.insert(last_func_index, faq_handler)
    
    # Write back to main.py
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✅ Successfully added FAQ handler function to main.py")
    return True

def add_faq_general_help_translation():
    """Add general FAQ help translation"""
    print("📝 Adding FAQ general help translation...")
    
    # Read main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add the general FAQ help translation
    general_help_translation = '''
        "faq_general_help": {
            "nl": "Ik kan je helpen met veelgestelde vragen! Hier zijn enkele onderwerpen waar je naar kunt vragen:\n\n• Inspiratie en achtergrond\n• Onze onderwijsaanpak\n• Wat ons uniek maakt\n• Leerstijlen en niveaus\n• Resultaten en successen\n• Organisatie van lessen\n• Kosten en tarieven\n• Aanmelden en proefles\n• Betalingen\n• Beroepsspecifieke vakken\n• AI en technologie\n• Soft skills\n• Leerproblemen\n• Motivatie\n• Feedback\n• Bedrijven en instellingen\n• Contact\n• Materialen en tools\n• Frequentie en duur\n\nStel gewoon je vraag en ik help je verder!",
            "en": "I can help you with frequently asked questions! Here are some topics you can ask about:\n\n• Inspiration and background\n• Our teaching approach\n• What makes us unique\n• Learning styles and levels\n• Results and successes\n• Lesson organization\n• Costs and rates\n• Signing up and trial lessons\n• Payments\n• Profession-specific subjects\n• AI and technology\n• Soft skills\n• Learning difficulties\n• Motivation\n• Feedback\n• Companies and institutions\n• Contact\n• Materials and tools\n• Frequency and duration\n\nJust ask your question and I'll help you further!"
        },
'''
    
    # Find the FAQ translations section and add the general help
    pattern = r'(# FAQ Translations\n.*?)(\s*\}\s*\n\s*# Get language-specific translation)'
    
    if re.search(pattern, content, re.DOTALL):
        replacement = r'\1' + general_help_translation + r'\2'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write back to main.py
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully added FAQ general help translation")
        return True
    else:
        print("❌ Could not find FAQ translations section")
        return False

def main():
    """Main function"""
    print("🚀 Setting up FAQ data for TutorBot")
    print("=" * 50)
    
    try:
        # Parse FAQ data
        main_faq, tutoring_faq = parse_faq_data()
        
        # Generate translations
        translations = generate_faq_translations(main_faq, tutoring_faq)
        
        # Update main.py with FAQ translations
        if update_main_py_with_faq(translations):
            print("✅ FAQ translations added to main.py")
        else:
            print("❌ Failed to add FAQ translations to main.py")
            return
        
        # Add FAQ general help translation
        if add_faq_general_help_translation():
            print("✅ FAQ general help translation added")
        else:
            print("❌ Failed to add FAQ general help translation")
        
        # Create FAQ handler function
        if create_faq_handler_function():
            print("✅ FAQ handler function created")
        else:
            print("❌ Failed to create FAQ handler function")
        
        print("\n" + "=" * 50)
        print("✅ FAQ setup completed successfully!")
        print("\n📋 Summary:")
        print(f"   • {len(main_faq)} main FAQ questions added")
        print(f"   • {len(tutoring_faq)} tutoring FAQ questions added")
        print(f"   • {len(translations)} translations generated")
        print(f"   • FAQ handler function created")
        print(f"   • General FAQ help added")
        
        print("\n💡 Next steps:")
        print("   1. Restart the bot: docker-compose restart tutorbot")
        print("   2. Test FAQ functionality by asking questions")
        print("   3. Integrate FAQ handler into message processing")
        
    except Exception as e:
        print(f"❌ Error during FAQ setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
