# Grilling Session Decisions — 2026-06-19

Decisions from a `/grill-with-docs` session on [MVP-v1.md](MVP-v1.md) before implementation began.

---

## Summary

MVP v1 targets small businesses (one non-technical manager, 1–10 developers). Cogence is a **report engine + API**; delivery is **external** (cron + bash → Rocket.Chat). Reports cover a **Tehran calendar day**, are generated with **LLM + truncated diffs**, and are written in a **configurable locale** (Persian required for demo).

---

## Decisions

| # | Topic | Decision |
|---|-------|----------|
| 1 | Report period | Calendar day `Asia/Tehran` (00:00–23:59), not rolling 24h |
| 2 | MVP question | "What did engineering accomplish on this calendar day?" |
| 3 | Delivery time | 07:00 next morning (external cron), not 21:00 same night |
| 4 | Rocket.Chat | Bash script owns delivery in pilot; built-in channels in backlog |
| 5 | API date | Explicit `{date}` (`YYYY-MM-DD`); idempotent `POST .../generate` |
| 6 | Generate pipeline | Collect → generate → store → return in one call |
| 7 | Repository scope | All repos the Gitea token can access (~20; typically <6 active/day) |
| 8 | Allowlist / exclude | Deferred |
| 9 | Empty days | Always generate; explicit copy in executive summary + management notes |
| 10 | LLM | Required before manager demo; template reports for internal dev only |
| 11 | Diff input | Truncated unified diff at generate time; discarded after ([ADR-012](../../adr/ADR-012-truncated-diff-for-llm-translation.md)) |
| 12 | Code quality | Out of scope — diffs for business translation only |
| 13 | Observability gaps | Neutral inline notes when messages are vague; not "bad committer" labels |
| 14 | Commit coaching | Separate future channel; not in CEO daily report |
| 15 | Report depth | `brief` / `standard` / `deep` in backlog; MVP builds `standard` only |
| 16 | Contributor identity | Raw Git authors in MVP; merging deferred (cultural nudge) |
| 17 | Report locale | Configurable; Persian (`fa`) for MVP demo |

---

## Empty-Day Copy

- **Executive summary:** "No engineering activity was recorded on {day}."
- **Management notes:** "This may reflect a holiday or non-coding day."

---

## Files Updated

- [MVP-v1.md](MVP-v1.md)
- [product-slices.md](product-slices.md)
- [backlog.md](../backlog.md)
- [glossary.md](../glossary.md)
- [sample-report.json](../../examples/sample-report.json)
- [CONTEXT.md](../../../CONTEXT.md)
- [ADR-012](../../adr/ADR-012-truncated-diff-for-llm-translation.md)
- [ADR-003](../../adr/ADR-003-no-code-analysis-in-mvp.md) (cross-reference to ADR-012)

---

## Open for Implementation (Not Grilled)

- Bearer token auth details
- Truncated diff size limits (tokens per commit / per report)
- Rocket.Chat message formatting in bash script
- Persian prompt templates

---

**Session date:** 2026-06-19
