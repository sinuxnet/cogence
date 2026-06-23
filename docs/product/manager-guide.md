# Manager Guide: Reading Cogence Reports

This guide is for non-technical managers — CEOs, founders, product managers — who receive Cogence daily reports.

---

## What is Cogence?

Cogence reads your team's Git activity and produces a plain-language summary every morning.

You get one concise report that answers:

- What did engineering accomplish yesterday?
- Which projects were active?
- Who contributed, and to what?
- Is there anything you should know?

You do not need to read code, review pull requests, or attend a daily standup to get this information.

---

## When Does the Report Arrive?

The report is delivered at **07:00** every morning (Tehran time) for the **previous day's** activity.

Example: On Tuesday morning at 07:00, you receive Monday's report.

If engineering did nothing on a given day (holiday, planning sprint, etc.), you still receive a report that states "No engineering activity was recorded." This means the system is working — silence is not a broken pipeline.

---

## What the Report Contains

### Executive Summary

A 2–4 sentence overview of the day's engineering work in plain business language.

> "Engineering focused on customer-facing improvements. The team worked across two repositories, with primary attention on the customer portal. Authentication enhancements and user experience improvements were the main areas of work."

Read this first. It is the only section you need to read if you are short on time.

---

### Active Repositories

The projects (Git repositories) that received work on that day. Repositories with no activity are not shown.

> - customer-portal: Authentication improvements and user experience enhancements.
> - api-gateway: Performance optimization and error handling improvements.

This tells you *which parts of your product* were worked on.

---

### Contributors

Each team member who committed code that day, and a brief description of what area they worked on.

> - Ali Rezaei: Worked on authentication and user management features.
> - Sara Mohammadi: Contributed to API performance improvements.

**What you will not see:**
- Rankings ("Ali committed more than Sara")
- Scores or productivity metrics
- Commit counts per person

Cogence does not evaluate developer performance. It describes what areas people worked on.

---

### Management Notes

Observations and patterns that may be useful for leadership.

> "High activity on customer-facing repositories indicates strong focus on strategic initiatives. Development is concentrated on two repositories, which may indicate a planned sprint focus."

This section also includes a note when some commits were large and complex:

> "Some commits touched many files, which may reduce summary precision. Atomic commits help Cogence provide clearer insights."

This is a neutral observation — it explains why a particular summary may be less specific than usual. It is not a performance warning about any individual.

---

## How to Interpret the Report

**"No engineering activity was recorded on {date}."**
Normal. This happens on weekends, holidays, or days when the team is in planning, design, or review mode rather than writing code.

**A summary that says "resolving issues" or "improving stability"**
The commit messages on that day were vague (e.g., "fix" or "updates"). Cogence still provides the best summary it can from the code changes, but the precision will be lower. Encouraging the team to write descriptive commit messages improves report quality over time.

**A repository is missing from the report**
That repository had no commits that day. Cogence only reports on active repositories — if a project is not listed, nothing was committed to it.

**The same report two days in a row**
This means the API was called with the same date twice (reports are stored and re-used). It is not a bug.

---

## Healthy Signals vs. Things to Discuss

Cogence does not flag "bad" engineering behaviour. However, some patterns are worth a conversation with your team:

| Pattern | What to discuss |
|---------|----------------|
| No activity for multiple consecutive working days | Is the team blocked? Are there dependencies waiting? |
| All activity in a single repository for extended periods | Is the rest of the product being maintained? |
| Repeated "observability gap" notes | The team may benefit from a short reminder about commit message hygiene |
| Report says "LLM unavailable" in metadata | The AI service had a temporary issue; the report used a template fallback with basic facts |

---

## What Cogence Does Not Do

- **It does not rank developers.** No leaderboards, no "top contributor" labels.
- **It does not measure productivity.** Commit volume is not a success metric.
- **It does not read code quality.** Cogence reads commit messages and code changes — not test coverage, bugs, or architecture.
- **It does not predict the future.** Reports describe what happened, not what will happen.
- **It does not replace conversations.** Use reports as a starting point for questions, not as a complete picture.

---

## Setting Up Delivery

Reports are delivered to Rocket.Chat via a scheduled script. To set this up, ask your engineering team to:

1. Deploy Cogence (see `docs/development/docker.md`)
2. Create a Rocket.Chat incoming webhook in your workspace
3. Configure `scripts/deliver.sh` with the webhook URL and schedule it at `07:00 Asia/Tehran`

Once set up, you receive reports automatically with no manual steps.

---

## Report Language

Reports can be generated in **English** (`en`) or **Persian / Farsi** (`fa`).

The language is a server configuration setting (`REPORT_LOCALE`). Ask your engineering team to change it if needed.

---

**Last Updated:** 2026-06-24
