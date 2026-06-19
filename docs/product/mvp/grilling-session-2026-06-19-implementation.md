# Grilling Session — Implementation Decisions
## 2026-06-19 (Second Session)

This document captures implementation decisions made during a detailed grilling session on MVP v1 before development begins.

---

## Session Summary

Resolved open implementation questions from [grilling-decisions-2026-06-19.md](grilling-decisions-2026-06-19.md) through systematic interview. Focus: keep MVP simple while designing for future extensibility.

---

## Decisions Made

| # | Topic | Decision | Rationale |
|---|-------|----------|-----------|
| 1 | API endpoint naming | Use `/generate` only (not `/regenerate`) | Simpler API surface; true idempotency handles both cases |
| 2 | Idempotent behavior | Return existing report without regeneration | True idempotency; faster; consistent with "calendar day is closed" |
| 3 | Bearer token auth | Single shared token via `COGENCE_API_TOKEN` env var | Simplest for single-tenant pilot; no token management needed |
| 4 | Persian prompt language | Prompts in English, instruct LLM to respond in Persian | Easier to maintain; better LLM performance; output quality matters |
| 5 | Rocket.Chat formatting | Use message attachments with structured fields | Professional appearance; uses platform features |
| 6 | Commit counts in API | Include in metadata for debugging/validation | Encourages atomic commits; available but not emphasized |
| 7 | Commit counts in Rocket.Chat | Hide from manager view | Avoid surveillance perception; focus on accomplishments |
| 8 | Atomic commit detection | Simple file count rule: `>ATOMIC_COMMIT_THRESHOLD` files | MVP uses threshold only; defer LLM semantic analysis to backlog |
| 9 | Atomic commit threshold | Configurable via env: `ATOMIC_COMMIT_THRESHOLD=10` | Default 10 files; configurable now, per-org in future |
| 10 | Non-atomic commit reporting | Include in metadata + Management Notes when detected | Educational team-level message; explains precision impact |
| 11 | Report locale config | Query parameter `?locale=fa` with ENV default | Avoids breaking changes for future multi-tenancy |
| 12 | Gitea fetch strategy | Sequential with 100ms delay between repos | Safest for shared/constrained Gitea instances |
| 13 | Diff fetching strategy | Deferred to implementation | Start simple; optimize post-pilot based on real costs |
| 14 | Diff truncation limits | Deferred to backlog | Not critical for MVP; tune after pilot feedback |

---

## Key Principles Reinforced

1. **Simplicity First**: Choose simplest implementation for MVP; defer optimization
2. **Future-Ready Design**: Make choices that won't require breaking changes (e.g., query params)
3. **No Surveillance**: Hide commit counts from managers; focus on accomplishments
4. **Educational, Not Punitive**: Non-atomic commit notes are team-level and helpful
5. **Configurable Thresholds**: Use environment variables for tunable parameters

---

## Configuration Summary

### Environment Variables (MVP v1)

```bash
# Authentication
COGENCE_API_TOKEN=<shared_secret>

# Gitea Integration
GITEA_URL=https://git.example.com
GITEA_TOKEN=<access_token>

# Report Configuration
COGENCE_REPORT_LOCALE=fa  # Default locale (fa or en)
ATOMIC_COMMIT_THRESHOLD=10  # Files changed threshold

# Gitea API
GITEA_REQUEST_DELAY_MS=100  # Delay between repo fetches
```

---

## API Endpoint Specification

### Generate Daily Report

**Endpoint**: `POST /api/v1/reports/daily/{date}/generate`

**Query Parameters**:
- `depth` (optional, default: `standard`): Report depth tier
- `locale` (optional, default from `COGENCE_REPORT_LOCALE`): Report language (`fa`, `en`)

**Behavior**:
- Idempotent: Returns existing report if already generated for `{date}`
- Does NOT regenerate if report exists (true idempotency)
- Collects commits → generates summary → stores → returns in one call
- `{date}` is explicit `YYYY-MM-DD` in `Asia/Tehran` timezone

**Response**: `200 OK` with full report JSON

---

## Report JSON Structure Updates

### Metadata Section

```json
{
  "metadata": {
    "generated_at": "2024-01-15T21:00:00+03:30",
    "delivery": ["api", "rocketchat"],
    "total_commits": 15,
    "total_repositories": 3,
    "total_contributors": 4,
    "non_atomic_commits": 2,
    "atomic_commit_threshold": 10,
    "generation_duration_ms": 2340,
    "llm_model": "gpt-4",
    "llm_tokens_used": 1250
  }
}
```

**New fields**:
- `non_atomic_commits`: Count of commits exceeding threshold
- `atomic_commit_threshold`: Threshold used for detection

### Management Notes (when non-atomic commits detected)

Example text:
> "Some commits touched many files, which may reduce summary precision. Atomic commits help Cogence provide clearer insights."

---

## Rocket.Chat Message Format

### Structure (Message Attachment)

```json
{
  "attachments": [
    {
      "title": "Daily Engineering Report — 2024-01-15",
      "text": "<Executive Summary>",
      "fields": [
        {
          "title": "Active Repositories",
          "value": "• customer-portal\n• api-gateway\n• admin-dashboard"
        },
        {
          "title": "Contributors",
          "value": "• John Doe: Authentication system work\n• Jane Smith: API performance improvements"
        },
        {
          "title": "Management Notes",
          "value": "<Management Notes text>"
        }
      ],
      "color": "#0066cc"
    }
  ]
}
```

**Excluded from Rocket.Chat**:
- Commit counts (per repo, per contributor, or total)
- Technical metadata
- Non-atomic commit counts

**Included**:
- Executive summary (main text)
- Repository names and summaries
- Contributor names and work summaries
- Management notes (including atomic commit guidance when applicable)

---

## Atomic Commit Detection Logic

### Detection Rules (MVP v1)

```python
def is_non_atomic(commit, threshold: int) -> bool:
    """Simple file count rule for MVP."""
    return commit.files_changed > threshold
```

### Future Enhancement (Backlog)

Semantic detection via LLM:
- `< 5 files`: No LLM check needed
- `5-10 files`: Simple LLM call (file paths + commit message)
- `10-20 files`: Moderate LLM call (file paths + headers + truncated diffs)
- `> 20 files`: Definitely non-atomic (no LLM needed)

---

## LLM Prompt Strategy

### Locale Handling

**System Prompt** (English):
```
You are a business intelligence assistant helping non-technical managers understand engineering work.
Generate a report in {locale} language that is clear, concise, and business-focused.
```

**User Prompt** (English with locale instruction):
```
Generate a daily engineering report in Persian (fa) based on the following commits...
```

### Report Generation

Single LLM call per report section:
1. Executive Summary
2. Repository Summaries (batch)
3. Contributor Summaries (batch)
4. Management Notes

**Input per section**:
- Commit metadata (title, description, author, timestamp)
- Truncated unified diffs (when available)
- File paths and change statistics

---

## Deferred to Backlog

| Item | Reason | Future Consideration |
|------|--------|---------------------|
| Diff truncation token limits | Not critical for MVP; tune post-pilot | Start with reasonable defaults (500 tokens/commit) |
| LLM-based atomic detection | Too complex for MVP | Add semantic "multiple purposes" analysis |
| Commit quality indicator API | Nice-to-have metric | `atomic_commit_ratio` in metadata |
| Per-organization locale | Multi-tenancy feature | Database config per org |
| Parallel Gitea fetching | Optimization | Add concurrency limit if needed |
| Smart diff fetching | Cost optimization | Fetch only for vague commits |

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Database schema with `atomic_commit_threshold` config
- [ ] Environment variable loading and validation
- [ ] Bearer token authentication middleware
- [ ] Gitea client with sequential fetching + delay

### Phase 2: Report Generation
- [ ] Idempotent `/generate` endpoint
- [ ] Locale parameter with ENV default
- [ ] Atomic commit detection (file count rule)
- [ ] LLM integration with English prompts
- [ ] Persian output generation
- [ ] Metadata with non-atomic commit counts

### Phase 3: Delivery
- [ ] Rocket.Chat message attachment formatter
- [ ] Bash script with structured fields
- [ ] Management Notes with atomic commit guidance
- [ ] Cron setup at 07:00 Asia/Tehran

### Phase 4: Documentation
- [ ] Update API docs with `/generate` endpoint
- [ ] Remove `/regenerate` references
- [ ] Document environment variables
- [ ] Update sample report JSON with new metadata

---

## Related Documentation

- [Grilling Decisions (Session 1)](grilling-decisions-2026-06-19.md)
- [MVP v1 Specification](MVP-v1.md)
- [Product Slices](product-slices.md)
- [API Documentation](../../api/README.md)

---

**Session Date**: 2026-06-19  
**Participants**: Product Owner, AI Assistant  
**Status**: Complete — Ready for Implementation