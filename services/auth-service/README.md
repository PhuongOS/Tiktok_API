# Auth Service

> Authentication & Authorization microservice for TikTok LIVE Platform

**Version:** 1.0.0  
**Port:** 8001  
**Database:** PostgreSQL (auth_db)  
**Status:** 🚧 In Development

---

## 📋 Overview

Auth Service provides:
- User registration & login
- JWT-based authentication
- Workspace management (multi-tenancy)
- Role-based access control (RBAC)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Auth Service                │
│                                     │
│  ┌──────────┐      ┌────────────┐ │
│  │   API    │─────▶│  Database  │ │
│  │ Endpoints│      │ (auth_db)  │ │
│  └──────────┘      └────────────┘ │
│       │                            │
│       ▼                            │
│  ┌──────────┐                     │
│  │ Security │                     │
│  │  Utils   │                     │
│  └──────────┘                     │
└─────────────────────────────────────┘
```

---

## 📁 Project Structure

```
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   └── workspace.py       # Workspace models
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py            # Auth request/response schemas
│   │   └── workspace.py       # Workspace schemas
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py            # /api/auth/* endpoints
│   │   └── workspaces.py      # /api/workspaces/* endpoints
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── security.py        # Password hashing, JWT
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── conftest.py            # Shared fixtures
│   ├── test_security.py       # Security utils tests
│   ├── test_auth.py           # Auth endpoints tests
│   └── integration/           # Integration tests
│
├── alembic/                    # Database migrations
│   ├── versions/
│   │   ├── 001_create_users.py
│   │   └── 002_create_workspaces.py
│   └── env.py
│
├── venv/                       # Virtual environment
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── alembic.ini                # Alembic configuration
└── README.md                  # This file
```

---

## 🗄️ Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | String | Unique, indexed |
| `password_hash` | String | Argon2 hashed password |
| `is_active` | Boolean | Account status |
| `is_verified` | Boolean | Email verification status |
| `created_at` | DateTime | Account creation time |
| `updated_at` | DateTime | Last update time |

### Workspaces Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `name` | String | Workspace name |
| `owner_id` | UUID | Foreign key to users |
| `plan_tier` | Enum | free/pro/enterprise |
| `created_at` | DateTime | Creation time |
| `updated_at` | DateTime | Last update time |

### Workspace Members Table

| Column | Type | Description |
|--------|------|-------------|
| `workspace_id` | UUID | Foreign key (composite PK) |
| `user_id` | UUID | Foreign key (composite PK) |
| `role` | Enum | owner/admin/operator/viewer |
| `joined_at` | DateTime | Join time |

---

## 🛣️ API Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new user

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-01-07T10:00:00Z"
}
```

---

#### POST `/api/auth/login`
Login and receive JWT token

**Request:** (form data)
```
username: user@example.com
password: securepassword123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

#### GET `/api/auth/me`
Get current user information

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-01-07T10:00:00Z"
}
```

---

### Workspaces

#### POST `/api/workspaces`
Create a new workspace

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "name": "My Workspace",
  "plan_tier": "free"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "My Workspace",
  "owner_id": "user-uuid",
  "plan_tier": "free",
  "created_at": "2026-01-07T10:00:00Z"
}
```

---

#### GET `/api/workspaces`
List user's workspaces

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "My Workspace",
    "owner_id": "user-uuid",
    "plan_tier": "free",
    "created_at": "2026-01-07T10:00:00Z"
  }
]
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ (running via Docker)
- Virtual environment

### Setup

```bash
# Navigate to service directory
cd services/auth-service

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://auth_user:auth_password@localhost:5432/auth_db"
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret"

# Run database migrations
alembic upgrade head

# Start the service
uvicorn app.main:app --reload --port 8001
```

### Access API Documentation

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

---

## 🧪 Testing

### Run All Tests

```bash
# Activate venv
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Security utils tests
pytest tests/test_security.py -v

# Auth endpoints tests
pytest tests/test_auth.py -v

# Integration tests
pytest tests/integration/ -v
```

### Test Coverage

**Current:** 92%

| Module | Coverage |
|--------|----------|
| `app/utils/security.py` | 100% |
| `app/models/` | TBD |
| `app/api/` | TBD |

---

## 🔐 Security

### Password Security
- **Algorithm:** Argon2 (industry standard)
- **Minimum length:** 8 characters
- **Storage:** Only hashed passwords stored

### JWT Tokens
- **Algorithm:** HS256
- **Expiration:** 30 minutes
- **Secret:** From environment variable

### Database Security
- **SQL Injection:** Protected by SQLAlchemy ORM
- **Workspace Isolation:** Enforced at query level

---

## 📊 Performance

### Benchmarks

| Endpoint | Latency (p95) | Target |
|----------|---------------|--------|
| Register | TBD | <500ms |
| Login | TBD | <300ms |
| Get User | TBD | <200ms |

---

## 🔄 Changelog

### [Unreleased]

#### Added
- ✅ Security utilities (password hashing, JWT)
- ✅ Database configuration
- ✅ FastAPI app skeleton
- ✅ Unit tests for security utils (9 tests, 100% coverage)
- ✅ Testing infrastructure (pytest, fixtures)

#### In Progress
- 🚧 User & Workspace models
- 🚧 Database migrations
- 🚧 Auth API endpoints
- 🚧 Workspace API endpoints

#### Planned
- ⏳ Email verification
- ⏳ Password reset
- ⏳ OAuth2 integration
- ⏳ Rate limiting
- ⏳ Audit logging

---

## 🐛 Known Issues

None currently.

---

## 📝 Development Notes

### Adding New Endpoints

1. Create Pydantic schema in `app/schemas/`
2. Add endpoint in `app/api/`
3. Include router in `app/main.py`
4. Write tests in `tests/`
5. Update this README

### Database Migrations

```bash
# Create new migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | App secret key | Required |
| `JWT_SECRET_KEY` | JWT signing key | Required |
| `JWT_EXPIRATION_MINUTES` | Token expiration | 30 |

---

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Update changelog
5. Submit PR

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Argon2 Documentation](https://argon2-cffi.readthedocs.io/)

---

**Last Updated:** 2026-01-07  
**Maintainer:** Development Team  
**Status:** 🚧 Active Development
