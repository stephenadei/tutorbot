#!/usr/bin/env python3
"""
Google Workspace Setup for lessons@stephensprivelessen.nl

This script helps you set up Google Calendar and Gmail integration
for the lessons@stephensprivelessen.nl account.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_setup_instructions():
    """Print setup instructions for Google Workspace"""
    print("🚀 Google Workspace Setup voor lessons@stephensprivelessen.nl")
    print("=" * 70)
    print()
    
    print("📋 STAP 1: Google Cloud Project Setup")
    print("-" * 40)
    print("1. Ga naar https://console.cloud.google.com")
    print("2. Maak een nieuw project aan of selecteer een bestaand project")
    print("3. Enable de Google Calendar API:")
    print("   - Ga naar 'APIs & Services' > 'Library'")
    print("   - Zoek naar 'Google Calendar API'")
    print("   - Klik op 'Enable'")
    print()
    
    print("📋 STAP 2: Service Account Aanmaken")
    print("-" * 40)
    print("1. Ga naar 'APIs & Services' > 'Credentials'")
    print("2. Klik op '+ CREATE CREDENTIALS' > 'Service Account'")
    print("3. Vul in:")
    print("   - Service account name: 'tutorbot-calendar'")
    print("   - Service account ID: 'tutorbot-calendar'")
    print("   - Description: 'Service account for TutorBot calendar integration'")
    print("4. Klik op 'CREATE AND CONTINUE'")
    print("5. Skip de optionele stappen en klik op 'DONE'")
    print()
    
    print("📋 STAP 3: Service Account Key Downloaden")
    print("-" * 40)
    print("1. Klik op de service account die je net hebt aangemaakt")
    print("2. Ga naar het 'KEYS' tabblad")
    print("3. Klik op 'ADD KEY' > 'Create new key'")
    print("4. Selecteer 'JSON' en klik op 'CREATE'")
    print("5. Download het JSON bestand")
    print("6. Hernoem het naar 'gcal-service-account.json'")
    print("7. Plaats het in de 'config/' directory")
    print()
    
    print("📋 STAP 4: Calendar Permissions")
    print("-" * 40)
    print("1. Open het gedownloade JSON bestand")
    print("2. Kopieer de 'client_email' waarde")
    print("3. Ga naar https://calendar.google.com")
    print("4. Log in met lessons@stephensprivelessen.nl")
    print("5. Ga naar Settings > 'Settings for my calendars'")
    print("6. Klik op 'Share with specific people'")
    print("7. Voeg de service account email toe met 'Make changes to events' rechten")
    print()
    
    print("📋 STAP 5: Gmail SMTP Setup")
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
    
    print("📋 STAP 6: Environment Variables")
    print("-" * 40)
    print("Voeg de volgende variabelen toe aan je .env bestand:")
    print()
    print("# Google Calendar")
    print("GCAL_SERVICE_ACCOUNT_JSON=/app/config/gcal-service-account.json")
    print("GCAL_CALENDAR_ID=lessons@stephensprivelessen.nl")
    print()
    print("# Gmail SMTP")
    print("GMAIL_USER=lessons@stephensprivelessen.nl")
    print("GMAIL_APP_PASSWORD=YOUR_APP_PASSWORD_HERE")
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print()

def check_current_status():
    """Check current configuration status"""
    print("🔍 Huidige Configuratie Status:")
    print("-" * 40)
    
    # Check service account file
    service_account_path = os.getenv("GCAL_SERVICE_ACCOUNT_JSON", "/app/config/gcal-service-account.json")
    if os.path.exists(service_account_path):
        print(f"✅ Service account file: {service_account_path}")
    else:
        print(f"❌ Service account file: {service_account_path} (niet gevonden)")
    
    # Check environment variables
    env_vars = {
        "GCAL_CALENDAR_ID": "Calendar ID",
        "GMAIL_USER": "Gmail User",
        "GMAIL_APP_PASSWORD": "Gmail App Password",
        "SMTP_SERVER": "SMTP Server",
        "SMTP_PORT": "SMTP Port"
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            if "PASSWORD" in var:
                print(f"✅ {description}: {'*' * len(value)}")
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: Niet ingesteld")
    
    print()

def main():
    """Main function"""
    print_setup_instructions()
    check_current_status()
    
    print("📝 Volgende Stappen:")
    print("1. Volg de setup instructies hierboven")
    print("2. Plaats het service account JSON bestand in config/")
    print("3. Update je .env bestand met de juiste waarden")
    print("4. Run: python3 test_calendar_integration.py")
    print("5. Test de integratie")
    print()
    
    print("❓ Heb je hulp nodig?")
    print("- Check de Google Cloud Console logs")
    print("- Verifieer de calendar permissions")
    print("- Test de SMTP instellingen")

if __name__ == "__main__":
    main()
