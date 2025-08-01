#!/bin/bash

# Development script for tutorbot
# Usage: ./dev.sh [restart|rebuild|logs|clean]

case "$1" in
    "restart")
        echo "🔄 Restarting bot..."
        docker-compose restart
        ;;
    "rebuild")
        echo "🔨 Rebuilding bot..."
        docker-compose down && docker-compose up --build -d
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f tutorbot
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        docker-compose down
        docker system prune -f
        docker-compose up --build -d
        ;;
    *)
        echo "Usage: ./dev.sh [restart|rebuild|logs|clean]"
        echo ""
        echo "Commands:"
        echo "  restart  - Restart bot (for env changes)"
        echo "  rebuild  - Rebuild and restart (for deps)"
        echo "  logs     - Show live logs"
        echo "  clean    - Clean and rebuild everything"
        ;;
esac 