# ADR-001: Commits Are The Source Of Truth

## Status

Accepted

## Date

2026-06-16

## Context

Cogence aims to transform engineering activity into business-readable intelligence. Modern software organizations generate signals from multiple sources:

- Git commits
- Pull requests
- Jira tickets
- Deployments
- Slack conversations
- Monitoring and incident data
- Code reviews

While all these sources provide valuable information, attempting to integrate them all in the MVP creates significant complexity:

- Multiple API integrations to build and maintain
- Complex data correlation logic across systems
- Higher risk of scope creep
- Longer time to first value
- More authentication and permission management

The core question is: What is the minimum viable source of truth that can provide meaningful engineering intelligence?

## Decision

**MVP v1 uses Git commits as the only source of engineering activity.**

All initial intelligence, reports, and insights will be derived exclusively from commit history. No other data sources (Jira, PRs, deployments, Slack, monitoring) will be integrated in the first version.

## Consequences

### Positive

- **Focused scope**: Single integration point reduces complexity dramatically
- **Universal availability**: Every software organization uses Git
- **Rich signal**: Commits contain author, timestamp, message, files changed, and diff content
- **Faster MVP delivery**: Eliminates multi-system integration overhead
- **Simpler authentication**: Only Git provider credentials needed
- **Validates core hypothesis**: Tests whether commit-based intelligence provides value before expanding
- **Aligns with "Incremental Intelligence" principle**: Start simple, add sophistication when proven valuable

### Negative

- **Limited context**: Cannot correlate commits with tickets, deployments, or incidents
- **Missing workflow data**: No PR review information or approval flows
- **No deployment correlation**: Cannot track what's in production vs. committed
- **Incomplete picture**: Some engineering work (meetings, planning, incidents) won't be visible
- **May miss important signals**: Critical information might exist only in other systems

## Alternatives Considered

### Multi-Source Integration from Day One

Integrate Git, Jira, GitHub/GitLab PRs, and deployment systems simultaneously.

**Rejected because:**
- Dramatically increases MVP complexity
- Requires 4-5x more integration work
- Delays validation of core value proposition
- Violates "Incremental Intelligence" principle
- Higher risk of building something nobody wants

### Pull Requests as Primary Source

Use PR data instead of commits as the foundation.

**Rejected because:**
- Not all teams use PRs (some commit directly to main)
- PRs are a GitHub/GitLab-specific concept
- Commits are more universal and fundamental
- Can add PR data later as enhancement

### Jira Tickets as Primary Source

Use project management data as the source of truth.

**Rejected because:**
- Jira data describes planned work, not actual engineering activity
- Not all organizations use Jira
- Doesn't capture actual code changes
- Further from the "engineering activity" we want to translate

## Revisit Conditions

This decision should be reconsidered when:

1. **MVP validation complete**: After proving commit-based intelligence provides value to users
2. **Clear gaps identified**: When users consistently request specific data from other sources
3. **Correlation needs emerge**: When commit data alone cannot answer critical business questions
4. **Deployment tracking required**: When understanding production state becomes essential
5. **Incident correlation needed**: When connecting engineering activity to operational issues becomes valuable

The next data source should be added based on user feedback and demonstrated need, not speculation.