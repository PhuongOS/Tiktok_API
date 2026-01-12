#!/bin/bash

# Start IoT Worker Service

echo "Starting IoT Worker Service..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run service
python -m app.main
