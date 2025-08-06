#!/bin/bash

# TutorBot - Confirmation Toggle Script
# Toggles confirmation mode on/off

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Confirmation configuration file
CONFIRM_CONFIG_FILE=".confirm_config"

# Function to show current confirmation status
show_confirm_status() {
    if [ -f "$CONFIRM_CONFIG_FILE" ]; then
        echo "✅ Current Confirmation Status:"
        echo "================================"
        cat "$CONFIRM_CONFIG_FILE"
    else
        echo "✅ Confirmation Status: DISABLED"
        echo "================================"
        echo "No confirmation configuration found."
    fi
    echo ""
}

# Function to enable confirmation mode
enable_confirm() {
    echo "✅ Enabling confirmation mode..."
    cat > "$CONFIRM_CONFIG_FILE" << EOF
CONFIRM_ENABLED=true
CONFIRM_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
CONFIRM_DESCRIPTION=Confirmation mode enabled
CONFIRM_LEVEL=standard
EOF
    echo "✅ Confirmation mode enabled"
    
    echo "🔄 Restarting TutorBot to apply confirmation settings..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose restart tutorbot
    else
        echo "⚠️ Docker Compose not found, manual restart may be needed"
    fi
}

# Function to disable confirmation mode
disable_confirm() {
    echo "✅ Disabling confirmation mode..."
    
    if [ -f "$CONFIRM_CONFIG_FILE" ]; then
        rm "$CONFIRM_CONFIG_FILE"
        echo "✅ Confirmation mode disabled"
    else
        echo "ℹ️ Confirmation mode was already disabled"
    fi
    
    echo "🔄 Restarting TutorBot to apply settings..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose restart tutorbot
    else
        echo "⚠️ Docker Compose not found, manual restart may be needed"
    fi
}

# Function to toggle confirmation mode
toggle_confirm() {
    if [ -f "$CONFIRM_CONFIG_FILE" ]; then
        echo "✅ Confirmation mode is currently ENABLED, disabling..."
        disable_confirm
    else
        echo "✅ Confirmation mode is currently DISABLED, enabling..."
        enable_confirm
    fi
}

# Main script logic
case "${1:-toggle}" in
    "on"|"enable")
        enable_confirm
        ;;
    "off"|"disable")
        disable_confirm
        ;;
    "status")
        show_confirm_status
        ;;
    "toggle")
        toggle_confirm
        ;;
    "help"|"-h"|"--help")
        echo "✅ TutorBot Confirmation Toggle Script"
        echo "====================================="
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  toggle    - Toggle confirmation mode on/off (default)"
        echo "  on        - Enable confirmation mode"
        echo "  off       - Disable confirmation mode"
        echo "  status    - Show current confirmation status"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # Toggle confirmation mode"
        echo "  $0 on           # Enable confirmation mode"
        echo "  $0 off          # Disable confirmation mode"
        echo "  $0 status       # Show confirmation status"
        echo ""
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

# Show status after any command (except help)
if [ "$1" != "help" ] && [ "$1" != "-h" ] && [ "$1" != "--help" ]; then
    echo ""
    show_confirm_status
fi 