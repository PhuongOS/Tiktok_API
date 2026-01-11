#!/bin/bash

# TikTok Platform Microservices - Stop All Services Script

set -e

echo "🛑 Stopping TikTok Platform Microservices..."
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Stop services using PIDs file
if [ -f ".pids" ]; then
    print_status "Stopping services from .pids file..."
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            echo "  ✓ Stopped process $pid"
        fi
    done < .pids
    rm .pids
    print_status "All service processes stopped"
else
    print_status "No .pids file found, stopping by port..."
    
    # Stop by port
    for port in 8001 8002 8003; do
        pid=$(lsof -ti:$port)
        if [ ! -z "$pid" ]; then
            kill $pid
            echo "  ✓ Stopped service on port $port (PID: $pid)"
        fi
    done
fi

# Stop Docker containers
print_status "Stopping Docker containers..."
docker-compose down

echo ""
echo "=============================================="
echo -e "${GREEN}✅ All services stopped successfully!${NC}"
echo "=============================================="
