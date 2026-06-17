# Cogence

**Engineering Intelligence Platform**

Transform engineering activity into clear, actionable, business-readable intelligence.

## Overview

Cogence automatically analyzes signals from software development teams and converts them into concise reports that help non-technical leaders understand what engineering accomplished, what's happening, and what requires attention.

### The Problem

Engineering teams create enormous amounts of information daily through commits, deployments, pull requests, and discussions. Yet most non-technical leaders cannot easily understand this information, creating a gap between those building software and those making business decisions.

### The Solution

Cogence bridges that gap by continuously analyzing engineering signals and generating business-readable reports that answer:

- **What did engineering accomplish?**
- **What are teams working on?**
- **Where are risks emerging?**
- **What should leadership know?**

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/cogence.git
cd cogence

# Set up development environment
./scripts/bootstrap.sh

# Run development server
./scripts/dev.sh
```

## MVP v1 Focus

The first version focuses on one question: **"What did we do during the last 24 hours?"**

**Data Sources:** Gitea repositories and Git commits only

**Output:** Daily business-readable report with:
- Executive summary
- Projects worked on
- Contributor activities
- Management notes

See [MVP v1 Documentation](docs/product/mvp/MVP-v1.md) for details.

## Documentation

### Product Documentation
- [Vision](docs/product/vision.md) - Why Cogence exists
- [Principles](docs/product/principles.md) - Core design principles
- [Requirements](docs/product/requirements.md) - Functional requirements
- [Target Users](docs/product/target-users.md) - Who we're building for
- [Roadmap](docs/product/roadmap.md) - Future plans
- [Glossary](docs/product/glossary.md) - Key terminology

### Architecture Documentation
- [System Overview](docs/architecture/system-overview.md) - High-level architecture
- [Backend](docs/architecture/backend.md) - FastAPI implementation
- [Database](docs/architecture/database.md) - PostgreSQL schema
- [Frontend](docs/architecture/frontend.md) - UI specifications
- [Security](docs/architecture/security.md) - Security considerations
- [Deployment](docs/architecture/deployment.md) - Deployment strategy

### Development
- [Setup Guide](docs/development/setup.md) - Development environment setup
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Git Conventions](docs/engineering/git-commit-convention.md) - Commit message format
- [Testing Strategy](docs/testing/strategy.md) - Testing approach

### Architecture Decision Records (ADRs)
- [ADR-001](docs/adr/ADR-001-commits-as-source-of-truth.md) - Commits as source of truth
- [ADR-002](docs/adr/ADR-002-business-language-reporting.md) - Business language in reports
- [ADR-003](docs/adr/ADR-003-no-code-analysis-in-mvp.md) - No code analysis in MVP
- [ADR-004](docs/adr/ADR-004-signals-over-surveillance.md) - Signals over surveillance
- [ADR-005](docs/adr/ADR-005-ai-generates-summaries-not-facts.md) - AI generates summaries
- [ADR-006](docs/adr/ADR-006-daily-report-first.md) - Daily report first
- [ADR-007](docs/adr/ADR-007-human-readability-over-analytics.md) - Human readability priority
- [ADR-008](docs/adr/ADR-008-single-tenant-internal-first.md) - Single-tenant approach
- [ADR-009](docs/adr/ADR-009-fastapi-backend.md) - FastAPI backend choice
- [ADR-010](docs/adr/ADR-010-postgresql-system-of-record.md) - PostgreSQL as system of record
- [ADR-011](docs/adr/ADR-011-scheduled-data-collection.md) - Scheduled data collection

## Technology Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Data Source:** Gitea API
- **AI:** LLM for report generation
- **Deployment:** Single-tenant, internal-first

## Core Principles

1. **Business First** - Reports for managers, not engineers
2. **Signals Over Surveillance** - Understand work, don't monitor people
3. **Context Before Metrics** - Explain what happened, not just numbers
4. **Explainability Over Mystery** - Transparent AI summaries
5. **Human-Centered Reporting** - Readable in under 60 seconds

## Project Status

🚧 **In Development** - MVP v1

Current focus: Building the core daily report generation system.

## License

See [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

For questions or issues, please open a GitHub issue.