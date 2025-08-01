#!/bin/bash

set -e

echo "🚀 Starting Tutorbot deployment..."

# Navigate to project directory
cd /home/stephen/tutorbot

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin master

# Install/update dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Setup systemd service if not exists
if [ ! -f /etc/systemd/system/tutorbot.service ]; then
    echo "🔧 Setting up systemd service..."
    sudo cp deploy/tutorbot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable tutorbot.service
fi

# Restart the service
echo "🔄 Restarting tutorbot service..."
sudo systemctl restart tutorbot.service

# Wait and check status
sleep 5
if sudo systemctl is-active --quiet tutorbot.service; then
    echo "✅ Tutorbot successfully deployed and running!"
    echo "📊 Service status:"
    sudo systemctl status tutorbot.service --no-pager -l
    echo "📋 Recent logs:"
    sudo journalctl -u tutorbot.service -n 10 --no-pager
else
    echo "❌ Failed to start tutorbot service"
    echo "📋 Service logs:"
    sudo journalctl -u tutorbot.service -n 20 --no-pager
    exit 1
fi 