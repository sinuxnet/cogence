# Cogence API Documentation

REST API documentation for Cogence MVP v1.

**Base URL:** `http://localhost:8000/api/v1` (development)

**Authentication:** Bearer token (to be implemented)

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Reports API](#reports-api)
- [Repositories API](#repositories-api)
- [Commits API](#commits-api)
- [Health Check API](#health-check-api)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Overview

### API Principles

1. **RESTful Design:** Standard HTTP methods and status codes
2. **JSON Format:** All requests and responses use JSON
3. **Versioned:** API version in URL path (`/api/v1/`)
4. **Consistent:** Predictable naming and structure
5. **Documented:** OpenAPI/Swagger documentation available

### Base Response Format

All successful responses follow this structure:

```json
{
  "data": { /* response data */ },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0"
  }
}
```

### OpenAPI Documentation

Interactive API documentation available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## Authentication

### Bearer Token Authentication

**Header:**
```
Authorization: Bearer <token>
```

**Example:**
```bash
curl -H "Authorization: Bearer your_token_here" \
  http://localhost:8000/api/v1/reports/daily/latest
```

### Token Management

Tokens are managed through environment configuration (MVP v1).

Future versions will include:
- Token generation API
- Token refresh mechanism
- Role-based access control

---

## Reports API

### Get Daily Report

Retrieve a daily engineering report for a specific date.

**Endpoint:** `GET /api/v1/reports/daily/{date}`

**Parameters:**
- `date` (path, required): Date in YYYY-MM-DD format

**Response:** `200 OK`

```json
{
  "report_date": "2024-01-15",
  "report_type": "daily",
  "executive_summary": "Engineering focused on customer-facing improvements yesterday. The team made 15 commits across 3 projects, with primary attention on the customer portal.",
  "projects": [
    {
      "repository": "customer-portal",
      "commit_count": 8,
      "summary": "Authentication improvements and user experience enhancements"
    },
    {
      "repository": "api-gateway",
      "commit_count": 5,
      "summary": "Performance optimization and error handling improvements"
    },
    {
      "repository": "admin-dashboard",
      "commit_count": 2,
      "summary": "Minor bug fixes and UI updates"
    }
  ],
  "contributors": [
    {
      "name": "John Doe",
      "commit_count": 6,
      "summary": "Worked on authentication system and user management features"
    },
    {
      "name": "Jane Smith",
      "commit_count": 4,
      "summary": "Improved API performance and added comprehensive monitoring"
    },
    {
      "name": "Bob Johnson",
      "commit_count": 3,
      "summary": "Enhanced admin dashboard functionality"
    },
    {
      "name": "Alice Williams",
      "commit_count": 2,
      "summary": "Fixed critical bugs in payment processing"
    }
  ],
  "management_notes": "High activity on customer-facing projects. Team is focused on strategic initiatives. No unusual patterns or concerns detected.",
  "metadata": {
    "generated_at": "2024-01-16T00:30:00Z",
    "total_commits": 15,
    "total_repositories": 3,
    "total_contributors": 4,
    "generation_duration_ms": 2340
  }
}
```

**Example Request:**

```bash
curl http://localhost:8000/api/v1/reports/daily/2024-01-15
```

**Error Responses:**

```json
// 404 Not Found
{
  "detail": "No report found for 2024-01-15"
}

// 400 Bad Request
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

---

### Get Latest Daily Report

Retrieve the most recent daily report.

**Endpoint:** `GET /api/v1/reports/daily/latest`

**Response:** `200 OK` (same structure as Get Daily Report)

**Example Request:**

```bash
curl http://localhost:8000/api/v1/reports/daily/latest
```

---

### Generate Daily Report

Generate a daily report for a specific date. Idempotent - returns existing report if already generated.

**Endpoint:** `POST /api/v1/reports/daily/{date}/generate`

**Parameters:**
- `date` (path, required): Date in YYYY-MM-DD format (Asia/Tehran timezone)
- `depth` (query, optional, default: `standard`): Report depth tier
- `locale` (query, optional, default from `COGENCE_REPORT_LOCALE`): Report language (`fa`, `en`)

**Behavior:**
- Idempotent: Returns existing report if already generated for the date
- Does NOT regenerate if report exists (true idempotency)
- Collects commits → generates summary → stores → returns in one call

**Response:** `200 OK`

```json
{
  "report_date": "2024-01-15",
  "report_type": "daily",
  "report_depth": "standard",
  "locale": "en",
  "timezone": "Asia/Tehran",
  "executive_summary": "Engineering focused on customer-facing improvements...",
  "repositories": [...],
  "contributors": [...],
  "management_notes": "High activity on customer-facing repositories...",
  "metadata": {
    "generated_at": "2024-01-16T00:30:00+03:30",
    "total_commits": 15,
    "total_repositories": 3,
    "total_contributors": 4,
    "non_atomic_commits": 2,
    "atomic_commit_threshold": 10,
    "generation_duration_ms": 2340,
    "llm_model": "gpt-4",
    "llm_tokens_used": 1250
  }
}
```

**Example Requests:**

```bash
# Generate with defaults
curl -X POST http://localhost:8000/api/v1/reports/daily/2024-01-15/generate

# Generate with Persian locale
curl -X POST "http://localhost:8000/api/v1/reports/daily/2024-01-15/generate?locale=fa"

# Generate with explicit depth
curl -X POST "http://localhost:8000/api/v1/reports/daily/2024-01-15/generate?depth=standard&locale=en"
```

---

### List Reports

List available reports with pagination.

**Endpoint:** `GET /api/v1/reports`

**Query Parameters:**
- `limit` (optional, default: 10): Number of reports per page
- `offset` (optional, default: 0): Pagination offset
- `type` (optional): Filter by report type (e.g., "daily")

**Response:** `200 OK`

```json
{
  "reports": [
    {
      "report_date": "2024-01-15",
      "report_type": "daily",
      "generated_at": "2024-01-16T00:30:00Z",
      "url": "/api/v1/reports/daily/2024-01-15"
    },
    {
      "report_date": "2024-01-14",
      "report_type": "daily",
      "generated_at": "2024-01-15T00:30:00Z",
      "url": "/api/v1/reports/daily/2024-01-14"
    }
  ],
  "pagination": {
    "total": 45,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/reports?limit=10&offset=0"
```

---

## Repositories API

### List Repositories

List all repositories being tracked.

**Endpoint:** `GET /api/v1/repositories`

**Query Parameters:**
- `limit` (optional, default: 50): Number of repositories per page
- `offset` (optional, default: 0): Pagination offset

**Response:** `200 OK`

```json
{
  "repositories": [
    {
      "id": 1,
      "name": "customer-portal",
      "full_name": "acme/customer-portal",
      "url": "https://git.acme.com/acme/customer-portal",
      "description": "Customer-facing web portal",
      "created_at": "2024-01-01T00:00:00Z",
      "last_commit_at": "2024-01-15T14:30:00Z"
    },
    {
      "id": 2,
      "name": "api-gateway",
      "full_name": "acme/api-gateway",
      "url": "https://git.acme.com/acme/api-gateway",
      "description": "API gateway service",
      "created_at": "2024-01-01T00:00:00Z",
      "last_commit_at": "2024-01-15T16:45:00Z"
    }
  ],
  "pagination": {
    "total": 12,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

**Example Request:**

```bash
curl http://localhost:8000/api/v1/repositories
```

---

### Get Repository Details

Get detailed information about a specific repository.

**Endpoint:** `GET /api/v1/repositories/{id}`

**Parameters:**
- `id` (path, required): Repository ID

**Response:** `200 OK`

```json
{
  "id": 1,
  "name": "customer-portal",
  "full_name": "acme/customer-portal",
  "url": "https://git.acme.com/acme/customer-portal",
  "description": "Customer-facing web portal",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z",
  "statistics": {
    "total_commits": 1234,
    "commits_last_30_days": 87,
    "active_contributors": 5,
    "last_commit_at": "2024-01-15T14:30:00Z"
  }
}
```

**Example Request:**

```bash
curl http://localhost:8000/api/v1/repositories/1
```

---

## Commits API

### Query Commits

Query commits with filters.

**Endpoint:** `GET /api/v1/commits`

**Query Parameters:**
- `repository_id` (optional): Filter by repository
- `author` (optional): Filter by author name
- `since` (optional): Start date (ISO 8601)
- `until` (optional): End date (ISO 8601)
- `limit` (optional, default: 50): Number of commits per page
- `offset` (optional, default: 0): Pagination offset

**Response:** `200 OK`

```json
{
  "commits": [
    {
      "id": 12345,
      "sha": "abc123def456",
      "repository": "customer-portal",
      "author_name": "John Doe",
      "author_email": "john@example.com",
      "timestamp": "2024-01-15T14:30:00Z",
      "title": "feat(auth): add OAuth2 support",
      "description": "Implemented OAuth2 authentication flow with support for Google and GitHub providers.",
      "files_changed": 8,
      "insertions": 245,
      "deletions": 67,
      "url": "https://git.acme.com/acme/customer-portal/commit/abc123def456"
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

**Example Requests:**

```bash
# All commits
curl http://localhost:8000/api/v1/commits

# Commits by repository
curl "http://localhost:8000/api/v1/commits?repository_id=1"

# Commits by author
curl "http://localhost:8000/api/v1/commits?author=John%20Doe"

# Commits in date range
curl "http://localhost:8000/api/v1/commits?since=2024-01-01&until=2024-01-15"
```

---

### Get Commit Details

Get detailed information about a specific commit.

**Endpoint:** `GET /api/v1/commits/{sha}`

**Parameters:**
- `sha` (path, required): Commit SHA

**Response:** `200 OK`

```json
{
  "id": 12345,
  "sha": "abc123def456",
  "repository": {
    "id": 1,
    "name": "customer-portal",
    "full_name": "acme/customer-portal"
  },
  "author": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "timestamp": "2024-01-15T14:30:00Z",
  "message": {
    "title": "feat(auth): add OAuth2 support",
    "description": "Implemented OAuth2 authentication flow with support for Google and GitHub providers."
  },
  "statistics": {
    "files_changed": 8,
    "insertions": 245,
    "deletions": 67
  },
  "url": "https://git.acme.com/acme/customer-portal/commit/abc123def456"
}
```

**Example Request:**

```bash
curl http://localhost:8000/api/v1/commits/abc123def456
```

---

## Health Check API

### Basic Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

**Example Request:**

```bash
curl http://localhost:8000/health
```

---

### Readiness Check

Check if the API is ready to serve requests (includes database connectivity).

**Endpoint:** `GET /health/ready`

**Response:** `200 OK`

```json
{
  "status": "ready",
  "checks": {
    "database": "connected",
    "gitea": "accessible",
    "llm": "available"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Error Response:** `503 Service Unavailable`

```json
{
  "status": "not_ready",
  "checks": {
    "database": "connected",
    "gitea": "error",
    "llm": "available"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example Request:**

```bash
curl http://localhost:8000/health/ready
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 201 | Created | Resource created |
| 202 | Accepted | Request accepted for processing |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Codes

```json
// Validation Error
{
  "detail": [
    {
      "loc": ["query", "date"],
      "msg": "Invalid date format",
      "type": "value_error"
    }
  ]
}

// Not Found
{
  "detail": "Report not found for 2024-01-15"
}

// Rate Limited
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

---

## Rate Limiting

### Limits (MVP v1)

- **Default:** 100 requests per minute per IP
- **Authenticated:** 1000 requests per minute per token

### Headers

Response includes rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

### Rate Limit Exceeded

**Response:** `429 Too Many Requests`

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

---

## Examples

### Python Example

```python
import httpx
import asyncio

async def get_latest_report():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/reports/daily/latest",
            headers={"Authorization": "Bearer your_token"}
        )
        response.raise_for_status()
        return response.json()

# Run
report = asyncio.run(get_latest_report())
print(report["executive_summary"])
```

### JavaScript Example

```javascript
async function getLatestReport() {
  const response = await fetch(
    'http://localhost:8000/api/v1/reports/daily/latest',
    {
      headers: {
        'Authorization': 'Bearer your_token'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// Usage
getLatestReport()
  .then(report => console.log(report.executive_summary))
  .catch(error => console.error('Error:', error));
```

### cURL Examples

```bash
# Get latest report
curl -H "Authorization: Bearer your_token" \
  http://localhost:8000/api/v1/reports/daily/latest

# Get specific date report
curl http://localhost:8000/api/v1/reports/daily/2024-01-15

# Query commits by author
curl "http://localhost:8000/api/v1/commits?author=John%20Doe&limit=10"

# List repositories
curl http://localhost:8000/api/v1/repositories

# Health check
curl http://localhost:8000/health/ready
```

---

## Versioning

### Current Version

**v1** - Initial MVP release

### Version Strategy

- **URL Versioning:** Version in path (`/api/v1/`)
- **Backward Compatibility:** Maintained within major version
- **Deprecation:** 6-month notice before removal
- **Migration Guides:** Provided for major version changes

### Future Versions

Future API versions will be announced with:
- Migration guide
- Deprecation timeline
- Breaking changes list
- New features documentation

---

## Related Documentation

- [System Architecture](../architecture/system-overview.md)
- [Data Flow](../architecture/data-flow.md)
- [Development Setup](../development/setup.md)
- [Contributing Guide](../../CONTRIBUTING.md)

---

**Last Updated:** 2026-06-17

**API Version:** 1.0.0