# Cogence Engineering Glossary

## Overview

This glossary defines key terms used throughout the Cogence project. It serves as the **Ubiquitous Language** for the domain, ensuring consistent terminology across documentation, code, and communication.

---

## Core Domain Terms

### Activity
Engineering work represented by commits and other signals. Not to be confused with "productivity" which implies measurement and comparison.

**Usage:** "High activity on customer-facing projects"  
**Avoid:** "High productivity" (implies scoring)

---

### Aggregate
A cluster of domain objects that can be treated as a single unit. In Cogence, Repository and Report are aggregates.

**Example:** Repository aggregate includes the repository and its commits.

---

### Business Language
Non-technical terminology understandable by managers and executives. The opposite of technical jargon.

**Example:** "Authentication improvements" instead of "Refactored OAuth2 implementation"

---

### Commit
A Git commit with metadata including SHA, author, timestamp, message, and statistics. The primary signal in Cogence MVP v1.

**Not:** "Change", "Update", "Modification"  
**Related:** Signal, Repository, Contributor

---

### Contributor
A person who authors commits. Identified by email address. Not to be ranked, scored, or compared.

**Not:** "Developer", "Engineer", "Programmer" (too specific)  
**Related:** Commit, Author

---

### Daily Report
A generated summary of engineering activity for a 24-hour period. The primary deliverable of Cogence MVP v1.

**Not:** "Dashboard", "Analytics", "Metrics"  
**Related:** Report, Summary

---

### Domain Model
The conceptual model of the business domain, including entities, relationships, and business rules.

**Related:** Entity, Aggregate, Value Object

---

### Engineering Intelligence
The transformation of engineering signals into actionable business insights. The core value proposition of Cogence.

**Not:** "Analytics", "Metrics", "Monitoring"

---

## Data Terms

### Author
The person who created a commit. Represented by name and email in Git metadata.

**Related:** Contributor, Commit

---

### Collection
The process of fetching commits from Gitea and storing them in the database.

**Not:** "Scraping", "Pulling", "Harvesting"  
**Related:** Data Collection, Gitea

---

### Gitea
The Git platform being integrated with in MVP v1. Source of commit data.

**Related:** Repository, Commit, API

---

### Metadata
Additional information about an entity, such as commit statistics or report generation details.

**Example:** Commit metadata includes files changed, insertions, deletions.

---

### Repository
A Git repository being tracked by Cogence. Contains commits and belongs to an organization.

**Not:** "Project", "Codebase", "Repo" (informal)  
**Related:** Commit, Organization

---

### SHA
The unique 40-character hexadecimal identifier for a Git commit.

**Example:** `abc123def456789...`  
**Related:** Commit

---

### Signal
A data point from engineering activity. In MVP v1, commits are the primary signal.

**Not:** "Metric", "Measurement", "Data point"  
**Related:** Commit, Activity

---

## Report Terms

### Executive Summary
A 2-4 sentence overview of engineering activity, written in business language. The first section of a daily report.

**Requirements:** Business language, concise, factual, actionable  
**Related:** Daily Report, Summary

---

### Management Notes
Observations and recommendations for leadership. The final section of a daily report.

**Purpose:** Highlight patterns, risks, and action items  
**Related:** Daily Report, Actionable

---

### Project Summary
A brief description of work done in a repository. Part of the daily report.

**Format:** One sentence per repository  
**Related:** Repository, Daily Report

---

### Contributor Summary
A brief description of an individual's contributions. Part of the daily report.

**Requirements:** Neutral, respectful, no ranking or scoring  
**Related:** Contributor, Daily Report

---

### Summary
AI-generated business-readable text that translates technical activity into business language.

**Not:** "Description", "Translation", "Explanation"  
**Related:** LLM, Business Language

---

### Observability Gap
A neutral note when a contributor's commit message did not carry enough information; the summary relied on other signals (e.g. truncated diff).

**Not:** "Bad committer", "Poor performer", "Non-compliant"  
**Related:** Commit Culture, Contributor Summary, ADR-004

---

### Report Depth
How much source material the LLM reads when generating a report: `brief`, `standard`, or `deep`. MVP v1 implements `standard` only.

**Related:** Daily Report, Standard Report, Truncated Diff

---

### Report Locale
The configured language for generated report text (e.g. `fa` for Persian, `en` for English).

**Not:** Auto-detected language, mixed-locale output  
**Related:** Business Language, Daily Report

---

### Calendar Day
One full day in `Asia/Tehran` from 00:00 to 23:59. The period a Daily Report covers.

**Not:** "Last 24 hours", rolling window  
**Related:** Daily Report, Report Date

---

## Technical Terms

### API
Application Programming Interface. Cogence provides a REST API for accessing reports and data.

**Related:** REST, Endpoint, JSON

---

### Endpoint
A specific URL path in the API that performs a function.

**Example:** `/api/v1/reports/daily/latest`  
**Related:** API, REST

---

### LLM
Large Language Model. Used to generate business-readable summaries from commit data.

**Example:** GPT-4, Claude  
**Related:** AI, Summary Generation

---

### PostgreSQL
The relational database used as the system of record for Cogence.

**Related:** Database, Schema, SQL

---

### REST
Representational State Transfer. The architectural style for the Cogence API.

**Related:** API, HTTP, JSON

---

### Schema
The structure of the database, including tables, columns, and relationships.

**Related:** Database, PostgreSQL, Migration

---

## Process Terms

### Actionable
Providing clear next steps or recommendations. A key principle for reports.

**Example:** "Consider reviewing authentication changes with security team"  
**Not:** "There were authentication changes" (not actionable)

---

### Aggregation
Combining multiple data points into a summary or total.

**Example:** Aggregating commits by repository or contributor  
**Related:** Summary, Report Generation

---

### Collection Schedule
The configured frequency for fetching commits from Gitea. Daily in MVP v1.

**Related:** Scheduled Task, Data Collection

---

### Generation
The process of creating a report from commit data using AI.

**Not:** "Building", "Compiling", "Creating"  
**Related:** Report, LLM, Summary

---

### Regeneration
Creating a new version of an existing report, typically after fixing an issue.

**Related:** Report, Generation

---

### Validation
Checking data for correctness and completeness before storage or processing.

**Related:** Data Quality, Error Handling

---

## Quality Terms

### Business-Readable
Understandable by non-technical managers without explanation or translation.

**Test:** Can a CEO understand this without asking an engineer?  
**Related:** Business Language, Jargon-Free

---

### Concise
Brief and to the point. Reports should be readable in under 60 seconds.

**Related:** Readability, Executive Summary

---

### Factual
Based on actual data, not assumptions or speculation. AI summaries must be grounded in commit data.

**Related:** Accuracy, Trustworthy

---

### Privacy-Respecting
Not using data for surveillance or individual performance measurement.

**Principle:** Signals over surveillance (ADR-004)  
**Related:** Contributor, Ethics

---

### Trustworthy
Accurate, reliable, and honest. A core principle for Cogence.

**Related:** Accuracy, Factual, Transparency

---

## Anti-Patterns (Terms to Avoid)

### ❌ Lines of Code (LOC)
A productivity metric that should never be mentioned in reports.

**Why:** Not a measure of value or quality  
**Use instead:** "Improvements", "Changes", "Work"

---

### ❌ Productivity
Implies measurement and comparison of individuals.

**Why:** Violates privacy and surveillance principles  
**Use instead:** "Activity", "Contributions", "Work"

---

### ❌ Ranking
Ordering contributors by any metric.

**Why:** Violates ADR-004 (Signals over Surveillance)  
**Use instead:** Alphabetical listing with neutral descriptions

---

### ❌ Scoring
Assigning numerical values to contributors or their work.

**Why:** Surveillance, not intelligence  
**Use instead:** Qualitative descriptions

---

### ❌ Technical Jargon
Terms like "refactored", "async/await", "dependency injection", etc.

**Why:** Not business-readable  
**Use instead:** Business language translations

---

## Acronyms

| Acronym | Full Term | Definition |
|---------|-----------|------------|
| ADR | Architecture Decision Record | Document explaining a significant architectural decision |
| API | Application Programming Interface | Interface for programmatic access to Cogence |
| CEO | Chief Executive Officer | Primary target user for reports |
| CI/CD | Continuous Integration/Continuous Deployment | Automated build and deployment (out of scope for MVP) |
| CTO | Chief Technology Officer | Technical leadership user persona |
| JSON | JavaScript Object Notation | Data format for API responses |
| LLM | Large Language Model | AI used for summary generation |
| LOC | Lines of Code | Metric to avoid in reports |
| MVP | Minimum Viable Product | Initial release version |
| REST | Representational State Transfer | API architectural style |
| SHA | Secure Hash Algorithm | Git commit identifier |
| SQL | Structured Query Language | Database query language |
| UTC | Coordinated Universal Time | Timezone for all timestamps |

---

## Phrases and Idioms

### "Business-Readable"
Written in language that non-technical managers can understand without explanation.

**Example:** "Authentication improvements" not "OAuth2 refactoring"

---

### "Readable in Under 60 Seconds"
A report quality metric. The entire report should be scannable in one minute.

**Breakdown:** 15s executive summary, 30s projects, 15s contributors

---

### "Signals Over Surveillance"
A core principle (ADR-004). Focus on organizational insights, not individual monitoring.

**Means:** No productivity metrics, rankings, or scoring

---

### "System of Record"
The authoritative source of truth for data. PostgreSQL is the system of record for Cogence.

**Related:** Database, Source of Truth

---

### "Ubiquitous Language"
Consistent terminology used throughout the project, from code to documentation to conversation.

**Source:** Domain-Driven Design  
**Related:** Glossary, Domain Model

---

## Context-Specific Terms

### In Code

**Entity:** A domain object with identity (Repository, Commit, Report)  
**Value Object:** An object defined by its attributes (Summary, Metadata)  
**Service:** A stateless operation (ReportGenerationService)  
**Repository (Pattern):** Data access abstraction (not Git repository)

---

### In Documentation

**ADR:** Architecture Decision Record  
**FR:** Functional Requirement  
**NFR:** Non-Functional Requirement  
**AC:** Acceptance Criteria

---

### In API

**Endpoint:** URL path for API operation  
**Resource:** Entity exposed via API (reports, repositories, commits)  
**Payload:** Request or response body  
**Status Code:** HTTP response code (200, 404, 500, etc.)

---

## Related Documentation

- [Domain Model](../architecture/domain-model.md) - Detailed domain concepts
- [Product Vision](vision.md) - Why these terms matter
- [Product Principles](principles.md) - Guiding principles
- [ADRs](../adr/) - Architecture decisions

---

## Glossary Maintenance

### Adding New Terms

1. Ensure term is used consistently in codebase
2. Add definition with context
3. Include examples and anti-patterns
4. Link to related terms
5. Update related documentation

### Updating Terms

1. Document reason for change
2. Update all references in codebase
3. Update related documentation
4. Communicate change to team

---

**Last Updated:** 2026-06-19

**Version:** 1.0.0