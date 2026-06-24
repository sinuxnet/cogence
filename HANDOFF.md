# Session Handoff

## What was built

This codebase contains the complete MVP-v1 pipeline (6 slices) plus all MVP-v2 refinements.

---

## Decisions carried forward

| Decision | Value |
|----------|-------|
| LLM provider | OpenAI `gpt-4o-mini`, temperature=0.3 |
| Report language | English default (`REPORT_LOCALE=en`); Persian (`fa`) via env var |
| API auth | Single static `API_SECRET_KEY` env-var bearer token |
| Diff truncation | ~10 lines of unified diff per file; discarded after use (ADR-012) |
| Gitea HTTP client | `httpx` (async) |
| DB | User-provided `DATABASE_URL`; docker-compose runs Postgres 16 |
| LLM calls per report | 2 calls (per-repo, per-contributor) — executive summary and management notes removed in MVP-v2 |
| App version | `2.0.0` |

---

## Project structure

```
app/
├── api/
│   ├── deps.py            # Bearer auth dependency
│   └── routes/
│       ├── health.py      # GET /health, GET /health/ready
│       └── reports.py     # POST + GET report endpoints
├── core/
│   ├── config.py          # Pydantic Settings — reads all env vars
│   └── log_setup.py       # JSON structured logging (setup_logging, get_logger)
├── db/
│   └── session.py         # Async SQLAlchemy engine + session factory
├── models/
│   └── orm.py             # Repository, Commit, Report ORM models
├── services/
│   ├── aggregator.py      # Aggregate commits → RepositoryData, OrganizationData, ContributorData
│   ├── ai.py              # OpenAI calls: per-repo and per-contributor factual summaries only
│   ├── gitea.py           # GiteaClient — list repos (org-filtered), fetch commits + diffs
│   ├── ingest.py          # upsert_repository, ingest_commit, query_commits_for_day
│   └── report.py          # build_report — template path + AI path + fallback
├── collector.py           # CLI: python -m app.collector [YYYY-MM-DD]
├── main.py                # FastAPI app entry point; GET /api/version
└── reporter.py            # CLI: python -m app.reporter [YYYY-MM-DD] (template, no LLM)

alembic/
├── versions/
│   ├── 0001_initial_schema.py   # repositories + commits tables
│   └── 0002_add_reports.py      # reports table
├── env.py
└── script.py.mako

scripts/
└── deliver.sh             # Bash delivery; curl error handling per HTTP status code

Dockerfile                 # python:3.12-slim, non-root user, runs migrations on start
docker-compose.yml         # db (Postgres 16) + api; DATABASE_URL auto-overridden
```

---

## Environment variables

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | yes (local) | Overridden by docker-compose; `postgresql+asyncpg://cogence:cogence@localhost:5432/cogence` for local dev |
| `GITEA_URL` | yes | Base URL of the Gitea instance |
| `GITEA_TOKEN` | yes | Personal access token |
| `GITEA_ORGANIZATIONS` | yes* | Comma-separated org names to track. Empty = warn + fetch all |
| `GITEA_INCLUDE_PERSONAL` | no | `false` — include user-owned repos alongside org repos |
| `API_SECRET_KEY` | yes | Static bearer token for the Cogence API |
| `OPENAI_API_KEY` | yes | Used for AI summaries |
| `OPENAI_MODEL` | no | Defaults to `gpt-4o-mini` |
| `ATOMIC_COMMIT_THRESHOLD` | no | Defaults to `10` files |
| `REPORT_LOCALE` | no | `en` or `fa`; defaults to `en` |
| `LOG_LEVEL` | no | `INFO` (default). Set to `DEBUG` for verbose output |
| `LOG_FILE` | no | Optional path for JSON log file (stdout always logged) |

---

## Report JSON structure (v2)

```json
{
  "report_date": "2026-06-24",
  "report_type": "daily",
  "locale": "en",
  "timezone": "Asia/Tehran",
  "general": {
    "organizations_count": 2,
    "contributor_count": 3,
    "total_updates": 25
  },
  "projects": [
    {
      "organization": "acme",
      "repositories": [
        {"name": "backend", "update_count": 10, "summary": "..."}
      ]
    }
  ],
  "contributors": [{"name": "Abbas", "summary": "..."}],
  "metadata": {
    "generated_at": "...",
    "total_updates": 25,
    "total_organizations": 2,
    "total_repositories": 3,
    "total_contributors": 3,
    "non_atomic_commits": 0,
    "atomic_commit_threshold": 10,
    "generation_duration_ms": 1234,
    "llm_model": "gpt-4o-mini",
    "llm_tokens_used": 1500
  }
}
```

---

## How to run

### With Docker (recommended)

```bash
cp .env.example .env
# fill in GITEA_URL, GITEA_TOKEN, GITEA_ORGANIZATIONS, API_SECRET_KEY, OPENAI_API_KEY

docker compose up -d
# migrations run automatically

curl http://localhost:8000/health/ready
curl http://localhost:8000/api/version
curl -X POST -H "Authorization: Bearer $API_SECRET_KEY" \
  http://localhost:8000/api/v1/reports/daily/$(date +%Y-%m-%d)/generate
```

### Local (no Docker)

```bash
docker compose up -d db
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

python -m app.reporter 2026-06-24   # template report, no LLM
python -m app.collector 2026-06-24  # collect only
```

---

## Slice completion

### MVP-v1

| Slice | Status | Key output |
|-------|--------|------------|
| 1 — Collect commits | done | `app/services/gitea.py`, `app/collector.py` |
| 2 — Persist commits | done | `app/services/ingest.py`, `app/models/orm.py` |
| 3 — Template report | done | `app/services/aggregator.py`, `app/reporter.py` |
| 4 — AI summaries | done | `app/services/ai.py`, `app/services/report.py` |
| 5 — Report API | done | `app/api/`, `app/main.py` |
| 6 — Delivery script | done | `scripts/deliver.sh` |

### MVP-v2

| Slice | Status | Key changes |
|-------|--------|-------------|
| 1 — Fix Report Language | done | `_NEUTRAL_TONE` constant; forbidden phrases enforced in prompts; temperature=0.3 |
| 2 — Restructure Report Output | done | `OrganizationData` in aggregator; new `general/projects/contributors` JSON shape; "updates" not "commits" |
| 3 — Improve Error Handling (deliver.sh) | done | `curl -w "%{http_code}"` + `case` per status; timestamps on all log lines |
| 4 — Repository Filtering | done | `GITEA_ORGANIZATIONS` env var; org-owner filter in `gitea.py`; warns if unconfigured |
| 5 — Structured Logging | done | `app/core/log_setup.py`; JSON formatter; wired via FastAPI lifespan; key events in all services |
| 6 — API Versioning | done | `APP_VERSION = "2.0.0"`; `GET /api/version` endpoint |

---

## What is next (MVP-v3)

See `docs/product/mvp/MVP-v3.md`. Top candidates:

- Collector logging (`app/collector.py` still uses `print`)
- Unit tests: prompt validation (no forbidden phrases), report structure, org filtering, error handling
- Documentation: `docs/api/versioning.md`, `docs/engineering/logging.md`, updated `docs/examples/sample-report.json`
- `REPORT_LOCALE=fa` testing with a real manager
- Contributor identity merging (multiple emails → one person)
- Delivery channel built into the API
