#!/usr/bin/env python3
"""
Test script to manually trigger prefill overview display
"""

import os
import sys
import requests
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import prefill_intake_from_message, send_interactive_menu, set_conv_attrs, get_conv_attrs

def test_prefill_overview():
    """Test the prefill overview functionality"""
    
    # Test message that should trigger prefill
    test_message = """Goedemorgen Stephen,

Mijn dochter Maria zit in Havo 5 bij het Spinoza Lyceum. Zij heeft problemen met Wiskunde A: ze leert en maakt huiswerk zonder problemen, maar tijdens de toetsweek behaalde ze een 5,2 (het gemiddelde cijfer voor de hele Havo 5 was 4,5). Ik denk dat ze geen eindexamen heeft gedaan en daardoor geen ervaring heeft met complexere oefeningen. Maria geeft de voorkeur aan "live" lessen, en we wonen niet ver van het Science Park. Maria is woensdagmiddag vrij.

Ik hoor graag van je. Alvast bedankt.

Met vriendelijke groet,  
Roberta Sandrelli"""
    
    conversation_id = 247  # Use existing conversation
    
    print("🔍 Testing prefill from message...")
    print(f"📝 Message: {test_message[:100]}...")
    
    # Test prefill extraction
    prefilled = prefill_intake_from_message(test_message, conversation_id)
    
    if prefilled:
        print(f"✅ Prefill successful: {list(prefilled.keys())}")
        
        # Apply to conversation attributes
        current_attrs = get_conv_attrs(conversation_id)
        current_attrs.update(prefilled)
        current_attrs["has_been_prefilled"] = True
        current_attrs["prefill_processed_for_message"] = test_message
        
        set_conv_attrs(conversation_id, current_attrs)
        
        # Generate overview
        detected_info = []
        
        # Basic information
        if prefilled.get("learner_name"):
            detected_info.append(f"👤 *Naam*: {prefilled['learner_name']}")
        
        if prefilled.get("school_level"):
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
            level_text = level_display.get(prefilled['school_level'], prefilled['school_level'])
            detected_info.append(f"🎓 *Niveau*: {level_text}")
        
        # Subject information
        if prefilled.get("topic_secondary"):
            detected_info.append(f"📚 *Vak*: {prefilled['topic_secondary']}")
        elif prefilled.get("topic_primary"):
            topic_display = {
                "math": "Wiskunde",
                "stats": "Statistiek", 
                "english": "Engels",
                "programming": "Programmeren",
                "science": "Natuurkunde",
                "chemistry": "Scheikunde"
            }
            topic_text = topic_display.get(prefilled['topic_primary'], prefilled['topic_primary'])
            detected_info.append(f"📚 *Vak*: {topic_text}")
        
        # Additional information
        if prefilled.get("referral_source"):
            referral_display = {
                "google_search": "Google zoekopdracht",
                "social_media": "Social media",
                "friend_recommendation": "Vriend/kennis aanbeveling",
                "school_recommendation": "School/docent aanbeveling",
                "advertisement": "Advertentie",
                "website": "Website",
                "other": "Anders"
            }
            referral_text = referral_display.get(prefilled['referral_source'], prefilled['referral_source'])
            detected_info.append(f"📞 *Hoe ben je bij ons terechtgekomen*: {referral_text}")
        
        if prefilled.get("goals"):
            detected_info.append(f"🎯 *Leerdoelen*: {prefilled['goals']}")
        
        if prefilled.get("preferred_times"):
            detected_info.append(f"⏰ *Voorkeur tijd*: {prefilled['preferred_times']}")
        
        if prefilled.get("location_preference"):
            detected_info.append(f"📍 *Locatie voorkeur*: {prefilled['location_preference']}")
        
        if prefilled.get("contact_name") and prefilled.get("for_who") != "self":
            detected_info.append(f"👤 *Contactpersoon*: {prefilled['contact_name']}")
        
        if prefilled.get("for_who"):
            for_who_display = {
                "self": "Zichzelf",
                "child": "Kind",
                "student": "Student",
                "other": "Iemand anders"
            }
            for_who_text = for_who_display.get(prefilled['for_who'], prefilled['for_who'])
            detected_info.append(f"👥 *Voor wie*: {for_who_text}")
        
        if prefilled.get("relationship_to_learner"):
            relationship_display = {
                "self": "Zichzelf",
                "parent": "Ouder",
                "teacher": "Docent",
                "other": "Anders"
            }
            relationship_text = relationship_display.get(prefilled['relationship_to_learner'], prefilled['relationship_to_learner'])
            detected_info.append(f"👨‍👩‍👧‍👦 *Relatie*: {relationship_text}")
        
        if detected_info:
            print(f"📋 Generated overview with {len(detected_info)} items:")
            for info in detected_info:
                print(f"   {info}")
            
            # Set pending intent for confirmation
            set_conv_attrs(conversation_id, {
                "pending_intent": "prefill_confirmation",
                "prefill_confirmation_sent": True,
                "original_message_processed": test_message
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
    else:
        print("❌ Prefill failed - no information extracted")

if __name__ == "__main__":
    test_prefill_overview() 