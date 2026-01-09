# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- ✅ Project structure with 5 microservices
- ✅ Docker Compose for databases (4x PostgreSQL + Redis)
- ✅ Virtual environments for each service
- ✅ Testing framework (pytest + fixtures)
- ✅ Security utilities (Argon2 + JWT)
- ✅ Comprehensive documentation
- ✅ README for each service

### In Progress
- 🚧 Auth Service implementation
- 🚧 Database migrations

### Planned
- ⏳ TikTok Service
- ⏳ Rule Engine
- ⏳ Device Service
- ⏳ API Gateway
- ⏳ Frontend (React)
- ⏳ Edge Client (Arduino/ESP32)

---

## [0.1.0] - 2026-01-07

### Infrastructure Setup

#### Added
- Project structure for microservices architecture
- Docker Compose configuration
  - 4 PostgreSQL databases (auth, tiktok, rules, device)
  - Redis for event bus and caching
  - Health checks for all services
- Virtual environments for each service
  - Isolated dependencies
  - No global Python pollution
- Automated setup script (`setup.sh`)
- Database management script (`db-service.sh`)

#### Documentation
- Main README with quick start guide
- Microservices architecture overview
- Implementation plan (10-12 weeks)
- Testing guide with examples
- Docker setup guide
- Quick reference guides

#### Testing
- pytest configuration
- Shared test fixtures
- 9 unit tests for security utilities (100% coverage)
- Coverage reporting (HTML + terminal)
- Test automation script (`test-all.sh`)

#### Auth Service
- FastAPI app skeleton
- Database configuration (SQLAlchemy async)
- Security utilities
  - Argon2 password hashing
  - JWT token generation/validation
- Unit tests (9 tests, 92% coverage)
- Service README

#### TikTok Service
- Project structure
- Requirements.txt with TikTokLive library
- Service README template

#### Rule Engine
- Project structure
- Requirements.txt
- Service README template

#### Device Service
- Project structure
- Requirements.txt with WebSocket support
- Service README template

#### API Gateway
- Project structure
- Requirements.txt
- Service README template

---

## Service Status

| Service | Version | Status | Progress |
|---------|---------|--------|----------|
| **Auth Service** | 0.1.0 | 🚧 In Development | 30% |
| **TikTok Service** | 0.0.1 | 📝 Planned | 10% |
| **Rule Engine** | 0.0.1 | 📝 Planned | 10% |
| **Device Service** | 0.0.1 | 📝 Planned | 10% |
| **API Gateway** | 0.0.1 | 📝 Planned | 5% |

---

## Dependencies

### Core
- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose

### Python Packages
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Alembic 1.13.1
- TikTokLive 6.3.0
- pytest 7.4.4
- argon2-cffi 23.1.0
- python-jose 3.3.0

---

## Breaking Changes

None yet.

---

## Migration Guide

### From Monolith to Microservices

If you have the old monolithic version:

1. **Backup your data**
   ```bash
   docker-compose exec postgres pg_dump -U user db > backup.sql
   ```

2. **Stop old services**
   ```bash
   docker-compose down
   ```

3. **Setup new microservices**
   ```bash
   cd tiktok-platform-microservices
   ./setup.sh
   ```

4. **Migrate data** (service by service)
   - Auth data → auth_db
   - TikTok data → tiktok_db
   - Rules → rules_db
   - Devices → device_db

---

## Known Issues

### Current
None.

### Resolved
None yet.

---

## Security Updates

None yet.

---

## Performance Improvements

None yet.

---

## Contributors

- Development Team

---

## Links

- [GitHub Repository](#)
- [Documentation](#)
- [Issue Tracker](#)

---

**Last Updated:** 2026-01-07  
**Next Release:** TBD
