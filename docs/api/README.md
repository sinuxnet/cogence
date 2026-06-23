# Cogence API Documentation

REST API for Cogence MVP v1.

**Base URL:** `http://localhost:8000` (development) / `http://your-server:8000` (production)

**Interactive docs:** `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

All `/api/v1/reports/` endpoints require a bearer token matching the `API_SECRET_KEY` env var.

```
Authorization: Bearer <API_SECRET_KEY>
```

Health endpoints (`/health`, `/health/ready`) do not require authentication.

---

## Report Endpoints

### Generate daily report

Collect commits from Gitea, generate an AI summary, and store the result.
**Idempotent** — calling the same date twice returns the stored report without re-generating.

```
POST /api/v1/reports/daily/{date}/generate
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `date` | path | Calendar day in `YYYY-MM-DD` (Asia/Tehran timezone) |

**Response `200 OK`:**

```json
{
  "report_date": "2026-06-23",
  "report_type": "daily",
  "report_depth": "standard",
  "locale": "en",
  "timezone": "Asia/Tehran",
  "executive_summary": "Engineering focused on customer-facing improvements...",
  "repositories": [
    {
      "name": "customer-portal",
      "summary": "Authentication improvements and user experience enhancements."
    }
  ],
  "contributors": [
    {
      "name": "Ali Rezaei",
      "summary": "Worked on authentication and user management features."
    }
  ],
  "management_notes": "High activity on customer-facing repositories...",
  "metadata": {
    "generated_at": "2026-06-24T07:00:00+03:30",
    "delivery": ["api"],
    "total_commits": 12,
    "total_repositories": 2,
    "total_contributors": 3,
    "non_atomic_commits": 1,
    "atomic_commit_threshold": 10,
    "generation_duration_ms": 4210,
    "llm_model": "gpt-4o-mini",
    "llm_tokens_used": 1340
  }
}
```

**Empty-day report** (no commits on that date):

```json
{
  "report_date": "2026-06-23",
  "executive_summary": "No engineering activity was recorded on 2026-06-23.",
  "repositories": [],
  "contributors": [],
  "management_notes": "This may reflect a holiday or non-coding day.",
  "metadata": {
    "total_commits": 0,
    "llm_model": null,
    "llm_tokens_used": null
  }
}
```

**Example:**

```bash
curl -s -X POST \
  -H "Authorization: Bearer $API_SECRET_KEY" \
  http://localhost:8000/api/v1/reports/daily/2026-06-23/generate
```

---

### Get report by date

```
GET /api/v1/reports/daily/{date}
```

Returns the stored report for the given date. `404` if `generate` has not been called for that date.

**Example:**

```bash
curl -s -H "Authorization: Bearer $API_SECRET_KEY" \
  http://localhost:8000/api/v1/reports/daily/2026-06-23
```

---

### Get latest report

```
GET /api/v1/reports/daily/latest
```

Returns the most recently generated report. `404` if no reports exist yet.

**Example:**

```bash
curl -s -H "Authorization: Bearer $API_SECRET_KEY" \
  http://localhost:8000/api/v1/reports/daily/latest
```

---

## Health Endpoints

### Liveness

```
GET /health
```

Returns `200 OK` as long as the process is running.

```json
{"status": "ok"}
```

### Readiness

```
GET /health/ready
```

Returns `200 OK` when the database is reachable. Returns `503` otherwise.

```json
{"status": "ready"}
```

---

## Error Responses

| Code | When |
|------|------|
| 401 | Missing or invalid `Authorization` header |
| 404 | Report not found for the given date |
| 422 | `date` is not a valid `YYYY-MM-DD` string |
| 503 | Database unreachable (`/health/ready` only) |

All errors return:

```json
{"detail": "Human-readable message"}
```

---

## Delivery script

For automated morning delivery to Rocket.Chat, see `scripts/deliver.sh`. It calls `generate` for yesterday's date and posts the result to a Rocket.Chat webhook. Intended to be run via cron at `07:00 Asia/Tehran`.

---

**Last Updated:** 2026-06-24

**API Version:** 1.0.0
