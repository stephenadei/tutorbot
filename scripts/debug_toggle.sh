#!/bin/bash

# TutorBot - Debug Toggle Script
# Toggles debug mode on/off

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Debug configuration file
DEBUG_CONFIG_FILE=".debug_config"

# Function to show current debug status
show_debug_status() {
    if [ -f "$DEBUG_CONFIG_FILE" ]; then
        echo "🔍 Current Debug Status:"
        echo "=========================="
        cat "$DEBUG_CONFIG_FILE"
    else
        echo "🔍 Debug Status: DISABLED"
        echo "=========================="
        echo "No debug configuration found."
    fi
    echo ""
}

# Function to enable debug mode
enable_debug() {
    local mode="${1:-public}"
    
    case $mode in
        "public"|"on")
            echo "🔍 Enabling PUBLIC debug mode..."
            cat > "$DEBUG_CONFIG_FILE" << EOF
DEBUG_MODE=public
DEBUG_ENABLED=true
DEBUG_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DEBUG_DESCRIPTION=Public debug mode enabled
DEBUG_LEVEL=verbose
EOF
            echo "✅ Public debug mode enabled"
            ;;
        "private")
            echo "🔍 Enabling PRIVATE debug mode..."
            cat > "$DEBUG_CONFIG_FILE" << EOF
DEBUG_MODE=private
DEBUG_ENABLED=true
DEBUG_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DEBUG_DESCRIPTION=Private debug mode enabled
DEBUG_LEVEL=verbose
EOF
            echo "✅ Private debug mode enabled"
            ;;
        "console")
            echo "🔍 Enabling CONSOLE debug mode..."
            cat > "$DEBUG_CONFIG_FILE" << EOF
DEBUG_MODE=console
DEBUG_ENABLED=true
DEBUG_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DEBUG_DESCRIPTION=Console debug mode enabled
DEBUG_LEVEL=verbose
EOF
            echo "✅ Console debug mode enabled"
            ;;
        *)
            echo "❌ Invalid debug mode: $mode"
            echo "Valid modes: public, private, console"
            exit 1
            ;;
    esac
    
    echo "🔄 Restarting TutorBot to apply debug settings..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose restart tutorbot
    else
        echo "⚠️ Docker Compose not found, manual restart may be needed"
    fi
}

# Function to disable debug mode
disable_debug() {
    echo "🔍 Disabling debug mode..."
    
    if [ -f "$DEBUG_CONFIG_FILE" ]; then
        rm "$DEBUG_CONFIG_FILE"
        echo "✅ Debug mode disabled"
    else
        echo "ℹ️ Debug mode was already disabled"
    fi
    
    echo "🔄 Restarting TutorBot to apply settings..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose restart tutorbot
    else
        echo "⚠️ Docker Compose not found, manual restart may be needed"
    fi
}

# Function to toggle debug mode
toggle_debug() {
    if [ -f "$DEBUG_CONFIG_FILE" ]; then
        echo "🔍 Debug mode is currently ENABLED, disabling..."
        disable_debug
    else
        echo "🔍 Debug mode is currently DISABLED, enabling..."
        enable_debug "public"
    fi
}

# Main script logic
case "${1:-toggle}" in
    "on"|"enable")
        enable_debug "public"
        ;;
    "off"|"disable")
        disable_debug
        ;;
    "public")
        enable_debug "public"
        ;;
    "private")
        enable_debug "private"
        ;;
    "console")
        enable_debug "console"
        ;;
    "status")
        show_debug_status
        ;;
    "toggle")
        toggle_debug
        ;;
    "help"|"-h"|"--help")
        echo "🔍 TutorBot Debug Toggle Script"
        echo "================================"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  toggle    - Toggle debug mode on/off (default)"
        echo "  on        - Enable public debug mode"
        echo "  off       - Disable debug mode"
        echo "  public    - Enable public debug mode"
        echo "  private   - Enable private debug mode"
        echo "  console   - Enable console debug mode"
        echo "  status    - Show current debug status"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # Toggle debug mode"
        echo "  $0 on           # Enable debug mode"
        echo "  $0 off          # Disable debug mode"
        echo "  $0 status       # Show debug status"
        echo "  $0 private      # Enable private debug mode"
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
    show_debug_status
fi 