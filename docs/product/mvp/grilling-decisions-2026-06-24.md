# Grilling Session — 2026-06-24

Design decisions for v0.3.0. Each decision was stress-tested one at a time.

## Decisions

### Format: per-goal contributor attribution

Remove the `contributors[]` section from the JSON response entirely. Within each Repository, the LLM groups commits by goal/theme and outputs a `contributions[]` list — one entry per goal per Contributor. Attribution is embedded on each bullet: `**Abbas**: fixed X in Y`. The separate Contributors section was vague and redundant (ADR-013).

### LLM output: OpenAI JSON mode

Use `response_format={"type": "json_object"}` for per-repository calls. The LLM returns a structured `{"contributions": [...]}` object directly. Free-text parsing was rejected as fragile on edge cases (non-ASCII names, multi-line descriptions). One call per repository replaces the two previous calls (per-repo + per-contributor) (ADR-015).

### Specificity rule in prompts

Added to system prompt: always name the specific component, screen, or module affected. State what changed and where. Do not explain the goal or purpose — managers can ask. Bad: "improved user experience". Good: "fixed token expiry check in login form".

### Persian locale: LLM judges term boundaries

When `REPORT_LOCALE=fa`, technical terms (API, endpoint, OAuth, library names) stay in English. Product-domain terms use Persian when a natural equivalent exists. No hard-coded glossary — left to LLM judgment. Can revisit if output quality requires it.

### RTL-first layout for Rocket.Chat (ADR-014)

Rocket.Chat sets text direction from the script of the first line. When locale is `fa`, the first line is always a Persian date string (e.g. `گزارش روز 4 تیر 1404`) to force RTL for the entire message. Western (ASCII) numerals used in the date to avoid font rendering issues.

### Jalali calendar via jdatetime (ADR-014)

When `REPORT_LOCALE=fa`, dates shown in the message use the Jalali calendar computed by the `jdatetime` Python library. A separate `CALENDAR_SYSTEM` env var was rejected — no realistic use case for mismatched locale+calendar.

### Rocket.Chat message hierarchy

`# Title` (h1) → `## OrgName` (h2) → `### repo-name` (h3) → contribution bullets → Report Footer. Org heading is always shown even with one organization — simpler code, useful context.

### Report Footer always in English

The closing stats line (`3 active repos · 5 contributions detected · 12 commits`) is hardcoded in English regardless of `REPORT_LOCALE`. Numbers and short labels render correctly in both directions; keeping it English is consistent and avoids locale branching in the footer.

### Cross-repo relevancy: deferred

Detecting thematic connections between work in different repositories of the same organization is deferred to backlog (MVP-v3+). Scope was clear but the feature would delay the v0.3.0 release for uncertain value.

### Release: v0.3.0

JSON schema change + new dependency (`jdatetime`) + visible format change to delivered messages qualifies as a minor bump. Patch is reserved for backwards-compatible fixes.

## New ADRs

- ADR-013: Per-Goal Contributor Attribution Replaces Per-Section Summaries
- ADR-014: RTL-First Persian Locale With Jalali Calendar
- ADR-015: LLM Returns Structured JSON for Contribution Grouping

## Updated ADRs

- ADR-005: amendment noting structured JSON output replaces free-text summaries
- ADR-007: amendment noting Contributors section removal and rationale
