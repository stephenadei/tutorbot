#!/usr/bin/env python3
"""
Temporary Email Service

This is a temporary email service that simulates email sending
for testing purposes. It logs emails instead of actually sending them.
"""

import os
from datetime import datetime

class TempEmailService:
    """Temporary email service for testing"""
    
    def __init__(self):
        self.from_email = "lessen@stephensprivelessen.nl"
        self.log_file = "email_log.txt"
    
    def send_email(self, to_email, subject, body, from_name="TutorBot"):
        """
        Simulate sending an email by logging it
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            from_name: Sender name
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create email log entry
        log_entry = f"""
=== EMAIL LOG ENTRY ===
Timestamp: {timestamp}
From: {from_name} <{self.from_email}>
To: {to_email}
Subject: {subject}
Body:
{body}
=== END EMAIL ===

"""
        
        # Write to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
            
            print(f"✅ Email logged successfully:")
            print(f"   From: {from_name} <{self.from_email}>")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Logged to: {self.log_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to log email: {e}")
            return False
    
    def send_trial_confirmation(self, to_email, student_name, lesson_date, lesson_time):
        """Send trial lesson confirmation email"""
        subject = "Bevestiging Proefles - Stephen's Privélessen"
        body = f"""
Beste {student_name},

Bedankt voor je aanmelding voor een proefles bij Stephen's Privélessen!

📅 **Proefles Details:**
   Datum: {lesson_date}
   Tijd: {lesson_time}
   Duur: 1 uur
   Kosten: Gratis

📍 **Locatie:**
   Online via Zoom/Google Meet
   (Link wordt 15 minuten voor de les gedeeld)

📋 **Wat neem je mee:**
   - Laptop/computer met camera en microfoon
   - Pen en papier voor aantekeningen
   - Eventuele vragen over de stof

📞 **Contact:**
   Bij vragen kun je contact opnemen via WhatsApp of email.

We kijken ernaar uit om je te ontmoeten!

Met vriendelijke groet,
Stephen's Privélessen
lessen@stephensprivelessen.nl
        """
        
        return self.send_email(to_email, subject, body, "Stephen's Privélessen")
    
    def send_payment_request(self, to_email, student_name, amount, payment_link):
        """Send payment request email"""
        subject = "Betaalverzoek - Stephen's Privélessen"
        body = f"""
Beste {student_name},

Hier is je betaalverzoek voor de bijles bij Stephen's Privélessen.

💰 **Betaling Details:**
   Bedrag: €{amount}
   Betaallink: {payment_link}

📋 **Instructies:**
   1. Klik op de betaallink hierboven
   2. Vul je betalingsgegevens in
   3. Bevestig de betaling

Na ontvangst van de betaling wordt je les bevestigd.

📞 **Vragen?**
   Neem contact op via WhatsApp of email.

Met vriendelijke groet,
Stephen's Privélessen
testvan@stephenadei.nl
        """
        
        return self.send_email(to_email, subject, body, "Stephen's Privélessen")
    
    def send_lesson_reminder(self, to_email, student_name, lesson_date, lesson_time):
        """Send lesson reminder email"""
        subject = "Herinnering Proefles - Stephen's Privélessen"
        body = f"""
Beste {student_name},

Dit is een herinnering voor je proefles morgen!

📅 **Proefles Details:**
   Datum: {lesson_date}
   Tijd: {lesson_time}
   Duur: 1 uur

🔗 **Zoom Link:**
   De Zoom link wordt 15 minuten voor de les gedeeld via WhatsApp.

📋 **Voorbereiding:**
   - Zorg dat je laptop/computer werkt
   - Test je camera en microfoon
   - Heb pen en papier klaar

Tot morgen!

Met vriendelijke groet,
Stephen's Privélessen
testvan@stephenadei.nl
        """
        
        return self.send_email(to_email, subject, body, "Stephen's Privélessen")

def test_temp_email_service():
    """Test the temporary email service"""
    print("🧪 Testing Temporary Email Service...")
    
    email_service = TempEmailService()
    
    # Test trial confirmation
    print("\n📧 Testing trial confirmation email...")
    success1 = email_service.send_trial_confirmation(
        "testnaar@stephenadei.nl",
        "Juul",
        "Maandag 25 augustus",
        "14:00"
    )
    
    # Test payment request
    print("\n💰 Testing payment request email...")
    success2 = email_service.send_payment_request(
        "testnaar@stephenadei.nl",
        "Juul",
        "120",
        "https://payment.example.com/123"
    )
    
    # Test lesson reminder
    print("\n⏰ Testing lesson reminder email...")
    success3 = email_service.send_lesson_reminder(
        "testnaar@stephenadei.nl",
        "Juul",
        "Maandag 25 augustus",
        "14:00"
    )
    
    print(f"\n📊 Test Results:")
    print(f"   Trial confirmation: {'✅' if success1 else '❌'}")
    print(f"   Payment request: {'✅' if success2 else '❌'}")
    print(f"   Lesson reminder: {'✅' if success3 else '❌'}")
    
    print(f"\n📝 Check the email log: {email_service.log_file}")

if __name__ == "__main__":
    test_temp_email_service()
