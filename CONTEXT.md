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
The default Report Depth for MVP v2: General Report, Organizations (with per-repository summaries), and Contributors. Uses commit metadata plus truncated unified diffs; diffs are fetched at generate time and discarded after generation.
_Avoid_: Full report, normal report, management notes

**Contributor**:
A person who authors commits, shown as recorded in Git metadata. Daily Reports name contributors and describe what they worked on so managers can route follow-up work and customer questions — not to rank or score people.
_Avoid_: Developer ranking, engineer score, productivity comparison

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

**General Report**:
The opening section of a Daily Report: which Organizations had activity, how many Contributors were detected, and total update count. Replaces the MVP v1 executive summary as the report opener.
_Avoid_: Executive summary (retired field name), management notes

**Neutral Tone**:
Report language that states what happened without endorsing, blaming, or predicting outcomes. Enforced by tuned prompts plus post-generation checks for forbidden phrases; failed sections fall back to a factual template.
_Avoid_: Optimistic review, management advice, performance praise

**Repository**:
A Git repository tracked by Cogence. Belongs to exactly one Organization in Gitea. Organization is derived from `full_name` (e.g. `acme/api` → Organization `acme`), not stored separately in MVP v2.
_Avoid_: Project, codebase, repo
