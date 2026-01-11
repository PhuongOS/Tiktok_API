# Device Service

> Hardware device management and control microservice

**Version:** 0.1.0  
**Port:** 8004  
**Database:** PostgreSQL (device_db)  
**Communication:** WebSocket  
**Status:** 🚧 Not Started

---

## 📋 Overview

Device Service provides:
- Device registration and management
- Agent token generation
- Command queue management
- WebSocket communication with Edge Clients
- Device status monitoring

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Device Service                  │
│                                         │
│  ┌──────────────┐    ┌──────────────┐ │
│  │   WebSocket  │───▶│   Command    │ │
│  │    Server    │    │    Queue     │ │
│  └──────────────┘    └──────────────┘ │
│         │                     │        │
│         ▼                     ▼        │
│  ┌──────────────┐    ┌──────────────┐ │
│  │ Edge Client  │    │   Database   │ │
│  │ (Arduino/    │    │ (device_db)  │ │
│  │  ESP32)      │    └──────────────┘ │
│  └──────────────┘                     │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
device-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── device.py
│   │   └── command.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── device.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── devices.py
│   │   └── websocket.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── device_manager.py
│   │   └── command_queue.py
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
├── venv/
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema

### Devices Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `workspace_id` | UUID | Foreign key |
| `name` | String | Device name |
| `type` | Enum | arduino/esp32 |
| `status` | Enum | online/offline |
| `last_seen` | DateTime | Last connection |

### Agent Tokens Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `device_id` | UUID | Foreign key |
| `token_hash` | String | Hashed token |
| `created_at` | DateTime | Creation time |

### Command Queue Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `device_id` | UUID | Foreign key |
| `command` | String | Command type |
| `params` | JSONB | Command parameters |
| `status` | Enum | pending/sent/completed |

---

## 🛣️ API Endpoints

### POST `/api/devices`
Register a new device

### GET `/api/devices`
List devices

### POST `/api/devices/{id}/command`
Send command to device

### GET `/api/devices/{id}/status`
Get device status

### WS `/ws/device/{token}`
WebSocket connection for Edge Client

---

## 🔄 Changelog

### [Unreleased]

#### Planned
- ⏳ Device models
- ⏳ WebSocket handler
- ⏳ Command queue
- ⏳ Agent token management
- ⏳ API endpoints
- ⏳ Tests

---

**Last Updated:** 2026-01-07  
**Status:** 🚧 Not Started
