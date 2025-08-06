#!/bin/bash

# TutorBot - Environment Export Script
# Exports environment variables from .env file

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found in $(pwd)"
    echo "Please ensure you have a .env file with your environment variables."
    echo ""
    echo "You can create one from the template:"
    echo "  cp env_example.txt .env"
    echo "  # Then edit .env with your actual values"
    exit 1
fi

# Export environment variables
echo "🌍 Exporting environment variables from .env file..."
echo "=================================================="

# Read .env file and export variables
while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
        # Export the variable
        export "$line"
        echo "✅ Exported: ${line%%=*}"
    fi
done < .env

echo ""
echo "✅ Environment variables exported successfully!"
echo ""
echo "You can now run Python scripts directly:"
echo "  python3 main.py"
echo "  python3 scripts/setup_all.py"
echo "  python3 tests/run_tests.py"
echo ""
echo "To verify exported variables:"
echo "  env | grep CW_"
echo "  env | grep OPENAI_"
echo "  env | grep STRIPE_" 