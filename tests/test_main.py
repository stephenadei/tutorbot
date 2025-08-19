#!/usr/bin/env python3
"""
Comprehensive test suite for TutorBot main.py functionality
"""

import os
import sys
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main application
from main import (
    t, send_text_with_duplicate_check, assign_conversation, 
    send_handoff_message, send_handoff_menu, send_admin_warning,
    analyze_first_message_with_openai, map_school_level, 
    detect_language_from_message, map_topic, 
    is_prefill_sufficient_for_trial_lesson, create_child_contact,
    prefill_intake_from_message, get_contact_id_from_conversation,
    send_input_select_only,
    detect_segment, suggest_slots, book_slot, create_payment_link,
    verify_stripe_webhook, verify_webhook, handle_conversation_created,
    handle_message_created, show_info_menu, handle_prefill_confirmation,
    handle_info_menu_selection, show_detailed_info_menu,
    handle_handoff_menu_selection, show_segment_menu, handle_menu_selection,
    is_existing_customer, has_completed_intake, start_planning_flow,
    start_intake_flow, handle_intake_step, suggest_available_slots,
    handle_planning_selection, handle_email_request, create_payment_request,
    handle_payment_success, PLANNING_PROFILES
)

# Mock the cw_api module
sys.modules['cw_api'] = Mock()

class TestTranslation(unittest.TestCase):
    """Test the translation function"""
    
    def test_basic_translation(self):
        """Test basic translation functionality"""
        # Test Dutch translation
        result = t("greeting_with_name", "nl", name="John")
        self.assertEqual(result, "Hallo John! 👋")
        
        # Test English translation
        result = t("greeting_with_name", "en", name="John")
        self.assertEqual(result, "Hello John! 👋")
    
    def test_missing_translation(self):
        """Test handling of missing translations"""
        result = t("nonexistent_key", "nl")
        self.assertEqual(result, "nonexistent_key")
    
    def test_formatting_with_kwargs(self):
        """Test translation with keyword arguments"""
        result = t("planning_confirm", "nl", slot="Maandag 14:00")
        self.assertEqual(result, "Gekozen: Maandag 14:00. Ik zet 'm voorlopig vast.")
    
    def test_language_fallback(self):
        """Test language fallback behavior"""
        # Test with unsupported language
        result = t("greeting_with_name", "fr", name="John")
        self.assertEqual(result, "greeting_with_name")

class TestMessageHandling(unittest.TestCase):
    """Test message sending and handling functions"""
    
    @patch('main.get_conv_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.send_text')
    def test_send_text_with_duplicate_check(self, mock_send_text, mock_set_conv_attrs, mock_get_conv_attrs):
        """Test duplicate message detection"""
        # Mock conversation attributes
        mock_get_conv_attrs.return_value = {"last_bot_message": "Previous message"}
        mock_send_text.return_value = True
        
        # Test duplicate message
        result = send_text_with_duplicate_check(123, "Previous message")
        self.assertFalse(result)
        
        # Test new message
        result = send_text_with_duplicate_check(123, "New message")
        self.assertTrue(result)
        mock_send_text.assert_called_with(123, "New message")
    
    @patch('main.requests.post')
    def test_assign_conversation(self, mock_post):
        """Test conversation assignment"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        assign_conversation(123, 456)
        mock_post.assert_called_once()
    
    @patch('main.requests.post')
    @patch('main.add_conv_labels')
    @patch('main.set_conv_attrs')
    @patch('main.assign_conversation')
    def test_send_handoff_message(self, mock_assign, mock_set_attrs, mock_add_labels, mock_post):
        """Test handoff message sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_handoff_message(123, "Handoff message")
        self.assertTrue(result)
        mock_assign.assert_called_with(123, 2)

class TestOpenAIIntegration(unittest.TestCase):
    """Test OpenAI integration functions"""
    
    @patch('main.openai')
    def test_analyze_first_message_with_openai(self, mock_openai):
        """Test OpenAI message analysis"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"learner_name": "John", "school_level": "vwo"}'
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response
        
        result = analyze_first_message_with_openai("Hallo, ik ben John en zit in 6V", 123)
        self.assertEqual(result["learner_name"], "John")
        self.assertEqual(result["school_level"], "vwo")
    
    def test_map_school_level(self):
        """Test school level mapping"""
        self.assertEqual(map_school_level("6V"), "vwo")
        self.assertEqual(map_school_level("HAVO"), "havo")
        self.assertEqual(map_school_level("MBO"), "mbo")
        self.assertEqual(map_school_level("unknown"), "adult")
    
    def test_detect_language_from_message(self):
        """Test language detection"""
        # Test Dutch detection
        dutch_message = "Ik heb moeite met wiskunde en wil graag hulp"
        self.assertEqual(detect_language_from_message(dutch_message), "nl")
        
        # Test English detection
        english_message = "I have trouble with mathematics and would like help"
        self.assertEqual(detect_language_from_message(english_message), "en")
    
    def test_map_topic(self):
        """Test topic mapping"""
        self.assertEqual(map_topic("wiskunde"), "math")
        self.assertEqual(map_topic("statistiek"), "stats")
        self.assertEqual(map_topic("engels"), "english")
        self.assertEqual(map_topic("unknown"), "other")

class TestPrefillFunctionality(unittest.TestCase):
    """Test prefill and intake functionality"""
    
    def test_is_prefill_sufficient_for_trial_lesson(self):
        """Test prefill sufficiency check"""
        # Test sufficient information
        sufficient_info = {
            "learner_name": "John Doe",
            "school_level": "vwo",
            "topic_secondary": "wiskunde B"
        }
        self.assertTrue(is_prefill_sufficient_for_trial_lesson(sufficient_info))
        
        # Test insufficient information
        insufficient_info = {
            "learner_name": "John Doe"
        }
        self.assertFalse(is_prefill_sufficient_for_trial_lesson(insufficient_info))
    
    @patch('main.get_contact_id_from_conversation')
    @patch('main.ChatwootAPI')
    def test_create_child_contact(self, mock_chatwoot_api, mock_get_contact_id):
        """Test child contact creation"""
        mock_get_contact_id.return_value = 456
        mock_chatwoot_api.create_contact.return_value = {"id": 789}
        
        analysis = {"learner_name": "Child Name"}
        result = create_child_contact(analysis, 123)
        self.assertEqual(result, 789)
    
    @patch('main.analyze_first_message_with_openai')
    def test_prefill_intake_from_message(self, mock_analyze):
        """Test intake prefill from message"""
        mock_analyze.return_value = {
            "learner_name": "John",
            "school_level": "vwo",
            "topic_secondary": "wiskunde B",
            "for_who": "self"
        }
        
        result = prefill_intake_from_message("Test message", 123)
        self.assertEqual(result["learner_name"], "John")
        self.assertEqual(result["school_level"], "vwo")

class TestSegmentDetection(unittest.TestCase):
    """Test segment detection functionality"""
    
    @patch('main.get_contact_attrs')
    @patch('main.set_contact_attrs')
    def test_detect_segment(self, mock_set_attrs, mock_get_attrs):
        """Test segment detection logic"""
        # Test new customer
        mock_get_attrs.return_value = {}
        result = detect_segment(123)
        self.assertEqual(result, "new")
        
        # Test existing customer
        mock_get_attrs.return_value = {"has_paid_lesson": True}
        result = detect_segment(123)
        self.assertEqual(result, "existing")
        
        # Test weekend segment
        mock_get_attrs.return_value = {"weekend_whitelisted": True}
        result = detect_segment(123)
        self.assertEqual(result, "weekend")

class TestPlanningFunctionality(unittest.TestCase):
    """Test planning and slot suggestion functionality"""
    
    def test_planning_profiles(self):
        """Test planning profiles configuration"""
        self.assertIn("new", PLANNING_PROFILES)
        self.assertIn("existing", PLANNING_PROFILES)
        self.assertIn("weekend", PLANNING_PROFILES)
        
        # Test profile structure
        new_profile = PLANNING_PROFILES["new"]
        self.assertIn("duration_minutes", new_profile)
        self.assertIn("earliest_hour", new_profile)
        self.assertIn("latest_hour", new_profile)
    
    @patch('main.get_conv_attrs')
    def test_suggest_slots(self, mock_get_conv_attrs):
        """Test slot suggestion"""
        mock_get_conv_attrs.return_value = {"preferred_times": "maandag 19:00"}
        
        slots = suggest_slots(123, "new")
        self.assertIsInstance(slots, list)
        # Should return slots for the next 14 days
        self.assertLessEqual(len(slots), 8)  # Limited to 8 slots
    
    @patch('main.datetime')
    def test_book_slot(self, mock_datetime):
        """Test slot booking"""
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0)
        
        result = book_slot(123, "2024-01-02T14:00:00+02:00", "2024-01-02T15:00:00+02:00", "Test", "Description")
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)

class TestPaymentFunctionality(unittest.TestCase):
    """Test payment and webhook functionality"""
    
    def test_create_payment_link(self):
        """Test payment link creation"""
        result = create_payment_link("new", 60, "TEST-123", 456, "John", "1on1", "vwo", "none")
        self.assertIsInstance(result, str)
        self.assertIn("stripe.com", result)
    
    def test_verify_stripe_webhook(self):
        """Test Stripe webhook verification"""
        # Test with no secret (should return True)
        result = verify_stripe_webhook(b"test", "signature")
        self.assertTrue(result)
    
    def test_verify_webhook(self):
        """Test Chatwoot webhook verification"""
        # Test with no secret (should return True)
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.get_data.return_value = b"test"
        
        result = verify_webhook(mock_request)
        self.assertTrue(result)

class TestIntakeFlow(unittest.TestCase):
    """Test intake flow functionality"""
    
    @patch('main.get_contact_attrs')
    @patch('main.set_contact_attrs')
    @patch('main.get_conv_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.send_text_with_duplicate_check')
    def test_start_intake_flow(self, mock_send_text, mock_set_conv, mock_get_conv, mock_set_contact, mock_get_contact):
        """Test intake flow start"""
        mock_get_contact.return_value = {}
        mock_get_conv.return_value = {}
        
        start_intake_flow(123, 456, "nl")
        
        # Should set pending intent and send first question
        mock_set_conv.assert_called()
        mock_send_text.assert_called()
    
    @patch('main.get_conv_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.set_contact_attrs')
    @patch('main.send_text_with_duplicate_check')
    def test_handle_intake_step(self, mock_send_text, mock_set_contact, mock_set_conv, mock_get_conv):
        """Test intake step handling"""
        # Test for_who step
        mock_get_conv.return_value = {"pending_intent": "intake", "intake_step": "for_who"}
        
        handle_intake_step(123, 456, "self", "nl")
        
        mock_set_conv.assert_called()
        mock_send_text.assert_called()

class TestMenuHandling(unittest.TestCase):
    """Test menu and selection handling"""
    
    @patch('main.set_conv_attrs')
    @patch('main.send_text_with_duplicate_check')
    def test_show_info_menu(self, mock_send_text, mock_set_conv):
        """Test info menu display"""
        show_info_menu(123, "nl")
        
        mock_set_conv.assert_called_with(123, {"pending_intent": "info_menu"})
        mock_send_text.assert_called()
    
    @patch('main.get_conv_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.send_text_with_duplicate_check')
    @patch('main.start_planning_flow')
    def test_handle_menu_selection(self, mock_start_planning, mock_send_text, mock_set_conv, mock_get_conv):
        """Test menu selection handling"""
        mock_get_conv.return_value = {}
        
        # Test lesson planning selection
        handle_menu_selection(123, 456, "plan_lesson", "nl")
        
        mock_start_planning.assert_called_with(123, 456, "nl")

class TestWebhookHandling(unittest.TestCase):
    """Test webhook handling functionality"""
    
    @patch('main.set_conv_attrs')
    @patch('main.set_contact_attrs')
    @patch('main.detect_segment')
    @patch('main.show_segment_menu')
    def test_handle_conversation_created(self, mock_show_menu, mock_detect_segment, mock_set_contact, mock_set_conv):
        """Test conversation creation handling"""
        data = {
            "conversation": {"id": 123},
            "contact": {"id": 456}
        }
        
        mock_detect_segment.return_value = "new"
        
        handle_conversation_created(data)
        
        mock_set_conv.assert_called()
        mock_set_contact.assert_called()
        mock_detect_segment.assert_called_with(456)
    
    @patch('main.get_conv_attrs')
    @patch('main.get_contact_attrs')
    @patch('main.detect_segment')
    @patch('main.set_contact_attrs')
    @patch('main.handle_intake_step')
    @patch('main.handle_planning_selection')
    @patch('main.handle_prefill_confirmation')
    @patch('main.handle_info_menu_selection')
    @patch('main.handle_menu_selection')
    def test_handle_message_created(self, mock_handle_menu, mock_handle_info, mock_handle_prefill, 
                                  mock_handle_planning, mock_handle_intake, mock_set_contact, 
                                  mock_detect_segment, mock_get_contact, mock_get_conv):
        """Test message creation handling"""
        data = {
            "conversation": {"id": 123},
            "sender": {"id": 456},
            "content": "Test message",
            "event": "message_created",
            "message_type": "incoming"
        }
        
        mock_get_conv.return_value = {"pending_intent": "intake"}
        mock_get_contact.return_value = {"language": "nl"}
        mock_detect_segment.return_value = "new"
        
        handle_message_created(data)
        
        mock_handle_intake.assert_called()

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_is_existing_customer(self):
        """Test existing customer detection"""
        # Test existing customer
        contact_attrs = {"is_student": True, "has_paid_lesson": True}
        self.assertTrue(is_existing_customer(contact_attrs))
        
        # Test new customer
        contact_attrs = {}
        self.assertFalse(is_existing_customer(contact_attrs))
    
    def test_has_completed_intake(self):
        """Test intake completion check"""
        # Test completed intake
        conv_attrs = {"intake_completed": True}
        self.assertTrue(has_completed_intake(conv_attrs))
        
        # Test incomplete intake
        conv_attrs = {}
        self.assertFalse(has_completed_intake(conv_attrs))

class TestEmailAndPaymentHandling(unittest.TestCase):
    """Test email and payment handling"""
    
    @patch('main.set_contact_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.send_text_with_duplicate_check')
    def test_handle_email_request_valid(self, mock_send_text, mock_set_conv, mock_set_contact):
        """Test valid email handling"""
        handle_email_request(123, 456, "test@example.com", "nl")
        
        mock_set_contact.assert_called()
        mock_set_conv.assert_called()
        mock_send_text.assert_called()
    
    @patch('main.send_text_with_duplicate_check')
    def test_handle_email_request_invalid(self, mock_send_text):
        """Test invalid email handling"""
        handle_email_request(123, 456, "invalid-email", "nl")
        
        mock_send_text.assert_called()
    
    @patch('main.set_conv_attrs')
    @patch('main.add_conv_labels')
    @patch('main.send_text_with_duplicate_check')
    def test_create_payment_request(self, mock_send_text, mock_add_labels, mock_set_conv):
        """Test payment request creation"""
        create_payment_request(123, 456, "nl")
        
        mock_set_conv.assert_called()
        mock_add_labels.assert_called()
        mock_send_text.assert_called()

class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and end-to-end flows"""
    
    @patch('main.get_contact_attrs')
    @patch('main.get_conv_attrs')
    @patch('main.set_contact_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.send_text_with_duplicate_check')
    @patch('main.detect_segment')
    def test_new_customer_flow(self, mock_detect_segment, mock_send_text, mock_set_conv, 
                              mock_set_contact, mock_get_conv, mock_get_contact):
        """Test new customer flow"""
        mock_get_contact.return_value = {"language": "nl"}
        mock_get_conv.return_value = {}
        mock_detect_segment.return_value = "new"
        
        # Test segment menu for new customer
        show_segment_menu(123, 456, "new", "nl")
        
        mock_send_text.assert_called()
    
    @patch('main.get_contact_attrs')
    @patch('main.get_conv_attrs')
    @patch('main.set_contact_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.send_text_with_duplicate_check')
    @patch('main.suggest_available_slots')
    def test_existing_customer_flow(self, mock_suggest_slots, mock_send_text, mock_set_conv,
                                   mock_set_contact, mock_get_conv, mock_get_contact):
        """Test existing customer flow"""
        mock_get_contact.return_value = {"language": "nl", "has_paid_lesson": True}
        mock_get_conv.return_value = {}
        
        # Test planning flow for existing customer
        start_planning_flow(123, 456, "nl")
        
        mock_send_text.assert_called()
        mock_suggest_slots.assert_called()

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    @patch('main.get_conv_attrs')
    @patch('main.set_conv_attrs')
    @patch('main.send_handoff_message')
    def test_duplicate_message_handling(self, mock_handoff, mock_set_conv, mock_get_conv):
        """Test duplicate message handling"""
        mock_get_conv.return_value = {"last_bot_message": "Same message"}
        
        # This should trigger handoff
        send_text_with_duplicate_check(123, "Same message")
        
        mock_handoff.assert_called()
    
    @patch('main.requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Test that errors are handled gracefully
        result = assign_conversation(123, 456)
        # Should not raise an exception

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestTranslation,
        TestMessageHandling,
        TestOpenAIIntegration,
        TestPrefillFunctionality,
        TestSegmentDetection,
        TestPlanningFunctionality,
        TestPaymentFunctionality,
        TestIntakeFlow,
        TestMenuHandling,
        TestWebhookHandling,
        TestUtilityFunctions,
        TestEmailAndPaymentHandling,
        TestIntegrationScenarios,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Exit with appropriate code
    sys.exit(len(result.failures) + len(result.errors)) 