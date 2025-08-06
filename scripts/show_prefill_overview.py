#!/usr/bin/env python3
"""
Script to manually show prefill overview for existing conversation
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_conv_attrs, send_interactive_menu, set_conv_attrs

def show_prefill_overview(conversation_id):
    """Show prefill overview for existing conversation"""
    
    print(f"🔍 Getting conversation attributes for {conversation_id}...")
    conv_attrs = get_conv_attrs(conversation_id)
    
    if not conv_attrs:
        print("❌ No conversation attributes found")
        return
    
    print(f"📋 Conversation attributes: {list(conv_attrs.keys())}")
    
    # Check if we have prefilled information
    prefilled_keys = [
        'learner_name', 'school_level', 'topic_primary', 'topic_secondary',
        'goals', 'referral_source', 'preferred_times', 'location_preference',
        'contact_name', 'for_who', 'relationship_to_learner'
    ]
    
    prefilled_info = {k: conv_attrs.get(k) for k in prefilled_keys if conv_attrs.get(k)}
    
    if not prefilled_info:
        print("❌ No prefilled information found")
        return
    
    print(f"✅ Found prefilled information: {list(prefilled_info.keys())}")
    
    # Generate overview
    detected_info = []
    
    # Basic information
    if prefilled_info.get("learner_name"):
        detected_info.append(f"👤 *Naam*: {prefilled_info['learner_name']}")
    
    if prefilled_info.get("school_level"):
        level_display = {
            "po": "Basisschool",
            "vmbo": "VMBO", 
            "havo": "HAVO",
            "vwo": "VWO",
            "mbo": "MBO",
            "university_wo": "Universiteit (WO)",
            "university_hbo": "Universiteit (HBO)",
            "adult": "Volwassenenonderwijs"
        }
        level_text = level_display.get(prefilled_info['school_level'], prefilled_info['school_level'])
        detected_info.append(f"🎓 *Niveau*: {level_text}")
    
    # Subject information
    if prefilled_info.get("topic_secondary"):
        detected_info.append(f"📚 *Vak*: {prefilled_info['topic_secondary']}")
    elif prefilled_info.get("topic_primary"):
        topic_display = {
            "math": "Wiskunde",
            "stats": "Statistiek", 
            "english": "Engels",
            "programming": "Programmeren",
            "science": "Natuurkunde",
            "chemistry": "Scheikunde"
        }
        topic_text = topic_display.get(prefilled_info['topic_primary'], prefilled_info['topic_primary'])
        detected_info.append(f"📚 *Vak*: {topic_text}")
    
    # Additional information
    if prefilled_info.get("referral_source"):
        referral_display = {
            "google_search": "Google zoekopdracht",
            "social_media": "Social media",
            "friend_recommendation": "Vriend/kennis aanbeveling",
            "school_recommendation": "School/docent aanbeveling",
            "advertisement": "Advertentie",
            "website": "Website",
            "other": "Anders"
        }
        referral_text = referral_display.get(prefilled_info['referral_source'], prefilled_info['referral_source'])
        detected_info.append(f"📞 *Hoe ben je bij ons terechtgekomen*: {referral_text}")
    
    if prefilled_info.get("goals"):
        detected_info.append(f"🎯 *Leerdoelen*: {prefilled_info['goals']}")
    
    if prefilled_info.get("preferred_times"):
        detected_info.append(f"⏰ *Voorkeur tijd*: {prefilled_info['preferred_times']}")
    
    if prefilled_info.get("location_preference"):
        detected_info.append(f"📍 *Locatie voorkeur*: {prefilled_info['location_preference']}")
    
    if prefilled_info.get("contact_name") and prefilled_info.get("for_who") != "self":
        detected_info.append(f"👤 *Contactpersoon*: {prefilled_info['contact_name']}")
    
    if prefilled_info.get("for_who"):
        for_who_display = {
            "self": "Zichzelf",
            "child": "Kind",
            "student": "Student",
            "other": "Iemand anders"
        }
        for_who_text = for_who_display.get(prefilled_info['for_who'], prefilled_info['for_who'])
        detected_info.append(f"👥 *Voor wie*: {for_who_text}")
    
    if prefilled_info.get("relationship_to_learner"):
        relationship_display = {
            "self": "Zichzelf",
            "parent": "Ouder",
            "teacher": "Docent",
            "other": "Anders"
        }
        relationship_text = relationship_display.get(prefilled_info['relationship_to_learner'], prefilled_info['relationship_to_learner'])
        detected_info.append(f"👨‍👩‍👧‍👦 *Relatie*: {relationship_text}")
    
    if detected_info:
        print(f"📋 Generated overview with {len(detected_info)} items:")
        for info in detected_info:
            print(f"   {info}")
        
        # Set pending intent for confirmation
        set_conv_attrs(conversation_id, {
            "pending_intent": "prefill_confirmation",
            "prefill_confirmation_sent": True
        })
        
        # Send confirmation
        confirmation_text = f"📋 *Wat ik van je bericht begrepen heb:*\n\n" + "\n".join(detected_info)
        confirmation_text += f"\n\n❓ *Klopt dit allemaal?*"
        
        print(f"📤 Sending confirmation to conversation {conversation_id}")
        print(f"📝 Confirmation text: {confirmation_text[:100]}...")
        
        send_interactive_menu(conversation_id, confirmation_text, [
            ("✅ Ja, dat klopt", "confirm_all"),
            ("❌ Nee, aanpassen", "correct_all"),
            ("🤔 Deels correct", "correct_partial")
        ])
        
        print("✅ Prefill overview sent successfully!")
    else:
        print("❌ No information detected for overview")

if __name__ == "__main__":
    conversation_id = 247  # Use existing conversation
    show_prefill_overview(conversation_id) 