#!/bin/bash

# TikTok Service Startup Script

echo "🚀 Starting TikTok Service..."

# Stop server (Ctrl+C nếu đang chạy)

# Đảm bảo đang ở đúng thư mục
cd "$(dirname "$0")"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://tiktok_user:tiktok_password@localhost:5433/tiktok_db"
export REDIS_URL="redis://localhost:6379"

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start server
echo "✅ Starting FastAPI server on port 8002..."
uvicorn app.main:app --reload --port 8002
