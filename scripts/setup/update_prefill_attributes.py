#!/usr/bin/env python3
"""
Update Prefill Attributes and Labels Script
This script shows what attributes and labels should be set after prefill confirmation
"""

import os
import sys
import yaml
from typing import Dict, Any, List

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels: setup -> scripts -> project_root
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "config/contact_attributes.yaml",
        "config/conversation_attributes.yaml",
        "config/labels_lean.yaml"
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
        print(f"   python3 scripts/setup/update_prefill_attributes.py")
        sys.exit(1)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

# Ensure we're in the right directory before importing anything else
PROJECT_ROOT = ensure_project_root()

def load_config(filename: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_path = os.path.join(PROJECT_ROOT, "config", filename)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ {config_path} not found!")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Error parsing {config_path}: {e}")
        return {}

def analyze_prefill_confirmation_flow():
    """Analyze what attributes and labels should be set after prefill confirmation"""
    
    print("🎯 PREFILL CONFIRMATION FLOW ANALYSIS")
    print("=" * 50)
    
    # Load configurations
    contact_attrs_config = load_config("contact_attributes.yaml")
    conv_attrs_config = load_config("conversation_attributes.yaml")
    labels_config = load_config("labels_lean.yaml")
    
    print("\n📋 CONTACT ATTRIBUTES (Persistent)")
    print("-" * 30)
    
    # Contact attributes that should be set after prefill confirmation
    contact_attributes_to_set = {
        "language": "User's preferred language (nl/en)",
        "school_level": "Education level (po/vmbo/havo/vwo/mbo/university_wo/university_hbo/adult)",
        "segment": "Customer segment (new/existing/returning_broadcast/weekend)",
        "is_adult": "Age verification status",
        "learner_name": "Name of the student/learner",
        "contact_name": "Name of the contact person (if different from learner)",
        "contact_email": "Email address",
        "contact_phone": "Phone number",
        "child_contact_id": "ID of child contact (if parent writing for child)",
        "customer_since": "When they became a customer",
        "has_completed_intake": "Whether intake flow was completed",
        "trial_lesson_completed": "Whether trial lesson was completed",
        "lesson_booked": "Whether any lesson was booked",
        "has_paid_lesson": "Whether they paid for a lesson"
    }
    
    for attr, description in contact_attributes_to_set.items():
        config = contact_attrs_config.get("contact_attributes", {}).get(attr, {})
        display_name = config.get("attribute_display_name", attr)
        print(f"  ✅ {attr} ({display_name}): {description}")
    
    print("\n📋 CONVERSATION ATTRIBUTES (Per conversation)")
    print("-" * 40)
    
    # Conversation attributes that should be set after prefill confirmation
    conv_attributes_to_set = {
        "pending_intent": "What user wants to do next",
        "prefill_confirmation_sent": "Whether confirmation was sent",
        "use_prefill": "Flag to use prefill in planning flow",
        "has_been_prefilled": "Whether prefill was processed",
        "learner_name": "Name of the student/learner",
        "school_level": "Education level",
        "topic_primary": "Primary subject",
        "topic_secondary": "Secondary subject",
        "goals": "Learning goals",
        "preferred_times": "Preferred lesson times",
        "lesson_mode": "Lesson format (online/in_person/hybrid)",
        "relationship_to_learner": "Relationship to learner (parent/family/teacher/other)",
        "for_who": "Who the lesson is for (self/child/student/other)",
        "contact_name": "Contact person name",
        "location_preference": "Preferred location",
        "toolset": "Required tools",
        "urgency": "Urgency level",
        "planning_profile": "Planning profile (new/existing/returning_broadcast/weekend)"
    }
    
    for attr, description in conv_attributes_to_set.items():
        config = conv_attrs_config.get("conversation_attributes", {}).get(attr, {})
        display_name = config.get("attribute_display_name", attr)
        print(f"  ✅ {attr} ({display_name}): {description}")
    
    print("\n🏷️ LABELS TO SET")
    print("-" * 20)
    
    # Labels that should be set based on prefill information
    labels_to_set = {
        "audience": {
            "audience_po": "Primary education",
            "audience_vmbo": "VMBO",
            "audience_havo": "HAVO", 
            "audience_vwo": "VWO",
            "audience_mbo": "MBO",
            "audience_university_wo": "University (WO)",
            "audience_university_hbo": "University (HBO)",
            "audience_adult": "Adult education"
        },
        "subject": {
            "subject_math": "Mathematics",
            "subject_stats": "Statistics",
            "subject_science": "Science",
            "subject_english": "English",
            "subject_programming": "Programming"
        },
        "service": {
            "service_trial": "Trial lesson",
            "service_1on1": "One-on-one lessons"
        },
        "process": {
            "status_awaiting_reply": "Waiting for user response"
        },
        "source": {
            "source_whatsapp": "Came via WhatsApp"
        }
    }
    
    for category, category_labels in labels_to_set.items():
        print(f"  📂 {category.upper()}:")
        for label, description in category_labels.items():
            print(f"    🏷️ {label}: {description}")
    
    print("\n🔄 FLOW LOGIC")
    print("-" * 15)
    
    print("""
1. USER CONFIRMS PREFILL:
   - Set contact attributes with extracted info
   - Set conversation attributes for current flow
   - Detect and set customer segment
   - Set appropriate audience and subject labels
   
2. SEGMENT DETECTION:
   - weekend_whitelisted → "weekend"
   - returning_broadcast → "returning_broadcast" 
   - has_paid_lesson OR has_completed_intake OR trial_lesson_completed → "existing"
   - Default → "new"
   
3. PLANNING PROFILE:
   - Use detected segment for planning profile
   - Affects available time slots and pricing
   
4. LABELS:
   - Set audience label based on school_level
   - Set subject label based on topic_primary/topic_secondary
   - Set service_trial for trial lesson requests
   - Set source_whatsapp for WhatsApp conversations
""")

def show_current_implementation():
    """Show what's currently implemented in main.py"""
    
    print("\n🔧 CURRENT IMPLEMENTATION IN MAIN.PY")
    print("=" * 40)
    
    print("""
📍 handle_prefill_confirmation() function:

✅ WHAT'S ALREADY IMPLEMENTED:
- Extracts prefilled info from conversation attributes
- Applies info to contact attributes
- Creates child contact if needed
- Sets use_prefill flag
- Shows prefill action menu

❌ WHAT'S MISSING:
- Segment detection and setting
- Label setting based on school_level and topics
- Planning profile setting
- Customer status tracking (customer_since, has_completed_intake, etc.)

🔧 NEEDED UPDATES:
1. Call detect_segment() after setting contact attributes
2. Set appropriate labels based on extracted information
3. Set planning_profile based on detected segment
4. Set customer status attributes
5. Add proper error handling for attribute/label setting
""")

def generate_implementation_code():
    """Generate the code that should be added to main.py"""
    
    print("\n💻 IMPLEMENTATION CODE TO ADD")
    print("=" * 30)
    
    code = '''
# After setting contact attributes in handle_prefill_confirmation():

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
'''
    
    print(code)

def main():
    """Main function"""
    print("🚀 Prefill Confirmation Attributes & Labels Analysis")
    print("=" * 55)
    
    analyze_prefill_confirmation_flow()
    show_current_implementation()
    generate_implementation_code()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Add the generated code to handle_prefill_confirmation()")
    print("2. Test the flow with different types of prefill information")
    print("3. Verify that attributes and labels are set correctly")
    print("4. Update documentation if needed")

if __name__ == "__main__":
    main()
