# 🔄 Webhook System & Error Handling

## 🎯 Overview

The webhook system in TutorBot handles all incoming requests from Chatwoot and Stripe with sophisticated deduplication, error handling, and logging. This system ensures reliable message processing and prevents duplicate operations.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chatwoot      │    │   TutorBot      │    │     Stripe      │
│                 │    │                 │    │                 │
│  - Messages     │───▶│  - Webhook      │◄───│  - Payments     │
│  - Events       │    │  - Deduplication│    │  - Webhooks     │
│  - Status       │    │  - Error Handling│   │  - Events       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Processing    │
                       │                 │
                       │  - Message      │
                       │  - Payment      │
                       │  - Calendar     │
                       └─────────────────┘
```

## 🔄 Webhook Deduplication System

### **Purpose**
Prevents duplicate processing of the same webhook event, which can occur due to Chatwoot's retry mechanism or network issues.

### **Implementation** (Lines 2104-2123)

```python
# Create a unique webhook ID for idempotency
message_id = data.get("id") or data.get("message", {}).get("id")
webhook_id = f"{conversation_id}_{message_id}_{event}"

# Check if we've already processed this exact webhook
import hashlib
webhook_hash = hashlib.md5(webhook_id.encode()).hexdigest()

# Use a simple in-memory cache for webhook deduplication
if not hasattr(cw, 'processed_webhooks'):
    cw.processed_webhooks = set()

if webhook_hash in cw.processed_webhooks:
    print(f"🔄 Duplicate webhook detected: {webhook_id} - skipping")
    return "OK", 200

# Add to processed set (keep last 1000 webhooks)
cw.processed_webhooks.add(webhook_hash)
if len(cw.processed_webhooks) > 1000:
    cw.processed_webhooks.clear()  # Reset to prevent memory leaks
```

### **Key Features**

1. **Unique ID Generation**
   - Combines conversation_id, message_id, and event type
   - Ensures uniqueness across all webhook types

2. **Hash-Based Tracking**
   - Uses MD5 hash for efficient storage and comparison
   - Prevents memory bloat from long webhook IDs

3. **Memory Management**
   - Limits cache to 1000 webhooks
   - Automatic cleanup to prevent memory leaks
   - In-memory storage for fast access

4. **Idempotency**
   - Same webhook processed only once
   - Safe for retry scenarios
   - Maintains data consistency

## 🚨 Error Handling

### **Critical Error Fix** (Line 2102)

**Problem**: `TypeError: object of type 'NoneType' has no len()`

**Root Cause**: Webhook content could be `None`, causing length check to fail

**Solution**:
```python
# Before (causing error):
message_content = data.get("content", "")[:50] + "..." if len(data.get("content", "")) > 50 else data.get("content", "")

# After (fixed):
content = data.get("content", "")
message_content = content[:50] + "..." if content and len(content) > 50 else content or ""
```

### **Error Handling Strategy**

1. **Defensive Programming**
   - Always check for `None` values
   - Provide fallback values
   - Use safe string operations

2. **Graceful Degradation**
   - Continue processing when possible
   - Log errors for debugging
   - Return appropriate HTTP status codes

3. **Comprehensive Logging**
   - Log all webhook events
   - Include error details
   - Track processing status

## 📨 Webhook Types

### **Chatwoot Webhooks**

#### **Message Created** (Primary)
- **Event**: `message_created`
- **Type**: `incoming` (user messages only)
- **Processing**: Full message analysis and response

#### **Conversation Created**
- **Event**: `conversation_created`
- **Processing**: Initialize conversation attributes
- **Actions**: Set language, segment, labels

### **Stripe Webhooks**

#### **Payment Success**
- **Event**: `checkout.session.completed`
- **Processing**: Update payment status
- **Actions**: Create calendar events, send confirmations

#### **Payment Intent Succeeded**
- **Event**: `payment_intent.succeeded`
- **Processing**: Alternative payment success handling
- **Actions**: Same as checkout.session.completed

## 🔐 Security

### **Webhook Verification**

#### **Chatwoot Verification** (Line 2092)
```python
def verify_webhook(request):
    """Verify Chatwoot webhook signature"""
    if not SIG:
        print("⚠️ No HMAC secret configured - skipping verification")
        return True
    
    signature = request.headers.get('X-Chatwoot-Signature')
    if not signature:
        print("❌ No signature in webhook")
        return False
    
    # Verify HMAC signature
    expected_signature = hmac.new(
        SIG.encode(),
        request.get_data(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

#### **Stripe Verification** (Line 2049)
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

## 📊 Performance

### **Optimization Features**

1. **Fast Hash Lookup**
   - O(1) hash table access
   - Minimal memory footprint
   - Efficient duplicate detection

2. **Memory Management**
   - Automatic cleanup at 1000 webhooks
   - Prevents memory leaks
   - Maintains performance over time

3. **Early Returns**
   - Skip processing for duplicates
   - Skip non-user messages
   - Reduce unnecessary computation

### **Monitoring**

1. **Webhook Processing Rate**
   - Track webhooks per minute
   - Monitor duplicate rates
   - Alert on high error rates

2. **Memory Usage**
   - Monitor webhook cache size
   - Track memory growth
   - Alert on memory leaks

3. **Error Rates**
   - Track verification failures
   - Monitor processing errors
   - Alert on critical failures

## 🚀 Best Practices

### **Development**

1. **Always Handle None Values**
   ```python
   # Good
   content = data.get("content", "")
   if content:
       process_content(content)
   
   # Bad
   if len(data.get("content", "")) > 0:
       process_content(data["content"])
   ```

2. **Use Defensive Programming**
   ```python
   # Good
   conversation_id = data.get("conversation", {}).get("id", "unknown")
   
   # Bad
   conversation_id = data["conversation"]["id"]
   ```

3. **Comprehensive Logging**
   ```python
   print(f"📨 Webhook received: {event_str} | Type: {msg_type} | Conv:{conversation_id}")
   ```

### **Production**

1. **Monitor Webhook Health**
   - Track processing times
   - Monitor error rates
   - Alert on failures

2. **Regular Maintenance**
   - Review webhook logs
   - Clean up old data
   - Update security keys

3. **Backup and Recovery**
   - Backup webhook configurations
   - Test recovery procedures
   - Document incident response

## 🔧 Configuration

### **Environment Variables**

```bash
# Chatwoot Webhook
CW_HMAC_SECRET="your_hmac_secret"

# Stripe Webhook
STRIPE_WEBHOOK_SECRET="whsec_your_stripe_secret"
```

### **Webhook Endpoints** - Modular Route Architecture

```python
# Chatwoot webhook - modules/routes/webhook.py
@app.post("/cw")
def cw():
    # Main webhook handler - delegates to modules/handlers/conversation.py
    from modules.handlers.conversation import handle_message_created
    # ... webhook processing logic

# Stripe webhook - modules/routes/stripe.py  
@app.post("/webhook/payments")
def stripe_webhook():
    # Payment webhook handler - delegates to modules/handlers/payment.py
    from modules.handlers.payment import verify_stripe_webhook, handle_payment_success
    # ... payment processing logic
    
# Route registration in main.py
route_webhook.register(app)
route_stripe.register(app)
```

## 📝 Troubleshooting

### **Common Issues**

1. **Duplicate Processing**
   - Check webhook deduplication cache
   - Verify unique ID generation
   - Review retry mechanisms

2. **Verification Failures**
   - Check HMAC secret configuration
   - Verify webhook signatures
   - Review security settings

3. **Memory Issues**
   - Monitor webhook cache size
   - Check cleanup procedures
   - Review memory usage patterns

### **Debug Commands**

```python
# Check webhook cache size
print(f"Cache size: {len(cw.processed_webhooks)}")

# Check webhook processing
print(f"Webhook ID: {webhook_id}")
print(f"Hash: {webhook_hash}")

# Verify webhook data
print(f"Event: {event}")
print(f"Type: {msg_type}")
print(f"Content: {message_content}")
```

---

**💡 Tip**: The webhook system is critical for reliable operation. Always test webhook handling thoroughly and monitor for errors in production.
