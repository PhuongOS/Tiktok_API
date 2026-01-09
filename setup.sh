#!/bin/bash

echo "🚀 TikTok Platform Microservices - Setup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0.32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")"

# Function to setup a service
setup_service() {
    local service=$1
    echo -e "${BLUE}📦 Setting up $service...${NC}"
    
    cd "services/$service"
    
    # Activate venv and install dependencies
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    deactivate
    
    echo -e "${GREEN}✅ $service ready${NC}"
    cd ../..
}

# Start Docker services
echo "🐳 Starting Docker services (databases + Redis)..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Setup each microservice
setup_service "api-gateway"
setup_service "auth-service"
setup_service "tiktok-service"
setup_service "rule-engine"
setup_service "device-service"

echo ""
echo "========================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "📊 Services Status:"
docker-compose ps
echo ""
echo "🚀 Next Steps:"
echo "1. Start API Gateway:    cd services/api-gateway && ./start.sh"
echo "2. Start Auth Service:   cd services/auth-service && ./start.sh"
echo "3. Start TikTok Service: cd services/tiktok-service && ./start.sh"
echo "4. Start Rule Engine:    cd services/rule-engine && ./start.sh"
echo "5. Start Device Service: cd services/device-service && ./start.sh"
echo ""
echo "📍 Databases:"
echo "   - Auth DB:   localhost:5432"
echo "   - TikTok DB: localhost:5433"
echo "   - Rules DB:  localhost:5434"
echo "   - Device DB: localhost:5435"
echo "   - Redis:     localhost:6379"
echo ""
echo "========================================"
