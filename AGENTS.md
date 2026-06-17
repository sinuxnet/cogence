# Cogence AI Agents Guide

## Overview

This document provides guidance for AI coding assistants (like Cursor, GitHub Copilot, or Claude) working on the Cogence project. It ensures AI agents understand the project context, architecture decisions, and coding standards.

---

## Project Context

### What is Cogence?

Cogence is an **Engineering Intelligence Platform** that transforms engineering activity into business-readable reports. It helps non-technical managers understand what engineering teams accomplish without reading code or attending technical meetings.

**Core Value Proposition:** A manager can understand yesterday's engineering work in under 60 seconds.

---

### Key Principles

1. **Business First** - Reports use business language, not technical jargon
2. **Signals Over Surveillance** - No individual productivity metrics or rankings
3. **Context Before Metrics** - Understand why, not just what
4. **Trust Is Mandatory** - Accuracy and honesty are non-negotiable
5. **Actionability Over Information** - Provide insights, not just data

See [docs/product/principles.md](docs/product/principles.md) for details.

---

## Architecture Overview

### Technology Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (async)
- **Database:** PostgreSQL 15+
- **Git Platform:** Gitea (MVP v1)
- **AI/LLM:** OpenAI API or compatible
- **Async:** asyncio, aiohttp, asyncpg

### Core Components

1. **Data Collection Service** - Fetches commits from Gitea
2. **Data Storage** - PostgreSQL with SQLAlchemy ORM
3. **Report Generation Service** - Creates daily reports using LLM
4. **API Service** - FastAPI REST API
5. **Task Scheduler** - APScheduler for scheduled operations

See [docs/architecture/system-overview.md](docs/architecture/system-overview.md) for details.

---

## Important Architecture Decisions

### ADR-001: Commits as Source of Truth
- Use Git commits as primary signal
- No code analysis in MVP
- Focus on commit metadata only

### ADR-002: Business Language Reporting
- All reports use business language
- No technical jargon
- Translate technical terms to business concepts

### ADR-003: No Code Analysis in MVP
- No static code analysis
- No code quality metrics
- No source code embeddings
- Commits only

### ADR-004: Signals Over Surveillance
- No individual productivity metrics
- No developer rankings
- No lines of code (LOC) metrics
- Privacy-respecting aggregation only

### ADR-005: AI Generates Summaries, Not Facts
- LLM generates summaries from commit data
- Facts come from Git, not AI
- AI translates technical to business language
- No hallucination of data

### ADR-006: Daily Report First
- Focus on daily reports only in MVP
- No weekly/monthly reports yet
- Simple before complex

### ADR-007: Human Readability Over Analytics
- Reports readable in under 60 seconds
- Designed for quick scanning
- No complex dashboards in MVP

### ADR-008: Single-Tenant, Internal-First
- No multi-tenancy in MVP
- Deploy internally first
- Simplify architecture

See [docs/adr/](docs/adr/) for all ADRs.

---

## Domain Model

### Core Entities

- **Organization** - The company using Cogence
- **Repository** - A Git repository being tracked
- **Commit** - A Git commit with metadata
- **Contributor** - A person who authors commits
- **DailyReport** - A generated daily summary
- **Summary** - AI-generated business-readable text

### Key Relationships

- Organization owns Repositories
- Repository contains Commits
- Contributor authors Commits
- DailyReport summarizes Commits

See [docs/architecture/domain-model.md](docs/architecture/domain-model.md) for details.

---

## Database Schema

### Main Tables

```sql
repositories (id, gitea_id, name, full_name, description, url, created_at, updated_at)
commits (id, repository_id, sha, author_name, author_email, timestamp, title, description, files_changed, insertions, deletions, created_at)
contributors (id, email, name, commit_count, first_seen, last_seen, updated_at)
reports (id, report_date, report_type, executive_summary, projects_summary, contributors_summary, management_notes, metadata, generated_at)
report_commits (id, report_id, commit_id)
```

See [docs/architecture/data-model.md](docs/architecture/data-model.md) for complete schema.

---

## API Structure

### Endpoints

```
/api/v1/reports/daily/{date}          - Get daily report
/api/v1/reports/daily/latest          - Get latest report
/api/v1/repositories                  - List repositories
/api/v1/commits                       - Query commits
/health                               - Health check
/health/ready                         - Readiness check
```

See [docs/api/README.md](docs/api/README.md) for complete API documentation.

---

## Coding Standards

### Python Style

- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for all public APIs
- **Async/await** for I/O operations
- **Pydantic** for validation

### Example Function

```python
async def get_commits_by_date_range(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    repository_id: Optional[int] = None
) -> List[Commit]:
    """
    Retrieve commits within a date range.
    
    Args:
        db: Database session
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        repository_id: Optional repository filter
        
    Returns:
        List of commits in date range
        
    Raises:
        DatabaseError: If query fails
    """
    query = select(Commit).where(
        Commit.timestamp >= start_date,
        Commit.timestamp <= end_date
    )
    
    if repository_id:
        query = query.where(Commit.repository_id == repository_id)
    
    result = await db.execute(query)
    return result.scalars().all()
```

---

## AI Prompt Guidelines

### When Generating Summaries

**MUST:**
- Use business language only
- Base summaries on actual commit data
- Be concise and actionable
- Respect privacy (no individual scoring)

**MUST NOT:**
- Mention lines of code (LOC)
- Rank or score developers
- Invent repositories or contributors
- Use technical jargon
- Analyze code (commits only)

See [docs/ai/report-generation.md](docs/ai/report-generation.md) for complete prompt specifications.

---

## Common Tasks

### Adding a New API Endpoint

1. Define Pydantic models in `app/models/`
2. Create endpoint in `app/api/v1/`
3. Add route to `app/api/v1/router.py`
4. Write tests in `tests/api/`
5. Update API documentation

### Adding a Database Table

1. Create SQLAlchemy model in `app/db/models/`
2. Create Alembic migration: `alembic revision --autogenerate -m "description"`
3. Review and edit migration
4. Test migration: `alembic upgrade head`
5. Update data model documentation

### Adding a New Report Section

1. Update domain model
2. Modify report generation service
3. Update AI prompts
4. Update database schema (if needed)
5. Update API response models
6. Write tests
7. Update documentation

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
├── integration/       # Integration tests (database, API)
├── e2e/              # End-to-end tests (full workflows)
└── fixtures/         # Test data and fixtures
```

### Test Requirements

- **80%+ code coverage**
- **All business logic tested**
- **Edge cases covered**
- **Mocks for external services**

### Example Test

```python
import pytest
from datetime import datetime, timedelta
from app.services.report_generation import ReportGenerationService

@pytest.mark.asyncio
async def test_generate_daily_report(db_session, sample_commits):
    """Test daily report generation with sample commits."""
    service = ReportGenerationService(db_session)
    
    report_date = datetime.now().date()
    report = await service.generate_daily_report(report_date)
    
    assert report is not None
    assert report.report_date == report_date
    assert len(report.executive_summary) > 0
    assert len(report.projects_summary) > 0
    assert "productivity" not in report.executive_summary.lower()
```

---

## Error Handling

### Error Categories

1. **Transient Errors** - Retry with exponential backoff
2. **Configuration Errors** - Fail fast with clear messages
3. **Data Errors** - Log and skip, continue processing
4. **External Service Errors** - Graceful degradation

### Example Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_commits_from_gitea(
    repository_id: int
) -> List[CommitData]:
    """
    Fetch commits from Gitea with retry logic.
    
    Retries up to 3 times with exponential backoff.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch commits: {e}")
        raise
```

---

## Security Considerations

### Authentication

- Bearer token authentication for API
- Tokens encrypted at rest
- Rate limiting enforced

### Data Protection

- Gitea tokens stored securely
- Database connections use SSL/TLS
- API uses HTTPS in production
- No sensitive data in logs

### Privacy

- No individual productivity metrics
- No surveillance features
- Aggregate data only in reports
- Transparent data collection

---

## Performance Guidelines

### Database Queries

- Use indexes for frequently queried fields
- Limit result sets with pagination
- Avoid SELECT * (select only needed columns)
- Use EXPLAIN ANALYZE for slow queries

### API Performance

- Response time < 2 seconds (P95)
- Support 10+ concurrent requests
- Cache frequently accessed reports
- Use async/await for I/O

### Report Generation

- Complete in under 30 seconds
- Process commits in batches
- Cache LLM responses when possible
- Monitor generation duration

---

## Documentation Requirements

### Code Documentation

- Docstrings for all public functions
- Type hints for all parameters
- Examples in docstrings
- Explain complex logic

### API Documentation

- OpenAPI/Swagger specs
- Request/response examples
- Error responses documented
- Authentication explained

### Architecture Documentation

- ADRs for significant decisions
- System diagrams updated
- Data flow documented
- Integration points explained

---

## Common Pitfalls to Avoid

### ❌ Don't Do This

```python
# Bad: Technical jargon in summary
summary = "Refactored OAuth2 implementation using async/await"

# Bad: Individual productivity metrics
report = f"{developer} made {commit_count} commits"

# Bad: Synchronous I/O
def fetch_commits():
    response = requests.get(url)  # Blocking!
    return response.json()

# Bad: No error handling
async def process_commits():
    commits = await fetch_commits()  # What if this fails?
    return commits
```

### ✅ Do This Instead

```python
# Good: Business language
summary = "Authentication improvements and security enhancements"

# Good: Aggregate, no individual metrics
report = f"Team made {total_commits} commits across {repo_count} projects"

# Good: Async I/O
async def fetch_commits():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Good: Error handling
async def process_commits():
    try:
        commits = await fetch_commits()
        return commits
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch commits: {e}")
        raise
```

---

## Useful Commands

### Development

```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=app tests/

# Lint code
ruff check app/
black app/

# Type check
mypy app/
```

### Database

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current version
alembic current
```

---

## Project Structure

```
cogence/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core configuration
│   ├── db/               # Database models and session
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   └── main.py           # Application entry point
├── docs/                 # Documentation
│   ├── adr/             # Architecture Decision Records
│   ├── ai/              # AI prompt specifications
│   ├── api/             # API documentation
│   ├── architecture/    # Architecture docs
│   ├── product/         # Product documentation
│   └── testing/         # Testing documentation
├── tests/               # Test suite
├── scripts/             # Utility scripts
├── alembic/             # Database migrations
└── requirements.txt     # Python dependencies
```

---

## Getting Help

### Documentation

- [Product Vision](docs/product/vision.md)
- [System Architecture](docs/architecture/system-overview.md)
- [API Documentation](docs/api/README.md)
- [Development Setup](docs/development/setup.md)

### Key Files

- `.cursorrules` - Cursor AI rules
- `CONTRIBUTING.md` - Contribution guidelines
- `README.md` - Project overview

---

## Quick Reference

### Ubiquitous Language

- **Commit** (not "change" or "update")
- **Repository** (not "project" or "codebase")
- **Contributor** (not "developer" or "engineer")
- **Report** (not "dashboard" or "analytics")
- **Summary** (not "description")
- **Activity** (not "productivity")

### Forbidden Terms in Reports

- ❌ Lines of code (LOC)
- ❌ Productivity metrics
- ❌ Developer rankings
- ❌ Technical jargon
- ❌ Code quality scores

### Required Report Qualities

- ✅ Business language
- ✅ Readable in < 60 seconds
- ✅ Factually accurate
- ✅ Privacy-respecting
- ✅ Actionable

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-17 | Initial AGENTS.md |

---

**Last Updated:** 2026-06-17

**For AI Agents:** This document is your guide to understanding and contributing to Cogence. Follow the principles, respect the architecture decisions, and maintain code quality. When in doubt, refer to the linked documentation.