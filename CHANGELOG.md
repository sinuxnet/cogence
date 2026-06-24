# Changelog

All notable changes are documented here.

## [0.3.0] — 2026-06-24

### Added
- Per-goal contributor attribution: LLM groups commits by theme and returns structured `contributions[]` per repository (ADR-013, ADR-015)
- Jalali calendar support for `REPORT_LOCALE=fa` via `jdatetime` (ADR-014)
- RTL-first message layout for Rocket.Chat when locale is `fa` — first line is a Persian date string (ADR-014)
- Rocket.Chat message structure: h1 title / h2 org / h3 repo / bullet contributions / English footer
- Report Footer: single English closing line with active repos, contributions detected, and commit count

### Changed
- LLM switched to OpenAI JSON mode (`response_format=json_object`) for structured contribution output
- Report JSON shape: `contributors[]` removed; `repositories[].summary` replaced by `repositories[].contributions[]`; `general` section removed
- Per-contributor LLM call removed; one structured JSON call per repository replaces both previous calls
- Specificity rule added to LLM prompts: descriptions must name the component or module, state what changed and where
- Persian locale instruction updated: technical terms stay English, product terms use Persian at LLM's judgment

### Deferred
- Cross-repository relevancy detection (backlog, MVP-v3+)

## [0.2.0] — 2026-06-24

### Added
- implement all 6 MVP-v2 slices

### Fixed
- rename reserved 'message' key in log extra dict

### Chores
- chore(release): add release script

