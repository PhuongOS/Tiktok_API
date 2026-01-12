# IoT Worker Service

Real-time event processor that bridges TikTok Platform with ThingsBoard IoT devices.

## Architecture

```
Redis Streams → IoT Worker → MQTT → ThingsBoard → Devices
```

## Features

- Consume events from Redis Streams
- Process business logic (gift → device commands)
- Publish MQTT commands to ThingsBoard
- Handle device responses
- Retry logic with exponential backoff

## Tech Stack

- Python 3.10+
- paho-mqtt (MQTT client)
- redis-py (Redis Streams)
- asyncio (async processing)

## Configuration

See `config/config.yaml` for configuration options.

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python -m app.main
```
