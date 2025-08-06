# 🚀 Quick Start Guide - TutorBot

Snelle setup van de WhatsApp bot in 5 minuten.

## 📋 Prerequisites

- Docker & Docker Compose geïnstalleerd
- Chatwoot instance beschikbaar
- Stripe account (voor betalingen)
- Google Cloud Project (voor Calendar)

## ⚡ Snelle Setup

### 1. Clone & Setup
```bash
cd tutorbot
cp env_example.txt .env
# Vul de .env file in met jouw waarden
```

### 2. Chatwoot Configuratie
```bash
# Setup custom attributes, labels en teams
python3 scripts/setup_chatwoot.py

# Of bekijk bestaande configuratie
python3 scripts/setup_chatwoot.py list
```

### 3. Start Bot
```bash
docker-compose up --build -d
```

### 4. Test Bot
```bash
# Test alle functionaliteiten
python3 scripts/test_bot.py
```

## 🔧 Configuratie

### Environment Variables
Vul deze waarden in in `.env`:

```bash
# Chatwoot (verplicht)
CW_URL=https://your-chatwoot-instance.com
CW_ACC_ID=1
CW_TOKEN=your_bot_token
CW_ADMIN_TOKEN=your_admin_token
CW_HMAC_SECRET=your_hmac_secret

# Stripe (optioneel voor betalingen)
STRIPE_WEBHOOK_SECRET=whsec_xxx
STANDARD_PRICE_ID_60=price_xxx
WEEKEND_PRICE_ID_60=price_xxx

# Google Calendar (optioneel voor planning)
GCAL_SERVICE_ACCOUNT_JSON=/app/config/gcal-service-account.json
```

### Chatwoot Webhook
Configureer in Chatwoot:
- **URL**: `https://your-domain.com/cw`
- **Events**: `conversation_created`, `message_created`
- **HMAC Secret**: Zelfde als in `.env`

## 🧪 Testen

### Test Scenario's
1. **Nieuwe klant**: Volledige intake flow
2. **Bestaande klant**: Snelle planning
3. **Weekend klant**: Speciale flow
4. **Betaling**: Stripe integratie

### Manual Testing
```bash
# Start bot
docker-compose up -d

# Bekijk logs
docker-compose logs -f tutorbot

# Test webhook
curl -X POST http://localhost:8000/cw \
  -H "Content-Type: application/json" \
  -d '{"event": "conversation_created", ...}'
```

## 🐛 Troubleshooting

### Bot start niet
```bash
# Check logs
docker-compose logs tutorbot

# Check environment
docker-compose config

# Rebuild
docker-compose down
docker-compose up --build -d
```

### Webhook niet ontvangen
- Controleer Chatwoot webhook URL
- Verificeer HMAC secret
- Check firewall/port configuratie

### Chatwoot errors
- Controleer API tokens
- Verificeer account ID
- Check custom attributes setup

## 📞 Support

Voor vragen:
1. Check de logs: `docker-compose logs tutorbot`
2. Test met: `python3 scripts/test_bot.py`
3. Controleer configuratie: `python3 scripts/setup_chatwoot.py list`

## 🎯 Volgende Stappen

Na succesvolle setup:
1. Configureer Stripe producten
2. Setup Google Calendar integratie
3. Test met echte WhatsApp berichten
4. Monitor logs en performance
5. Configureer team routing

---

**Status**: ✅ Ready for Production  
**Versie**: 2.0.0  
**Laatste update**: December 2024 