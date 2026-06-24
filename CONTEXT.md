# Cogence

Engineering intelligence for small businesses: turn Git activity into business-readable daily reports for non-technical managers.

## Language

**Calendar Day (report period)**:
One full day in `Asia/Tehran` from 00:00 to 23:59. The unit a Daily Report covers.
_Avoid_: Last 24 hours, rolling window

**Daily Report**:
A generated summary of engineering activity for one Calendar Day, written in business language for managers.
_Avoid_: Dashboard, analytics export

**Report Date**:
The calendar date (`YYYY-MM-DD`) a Daily Report describes, interpreted in `Asia/Tehran`.
_Avoid_: Generation timestamp, delivery date

**Generate**:
An idempotent operation that collects commits for a Report Date, produces a Daily Report, stores it, and returns it.
_Avoid_: Build, compile, refresh

**Observability Gap**:
A neutral note when a contributor's commit message did not carry enough information; the summary relied on other signals (e.g. truncated diff).
_Avoid_: Bad committer, poor performer, non-compliant developer

**Report Depth**:
How much source material the LLM reads when generating a report (`brief`, `standard`, `deep`). MVP v1 implements `standard` only.
_Avoid_: Report type, report mode

**Standard Report**:
The daily report format from v0.3.0: per-Repository Contribution bullets grouped under each Organization, followed by a Report Footer. No separate Contributors section or executive summary. Uses commit metadata plus truncated unified diffs; diffs are fetched at generate time and discarded after generation.
_Avoid_: Full report, normal report, management notes

**Contributor**:
A person who authors commits, shown as recorded in Git metadata. Cogence attributes work to Contributors at the Contribution level — not to rank or score people, but so managers can route follow-up questions. Contributors do not have their own section in the report; their name appears on each Contribution bullet within the relevant Repository.
_Avoid_: Developer ranking, engineer score, productivity comparison

**Contribution**:
A goal-grouped cluster of commits by one Contributor within one Repository, surfaced as a single bullet in the delivered message. The LLM determines goal boundaries — if a Contributor's commits addressed two distinct goals, they produce two Contributions. The unit of attribution in a Daily Report.
_Avoid_: Commit (too granular), summary (too vague), task

**Delivery**:
How a manager receives a report. MVP v1 delivery is external (cron + bash posting to Rocket.Chat); Cogence exposes the report via API only. Delivery failures are separate from report generation — a stored report can be re-delivered without re-generating.
_Avoid_: Built-in notification, push

**Report Locale**:
The language used for generated report text (e.g. `fa` for Persian, `en` for English). Configured per deployment.
_Avoid_: Auto-detect, mixed language

**Organization**:
A Gitea organization that owns one or more Repositories. The grouping level in a Daily Report between the deployment and individual Repositories.
_Avoid_: Project, team, tenant

**Update**:
Manager-facing label for a single Git commit when surfaced in report text or delivery messages. Counts and summaries use "update(s)"; the underlying record remains a Commit in code and storage.
_Avoid_: Commit (in user-facing text), change, modification

**Report Footer**:
A single closing line appended to every delivered message, always in English regardless of Report Locale, stating total active repositories, contributions detected, and commit count. Example: `3 active repos · 5 contributions detected · 12 commits`. Replaces the General Report opening section (retired in v0.3.0).
_Avoid_: Summary, statistics block, analytics row

**Neutral Tone**:
Report language that states what happened without endorsing, blaming, or predicting outcomes. Enforced by tuned prompts plus post-generation checks for forbidden phrases; failed sections fall back to a factual template.
_Avoid_: Optimistic review, management advice, performance praise

**Repository**:
A Git repository tracked by Cogence. Belongs to exactly one Organization in Gitea. Organization is derived from `full_name` (e.g. `acme/api` → Organization `acme`), not stored separately in MVP v2.
_Avoid_: Project, codebase, repo
