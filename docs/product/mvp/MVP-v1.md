# Cogence MVP v1

## Objective

Validate that Cogence can automatically generate a useful, business-readable summary of engineering work performed during the last 24 hours.

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

> What did we do during the last 24 hours?

Every feature included in MVP v1 must contribute directly to answering this question.

---

## Target User

Primary User:

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

* Gitea repositories
* Git commits

Excluded from MVP:

* Pull Requests
* Issues
* Jira
* Deployments
* CI/CD
* Monitoring systems
* Repository scanning
* Code analysis
* Source code embeddings
* Vector databases

---

## Inputs

Required:

* Gitea URL
* Gitea Access Token

Optional:

* Company Name
* Rocket.Chat webhook URL (for scheduled delivery)

---

## Report Schedule

| Setting | Value |
|---------|-------|
| Timezone | `Asia/Tehran` |
| Generation & delivery | Daily at **21:00** (9:00 PM) |
| Report period | Calendar day in `Asia/Tehran` (00:00–23:59) |

Each night at 21:00 Asia/Tehran, Cogence collects commits for that calendar day, generates the report, and delivers it.

Commits made after 21:00 belong to the next calendar day's report.

---

## Report Delivery

MVP v1 has **no dashboard**. Reports reach managers through:

1. **REST API** — `GET /api/v1/reports/daily/{date}` and `GET /api/v1/reports/daily/latest`
2. **Rocket.Chat** — scheduled message posted to a configured channel at 21:00 Asia/Tehran

Email, Slack, and web UI are out of scope for the pilot. See [backlog.md](../backlog.md).

---

## Core Workflow

1. Connect to Gitea
2. Discover repositories
3. Fetch commits for the current calendar day (Asia/Tehran)
4. Store commit metadata
5. Aggregate commits
6. Generate AI summary
7. Store report
8. Deliver report (API + Rocket.Chat)

---

## Commit Culture

Commit **counts** are not a success metric. Cogence does not rank contributors or repositories by volume.

The platform encourages **atomic commits** with clear, descriptive messages. When engineers write focused commits with meaningful titles and descriptions, reports become more accurate and useful for leadership.

Good commit hygiene is a cultural outcome of using Cogence — not surveillance.

---

## Commit Data Collected

For each commit:

* Repository
* Commit SHA
* Author
* Timestamp
* Commit Title
* Commit Description

Additional metadata (stored for future use, not shown in pilot reports):

* Files Changed
* Insertions
* Deletions

---

## Report Sections

### Executive Summary

High-level explanation of what engineering accomplished during the report period.

Example themes:

* Authentication improvements
* Customer workflow enhancements
* Bug fixes

---

### Active Repositories

List repositories that received engineering activity.

Example:

* Chatbot
* Internal Portal

Use repository names, not informal "project" labels, unless a future grouping layer is added.

---

### Contributor Summary

List contributors and a brief summary of **what areas they worked on**.

Example:

* Sean: Customer platform improvements
* Donald: AI workflow updates
* Florentino: Frontend enhancements

No rankings. No productivity scores. No commit-count comparisons.

---

### Management Notes

Important observations.

Examples:

* Activity focused on customer-facing improvements.
* Development concentrated on two strategic repositories.
* No unusual activity detected.

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
* Commit-count leaderboards
* Sorting repositories or contributors by activity volume

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

---

## Future Versions

Potential future capabilities:

* Weekly reports
* Monthly reports
* Web dashboard
* Email delivery
* Slack/Teams integration
* Commit quality scoring
* Risk detection
* Ownership analysis
* Jira integration
* Deployment integration
* Executive recommendations

These are intentionally excluded from MVP v1.
