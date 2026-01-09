#!/bin/bash

echo "🧪 Testing Auth Service Models"
echo "==============================="
echo ""

# Navigate to auth-service directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run model tests
echo "📦 Running model tests..."
pytest tests/test_models.py -v --cov=app/models --cov-report=term-missing

# Deactivate
deactivate

echo ""
echo "✅ Testing complete!"
