#!/usr/bin/env python3
"""
Test script to verify Juul's categorization as university_wo
"""

import os
import sys
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function to test
from main import analyze_first_message_with_openai, map_school_level

def test_juul_categorization():
    """Test that Juul's message is correctly categorized"""
    
    # Juul's actual message
    juul_message = """Hallo Stephen,
Ik zoek een wekelijkse tutor voor het vak aan de Rijksuniversiteit Groningen: Matrix Analysis & Optimization. Zie voor details: https://ocasys.rug.nl/2025-2026/catalog/course/EBB066A05#EBB066A05.2025-2026.1
Het tentamen is op dinsdag 28 oktober en ik MOET deze echt halen. Ik zie nu al aankomen dat naast mijn voltijd baan dit lastig gaat worden, ook met mijn ADHD. Ik heb alle documentatie al incl. 8 proefexamens. Ik zoek voor een wekelijkse les als stok achter de deur en om vragen te beantwoorden. Het is vrij technisch als 2e jaars wiskunde vak binnen de BSc International Economics. Ik hoor graag of je ervaring hebt met matrices en de andere aspecten van dit vak, even bellen op 0617713170 kan ook. Ik woon in Buitenveldert, bij Amsterdam Zuid. We kunnen afspreken in een universiteitsbieb (al heb ik dus geen pas van de UVA/VU), maar online kan ook.

Vriendelijke groeten,
Juul Oosterhuis"""

    print("🧪 Testing Juul's message categorization...")
    print(f"📝 Message length: {len(juul_message)} characters")
    
    # Test the OpenAI analysis
    try:
        result = analyze_first_message_with_openai(juul_message)
        print(f"✅ OpenAI analysis completed")
        print(f"📊 Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Check school_level specifically
        school_level = result.get("school_level", "NOT_FOUND")
        print(f"🎓 School level detected: '{school_level}'")
        
        if school_level == "university_wo":
            print("✅ SUCCESS: Juul correctly categorized as university_wo!")
        elif school_level == "adult":
            print("❌ FAILURE: Juul incorrectly categorized as adult (should be university_wo)")
        else:
            print(f"⚠️ UNEXPECTED: Juul categorized as '{school_level}' (expected university_wo)")
            
        # Test map_school_level function
        print(f"\n🔧 Testing map_school_level function:")
        test_cases = [
            "bachelor", "master", "BSc", "MSc", "2e jaars", "universiteitsstudent",
            "university", "Rijksuniversiteit", "WO", "bachelor student"
        ]
        
        for test_case in test_cases:
            mapped = map_school_level(test_case)
            print(f"   '{test_case}' → '{mapped}'")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_juul_categorization()
    sys.exit(0 if success else 1)
