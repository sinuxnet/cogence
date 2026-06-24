# Software Engineering Guidelines

**Version:** 1.0.0  
**Last Updated:** 2026-06-24  
**Status:** Active

---

## Overview

This document defines software engineering principles, practices, and standards for the Cogence project. These guidelines ensure code quality, maintainability, and consistency across the codebase.

---

## Core Engineering Principles

### 1. Simplicity First

**Principle:** Choose the simplest solution that solves the problem.

**Guidelines:**
- Avoid premature optimization
- Don't add features "just in case"
- Prefer boring, proven technology
- YAGNI (You Aren't Gonna Need It)
- Start simple, evolve as needed

**Examples:**
```python
# Good: Simple, clear
def calculate_total(items):
    return sum(item.price for item in items)

# Bad: Over-engineered
class TotalCalculationStrategy:
    def __init__(self, aggregator, validator, transformer):
        self.aggregator = aggregator
        self.validator = validator
        self.transformer = transformer
```

---

### 2. Explicit Over Implicit

**Principle:** Make behavior obvious and predictable.

**Guidelines:**
- Explicit function parameters over global state
- Clear variable names over abbreviations
- Type hints for all public APIs
- No magic numbers or strings
- Document non-obvious behavior

**Examples:**
```python
# Good: Explicit
async def fetch_commits(
    repo_id: int,
    start_date: date,
    end_date: date,
    include_merges: bool = False
) -> list[Commit]:
    ...

# Bad: Implicit
async def fetch(repo, dates, opts=None):
    ...
```

---

### 3. Fail Fast, Fail Loud

**Principle:** Detect errors early and make them visible.

**Guidelines:**
- Validate inputs at boundaries
- Use type hints and runtime validation
- Raise specific exceptions
- Log errors with context
- Don't silently swallow exceptions

**Examples:**
```python
# Good: Fail fast with clear error
def generate_report(date_str: str) -> Report:
    if not date_str:
        raise ValueError("date_str is required")
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}") from e
    
    return _build_report(date_obj)

# Bad: Silent failure
def generate_report(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return _build_report(date_obj)
    except:
        return None
```

---

### 4. Separation of Concerns

**Principle:** Each module/function should have a single, well-defined responsibility.

**Guidelines:**
- Business logic separate from I/O
- Data access separate from presentation
- Configuration separate from code
- Pure functions where possible
- Dependency injection for testability

**Architecture:**
```
app/
├── api/          # HTTP layer (routes, request/response)
├── services/     # Business logic (pure functions where possible)
├── db/           # Data access (repositories, queries)
├── models/       # Data structures (Pydantic, SQLAlchemy)
└── core/         # Configuration, utilities
```

---

### 5. Test-Driven Mindset

**Principle:** Write testable code, test critical paths.

**Guidelines:**
- Write tests for business logic
- Test edge cases and error paths
- Use dependency injection for mocking
- Keep tests fast and isolated
- Aim for 80%+ coverage on critical code

**Test Structure:**
```python
# Good: Testable design
async def generate_report(
    commits: list[Commit],
    ai_service: AIService
) -> Report:
    # Pure logic, easy to test
    aggregated = aggregate_commits(commits)
    summary = await ai_service.generate_summary(aggregated)
    return build_report(aggregated, summary)

# Bad: Hard to test
async def generate_report(date_str: str) -> Report:
    # Tightly coupled to database and external services
    commits = await db.fetch_commits(date_str)
    summary = await openai.generate(commits)
    return Report(summary=summary)
```

---

## Code Style and Standards

### Python Style Guide

**Base Standard:** PEP 8 with project-specific additions

**Key Rules:**
- Line length: 100 characters (not 79)
- Indentation: 4 spaces
- Quotes: Double quotes for strings
- Imports: Absolute imports, grouped (stdlib, third-party, local)
- Naming: snake_case for functions/variables, PascalCase for classes

**Type Hints:**
```python
# Required for all public functions
def process_commits(
    commits: list[Commit],
    date_range: tuple[date, date],
    options: dict[str, Any] | None = None
) -> ProcessingResult:
    ...

# Use modern syntax (Python 3.10+)
def get_config() -> dict[str, str]:  # Not Dict[str, str]
    ...

# Optional for private functions, but encouraged
def _internal_helper(data: list[int]) -> int:
    ...
```

**Docstrings:**
```python
def generate_daily_report(date_str: str, use_ai: bool = True) -> dict:
    """Generate a daily engineering report for the specified date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        use_ai: Whether to use AI for summary generation
        
    Returns:
        Report dictionary with executive_summary, repositories, contributors
        
    Raises:
        ValueError: If date_str is invalid format
        DatabaseError: If commit data cannot be retrieved
    """
    ...
```

---

### Async/Await Guidelines

**When to Use Async:**
- I/O operations (database, HTTP, file)
- Multiple concurrent operations
- Long-running operations

**When NOT to Use Async:**
- Pure computation
- Simple data transformations
- Synchronous libraries

**Best Practices:**
```python
# Good: Async for I/O
async def fetch_commits(repo_id: int) -> list[Commit]:
    async with db.session() as session:
        result = await session.execute(query)
        return result.scalars().all()

# Good: Sync for computation
def aggregate_commits(commits: list[Commit]) -> AggregatedDay:
    # Pure computation, no I/O
    return AggregatedDay(...)

# Good: Concurrent operations
async def generate_report(date_str: str) -> Report:
    commits = await fetch_commits(date_str)
    
    # Run AI calls concurrently
    exec_summary, repo_summaries = await asyncio.gather(
        generate_executive_summary(commits),
        generate_repository_summaries(commits)
    )
    
    return Report(...)
```

---

### Error Handling

**Exception Hierarchy:**
```python
# Define domain-specific exceptions
class CogenceError(Exception):
    """Base exception for Cogence"""
    pass

class ConfigurationError(CogenceError):
    """Configuration is invalid or missing"""
    pass

class DataCollectionError(CogenceError):
    """Error collecting data from external source"""
    pass

class ReportGenerationError(CogenceError):
    """Error generating report"""
    pass
```

**Error Handling Patterns:**
```python
# Good: Specific exceptions, context
async def fetch_repository(repo_id: int) -> Repository:
    try:
        repo = await gitea_client.get_repository(repo_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise DataCollectionError(
                f"Repository {repo_id} not found"
            ) from e
        raise DataCollectionError(
            f"Failed to fetch repository {repo_id}: {e}"
        ) from e
    except httpx.RequestError as e:
        raise DataCollectionError(
            f"Network error fetching repository {repo_id}: {e}"
        ) from e
    
    return repo

# Good: Graceful degradation
async def generate_report(date_str: str) -> Report:
    try:
        return await _generate_ai_report(date_str)
    except Exception as e:
        logger.error("AI report generation failed", exc_info=e)
        return _generate_template_report(date_str)
```

---

## Database Guidelines

### Query Patterns

**Use Async SQLAlchemy:**
```python
# Good: Async session, explicit query
async def get_commits_by_date(
    session: AsyncSession,
    date_str: str
) -> list[Commit]:
    stmt = (
        select(Commit)
        .where(Commit.date == date_str)
        .order_by(Commit.timestamp)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

# Good: Use relationships efficiently
async def get_repository_with_commits(
    session: AsyncSession,
    repo_id: int
) -> Repository:
    stmt = (
        select(Repository)
        .where(Repository.id == repo_id)
        .options(selectinload(Repository.commits))
    )
    result = await session.execute(stmt)
    return result.scalar_one()
```

**Avoid N+1 Queries:**
```python
# Bad: N+1 query problem
async def get_all_repos_with_commits():
    repos = await session.execute(select(Repository))
    for repo in repos:
        # This triggers a separate query for each repo!
        commits = await session.execute(
            select(Commit).where(Commit.repository_id == repo.id)
        )

# Good: Use joins or eager loading
async def get_all_repos_with_commits():
    stmt = (
        select(Repository)
        .options(selectinload(Repository.commits))
    )
    result = await session.execute(stmt)
    return result.scalars().all()
```

---

### Migrations

**Alembic Best Practices:**
```python
# Always review auto-generated migrations
# Add meaningful revision messages
alembic revision --autogenerate -m "add organization_id to repositories"

# Test migrations both ways
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# Never edit applied migrations
# Create a new migration to fix issues
```

---

## API Design Guidelines

### RESTful Principles

**Resource Naming:**
```
# Good: Plural nouns, hierarchical
GET  /api/v1/repositories
GET  /api/v1/repositories/{id}
GET  /api/v1/repositories/{id}/commits
GET  /api/v1/reports/daily/{date}

# Bad: Verbs, inconsistent
GET  /api/v1/getRepositories
GET  /api/v1/repo/{id}
POST /api/v1/generateReport
```

**HTTP Methods:**
```
GET    - Retrieve resource(s), idempotent
POST   - Create resource or trigger action
PUT    - Replace entire resource
PATCH  - Partial update
DELETE - Remove resource
```

**Status Codes:**
```
200 OK              - Successful GET, PUT, PATCH
201 Created         - Successful POST
204 No Content      - Successful DELETE
400 Bad Request     - Invalid input
401 Unauthorized    - Missing/invalid auth
404 Not Found       - Resource doesn't exist
500 Internal Error  - Server error
```

### Request/Response Models

**Use Pydantic:**
```python
# Request model
class GenerateReportRequest(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    use_ai: bool = True
    locale: str = "en"

# Response model
class DailyReportResponse(BaseModel):
    report_date: str
    report_type: str
    executive_summary: str
    repositories: list[RepositorySummary]
    contributors: list[ContributorSummary]
    metadata: ReportMetadata

# Use in endpoint
@router.post("/reports/daily/{date}/generate")
async def generate_report(
    date: str,
    request: GenerateReportRequest,
    session: AsyncSession = Depends(get_session)
) -> DailyReportResponse:
    ...
```

---

## Logging Guidelines

### Structured Logging

**Use Structured Logs:**
```python
import structlog

logger = structlog.get_logger()

# Good: Structured with context
logger.info(
    "report_generation_started",
    date=date_str,
    repositories_count=len(repos),
    commits_count=total_commits
)

# Good: Error with context
logger.error(
    "llm_call_failed",
    section="executive_summary",
    model=settings.openai_model,
    error=str(e),
    exc_info=True
)

# Bad: Unstructured string
logger.info(f"Generating report for {date_str} with {len(repos)} repos")
```

**Log Levels:**
```
DEBUG   - Detailed diagnostic info (disabled in production)
INFO    - General informational messages
WARNING - Something unexpected but handled
ERROR   - Error that prevented operation
CRITICAL - System-level failure
```

**What to Log:**
```python
# Log important events
logger.info("report_generation_started", date=date_str)
logger.info("report_generation_completed", duration_ms=duration)

# Log external calls
logger.info("gitea_api_call", endpoint="/repos", status=200)
logger.info("openai_api_call", model="gpt-4", tokens=1250)

# Log errors with context
logger.error("database_error", operation="fetch_commits", error=str(e))

# Don't log sensitive data
logger.info("user_authenticated", user_id=user.id)  # Good
logger.info("user_authenticated", password=password)  # BAD!
```

---

## Testing Guidelines

### Test Structure

**Organize Tests:**
```
tests/
├── unit/              # Fast, isolated tests
│   ├── services/
│   ├── models/
│   └── utils/
├── integration/       # Database, API tests
│   ├── api/
│   └── db/
├── e2e/              # End-to-end workflows
└── fixtures/         # Test data
```

**Test Naming:**
```python
# Good: Descriptive test names
def test_aggregate_commits_groups_by_repository():
    ...

def test_generate_report_returns_template_when_ai_fails():
    ...

def test_fetch_commits_raises_error_for_invalid_date():
    ...

# Bad: Vague names
def test_aggregation():
    ...

def test_report():
    ...
```

### Test Patterns

**Arrange-Act-Assert:**
```python
def test_calculate_total_with_multiple_items():
    # Arrange
    items = [
        Item(price=10.0),
        Item(price=20.0),
        Item(price=30.0)
    ]
    
    # Act
    total = calculate_total(items)
    
    # Assert
    assert total == 60.0
```

**Use Fixtures:**
```python
@pytest.fixture
async def sample_commits():
    return [
        Commit(sha="abc123", title="feat: add login"),
        Commit(sha="def456", title="fix: resolve timeout"),
    ]

async def test_aggregate_commits(sample_commits):
    result = aggregate_commits("2024-01-15", sample_commits)
    assert result.total_commits == 2
```

**Mock External Services:**
```python
@pytest.mark.asyncio
async def test_generate_report_with_mocked_ai(mocker):
    # Mock external AI service
    mock_ai = mocker.patch("app.services.ai.generate_ai_report")
    mock_ai.return_value = LLMResult(
        executive_summary="Test summary",
        repository_summaries={},
        contributor_summaries={},
        management_notes="Test notes",
        tokens_used=100,
        duration_ms=500
    )
    
    report = await generate_report("2024-01-15", commits=[])
    
    assert report["executive_summary"] == "Test summary"
    mock_ai.assert_called_once()
```

---

## Performance Guidelines

### Database Performance

**Use Indexes:**
```sql
-- Index frequently queried columns
CREATE INDEX idx_commits_date ON commits(date);
CREATE INDEX idx_commits_repository_id ON commits(repository_id);
CREATE INDEX idx_commits_author_email ON commits(author_email);
```

**Pagination:**
```python
# Good: Paginate large result sets
async def get_commits_paginated(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 100
) -> list[Commit]:
    offset = (page - 1) * page_size
    stmt = (
        select(Commit)
        .order_by(Commit.timestamp.desc())
        .limit(page_size)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
```

### API Performance

**Response Time Targets:**
- Simple queries: < 200ms (P95)
- Report generation: < 2s (P95)
- Data collection: < 30s (P95)

**Caching:**
```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def parse_commit_message(message: str) -> ParsedMessage:
    # Expensive parsing logic
    ...

# Cache with TTL for external data
from cachetools import TTLCache

jira_cache = TTLCache(maxsize=1000, ttl=3600)

async def fetch_jira_issue(issue_key: str) -> JiraIssue:
    if issue_key in jira_cache:
        return jira_cache[issue_key]
    
    issue = await jira_client.get_issue(issue_key)
    jira_cache[issue_key] = issue
    return issue
```

---

## Security Guidelines

### Authentication

**API Key Authentication:**
```python
# Use bearer token authentication
async def verify_api_key(
    authorization: str = Header(...)
) -> None:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    
    token = authorization[7:]
    if not secrets.compare_digest(token, settings.api_secret_key):
        raise HTTPException(401, "Invalid API key")
```

### Data Privacy

**Privacy Rules:**
```python
# Never log sensitive data
logger.info("api_request", endpoint="/reports", user_id=user.id)  # Good
logger.info("api_request", api_key=api_key)  # BAD!

# Never expose sensitive data in responses
class UserResponse(BaseModel):
    id: int
    email: str
    # Don't include: password_hash, api_key, etc.

# Aggregate data only in reports
# No individual productivity metrics
# No developer rankings
```

---

## Documentation Guidelines

### Code Documentation

**When to Document:**
- All public APIs (functions, classes)
- Complex algorithms
- Non-obvious behavior
- Business logic decisions
- Configuration options

**What NOT to Document:**
```python
# Bad: Obvious comment
# Increment counter by 1
counter += 1

# Good: Explain why
# Use exponential backoff to avoid overwhelming the API
# during transient failures
await asyncio.sleep(2 ** retry_count)
```

### Architecture Documentation

**Keep Updated:**
- System architecture diagrams
- Data flow diagrams
- API documentation
- ADRs (Architecture Decision Records)
- Setup guides

---

## Git Workflow

### Commit Messages

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(api): add daily report generation endpoint

Implement POST /api/v1/reports/daily/{date}/generate endpoint
that triggers report generation for a specific date.

Closes #123

---

fix(collector): handle rate limit errors from Gitea

Add exponential backoff retry logic when Gitea API returns
429 Too Many Requests.

---

refactor(report): extract AI prompt logic to separate module

Move prompt templates and LLM interaction logic from report.py
to new ai.py module for better separation of concerns.
```

### Branch Strategy

**Branches:**
```
main        - Production-ready code
develop     - Integration branch
feature/*   - Feature development
fix/*       - Bug fixes
hotfix/*    - Production hotfixes
```

**Workflow:**
1. Create feature branch from `develop`
2. Develop and test
3. Create pull request to `develop`
4. Code review and approval
5. Merge to `develop`
6. Deploy to staging
7. Merge to `main` for production

---

## Code Review Guidelines

### What to Review

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] No performance issues
- [ ] Error handling is appropriate
- [ ] Logging is adequate
- [ ] Changes align with architecture

### Review Comments

**Be Constructive:**
```
# Good: Specific, actionable
"Consider using a set instead of a list here for O(1) lookup 
instead of O(n). This function is called frequently in the 
report generation loop."

# Bad: Vague, unhelpful
"This is slow."
```

---

## Continuous Improvement

### Refactoring

**When to Refactor:**
- Code is hard to understand
- Code is duplicated
- Tests are hard to write
- Performance is poor
- Adding features is difficult

**How to Refactor:**
1. Ensure tests exist
2. Make small, incremental changes
3. Run tests after each change
4. Commit frequently
5. Don't mix refactoring with features

### Technical Debt

**Track Technical Debt:**
- Document in code with `# TODO:` or `# FIXME:`
- Create issues for larger items
- Prioritize in backlog
- Allocate time for debt reduction

---

## Resources

### Tools

- **Linting:** ruff, black, mypy
- **Testing:** pytest, pytest-asyncio, pytest-cov
- **Documentation:** Sphinx, mkdocs
- **Profiling:** py-spy, memory_profiler

### References

- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

**Last Updated:** 2026-06-24  
**Version:** 1.0.0  
**Next Review:** After MVP-v2 completion