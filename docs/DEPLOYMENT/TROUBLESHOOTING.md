# 🔧 Troubleshooting Guide

Complete guide for diagnosing and resolving common TutorBot issues.

## 🎯 Overview

This guide covers common problems, their causes, and step-by-step solutions for the TutorBot application.

## 📋 Quick Diagnostic Checklist

Before diving into specific issues, run through this checklist:

- [ ] Environment variables are set correctly
- [ ] Docker containers are running
- [ ] Network connectivity is working
- [ ] API keys are valid and active
- [ ] Webhook endpoints are accessible
- [ ] Log files show no critical errors

## 🚨 Common Issues

### **Webhook Errors**

#### **TypeError: object of type 'NoneType' has no len()**
**Error**: `TypeError: object of type 'NoneType' has no len()` at line 2102

**Cause**: Webhook content can be `None`, causing length check to fail

**Solution**: Fixed in main.py line 2102
```python
# Before (causing error):
message_content = data.get("content", "")[:50] + "..." if len(data.get("content", "")) > 50 else data.get("content", "")

# After (fixed):
content = data.get("content", "")
message_content = content[:50] + "..." if content and len(content) > 50 else content or ""
```

**Prevention**: Always check for `None` values before string operations

### 1. Application Won't Start

#### Symptoms
- Container fails to start
- Application crashes on startup
- Port already in use errors

#### Diagnosis
```bash
# Check container status
docker-compose ps

# View startup logs
docker-compose logs tutorbot

# Check port usage
sudo netstat -tulpn | grep :5000

# Verify environment variables
docker-compose exec tutorbot env
```

#### Solutions

**Port Already in Use:**
```bash
# Kill process using port 5000
sudo lsof -ti:5000 | xargs kill -9

# Or use different port
docker-compose up -p 5001:5000
```

**Missing Environment Variables:**
```bash
# Export environment variables
source scripts/dev/export_env.sh

# Restart container
docker-compose restart tutorbot
```

**Python Dependencies:**
```bash
# Rebuild container
docker-compose build --no-cache

# Check requirements.txt
docker-compose exec tutorbot pip list
```

### 2. Chatwoot Integration Issues

#### Symptoms
- Messages not being sent
- Webhook errors
- API authentication failures

#### Diagnosis
```bash
# Test Chatwoot API connection
curl -H "api_access_token: $CW_ADMIN_TOKEN" \
  "$CW_URL/api/v1/accounts/$CW_ACC_ID/contacts"

# Check webhook configuration
curl -X POST https://your-domain.com/cw \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

# Verify HMAC signature
# Check Chatwoot webhook logs
```

#### Solutions

**Invalid API Token:**
```bash
# Regenerate API token in Chatwoot
# Update .env file with new token
source scripts/dev/export_env.sh
docker-compose restart tutorbot
```

**Webhook Not Receiving Events:**
```bash
# Check webhook URL in Chatwoot
# Verify HMAC secret matches
# Test webhook endpoint accessibility
```

**HMAC Verification Failures:**
```bash
# Regenerate HMAC secret
# Update both Chatwoot and .env
# Restart application
```

### 3. OpenAI Integration Issues

#### Symptoms
- Message analysis not working
- Prefill functionality disabled
- API rate limit errors

#### Diagnosis
```bash
# Test OpenAI API connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models"

# Check API key validity
python3 -c "import openai; openai.api_key='$OPENAI_API_KEY'; print(openai.Model.list())"
```

#### Solutions

**Invalid API Key:**
```bash
# Generate new OpenAI API key
# Update .env file
source scripts/dev/export_env.sh
docker-compose restart tutorbot
```

**Rate Limit Exceeded:**
```bash
# Check usage in OpenAI dashboard
# Implement rate limiting in code
# Consider upgrading API plan
```

**Model Not Available:**
```bash
# Check model availability
# Update OPENAI_MODEL in .env
# Restart application
```

### 4. Stripe Payment Issues

#### Symptoms
- Payment links not generated
- Webhook processing failures
- Payment verification errors

#### Diagnosis
```bash
# Test Stripe webhook endpoint
curl -X POST https://your-domain.com/webhook/payments \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

# Check Stripe dashboard for webhook failures
# Verify webhook secret
```

#### Solutions

**Invalid Webhook Secret:**
```bash
# Regenerate webhook secret in Stripe
# Update STRIPE_WEBHOOK_SECRET in .env
# Restart application
```

**Price ID Not Found:**
```bash
# Verify price IDs in Stripe dashboard
# Update price IDs in .env file
# Test payment link generation
```

**Webhook Not Receiving Events:**
```bash
# Check webhook endpoint URL
# Verify SSL certificate
# Test endpoint accessibility
```

### 5. Google Calendar Issues

#### Symptoms
- Slot suggestions not working
- Booking failures
- Calendar access denied

#### Diagnosis
```bash
# Test Google Calendar API
python3 -c "
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = '$GCAL_SERVICE_ACCOUNT_JSON'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

events = service.events().list(calendarId='$GCAL_CALENDAR_ID').execute()
print('Calendar access OK')
"
```

#### Solutions

**Service Account Issues:**
```bash
# Regenerate service account key
# Update JSON file in config/
# Verify calendar sharing
```

**Calendar Not Shared:**
```bash
# Share calendar with service account email
# Check calendar permissions
# Verify calendar ID
```

**API Quota Exceeded:**
```bash
# Check Google Cloud Console
# Implement rate limiting
# Consider quota increase
```

## 🔍 Debug Mode

### Enable Debug Mode
```bash
# Enable debug mode
./scripts/debug_toggle.sh on

# Check debug status
./scripts/debug_toggle.sh status

# View debug logs
docker-compose logs -f tutorbot
```

### Debug Information
Debug mode provides:
- Detailed API request/response logs
- Function execution traces
- Error stack traces
- Configuration validation

## 📊 Monitoring and Logs

### View Application Logs
```bash
# Real-time logs
docker-compose logs -f tutorbot

# Recent logs
docker-compose logs --tail=100 tutorbot

# Logs with timestamps
docker-compose logs -t tutorbot
```

### Check System Resources
```bash
# Container resource usage
docker stats

# Disk space
df -h

# Memory usage
free -h
```

### Monitor API Usage
```bash
# Check OpenAI usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/usage"

# Check Stripe webhook events
# (Check Stripe dashboard)
```

## 🛠️ Advanced Troubleshooting

### Network Connectivity
```bash
# Test external connectivity
docker-compose exec tutorbot ping google.com

# Test DNS resolution
docker-compose exec tutorbot nslookup api.openai.com

# Check firewall rules
sudo ufw status
```

### File Permissions
```bash
# Fix file permissions
chmod -R 755 .
chmod 600 .env

# Check ownership
ls -la

# Fix ownership if needed
sudo chown -R $USER:$USER .
```

### Database Issues
```bash
# Check database connectivity
docker-compose exec tutorbot python -c "
import requests
print('Database connection test')
"

# Verify database schema
# (If using external database)
```

## 🔄 Recovery Procedures

### Application Recovery
```bash
# Restart application
docker-compose restart tutorbot

# Full restart with rebuild
docker-compose down
docker-compose up --build -d

# Clean restart
docker-compose down -v
docker-compose up --build -d
```

### Configuration Recovery
```bash
# Restore from backup
cp .env.backup.$(date +%Y%m%d) .env

# Reset to defaults
cp env_example.txt .env

# Reconfigure environment
source scripts/dev/export_env.sh
```

### Data Recovery
```bash
# Backup current data
docker-compose exec tutorbot tar -czf backup.tar.gz /app/data

# Restore from backup
docker-compose exec tutorbot tar -xzf backup.tar.gz -C /app
```

## 📞 Getting Help

### Before Contacting Support
1. Check this troubleshooting guide
2. Review application logs
3. Test with debug mode enabled
4. Verify environment configuration
5. Check external service status

### Information to Provide
When seeking help, include:
- Error messages and logs
- Environment configuration (without secrets)
- Steps to reproduce the issue
- Expected vs actual behavior
- Recent changes made

### Support Channels
- **GitHub Issues**: For bugs and feature requests
- **Documentation Issues**: For documentation problems
- **Community**: For general questions and discussions

## 📚 Related Documentation

- **[Environment Setup](../SETUP/ENVIRONMENT.md)** - Environment configuration
- **[Docker Setup](../SETUP/DOCKER.md)** - Docker configuration
- **[Debug Scripts](../TESTING/DEBUG_SCRIPTS.md)** - Debug and configuration management
- **[Test Scenarios](../TESTING/TEST_SCENARIOS.md)** - Testing procedures

## 🔄 Maintenance

### Regular Maintenance Tasks
- [ ] Review logs weekly
- [ ] Check API usage monthly
- [ ] Update dependencies quarterly
- [ ] Test backup procedures monthly
- [ ] Review security settings quarterly

### Preventive Measures
- [ ] Monitor system resources
- [ ] Set up alerting for critical errors
- [ ] Regular security updates
- [ ] Backup configuration and data
- [ ] Test recovery procedures

---

**Last Updated**: August 2025  
**Version**: 2.0  
**Maintainer**: Stephen Adei 