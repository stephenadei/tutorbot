# Google Workspace Integration Status

## 📊 Huidige Status

### ❌ Google Calendar Integration
- **Service Account**: Niet geconfigureerd
- **Calendar Access**: Niet beschikbaar
- **Event Creation**: Niet mogelijk

### ❌ Gmail SMTP Integration  
- **SMTP Credentials**: Niet geconfigureerd
- **Email Sending**: Niet mogelijk
- **App Password**: Niet ingesteld

## 🔧 Benodigde Setup

### 1. Google Cloud Project
- [ ] Google Cloud Project aanmaken
- [ ] Google Calendar API enable
- [ ] Service Account aanmaken
- [ ] Service Account key downloaden

### 2. Calendar Permissions
- [ ] Service account toevoegen aan calendar
- [ ] "Make changes to events" rechten geven
- [ ] Calendar ID instellen op `lessons@stephensprivelessen.nl`

### 3. Gmail SMTP Setup
- [ ] 2-Factor Authentication enable
- [ ] App Password genereren voor TutorBot
- [ ] SMTP instellingen configureren

### 4. Environment Variables
Voeg toe aan `.env`:

```bash
# Google Calendar
GCAL_SERVICE_ACCOUNT_JSON=/app/config/gcal-service-account.json
GCAL_CALENDAR_ID=lessons@stephensprivelessen.nl

# Gmail SMTP
GMAIL_USER=lessons@stephensprivelessen.nl
GMAIL_APP_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 🧪 Test Scripts

### Calendar Test
```bash
python3 test_calendar_integration.py
```

### Email Test  
```bash
python3 test_email_integration.py
```

### Setup Helper
```bash
python3 setup_google_workspace.py
```

## 📋 Stap-voor-Stap Setup

### Stap 1: Google Cloud Console
1. Ga naar https://console.cloud.google.com
2. Maak nieuw project aan: "TutorBot Calendar"
3. Enable Google Calendar API
4. Maak service account aan: "tutorbot-calendar"
5. Download JSON key bestand
6. Plaats in `config/gcal-service-account.json`

### Stap 2: Calendar Permissions
1. Log in op https://calendar.google.com met `lessons@stephensprivelessen.nl`
2. Ga naar Settings > "Settings for my calendars"
3. Klik op "Share with specific people"
4. Voeg service account email toe met "Make changes to events" rechten

### Stap 3: Gmail Security
1. Ga naar https://myaccount.google.com/security
2. Log in met `lessons@stephensprivelessen.nl`
3. Enable 2-Step Verification
4. Ga naar "App passwords"
5. Genereer app password voor "TutorBot"

### Stap 4: Environment Variables
Update `.env` bestand met alle benodigde variabelen

### Stap 5: Testen
Run beide test scripts om te verifiëren dat alles werkt

## 🎯 Doel

Na setup moet je kunnen:
- ✅ Calendar events aanmaken voor lessen
- ✅ Calendar events lezen en bewerken
- ✅ Emails versturen van `lessons@stephensprivelessen.nl`
- ✅ Automatische lesbevestigingen versturen
- ✅ Calendar integratie met TutorBot

## ❓ Hulp

Als je problemen hebt:
1. Check Google Cloud Console logs
2. Verifieer calendar permissions
3. Test SMTP instellingen
4. Controleer environment variables
