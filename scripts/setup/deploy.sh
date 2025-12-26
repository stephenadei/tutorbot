#!/bin/bash

echo "🚀 Starting TutorBot deployment..."

# Navigate to project directory
cd /home/stephen/projects/tutorbot

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin master

# Restart Docker container
echo "🔄 Restarting Docker container..."
docker compose down
docker compose up -d

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Check container status
echo "📊 Checking container status..."
if docker compose ps | grep -q "Up"; then
    echo "✅ Container is running"
else
    echo "❌ Container failed to start"
    echo "📋 Container logs:"
    docker compose logs
    exit 1
fi

# Test health endpoint
echo "🏥 Testing health endpoint..."
health_response=$(curl -s http://localhost:8000/health)
if [[ $health_response == *"healthy"* ]]; then
    echo "✅ Health check passed: $health_response"
else
    echo "❌ Health check failed: $health_response"
    echo "📋 Recent logs:"
    docker compose logs --tail=20
    exit 1
fi

# Test webhook endpoint
echo "🔗 Testing webhook endpoint..."
webhook_response=$(curl -s -X POST http://localhost:8000/cw -H "Content-Type: application/json" -d '{"test": "data"}')
if [[ $webhook_response == *"Unauthorized"* ]] || [[ $webhook_response == "" ]]; then
    echo "✅ Webhook endpoint responding (Unauthorized expected without proper signature)"
else
    echo "⚠️ Unexpected webhook response: $webhook_response"
fi

echo ""
echo "🎉 TutorBot successfully deployed and running!"
echo "📊 Container status:"
docker compose ps
echo ""
echo "📋 Recent logs:"
docker compose logs --tail=10
echo ""
echo "🌐 Health endpoint: http://localhost:8000/health"
echo "🔗 Webhook endpoint: http://localhost:8000/cw"
