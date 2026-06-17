# AI Prompt Specification: Report Generation

## Overview

This document specifies the AI prompts and rules for generating business-readable daily reports from engineering commit data. The prompts are designed to transform technical Git commits into executive-friendly summaries.

**Goal:** Generate clear, actionable, business-readable reports that non-technical managers can understand in under 60 seconds.

---

## Core Principles

Based on [ADR-002](../adr/ADR-002-business-language-reporting.md), [ADR-004](../adr/ADR-004-signals-over-surveillance.md), and [ADR-005](../adr/ADR-005-ai-generates-summaries-not-facts.md):

1. **Business Language Only** - No technical jargon
2. **No Individual Scoring** - No developer rankings or productivity metrics
3. **Factual Basis** - Only use provided commit data
4. **Concise** - Readable in under 60 seconds
5. **Actionable** - Provide insights for leadership

---

## Input Data Structure

### Commits Input

```json
{
  "date": "2024-01-15",
  "commits": [
    {
      "sha": "abc123",
      "repository": "customer-portal",
      "author": "John Doe",
      "author_email": "john@example.com",
      "timestamp": "2024-01-15T14:30:00Z",
      "title": "feat(auth): add OAuth2 support",
      "description": "Implemented OAuth2 authentication flow with support for Google and GitHub providers.",
      "files_changed": 8,
      "insertions": 245,
      "deletions": 67
    }
  ]
}
```

### Repositories Input

```json
{
  "repositories": [
    {
      "name": "customer-portal",
      "full_name": "acme/customer-portal",
      "description": "Customer-facing web portal",
      "commit_count": 8
    }
  ]
}
```

### Contributors Input

```json
{
  "contributors": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "commit_count": 6,
      "repositories": ["customer-portal", "api-gateway"]
    }
  ]
}
```

---

## Output Structure

### Complete Report Output

```json
{
  "executive_summary": "Engineering focused on customer-facing improvements yesterday...",
  "projects": [
    {
      "repository": "customer-portal",
      "commit_count": 8,
      "summary": "Authentication improvements and user experience enhancements"
    }
  ],
  "contributors": [
    {
      "name": "John Doe",
      "commit_count": 6,
      "summary": "Worked on authentication system and user management features"
    }
  ],
  "management_notes": "High activity on customer-facing projects. Team is focused on strategic initiatives."
}
```

---

## Prompt Templates

### 1. Executive Summary Prompt

**Purpose:** Generate 2-4 sentence overview of engineering activity.

**System Prompt:**
```
You are an executive assistant translating engineering activity into business language.
Your audience is non-technical executives who need to understand what engineering accomplished.
Use clear, concise business language. Avoid technical jargon.
Focus on business value and strategic alignment.
```

**User Prompt Template:**
```
Generate an executive summary for the following engineering activity from {date}.

Commits: {commit_count} commits across {repository_count} projects by {contributor_count} team members.

Key repositories:
{repository_list}

Key commit messages:
{commit_titles}

Requirements:
- 2-4 sentences maximum
- Business language only (no technical terms)
- Highlight key accomplishments
- Focus on business value
- Be specific but concise

Executive Summary:
```

**Example Output:**
```
Engineering focused on customer-facing improvements yesterday. The team made 15 commits across 3 projects, with primary attention on the customer portal. Key accomplishments include authentication enhancements and user experience improvements. This work directly supports our Q1 customer acquisition goals.
```

---

### 2. Project Summary Prompt

**Purpose:** Generate brief description of work per repository.

**System Prompt:**
```
You are a technical translator converting Git commits into business-readable project summaries.
Your audience is managers who need to understand what happened in each project.
Use business language and focus on outcomes, not implementation details.
```

**User Prompt Template:**
```
Generate a project summary for repository: {repository_name}

Repository description: {repository_description}

Commits ({commit_count}):
{commit_list}

Requirements:
- One sentence summary
- Business language (no technical jargon)
- Focus on what was accomplished, not how
- Highlight business value
- Be specific but brief

Project Summary:
```

**Example Output:**
```
Authentication improvements and user experience enhancements
```

**Bad Examples (Avoid):**
```
❌ "Refactored OAuth2 implementation using async/await patterns"
❌ "Updated dependencies and fixed TypeScript errors"
❌ "Merged 8 pull requests with 245 insertions and 67 deletions"
```

---

### 3. Contributor Summary Prompt

**Purpose:** Summarize individual contributor's work without scoring.

**System Prompt:**
```
You are summarizing an individual's engineering contributions in business terms.
Your audience is managers who want to understand what each person worked on.
CRITICAL: Do not rank, score, or compare contributors.
Focus on describing work, not evaluating performance.
Use neutral, respectful language.
```

**User Prompt Template:**
```
Generate a contributor summary for: {contributor_name}

Commits ({commit_count}):
{commit_list}

Repositories worked on:
{repository_list}

Requirements:
- One sentence summary
- Describe work in business terms
- DO NOT rank or score the contributor
- DO NOT compare to other contributors
- DO NOT mention lines of code or commit counts
- Focus on what areas they contributed to
- Use neutral, respectful language

Contributor Summary:
```

**Example Output:**
```
Worked on authentication system and user management features
```

**Bad Examples (Avoid):**
```
❌ "Top performer with 6 commits" (ranking)
❌ "Highly productive, added 245 lines" (productivity metric)
❌ "More active than other team members" (comparison)
❌ "Fixed bugs in the OAuth2 implementation" (too technical)
```

---

### 4. Management Notes Prompt

**Purpose:** Provide actionable insights for leadership.

**System Prompt:**
```
You are an engineering advisor providing insights to leadership.
Your audience is managers and executives who need actionable information.
Identify patterns, risks, and opportunities.
Be honest but constructive.
Focus on what leadership should know or do.
```

**User Prompt Template:**
```
Generate management notes based on this engineering activity from {date}.

Overall activity:
- {commit_count} commits
- {repository_count} repositories
- {contributor_count} contributors

Repository distribution:
{repository_distribution}

Patterns observed:
{patterns}

Requirements:
- 2-3 sentences
- Highlight important observations
- Identify potential risks or concerns
- Suggest areas requiring leadership attention
- Be actionable and specific
- Use business language

Management Notes:
```

**Example Output:**
```
High activity on customer-facing projects indicates strong focus on strategic initiatives. Team is well-distributed across key repositories. No unusual patterns or concerns detected. Consider reviewing authentication changes with security team before release.
```

**Pattern Detection Examples:**
```
✓ "Concentrated effort on single repository may indicate priority shift"
✓ "Multiple contributors working on same area suggests good collaboration"
✓ "Low activity may indicate planning phase or blocked work"
✓ "Security-related changes should be reviewed before deployment"
```

---

## Prompt Rules

### MUST Rules

1. **MUST use business language** - No technical jargon
2. **MUST be factual** - Only use provided commit data
3. **MUST be concise** - Keep summaries brief
4. **MUST be respectful** - Neutral language for contributors
5. **MUST avoid scoring** - No rankings or productivity metrics
6. **MUST be actionable** - Provide useful insights

### MUST NOT Rules

1. **MUST NOT mention lines of code** - No LOC metrics
2. **MUST NOT rank developers** - No performance comparisons
3. **MUST NOT invent repositories** - Only use provided data
4. **MUST NOT invent contributors** - Only use provided data
5. **MUST NOT use technical jargon** - Business language only
6. **MUST NOT analyze code** - Commits only, no code review
7. **MUST NOT make assumptions** - Stick to facts

---

## Language Guidelines

### Business Language Translation

| Technical Term | Business Translation |
|----------------|---------------------|
| "Refactored code" | "Improved system maintainability" |
| "Fixed bug" | "Resolved issue" |
| "Added feature" | "Implemented capability" |
| "Updated dependencies" | "Maintained system currency" |
| "Optimized performance" | "Improved system efficiency" |
| "Merged PR" | "Integrated changes" |
| "Deployed to production" | "Released to customers" |
| "Added unit tests" | "Improved quality assurance" |

### Forbidden Terms

❌ **Never use:**
- Lines of code (LOC)
- Commits per day
- Productivity metrics
- Performance rankings
- Technical stack details
- Implementation specifics
- Code quality scores

### Preferred Terms

✓ **Use instead:**
- Business capabilities
- Customer value
- Strategic alignment
- Project focus
- Team collaboration
- System improvements
- Feature delivery

---

## Quality Validation

### Summary Quality Checklist

- [ ] Uses business language (no jargon)
- [ ] Factually accurate (based on commits)
- [ ] Concise (appropriate length)
- [ ] Actionable (provides insights)
- [ ] Respectful (neutral tone)
- [ ] Complete (all sections present)
- [ ] Readable (under 60 seconds)

### Validation Prompts

**Check for Technical Jargon:**
```
Review this summary and identify any technical jargon that should be replaced with business language:
{summary}
```

**Check for Scoring/Ranking:**
```
Review this contributor summary and identify any language that ranks, scores, or compares contributors:
{contributor_summary}
```

---

## Error Handling

### Insufficient Data

**If commits are empty:**
```
Executive Summary: "No engineering activity recorded for this date."
Projects: []
Contributors: []
Management Notes: "No commits collected. Verify data collection is functioning correctly."
```

### LLM Failure

**Fallback template:**
```
Executive Summary: "Engineering activity included {commit_count} commits across {repository_count} projects."
Projects: [Use repository names with commit counts]
Contributors: [Use contributor names with commit counts]
Management Notes: "Detailed analysis unavailable. Review commit details for more information."
```

---

## Testing Prompts

### Test Case 1: Single Repository

**Input:**
```json
{
  "commits": [
    {"repository": "api", "title": "feat: add user endpoint"},
    {"repository": "api", "title": "fix: handle null values"}
  ]
}
```

**Expected Output:**
```
Executive Summary: "Engineering focused on API development with 2 commits."
Projects: [{"repository": "api", "summary": "User management and error handling improvements"}]
```

---

### Test Case 2: Multiple Contributors

**Input:**
```json
{
  "contributors": [
    {"name": "Alice", "commit_count": 3},
    {"name": "Bob", "commit_count": 2}
  ]
}
```

**Expected Output:**
```
Contributors: [
  {"name": "Alice", "summary": "Worked on [areas]"},
  {"name": "Bob", "summary": "Contributed to [areas]"}
]
```

**Must NOT include:**
- "Alice was more productive than Bob"
- "Top contributor: Alice"
- "Alice: 3 commits, Bob: 2 commits"

---

## LLM Configuration

### Recommended Settings

```json
{
  "model": "gpt-4",
  "temperature": 0.3,
  "max_tokens": 500,
  "top_p": 0.9,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

**Rationale:**
- **Low temperature (0.3):** Consistent, factual output
- **Max tokens (500):** Sufficient for summaries
- **Top_p (0.9):** Balanced creativity
- **No penalties:** Avoid repetition issues

---

## Monitoring and Improvement

### Quality Metrics

1. **Readability:** Time to read < 60 seconds
2. **Accuracy:** Matches commit data
3. **Business Language:** No technical jargon
4. **Actionability:** Provides useful insights
5. **Consistency:** Similar format across reports

### Feedback Loop

1. **Collect user feedback** on report quality
2. **Review flagged reports** for issues
3. **Update prompts** based on patterns
4. **Test changes** before deployment
5. **Document improvements** in this file

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-17 | Initial prompt specification |

---

## Related Documentation

- [ADR-002: Business Language Reporting](../adr/ADR-002-business-language-reporting.md)
- [ADR-004: Signals Over Surveillance](../adr/ADR-004-signals-over-surveillance.md)
- [ADR-005: AI Generates Summaries](../adr/ADR-005-ai-generates-summaries-not-facts.md)
- [Product Requirements](../product/requirements.md)
- [Domain Model](../architecture/domain-model.md)

---

**Last Updated:** 2026-06-17

**Version:** 1.0.0