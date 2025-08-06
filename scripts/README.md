# TutorBot Scripts Directory

This directory contains all the shell scripts for managing the TutorBot application.

## 📁 Script Categories

### 🔧 Development Scripts
- **`dev.sh`** - Development environment setup and management

### 🧹 Data Management Scripts
- **`wipe.sh`** - Wipe all contacts and conversations
- **`wipe_all.sh`** - Wipe all labels and attributes

### 🔍 Debug Management Scripts
- **`debug_toggle.sh`** - Main debug toggle script with multiple modes
- **`debug_on.sh`** - Quick enable debug mode
- **`debug_off.sh`** - Quick disable debug mode
- **`debug_private.sh`** - Enable private debug mode
- **`debug_console.sh`** - Enable console debug mode
- **`debug_status.sh`** - Show debug status

### ✅ Confirmation Management Scripts
- **`confirm_toggle.sh`** - Main confirmation toggle script
- **`confirm_on.sh`** - Quick enable confirmation mode
- **`confirm_off.sh`** - Quick disable confirmation mode
- **`confirm_status.sh`** - Show confirmation status

### 🌍 Environment Management Scripts
- **`export_env.sh`** - Export environment variables from .env file

## 🚀 Quick Commands

### Development
```bash
./scripts/dev.sh
```

### Data Management
```bash
./scripts/wipe.sh          # Wipe contacts
./scripts/wipe_all.sh      # Wipe all data
```

### Debug Management
```bash
./scripts/debug_toggle.sh  # Toggle debug mode
./scripts/debug_on.sh      # Enable debug
./scripts/debug_off.sh     # Disable debug
./scripts/debug_status.sh  # Show debug status
```

### Confirmation Management
```bash
./scripts/confirm_toggle.sh  # Toggle confirmation mode
./scripts/confirm_on.sh      # Enable confirmation
./scripts/confirm_off.sh     # Disable confirmation
./scripts/confirm_status.sh  # Show confirmation status
```

### Environment Management
```bash
./scripts/export_env.sh     # Export environment variables
```

## 🎯 Usage Examples

### Debug Mode Management
```bash
# Check current debug status
./scripts/debug_toggle.sh status

# Enable public debug mode
./scripts/debug_toggle.sh public

# Enable private debug mode for admin-only debugging
./scripts/debug_toggle.sh private

# Disable debug mode
./scripts/debug_toggle.sh off

# Quick toggle
./scripts/debug_toggle.sh
```

### Confirmation Mode Management
```bash
# Check current confirmation status
./scripts/confirm_toggle.sh status

# Enable confirmation mode
./scripts/confirm_toggle.sh on

# Disable confirmation mode
./scripts/confirm_toggle.sh off

# Quick toggle
./scripts/confirm_toggle.sh
```

### Data Management
```bash
# Wipe all contacts and conversations
./scripts/wipe.sh

# Wipe all data (contacts, conversations, labels, attributes)
./scripts/wipe_all.sh
```

### Environment Management
```bash
# Export environment variables
./scripts/export_env.sh

# Verify exported variables
env | grep CW_
env | grep OPENAI_
env | grep STRIPE_
```

## 🔧 Script Permissions

All scripts are executable. If you encounter permission issues, run:
```bash
chmod +x scripts/*.sh
```

## 📋 Script Dependencies

### Required Files
- `.env` - Environment variables file (for export_env.sh)
- `docker-compose.yml` - Docker Compose configuration (for restart functionality)

### Required Environment Variables
- `CW_URL` - Chatwoot URL
- `CW_ACC_ID` - Chatwoot Account ID
- `CW_ADMIN_TOKEN` - Chatwoot Admin Token

## 🎉 Benefits of Organization

### ✅ Better Structure
- All scripts in one place
- Easy to find and manage
- Clear categorization

### ✅ Maintainability
- Centralized script management
- Easy to add new scripts
- Consistent naming conventions

### ✅ Documentation
- Clear README for each category
- Usage examples for all scripts
- Dependency information

## 🚀 Integration with Main Application

The scripts are designed to work with the main TutorBot application:

### Debug Configuration
Scripts create configuration files that the main app can read:
- `.debug_config` - Debug mode settings
- `.confirm_config` - Confirmation mode settings

### Docker Integration
Scripts automatically restart the TutorBot container when settings change:
```bash
docker-compose restart tutorbot
```

### Environment Variables
The export script makes environment variables available for Python scripts:
```bash
source scripts/export_env.sh
python3 main.py
```

## 🔍 Troubleshooting

### Permission Denied
```bash
chmod +x scripts/*.sh
```

### Script Not Found
Make sure you're running from the project root:
```bash
cd /home/stephen/tutorbot
./scripts/script_name.sh
```

### Docker Compose Not Found
Scripts will show a warning if Docker Compose is not available, but will still work for configuration changes.

### Environment Variables Not Set
Use the export script:
```bash
./scripts/export_env.sh
```

## 📚 Related Documentation

- **Main Application**: `../main.py`
- **Configuration**: `../config/`
- **Docker Setup**: `../docker-compose.yml`, `../Dockerfile`
- **Environment**: `../.env`, `../env_example.txt`
- **Help System**: `../help.sh` 