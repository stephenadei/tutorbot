#!/bin/bash

# TutorBot - Quick Data Wipe Script
# Automatically wipes all labels and custom attributes from Chatwoot

echo "🗑️  TutorBot - Quick Data Wipe"
echo "==============================="
echo "📅 $(date)"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: This script must be run from the tutorbot directory!"
    echo "   Current directory: $(pwd)"
    echo "   Expected: /home/stephen/projects/tutorbot"
    echo ""
    echo "💡 Solution:"
    echo "   cd /home/stephen/projects/tutorbot"
    echo "   ./wipe_all.sh"
    exit 1
fi

# Check if environment variables are set
if [ -z "$CW_URL" ] || [ -z "$CW_ACC_ID" ] || [ -z "$CW_ADMIN_TOKEN" ]; then
    echo "❌ Error: Missing environment variables!"
    echo "   Please set: CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN"
    echo ""
    echo "💡 Quick fix:"
    echo "   export CW_URL=https://crm.stephenadei.nl"
    echo "   export CW_ACC_ID=1"
    echo "   export CW_ADMIN_TOKEN=your_token_here"
    echo "   ./wipe_all.sh"
    exit 1
fi

echo "✅ Environment variables configured"
echo "🌐 CW_URL: $CW_URL"
echo "📊 CW_ACC_ID: $CW_ACC_ID"
echo "🔑 CW_ADMIN_TOKEN: ${CW_ADMIN_TOKEN:0:10}..."
echo ""

# Run the wipe script with automatic confirmation
echo "🚀 Starting automatic data wipe..."
echo ""

python3 scripts/wipe_all.py --auto-wipe

echo ""
echo "🎉 Data wipe completed!"
echo ""
echo "💡 Next steps:"
echo "   1. Run setup scripts for clean installation:"
echo "      python3 scripts/setup_all.py"
echo "   2. Test the bot with new conversations"
echo "   3. Verify all labels and attributes are created correctly" 