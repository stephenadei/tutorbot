# TutorBot Refactoring Plan - Met Functionaliteit Garantie

## 🎯 **DOEL**
Refactor `main.py` (6244 regels) naar modulaire architectuur **ZONDER** functionaliteit te breken.

## ✅ **GARANTIES**
- **100% backward compatibility** - Alle functies werken exact hetzelfde
- **Geen breaking changes** - API endpoints blijven identiek
- **Incremental refactoring** - Stap voor stap, test na elke stap
- **Rollback mogelijk** - Elke stap kan ongedaan gemaakt worden

## 📋 **REFACTORING STAPPEN**

### **STAP 1: Extract OpenAI Integration (HIGH PRIORITY)**
**Van:** `main.py` (regels 1308-2019)
**Naar:** `modules/integrations/openai_service.py`

**Functies:**
- `analyze_preferences_with_openai()`
- `analyze_first_message_with_openai()`
- `analyze_info_request_with_openai()`
- `prefill_intake_from_message()`

**Test:** ✅ Test elke functie na extractie

### **STAP 2: Extract Utility Functions (HIGH PRIORITY)**
**Van:** `main.py` (regels 31-1150)
**Naar:** `modules/utils/`

**Categorieën:**
- `modules/utils/text_helpers.py` - Text en messaging functies
- `modules/utils/language.py` - Language detection en mapping
- `modules/utils/mapping.py` - School level, topic mapping

**Test:** ✅ Test alle utility functies

### **STAP 3: Extract Webhook Handlers (MEDIUM PRIORITY)**
**Van:** `main.py` (regels 2662-6201)
**Naar:** `modules/handlers/`

**Modules:**
- `modules/handlers/conversation.py` - Conversation created
- `modules/handlers/message.py` - Message handling
- `modules/handlers/intake.py` - Intake flow
- `modules/handlers/prefill.py` - Prefill logic
- `modules/handlers/menu.py` - Menu handling

**Test:** ✅ Test elke webhook handler

### **STAP 4: Extract Flask Routes (LOW PRIORITY)**
**Van:** `main.py` (regels 2598-6146)
**Naar:** `modules/routes/`

**Modules:**
- `modules/routes/health.py` - Health check
- `modules/routes/webhook.py` - Main webhook
- `modules/routes/stripe.py` - Stripe webhook

**Test:** ✅ Test alle endpoints

### **STAP 5: Extract Core App (LOW PRIORITY)**
**Van:** `main.py` (regels 1-73)
**Naar:** `modules/core/`

**Modules:**
- `modules/core/app.py` - Flask app setup
- `modules/core/config.py` - Configuration

**Test:** ✅ Test complete app startup

## 🔄 **REFACTORING STRATEGIE**

### **Voor Elke Stap:**
1. **Backup maken** van huidige state
2. **Extract functies** naar nieuwe module
3. **Import toevoegen** in main.py
4. **Test functionaliteit** - exacte output vergelijken
5. **Commit changes** met duidelijke message

### **Testing Garantie:**
- **Unit tests** voor elke geëxtraheerde functie
- **Integration tests** voor webhook flows
- **Manual testing** van WhatsApp bot flows
- **Log comparison** - zelfde output garanderen

## 📊 **VERWACHTE RESULTAAT**

### **Voor Refactoring:**
```
main.py: 6244 regels
├── 67 functies
├── Alle business logic
└── Monolithische structuur
```

### **Na Refactoring:**
```
main.py: ~200 regels
├── Flask app setup
├── Route registratie
└── Clean imports

modules/
├── handlers/ (~2000 regels)
├── integrations/ (~500 regels)  
├── utils/ (~1000 regels)
├── routes/ (~300 regels)
└── core/ (~100 regels)
```

## 🚀 **START REFACTORING**

Klaar om te beginnen met **STAP 1: OpenAI Integration**?
