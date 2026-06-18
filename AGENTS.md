# Cogence AI Agents Guide

## Overview

This document provides essential guidance for AI coding assistants working on Cogence. It focuses on core principles, architecture decisions, and critical context needed for effective contribution.

---

## What is Cogence?

Cogence is an **Engineering Intelligence Platform** that transforms engineering activity into business-readable reports. It helps non-technical managers understand what engineering teams accomplish without reading code or attending technical meetings.

**Core Value Proposition:** A manager can understand today's engineering work in under 60 seconds — delivered via API or Rocket.Chat at 21:00 Asia/Tehran (no dashboard in pilot).

---

## Core Principles (Non-Negotiable)

1. **Business First** - Reports use business language, not technical jargon
2. **Signals Over Surveillance** - No individual productivity metrics or rankings
3. **Context Before Metrics** - Understand why, not just what
4. **Trust Is Mandatory** - Accuracy and honesty are non-negotiable
5. **Actionability Over Information** - Provide insights, not just data

See [docs/product/principles.md](docs/product/principles.md) for details.

---

## Technology Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (async)
- **Database:** PostgreSQL 15+
- **Git Platform:** Gitea (MVP v1)
- **AI/LLM:** OpenAI API or compatible
- **Async:** asyncio, aiohttp, asyncpg

---

## Critical Architecture Decisions

### ADR-001: Commits as Source of Truth
- Use Git commits as primary signal
- No code analysis in MVP
- Focus on commit metadata only

### ADR-002: Business Language Reporting
- All reports use business language
- No technical jargon
- Translate technical terms to business concepts

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

See [docs/architecture/domain-model.md](docs/architecture/domain-model.md) for complete details.

---

## MVP v1 Pilot

- **Delivery:** REST API + Rocket.Chat at 21:00 `Asia/Tehran` — no dashboard
- **Build order:** [docs/product/mvp/product-slices.md](docs/product/mvp/product-slices.md)
- **Pilot stories:** [docs/product/user-stories.md](docs/product/user-stories.md)
- **Backlog:** [docs/product/backlog.md](docs/product/backlog.md)

---

## Database Schema

Main tables: `repositories`, `commits`, `contributors`, `reports`, `report_commits`

See [docs/architecture/data-model.md](docs/architecture/data-model.md) for complete schema.

---

## API Structure

Key endpoints:
- `/api/v1/reports/daily/{date}` - Get daily report
- `/api/v1/reports/daily/latest` - Get latest report
- `/api/v1/repositories` - List repositories
- `/api/v1/commits` - Query commits

See [docs/api/README.md](docs/api/README.md) for complete API documentation.

---

## Coding Standards

### Python Style

- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for all public APIs
- **Async/await** for I/O operations
- **Pydantic** for validation

See [docs/architecture/system-overview.md](docs/architecture/system-overview.md) for architecture details.

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

See [docs/ai/report-generation.md](docs/ai/report-generation.md) for complete specifications.

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
- `tests/unit/` - Unit tests (fast, isolated)
- `tests/integration/` - Integration tests (database, API)
- `tests/e2e/` - End-to-end tests (full workflows)
- `tests/fixtures/` - Test data and fixtures

### Requirements
- 80%+ code coverage
- All business logic tested
- Edge cases covered
- Mocks for external services

See [docs/testing/strategy.md](docs/testing/strategy.md) for details.

---

## Error Handling

### Error Categories
1. **Transient Errors** - Retry with exponential backoff
2. **Configuration Errors** - Fail fast with clear messages
3. **Data Errors** - Log and skip, continue processing
4. **External Service Errors** - Graceful degradation

---

## Security & Privacy

- Bearer token authentication for API
- Gitea tokens stored securely
- Database connections use SSL/TLS
- No individual productivity metrics
- No surveillance features
- Aggregate data only in reports

See [docs/adr/ADR-004-signals-over-surveillance.md](docs/adr/ADR-004-signals-over-surveillance.md) and [docs/adr/ADR-008-single-tenant-internal-first.md](docs/adr/ADR-008-single-tenant-internal-first.md) for security and privacy constraints.

---

## Performance Guidelines

- Database: Use indexes, pagination, avoid SELECT *
- API: Response time < 2 seconds (P95), async/await for I/O
- Reports: Complete in < 30 seconds, batch processing

---

## Ubiquitous Language

**Use These Terms:**
- **Commit** (not "change" or "update")
- **Repository** (not "project" or "codebase")
- **Contributor** (not "developer" or "engineer")
- **Report** (not "dashboard" or "analytics")
- **Summary** (not "description")
- **Activity** (not "productivity")

**Forbidden Terms in Reports:**
- ❌ Lines of code (LOC)
- ❌ Productivity metrics
- ❌ Developer rankings
- ❌ Technical jargon
- ❌ Code quality scores

**Required Report Qualities:**
- ✅ Business language
- ✅ Readable in < 60 seconds
- ✅ Factually accurate
- ✅ Privacy-respecting
- ✅ Actionable

---

## Documentation

### Key Resources
- [Product Vision](docs/product/vision.md)
- [System Architecture](docs/architecture/system-overview.md)
- [API Documentation](docs/api/README.md)
- [Development Setup](docs/development/setup.md)
- [Testing Strategy](docs/testing/strategy.md)

### Key Files
- `.cursorrules` - Cursor AI rules
- `CONTRIBUTING.md` - Contribution guidelines
- `README.md` - Project overview

---

## Quick Reference

### Development Commands
```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload

# Test
pytest tests/ -v --cov=app

# Lint
ruff check app/ && black app/ && mypy app/
```

### Database Commands
```bash
# Migration
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

See [docs/development/setup.md](docs/development/setup.md) for complete setup guide.

---

## Project Structure

```
cogence/
├── app/              # Application code
│   ├── api/         # API endpoints
│   ├── core/        # Core configuration
│   ├── db/          # Database models
│   ├── models/      # Pydantic models
│   └── services/    # Business logic
├── docs/            # Documentation
├── tests/           # Test suite
├── scripts/         # Utility scripts
└── alembic/         # Database migrations
```

---

**Last Updated:** 2026-06-18

**For AI Agents:** This document provides essential context for contributing to Cogence. Follow the principles, respect the architecture decisions, and maintain code quality. When you need more details, refer to the linked documentation.