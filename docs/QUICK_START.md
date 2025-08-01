# Quick Start Guide - Chatwoot Setup

## 🚀 Snelle Setup (5 minuten)

### 1. Environment Variables
Zet deze environment variables in je `.env` bestand:

```bash
CW_URL=https://crm.stephenadei.nl
CW_ACC_ID=your_account_id
CW_ADMIN_TOKEN=your_admin_token
CW_TOKEN=your_bot_token
CW_HMAC_SECRET=your_hmac_secret
```

### 2. Run Master Setup
```bash
cd tutorbot
python3 scripts/setup_all.py
```

Dit script:
- ✅ Maakt alle custom attributes aan
- ✅ Maakt alle labels aan  
- ✅ Toont automation rules info
- ✅ Geeft next steps

### 3. Manual Steps
De automation rules moeten handmatig worden geconfigureerd in de Chatwoot interface:

1. Ga naar **Settings > Automations**
2. Maak nieuwe automation rules aan volgens `config/automations.yaml`
3. Test met dummy conversaties

## 📁 Bestanden Overzicht

| Bestand | Beschrijving |
|---------|-------------|
| `config/contact_attributes.yaml` | Contact eigenschappen (blijvend) |
| `config/conversation_attributes.yaml` | Conversatie eigenschappen (per ticket) |
| `config/labels_lean.yaml` | Lean labels voor routing |
| `config/automations.yaml` | Automation rules specificatie |
| `scripts/setup_all.py` | Master setup script |
| `scripts/setup_attributes.py` | Custom attributes setup |
| `scripts/setup_labels.py` | Labels setup |
| `docs/README_chatwoot_setup.md` | Volledige documentatie |

## 🎯 Belangrijkste Features

### Contact Attributes
- **language** - Voorkeurstaal (nl|en)
- **school_level** - Onderwijsniveau (po|vmbo|havo|vwo|mbo|university_wo|university_hbo|adult)
- **segment** - Segment (parent, student, company)

### Conversation Attributes  
- **program** - Specifiek programma (mbo_rekenen_2f|3f|ib_math_sl|hl|cambridge)
- **topic_primary** - Hoofdonderwerp (calculus, percentages)
- **toolset** - Benodigde tools (python,spss,r)
- **lesson_mode** - Lesmodus (online|in_person|hybrid)
- **language_prompted** - Anti-loop vlag
- **intake_completed** - Intake voltooid

### Labels (Lean)
- **Audience** (XOR): `audience:po|vmbo|havo|vwo|mbo|university:wo|university:hbo|adult`
- **Subject**: `subject:math|stats|science|english|data-science|programming|didactics|economics|creative`
- **Service**: `service:trial|1on1|group|exam-prep|workshop|project-supervision|consultancy`
- **Process**: `status:*|payment:*|priority:urgent|flag:vip|spam`

## 🔄 Automation Rules

### Kernregels
1. **Bootstrap** - WhatsApp conversaties initialiseren
2. **Taal detectie** - Eén keer vragen, daarna automatisch
3. **Audience detectie** - Schoolniveau herkennen
4. **Program detectie** - Specifieke programma's (2F, 3F, IB, etc.)
5. **Topic & tools** - Onderwerpen en tools herkennen
6. **Service detectie** - Dienstverlening herkennen
7. **Team routing** - Automatische team assignment
8. **Finance tagging** - Betaling gerelateerde zaken
9. **Status tracking** - Conversatie status bijhouden
10. **Cleanup** - XOR enforcement + label cap (max 6)

## 📊 Voorbeelden

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

## 🛠️ Troubleshooting

### Veelvoorkomende problemen
1. **Labels worden niet toegevoegd** - Check automation rule conditions
2. **Team routing werkt niet** - Verify team names in Chatwoot
3. **Attributes worden niet opgeslagen** - Check API permissions

### Debug commands
```bash
# List existing labels
python3 scripts/setup_labels.py list

# List existing attributes  
python3 scripts/setup_attributes.py list

# Setup only contact attributes
python3 scripts/setup_attributes.py contact

# Setup only conversation attributes
python3 scripts/setup_attributes.py conversation
```

## 📞 Support

Voor vragen over deze setup, neem contact op met Stephen via de bot of direct.

---

**Status**: ✅ Ready for production
**Laatste update**: December 2024
**Versie**: 1.0.0 