# 🌍 Environment Configuration Guide

Complete guide for setting up the TutorBot environment variables and configuration.

## 🎯 Overview

This guide covers all environment variables needed for TutorBot, including Chatwoot integration, Stripe payments, Google Calendar, and OpenAI services.

## 📋 Prerequisites

Before configuring environment variables, ensure you have:
- Chatwoot instance with API access
- Stripe account (for payments)
- Google Cloud Project with Calendar API
- OpenAI API key
- Domain with SSL certificate (for webhooks)

## 🔧 Environment Variables Setup

### 1. Create Environment File

Copy the example file and configure your values:

```bash
cp env_example.txt .env
```

### 2. Chatwoot Configuration

**Required for core functionality:**

```bash
# Chatwoot instance URL
CW_URL=https://crm.stephenadei.nl

# Account ID (usually 1 for single-tenant)
CW_ACC_ID=1

# Bot token for sending messages
CW_TOKEN=your_bot_token_here

# Admin token for API operations
CW_ADMIN_TOKEN=your_admin_token_here

# HMAC secret for webhook verification
CW_HMAC_SECRET=your_hmac_secret_here
```

**How to get these values:**
1. **CW_URL**: Your Chatwoot instance URL
2. **CW_ACC_ID**: Usually 1, check in Chatwoot admin
3. **CW_TOKEN**: Create bot user in Chatwoot and get access token
4. **CW_ADMIN_TOKEN**: Create admin user and get access token
5. **CW_HMAC_SECRET**: Generate random string for webhook security

### 3. Stripe Configuration

**Required for payment processing:**

```bash
# Webhook secret from Stripe
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Price IDs for different segments
STANDARD_PRICE_ID_60=price_your_standard_60min_price_id
STANDARD_PRICE_ID_90=price_your_standard_90min_price_id
WEEKEND_PRICE_ID_60=price_your_weekend_60min_price_id
WEEKEND_PRICE_ID_90=price_your_weekend_90min_price_id
```

**How to get these values:**
1. Create products in Stripe Dashboard
2. Configure webhook endpoint: `https://your-domain.com/webhook/payments`
3. Copy webhook secret from Stripe
4. Copy price IDs from product configuration

### 4. Google Calendar Configuration

**Required for scheduling functionality:**

```bash
# Service account JSON file path
GCAL_SERVICE_ACCOUNT_JSON=/app/config/gcal-service-account.json

# Calendar ID (usually 'primary')
GCAL_CALENDAR_ID=primary
```

**How to get these values:**
1. Create Google Cloud Project
2. Enable Google Calendar API
3. Create Service Account
4. Download JSON key file
5. Place in `config/gcal-service-account.json`
6. Share calendar with service account email

### 5. OpenAI Configuration

**Required for message analysis and prefill:**

```bash
# OpenAI API key
OPENAI_API_KEY=sk-proj-your_openai_api_key_here

# Model to use (recommended: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini
```

**How to get these values:**
1. Create OpenAI account
2. Generate API key
3. Choose appropriate model (gpt-4o-mini recommended)

### 6. System Configuration

**General system settings:**

```bash
# Timezone for scheduling
TZ=Europe/Amsterdam

# Flask environment
FLASK_ENV=production
```

## 🔒 Security Considerations

### Environment File Security
- Never commit `.env` file to version control
- Use `.env.example` for templates
- Set proper file permissions: `chmod 600 .env`

### API Key Security
- Rotate API keys regularly
- Use least privilege principle
- Monitor API usage
- Set up alerts for unusual activity

### Webhook Security
- Use HMAC verification for all webhooks
- Validate webhook signatures
- Use HTTPS for all webhook endpoints
- Monitor webhook failures

## 🧪 Environment Validation

### Test Environment Setup
```bash
# Export environment variables
source scripts/dev/export_env.sh

# Validate configuration
python3 scripts/validate_structure.py

# Test connections
python3 scripts/test_chatwoot_api.py
```

### Validation Checklist
- [ ] All required variables are set
- [ ] Chatwoot API is accessible
- [ ] Stripe webhook is configured
- [ ] Google Calendar is accessible
- [ ] OpenAI API is working
- [ ] Webhook endpoints are reachable

## 🔄 Environment Management

### Development vs Production
```bash
# Development
FLASK_ENV=development
DEBUG_MODE=console

# Production
FLASK_ENV=production
DEBUG_MODE=disabled
```

### Environment-Specific Configs
```bash
# Development
CW_URL=https://dev-chatwoot.example.com
STRIPE_WEBHOOK_SECRET=whsec_dev_secret

# Production
CW_URL=https://crm.stephenadei.nl
STRIPE_WEBHOOK_SECRET=whsec_prod_secret
```

### Configuration Updates
```bash
# Update environment variables
source scripts/dev/export_env.sh

# Restart application
docker-compose restart tutorbot

# Verify changes
docker-compose logs tutorbot
```

## 🐛 Troubleshooting

### Common Issues

#### Missing Environment Variables
```bash
# Check if variables are set
env | grep CW_
env | grep STRIPE_
env | grep OPENAI_

# Export if missing
source scripts/dev/export_env.sh
```

#### API Connection Issues
```bash
# Test Chatwoot connection
curl -H "api_access_token: $CW_ADMIN_TOKEN" \
  "$CW_URL/api/v1/accounts/$CW_ACC_ID/contacts"

# Test OpenAI connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models"
```

#### Webhook Issues
```bash
# Check webhook endpoint
curl -X POST https://your-domain.com/cw \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

# Verify HMAC signature
# (Check Chatwoot webhook logs)
```

### Debug Mode
```bash
# Enable debug mode
./scripts/debug_toggle.sh on

# Check debug status
./scripts/debug_toggle.sh status

# View debug logs
docker-compose logs -f tutorbot
```

## 📚 Related Documentation

- **[Chatwoot Setup](CHATWOOT_SETUP.md)** - Detailed Chatwoot configuration
- **[Quick Start Guide](QUICK_START.md)** - Quick setup instructions
- **[Docker Setup](../DEPLOYMENT/DOCKER.md)** - Docker configuration
- **[Troubleshooting](../DEPLOYMENT/TROUBLESHOOTING.md)** - Common issues and solutions

## 🔄 Maintenance

### Regular Tasks
- [ ] Rotate API keys quarterly
- [ ] Update webhook secrets annually
- [ ] Monitor API usage monthly
- [ ] Review security settings quarterly
- [ ] Test webhook endpoints weekly

### Backup Configuration
```bash
# Backup environment file
cp .env .env.backup.$(date +%Y%m%d)

# Restore from backup
cp .env.backup.20250806 .env
```

---

**Last Updated**: August 2025  
**Version**: 2.0  
**Maintainer**: Stephen Adei 