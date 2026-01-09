# TikTok Service

> TikTok LIVE integration microservice

**Version:** 0.1.0  
**Port:** 8002  
**Database:** PostgreSQL (tiktok_db)  
**Event Bus:** Redis Streams  
**Status:** 🚧 Not Started

---

## 📋 Overview

TikTok Service provides:
- TikTok LIVE connection management
- Real-time event processing (comments, gifts, likes)
- Event publishing to Redis Streams
- Livestream session management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         TikTok Service                  │
│                                         │
│  ┌──────────────┐    ┌──────────────┐ │
│  │  TikTok      │───▶│   Database   │ │
│  │  LIVE Client │    │  (tiktok_db) │ │
│  └──────────────┘    └──────────────┘ │
│         │                              │
│         ▼                              │
│  ┌──────────────┐                     │
│  │    Redis     │                     │
│  │   Streams    │                     │
│  │  (Publisher) │                     │
│  └──────────────┘                     │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
tiktok-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── livestream.py      # Livestream model
│   │   └── event.py           # Event log model
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   └── livestream.py      # Livestream schemas
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   └── livestreams.py     # /api/livestreams/* endpoints
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── tiktok_client.py   # TikTok LIVE wrapper
│   │   └── event_publisher.py # Redis publisher
│   │
│   └── utils/                  # Utilities
│       └── __init__.py
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_tiktok_client.py
│
├── venv/                       # Virtual environment
├── requirements.txt            # Dependencies
└── README.md                  # This file
```

---

## 🗄️ Database Schema

### Livestreams Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `workspace_id` | UUID | Foreign key |
| `tiktok_username` | String | TikTok username |
| `room_id` | String | TikTok room ID |
| `status` | Enum | connecting/live/ended |
| `connected_at` | DateTime | Connection time |
| `disconnected_at` | DateTime | Disconnection time |

### Events Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `livestream_id` | UUID | Foreign key |
| `event_type` | String | comment/gift/like/join |
| `user_id` | String | TikTok user ID |
| `username` | String | TikTok username |
| `payload` | JSONB | Event data |
| `timestamp` | DateTime | Event time |

---

## 🛣️ API Endpoints

### POST `/api/livestreams/connect`
Connect to a TikTok LIVE stream

### POST `/api/livestreams/{id}/disconnect`
Disconnect from a stream

### GET `/api/livestreams`
List active livestreams

### GET `/api/livestreams/{id}/events`
Get event stream (SSE)

---

## 📊 Event Types

### Published to Redis Streams

- `tiktok.comment` - User comments
- `tiktok.gift` - Gift events
- `tiktok.like` - Like events
- `tiktok.join` - User joins
- `tiktok.follow` - Follow events
- `tiktok.share` - Share events

---

## 🔄 Changelog

### [Unreleased]

#### Planned
- ⏳ TikTok LIVE client wrapper
- ⏳ Event handlers
- ⏳ Redis Streams publisher
- ⏳ Livestream models
- ⏳ API endpoints
- ⏳ Tests

---

**Last Updated:** 2026-01-07  
**Status:** 🚧 Not Started
