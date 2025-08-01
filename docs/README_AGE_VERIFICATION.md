# Leeftijdscontrole Systeem - Setup Instructies

## 1. Chatwoot Attributes Instellen

### Contact Attributes (per klant)
Voeg deze custom attributes toe aan je Chatwoot contacten:

- **is_adult** (checkbox)
- **age_verified_at** (text/datetime)
- **guardian_consent** (checkbox)
- **guardian_name** (text, optioneel)
- **guardian_phone** (text, optioneel)

### Conversation Attributes (per gesprek)
Voeg deze custom attributes toe aan je Chatwoot conversaties:

- **age_verified** (checkbox)
- **pending_intent** (text, tijdelijk gebruikt voor "plan")

### Labels (optioneel maar handig)
Voeg deze labels toe aan je Chatwoot:

- **age_verified** (label op gesprek)
- **needs_guardian** (gesprek)
- **minor** (gesprek)

## 2. Hoe het werkt

### Leeftijdscontrole Flow
1. **Bot start altijd met hoofdmenu** (zoals voorheen)
2. **Alleen bij "📅 Les plannen"** wordt leeftijdscontrole uitgevoerd:
   - Als `conversation.age_verified == true` → direct door naar plannen
   - Anders, als `contact.is_adult` bekend en niet verlopen (TTL) → markeer gesprek als verified en door
   - Anders → stel age-gate (✅ 18+ / 🚫 <18)

### TTL (Time To Live)
- Standaard: 365 dagen
- Configureerbaar via `AGE_TTL_DAYS` in docker-compose.yml
- Als klant-verificatie ouder is dan TTL, wordt opnieuw gevraagd

### Voogd Flow
Voor minderjarigen:
1. Vraag één bericht met naam + 06 van ouder/voogd
2. Zodra akkoord, wordt opgeslagen:
   - `guardian_consent: true`
   - `guardian_name: "<naam>"`
   - `guardian_phone: "<06>"`
   - `guardian_verified_at: "<timestamp>"`

## 3. Testcases

### Test 1: Nieuwe klant
1. Stuur "menu" → hoofdmenu verschijnt
2. Stuur "plan" → bot vraagt "18+?"
3. Stuur "adult" → door naar tijden; labels: age_verified

### Test 2: Minderjarige
1. Stuur "plan" → bot vraagt "18+?"
2. Stuur "minor" → vraagt voogd → blokkeert plannen; labels: minor,needs_guardian

### Test 3: Bestaande klant
1. Klant met `is_adult=true` en recent `age_verified_at`
2. Stuur "plan" → geen vraag, direct plannen
3. Ook nieuw gesprek werkt

### Test 4: TTL verlopen
1. Zet `AGE_TTL_DAYS=0` in docker-compose.yml
2. Stuur "plan" → age-gate opnieuw

## 4. Deploy

```bash
# Rebuild en restart
docker compose build && docker compose up -d

# Health check
curl -I https://bot.stephensprivelessen.nl/cw

# End-to-end test
# Stuur "menu" → "plan" → zie de gate/doorstroom
```

## 5. Privacy

- **Geen geboortedatum** wordt opgeslagen
- Alleen boolean `is_adult` + timestamp `age_verified_at`
- AVG-vriendelijker dan geboortedatum opslaan
- Voldoende voor beleid en compliance

## 6. Troubleshooting

### Logs bekijken
```bash
docker compose logs -f tutorbot
```

### Attributes controleren
- Controleer in Chatwoot of contact/conversation attributes correct zijn ingesteld
- Kijk naar de bot logs voor debugging informatie

### TTL aanpassen
- Wijzig `AGE_TTL_DAYS` in docker-compose.yml
- Rebuild en restart de container 