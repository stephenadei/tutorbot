# TutorBot Workflow Documentation

## 📋 Overzicht

Deze documentatie beschrijft hoe TutorBot, Chatwoot automation rules, en custom attributes samenwerken om een efficiënte workflow te creëren voor bijles management.

## 🏗️ Architectuur

### **Componenten:**
1. **TutorBot** - Python Flask applicatie
2. **Chatwoot** - CRM platform
3. **Automation Rules** - Automatische workflow triggers
4. **Custom Attributes** - Contact data opslag
5. **Labels** - Workflow management

### **Data Flow:**
```
Klant → TutorBot → Custom Attributes → Automation Rules → Labels → Workflow
```

## 🔧 Custom Attributes

### **Contact Attributes (20 stuks):**

| Attribute | Type | Beschrijving | Gebruik |
|-----------|------|--------------|---------|
| `first_name` | text | Voornaam klant | Persoonlijke communicatie |
| `language` | text | Taalvoorkeur (nl/en) | Meertalige ondersteuning |
| `is_adult` | text | Leeftijd status | Leeftijdsverificatie |
| `guardian_consent` | text | Ouder toestemming | Minderjarigen workflow |
| `guardian_name` | text | Naam ouder/voogd | Contact informatie |
| `guardian_phone` | text | Telefoon ouder/voogd | Contact informatie |
| `guardian_verified_at` | text | Toestemming verificatie datum | Audit trail |
| `is_student` | text | Leerling status | Student workflow |
| `is_parent` | text | Ouder status | Ouder workflow |
| `student_since` | text | Student sinds datum | Geschiedenis |
| `parent_since` | text | Ouder sinds datum | Geschiedenis |
| `education_level` | text | Onderwijsniveau | Les planning |
| `subject` | text | Vak voor bijles | Les planning |
| `year` | text | Jaar/leerjaar | Les planning |
| `format_preference` | text | Online/offline voorkeur | Les planning |
| `welcome_done` | text | Welkom voltooid | Nieuwe vs bestaande klant |
| `first_contact_at` | text | Eerste contact datum | Geschiedenis |
| `name_asked_at` | text | Naam gevraagd datum | Audit trail |
| `age_verified_at` | text | Leeftijd geverifieerd datum | Audit trail |
| `wknd_eligible` | text | Weekend korting beschikbaar | Korting management |

### **Conversation Attributes (2 stuks):**

| Attribute | Type | Beschrijving | Gebruik |
|-----------|------|--------------|---------|
| `age_verified` | text | Leeftijd geverifieerd | Conversatie status |
| `pending_intent` | text | Wachtende intentie | Conversatie flow |

## 🏷️ Labels

### **Workflow Labels (7 stuks):**

| Label | Trigger | Beschrijving | Workflow |
|-------|---------|--------------|----------|
| `new_client` | `is_student=true` + `welcome_done=false` | Nieuwe klant | Welkom workflow |
| `returning_client` | `is_student=true` + `welcome_done=true` | Bestaande klant | Follow-up workflow |
| `needs_guardian` | `is_adult=false` | Minderjarig | Ouder toestemming workflow |
| `minor` | `is_adult=false` | Minderjarig | Leeftijdsverificatie |
| `age_verified` | `age_verified_at` is present | Leeftijd geverifieerd | Planning workflow |
| `weekend_discount` | `wknd_eligible=true` | Weekend korting beschikbaar | Korting workflow |
| `needs_parent_contact` | `is_adult=false` + `guardian_consent=""` | Ouder contact nodig | Ouder workflow |

## 🤖 Automation Rules

### **Leeftijd Management:**

#### **1. Minor Needs Guardian**
- **Trigger:** `contact_updated`
- **Condition:** `is_adult = false`
- **Action:** Add label `needs_guardian`
- **Workflow:** Automatische ouder toestemming workflow

#### **2. Age Verified**
- **Trigger:** `contact_updated`
- **Condition:** `age_verified_at` is present
- **Action:** Add label `age_verified`
- **Workflow:** Planning workflow vrijgeven

### **Student Management:**

#### **3. New Student Registration**
- **Trigger:** `contact_updated`
- **Condition:** `is_student = true` AND `welcome_done = false`
- **Action:** Add label `new_client`
- **Workflow:** Welkom en registratie workflow

#### **4. Returning Student**
- **Trigger:** `contact_updated`
- **Condition:** `is_student = true` AND `welcome_done = true`
- **Action:** Add label `returning_client`
- **Workflow:** Follow-up en planning workflow

### **Ouder Management:**

#### **5. Needs Parent Contact**
- **Trigger:** `contact_updated`
- **Condition:** `is_adult = false` AND `guardian_consent = ""`
- **Action:** Add label `needs_parent_contact`
- **Workflow:** Ouder contact workflow

### **Korting Management:**

#### **6. Weekend Discount Eligible**
- **Trigger:** `contact_updated`
- **Condition:** `wknd_eligible = true`
- **Action:** Add label `weekend_discount`
- **Workflow:** Korting toepassing

## 🔄 Workflow Flows

### **Nieuwe Klant Flow:**
```
1. Klant stuurt bericht
2. Bot detecteert taal
3. Bot vraagt naam
4. Bot stelt `first_name` en `language`
5. Bot toont welkom menu
6. Klant kiest optie (proefles/betaling/info)
7. Bot verzamelt informatie
8. Bot stelt `is_student = true`
9. Automation rule voegt `new_client` label toe
10. Stephen krijgt notificatie van nieuwe klant
```

### **Minderjarige Flow:**
```
1. Klant is minderjarig
2. Bot stelt `is_adult = false`
3. Automation rule voegt `needs_guardian` label toe
4. Bot vraagt ouder toestemming
5. Ouder geeft toestemming
6. Bot stelt `guardian_consent = true`
7. Bot kan verder met planning
```

### **Planning Flow:**
```
1. Klant wil les plannen
2. Bot controleert leeftijd
3. Bot stelt `age_verified_at`
4. Automation rule voegt `age_verified` label toe
5. Bot verzamelt planning informatie
6. Bot stelt `pending_intent = "plan"`
7. Stephen krijgt notificatie van planning verzoek
```

### **Weekend Korting Flow:**
```
1. Klant is eligible voor weekend korting
2. Bot stelt `wknd_eligible = true`
3. Automation rule voegt `weekend_discount` label toe
4. Bot toont weekend korting in menu
5. Klant kan profiteren van korting
```

## 📊 Monitoring & Analytics

### **Key Metrics:**
- **Nieuwe klanten:** `new_client` label count
- **Bestaande klanten:** `returning_client` label count
- **Minderjarigen:** `needs_guardian` label count
- **Planning verzoeken:** `age_verified` label count
- **Weekend kortingen:** `weekend_discount` label count

### **Dashboard Views:**
- **Conversations by Label** - Overzicht per workflow
- **Contact Attributes** - Data kwaliteit
- **Automation Rules** - Rule performance
- **Bot Performance** - Response times, success rates

## 🛠️ Onderhoud

### **Dagelijks:**
- Monitor automation rules performance
- Check voor failed webhook calls
- Review nieuwe contacten en labels

### **Wekelijks:**
- Audit custom attributes data kwaliteit
- Review workflow efficiency
- Update automation rules indien nodig

### **Maandelijks:**
- Volledige workflow audit
- Performance analyse
- Feature updates en verbeteringen

## 🔧 Troubleshooting

### **Veelvoorkomende Issues:**

#### **1. Automation Rules werken niet**
- **Check:** API permissions
- **Check:** Rule conditions syntax
- **Check:** Custom attributes bestaan

#### **2. Labels worden niet toegevoegd**
- **Check:** Automation rule status
- **Check:** Contact attribute values
- **Check:** Bot webhook calls

#### **3. Bot reageert niet**
- **Check:** Docker container status
- **Check:** Webhook URL configuratie
- **Check:** HMAC secret instellingen

### **Debug Commands:**
```bash
# Check bot status
docker-compose logs -f

# Audit attributes
python3 audit_attributes.py

# Test automation rules
python3 setup_automation_rules.py

# Wipe contacts (voor testing)
python3 wipe_contacts.py --force
```

## 🚀 Toekomstige Verbeteringen

### **Geplande Features:**
1. **Advanced Analytics** - Gedetailleerde workflow metrics
2. **A/B Testing** - Verschillende workflow varianten
3. **Machine Learning** - Automatische intentie detectie
4. **Multi-language Support** - Meer talen dan NL/EN
5. **Integration APIs** - Koppeling met andere systemen

### **Workflow Optimalisaties:**
1. **Smart Routing** - Automatische conversatie routing
2. **Predictive Analytics** - Klant gedrag voorspelling
3. **Automated Follow-up** - Automatische herinneringen
4. **Dynamic Pricing** - Dynamische tarief berekening

---

**Laatste update:** 30 juli 2025  
**Versie:** 1.0  
**Auteur:** TutorBot Development Team 