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
| LLM calls per report | 1 call per repository (structured JSON contributions); per-contributor call removed in v0.3.0 |
| LLM output format | OpenAI JSON mode (`response_format=json_object`) returning `contributions[]` per repo |
| Jalali calendar | `jdatetime` library; active when `REPORT_LOCALE=fa` |
| App version | `3.0.0` |

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

## Report JSON structure (v3)

`contributors[]` and `general{}` removed. `repositories[].summary` replaced by `repositories[].contributions[]`.

```json
{
  "report_date": "2026-06-24",
  "report_type": "daily",
  "locale": "fa",
  "timezone": "Asia/Tehran",
  "projects": [
    {
      "organization": "acme",
      "repositories": [
        {
          "name": "backend",
          "update_count": 10,
          "contributions": [
            {"contributor": "Abbas", "description": "fixed token expiry check in login form"},
            {"contributor": "Abbas", "description": "added invoice list endpoint to billing module"},
            {"contributor": "Soheil", "description": "increased dashboard refresh interval from 30 to 45 minutes"}
          ]
        }
      ]
    }
  ],
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

### Rocket.Chat message format (fa locale)

```
گزارش روز 4 تیر 1404

## acme

### backend
- **Abbas**: fixed token expiry check in login form
- **Abbas**: added invoice list endpoint to billing module
- **Soheil**: increased dashboard refresh interval from 30 to 45 minutes

3 active repos · 5 contributions detected · 12 commits
```

First line is always Persian when `REPORT_LOCALE=fa` to force RTL rendering (ADR-014). Report Footer is always English regardless of locale.

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

### v0.3.0

| Slice | Status | Key changes |
|-------|--------|-------------|
| 1 — Per-goal attribution | planned | `contributions[]` replaces `summary` + `contributors[]`; LLM JSON mode (ADR-013, ADR-015) |
| 2 — RTL + Jalali locale | planned | Persian first line; `jdatetime`; English footer always (ADR-014) |
| 3 — Rocket.Chat markdown | planned | h1/h2/h3 headings in `deliver.sh`; drop Contributors block |
| 4 — LLM specificity | planned | Component-naming rule added to system prompt |
| 5 — Release | planned | `v0.3.0`, `jdatetime` in requirements, updated ADRs |

---

## What is next (MVP-v3+)

See `docs/product/mvp/MVP-v3.md`. Planned: enhanced commit intelligence, optional Jira context enrichment, cross-repository relevancy detection (deferred from v0.3.0 grilling session 2026-06-24).

Near-term candidates not yet scheduled:
- Contributor identity merging (multiple emails → one person)
- Unit tests: prompt validation, report structure, org filtering
- Collector logging (`app/collector.py` still uses `print`)
