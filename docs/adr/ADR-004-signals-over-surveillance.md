# ADR-004: Signals Over Surveillance

## Status

Accepted

## Date

2026-06-16

## Context

Engineering analytics tools often create metrics that rank or score individual developers:

- Lines of code written
- Commit counts
- Pull request velocity
- Code review participation
- "Productivity scores"
- Developer leaderboards
- Activity rankings
- Contribution percentages

These metrics are easy to calculate and appear objective. Many organizations request them.

However, individual developer metrics create serious problems:

**Measurement Gaming**: Developers optimize for metrics rather than outcomes (commit spam, unnecessary code)

**Toxic Culture**: Rankings create competition instead of collaboration

**Misleading Conclusions**: Metrics lack context (senior developers may commit less but provide more value through design, mentoring, code review)

**Trust Erosion**: Developers feel monitored rather than supported

**Wrong Focus**: Emphasizes individual activity over team outcomes

**Ethical Concerns**: Surveillance-style metrics can be used for unfair performance evaluation

Cogence's mission is to provide organizational visibility, not workforce surveillance.

The fundamental question is: Should Cogence rank or score individual developers?

## Decision

**Cogence does not rank developers.**

The platform will NOT include:
- Developer leaderboards
- Productivity scores
- Lines of code rankings
- Commit count rankings
- Individual performance metrics
- Comparative developer analytics
- "Top contributor" lists

Cogence will provide:
- Contributor summaries (who worked on what)
- Team-level activity patterns
- Organizational insights
- Project-level progress

Individual developers are mentioned in context of their contributions, never ranked or scored.

## Consequences

### Positive

- **Builds trust**: Developers won't fear surveillance
- **Aligns with "Signals Over Surveillance" principle**: Core founding principle
- **Encourages adoption**: Engineering teams more likely to support tool that doesn't rank them
- **Focuses on outcomes**: Emphasizes what was accomplished, not who did most
- **Avoids gaming**: No metrics to optimize for
- **Ethical foundation**: Respects developer dignity and privacy
- **Team-oriented**: Promotes collaboration over competition
- **Reduces misuse risk**: Cannot be weaponized for unfair performance reviews

### Negative

- **May disappoint some managers**: Some leaders expect individual metrics
- **Harder to identify underperformance**: Cannot easily spot low-activity developers
- **Less "actionable" for HR**: Doesn't provide performance evaluation data
- **Competitive disadvantage**: Other tools offer individual metrics
- **Requires cultural alignment**: Only works for organizations that value team over individual metrics

## Alternatives Considered

### Optional Individual Metrics with Consent

Allow individual metrics but require explicit developer consent.

**Rejected because:**
- Consent under workplace pressure is not truly voluntary
- Creates two-tier system (those who consent vs. those who don't)
- Still enables surveillance culture
- Adds complexity to permission system
- Violates core principle even if "optional"

### Aggregate Individual Metrics Only

Show individual data only in aggregate (team averages, distributions).

**Rejected because:**
- Still requires collecting individual metrics
- Aggregates can be reverse-engineered in small teams
- Doesn't fully address surveillance concerns
- Better to not collect the data at all

### Individual Metrics for Self-Reflection Only

Provide individual metrics only to the developer themselves, not managers.

**Rejected for MVP because:**
- Adds complexity to permission and access control
- Developers already have Git tools for self-reflection
- Not aligned with Cogence's mission (business intelligence for managers)
- Could be considered for future version if requested

## Implementation Guidelines

### What We DO Show

**Contributor Summaries** (non-ranked):
- "Sean worked on customer platform improvements"
- "Donald focused on AI workflow updates"
- "Florentino enhanced frontend components"

**Team Activity**:
- "3 developers contributed to the project"
- "Engineering activity focused on two main areas"

**Project Context**:
- "Customer platform received most attention"
- "Backend and frontend both saw active development"

### What We DON'T Show

**Rankings**:
- ❌ "Top 5 contributors this week"
- ❌ "Sean: 45 commits, Donald: 32 commits, Florentino: 28 commits"

**Scores**:
- ❌ "Developer productivity score: 87/100"
- ❌ "Code contribution index"

**Comparisons**:
- ❌ "Sean contributed 40% more than team average"
- ❌ "Florentino's activity decreased 25% this week"

## Relationship to Other ADRs

This decision reinforces:
- **ADR-002 (Business Language)**: Focus on outcomes, not individual performance
- **ADR-003 (No Code Analysis)**: Avoid metrics that could become surveillance tools

This decision is reinforced by:
- **Principle 2: Signals Over Surveillance**: Core founding principle
- **Principle 7: Trust Is Mandatory**: Rankings erode trust

## Revisit Conditions

This decision should be reconsidered when:

1. **Never for surveillance purposes**: Individual rankings for performance evaluation remain prohibited
2. **Self-reflection features**: If developers request personal analytics for their own growth
3. **Team health indicators**: If non-ranking team dynamics insights become valuable
4. **Contribution attribution**: If understanding who has context on specific areas becomes necessary for operational reasons (not evaluation)

Even in future versions, any individual metrics must:
- Serve the individual developer, not management surveillance
- Be opt-in with genuine consent
- Never be used for rankings or comparisons
- Align with "Signals Over Surveillance" principle

This is a founding principle, not just an MVP decision.