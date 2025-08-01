# TutorBot Test Scenarios

## 📋 Test Overzicht

Deze documentatie bevat uitgebreide test scenarios om de TutorBot, automation rules, en workflow functionaliteit te valideren.

## 🧪 Test Setup

### **Voorbereiding:**
1. **Bot draait** in Docker
2. **Automation rules** zijn aangemaakt
3. **Webhook** is geconfigureerd in Chatwoot
4. **Test contacten** zijn gewiped (optioneel)

### **Test Commands:**
```bash
# Start bot
docker-compose up -d

# Check bot status
docker-compose logs -f

# Wipe contacts voor schone test
python3 wipe_contacts.py --force

# Audit attributes
python3 audit_attributes.py
```

## 🔄 Test Scenario 1: Nieuwe Volwassen Klant

### **Doel:** Test volledige nieuwe klant workflow
### **Verwachte Resultaten:** Alle automation rules triggeren correct

### **Stappen:**
1. **Start nieuwe conversatie** in Chatwoot
2. **Stuur bericht:** "Hallo, ik wil graag bijles"
3. **Verwacht:** Bot vraagt naam
4. **Stuur naam:** "Jan"
5. **Verwacht:** Bot toont welkom menu
6. **Kies:** "Proefles"
7. **Verwacht:** Bot verzamelt onderwijs informatie
8. **Vul in:** VMBO, Wiskunde, Jaar 2, Online
9. **Verwacht:** Bot vraagt leeftijd
10. **Antwoord:** "Ja, 18+"
11. **Verwacht:** Bot kan planning starten

### **Verwachte Labels:**
- ✅ `new_client`
- ✅ `age_verified`

### **Verwachte Attributes:**
- ✅ `first_name = "Jan"`
- ✅ `language = "nl"`
- ✅ `is_adult = "true"`
- ✅ `is_student = "true"`
- ✅ `education_level = "vmbo"`
- ✅ `subject = "wiskunde"`
- ✅ `year = "jaar2"`
- ✅ `format_preference = "online"`
- ✅ `age_verified_at` = timestamp

## 🔄 Test Scenario 2: Minderjarige Klant

### **Doel:** Test minderjarigen workflow met ouder toestemming
### **Verwachte Resultaten:** Guardian workflow triggert correct

### **Stappen:**
1. **Start nieuwe conversatie**
2. **Stuur:** "Hallo, ik ben 16 en wil bijles"
3. **Verwacht:** Bot vraagt naam
4. **Stuur:** "Lisa"
5. **Verwacht:** Bot vraagt leeftijd
6. **Antwoord:** "Nee, <18"
7. **Verwacht:** Bot vraagt ouder toestemming
8. **Stuur:** "Mijn moeder heet Maria, telefoon 0612345678"
9. **Verwacht:** Bot bevestigt toestemming
10. **Verwacht:** Bot kan verder met planning

### **Verwachte Labels:**
- ✅ `needs_guardian`
- ✅ `new_client`
- ✅ `age_verified`

### **Verwachte Attributes:**
- ✅ `is_adult = "false"`
- ✅ `guardian_name = "Maria"`
- ✅ `guardian_phone = "0612345678"`
- ✅ `guardian_consent = "true"`
- ✅ `guardian_verified_at` = timestamp

## 🔄 Test Scenario 3: Bestaande Klant

### **Doel:** Test returning client workflow
### **Verwachte Resultaten:** Bot herkent bestaande klant

### **Stappen:**
1. **Gebruik bestaande contact** (van scenario 1)
2. **Stuur bericht:** "Hallo, ik wil nog een les plannen"
3. **Verwacht:** Bot herkent klant
4. **Verwacht:** Bot toont welkom terug menu
5. **Kies:** "Planning"
6. **Verwacht:** Bot kan direct plannen

### **Verwachte Labels:**
- ✅ `returning_client`
- ✅ `age_verified`

### **Verwachte Attributes:**
- ✅ `welcome_done = "true"`

## 🔄 Test Scenario 4: Ouder voor Kind

### **Doel:** Test ouder workflow
### **Verwachte Resultaten:** Ouder wordt geregistreerd voor kind

### **Stappen:**
1. **Start nieuwe conversatie**
2. **Stuur:** "Hallo, ik ben de moeder van Lisa en wil bijles voor haar"
3. **Verwacht:** Bot detecteert ouder
4. **Verwacht:** Bot vraagt kind naam
5. **Stuur:** "Lisa"
6. **Verwacht:** Bot verzamelt kind informatie
7. **Vul in:** HAVO, Engels, Jaar 3, Offline
8. **Verwacht:** Bot vraagt leeftijd kind
9. **Antwoord:** "Nee, <18"
10. **Verwacht:** Bot vraagt ouder toestemming
11. **Stuur:** "Ik geef toestemming"
12. **Verwacht:** Bot kan planning starten

### **Verwachte Labels:**
- ✅ `needs_guardian`
- ✅ `new_client`
- ✅ `age_verified`

### **Verwachte Attributes:**
- ✅ `is_parent = "true"`
- ✅ `guardian_consent = "true"`

## 🔄 Test Scenario 5: Betaling Workflow

### **Doel:** Test betaling workflow
### **Verwachte Resultaten:** Alleen studenten kunnen betalen

### **Stappen:**
1. **Gebruik bestaande student** (van scenario 1)
2. **Stuur:** "Betaling"
3. **Verwacht:** Bot toont betalingsinformatie
4. **Stuur:** "Tikkie"
5. **Verwacht:** Bot bevestigt betalingslink

### **Test zonder student status:**
1. **Start nieuwe conversatie**
2. **Stuur:** "Betaling"
3. **Verwacht:** Bot zegt dat alleen studenten kunnen betalen

## 🔄 Test Scenario 6: FAQ Workflow

### **Doel:** Test FAQ responses
### **Verwachte Resultaten:** Correcte FAQ antwoorden

### **Test Cases:**
| Input | Verwacht Resultaat |
|-------|-------------------|
| "Tarieven" | Tarieven informatie |
| "Voorwaarden" | Pakketvoorwaarden |
| "Reiskosten" | Reiskosten informatie |
| "Online" | Online lessen info |
| "Locatie" | Locatie informatie |

## 🔄 Test Scenario 7: Weekend Korting

### **Doel:** Test weekend korting workflow
### **Verwachte Resultaten:** Korting wordt toegepast

### **Stappen:**
1. **Gebruik bestaande klant**
2. **Stuur:** "Weekend korting"
3. **Verwacht:** Bot toont weekend korting info
4. **Verwacht:** `weekend_discount` label wordt toegevoegd

## 🔄 Test Scenario 8: Meertalige Ondersteuning

### **Doel:** Test meertalige functionaliteit
### **Verwachte Resultaten:** Bot schakelt naar juiste taal

### **Nederlands Test:**
1. **Stuur:** "Hallo, ik wil bijles"
2. **Verwacht:** Bot blijft in Nederlands

### **Engels Test:**
1. **Stuur:** "Hello, I want tutoring"
2. **Verwacht:** Bot schakelt naar Engels
3. **Verwacht:** Alle berichten in Engels

## 🔄 Test Scenario 9: Automation Rules

### **Doel:** Valideer automation rules
### **Verwachte Resultaten:** Labels worden automatisch toegevoegd

### **Test Cases:**

#### **1. Minor Detection:**
- Stel `is_adult = false` in contact attributes
- **Verwacht:** `needs_guardian` label wordt toegevoegd

#### **2. Age Verification:**
- Stel `age_verified_at` in contact attributes
- **Verwacht:** `age_verified` label wordt toegevoegd

#### **3. New Student:**
- Stel `is_student = true` en `welcome_done = false` in
- **Verwacht:** `new_client` label wordt toegevoegd

#### **4. Returning Student:**
- Stel `is_student = true` en `welcome_done = true` in
- **Verwacht:** `returning_client` label wordt toegevoegd

#### **5. Weekend Discount:**
- Stel `wknd_eligible = true` in
- **Verwacht:** `weekend_discount` label wordt toegevoegd

## 🔄 Test Scenario 10: Error Handling

### **Doel:** Test error handling en edge cases
### **Verwachte Resultaten:** Bot handelt errors gracefully af

### **Test Cases:**

#### **1. Ongeldige Input:**
- Stuur onzin berichten
- **Verwacht:** Bot vraagt om verduidelijking

#### **2. Dubbele Registratie:**
- Probeer opnieuw te registreren als student
- **Verwacht:** Bot herkent bestaande status

#### **3. Webhook Errors:**
- Simuleer webhook failures
- **Verwacht:** Bot retry mechanisme

#### **4. API Errors:**
- Simuleer Chatwoot API errors
- **Verwacht:** Bot graceful degradation

## 📊 Test Resultaten Template

### **Test Rapport:**
```
Test Scenario: [Naam]
Datum: [YYYY-MM-DD]
Tester: [Naam]

✅ Passed Tests:
- [Test 1]
- [Test 2]

❌ Failed Tests:
- [Test 3] - [Reden]

⚠️ Issues Found:
- [Issue 1]
- [Issue 2]

📊 Metrics:
- Response Time: [X] seconds
- Success Rate: [X]%
- Labels Created: [X]
- Attributes Set: [X]

🎯 Recommendations:
- [Aanbeveling 1]
- [Aanbeveling 2]
```

## 🚀 Performance Tests

### **Load Testing:**
1. **10 gelijktijdige conversaties**
2. **100 berichten per minuut**
3. **24/7 uptime test**

### **Stress Testing:**
1. **API rate limiting**
2. **Memory usage**
3. **Database performance**

## 🔧 Debug Tools

### **Log Analysis:**
```bash
# Bot logs
docker-compose logs -f

# API calls
grep "API" logs

# Error tracking
grep "ERROR" logs
```

### **Attribute Verification:**
```bash
# Check contact attributes
python3 audit_attributes.py

# Verify automation rules
python3 setup_automation_rules.py
```

### **Manual Testing:**
1. **Chatwoot Dashboard** - Check labels en attributes
2. **API Testing** - Direct API calls testen
3. **Webhook Testing** - Webhook payloads valideren

---

**Laatste update:** 30 juli 2025  
**Versie:** 1.0  
**Auteur:** TutorBot Development Team 