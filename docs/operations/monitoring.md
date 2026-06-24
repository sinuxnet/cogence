# Cogence Monitoring & Observability

**Version:** 1.0.0  
**Last Updated:** 2026-06-24  
**Applies to:** MVP-v2+

---

## Overview

This document specifies monitoring, observability, and operational health requirements for Cogence. These capabilities ensure system reliability and provide visibility into performance and costs.

---

## Performance Monitoring

### API Response Time Tracking

**Requirement:** Track response time for all API endpoints to ensure SLA compliance.

**Implementation:**
- Middleware to measure request duration
- Log response times with structured logging
- Track P50, P95, P99 percentiles
- Alert on degradation

**Target SLAs:**
- `/health` endpoints: < 100ms (P95)
- `/api/v1/reports/daily/{date}` (cached): < 500ms (P95)
- `/api/v1/reports/daily/{date}/generate`: < 30s (P95)

**Metrics to Track:**
```python
# Example metrics
api_request_duration_seconds{endpoint="/api/v1/reports/daily/{date}", method="GET"}
api_request_duration_seconds{endpoint="/api/v1/reports/daily/{date}/generate", method="POST"}
api_request_total{endpoint, method, status_code}
```

**Implementation Notes:**
- Use FastAPI middleware for automatic tracking
- Store metrics in Prometheus (future) or structured logs
- Include endpoint, method, status code in metrics
- Track both successful and failed requests

---

### LLM Token Usage and Cost Tracking

**Requirement:** Monitor LLM API usage to control costs and optimize prompts.

**Metrics to Track:**
- Total tokens per request (prompt + completion)
- Cost per report generation
- Daily/weekly/monthly token usage
- Token usage by report type
- Failed LLM requests

**Implementation:**
```python
# Track in report metadata
{
  "metadata": {
    "llm_model": "gpt-4o-mini",
    "llm_tokens_used": 1340,
    "llm_prompt_tokens": 890,
    "llm_completion_tokens": 450,
    "llm_cost_usd": 0.0012,
    "llm_request_duration_ms": 2100
  }
}
```

**Cost Alerts:**
- Alert if daily cost exceeds threshold
- Alert if token usage spikes unexpectedly
- Alert if LLM request failure rate > 5%

**Optimization Tracking:**
- Track token usage trends over time
- Identify expensive prompts
- Monitor impact of prompt changes

---

### Report Caching

**Requirement:** Cache generated reports to avoid regenerating the same date multiple times.

**Implementation Strategy:**
- Database-backed cache (reports table)
- Check if report exists before generating
- Return cached report if available
- Invalidate cache only on explicit regeneration

**Cache Behavior:**
```python
# Pseudo-code
def generate_report(date):
    # Check cache first
    cached_report = db.get_report(date)
    if cached_report:
        return cached_report
    
    # Generate new report
    report = collect_and_generate(date)
    db.store_report(report)
    return report
```

**Cache Metrics:**
- Cache hit rate
- Cache miss rate
- Average cache retrieval time
- Cache size (number of reports)

**Cache Management:**
- Retention: 90+ days
- Manual invalidation via regenerate endpoint
- Automatic cleanup of old reports (optional)

---

## Startup Validation

### Environment Variable Validation

**Requirement:** Validate all required environment variables on startup and fail fast with clear errors.

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cogence

# API
API_SECRET_KEY=your-secret-key-here

# Gitea
GITEA_URL=https://gitea.example.com
GITEA_TOKEN=your-gitea-token

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Optional
TIMEZONE=Asia/Tehran
LOCALE=en
```

**Validation Logic:**
```python
# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # Required
    database_url: str = Field(..., description="PostgreSQL connection URL")
    api_secret_key: str = Field(..., min_length=32, description="API authentication key")
    gitea_url: str = Field(..., description="Gitea instance URL")
    gitea_token: str = Field(..., description="Gitea API token")
    openai_api_key: str = Field(..., description="OpenAI API key")
    
    # Optional with defaults
    openai_model: str = Field(default="gpt-4o-mini")
    timezone: str = Field(default="Asia/Tehran")
    locale: str = Field(default="en")
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith('postgresql'):
            raise ValueError('DATABASE_URL must be a PostgreSQL connection string')
        return v
    
    @validator('api_secret_key')
    def validate_api_key(cls, v):
        if len(v) < 32:
            raise ValueError('API_SECRET_KEY must be at least 32 characters')
        return v
    
    class Config:
        env_file = '.env'
        case_sensitive = False

# Fail fast on startup
try:
    settings = Settings()
except Exception as e:
    print(f"ERROR: Configuration validation failed: {e}")
    sys.exit(1)
```

**Error Messages:**
```
ERROR: Configuration validation failed
  Missing required environment variable: GITEA_TOKEN
  
Please set the following in your .env file:
  GITEA_TOKEN=your-gitea-token-here

See .env.example for reference.
```

---

### External Service Connectivity Tests

**Requirement:** Test connectivity to external services before starting and fail fast if misconfigured.

#### Test Gitea Connectivity

```python
async def test_gitea_connection():
    """Test Gitea API connectivity on startup."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.gitea_url}/api/v1/user"
            headers = {"Authorization": f"token {settings.gitea_token}"}
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    user = await response.json()
                    logger.info(f"✓ Gitea connection successful (user: {user['login']})")
                    return True
                elif response.status == 401:
                    logger.error("✗ Gitea authentication failed: Invalid token")
                    return False
                else:
                    logger.error(f"✗ Gitea connection failed: HTTP {response.status}")
                    return False
    except asyncio.TimeoutError:
        logger.error("✗ Gitea connection timeout")
        return False
    except Exception as e:
        logger.error(f"✗ Gitea connection error: {e}")
        return False
```

#### Test OpenAI API Key Validity

```python
async def test_openai_connection():
    """Test OpenAI API key validity on startup."""
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Simple test request
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        logger.info(f"✓ OpenAI connection successful (model: {settings.openai_model})")
        return True
    except AuthenticationError:
        logger.error("✗ OpenAI authentication failed: Invalid API key")
        return False
    except Exception as e:
        logger.error(f"✗ OpenAI connection error: {e}")
        return False
```

#### Test Database Connectivity

```python
async def test_database_connection():
    """Test database connectivity on startup."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False
```

#### Startup Sequence

```python
# app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks before accepting requests."""
    logger.info("Starting Cogence...")
    
    # Test all connections
    db_ok = await test_database_connection()
    gitea_ok = await test_gitea_connection()
    openai_ok = await test_openai_connection()
    
    if not all([db_ok, gitea_ok, openai_ok]):
        logger.error("Startup checks failed. Exiting.")
        sys.exit(1)
    
    logger.info("All startup checks passed. Ready to accept requests.")
    yield
    
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

**Startup Output:**
```
[2026-06-24 07:00:00] INFO: Starting Cogence...
[2026-06-24 07:00:01] INFO: ✓ Database connection successful
[2026-06-24 07:00:02] INFO: ✓ Gitea connection successful (user: cogence-bot)
[2026-06-24 07:00:03] INFO: ✓ OpenAI connection successful (model: gpt-4o-mini)
[2026-06-24 07:00:03] INFO: All startup checks passed. Ready to accept requests.
[2026-06-24 07:00:03] INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## Comprehensive Health Endpoint

**Requirement:** Provide detailed health information including database, Gitea, and OpenAI status.

### Enhanced /health/ready Endpoint

```python
@router.get("/health/ready")
async def health_ready():
    """
    Comprehensive readiness check.
    Returns 200 if all systems operational, 503 otherwise.
    """
    checks = {
        "database": await check_database(),
        "gitea": await check_gitea(),
        "openai": await check_openai()
    }
    
    all_healthy = all(check["status"] == "ok" for check in checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "degraded",
            "timestamp": datetime.now(ZoneInfo("Asia/Tehran")).isoformat(),
            "checks": checks
        }
    )

async def check_database():
    """Check database connectivity."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database reachable"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def check_gitea():
    """Check Gitea API connectivity."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.gitea_url}/api/v1/user"
            headers = {"Authorization": f"token {settings.gitea_token}"}
            async with session.get(url, headers=headers, timeout=5) as response:
                if response.status == 200:
                    return {"status": "ok", "message": "Gitea reachable"}
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def check_openai():
    """Check OpenAI API connectivity."""
    try:
        # Simple connectivity check (no actual request)
        # Could do a minimal test request if needed
        return {"status": "ok", "message": "OpenAI configured"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

**Response Example (Healthy):**
```json
{
  "status": "ready",
  "timestamp": "2026-06-24T07:00:00+03:30",
  "checks": {
    "database": {
      "status": "ok",
      "message": "Database reachable"
    },
    "gitea": {
      "status": "ok",
      "message": "Gitea reachable"
    },
    "openai": {
      "status": "ok",
      "message": "OpenAI configured"
    }
  }
}
```

**Response Example (Degraded):**
```json
{
  "status": "degraded",
  "timestamp": "2026-06-24T07:00:00+03:30",
  "checks": {
    "database": {
      "status": "ok",
      "message": "Database reachable"
    },
    "gitea": {
      "status": "error",
      "message": "Connection timeout"
    },
    "openai": {
      "status": "ok",
      "message": "OpenAI configured"
    }
  }
}
```

---

## Metrics Collection

### Key Metrics

**API Metrics:**
- Request count by endpoint
- Response time by endpoint
- Error rate by endpoint
- Active requests (concurrent)

**Report Generation Metrics:**
- Reports generated per day
- Average generation time
- LLM token usage
- LLM cost
- Cache hit/miss rate

**Data Collection Metrics:**
- Commits collected per run
- Repositories processed
- Collection duration
- Gitea API errors

**System Metrics:**
- Database connection pool usage
- Memory usage
- CPU usage
- Disk usage

### Prometheus Integration (Future)

```python
from prometheus_client import Counter, Histogram, Gauge

# API metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint', 'method']
)

# Report metrics
reports_generated_total = Counter(
    'reports_generated_total',
    'Total reports generated',
    ['report_type']
)

llm_tokens_used_total = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['model']
)

llm_cost_usd_total = Counter(
    'llm_cost_usd_total',
    'Total LLM cost in USD',
    ['model']
)
```

---

## Logging Standards

### Structured Logging

All logs should be structured JSON for easy parsing:

```python
import structlog

logger = structlog.get_logger()

# Example usage
logger.info(
    "report_generated",
    report_date="2026-06-23",
    duration_ms=4210,
    total_commits=12,
    llm_tokens=1340
)
```

### Log Levels

- **DEBUG:** Detailed diagnostic information
- **INFO:** General informational messages
- **WARNING:** Warning messages (degraded but functional)
- **ERROR:** Error messages (operation failed)
- **CRITICAL:** Critical errors (system failure)

### Required Log Fields

All logs should include:
- `timestamp` - ISO 8601 format
- `level` - Log level
- `message` - Human-readable message
- `service` - "cogence"
- `environment` - "production", "staging", "development"

---

## Alerting

### Alert Conditions

**Critical Alerts:**
- Database connection lost
- Gitea API unreachable
- OpenAI API errors > 10% in 5 minutes
- Report generation failing
- Disk space < 10%

**Warning Alerts:**
- API response time P95 > 2 seconds
- LLM cost > daily threshold
- Cache hit rate < 80%
- Memory usage > 80%

**Info Alerts:**
- Daily report generated successfully
- Data collection completed
- System startup/shutdown

---

## Related Documentation

- [Error Handling](deliver-error-handling.md) - Delivery script error handling
- [System Overview](../architecture/system-overview.md) - Architecture details
- [Logging Guidelines](../engineering/logging.md) - Logging standards

---

**Last Updated:** 2026-06-24  
**Version:** 1.0.0  
**Next Review:** After MVP-v2 deployment