#!/bin/bash

echo "🚀 Starting Auth Service"
echo "======================="
echo ""

# Navigate to auth-service directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://auth_user:auth_password@localhost:5432/auth_db"
export SECRET_KEY="dev-secret-key-change-in-production"
export JWT_SECRET_KEY="dev-jwt-secret-change-in-production"

# Check if database is running
echo "🐳 Checking database..."
if ! docker ps | grep -q auth-db; then
    echo "⚠️  Database not running. Starting Docker services..."
    cd ../..
    docker-compose up -d auth-db redis_streams
    cd services/auth-service
    sleep 3
fi

# Run migrations
echo "📊 Running database migrations..."
alembic upgrade head

# Start server
echo ""
echo "✅ Starting FastAPI server on http://localhost:8001"
echo "📚 Swagger UI: http://localhost:8001/docs"
echo "📖 ReDoc: http://localhost:8001/redoc"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --port 8001
