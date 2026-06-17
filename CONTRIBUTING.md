# Contributing to Cogence

Thank you for your interest in contributing to Cogence! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Convention](#commit-convention)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Principles

Cogence is built on the principle of **Signals Over Surveillance** (ADR-004). We are building a tool to help leaders understand engineering work, not to monitor or rank individuals.

When contributing, please:
- Focus on business value and user needs
- Respect privacy and avoid surveillance features
- Write code that produces human-readable outputs
- Prioritize clarity over cleverness
- Be respectful and constructive in discussions

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Git
- A Gitea instance for testing (or use a test account)

### Initial Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/cogence.git
   cd cogence
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Setup Database**
   ```bash
   # Create database
   createdb cogence_dev
   
   # Run migrations
   alembic upgrade head
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Start development server
   uvicorn app.main:app --reload
   ```

---

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

### Creating a Feature Branch

```bash
# Update your local repository
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Read Relevant Documentation**
   - [Product Vision](docs/product/vision.md)
   - [MVP Scope](docs/product/mvp/MVP-v1.md)
   - [Architecture Overview](docs/architecture/system-overview.md)
   - [Relevant ADRs](docs/adr/)

2. **Write Code**
   - Follow [coding standards](#coding-standards)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Locally**
   ```bash
   # Run tests
   pytest
   
   # Check coverage
   pytest --cov=app tests/
   
   # Run linter
   ./scripts/lint.sh
   ```

4. **Commit Changes**
   - Follow [commit convention](#commit-convention)
   - Write clear, descriptive commit messages

---

## Coding Standards

### Python Style

We follow **PEP 8** with some specific conventions:

#### Type Hints (Required)

```python
from datetime import datetime
from typing import Optional

async def fetch_commits(
    repo_id: int,
    since: datetime,
    until: Optional[datetime] = None
) -> list[Commit]:
    """Fetch commits from repository."""
    pass
```

#### Docstrings (Required for Public APIs)

Use Google-style docstrings:

```python
def generate_report(commits: list[Commit]) -> Report:
    """Generate daily business-readable report.
    
    Per ADR-005, AI generates summaries, not facts.
    Per ADR-007, prioritize human readability.
    
    Args:
        commits: List of commits from the last 24 hours
        
    Returns:
        Report object with executive summary and sections
        
    Raises:
        ReportGenerationError: If report generation fails
    """
    pass
```

#### Async/Await

Use async/await for all I/O operations:

```python
# Good
async def get_repositories() -> list[Repository]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITEA_URL}/api/v1/repos")
        return parse_repositories(response.json())

# Bad - blocking I/O
def get_repositories() -> list[Repository]:
    response = requests.get(f"{GITEA_URL}/api/v1/repos")
    return parse_repositories(response.json())
```

#### Error Handling

```python
from app.core.exceptions import GiteaAPIError

try:
    commits = await gitea_client.fetch_commits(repo_id)
except httpx.HTTPError as e:
    logger.error(f"Failed to fetch commits: {e}", extra={
        "repo_id": repo_id,
        "error": str(e)
    })
    raise GiteaAPIError("Unable to fetch commits") from e
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use structured logging
logger.info("Report generated", extra={
    "report_date": date,
    "commit_count": len(commits),
    "duration_ms": duration
})
```

### Code Organization

```
app/
├── api/              # FastAPI routes
│   ├── v1/
│   │   ├── reports.py
│   │   └── repositories.py
│   └── deps.py       # Dependencies
├── core/             # Core business logic
│   ├── config.py
│   ├── exceptions.py
│   └── security.py
├── models/           # SQLAlchemy models
│   ├── commit.py
│   └── repository.py
├── schemas/          # Pydantic schemas
│   ├── commit.py
│   └── report.py
├── services/         # Business services
│   ├── collector.py
│   ├── generator.py
│   └── aggregator.py
└── integrations/     # External integrations
    ├── gitea.py
    └── llm.py
```

---

## Commit Convention

We follow a strict commit message convention based on [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
type(scope): brief description

Longer explanation if needed. Explain WHY, not WHAT.
Reference relevant ADRs or issues.

Refs: #123
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, no logic change)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

### Scopes

- `api` - API endpoints
- `collector` - Data collection
- `generator` - Report generation
- `db` - Database changes
- `gitea` - Gitea integration
- `llm` - LLM integration
- `tests` - Test-related changes

### Examples

```bash
# Good commits
feat(api): add daily report endpoint
fix(collector): handle Gitea API rate limiting
docs(adr): add ADR-012 for caching strategy
refactor(generator): extract summary logic to service
test(collector): add tests for error handling

# Bad commits
update code
fix bug
changes
WIP
```

### Detailed Example

```
feat(generator): implement AI-powered executive summary

Add LLM integration to generate business-readable summaries
from commit data. Per ADR-005, AI generates summaries not facts.

The summary is generated from structured commit metadata and
uses a prompt template that emphasizes business language over
technical details (ADR-002).

Refs: #45
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/             # Unit tests
│   ├── test_collector.py
│   ├── test_generator.py
│   └── test_aggregator.py
├── integration/      # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── fixtures/         # Test fixtures
    └── sample_data.py
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_commits_success():
    """Test successful commit fetching from Gitea."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value.json.return_value = [
        {"sha": "abc123", "commit": {"message": "Test commit"}}
    ]
    
    # Act
    commits = await fetch_commits(mock_client, repo_id=1)
    
    # Assert
    assert len(commits) == 1
    assert commits[0].sha == "abc123"
```

#### Integration Tests

```python
@pytest.mark.asyncio
async def test_daily_report_endpoint(client, db_session):
    """Test daily report API endpoint."""
    # Arrange - create test data
    repo = Repository(name="test-repo")
    db_session.add(repo)
    await db_session.commit()
    
    # Act
    response = await client.get("/api/v1/reports/daily/2024-01-15")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "executive_summary" in data
```

### Test Coverage

- Aim for **80%+ coverage** on business logic
- **100% coverage** on critical paths (data collection, report generation)
- Mock external services (Gitea, LLM)
- Test error conditions and edge cases

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_collector.py

# With coverage
pytest --cov=app tests/

# Coverage report
pytest --cov=app --cov-report=html tests/
```

---

## Pull Request Process

### Before Submitting

1. **Update from develop**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout your-feature-branch
   git rebase develop
   ```

2. **Run all checks**
   ```bash
   # Tests
   pytest
   
   # Linting
   ./scripts/lint.sh
   
   # Type checking
   mypy app/
   ```

3. **Update documentation**
   - Update relevant docs if behavior changes
   - Add/update docstrings
   - Update CHANGELOG.md

### Creating Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Use a clear, descriptive title
   - Reference related issues
   - Describe what changed and why
   - Include screenshots for UI changes
   - List any breaking changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings
```

### Review Process

1. **Automated Checks**
   - Tests must pass
   - Linting must pass
   - Coverage must not decrease

2. **Code Review**
   - At least one approval required
   - Address all comments
   - Update based on feedback

3. **Merge**
   - Squash and merge to develop
   - Delete feature branch after merge

---

## Documentation

### When to Update Documentation

Update documentation when you:
- Add new features
- Change existing behavior
- Add new APIs or endpoints
- Make architectural decisions
- Fix bugs that affect documented behavior

### Documentation Types

#### 1. Code Documentation
- Docstrings for all public functions/classes
- Inline comments for complex logic
- Type hints for all function signatures

#### 2. API Documentation
- Update `docs/api/README.md` for new endpoints
- Include request/response examples
- Document error responses

#### 3. Architecture Documentation
- Update relevant architecture docs
- Create ADR for significant decisions
- Update system diagrams if needed

#### 4. User Documentation
- Update README.md for user-facing changes
- Update setup guides if needed
- Add examples for new features

### Creating an ADR

For significant architectural decisions:

```bash
# Copy template
cp docs/adr/ADR-000-Template.md docs/adr/ADR-012-your-decision.md

# Fill in:
# - Context
# - Decision
# - Consequences
# - Alternatives considered
```

---

## Questions or Issues?

- **Questions:** Open a GitHub Discussion
- **Bugs:** Open a GitHub Issue with reproduction steps
- **Features:** Open a GitHub Issue with use case description
- **Security:** Email security@cogence.example.com (do not open public issue)

---

## Additional Resources

- [Product Vision](docs/product/vision.md)
- [Architecture Overview](docs/architecture/system-overview.md)
- [API Documentation](docs/api/README.md)
- [Development Setup](docs/development/setup.md)
- [Testing Strategy](docs/testing/strategy.md)
- [All ADRs](docs/adr/)

---

## License

By contributing to Cogence, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Cogence! 🚀