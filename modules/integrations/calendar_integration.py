#!/usr/bin/env python3
"""
Calendar Integration for TutorBot

This module contains calendar integration functions for slot suggestion and booking.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import dependencies
from modules.utils.cw_api import get_conv_attrs, get_contact_attrs
from modules.core.config import TZ, PLANNING_PROFILES


def suggest_slots(conversation_id, profile_name):
    """Suggest available slots based on real calendar availability"""
    try:
        from calendar_integration import get_available_slots
        
        # Get user preferences from conversation attributes
        conv_attrs = get_conv_attrs(conversation_id)
        preferred_times = conv_attrs.get("preferred_times", "").lower()
        lesson_type = conv_attrs.get("lesson_type", "trial")
        
        # Parse preferred times into list
        preferred_time_list = []
        if preferred_times:
            # Extract specific times mentioned
            import re
            time_pattern = r'\b(\d{1,2}):?(\d{2})?\b'
            times = re.findall(time_pattern, preferred_times)
            for hour, minute in times:
                if minute:
                    preferred_time_list.append(f"{hour.zfill(2)}:{minute}")
                else:
                    preferred_time_list.append(f"{hour.zfill(2)}:00")
            
            # Add general time preferences
            if "avond" in preferred_times or "evening" in preferred_times:
                preferred_time_list.extend(["17:00", "18:00", "19:00"])
            if "middag" in preferred_times or "afternoon" in preferred_times:
                preferred_time_list.extend(["14:00", "15:00", "16:00"])
            if "ochtend" in preferred_times or "morning" in preferred_times:
                preferred_time_list.extend(["09:00", "10:00", "11:00"])
        
        # Get date range
        now = datetime.now(TZ)
        start_date = now + timedelta(days=1)  # Start from tomorrow
        end_date = now + timedelta(days=14)   # Look ahead 2 weeks
        
        # Get available slots from calendar
        available_slots = get_available_slots(
            start_date=start_date,
            end_date=end_date,
            preferred_times=preferred_time_list if preferred_time_list else None,
            lesson_type=lesson_type
        )
        
        # Convert to expected format
        slots = []
        for slot in available_slots:
            slots.append({
                "start": slot["start_iso"],
                "end": slot["end_iso"],
                "label": slot["label"]
            })
        
        # Return appropriate number of slots
        if profile_name == "premium":
            return slots[:15]  # More options for premium
        else:
            return slots[:6]   # Standard number for others
            
    except Exception as e:
        print(f"❌ Error getting calendar slots: {e}")
        # Fallback to mock implementation
        return suggest_slots_mock(conversation_id, profile_name)


def suggest_slots_mock(conversation_id, profile_name):
    """Fallback mock implementation"""
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
                
                # Adjust duration based on lesson type
                if lesson_type == "trial":
                    duration_minutes = 30  # Trial lessons are 30 minutes
                else:
                    duration_minutes = profile["duration_minutes"]  # Use profile duration for other lessons
                
                end_time = start_time + timedelta(minutes=duration_minutes)
                
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
        return slots[:15]  # More options for premium
    else:
        return slots[:6]  # Standard number for others


def book_slot(conversation_id, start_time, end_time, title, description):
    """Book a slot in Google Calendar and send to dashboard"""
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
        
        # Send lesson to dashboard
        try:
            from dashboard_integration import create_lesson_data, send_lesson_to_dashboard
            
            # Get conversation and contact data
            conv_attrs = get_conv_attrs(conversation_id)
            contact_id = conv_attrs.get("contact_id")
            contact_attrs = get_contact_attrs(contact_id) if contact_id else {}
            
            # Create lesson data
            lesson_data = create_lesson_data(
                student_name=conv_attrs.get("learner_name", "Unknown Student"),
                student_email=contact_attrs.get("email", ""),
                start_time=start_time,
                end_time=end_time,
                lesson_type=conv_attrs.get("lesson_type", "regular"),
                chatwoot_contact_id=contact_id,
                chatwoot_conversation_id=str(conversation_id),
                notes=description,
                location="Online",
                program=conv_attrs.get("program"),
                topic_primary=conv_attrs.get("topic_primary"),
                topic_secondary=conv_attrs.get("topic_secondary"),
                toolset=conv_attrs.get("toolset"),
                lesson_mode="ONLINE",
                is_adult=conv_attrs.get("is_adult", False),
                relationship_to_learner=conv_attrs.get("relationship_to_learner")
            )
            
            # Send to dashboard
            dashboard_success = send_lesson_to_dashboard(lesson_data)
            if dashboard_success:
                print(f"✅ Lesson sent to dashboard successfully")
            else:
                print(f"⚠️ Failed to send lesson to dashboard")
                
        except Exception as e:
            print(f"⚠️ Error sending to dashboard: {e}")
        
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
