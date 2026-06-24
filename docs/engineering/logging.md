# Structured Logging Standards

**Version:** 1.0.0  
**Last Updated:** 2026-06-24  
**Applies to:** MVP-v2+

---

## Overview

This document defines structured logging standards for Cogence. Structured logging provides machine-readable logs that enable better debugging, monitoring, and analysis.

**Goal:** Consistent, searchable, analyzable logs across the entire application.

---

## Why Structured Logging?

### Problems with Unstructured Logs

```python
# Bad: Unstructured string
logger.info(f"Generating report for {date} with {len(repos)} repos")
```

**Issues:**
- Hard to parse programmatically
- Difficult to search
- Can't aggregate metrics
- Inconsistent format

### Benefits of Structured Logs

```python
# Good: Structured with context
logger.info(
    "report_generation_started",
    date=date,
    repositories_count=len(repos),
    commits_count=total_commits
)
```

**Benefits:**
- ✅ Machine-readable (JSON)
- ✅ Easy to search and filter
- ✅ Consistent format
- ✅ Enables metrics and alerts
- ✅ Better debugging

---

## Log Format

### JSON Structure

All logs are output as JSON:

```json
{
  "timestamp": "2024-01-15T21:00:00.123456+03:30",
  "level": "INFO",
  "event": "report_generation_started",
  "date": "2024-01-15",
  "repositories_count": 3,
  "commits_count": 25,
  "logger": "app.services.report",
  "thread": "MainThread",
  "process": 12345
}
```

### Required Fields

Every log entry must include:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | When the event occurred |
| `level` | string | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `event` | string | Event name (snake_case) |
| `logger` | string | Logger name (module path) |

### Optional Fields

Add context-specific fields:

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Report date (YYYY-MM-DD) |
| `repository` | string | Repository name |
| `organization` | string | Organization name |
| `contributor` | string | Contributor name |
| `duration_ms` | int | Operation duration |
| `error` | string | Error message |
| `exc_info` | bool | Include exception traceback |

---

## Log Levels

### Level Guidelines

| Level | When to Use | Examples |
|-------|-------------|----------|
| **DEBUG** | Detailed diagnostic info | Variable values, function entry/exit |
| **INFO** | General informational | Operation started/completed, state changes |
| **WARNING** | Unexpected but handled | Deprecated API used, fallback triggered |
| **ERROR** | Error prevented operation | Database error, API failure |
| **CRITICAL** | System-level failure | Cannot start, data corruption |

### Level Usage

```python
# DEBUG - Detailed diagnostic (disabled in production)
logger.debug(
    "commit_processed",
    sha=commit.sha,
    repository=commit.repository,
    files_changed=commit.files_changed
)

# INFO - Normal operations
logger.info(
    "report_generation_started",
    date=date_str,
    repositories_count=len(repos)
)

# WARNING - Unexpected but handled
logger.warning(
    "llm_rate_limit_hit",
    retry_after=30,
    attempt=2
)

# ERROR - Operation failed
logger.error(
    "database_connection_failed",
    error=str(e),
    database=settings.database_url,
    exc_info=True
)

# CRITICAL - System failure
logger.critical(
    "configuration_invalid",
    missing_keys=["GITEA_URL", "GITEA_API_TOKEN"],
    exc_info=True
)
```

---

## Event Naming

### Naming Convention

**Format:** `{noun}_{verb}_{state}`

**Examples:**
- `report_generation_started`
- `report_generation_completed`
- `report_generation_failed`
- `commit_collection_started`
- `commit_collection_completed`
- `llm_call_started`
- `llm_call_completed`
- `llm_call_failed`

### Event Categories

**Lifecycle Events:**
```python
logger.info("application_started")
logger.info("application_ready")
logger.info("application_shutdown")
```

**Operation Events:**
```python
logger.info("report_generation_started", date=date)
logger.info("report_generation_completed", date=date, duration_ms=2340)
logger.error("report_generation_failed", date=date, error=str(e))
```

**External Service Events:**
```python
logger.info("gitea_api_call", endpoint="/repos", method="GET")
logger.info("openai_api_call", model="gpt-4", tokens=1250)
logger.error("gitea_api_error", endpoint="/repos", status=500)
```

**Data Events:**
```python
logger.info("commits_collected", count=25, repository="customer-portal")
logger.info("repository_filtered", repository="test-repo", reason="excluded")
logger.info("repository_tracked", repository="customer-portal", organization="acme")
```

---

## Standard Events

### Application Lifecycle

```python
# Application startup
logger.info(
    "application_started",
    version=settings.version,
    environment=settings.environment
)

# Configuration loaded
logger.info(
    "configuration_loaded",
    gitea_url=settings.gitea_url,
    organizations=settings.gitea_organizations
)

# Application ready
logger.info(
    "application_ready",
    startup_duration_ms=duration
)

# Application shutdown
logger.info(
    "application_shutdown",
    uptime_seconds=uptime
)
```

### Report Generation

```python
# Report generation started
logger.info(
    "report_generation_started",
    date=date_str,
    use_ai=use_ai
)

# Commits fetched
logger.info(
    "commits_fetched",
    date=date_str,
    count=len(commits),
    repositories_count=len(repos)
)

# LLM call started
logger.info(
    "llm_call_started",
    section="executive_summary",
    model=settings.openai_model,
    temperature=0.3
)

# LLM call completed
logger.info(
    "llm_call_completed",
    section="executive_summary",
    tokens_used=tokens,
    duration_ms=duration
)

# Report generation completed
logger.info(
    "report_generation_completed",
    date=date_str,
    duration_ms=duration,
    total_commits=total,
    repositories_count=len(repos)
)

# Report generation failed
logger.error(
    "report_generation_failed",
    date=date_str,
    error=str(e),
    exc_info=True
)
```

### Data Collection

```python
# Collection started
logger.info(
    "commit_collection_started",
    date=date_str,
    repositories_count=len(repos)
)

# Repository processed
logger.info(
    "repository_processed",
    repository=repo.name,
    commits_collected=count,
    duration_ms=duration
)

# Collection completed
logger.info(
    "commit_collection_completed",
    date=date_str,
    total_commits=total,
    repositories_processed=len(repos),
    duration_ms=duration
)

# Collection failed
logger.error(
    "commit_collection_failed",
    repository=repo.name,
    error=str(e),
    exc_info=True
)
```

### External API Calls

```python
# Gitea API call
logger.info(
    "gitea_api_call",
    endpoint="/api/v1/repos",
    method="GET",
    status=200,
    duration_ms=duration
)

# Gitea API error
logger.error(
    "gitea_api_error",
    endpoint="/api/v1/repos",
    method="GET",
    status=500,
    error=str(e)
)

# OpenAI API call
logger.info(
    "openai_api_call",
    model="gpt-4",
    temperature=0.3,
    max_tokens=300,
    tokens_used=250,
    duration_ms=duration
)

# OpenAI API error
logger.error(
    "openai_api_error",
    model="gpt-4",
    error=str(e),
    exc_info=True
)
```

### Repository Filtering

```python
# Filtering summary
logger.info(
    "repository_filtering_summary",
    total_repositories=25,
    tracked_repositories=12,
    filtered_repositories=13,
    filter_reasons={
        "wrong_organization": 5,
        "personal_repository": 4,
        "archived": 2,
        "excluded_by_name": 2
    }
)

# Repository tracked
logger.info(
    "repository_tracked",
    repository=repo.name,
    organization=repo.organization
)

# Repository filtered
logger.info(
    "repository_filtered",
    repository=repo.name,
    reason="personal_repository_disabled",
    owner=repo.owner
)
```

---

## Implementation

### Setup Structured Logging

```python
# app/core/logging.py
import structlog
from app.core.config import settings

def setup_logging():
    """Configure structured logging for the application."""
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### Using Structured Logger

```python
# In any module
import structlog

logger = structlog.get_logger(__name__)

# Log with context
logger.info(
    "report_generation_started",
    date=date_str,
    repositories_count=len(repos),
    use_ai=use_ai
)

# Log with error
try:
    result = await generate_report(date_str)
except Exception as e:
    logger.error(
        "report_generation_failed",
        date=date_str,
        error=str(e),
        exc_info=True
    )
    raise
```

### Context Binding

```python
# Bind context for multiple log calls
logger = logger.bind(
    date=date_str,
    repository=repo.name
)

# All subsequent logs include bound context
logger.info("processing_started")
logger.info("commits_fetched", count=25)
logger.info("processing_completed")
```

---

## Configuration

### Environment Variables

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log output file (optional, logs to stdout if not set)
LOG_FILE=/var/log/cogence/app.log

# Log format (json or text)
LOG_FORMAT=json

# Enable debug logging for specific modules
LOG_DEBUG_MODULES=app.services.report,app.services.ai
```

### Configuration in Code

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    log_level: str = "INFO"
    log_file: str | None = None
    log_format: str = "json"
    log_debug_modules: list[str] = []
    
    class Config:
        env_file = ".env"
```

---

## Log Output

### Development (Text Format)

For development, use human-readable text format:

```bash
LOG_FORMAT=text
```

**Output:**
```
2024-01-15 21:00:00 [INFO] report_generation_started date=2024-01-15 repositories_count=3
2024-01-15 21:00:02 [INFO] llm_call_started section=executive_summary model=gpt-4
2024-01-15 21:00:04 [INFO] llm_call_completed section=executive_summary tokens=250 duration_ms=2000
2024-01-15 21:00:05 [INFO] report_generation_completed date=2024-01-15 duration_ms=5000
```

### Production (JSON Format)

For production, use JSON format:

```bash
LOG_FORMAT=json
```

**Output:**
```json
{"timestamp":"2024-01-15T21:00:00.123+03:30","level":"INFO","event":"report_generation_started","date":"2024-01-15","repositories_count":3}
{"timestamp":"2024-01-15T21:00:02.456+03:30","level":"INFO","event":"llm_call_started","section":"executive_summary","model":"gpt-4"}
{"timestamp":"2024-01-15T21:00:04.789+03:30","level":"INFO","event":"llm_call_completed","section":"executive_summary","tokens":250,"duration_ms":2000}
{"timestamp":"2024-01-15T21:00:05.012+03:30","level":"INFO","event":"report_generation_completed","date":"2024-01-15","duration_ms":5000}
```

---

## Searching and Filtering

### Using grep

```bash
# Find all report generation events
grep "report_generation" logs/cogence.log

# Find errors
grep '"level":"ERROR"' logs/cogence.log

# Find events for specific date
grep '"date":"2024-01-15"' logs/cogence.log

# Find LLM calls
grep "llm_call" logs/cogence.log
```

### Using jq

```bash
# Pretty print logs
cat logs/cogence.log | jq '.'

# Filter by event
cat logs/cogence.log | jq 'select(.event == "report_generation_started")'

# Filter by level
cat logs/cogence.log | jq 'select(.level == "ERROR")'

# Extract specific fields
cat logs/cogence.log | jq '{timestamp, event, date, duration_ms}'

# Calculate average duration
cat logs/cogence.log | jq -s 'map(select(.duration_ms)) | map(.duration_ms) | add / length'
```

### Using Log Aggregation Tools

**Elasticsearch Query:**
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"event": "report_generation_completed"}},
        {"range": {"duration_ms": {"gte": 5000}}}
      ]
    }
  }
}
```

**Splunk Query:**
```
index=cogence event="report_generation_completed" duration_ms>5000
| stats avg(duration_ms) by date
```

---

## Monitoring and Alerts

### Key Metrics to Monitor

**Performance Metrics:**
```python
# Report generation duration
logger.info(
    "report_generation_completed",
    date=date_str,
    duration_ms=duration  # Alert if > 5000ms
)

# LLM call duration
logger.info(
    "llm_call_completed",
    section=section,
    duration_ms=duration  # Alert if > 3000ms
)
```

**Error Metrics:**
```python
# Count errors by type
logger.error(
    "report_generation_failed",
    date=date_str,
    error_type=type(e).__name__  # Alert if count > 5 in 1 hour
)
```

**Resource Metrics:**
```python
# LLM token usage
logger.info(
    "llm_call_completed",
    tokens_used=tokens  # Alert if daily total > 100000
)
```

### Alert Examples

**Slow Report Generation:**
```
Alert: Report generation taking > 5 seconds
Query: event="report_generation_completed" AND duration_ms > 5000
Action: Investigate performance bottleneck
```

**High Error Rate:**
```
Alert: More than 5 report generation failures in 1 hour
Query: event="report_generation_failed" | count > 5 in 1h
Action: Check external services (Gitea, OpenAI)
```

**High Token Usage:**
```
Alert: Daily OpenAI token usage > 100,000
Query: event="llm_call_completed" | sum(tokens_used) > 100000 in 24h
Action: Review prompt efficiency
```

---

## Best Practices

### 1. Use Consistent Event Names

**Good:**
```python
logger.info("report_generation_started")
logger.info("report_generation_completed")
logger.error("report_generation_failed")
```

**Bad:**
```python
logger.info("start_report")
logger.info("report_done")
logger.error("report_error")
```

### 2. Include Relevant Context

**Good:**
```python
logger.info(
    "llm_call_completed",
    section="executive_summary",
    model="gpt-4",
    tokens_used=250,
    duration_ms=2000
)
```

**Bad:**
```python
logger.info("llm_call_completed")
```

### 3. Don't Log Sensitive Data

**Good:**
```python
logger.info(
    "user_authenticated",
    user_id=user.id,
    email=user.email
)
```

**Bad:**
```python
logger.info(
    "user_authenticated",
    password=password,  # NEVER!
    api_key=api_key     # NEVER!
)
```

### 4. Use Appropriate Log Levels

**Good:**
```python
logger.debug("variable_value", x=x)  # Debug only
logger.info("operation_completed")   # Normal operation
logger.error("operation_failed")     # Error occurred
```

**Bad:**
```python
logger.info("variable_value", x=x)   # Too verbose
logger.error("operation_completed")  # Wrong level
```

### 5. Log Exceptions with Context

**Good:**
```python
try:
    result = await generate_report(date_str)
except Exception as e:
    logger.error(
        "report_generation_failed",
        date=date_str,
        error=str(e),
        error_type=type(e).__name__,
        exc_info=True  # Include traceback
    )
    raise
```

**Bad:**
```python
try:
    result = await generate_report(date_str)
except Exception as e:
    logger.error("error")  # No context!
```

---

## Testing Logs

### Unit Tests

```python
def test_report_generation_logs(caplog):
    """Test that report generation logs expected events."""
    
    with caplog.at_level(logging.INFO):
        generate_report("2024-01-15")
    
    # Check expected log events
    events = [record.getMessage() for record in caplog.records]
    assert "report_generation_started" in events
    assert "report_generation_completed" in events
```

### Integration Tests

```python
async def test_report_generation_logs_context(caplog):
    """Test that logs include expected context."""
    
    with caplog.at_level(logging.INFO):
        await generate_report("2024-01-15")
    
    # Find report completion log
    completion_log = next(
        r for r in caplog.records 
        if "report_generation_completed" in r.getMessage()
    )
    
    # Check context fields
    assert completion_log.date == "2024-01-15"
    assert completion_log.duration_ms > 0
```

---

## Related Documentation

- [Engineering Guidelines](guidelines.md) - General coding standards
- [Development Setup](../development/setup.md) - Local development
- [Monitoring](../operations/monitoring.md) - Production monitoring

---

**Last Updated:** 2026-06-24  
**Version:** 1.0.0  
**Next Review:** After MVP-v2 deployment