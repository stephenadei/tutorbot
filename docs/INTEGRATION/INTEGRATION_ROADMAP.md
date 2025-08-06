# Integration Roadmap - Calendar & Payment

## 🎯 **Status Overzicht**
- ✅ **Core Bot Logic** - Volledig functioneel
- ✅ **Chatwoot Integration** - Volledig functioneel  
- ✅ **Prefill & Intake System** - Volledig functioneel
- ✅ **WhatsApp Formatting** - Volledig functioneel
- ✅ **Menu System** - Volledig functioneel
- 🔄 **Calendar Integration** - Gedeeltelijk geïmplementeerd (mocked)
- 🔄 **Payment Integration** - Gedeeltelijk geïmplementeerd (mocked)

---

## 📅 **Calendar Integration (Google Calendar)**

### ✅ **Wat al werkt:**
- Mocked calendar functions in `main.py`
- Basic slot suggestion logic
- Timezone handling (Europe/Amsterdam)
- Slot booking structure

### 🔄 **Wat nog moet gebeuren:**

#### 1. **Google Calendar API Setup**
- [ ] **Service Account Configuration**
  - [ ] Google Cloud Project setup
  - [ ] Service account key generation
  - [ ] Calendar API enablement
  - [ ] Environment variables configuratie

#### 2. **Real Calendar Integration**
- [ ] **Replace mocked functions with real API calls:**
  - [ ] `suggest_slots()` - Echte beschikbare tijden ophalen
  - [ ] `book_slot()` - Echte afspraken maken in Google Calendar
  - [ ] `check_availability()` - Beschikbaarheid controleren

#### 3. **Calendar Logic Improvements**
- [ ] **Tutor Availability Management**
  - [ ] Working hours configuration
  - [ ] Break times handling
  - [ ] Holiday/absence management
  - [ ] Buffer time between lessons

#### 4. **Advanced Calendar Features**
- [ ] **Recurring Lessons**
  - [ ] Weekly/bi-weekly scheduling
  - [ ] Series booking logic
  - [ ] Cancellation handling

#### 5. **Calendar Notifications**
- [ ] **Automated Reminders**
  - [ ] 24h reminder emails
  - [ ] WhatsApp reminders
  - [ ] Calendar invites to students

---

## 💳 **Payment Integration (Stripe)**

### ✅ **Wat al werkt:**
- Mocked payment functions in `main.py`
- Payment webhook structure
- Basic payment flow logic
- Order ID generation

### 🔄 **Wat nog moet gebeuren:**

#### 1. **Stripe API Setup**
- [ ] **Stripe Account Configuration**
  - [ ] Stripe account setup
  - [ ] API keys generation
  - [ ] Webhook endpoint configuration
  - [ ] Environment variables configuratie

#### 2. **Real Payment Integration**
- [ ] **Replace mocked functions with real API calls:**
  - [ ] `create_payment_link()` - Echte Stripe checkout links
  - [ ] `verify_stripe_webhook()` - Echte webhook verificatie
  - [ ] `handle_payment_success()` - Echte betaling verwerking

#### 3. **Product Configuration**
- [ ] **Stripe Products Setup**
  - [ ] Standard lesson products (60min, 90min)
  - [ ] Weekend discount products
  - [ ] Package deals (2-lessen, 4-lessen)
  - [ ] Trial lesson (€0) product

#### 4. **Payment Flow Improvements**
- [ ] **Advanced Payment Features**
  - [ ] Multiple payment methods
  - [ ] Installment payments
  - [ ] Refund handling
  - [ ] Payment failure recovery

#### 5. **Financial Management**
- [ ] **Reporting & Analytics**
  - [ ] Payment tracking
  - [ ] Revenue reporting
  - [ ] Tax handling
  - [ ] Invoice generation

---

## 🔗 **Integration Points**

### 1. **Calendar ↔ Payment Flow**
- [ ] **Payment before booking**
  - [ ] Payment confirmation triggers calendar booking
  - [ ] Failed payment prevents booking
  - [ ] Refund triggers calendar cancellation

### 2. **Calendar ↔ Chatwoot Flow**
- [ ] **Booking confirmation**
  - [ ] Calendar event creates Chatwoot conversation update
  - [ ] Cancellation updates conversation status
  - [ ] Reminder messages via Chatwoot

### 3. **Payment ↔ Chatwoot Flow**
- [ ] **Payment status tracking**
  - [ ] Payment success updates conversation labels
  - [ ] Payment failure triggers retry flow
  - [ ] Refund updates conversation status

---

## 🛠️ **Technical Implementation**

### 1. **Environment Variables Needed**
```bash
# Google Calendar
GCAL_SERVICE_ACCOUNT_JSON="path/to/service-account.json"
GCAL_CALENDAR_ID="primary"

# Stripe
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
```

### 2. **New Dependencies**
```python
# requirements.txt additions
google-auth==2.23.0
google-auth-oauthlib==1.0.0
google-auth-httplib2==0.1.1
google-api-python-client==2.97.0
stripe==6.0.0
```

### 3. **File Structure**
```
tutorbot/
├── config/
│   ├── calendar_config.yaml    # Calendar settings
│   └── payment_config.yaml     # Payment settings
├── scripts/
│   ├── calendar_api.py         # Google Calendar client
│   └── payment_api.py          # Stripe client
└── tests/
    ├── test_calendar.py        # Calendar tests
    └── test_payment.py         # Payment tests
```

---

## 🧪 **Testing Strategy**

### 1. **Calendar Testing**
- [ ] **Unit Tests**
  - [ ] Slot availability calculation
  - [ ] Booking logic validation
  - [ ] Timezone handling

- [ ] **Integration Tests**
  - [ ] Real Google Calendar API calls
  - [ ] End-to-end booking flow
  - [ ] Error handling scenarios

### 2. **Payment Testing**
- [ ] **Unit Tests**
  - [ ] Payment link generation
  - [ ] Webhook verification
  - [ ] Payment status handling

- [ ] **Integration Tests**
  - [ ] Stripe test mode integration
  - [ ] Webhook processing
  - [ ] Payment flow completion

---

## 📋 **Implementation Priority**

### **Phase 1: Basic Integration (Week 1-2)**
1. Google Calendar API setup
2. Stripe API setup
3. Replace mocked functions with real API calls
4. Basic error handling

### **Phase 2: Advanced Features (Week 3-4)**
1. Advanced calendar features (recurring, availability)
2. Payment flow improvements
3. Integration point testing
4. Error recovery mechanisms

### **Phase 3: Production Ready (Week 5-6)**
1. Comprehensive testing
2. Documentation updates
3. Monitoring and logging
4. Performance optimization

---

## 🚨 **Critical Dependencies**

### **External Services**
- [ ] Google Cloud Platform account
- [ ] Stripe account
- [ ] SSL certificates for webhooks
- [ ] Domain configuration

### **Security Considerations**
- [ ] API key management
- [ ] Webhook signature verification
- [ ] Data encryption
- [ ] Access control

---

## 📊 **Success Metrics**

### **Calendar Integration**
- [ ] 100% booking success rate
- [ ] <5 second response time for slot queries
- [ ] Zero double-bookings
- [ ] 100% timezone accuracy

### **Payment Integration**
- [ ] 100% payment success rate
- [ ] <10 second payment processing
- [ ] Zero payment data loss
- [ ] 100% webhook reliability

---

## 🔄 **Next Steps**

1. **Immediate (This Week)**
   - [ ] Google Cloud Platform setup
   - [ ] Stripe account configuration
   - [ ] Environment variables setup

2. **Short Term (Next 2 Weeks)**
   - [ ] Basic API integration
   - [ ] Error handling implementation
   - [ ] Testing framework setup

3. **Medium Term (Next Month)**
   - [ ] Advanced features
   - [ ] Production deployment
   - [ ] Monitoring setup

---

*Last Updated: August 7, 2025*
*Status: Ready for Implementation* 