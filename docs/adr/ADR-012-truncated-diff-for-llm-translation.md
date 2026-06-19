# ADR-012: Truncated Diff for LLM Translation

MVP v1 feeds the LLM truncated unified diffs (not just commit messages) so reports stay business-readable when messages are vague. This is translation of *what changed*, not code-quality analysis. Diffs are fetched from Gitea at generate time and discarded after generation — not stored in PostgreSQL. This narrows [ADR-003](ADR-003-no-code-analysis-in-mvp.md): AST parsing, complexity scoring, security scanning, and developer quality judgment remain out of scope.

**Considered Options**

- Metadata only (commit message + file paths) — rejected for pilot because `fix` / `wip` messages produce useless manager summaries.
- Full diff per commit — rejected for pilot due to token cost, latency, and secret-leakage risk.
- Truncated diff per commit — accepted as the MVP balance.

**Consequences**

- Report generation requires live Gitea access (or cached commit metadata plus on-demand diff fetch).
- Idempotent re-generate re-fetches diffs.
- A future `brief` / `deep` Report Depth tier may change how much diff text is included; MVP implements `standard` only.
