# Docker Deployment

How to run Cogence anywhere using Docker Compose.

The stack is two containers: **`db`** (Postgres 16) and **`api`** (Cogence + Alembic migrations).
Migrations run automatically when the API container starts.

---

## Prerequisites

- Docker Engine 24+ and Docker Compose v2 (`docker compose` not `docker-compose`)
- A running Gitea instance the server can reach
- An OpenAI API key

---

## Quick Start

```bash
# 1. Copy and fill in secrets
cp .env.example .env
$EDITOR .env

# 2. Start everything (first run builds the image)
docker compose up -d

# 3. Verify
curl http://localhost:8000/health/ready
# → {"status": "ready"}

# 4. Generate today's report
curl -s -X POST \
  -H "Authorization: Bearer $API_SECRET_KEY" \
  http://localhost:8000/api/v1/reports/daily/$(date +%Y-%m-%d)/generate
```

---

## Environment Variables

Set these in `.env` before running `docker compose up`.

| Variable | Required | Example |
|----------|----------|---------|
| `GITEA_URL` | yes | `https://gitea.example.com` |
| `GITEA_TOKEN` | yes | Gitea personal access token |
| `API_SECRET_KEY` | yes | Random string — use `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `OPENAI_API_KEY` | yes | `sk-...` |
| `OPENAI_MODEL` | no | `gpt-4o-mini` (default) |
| `ATOMIC_COMMIT_THRESHOLD` | no | `10` (default) |
| `REPORT_LOCALE` | no | `en` or `fa` (default: `en`) |

`DATABASE_URL` is set automatically by `docker-compose.yml` to point at the `db` service.
You can leave it as-is in `.env` or remove it — the compose file always overrides it.

---

## Services

```
api   → http://localhost:8000   (Cogence API + Alembic migrations on start)
db    → localhost:5432           (Postgres 16 — port exposed for local access)
```

Data is persisted in the `postgres_data` Docker volume.

---

## Common Operations

```bash
# Tail API logs
docker compose logs -f api

# Check DB connectivity
curl http://localhost:8000/health/ready

# Run migrations manually (normally done automatically on start)
docker compose exec api alembic upgrade head

# Open a Postgres shell
docker compose exec db psql -U cogence cogence

# Restart only the API (after a code change)
docker compose build api && docker compose up -d api

# Stop everything (data preserved)
docker compose down

# Stop and delete all data
docker compose down -v
```

---

## Updating Cogence

```bash
git pull
docker compose build api
docker compose up -d api
# Migrations run automatically on restart
```

---

## Production Checklist

- [ ] `API_SECRET_KEY` is a random 32+ character string
- [ ] `OPENAI_API_KEY` is a valid production key
- [ ] Postgres port `5432` is **not** exposed to the internet (remove or bind to `127.0.0.1` in `docker-compose.yml`)
- [ ] API port `8000` is behind a reverse proxy (nginx/Caddy) with HTTPS
- [ ] Docker volume backup is scheduled (`postgres_data`)
- [ ] Log rotation is configured for Docker containers

---

## Delivery Script (Cron)

The `scripts/deliver.sh` script runs outside Docker. It calls the Cogence API and posts the result to Rocket.Chat. Schedule it on any machine that can reach the API:

```bash
# /etc/cron.d/cogence-deliver  (runs at 07:00 Tehran time)
0 7 * * * root TZ=Asia/Tehran COGENCE_API_URL=http://your-server:8000 \
  COGENCE_API_KEY=your-key ROCKETCHAT_WEBHOOK=https://... \
  /path/to/cogence/scripts/deliver.sh >> /var/log/cogence-deliver.log 2>&1
```

---

**Last Updated:** 2026-06-24
