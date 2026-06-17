# Cogence Testing Strategy

Comprehensive testing strategy for ensuring code quality and reliability.

---

## Testing Philosophy

### Core Principles

1. **Test Business Logic Thoroughly** - 80%+ coverage on core functionality
2. **Mock External Services** - Don't depend on Gitea or LLM APIs in tests
3. **Fast Feedback** - Tests should run quickly
4. **Readable Tests** - Tests are documentation
5. **Maintainable** - Tests should be easy to update

### Testing Pyramid

```
        /\
       /  \
      / E2E \
     /--------\
    /Integration\
   /--------------\
  /   Unit Tests   \
 /------------------\
```

- **70% Unit Tests** - Fast, isolated, focused
- **20% Integration Tests** - Database, API endpoints
- **10% E2E Tests** - Full workflow validation

---

## Test Structure

### Directory Organization

```
tests/
├── unit/                    # Unit tests
│   ├── test_collector.py
│   ├── test_aggregator.py
│   ├── test_generator.py
│   └── test_summarizer.py
├── integration/             # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_gitea_client.py
├── e2e/                     # End-to-end tests
│   └── test_report_flow.py
├── fixtures/                # Test fixtures
│   ├── sample_data.py
│   └── mock_responses.py
└── conftest.py             # Pytest configuration
```

---

## Unit Tests

### Purpose
Test individual functions and classes in isolation.

### Guidelines

- **One test per behavior**
- **Mock all external dependencies**
- **Fast execution** (< 1 second per test)
- **No database or network calls**
- **Clear test names** describing behavior

### Example: Testing Commit Collector

```python
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.services.collector import CommitCollector
from app.integrations.gitea import GiteaAPIError

@pytest.mark.asyncio
async def test_fetch_commits_success():
    """Test successful commit fetching from Gitea."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get_commits.return_value = [
        {
            "sha": "abc123",
            "commit": {
                "author": {"name": "John Doe", "email": "john@example.com"},
                "message": "feat: add feature",
                "committer": {"date": "2024-01-15T10:00:00Z"}
            },
            "stats": {"additions": 10, "deletions": 5}
        }
    ]
    
    collector = CommitCollector(gitea_client=mock_client)
    
    # Act
    commits = await collector.fetch_commits(
        repo_id=1,
        since=datetime(2024, 1, 15)
    )
    
    # Assert
    assert len(commits) == 1
    assert commits[0].sha == "abc123"
    assert commits[0].author_name == "John Doe"
    mock_client.get_commits.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_commits_handles_api_error():
    """Test that collector handles Gitea API errors gracefully."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get_commits.side_effect = GiteaAPIError("API Error")
    
    collector = CommitCollector(gitea_client=mock_client)
    
    # Act & Assert
    with pytest.raises(GiteaAPIError):
        await collector.fetch_commits(repo_id=1, since=datetime.now())


@pytest.mark.asyncio
async def test_fetch_commits_with_empty_result():
    """Test handling of repositories with no commits."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get_commits.return_value = []
    
    collector = CommitCollector(gitea_client=mock_client)
    
    # Act
    commits = await collector.fetch_commits(repo_id=1, since=datetime.now())
    
    # Assert
    assert len(commits) == 0
```

### Example: Testing Report Generator

```python
import pytest
from app.services.generator import ReportGenerator
from app.models import Commit

@pytest.mark.asyncio
async def test_generate_report_with_commits(mock_commits, mock_llm):
    """Test report generation with valid commits."""
    # Arrange
    generator = ReportGenerator(llm_client=mock_llm)
    
    # Act
    report = await generator.generate_daily_report(
        date=datetime(2024, 1, 15),
        commits=mock_commits
    )
    
    # Assert
    assert report.report_date == datetime(2024, 1, 15).date()
    assert report.executive_summary is not None
    assert len(report.projects) > 0
    assert len(report.contributors) > 0
    assert report.management_notes is not None


@pytest.mark.asyncio
async def test_generate_report_with_no_commits(mock_llm):
    """Test report generation when no commits exist."""
    # Arrange
    generator = ReportGenerator(llm_client=mock_llm)
    
    # Act
    report = await generator.generate_daily_report(
        date=datetime(2024, 1, 15),
        commits=[]
    )
    
    # Assert
    assert report.executive_summary == "No engineering activity recorded"
    assert len(report.projects) == 0
    assert len(report.contributors) == 0
```

---

## Integration Tests

### Purpose
Test interactions between components, including database and API.

### Guidelines

- **Use test database**
- **Test real integrations** (but mock external APIs)
- **Clean up after tests**
- **Test error scenarios**
- **Verify data persistence**

### Example: Testing API Endpoints

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_db
from tests.fixtures.sample_data import create_sample_report

@pytest.mark.asyncio
async def test_get_daily_report_success(test_db):
    """Test retrieving daily report via API."""
    # Arrange
    await create_sample_report(test_db, date="2024-01-15")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Act
        response = await client.get("/api/v1/reports/daily/2024-01-15")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["report_date"] == "2024-01-15"
        assert "executive_summary" in data
        assert "projects" in data
        assert "contributors" in data


@pytest.mark.asyncio
async def test_get_daily_report_not_found():
    """Test 404 response when report doesn't exist."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Act
        response = await client.get("/api/v1/reports/daily/2099-12-31")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_daily_report_invalid_date():
    """Test 400 response for invalid date format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Act
        response = await client.get("/api/v1/reports/daily/invalid-date")
        
        # Assert
        assert response.status_code == 400
```

### Example: Testing Database Operations

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Commit, Repository
from app.services.database import CommitRepository

@pytest.mark.asyncio
async def test_store_commit(test_db: AsyncSession):
    """Test storing commit in database."""
    # Arrange
    repo = Repository(name="test-repo", full_name="org/test-repo")
    test_db.add(repo)
    await test_db.commit()
    
    commit_repo = CommitRepository(test_db)
    
    # Act
    commit = await commit_repo.create(
        repository_id=repo.id,
        sha="abc123",
        author_name="John Doe",
        author_email="john@example.com",
        timestamp=datetime.now(),
        title="Test commit",
        description="Test description"
    )
    
    # Assert
    assert commit.id is not None
    assert commit.sha == "abc123"
    
    # Verify persistence
    retrieved = await commit_repo.get_by_sha("abc123")
    assert retrieved is not None
    assert retrieved.author_name == "John Doe"


@pytest.mark.asyncio
async def test_query_commits_by_date_range(test_db: AsyncSession):
    """Test querying commits within date range."""
    # Arrange - create test commits
    repo = Repository(name="test-repo")
    test_db.add(repo)
    await test_db.flush()
    
    commits = [
        Commit(
            repository_id=repo.id,
            sha=f"sha{i}",
            author_name="Test",
            timestamp=datetime(2024, 1, i+1)
        )
        for i in range(5)
    ]
    test_db.add_all(commits)
    await test_db.commit()
    
    commit_repo = CommitRepository(test_db)
    
    # Act
    results = await commit_repo.get_by_date_range(
        since=datetime(2024, 1, 2),
        until=datetime(2024, 1, 4)
    )
    
    # Assert
    assert len(results) == 3  # Days 2, 3, 4
```

---

## End-to-End Tests

### Purpose
Test complete workflows from start to finish.

### Guidelines

- **Test critical user journeys**
- **Use realistic data**
- **Verify end-to-end behavior**
- **Keep minimal** (slow to run)

### Example: Complete Report Generation Flow

```python
import pytest
from datetime import datetime
from app.services.collector import CommitCollector
from app.services.generator import ReportGenerator

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_complete_report_generation_flow(
    test_db,
    mock_gitea_client,
    mock_llm_client
):
    """Test complete flow from collection to report generation."""
    # Arrange
    collector = CommitCollector(gitea_client=mock_gitea_client)
    generator = ReportGenerator(llm_client=mock_llm_client)
    
    # Act - Collect commits
    await collector.collect_all_repositories(
        since=datetime(2024, 1, 15)
    )
    
    # Act - Generate report
    report = await generator.generate_daily_report(
        date=datetime(2024, 1, 15)
    )
    
    # Assert - Verify complete report
    assert report is not None
    assert report.report_date == datetime(2024, 1, 15).date()
    assert len(report.executive_summary) > 0
    assert len(report.projects) > 0
    assert len(report.contributors) > 0
    
    # Verify report is stored
    stored_report = await test_db.get_report_by_date(
        datetime(2024, 1, 15).date()
    )
    assert stored_report is not None
    assert stored_report.id == report.id
```

---

## Test Fixtures

### conftest.py

```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Repository, Commit

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/cogence_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """Create test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def mock_gitea_client():
    """Mock Gitea API client."""
    from unittest.mock import AsyncMock
    
    client = AsyncMock()
    client.list_repositories.return_value = [
        {"id": 1, "name": "test-repo", "full_name": "org/test-repo"}
    ]
    client.get_commits.return_value = []
    
    return client


@pytest.fixture
def mock_llm_client():
    """Mock LLM API client."""
    from unittest.mock import AsyncMock
    
    client = AsyncMock()
    client.generate_summary.return_value = "Test summary"
    
    return client


@pytest.fixture
def mock_commits():
    """Create mock commit data."""
    return [
        Commit(
            sha=f"sha{i}",
            repository="test-repo",
            author_name="Test Author",
            author_email="test@example.com",
            timestamp=datetime(2024, 1, 15, 10, i),
            title=f"Test commit {i}",
            description=f"Description {i}",
            files_changed=5,
            insertions=50,
            deletions=10
        )
        for i in range(5)
    ]
```

---

## Coverage Requirements

### Minimum Coverage Targets

- **Overall:** 80%
- **Core Business Logic:** 90%
- **API Endpoints:** 85%
- **Database Operations:** 85%
- **Utilities:** 70%

### Measuring Coverage

```bash
# Run tests with coverage
pytest --cov=app tests/

# Generate HTML report
pytest --cov=app --cov-report=html tests/
open htmlcov/index.html

# Check coverage threshold
pytest --cov=app --cov-fail-under=80 tests/
```

### Coverage Configuration (.coveragerc)

```ini
[run]
source = app
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

---

## Mocking Strategy

### External Services to Mock

1. **Gitea API** - Always mock in tests
2. **LLM API** - Always mock in tests
3. **Email/SMTP** - Mock in unit/integration tests
4. **Time/Datetime** - Mock when testing time-dependent logic

### Mock Examples

```python
from unittest.mock import AsyncMock, patch
from datetime import datetime

# Mock Gitea API
@patch('app.integrations.gitea.GiteaClient')
async def test_with_mocked_gitea(mock_gitea):
    mock_gitea.return_value.get_commits.return_value = []
    # Test code here

# Mock LLM API
@patch('app.integrations.llm.LLMClient')
async def test_with_mocked_llm(mock_llm):
    mock_llm.return_value.generate.return_value = "Test summary"
    # Test code here

# Mock datetime
@patch('app.services.generator.datetime')
def test_with_mocked_time(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 0, 0)
    # Test code here
```

---

## Performance Testing

### Load Testing

```python
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.performance
@pytest.mark.asyncio
async def test_api_concurrent_requests():
    """Test API handles concurrent requests."""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Create 100 concurrent requests
        tasks = [
            client.get("/api/v1/reports/daily/latest")
            for _ in range(100)
        ]
        
        # Execute concurrently
        responses = await asyncio.gather(*tasks)
        
        # Assert all succeeded
        assert all(r.status_code == 200 for r in responses)
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
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
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml tests/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Best Practices

### DO

✅ Write tests before fixing bugs  
✅ Test edge cases and error conditions  
✅ Use descriptive test names  
✅ Keep tests independent  
✅ Mock external dependencies  
✅ Test business logic thoroughly  
✅ Use fixtures for common setup  
✅ Run tests before committing  

### DON'T

❌ Test implementation details  
❌ Write flaky tests  
❌ Skip tests to make CI pass  
❌ Test framework code  
❌ Make tests depend on each other  
❌ Use real external APIs  
❌ Commit failing tests  
❌ Ignore test failures  

---

## Related Documentation

- [Development Setup](../development/setup.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [API Documentation](../api/README.md)
- [Examples](../examples/README.md)

---

**Last Updated:** 2026-06-17