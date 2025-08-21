#!/usr/bin/env python3
"""
Simple Google Workspace Setup for lessons@stephensprivelessen.nl

This script helps you set up email sending using your existing
lessons@stephensprivelessen.nl account without needing a service account.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_simple_setup():
    """Print simple setup instructions"""
    print("🚀 Eenvoudige Google Workspace Setup voor lessons@stephensprivelessen.nl")
    print("=" * 70)
    print()
    
    print("📋 Wat je al hebt:")
    print("-" * 40)
    print("✅ lessons@stephensprivelessen.nl Google Workspace account")
    print("✅ Toegang tot Gmail en Google Calendar")
    print("✅ Mogelijkheid om emails te versturen")
    print()
    
    print("📋 Wat je nog nodig hebt voor email:")
    print("-" * 40)
    print("1. Ga naar https://myaccount.google.com/security")
    print("2. Log in met lessons@stephensprivelessen.nl")
    print("3. Ga naar '2-Step Verification' en enable het")
    print("4. Ga naar 'App passwords'")
    print("5. Klik op 'Select app' > 'Other (Custom name)'")
    print("6. Vul in: 'TutorBot'")
    print("7. Klik op 'Generate'")
    print("8. Kopieer het gegenereerde wachtwoord")
    print()
    
    print("📋 Environment Variables:")
    print("-" * 40)
    print("Voeg toe aan je .env bestand:")
    print()
    print("# Gmail SMTP (voor email versturen)")
    print("GMAIL_USER=lessons@stephensprivelessen.nl")
    print("GMAIL_APP_PASSWORD=YOUR_APP_PASSWORD_HERE")
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print()
    
    print("📋 Voor Calendar (optioneel):")
    print("-" * 40)
    print("Als je automatische calendar integratie wilt:")
    print("1. Volg de volledige setup in setup_google_workspace.py")
    print("2. Maak een service account aan in Google Cloud Console")
    print("3. Download het JSON key bestand")
    print("4. Voeg calendar permissions toe")
    print()
    
    print("📋 Test je setup:")
    print("-" * 40)
    print("1. Update je .env bestand")
    print("2. Run: python3 test_email_integration.py")
    print("3. Check of je test email ontvangt")
    print()

def check_current_email_config():
    """Check current email configuration"""
    print("🔍 Huidige Email Configuratie:")
    print("-" * 40)
    
    config_vars = {
        "GMAIL_USER": "Gmail User",
        "GMAIL_APP_PASSWORD": "Gmail App Password", 
        "SMTP_SERVER": "SMTP Server",
        "SMTP_PORT": "SMTP Port"
    }
    
    all_configured = True
    
    for var, description in config_vars.items():
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var:
                print(f"✅ {description}: {'*' * len(value)}")
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: Niet ingesteld")
            all_configured = False
    
    return all_configured

def main():
    """Main function"""
    print_simple_setup()
    check_current_email_config()
    
    print("📝 Volgende Stappen:")
    print("1. Setup Gmail App Password")
    print("2. Update .env bestand")
    print("3. Test email functionaliteit")
    print("4. (Optioneel) Setup calendar integratie")
    print()
    
    print("❓ Heb je hulp nodig?")
    print("- Check de Gmail security instellingen")
    print("- Verifieer de SMTP instellingen")
    print("- Test met test_email_integration.py")

if __name__ == "__main__":
    main()
