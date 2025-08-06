# TutorBot Debug & Confirmation Scripts - Summary

## 🎯 Overview

I've created a complete set of debug and confirmation management scripts for your TutorBot application. These scripts allow you to easily toggle debug modes and confirmation settings without manually editing configuration files.

## 📁 Files Created

### Debug Management Scripts
- **`debug_toggle.sh`** - Main debug toggle script with multiple modes
- **`debug_on.sh`** - Quick enable debug mode
- **`debug_off.sh`** - Quick disable debug mode
- **`debug_private.sh`** - Enable private debug mode
- **`debug_console.sh`** - Enable console debug mode
- **`debug_status.sh`** - Show debug status

### Confirmation Management Scripts
- **`confirm_toggle.sh`** - Main confirmation toggle script
- **`confirm_on.sh`** - Quick enable confirmation mode
- **`confirm_off.sh`** - Quick disable confirmation mode
- **`confirm_status.sh`** - Show confirmation status

### Environment Management Scripts
- **`export_env.sh`** - Export environment variables from .env file

## 🚀 How to Use

### Debug Commands

#### Basic Debug Toggle
```bash
# Toggle debug mode on/off
./debug_toggle.sh

# Or use the simple command
debug
```

#### Specific Debug Commands
```bash
# Enable debug mode
./debug_toggle.sh on
./debug_on.sh

# Disable debug mode
./debug_toggle.sh off
./debug_off.sh

# Enable specific debug modes
./debug_toggle.sh public    # Public debug mode
./debug_toggle.sh private   # Private debug mode
./debug_toggle.sh console   # Console debug mode
./debug_private.sh
./debug_console.sh

# Show debug status
./debug_toggle.sh status
./debug_status.sh
debugstatus
```

#### Debug Modes Available
- **Public**: Debug information visible to users
- **Private**: Debug information only visible to admins
- **Console**: Debug information sent to console/logs

### Confirmation Commands

#### Basic Confirmation Toggle
```bash
# Toggle confirmation mode on/off
./confirm_toggle.sh

# Or use the simple command
confirm
```

#### Specific Confirmation Commands
```bash
# Enable confirmation mode
./confirm_toggle.sh on
./confirm_on.sh

# Disable confirmation mode
./confirm_toggle.sh off
./confirm_off.sh

# Show confirmation status
./confirm_toggle.sh status
./confirm_status.sh
confirmstatus
```

### Environment Commands

#### Export Environment Variables
```bash
# Export environment variables from .env file
./export_env.sh

# Or use the simple command
exportenv
```

## 🔧 Configuration Files

### Debug Configuration (`.debug_config`)
When debug mode is enabled, a configuration file is created:
```
DEBUG_MODE=public
DEBUG_ENABLED=true
DEBUG_TIMESTAMP=2025-08-06 22:53:26
DEBUG_DESCRIPTION=Public debug mode enabled
DEBUG_LEVEL=verbose
```

### Confirmation Configuration (`.confirm_config`)
When confirmation mode is enabled, a configuration file is created:
```
CONFIRM_ENABLED=true
CONFIRM_TIMESTAMP=2025-08-06 22:53:26
CONFIRM_DESCRIPTION=Confirmation mode enabled
CONFIRM_LEVEL=standard
```

## 🎯 Features

### Debug Script Features
- ✅ **Multiple Debug Modes**: Public, private, console
- ✅ **Automatic Restart**: Restarts TutorBot when settings change
- ✅ **Status Tracking**: Shows current debug configuration
- ✅ **Timestamp Tracking**: Records when debug was enabled/disabled
- ✅ **Configuration Persistence**: Settings saved to files
- ✅ **Error Handling**: Graceful handling of missing Docker Compose

### Confirmation Script Features
- ✅ **Toggle Functionality**: Easy on/off switching
- ✅ **Automatic Restart**: Restarts TutorBot when settings change
- ✅ **Status Tracking**: Shows current confirmation configuration
- ✅ **Timestamp Tracking**: Records when confirmation was enabled/disabled
- ✅ **Configuration Persistence**: Settings saved to files

### Environment Script Features
- ✅ **Safe Export**: Exports variables from .env file
- ✅ **Error Checking**: Validates .env file exists
- ✅ **Clear Feedback**: Shows which variables were exported
- ✅ **Usage Instructions**: Provides helpful next steps

## 🔍 Usage Examples

### Debug Mode Management
```bash
# Check current debug status
./debug_toggle.sh status

# Enable public debug mode
./debug_toggle.sh public

# Enable private debug mode for admin-only debugging
./debug_toggle.sh private

# Disable debug mode
./debug_toggle.sh off

# Quick toggle
./debug_toggle.sh
```

### Confirmation Mode Management
```bash
# Check current confirmation status
./confirm_toggle.sh status

# Enable confirmation mode
./confirm_toggle.sh on

# Disable confirmation mode
./confirm_toggle.sh off

# Quick toggle
./confirm_toggle.sh
```

### Environment Management
```bash
# Export environment variables
./export_env.sh

# Verify exported variables
env | grep CW_
env | grep OPENAI_
env | grep STRIPE_
```

## 🛠️ Integration with Main Application

### Reading Debug Configuration
Your main application can read the debug configuration:
```python
import os

def is_debug_enabled():
    """Check if debug mode is enabled"""
    return os.path.exists('.debug_config')

def get_debug_mode():
    """Get current debug mode"""
    if not is_debug_enabled():
        return None
    
    with open('.debug_config', 'r') as f:
        for line in f:
            if line.startswith('DEBUG_MODE='):
                return line.split('=')[1].strip()
    return None
```

### Reading Confirmation Configuration
```python
def is_confirm_enabled():
    """Check if confirmation mode is enabled"""
    return os.path.exists('.confirm_config')
```

## 🎉 Benefits

### For Development
- ✅ **Quick Debugging**: Enable/disable debug mode instantly
- ✅ **Multiple Modes**: Different debug levels for different needs
- ✅ **No Manual Editing**: No need to edit configuration files manually
- ✅ **Automatic Restart**: Changes applied immediately

### For Production
- ✅ **Safe Toggling**: Easy to enable/disable without errors
- ✅ **Status Tracking**: Always know current configuration
- ✅ **Audit Trail**: Timestamps for when settings changed
- ✅ **Graceful Handling**: Works even if Docker Compose unavailable

### For Maintenance
- ✅ **Consistent Interface**: All scripts follow same pattern
- ✅ **Clear Feedback**: Always know what's happening
- ✅ **Error Prevention**: Validates inputs and configurations
- ✅ **Documentation**: Built-in help for all commands

## 🚀 Quick Reference

### Debug Commands
```bash
debug              # Toggle debug mode
debugon            # Enable debug mode
debugoff           # Disable debug mode
debugprivate       # Enable private debug mode
debugconsole       # Enable console debug mode
debugstatus        # Show debug status
```

### Confirmation Commands
```bash
confirm            # Toggle confirmation mode
confirmon          # Enable confirmation mode
confirmoff         # Disable confirmation mode
confirmstatus      # Show confirmation status
```

### Environment Commands
```bash
exportenv          # Export environment variables
```

## 🔧 Technical Details

### Script Permissions
All scripts are executable:
```bash
chmod +x debug_*.sh
chmod +x confirm_*.sh
chmod +x export_env.sh
```

### Docker Integration
Scripts automatically restart TutorBot when settings change:
```bash
docker-compose restart tutorbot
```

### Error Handling
- Validates .env file exists before export
- Handles missing Docker Compose gracefully
- Provides clear error messages
- Shows helpful usage instructions

## 🎯 What This Achieves

### Complete Debug Management
Your TutorBot now has **comprehensive debug management** that allows you to:
- ✅ Enable/disable debug modes instantly
- ✅ Switch between different debug levels
- ✅ Track debug configuration changes
- ✅ Restart application automatically
- ✅ Monitor debug status easily

### Production-Ready Confirmation System
The confirmation system provides:
- ✅ Easy confirmation mode toggling
- ✅ Configuration persistence
- ✅ Status tracking
- ✅ Automatic application restart

### Environment Management
The environment export system offers:
- ✅ Safe environment variable export
- ✅ Clear feedback and validation
- ✅ Helpful usage instructions
- ✅ Error handling for missing files

## 🚀 Next Steps

1. **Test the debug commands**:
   ```bash
   ./debug_toggle.sh status
   ./debug_toggle.sh on
   ./debug_toggle.sh off
   ```

2. **Test the confirmation commands**:
   ```bash
   ./confirm_toggle.sh status
   ./confirm_toggle.sh on
   ./confirm_toggle.sh off
   ```

3. **Test environment export**:
   ```bash
   ./export_env.sh
   ```

4. **Integrate with your main application**:
   - Read debug configuration in your Flask app
   - Adjust logging based on debug mode
   - Use confirmation settings for user interactions

The debug and confirmation management system is now ready to help you develop and maintain your TutorBot application more effectively! 🎯 