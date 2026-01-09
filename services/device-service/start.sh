#!/bin/bash

# Device Service Startup Script

echo "🚀 Starting Device Service..."

# Navigate to service directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5435/device_db"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start the service
echo "✅ Starting Device Service on port 8004..."
uvicorn app.main:app --reload --port 8004 --host 0.0.0.0
