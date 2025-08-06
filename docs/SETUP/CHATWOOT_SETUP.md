# Chatwoot Setup voor TutorBot

## Overzicht

Deze configuratie implementeert een intelligente, gestructureerde aanpak voor Chatwoot + WhatsApp integratie voor Stephen's Privélessen. Het systeem gebruikt custom attributes, lean labels en automation rules voor optimale routing en rapportage.

## Bestanden

### 1. Contact Attributes (`contact_attributes.yaml`)
**Blijvende profieleigenschappen per contact:**

- `language` - Voorkeurstaal (nl|en)
- `school_level` - Onderwijsniveau (po|vmbo|havo|vwo|mbo|university_wo|university_hbo|adult)
- `segment` - Segment (parent, student, company, etc.)

### 2. Conversation Attributes (`conversation_attributes.yaml`)
**Per-ticket eigenschappen die resetten per conversatie:**

- `program` - Specifiek programma (mbo_rekenen_2f|3f|ib_math_sl|hl|cambridge)
- `topic_primary` - Hoofdonderwerp (calculus, percentages)
- `topic_secondary` - Secundair onderwerp
- `toolset` - Benodigde tools (python,spss,r)
- `lesson_mode` - Lesmodus (online|in_person|hybrid)
- `is_adult` - 18+ check
- `language_prompted` - Anti-loop vlag voor taalvraag
- `intake_completed` - Intake voltooid (audience+subject+service)

### 3. Labels (`labels_lean.yaml`)
**Lean labels georganiseerd per categorie:**

#### Audience (XOR - exact één per conversatie)
- `audience:po|vmbo|havo|vwo|mbo|university:wo|university:hbo|adult`

#### Subject (kan meerdere hebben)
- `subject:math|stats|science|english|data-science|programming|didactics|economics|creative`

#### Service (kan meerdere hebben)
- `service:trial|1on1|group|exam-prep|workshop|project-supervision|consultancy`

#### Process/Status (kan meerdere hebben)
- `status:awaiting_reply|booked|awaiting_pay`
- `payment:paid|overdue`
- `priority:urgent`
- `flag:vip|spam`

### 4. Automation Rules (`automations.yaml`)
**Volledige rules-spec voor intelligente routing:**

## Kernregels (samengevat)

### 1. Bootstrap
- **Event:** `conversation_created`
- **If:** `channel = WhatsApp`
- **Then:** Label `source:whatsapp`, zet `language_prompted=false`

### 2. Taal één keer vragen
- **Event:** `conversation_created`
- **If:** `contact.language` is leeg AND `language_prompted=false`
- **Then:** Stuur taalkeuze prompt, zet `language_prompted=true`

### 3. Taal detecteren
- **Event:** `message_created`
- **If:** Bericht bevat Nederlandse/Engelse woorden
- **Then:** Set `contact.language`, stuur bevestiging

### 4. Audience/schoollaag detecteren
- **Event:** `message_created`
- **If:** Tekst bevat PO/VMBO/HAVO/VWO/MBO/WO/HBO/Adult
- **Then:** Set `contact.school_level` + voeg audience-label toe

### 5. Program zetten
- **Event:** `message_created`
- **If:** Bevat 2F/3F/IB HL/IB SL/Cambridge
- **Then:** Set `conversation.program` + baseline subject-label

### 6. Onderwerp & tools
- **Event:** `message_created`
- **If:** Bevat kernwoorden (calculus, Python, SPSS, etc.)
- **Then:** Schrijf naar `topic_primary` en `toolset`, voeg subject-labels toe

### 7. Service detecteren
- **Event:** `message_created`
- **If:** Bevat service-woorden (proefles, 1-op-1, workshop, etc.)
- **Then:** Service-label toevoegen

### 8. Subject afleiden (fallback)
- **Event:** `message_created`
- **If:** Woordenlijsten per domein
- **Then:** Voeg overeenkomend subject-label toe

### 9. Team-routing
- **If:** `subject:programming|data-science` → assign team "Data/Programming"
- **Elif:** `audience:vmbo|havo|vwo` & `subject:math|science|english` → VO-docenten
- **Elif:** `audience:university:wo|hbo` → HO/Universiteit
- **Elif:** `program` in {ib_math_sl, ib_math_hl} → International/IB
- **Elif:** `payment:*` → Finance

### 10. Finance tagging
- **If:** "factuur, btw, tikkie, betaal, invoice, paid, openstaand"
- **Then:** Label `payment:info`, assign Finance

### 11. Status & betaling
- **If:** "bevestigd/confirmed/tot dan" → `status:booked`
- **If:** "betaald/paid" → `payment:paid` (en verwijder `status:awaiting_pay|payment:overdue`)

### 12. Urgentie
- **If:** "vandaag/today/morgen/tomorrow/asap/dringend/urgent"
- **Then:** `priority:urgent` + teamnotificatie

### 13. Cleanup (XOR + cap)
- **Event:** `label_added`
- **Enforce:**
  - XOR: slechts één van `audience:*`
  - Cap: max 6 labels (overschot verwijderen op volgorde: status→priority→service→subject)

## Voorbeelden

### MBO Rekenen 3F, proefles, NL
```
Attributes:
  program: mbo_rekenen_3f
  topic_primary: "percentages"
  toolset: ""

Labels:
  audience:mbo
  subject:math
  service:trial
  status:awaiting_reply
```

### WO Calculus, 1-op-1, EN, Python help
```
Attributes:
  program: none
  topic_primary: "calculus"
  toolset: "python"

Labels:
  audience:university:wo
  subject:math
  subject:data-science
  service:1on1
```

## Implementatie

### 1. Setup Custom Attributes
```bash
# Contact attributes
curl -X POST "https://your-chatwoot.com/api/v1/accounts/{account_id}/custom_attribute_definitions" \
  -H "Api-Access-Token: {admin_token}" \
  -H "Content-Type: application/json" \
  -d @contact_attributes.yaml

# Conversation attributes  
curl -X POST "https://your-chatwoot.com/api/v1/accounts/{account_id}/custom_attribute_definitions" \
  -H "Api-Access-Token: {admin_token}" \
  -H "Content-Type: application/json" \
  -d @conversation_attributes.yaml
```

### 2. Setup Labels
```bash
# Create all labels from labels_lean.yaml
curl -X POST "https://your-chatwoot.com/api/v1/accounts/{account_id}/labels" \
  -H "Api-Access-Token: {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"title": "audience:vmbo"}'
```

### 3. Setup Automation Rules
De automation rules in `automations.yaml` moeten handmatig worden geconfigureerd in de Chatwoot interface, omdat de API voor automations beperkt is.

## WhatsApp Quick Replies

### Taalkeuze
```
🌍 In welke taal wil je communiceren? / In which language would you like to communicate?

🇳🇱 Nederlands
🇬🇧 English
```

### Onderwijsniveau
```
📚 Wat is je huidige onderwijsniveau? / What is your current education level?

🏫 VMBO
🎓 HAVO  
🎓 VWO
🎓 HBO
🎓 WO
💼 Volwassenenonderwijs
🏢 Werknemer
```

### Vakken
```
📖 Welk vak wil je bijles in? / Which subject do you want tutoring in?

📊 Wiskunde
🧮 Rekenen
📈 Economie
🔬 Natuurkunde
🧪 Scheikunde
🌍 Aardrijkskunde
📖 Nederlands
🇬🇧 Engels
🇩🇪 Duits
🇫🇷 Frans
📚 Studievaardigheden
```

### Jaar/Leerjaar
```
📅 In welk jaar/leerjaar zit je? / In which year/grade are you?

1️⃣ Jaar 1
2️⃣ Jaar 2
3️⃣ Jaar 3
4️⃣ Jaar 4
5️⃣ Jaar 5
6️⃣ Jaar 6
🎓 Eindexamenjaar
💼 Volwassen
```

### Lesmodus
```
🎯 Hoe wil je de les volgen? / How would you like to follow the lesson?

🏠 Online (via Zoom)
🏫 Offline (bij jou thuis)
🏢 Offline (bij mij thuis)
🤔 Weet nog niet
```

## Monitoring & Rapportage

### Belangrijke metrics
- **Intake completion rate** - Percentage conversaties met `intake_completed=true`
- **Team routing accuracy** - Juiste team assignment
- **Response time** - Tijd tot eerste response
- **Conversion rate** - Van proefles naar betalende klant

### Dashboards
1. **Intake Overview** - Per audience, subject, service
2. **Team Performance** - Workload per team
3. **Language Distribution** - NL vs EN usage
4. **Urgency Tracking** - Priority:urgent labels

## Troubleshooting

### Veelvoorkomende problemen
1. **Labels worden niet toegevoegd** - Check automation rule conditions
2. **Team routing werkt niet** - Verify team names in Chatwoot
3. **Attributes worden niet opgeslagen** - Check API permissions
4. **Language detection faalt** - Review keyword lists

### Debug tips
- Check Chatwoot logs voor automation rule execution
- Verify custom attributes zijn aangemaakt
- Test automation rules met dummy data
- Monitor webhook payloads voor correcte data

## Volgende stappen

1. **Implementeer automation rules** in Chatwoot interface
2. **Test met dummy conversaties** 
3. **Configureer WhatsApp Business API**
4. **Setup monitoring dashboards**
5. **Train team op nieuwe labels en routing**

## Contact

Voor vragen over deze setup, neem contact op met Stephen via de bot of direct. 