# 💳 Stripe Payment Integration

## 🎯 Overview

TutorBot integrates with Stripe for secure online payments, handling lesson bookings, trial sessions, and urgent appointments. The system creates payment links, processes webhooks, and manages payment status in Chatwoot conversations.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TutorBot      │    │     Stripe      │    │   Chatwoot      │
│                 │    │                 │    │                 │
│  - Payment      │───▶│  - Checkout     │───▶│  - Status       │
│  - Links        │    │  - Sessions     │    │  - Updates      │
│  - Webhooks     │◄───│  - Webhooks     │◄───│  - Labels       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 💰 Payment Flow

### **1. Payment Link Creation**

#### **Function**: `create_payment_link()` (Line 2033)
```python
def create_payment_link(segment, minutes, order_id, conversation_id, student_name, service, audience, program):
    """Create Stripe payment link"""
    try:
        # Determine price based on segment and duration
        if segment == "urgent":
            price_id = WEEKEND_PRICE_ID_60 if minutes == 60 else WEEKEND_PRICE_ID_90
        else:
            price_id = STANDARD_PRICE_ID_60 if minutes == 60 else STANDARD_PRICE_ID_90
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'ideal'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"https://crm.stephenadei.nl/conversations/{conversation_id}",
            cancel_url=f"https://crm.stephenadei.nl/conversations/{conversation_id}",
            metadata={
                'order_id': order_id,
                'conversation_id': conversation_id,
                'student_name': student_name,
                'service': service,
                'audience': audience,
                'program': program,
                'minutes': minutes
            }
        )
        
        return session.url
    except Exception as e:
        print(f"❌ Error creating payment link: {e}")
        return None
```

#### **Price Structure**
- **Standard Rates**: €60/hour (weekdays)
- **Weekend Rates**: €75/hour (weekends)
- **Urgent Sessions**: €120/2-hour (immediate booking)

### **2. Payment Request Creation**

#### **Function**: `create_payment_request()` (Line 4918)
```python
def create_payment_request(cid, contact_id, lang):
    """Create payment request"""
    # Get contact and conversation attributes
    contact_attrs = get_contact_attrs(contact_id)
    conv_attrs = get_conv_attrs(cid)
    
    # Generate order ID
    order_id = f"order_{int(datetime.now().timestamp())}"
    
    # Create payment link
    payment_link = create_payment_link(
        segment=contact_attrs.get("segment", "standard"),
        minutes=conv_attrs.get("lesson_minutes", 60),
        order_id=order_id,
        conversation_id=cid,
        student_name=contact_attrs.get("name", "Student"),
        service=conv_attrs.get("service", "tutoring"),
        audience=conv_attrs.get("audience", "student"),
        program=conv_attrs.get("program", "general")
    )
    
    if payment_link:
        # Update conversation attributes
        set_conv_attrs(cid, {
            "order_id": order_id,
            "payment_status": "pending",
            "payment_link": payment_link
        })
        
        # Add payment labels
        add_conv_labels(cid, ["payment:pending"])
        
        # Send payment link
        send_text_with_duplicate_check(cid, t("payment_link", lang, link=payment_link))
        return True
    
    return False
```

### **3. Webhook Processing**

#### **Function**: `stripe_webhook()` (Line 4950)
```python
@app.post("/webhook/payments")
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    if not verify_stripe_webhook(payload, signature):
        return "Unauthorized", 401
    
    event = stripe.Webhook.construct_event(
        payload, signature, STRIPE_WEBHOOK_SECRET
    )
    
    event_type = event['type']
    
    if event_type == "checkout.session.completed":
        handle_payment_success(event)
    elif event_type == "payment_intent.succeeded":
        handle_payment_success(event)
    
    return "OK", 200
```

### **4. Payment Success Handling**

#### **Function**: `handle_payment_success()` (Line 4969)
```python
def handle_payment_success(event):
    """Handle successful payment"""
    try:
        # Extract metadata
        metadata = event['data']['object']['metadata']
        conversation_id = int(metadata.get('conversation_id'))
        order_id = metadata.get('order_id')
        student_name = metadata.get('student_name', 'Student')
        
        # Update conversation attributes
        set_conv_attrs(conversation_id, {
            "payment_status": "paid",
            "payment_date": datetime.now().isoformat(),
            "has_paid_lesson": True
        })
        
        # Update contact attributes
        contact_id = get_contact_id_from_conversation(conversation_id)
        if contact_id:
            set_contact_attrs(contact_id, {
                "has_paid_lesson": True,
                "customer_since": datetime.now().isoformat()
            })
        
        # Update conversation labels
        remove_conv_labels(conversation_id, ["payment:pending"])
        add_conv_labels(conversation_id, ["payment:paid", "status:booked"])
        
        # Add payment note
        payment_note = f"✅ Payment received for {student_name} - Order: {order_id}"
        send_text_with_duplicate_check(conversation_id, payment_note)
        
        print(f"✅ Payment processed: {order_id} for conversation {conversation_id}")
        
    except Exception as e:
        print(f"❌ Error processing payment success: {e}")
```

## 🔐 Security

### **Webhook Verification**

#### **Function**: `verify_stripe_webhook()` (Line 2049)
```python
def verify_stripe_webhook(payload, signature):
    """Verify Stripe webhook signature"""
    if not STRIPE_WEBHOOK_SECRET:
        print("⚠️ No Stripe webhook secret configured")
        return False
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )
        return True
    except Exception as e:
        print(f"❌ Stripe webhook verification failed: {e}")
        return False
```

### **Security Features**
- **Webhook Signature Verification**: Ensures webhooks come from Stripe
- **Metadata Validation**: Validates payment metadata
- **Error Handling**: Graceful handling of payment failures
- **Logging**: Comprehensive payment event logging

## 📊 Payment Status Management

### **Conversation Attributes**
```python
# Payment-related attributes
{
    "order_id": "order_1234567890",
    "payment_status": "pending|paid|failed",
    "payment_date": "2025-01-15T10:30:00",
    "payment_link": "https://checkout.stripe.com/...",
    "lesson_minutes": 60,
    "service": "tutoring",
    "audience": "student",
    "program": "general"
}
```

### **Contact Attributes**
```python
# Customer-related attributes
{
    "has_paid_lesson": True,
    "customer_since": "2025-01-15T10:30:00",
    "segment": "standard|urgent|premium"
}
```

### **Conversation Labels**
```python
# Payment status labels
["payment:pending"]  # Payment link sent
["payment:paid"]     # Payment received
["status:booked"]    # Lesson confirmed
```

## 🎯 Payment Scenarios

### **1. Trial Lesson**
- **Payment**: Not required
- **Flow**: Direct booking without payment
- **Status**: `trial_lesson`

### **2. Regular Lesson**
- **Payment**: Required before booking
- **Flow**: Payment link → Payment → Calendar booking
- **Status**: `definitief`

### **3. Urgent Session**
- **Payment**: Required immediately
- **Flow**: Direct payment link → Payment → Immediate booking
- **Status**: `urgent`

### **4. Weekend Lesson**
- **Payment**: Higher rate
- **Flow**: Weekend pricing → Payment → Booking
- **Status**: `weekend`

## 🔧 Configuration

### **Environment Variables**
```bash
# Stripe Configuration
STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
STANDARD_PRICE_ID_60="price_standard_60min"
STANDARD_PRICE_ID_90="price_standard_90min"
WEEKEND_PRICE_ID_60="price_weekend_60min"
WEEKEND_PRICE_ID_90="price_weekend_90min"
```

### **Stripe Products Setup**
```python
# Standard Rates (Weekdays)
STANDARD_PRICE_ID_60 = "price_1ABC123..."  # €60/hour
STANDARD_PRICE_ID_90 = "price_1DEF456..."  # €90/1.5hour

# Weekend Rates
WEEKEND_PRICE_ID_60 = "price_1GHI789..."   # €75/hour
WEEKEND_PRICE_ID_90 = "price_1JKL012..."   # €112.50/1.5hour
```

## 📝 Error Handling

### **Common Payment Errors**

1. **Payment Link Creation Failure**
   ```python
   try:
       payment_link = create_payment_link(...)
       if not payment_link:
           send_text_with_duplicate_check(cid, "❌ Payment system temporarily unavailable")
   except Exception as e:
       print(f"❌ Payment link creation failed: {e}")
   ```

2. **Webhook Verification Failure**
   ```python
   if not verify_stripe_webhook(payload, signature):
       print("❌ Invalid webhook signature")
       return "Unauthorized", 401
   ```

3. **Payment Processing Error**
   ```python
   try:
       handle_payment_success(event)
   except Exception as e:
       print(f"❌ Payment processing failed: {e}")
       # Send notification to admin
   ```

### **Recovery Procedures**

1. **Failed Payment Links**
   - Retry payment link creation
   - Send alternative payment instructions
   - Contact customer for manual payment

2. **Webhook Failures**
   - Check webhook endpoint availability
   - Verify webhook secret configuration
   - Review Stripe dashboard for failed webhooks

3. **Payment Status Mismatch**
   - Manual payment status verification
   - Stripe dashboard reconciliation
   - Contact customer for payment confirmation

## 📊 Monitoring

### **Key Metrics**
- **Payment Success Rate**: Track successful vs failed payments
- **Payment Processing Time**: Monitor webhook response times
- **Payment Link Usage**: Track payment link generation and usage
- **Error Rates**: Monitor payment-related errors

### **Alerts**
- **Payment Failures**: Alert on webhook verification failures
- **Processing Errors**: Alert on payment processing exceptions
- **High Error Rates**: Alert when error rate exceeds threshold

## 🚀 Best Practices

### **Development**
1. **Test in Stripe Test Mode**: Always test with test API keys
2. **Validate Webhook Signatures**: Never skip webhook verification
3. **Handle All Payment States**: Include pending, paid, and failed states
4. **Log Payment Events**: Comprehensive logging for debugging

### **Production**
1. **Monitor Payment Health**: Regular monitoring of payment flows
2. **Backup Payment Data**: Regular backups of payment configurations
3. **Update Security Keys**: Regular rotation of webhook secrets
4. **Test Payment Recovery**: Regular testing of payment recovery procedures

---

**💡 Tip**: Always test payment flows thoroughly in Stripe test mode before going live. Monitor webhook delivery and payment processing in production.
