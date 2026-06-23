# Session Handoff

## What was built

This codebase now contains the complete MVP v1 pipeline across all six slices from `docs/product/mvp/product-slices.md`.

---

## Decisions carried forward

| Decision | Value |
|----------|-------|
| LLM provider | OpenAI `gpt-4o-mini` |
| Report language | English default (`REPORT_LOCALE=en`); Persian (`fa`) via env var |
| API auth | Single static `API_SECRET_KEY` env-var bearer token |
| Diff truncation | ~10 lines of unified diff per file at generation time; discarded after (ADR-012) |
| Gitea HTTP client | `httpx` (async) |
| DB | User-provided `DATABASE_URL`; docker-compose runs Postgres 16 for dev/prod |
| LLM calls per report | 4 separate calls (exec summary, per-repo, per-contributor, management notes) |

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
│   └── config.py          # Pydantic Settings — reads all env vars
├── db/
│   └── session.py         # Async SQLAlchemy engine + session factory
├── models/
│   └── orm.py             # Repository, Commit, Report ORM models
├── services/
│   ├── aggregator.py      # Aggregate commits into per-repo / per-contributor structures
│   ├── ai.py              # OpenAI calls for all four report sections
│   ├── gitea.py           # GiteaClient — connect, list repos, fetch commits, fetch diffs
│   ├── ingest.py          # upsert_repository, ingest_commit, query_commits_for_day
│   └── report.py          # build_report — template path + AI path + fallback
├── collector.py           # CLI: python -m app.collector [YYYY-MM-DD]
├── main.py                # FastAPI app entry point
└── reporter.py            # CLI: python -m app.reporter [YYYY-MM-DD] (template, no LLM)

alembic/
├── versions/
│   ├── 0001_initial_schema.py   # repositories + commits tables
│   └── 0002_add_reports.py      # reports table
├── env.py
└── script.py.mako

scripts/
└── deliver.sh             # Bash delivery script for Rocket.Chat (Slice 6)

Dockerfile                 # python:3.12-slim, non-root user, runs migrations on start
docker-compose.yml         # db (Postgres 16) + api; DATABASE_URL auto-overridden
.dockerignore

docs/
├── api/README.md                    # updated — matches actual endpoints
├── development/setup.md             # updated — correct env vars, Docker section
├── development/docker.md            # new — Docker deployment guide
└── product/manager-guide.md        # new — for non-technical managers
```

---

## Environment variables

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | yes (local) | Overridden by docker-compose; `postgresql+asyncpg://cogence:cogence@localhost:5432/cogence` for local dev |
| `GITEA_URL` | yes | Base URL of the Gitea instance |
| `GITEA_TOKEN` | yes | Personal access token |
| `API_SECRET_KEY` | yes | Static bearer token for the Cogence API |
| `OPENAI_API_KEY` | yes | Used by Slice 4 AI summaries |
| `OPENAI_MODEL` | no | Defaults to `gpt-4o-mini` |
| `ATOMIC_COMMIT_THRESHOLD` | no | Defaults to `10` files |
| `REPORT_LOCALE` | no | `en` or `fa`; defaults to `en` |

---

## How to run

### With Docker (recommended)

```bash
cp .env.example .env
# fill in GITEA_URL, GITEA_TOKEN, API_SECRET_KEY, OPENAI_API_KEY

docker compose up -d
# migrations run automatically

curl http://localhost:8000/health/ready
curl -X POST -H "Authorization: Bearer $API_SECRET_KEY" \
  http://localhost:8000/api/v1/reports/daily/$(date +%Y-%m-%d)/generate
```

### Local (no Docker)

```bash
docker compose up -d db        # only start Postgres
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# collect + template report (no LLM):
python -m app.reporter 2026-06-23

# collect only:
python -m app.collector 2026-06-23
```

---

## Slice completion

| Slice | Status | Key output |
|-------|--------|------------|
| 1 — Collect commits | done | `app/services/gitea.py`, `app/collector.py` |
| 2 — Persist commits | done | `app/services/ingest.py`, `app/models/orm.py`, migration 0001 |
| 3 — Template report | done | `app/services/aggregator.py`, `app/reporter.py` |
| 4 — AI summaries | done | `app/services/ai.py`, `app/services/report.py` |
| 5 — Report API | done | `app/api/`, `app/main.py`, migration 0002 |
| 6 — Delivery script | done | `scripts/deliver.sh` |

---

## Pilot exit criteria status

| Criterion | Status |
|-----------|--------|
| `POST .../daily/{date}/generate` produces correct report idempotently | ready |
| Delivery script posts to Rocket.Chat at 07:00 Tehran | ready (needs cron setup) |
| Manager confirms readability in < 60 seconds (Persian locale) | pending pilot |
| Factual accuracy spot-check | pending pilot |
| No surveillance patterns in output | built-in (no rankings, no scores) |

---

## What is next (post-MVP)

All remaining items are in `docs/product/backlog.md`. Top candidates for a second iteration:

- `REPORT_LOCALE=fa` testing with a real manager
- Contributor identity merging (multiple emails → one person)
- Repository allowlists / exclude rules
- Report depth tiers (`brief`, `deep`)
- Built-in Rocket.Chat delivery channel
