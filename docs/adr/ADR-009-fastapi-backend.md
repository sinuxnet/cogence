# ADR-009: FastAPI Backend

## Status

Accepted

## Date

2026-06-16

## Context

Cogence requires a backend framework to:
- Collect data from Gitea
- Process commit metadata
- Interact with AI services
- Store structured data
- Generate reports
- Serve API endpoints
- Handle scheduled tasks

Multiple Python frameworks are available:

**FastAPI**:
- Modern async framework
- Automatic API documentation
- Type hints and validation
- High performance
- Growing ecosystem

**Django**:
- Mature, batteries-included
- Built-in admin panel
- ORM included
- Large ecosystem
- Synchronous by default

**Flask**:
- Lightweight, flexible
- Minimal opinions
- Large ecosystem
- Synchronous by default

**Other Options**:
- Node.js (Express, NestJS)
- Go (Gin, Echo)
- Ruby (Rails)

The choice impacts development speed, AI integration, async capabilities, and ecosystem compatibility.

## Decision

**Use FastAPI as the backend framework.**

### Rationale

**Fast Development**:
- Minimal boilerplate
- Automatic API documentation (OpenAPI/Swagger)
- Built-in request validation
- Type hints reduce bugs

**Async Support**:
- Native async/await
- Concurrent API calls to Gitea
- Non-blocking AI service calls
- Efficient scheduled tasks

**AI Ecosystem**:
- Python is dominant in AI/ML
- Easy integration with OpenAI, Anthropic, etc.
- Rich libraries for data processing
- NumPy, Pandas available if needed

**Modern Stack**:
- Type hints (Pydantic)
- Dependency injection
- Modern Python features
- Active development

## Consequences

### Positive

- **Rapid development**: Less boilerplate than Django
- **Async by default**: Efficient for I/O-bound operations (Git API, AI API)
- **Type safety**: Pydantic models catch errors early
- **Automatic docs**: OpenAPI spec generated automatically
- **AI-friendly**: Python ecosystem for AI integration
- **Performance**: Comparable to Node.js, faster than Django
- **Modern patterns**: Dependency injection, async/await
- **Small learning curve**: Simpler than Django for small projects

### Negative

- **Less mature than Django**: Fewer built-in features
- **Smaller ecosystem**: Fewer third-party packages than Django
- **No built-in admin**: Must build admin UI separately
- **Async complexity**: Async code can be harder to debug
- **Less opinionated**: More decisions required
- **ORM not included**: Must choose SQLAlchemy or similar

## Alternatives Considered

### Django

Full-featured framework with batteries included.

**Rejected because:**
- Heavier than needed for MVP
- Synchronous by default (async support is newer)
- More boilerplate for simple APIs
- Built-in features (admin, forms) not needed for API-first app
- Slower development for API-only backend

### Flask

Lightweight, flexible framework.

**Rejected because:**
- Synchronous by default
- No automatic API documentation
- No built-in validation
- More manual work for API endpoints
- FastAPI provides Flask's flexibility with more features

### Node.js (Express/NestJS)

JavaScript/TypeScript backend.

**Rejected because:**
- Weaker AI ecosystem than Python
- Team expertise in Python
- Python better for data processing
- NestJS is heavier than needed
- Express requires more setup

### Go

High-performance compiled language.

**Rejected because:**
- Steeper learning curve
- Weaker AI ecosystem
- Overkill for MVP performance needs
- Slower development than Python
- Less flexible for rapid iteration

## Implementation Details

### Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── api/              # API routes
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   └── core/             # Config, dependencies
├── tests/
└── requirements.txt
```

### Key Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM (see ADR-010)
- **Pydantic**: Data validation
- **httpx**: Async HTTP client (for Gitea API)
- **APScheduler**: Scheduled tasks (see ADR-011)
- **OpenAI/Anthropic SDK**: AI integration

### API Design

RESTful endpoints:
- `GET /api/reports/daily/{date}` - Get daily report
- `GET /api/repositories` - List repositories
- `GET /api/commits` - List commits
- `POST /api/collect` - Trigger collection (admin)

### Async Patterns

```python
@app.get("/api/reports/daily/{date}")
async def get_daily_report(date: str):
    # Async database query
    commits = await db.get_commits(date)
    
    # Async AI call
    summary = await ai.generate_summary(commits)
    
    return {"date": date, "summary": summary}
```

## Technology Stack

**Backend**:
- Python 3.11+
- FastAPI 0.100+
- Uvicorn (ASGI server)

**Database**:
- PostgreSQL (see ADR-010)
- SQLAlchemy (async)

**AI**:
- OpenAI API or Anthropic API
- Async client libraries

**Deployment**:
- Docker container
- Systemd service or Docker Compose

## Relationship to Other ADRs

This decision enables:
- **ADR-005 (AI Generates Summaries)**: Python's AI ecosystem
- **ADR-010 (PostgreSQL)**: SQLAlchemy integration
- **ADR-011 (Scheduled Collection)**: APScheduler integration

This decision is reinforced by:
- **Principle 5: Incremental Intelligence**: FastAPI enables rapid iteration
- **MVP Philosophy**: Fast development for quick validation

## Performance Considerations

FastAPI is sufficient for MVP scale:
- Handles hundreds of requests/second
- Async I/O for concurrent operations
- Can scale horizontally if needed

Performance is not a concern for:
- Single organization (ADR-008)
- Daily batch processing (ADR-006)
- Limited concurrent users

## Revisit Conditions

This decision should be reconsidered when:

1. **Performance bottlenecks**: If FastAPI cannot handle load (unlikely for MVP)
2. **Team expertise changes**: If team becomes primarily Node.js/Go developers
3. **AI ecosystem shifts**: If AI tools move away from Python (unlikely)
4. **Specific framework features needed**: If Django's admin or ORM becomes critical
5. **Multi-language requirements**: If parts of system need different languages

For MVP and foreseeable future, FastAPI is the right choice.

## Migration Path

If framework change becomes necessary:

1. **API contracts remain stable**: OpenAPI spec defines interface
2. **Database schema independent**: SQLAlchemy models can be ported
3. **Business logic separable**: Service layer can be rewritten
4. **Gradual migration possible**: Can run both frameworks during transition

However, framework migration is unlikely to be necessary.