# Rule Engine Service

> Event processing and rule execution microservice

**Version:** 0.1.0  
**Port:** 8003  
**Database:** PostgreSQL (rules_db)  
**Event Bus:** Redis Streams (Subscriber)  
**Status:** 🚧 Not Started

---

## 📋 Overview

Rule Engine provides:
- Rule creation and management
- Event matching logic
- Action execution
- Cooldown management
- Analytics tracking

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Rule Engine Service             │
│                                         │
│  ┌──────────────┐    ┌──────────────┐ │
│  │    Redis     │───▶│ Rule Matcher │ │
│  │   Streams    │    └──────────────┘ │
│  │ (Subscriber) │            │         │
│  └──────────────┘            ▼         │
│                     ┌──────────────┐  │
│                     │   Action     │  │
│                     │  Executor    │  │
│                     └──────────────┘  │
│                              │         │
│                              ▼         │
│                     ┌──────────────┐  │
│                     │   Database   │  │
│                     │  (rules_db)  │  │
│                     └──────────────┘  │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
rule-engine/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rule.py
│   │   └── execution.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── rule.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── rules.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rule_matcher.py
│   │   ├── action_executor.py
│   │   └── event_subscriber.py
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

### Rules Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `livestream_id` | UUID | Foreign key |
| `name` | String | Rule name |
| `trigger_config` | JSONB | Trigger conditions |
| `actions` | JSONB | Actions to execute |
| `cooldown_seconds` | Integer | Cooldown period |
| `enabled` | Boolean | Active status |

### Rule Executions Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `rule_id` | UUID | Foreign key |
| `event_id` | UUID | Event that triggered |
| `executed_at` | DateTime | Execution time |
| `result` | JSONB | Execution result |

---

## 🛣️ API Endpoints

### POST `/api/rules`
Create a new rule

### GET `/api/rules`
List rules

### PUT `/api/rules/{id}`
Update rule

### DELETE `/api/rules/{id}`
Delete rule

### GET `/api/rules/{id}/analytics`
Get rule analytics

---

## 🔄 Changelog

### [Unreleased]

#### Planned
- ⏳ Rule models
- ⏳ Rule matching engine
- ⏳ Redis Streams subscriber
- ⏳ Action executor
- ⏳ API endpoints
- ⏳ Tests

---

**Last Updated:** 2026-01-07  
**Status:** 🚧 Not Started
