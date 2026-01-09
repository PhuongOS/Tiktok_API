# Testing Quick Reference

## 🚀 Quick Commands

### Run All Tests
```bash
./test-all.sh
```

### Run Tests for Specific Service
```bash
# Auth Service
cd services/auth-service
source venv/bin/activate
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Run Specific Test File
```bash
pytest tests/test_auth.py -v
```

### Run Specific Test
```bash
pytest tests/test_auth.py::TestUserRegistration::test_register_user_success -v
```

### Run Tests by Marker
```bash
# Only unit tests
pytest tests/ -m unit

# Only integration tests
pytest tests/ -m integration

# Skip slow tests
pytest tests/ -m "not slow"
```

## 📊 Coverage

### Generate HTML Report
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### View in Terminal
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## 🐛 Debugging

### Run with Print Statements
```bash
pytest tests/ -s
```

### Run with Debugger
```bash
pytest tests/ --pdb
```

### Run Last Failed
```bash
pytest tests/ --lf
```

### Run with Verbose Output
```bash
pytest tests/ -vv
```

## ⚡ Performance

### Run in Parallel
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

### Show Slowest Tests
```bash
pytest tests/ --durations=10
```

## 📝 Test Structure

```
services/auth-service/tests/
├── conftest.py              # Shared fixtures
├── test_auth.py             # Auth endpoint tests
├── test_security.py         # Security utils tests
├── test_models.py           # Model tests
└── integration/
    ├── test_database.py     # Database tests
    └── test_redis.py        # Redis tests
```

## 🎯 Test Coverage Goals

- **Unit Tests:** 80%+ coverage
- **Integration Tests:** Critical paths
- **E2E Tests:** Main user flows

## 📚 More Info

See [TESTING.md](TESTING.md) for complete guide.
