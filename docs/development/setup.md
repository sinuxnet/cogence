# Cogence Development Setup Guide

Complete guide for setting up a local development environment for Cogence.

---

## Prerequisites

### Required Software

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads/)

### Optional Tools

- **Docker** - For containerized development
- **VS Code** - Recommended IDE with Python extension
- **Postman/Insomnia** - For API testing

### System Requirements

- **OS:** Windows 10+, macOS 10.15+, or Linux
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 2GB free space

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/cogence.git
cd cogence

# Run bootstrap script
./scripts/bootstrap.sh  # macOS/Linux
# or
.\scripts\bootstrap.ps1  # Windows

# Start development server
./scripts/dev.sh
```

---

## Detailed Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/cogence.git
cd cogence
```

### 2. Python Environment

#### Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

#### Verify Python Version

```bash
python --version
# Should be 3.11 or higher
```

### 3. Install Dependencies

#### Production Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Development Dependencies

```bash
pip install -r requirements-dev.txt
```

**requirements-dev.txt** includes:
- pytest - Testing framework
- pytest-asyncio - Async test support
- pytest-cov - Coverage reporting
- black - Code formatter
- mypy - Type checker
- ruff - Fast linter
- httpx - HTTP client for testing

### 4. Database Setup

#### Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql-15
sudo systemctl start postgresql
```

**Windows:**
Download installer from [postgresql.org](https://www.postgresql.org/download/windows/)

#### Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE cogence_dev;
CREATE USER cogence_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE cogence_dev TO cogence_user;

# Exit psql
\q
```

#### Verify Connection

```bash
psql -U cogence_user -d cogence_dev -h localhost
```

### 5. Environment Configuration

#### Create .env File

```bash
cp .env.example .env
```

#### Edit .env

```bash
# Database (use localhost for local dev; docker-compose overrides this automatically)
DATABASE_URL=postgresql+asyncpg://cogence:cogence@localhost:5432/cogence

# Gitea
GITEA_URL=https://your-gitea-instance.com
GITEA_TOKEN=your_gitea_access_token

# API auth — single static bearer token for all API clients
API_SECRET_KEY=change_this_to_a_random_secret

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Report settings
ATOMIC_COMMIT_THRESHOLD=10
REPORT_LOCALE=en   # en or fa
```

#### Generate API Secret Key

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Database Migrations

```bash
# Apply all migrations (migrations are pre-written, not auto-generated)
alembic upgrade head
```

#### Verify Tables

```bash
psql -U cogence -d cogence -c "\dt"
```

Should show tables: `repositories`, `commits`, `reports`

### 7. Verify Setup

#### Run Tests

```bash
pytest
```

#### Check Code Quality

```bash
# Format code
black .

# Type checking
mypy app/

# Linting
ruff check .
```

#### Start Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Test API

```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "ok"}
```

---

## Development Workflow

### Daily Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 2. Pull latest changes
git pull origin develop

# 3. Install any new dependencies
pip install -r requirements.txt

# 4. Run migrations
alembic upgrade head

# 5. Start development server
uvicorn app.main:app --reload
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_collector.py

# With coverage
pytest --cov=app tests/

# Coverage report
pytest --cov=app --cov-report=html tests/
open htmlcov/index.html
```

### Code Quality Checks

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linting
ruff check app/ tests/

# Fix auto-fixable issues
ruff check --fix app/ tests/
```

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (CAUTION: Deletes all data)
alembic downgrade base
alembic upgrade head
```

---

## IDE Setup

### VS Code

#### Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-yaml"
  ]
}
```

#### Settings (.vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.tabSize": 4
  }
}
```

### PyCharm

1. Open project directory
2. Configure Python interpreter: `Settings > Project > Python Interpreter`
3. Select virtual environment: `venv/bin/python`
4. Enable pytest: `Settings > Tools > Python Integrated Tools > Testing`
5. Configure code style: `Settings > Editor > Code Style > Python`

---

## Docker Setup

Docker is the recommended way to run Cogence. See [docker.md](docker.md) for the full deployment guide.

### Quick Start with Docker

```bash
cp .env.example .env
# fill in GITEA_URL, GITEA_TOKEN, API_SECRET_KEY, OPENAI_API_KEY in .env

docker compose up -d
# migrations run automatically on first start

curl http://localhost:8000/health
```

### Useful Docker Commands

```bash
# View API logs
docker compose logs -f api

# Run migrations manually
docker compose exec api alembic upgrade head

# Stop services (data preserved in volume)
docker compose down

# Stop and wipe all data
docker compose down -v
```

---

## Troubleshooting

### Python Version Issues

**Problem:** Wrong Python version

**Solution:**
```bash
# Install pyenv (version manager)
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0
pyenv local 3.11.0
```

### Database Connection Issues

**Problem:** Cannot connect to PostgreSQL

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status postgresql
   
   # Windows
   # Check Services app
   ```

2. **Verify credentials:**
   ```bash
   psql -U cogence_user -d cogence_dev -h localhost
   ```

3. **Check DATABASE_URL in .env:**
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/database
   ```

### Migration Issues

**Problem:** Alembic migration fails

**Solutions:**

1. **Check database connection**
2. **Reset migrations (CAUTION):**
   ```bash
   alembic downgrade base
   alembic upgrade head
   ```

3. **Manual migration:**
   ```bash
   psql -U cogence_user -d cogence_dev < migration.sql
   ```

### Import Errors

**Problem:** Module not found

**Solutions:**

1. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check virtual environment is activated:**
   ```bash
   which python  # Should point to venv
   ```

3. **Add project to PYTHONPATH:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:${PWD}"
   ```

### Port Already in Use

**Problem:** Port 8000 already in use

**Solutions:**

1. **Find and kill process:**
   ```bash
   # macOS/Linux
   lsof -ti:8000 | xargs kill -9
   
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Use different port:**
   ```bash
   uvicorn app.main:app --port 8001
   ```

---

## Useful Commands

### Development Scripts

```bash
# Bootstrap environment
./scripts/bootstrap.sh

# Start development server
./scripts/dev.sh

# Run linting
./scripts/lint.sh

# Create release
./scripts/release.sh
```

### Database Commands

```bash
# Backup database
pg_dump -U cogence_user cogence_dev > backup.sql

# Restore database
psql -U cogence_user cogence_dev < backup.sql

# Drop and recreate
dropdb -U cogence_user cogence_dev
createdb -U cogence_user cogence_dev
```

### Testing Commands

```bash
# Run specific test
pytest tests/unit/test_collector.py::test_fetch_commits

# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

---

## Next Steps

After setup is complete:

1. **Read the documentation:**
   - [Architecture Overview](../architecture/system-overview.md)
   - [API Documentation](../api/README.md)
   - [Contributing Guide](../../CONTRIBUTING.md)

2. **Explore the codebase:**
   - Review existing code
   - Understand project structure
   - Read ADRs for context

3. **Start developing:**
   - Pick an issue from GitHub
   - Create feature branch
   - Write tests
   - Submit pull request

---

## Getting Help

- **Documentation:** Check docs/ directory
- **Issues:** Open GitHub issue
- **Questions:** Start GitHub Discussion
- **Chat:** Join team Slack/Discord

---

## Related Documentation

- [Contributing Guide](../../CONTRIBUTING.md)
- [Architecture Overview](../architecture/system-overview.md)
- [Testing Strategy](../testing/strategy.md)
- [API Documentation](../api/README.md)

---

**Last Updated:** 2026-06-17