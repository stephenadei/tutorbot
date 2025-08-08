#!/bin/bash

# TutorBot - Quick Contact Wipe Script
# Automatically wipes all contacts and conversations from Chatwoot

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🗑️  TutorBot - Quick Contact Wipe"
echo "=================================="
echo "📅 $(date)"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: This script must be run from the tutorbot directory!"
    echo "   Current directory: $(pwd)"
    echo "   Expected: /home/stephen/tutorbot"
    echo ""
    echo "💡 Solution:"
    echo "   cd /home/stephen/tutorbot"
    echo "   ./wipe.sh"
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
    echo "   ./wipe.sh"
    exit 1
fi

echo "✅ Environment variables configured"
echo "🌐 CW_URL: $CW_URL"
echo "📊 CW_ACC_ID: $CW_ACC_ID"
echo "🔑 CW_ADMIN_TOKEN: ${CW_ADMIN_TOKEN:0:10}..."
echo ""

# Run the wipe script with automatic confirmation
echo "🚀 Starting automatic contact wipe..."
echo ""

# Run the wipe script with automatic confirmation
python3 scripts/data/wipe_contacts.py --auto-wipe

echo ""
echo "🎉 Contact wipe completed!"
echo ""
echo "💡 Next steps:"
echo "   1. Test the bot with new conversations"
echo "   2. Check if language detection works"
echo "   3. Verify info menu translations"
echo "   4. Test the back-to-menu functionality" 