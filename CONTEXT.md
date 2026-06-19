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
The default Report Depth for MVP v1: full four-section Daily Report using commit metadata plus truncated unified diffs. Diffs are fetched at generate time and discarded after generation.
_Avoid_: Full report, normal report

**Contributor**:
A person who authors commits, shown as recorded in Git metadata. MVP v1 does not merge multiple Git identities.
_Avoid_: Developer ranking, engineer score

**Delivery**:
How a manager receives a report. MVP v1 delivery is external (cron + bash posting to Rocket.Chat); Cogence exposes the report via API only.
_Avoid_: Built-in notification, push

**Report Locale**:
The language used for generated report text (e.g. `fa` for Persian, `en` for English). Configured per deployment.
_Avoid_: Auto-detect, mixed language
