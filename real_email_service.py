#!/usr/bin/env python3
"""
Real Email Service for TutorBot

This service sends real emails using the Google Workspace SMTP settings
for lessons@stephensprivelessen.nl
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RealEmailService:
    """Real email service using Google Workspace SMTP"""
    
    def __init__(self):
        # Use the same SMTP settings as existing Google Workspace
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.from_email = "lessons@stephensprivelessen.nl"
        
        # Get credentials from environment
        self.gmail_user = os.getenv("GMAIL_USER", "lessons@stephensprivelessen.nl")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not self.gmail_password:
            print("⚠️ GMAIL_APP_PASSWORD not set - using temp email service")
            self.use_temp_service = True
        else:
            self.use_temp_service = False
    
    def send_email(self, to_email, subject, body, from_name="Stephen's Privélessen"):
        """
        Send a real email using Google Workspace SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            from_name: Sender name
        """
        if self.use_temp_service:
            # Fallback to temp service if credentials not configured
            from temp_email_service import TempEmailService
            temp_service = TempEmailService()
            return temp_service.send_email(to_email, subject, body, from_name)
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            print(f"✅ Email sent successfully:")
            print(f"   From: {from_name} <{self.from_email}>")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            # Fallback to temp service
            from temp_email_service import TempEmailService
            temp_service = TempEmailService()
            return temp_service.send_email(to_email, subject, body, from_name)
    
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
lessons@stephensprivelessen.nl
        """
        
        return self.send_email(to_email, subject, body, "Stephen's Privélessen")
    
    def send_payment_request(self, to_email, student_name, amount, payment_link):
        """Send payment request email"""
        subject = "Betaalverzoek - Stephen's Privélessen"
        body = f"""
Beste {student_name},

Hier is je betaalverzoek voor de les bij Stephen's Privélessen.

💰 **Betaling Details:**
   Bedrag: €{amount}
   Betaallink: {payment_link}

💳 **Betaalmethoden:**
   - iDEAL
   - Credit Card
   - PayPal

📅 **Vervolgstap:**
   Na betaling ontvang je een bevestiging en kunnen we de les inplannen.

Met vriendelijke groet,
Stephen's Privélessen
lessons@stephensprivelessen.nl
        """
        
        return self.send_email(to_email, subject, body, "Stephen's Privélessen")
    
    def send_lesson_reminder(self, to_email, student_name, lesson_date, lesson_time):
        """Send lesson reminder email"""
        subject = "Herinnering - Les vanmorgen - Stephen's Privélessen"
        body = f"""
Beste {student_name},

Dit is een herinnering voor je les vanmorgen.

📅 **Les Details:**
   Datum: {lesson_date}
   Tijd: {lesson_time}
   Duur: 1 uur

📍 **Online Les:**
   Link: [Wordt 15 minuten voor de les gedeeld]
   Platform: Zoom/Google Meet

📋 **Voorbereiding:**
   - Zorg dat je laptop/computer werkt
   - Test je camera en microfoon
   - Heb pen en papier klaar

Tot straks!

Met vriendelijke groet,
Stephen's Privélessen
lessons@stephensprivelessen.nl
        """
        
        return self.send_email(to_email, subject, body, "Stephen's Privélessen")

# Test function
def test_email_service():
    """Test the email service"""
    print("🧪 Testing Real Email Service...")
    
    service = RealEmailService()
    
    # Test email
    result = service.send_email(
        to_email="test@example.com",
        subject="Test Email - TutorBot",
        body="Dit is een test email van TutorBot.",
        from_name="TutorBot Test"
    )
    
    if result:
        print("✅ Email service test successful!")
    else:
        print("❌ Email service test failed!")
    
    return result

if __name__ == "__main__":
    test_email_service()
