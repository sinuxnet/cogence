# MVP-V1.md

# Cogence MVP v1

## Objective

Validate that Cogence can automatically generate a useful, business-readable summary of engineering work performed during the last 24 hours.

Success is not measured by technical sophistication.

Success is measured by whether a non-technical manager can read the report in less than one minute and accurately understand what engineering worked on.

---

# Problem Statement

Managers often rely on meetings, manual updates, and individual conversations to understand engineering activity.

This process does not scale and creates information gaps between engineering teams and leadership.

Cogence aims to provide automatic visibility into engineering activity using development signals that already exist.

---

# MVP Question

The entire MVP is focused on answering one question:

> What did we do during the last 24 hours?

Every feature included in MVP v1 must contribute directly to answering this question.

---

# Target User

Primary User:

* CEO
* Founder
* Engineering Manager
* Product Manager

Characteristics:

* Limited visibility into day-to-day engineering work
* Does not want to read code
* Does not want technical details
* Wants concise summaries

---

# Data Sources

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

# Inputs

Required:

* Gitea URL
* Gitea Access Token

Optional:

* Company Name

---

# Core Workflow

1. Connect to Gitea
2. Discover repositories
3. Fetch commits from the last 24 hours
4. Store commit metadata
5. Aggregate commits
6. Generate AI summary
7. Store report
8. Deliver report

---

# Commit Data Collected

For each commit:

* Repository
* Commit SHA
* Author
* Timestamp
* Commit Title
* Commit Description

Additional metadata:

* Files Changed
* Insertions
* Deletions

Additional metadata is collected for future analytics but not used directly in MVP reporting.

---

# Report Sections

## Executive Summary

High-level explanation of what engineering accomplished during the last 24 hours.

Example:

* Authentication improvements
* Customer workflow enhancements
* Bug fixes

---

## Projects Worked On

List repositories receiving engineering activity.

Example:

* Chatbot
* Internal Portal

---

## Contributor Summary

List contributors and a brief summary of their activities.

Example:

* Sean: Customer platform improvements
* Donald: AI workflow updates
* Florentino: Frontend enhancements

No rankings.

No productivity scores.

---

## Management Notes

Important observations.

Examples:

* Activity focused on customer-facing improvements.
* Development concentrated on two strategic projects.
* No unusual activity detected.

---

# Explicit Non-Goals

MVP v1 does NOT attempt to answer:

* Who is the best developer?
* Who worked hardest?
* Code quality scoring
* Technical debt measurement
* Team performance evaluation
* Architecture analysis
* Security analysis
* Productivity scoring

---

# Success Criteria

A manager should be able to answer:

* What did engineering do?
* Which projects were active?
* Who contributed?
* What should I know?

after reading the report for less than 60 seconds.

---

# Future Versions

Potential future capabilities:

* Weekly reports
* Monthly reports
* Commit quality scoring
* Risk detection
* Ownership analysis
* Jira integration
* Deployment integration
* Executive recommendations
* Engineering intelligence dashboards

These are intentionally excluded from MVP v1.
