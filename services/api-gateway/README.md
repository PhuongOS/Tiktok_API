# API Gateway

> Single entry point for all microservices

**Version:** 0.1.0  
**Port:** 8000  
**Cache:** Redis  
**Status:** 🚧 Not Started

---

## 📋 Overview

API Gateway provides:
- Request routing to microservices
- JWT validation
- Rate limiting
- CORS configuration
- API documentation aggregation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│            API Gateway                  │
│                                         │
│  ┌──────────────┐    ┌──────────────┐ │
│  │   Routing    │───▶│     JWT      │ │
│  │    Logic     │    │  Validation  │ │
│  └──────────────┘    └──────────────┘ │
│         │                              │
│         ▼                              │
│  ┌──────────────┐                     │
│  │     Rate     │                     │
│  │   Limiting   │                     │
│  └──────────────┘                     │
└─────────────────────────────────────────┘
         │
    ┌────┴────┬────┬────┬────┐
    │         │    │    │    │
┌───▼───┐ ┌──▼──┐ ┌▼──┐ ┌▼──┐
│ Auth  │ │TikTok│ │Rule│ │Dev│
│Service│ │Service│ │Eng│ │Svc│
└───────┘ └─────┘ └───┘ └───┘
```

---

## 📁 Project Structure

```
api-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── rate_limit.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── proxy.py
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

## 🛣️ Route Mapping

| Path | Target Service | Port |
|------|----------------|------|
| `/api/auth/*` | Auth Service | 8001 |
| `/api/livestreams/*` | TikTok Service | 8002 |
| `/api/rules/*` | Rule Engine | 8003 |
| `/api/devices/*` | Device Service | 8004 |

---

## 🔄 Changelog

### [Unreleased]

#### Planned
- ⏳ Routing logic
- ⏳ JWT validation middleware
- ⏳ Rate limiting
- ⏳ CORS configuration
- ⏳ Tests

---

**Last Updated:** 2026-01-07  
**Status:** 🚧 Not Started
