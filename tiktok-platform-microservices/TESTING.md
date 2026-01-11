# Testing Guide - Microservices Platform

> Comprehensive testing strategy for TikTok LIVE Platform

---

## 📋 Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   E2E Tests │  (10%)
        └─────────────┘
      ┌───────────────────┐
      │ Integration Tests │  (30%)
      └───────────────────┘
    ┌───────────────────────┐
    │     Unit Tests        │  (60%)
    └───────────────────────┘
```

**Coverage Target:** 80%+

---

## 🧪 Test Types

### 1. Unit Tests
- Test individual functions/methods
- Mock external dependencies
- Fast execution (<1s per test)
- Run on every commit

### 2. Integration Tests
- Test service-to-service communication
- Test database operations
- Test event bus flow
- Run before deployment

### 3. End-to-End Tests
- Test complete user flows
- Test across all services
- Run on staging environment
- Run before production release

---

## 🚀 Quick Start

### Run All Tests

```bash
# From project root
./test-all.sh

# Or manually
cd services/auth-service
source venv/bin/activate
pytest
```

### Run Specific Service Tests

```bash
# Auth Service
cd services/auth-service
source venv/bin/activate
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_auth.py -v
```

### Run Specific Test

```bash
pytest tests/test_auth.py::test_register_user -v
```

---

## 📁 Test Structure

Each service has the same test structure:

```
services/auth-service/
├── app/
│   ├── main.py
│   ├── models/
│   ├── api/
│   └── services/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_auth.py         # Auth endpoint tests
│   ├── test_models.py       # Model tests
│   ├── test_services.py     # Service logic tests
│   └── integration/
│       ├── test_database.py
│       └── test_redis.py
└── pytest.ini
```

---

## 🔧 Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    asyncio: Async tests
```

### conftest.py (Shared Fixtures)

```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.database import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    """Database session for testing"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()
```

---

## 📝 Test Examples

### Unit Test Example

```python
# tests/test_auth.py
import pytest
from app.utils.security import hash_password, verify_password

def test_hash_password():
    """Test password hashing"""
    password = "test123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 20

def test_verify_password():
    """Test password verification"""
    password = "test123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False

@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration endpoint"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
```

### Integration Test Example

```python
# tests/integration/test_database.py
import pytest
from app.models.user import User

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_user_in_db(db_session):
    """Test creating user in database"""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None
```

### Mock Example

```python
# tests/test_tiktok_service.py
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_connect_to_tiktok_live():
    """Test TikTok LIVE connection"""
    with patch('app.services.tiktok.TikTokLiveClient') as mock_client:
        # Setup mock
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.connect.return_value = True
        
        # Test
        from app.services.tiktok import connect_to_live
        result = await connect_to_live("testuser")
        
        # Assert
        assert result is True
        mock_client.assert_called_once_with("testuser")
        mock_instance.connect.assert_called_once()
```

---

## 🎯 Service-Specific Tests

### Auth Service Tests

**What to Test:**
- ✅ User registration
- ✅ User login
- ✅ JWT token generation
- ✅ Token validation
- ✅ Password hashing
- ✅ Workspace creation
- ✅ RBAC permissions

**Example:**
```bash
cd services/auth-service
source venv/bin/activate
pytest tests/ -v -m "not integration"
```

### TikTok Service Tests

**What to Test:**
- ✅ TikTok LIVE connection
- ✅ Event processing
- ✅ Event publishing to Redis
- ✅ Connection retry logic
- ✅ Rate limit handling

**Example:**
```bash
cd services/tiktok-service
source venv/bin/activate
pytest tests/ -v
```

### Rule Engine Tests

**What to Test:**
- ✅ Rule creation/validation
- ✅ Event matching logic
- ✅ Action execution
- ✅ Cooldown management
- ✅ Redis event subscription

**Example:**
```bash
cd services/rule-engine
source venv/bin/activate
pytest tests/ -v
```

### Device Service Tests

**What to Test:**
- ✅ Device registration
- ✅ Agent token generation
- ✅ Command queue
- ✅ WebSocket connection
- ✅ Safety checks

**Example:**
```bash
cd services/device-service
source venv/bin/activate
pytest tests/ -v
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd services/auth-service
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd services/auth-service
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📊 Coverage Reports

### Generate Coverage Report

```bash
# HTML report
pytest tests/ --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html
```

### View Coverage in Terminal

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

**Expected Output:**
```
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
app/__init__.py              2      0   100%
app/main.py                 45      3    93%   78-80
app/models/user.py          28      0   100%
app/api/auth.py             67      5    93%   45, 89-92
app/utils/security.py       23      0   100%
------------------------------------------------------
TOTAL                      165      8    95%
```

---

## 🐛 Debugging Tests

### Run with Verbose Output

```bash
pytest tests/ -vv
```

### Run with Print Statements

```bash
pytest tests/ -s
```

### Run with Debugger

```bash
pytest tests/ --pdb
```

### Run Last Failed Tests

```bash
pytest tests/ --lf
```

---

## ⚡ Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class TikTokPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def register_user(self):
        self.client.post("/api/auth/register", json={
            "email": f"user{self.user_id}@test.com",
            "password": "password123"
        })
    
    @task(3)
    def login_user(self):
        self.client.post("/api/auth/login", data={
            "username": "test@example.com",
            "password": "password123"
        })
```

**Run:**
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## 📋 Test Checklist

### Before Commit
- [ ] All unit tests pass
- [ ] Code coverage > 80%
- [ ] No linting errors
- [ ] Type hints added

### Before PR
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Code reviewed

### Before Deploy
- [ ] E2E tests pass
- [ ] Load tests pass
- [ ] Security scan clean
- [ ] Staging tested

---

## 🎓 Best Practices

### 1. **AAA Pattern**
```python
def test_example():
    # Arrange
    user = create_test_user()
    
    # Act
    result = user.do_something()
    
    # Assert
    assert result == expected
```

### 2. **Use Fixtures**
```python
@pytest.fixture
def test_user():
    return User(email="test@example.com")

def test_with_fixture(test_user):
    assert test_user.email == "test@example.com"
```

### 3. **Parametrize Tests**
```python
@pytest.mark.parametrize("email,valid", [
    ("test@example.com", True),
    ("invalid", False),
    ("@example.com", False),
])
def test_email_validation(email, valid):
    assert is_valid_email(email) == valid
```

### 4. **Mock External Services**
```python
@patch('app.services.external_api.call')
def test_external_call(mock_call):
    mock_call.return_value = {"status": "ok"}
    result = my_function()
    assert result["status"] == "ok"
```

---

## 🚨 Common Issues

### Issue: Tests fail with database errors
**Solution:**
```bash
# Use test database
export DATABASE_URL="postgresql+asyncpg://test:test@localhost:5432/test_db"
pytest tests/
```

### Issue: Async tests not working
**Solution:**
```python
# Add pytest-asyncio
pip install pytest-asyncio

# Mark tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Issue: Tests are slow
**Solution:**
```bash
# Run in parallel
pip install pytest-xdist
pytest tests/ -n auto
```

---

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

---

**Next:** Run `./test-all.sh` to execute all tests! 🚀
