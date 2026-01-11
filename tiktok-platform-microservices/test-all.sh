#!/bin/bash

echo "🧪 TikTok Platform - Running All Tests"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run tests for a service
run_service_tests() {
    local service=$1
    echo -e "${BLUE}📦 Testing $service...${NC}"
    
    cd "services/$service"
    
    if [ ! -d "tests" ]; then
        echo -e "${RED}⚠️  No tests found for $service${NC}"
        cd ../..
        return
    fi
    
    # Activate venv and run tests
    source venv/bin/activate
    
    # Run pytest with coverage
    pytest tests/ -v --cov=app --cov-report=term-missing 2>&1 | tee test_output.txt
    
    # Check exit code
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✅ $service tests passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ $service tests failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    
    deactivate
    cd ../..
    echo ""
}

# Ensure Docker services are running
echo "🐳 Checking Docker services..."
docker-compose ps | grep -q "Up" || {
    echo "Starting Docker services..."
    docker-compose up -d
    sleep 5
}

echo ""

# Run tests for each service
run_service_tests "api-gateway"
run_service_tests "auth-service"
run_service_tests "tiktok-service"
run_service_tests "rule-engine"
run_service_tests "device-service"

# Summary
echo "======================================"
echo -e "${BLUE}📊 Test Summary${NC}"
echo "======================================"
echo "Total Services: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
