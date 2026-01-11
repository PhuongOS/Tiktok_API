#!/bin/bash

# TikTok Platform Microservices - Quick Start Script
# This script starts all services in the correct order

set -e  # Exit on error

echo "🚀 TikTok Platform Microservices - Quick Start"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi
print_success "Docker is running"

# Start databases and Redis
print_status "Starting databases and Redis..."
docker-compose up -d auth-db tiktok-db rules-db redis

# Wait for databases to be ready
print_status "Waiting for databases to be ready..."
sleep 5

# Check database health
print_status "Checking database health..."
docker exec auth_db pg_isready -U auth_user -d auth_db > /dev/null 2>&1 && print_success "auth-db is ready" || print_warning "auth-db not ready"
docker exec tiktok_db pg_isready -U tiktok_user -d tiktok_db > /dev/null 2>&1 && print_success "tiktok-db is ready" || print_warning "tiktok-db not ready"
docker exec rules_db pg_isready -U rules_user -d rules_db > /dev/null 2>&1 && print_success "rules-db is ready" || print_warning "rules-db not ready"

# Check Redis
docker exec redis_streams redis-cli ping > /dev/null 2>&1 && print_success "Redis is ready" || print_warning "Redis not ready"

echo ""
print_status "Starting microservices..."
echo ""

# Start Auth Service
print_status "Starting Auth Service (Port 8001)..."
cd services/auth-service
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment for Auth Service..."
    python3 -m venv venv
fi
chmod +x start.sh
./start.sh > /dev/null 2>&1 &
AUTH_PID=$!
print_success "Auth Service started (PID: $AUTH_PID)"
cd ../..

# Wait a bit
sleep 2

# Start TikTok Service
print_status "Starting TikTok Service (Port 8002)..."
cd services/tiktok-service
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment for TikTok Service..."
    python3 -m venv venv
fi
chmod +x start.sh
./start.sh > /dev/null 2>&1 &
TIKTOK_PID=$!
print_success "TikTok Service started (PID: $TIKTOK_PID)"
cd ../..

# Wait a bit
sleep 2

# Start Rule Engine Service
print_status "Starting Rule Engine Service (Port 8003)..."
cd services/rule-engine
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment for Rule Engine..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    deactivate
fi
source venv/bin/activate
export DATABASE_URL="postgresql+asyncpg://rules_user:rules_password@localhost:5434/rules_db"
uvicorn app.main:app --reload --port 8003 > /dev/null 2>&1 &
RULES_PID=$!
print_success "Rule Engine started (PID: $RULES_PID)"
deactivate
cd ../..

# Wait for services to start
print_status "Waiting for services to start..."
sleep 5

echo ""
echo "=============================================="
print_success "All services started successfully!"
echo "=============================================="
echo ""

# Display service URLs
echo "📊 Service URLs:"
echo ""
echo "  🔐 Auth Service:    http://localhost:8001/docs"
echo "  📺 TikTok Service:  http://localhost:8002/docs"
echo "  ⚙️  Rule Engine:     http://localhost:8003/docs"
echo ""

# Display health check
echo "🏥 Health Check:"
echo ""
sleep 2

# Check Auth Service
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    print_success "Auth Service is healthy"
else
    print_warning "Auth Service not responding yet"
fi

# Check TikTok Service
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    print_success "TikTok Service is healthy"
else
    print_warning "TikTok Service not responding yet"
fi

# Check Rule Engine
if curl -s http://localhost:8003/health > /dev/null 2>&1; then
    print_success "Rule Engine is healthy"
else
    print_warning "Rule Engine not responding yet"
fi

echo ""
echo "=============================================="
echo "🎉 Platform is ready!"
echo "=============================================="
echo ""

# Display process IDs
echo "📝 Process IDs:"
echo "  Auth Service:   $AUTH_PID"
echo "  TikTok Service: $TIKTOK_PID"
echo "  Rule Engine:    $RULES_PID"
echo ""

# Display stop instructions
echo "🛑 To stop all services:"
echo "  kill $AUTH_PID $TIKTOK_PID $RULES_PID"
echo "  docker-compose down"
echo ""

# Save PIDs to file for easy cleanup
echo "$AUTH_PID" > .pids
echo "$TIKTOK_PID" >> .pids
echo "$RULES_PID" >> .pids

print_success "PIDs saved to .pids file"
echo ""

# Display next steps
echo "📚 Next Steps:"
echo "  1. Open Swagger UI in your browser"
echo "  2. Register a user at http://localhost:8001/docs"
echo "  3. Connect to a TikTok LIVE at http://localhost:8002/docs"
echo "  4. Create automation rules at http://localhost:8003/docs"
echo ""

print_success "Happy automating! 🚀"
