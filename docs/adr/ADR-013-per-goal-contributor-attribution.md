# ADR-013: Per-Goal Contributor Attribution Replaces Per-Section Summaries

## Status

Accepted

## Date

2026-06-24

The v0.2.0 report had two separate sections: a `projects` block (one AI-generated sentence per Repository) and a `contributors` block (one AI-generated sentence per Contributor across all repos). Both produced vague, generic descriptions — "improved user experience", "worked on backend infrastructure" — because the LLM was asked to compress many commits into a single sentence.

Managers said these sentences were not actionable. They needed to know *what* changed and *where*, not a high-level paraphrase.

## Decision

Remove the `contributors` section from the report entirely. Within each Repository, the LLM groups commits by goal/theme and outputs one Contribution bullet per goal per Contributor. Attribution is embedded directly on each bullet (`**Abbas**: fixed token expiry check in login form`). The Contributor's name appears only where they have a Contribution — there is no separate contributor summary.

The LLM is instructed to name the specific component or screen affected, and to state what changed and where. The "why" (goal justification) is omitted — managers can ask; the report states facts.

## Considered Options

- **Per-commit bullets**: Too granular. A contributor with 8 commits produces 8 bullets, most of which describe the same logical change. Noisy and hard to scan.
- **Keep Contributors section alongside repo bullets**: Redundant. If attribution is already on each bullet, a separate contributors section repeats the same information at a higher abstraction — the worst of both worlds.
- **One sentence per repo (v0.2.0 approach)**: Too vague. Compressing all commits and all contributors into one sentence reliably loses the specifics managers need.

## Consequences

- The JSON schema changes: `contributors[]` is removed; `repositories[].contributions[]` replaces `repositories[].summary`.
- The LLM now returns structured JSON (see ADR-015) rather than a free-text string per repo.
- The delivery script drops the `Contributors:` heading block.
- Cross-repository contributor totals are still reported in the Report Footer (`x contributions detected`) for at-a-glance counts.
