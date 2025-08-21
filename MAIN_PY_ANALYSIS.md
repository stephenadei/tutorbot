# Main.py Analysis - Waarom zo lang?

## 📊 **HUIDIGE SITUATIE**
- **6,244 regels code** in één file
- **67 functies** in één file  
- **Alle business logic** in één monolithisch bestand

## 🔍 **PROBLEEM ANALYSE**

### **1. Monolithische Architectuur**
Het grootste probleem is dat `main.py` **ALLES** doet:

#### **Flask App & Routes (±100 regels)**
```python
app = Flask(__name__)
@app.route("/health") 
def stripe_webhook():
```

#### **OpenAI Integration (±500 regels)**
```python
def analyze_preferences_with_openai()
def analyze_first_message_with_openai() 
def analyze_info_request_with_openai()
def prefill_intake_from_message()
```

#### **Webhook Handlers (±2000 regels)**
```python
def handle_conversation_created()
def handle_message_created() 
def handle_prefill_confirmation()
def handle_info_menu_selection()
def handle_handoff_menu_selection()
def handle_menu_selection()
def handle_trial_lesson_mode_selection()
def handle_intake_step()
def handle_planning_selection()
def handle_email_request()
def handle_faq_request()
```

#### **Utility Functions (±1000 regels)**
```python
def safe_set_conv_attrs()
def send_text_with_duplicate_check()
def detect_language_from_message()
def map_school_level()
def map_topic()
```

#### **Business Logic (±2000+ regels)**
- Intake flow management
- Prefill logic
- Menu generation
- Payment processing
- Calendar integration
- Email handling

### **2. Waarom We Scripts Hebben vs Main.py**

**Scripts zijn voor:**
- ✅ **Testing** - Isolatie van test logic
- ✅ **Setup** - One-time configuration
- ✅ **Debug** - Development tools
- ✅ **Analysis** - Data analysis tools

**Main.py bevat:**
- ❌ **Production Code** - Live bot functionality
- ❌ **Business Logic** - Core application logic
- ❌ **All Route Handlers** - Web endpoints
- ❌ **All Integrations** - OpenAI, Stripe, Calendar, Email

## 🎯 **REFACTORING OPLOSSING**

### **Target Architectuur:**
```
main.py (±200 regels)
├── routes/
│   ├── __init__.py
│   ├── health.py
│   ├── webhook.py
│   └── stripe.py
├── handlers/
│   ├── __init__.py
│   ├── conversation.py
│   ├── message.py
│   ├── intake.py
│   ├── prefill.py
│   └── menu.py
├── integrations/
│   ├── __init__.py
│   ├── openai_service.py
│   ├── stripe_service.py
│   └── email_service.py
├── utils/
│   ├── __init__.py
│   ├── language.py
│   ├── mapping.py
│   └── text_helpers.py
└── core/
    ├── __init__.py
    ├── config.py
    └── app.py
```

### **Verwachte Resultaat:**
- **main.py: ~200 regels** (alleen Flask app setup)
- **Modulaire code** met duidelijke scheiding
- **Herbruikbare componenten**
- **Testbare isolatie**
- **Onderhoudbaarheid++**

## 📋 **REFACTORING PRIORITEIT**

1. **HIGH:** Extract OpenAI functions → `integrations/openai_service.py`
2. **HIGH:** Extract webhook handlers → `handlers/` modules  
3. **MEDIUM:** Extract utility functions → `utils/` modules
4. **MEDIUM:** Extract Flask routes → `routes/` modules
5. **LOW:** Extract config and setup → `core/` modules

Dit verklaart waarom main.py zo lang is - het is een monolithische applicatie die gerefactored moet worden naar een modulaire architectuur!
