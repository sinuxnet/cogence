# ADR-015: LLM Returns Structured JSON for Contribution Grouping

## Status

Accepted

## Date

2026-06-24

Per-goal contributor attribution (ADR-013) requires the LLM to output a *list* of `{contributor, description}` pairs per Repository, not a single string. If the LLM returns free text, we must parse it — and parsing LLM prose is fragile: line breaks vary, contributor names may be reformatted, and edge cases (one contributor, zero commits, non-ASCII names) produce inconsistent output.

## Decision

Use OpenAI's `response_format={"type": "json_object"}` (JSON mode) for all per-repository contribution calls. The LLM is instructed to return:

```json
{
  "contributions": [
    {"contributor": "Abbas", "description": "fixed token expiry check in login form"},
    {"contributor": "Abbas", "description": "added invoice list endpoint to billing module"},
    {"contributor": "Soheil", "description": "increased dashboard refresh interval from 30 to 45 minutes"}
  ]
}
```

The outer `"contributions"` key is required because JSON mode requires a top-level object, not an array.

## Considered Options

- **Free text with line parsing** (`contributor: description` lines): Simple prompt, but fragile on names with colons, multi-line descriptions, and non-Latin scripts. Rejected.
- **Function calling / tool use**: More explicit schema enforcement, but adds setup complexity for a straightforward structured output. JSON mode is sufficient. Rejected.
- **Embedding-based clustering followed by LLM labelling**: Two-step process that adds latency and a new dependency for no improvement in output quality at this scale. Rejected.

## Consequences

- The per-repository LLM call changes from `max_tokens=150` (one sentence) to `max_tokens=400` (N contribution objects). Budget must be monitored as repo activity grows.
- The `LLMResult` dataclass loses `repository_summaries: dict[str, str]` and gains `repository_contributions: dict[str, list[dict]]`.
- If JSON mode returns malformed JSON (rare but possible), the caller falls back to the template report per the existing graceful-degradation path (ADR-005).
- Contributor summary calls are removed entirely — per-contributor summaries are replaced by per-Contribution bullets within each Repository.
