#!/usr/bin/env python3
"""
Test App Password Access
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_app_password_access():
    """Test if we can access app passwords"""
    print("🔍 Testing App Password Access...")
    
    # Check if we can access the app passwords page
    print("📋 Om te controleren of app passwords werken:")
    print("1. Ga naar: https://myaccount.google.com/apppasswords")
    print("2. Log in met lessons@stephensprivelessen.nl")
    print("3. Controleer of je de app passwords pagina kunt zien")
    print()
    
    # Check current settings
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"📧 Huidige configuratie:")
    print(f"   User: {gmail_user}")
    print(f"   App Password: {gmail_password[:4]}...{gmail_password[-4:] if gmail_password else 'None'}")
    print()
    
    print("🔍 Mogelijke problemen:")
    print("1. 2-Step Verification is niet ingeschakeld")
    print("2. Google Workspace admin heeft app passwords geblokkeerd")
    print("3. Account heeft geen SMTP toegang")
    print("4. App password is verlopen of ongeldig")
    print()
    
    print("📋 Controleer dit:")
    print("1. Is 2-Step Verification ingeschakeld?")
    print("2. Kun je app passwords genereren?")
    print("3. Ben je admin van het Google Workspace account?")
    print("4. Zijn er beperkingen op SMTP toegang?")

if __name__ == "__main__":
    test_app_password_access()
