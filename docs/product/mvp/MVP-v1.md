# Cogence MVP v1

## Objective

Validate that Cogence can automatically generate a useful, business-readable summary of engineering work performed during a calendar day.

Success is not measured by technical sophistication.

Success is measured by whether a non-technical manager can read the report in less than one minute and accurately understand what engineering worked on.

---

## Problem Statement

Managers often rely on meetings, manual updates, and individual conversations to understand engineering activity.

This process does not scale and creates information gaps between engineering teams and leadership.

Cogence aims to provide automatic visibility into engineering activity using development signals that already exist.

---

## MVP Question

The entire MVP is focused on answering one question:

> What did engineering accomplish on this calendar day?

Every feature included in MVP v1 must contribute directly to answering this question.

The report period is a **calendar day** in `Asia/Tehran` (00:00–23:59), not a rolling 24-hour window.

---

## Target Customer

MVP v1 targets **small businesses**:

* One non-technical manager (CEO, Founder, or similar)
* One to ten developers
* Roughly 20 or fewer Gitea repositories; typically fewer than six active on any given day

Primary reader personas:

* CEO
* Founder
* Engineering Manager
* Product Manager

See [target-users.md](../target-users.md) for details.

Characteristics:

* Limited visibility into day-to-day engineering work
* Does not want to read code
* Does not want technical details
* Wants concise summaries

---

## Data Sources

MVP v1 uses only:

* Gitea repositories (all repos the access token can reach)
* Git commits

Excluded from MVP:

* Pull Requests
* Issues
* Jira
* Deployments
* CI/CD
* Monitoring systems
* Repository scanning beyond commit and diff fetch at generation time
* AST parsing, complexity scoring, and code-quality analysis
* Source code embeddings
* Vector databases

Repository allowlists and exclude rules are deferred. See [backlog.md](../backlog.md).

---

## Inputs

Required:

* Gitea URL
* Gitea Access Token
* Report locale (e.g. `fa` for Persian, `en` for English)

Optional:

* Company Name (included in report context where helpful)

Rocket.Chat webhook URL is **not** a Cogence input in MVP v1 — delivery is handled by external orchestration. See [Report Delivery](#report-delivery).

---

## Report Schedule

| Setting | Value |
|---------|-------|
| Timezone | `Asia/Tehran` |
| Report period | Calendar day (00:00–23:59) |
| Typical delivery | **07:00 the next morning** via external cron + bash |
| Cogence responsibility | Generate and serve reports on demand via API |

Example: on **Tuesday 07:00** `Asia/Tehran`, the manager receives **Monday's** report.

Cogence does not run an internal scheduler in MVP v1. A cron job calls the generate endpoint; timing is an operations concern.

---

## Report Delivery

MVP v1 has **no dashboard** and **no built-in chat integration**.

**Cogence provides:**

* `POST /api/v1/reports/daily/{date}/generate?depth=standard` — idempotent collect → generate → return
* `GET /api/v1/reports/daily/{date}` — retrieve a stored report
* `GET /api/v1/reports/daily/latest` — retrieve the most recent report

`{date}` is `YYYY-MM-DD` for a calendar day in `Asia/Tehran`. The caller (e.g. a bash script) computes the date explicitly — Cogence does not infer "yesterday."

**External orchestration (pilot):**

1. Cron runs at 07:00 `Asia/Tehran`
2. Bash script calls `POST .../daily/{date}/generate`
3. Bash script formats the JSON and posts to Rocket.Chat via webhook

Email, Slack, built-in Rocket.Chat, and web UI are out of scope for the pilot. See [backlog.md](../backlog.md).

---

## Core Workflow

1. Connect to Gitea
2. Discover all accessible repositories
3. On `generate` for `{date}`: fetch commits for that calendar day (`Asia/Tehran`)
4. Store commit metadata (idempotent by SHA)
5. Fetch truncated unified diffs from Gitea at generation time (discarded after generation)
6. Aggregate commits by repository and contributor (raw Git author identity)
7. Generate AI summary in configured Report Locale
8. Store report
9. Return report via API (external bash delivers to Rocket.Chat)

---

## Commit Culture

Commit **counts** are not a success metric. Cogence does not rank contributors or repositories by volume.

The platform encourages **atomic commits** with clear, descriptive messages. When engineers write focused commits with meaningful titles and descriptions, reports become more accurate and useful for leadership.

Good commit hygiene is a cultural outcome of using Cogence — not surveillance. Reports may include neutral **Observability Gap** notes when a message was too vague; they do not label developers as "bad committers."

Multiple Git identities for the same person appear as separate contributors in MVP v1 — fixing Git config is a team responsibility.

---

## Commit Data Collected

For each commit (stored):

* Repository
* Commit SHA
* Author (name and email as recorded in Git)
* Timestamp
* Commit Title
* Commit Description
* Files Changed
* Insertions
* Deletions

At generation time only (not stored):

* Truncated unified diff per commit, fed to the LLM and discarded after generation

See [ADR-012](../../adr/ADR-012-truncated-diff-for-llm-translation.md).

---

## Report Generation

### Report Depth

| Depth | Status | LLM input | Manager output |
|-------|--------|-----------|----------------|
| `brief` | Backlog | Messages + file paths | Short summary only |
| `standard` | **MVP v1** | Messages + truncated diff | Full four-section report |
| `deep` | Backlog | Full diffs, richer narrative | Extended report |

MVP v1 implements `standard` only. Additional report types may be added later.

### LLM and manager demo

Template reports (no LLM) are useful for internal validation of aggregation and API shape. **Managers should not see reports until LLM summaries work** — business-language translation is the product value.

When commit messages are useless (`fix`, `wip`), the LLM infers business meaning from truncated diffs. When even that is thin, the report states so honestly via an Observability Gap note.

### Report Locale

Report text is generated in a configured locale. Persian (`fa`) is required for the MVP v1 demo; English (`en`) is also supported. Locale is explicit configuration — not auto-detected from commit messages.

---

## Report Sections

### Executive Summary

High-level explanation of what engineering accomplished during the report period.

Example themes:

* Authentication improvements
* Customer workflow enhancements
* Bug fixes

**Empty day:** *"No engineering activity was recorded on {day}."*

---

### Active Repositories

List repositories that received engineering activity on the report date (inactive repos are omitted).

Example:

* Chatbot
* Internal Portal

Use repository names, not informal "project" labels, unless a future grouping layer is added.

---

### Contributor Summary

List contributors as recorded in Git metadata and a brief summary of **what areas they worked on**.

Example:

* Sean: Customer platform improvements
* Donald: AI workflow updates

Observability Gap example (neutral, not punitive):

* Ali: Payment flow work in customer-portal *(commit message did not describe the change; summary based on code changes)*

No rankings. No productivity scores. No commit-count comparisons. No contributor identity merging in MVP v1.

---

### Management Notes

Important observations.

Examples:

* Activity focused on customer-facing improvements.
* Development concentrated on two strategic repositories.

**Empty day:** *"This may reflect a holiday or non-coding day."*

---

## Empty Days

When no commits exist for the report date, Cogence still generates and stores a report idempotently:

* Executive summary states no activity was recorded
* Active repositories and contributors are empty or omitted
* Management notes may note a holiday or non-coding day
* External delivery still runs — silence is not misread as a broken system

---

## Explicit Non-Goals

MVP v1 does NOT attempt to answer:

* Who is the best developer?
* Who worked hardest?
* Code quality scoring
* Technical debt measurement
* Team performance evaluation
* Architecture analysis
* Security analysis
* Productivity scoring

MVP v1 also does NOT include:

* Dashboards or web UI
* Built-in Rocket.Chat, Telegram, SMS, or email delivery
* Internal job scheduler (external cron is sufficient)
* Commit-count leaderboards
* Sorting repositories or contributors by activity volume
* Contributor identity merging
* Repository allowlists or exclude rules

---

## Success Criteria

A manager should be able to answer:

* What did engineering do?
* Which repositories were active?
* Who contributed?
* What should I know?

after reading the report for less than 60 seconds.

---

## Implementation

Build order is defined in [product-slices.md](product-slices.md).

Pilot user stories are in [user-stories.md](../user-stories.md). Deferred work is in [backlog.md](../backlog.md).

Domain terms: [CONTEXT.md](../../../CONTEXT.md) (repo root) and [glossary.md](../glossary.md).

---

## Future Versions

Potential future capabilities:

* Report depth tiers (`brief`, `deep`) and additional report types
* Built-in delivery channels (Rocket.Chat, Telegram, SMS, email)
* Web dashboard and Cogence UI
* Weekly and monthly reports
* Jira and issue-tracker observability signals
* Contributor identity mapping
* Repository allowlists and grouping
* Deployment integration
* Executive recommendations

These are intentionally excluded from MVP v1.

---

**Last Updated:** 2026-06-19
