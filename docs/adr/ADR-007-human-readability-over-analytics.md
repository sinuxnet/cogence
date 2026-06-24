# ADR-007: Human Readability Over Analytics

## Status

Accepted

## Date

2026-06-16

## Amendment — v0.3.0 (2026-06-24)

The Contributors section (brief per-person summary) was removed from the report format. Per-goal attribution is now embedded directly on each bullet within the relevant Repository (`**Abbas**: fixed X in Y`). A separate Contributors section was redundant and forced the LLM to compress cross-repo work into a single sentence — always too vague to be actionable. The Report Footer retains contributor counts for at-a-glance statistics.

## Context

Engineering intelligence products typically evolve in one of two directions:

**Dashboard-First Products**:
- Interactive visualizations
- Charts, graphs, metrics
- Drill-down capabilities
- Real-time updates
- Customizable views

**Report-First Products**:
- Written summaries
- Narrative format
- Consumable in minutes
- Email or document delivery
- Human-readable prose

The dashboard approach seems modern and sophisticated. Most analytics products become dashboards with:
- Commit frequency charts
- Contributor activity graphs
- Repository heatmaps
- Trend lines
- Velocity metrics

However, dashboards have a critical problem: **Nobody reads them.**

Dashboards require:
- Active engagement (user must visit)
- Time to interpret (charts need analysis)
- Context switching (leave current work)
- Learning curve (understand visualizations)
- Regular checking (data doesn't come to you)

The result: Dashboards get built, briefly explored, then ignored.

Reports, by contrast:
- Come to the user (email, Slack)
- Readable in 60 seconds
- No interpretation needed
- Consumable during coffee
- Actionable immediately

The fundamental question: Should Cogence be a dashboard or a report?

## Decision

**A report is more important than a dashboard.**

Cogence MVP v1 prioritizes human-readable reports over interactive analytics dashboards.

### What This Means

**Primary Output**:
- Daily written report
- Narrative format
- Business language
- Consumable in under 60 seconds
- Delivered to user (email, web view)

**Explicitly NOT Building**:
- Interactive dashboards
- Chart visualizations
- Drill-down analytics
- Custom metric builders
- Real-time graphs

### Report Format

```
Daily Engineering Report - June 16, 2026

Executive Summary:
Engineering focused on customer-facing improvements yesterday.
The team made 15 commits across 2 projects, with primary attention
on the customer portal.

Projects Worked On:
• Customer Portal - Authentication and user experience improvements
• API Gateway - Performance optimization

Contributors:
• Sean - Customer platform enhancements
• Donald - Backend infrastructure improvements
• Florentino - Frontend component updates

Management Notes:
Activity concentrated on strategic customer-facing projects.
No unusual patterns detected.
```

This is readable in 45 seconds. A dashboard showing the same information would take 5+ minutes to interpret.

## Consequences

### Positive

- **Actually gets consumed**: Reports are read, dashboards are ignored
- **Aligns with "Human-Centered Reporting"**: Readable in minutes, not hours
- **Aligns with "Actionability Over Information"**: Clear insights, not raw data
- **Faster MVP delivery**: Writing reports is simpler than building dashboards
- **No learning curve**: Anyone can read a report
- **Passive consumption**: Report comes to user, user doesn't seek dashboard
- **Mobile-friendly**: Text is readable anywhere
- **Shareable**: Can forward report to others
- **Archivable**: Reports are historical records

### Negative

- **No interactive exploration**: Cannot drill down into data
- **No custom views**: Everyone sees same report
- **No real-time updates**: Report is static once generated
- **Limited data visualization**: No charts or graphs
- **May seem "less sophisticated"**: Dashboards appear more advanced
- **Cannot satisfy power users**: Some users want detailed analytics

## Alternatives Considered

### Dashboard-First Approach

Build interactive dashboard with charts, graphs, and drill-down capabilities.

**Rejected because:**
- Dashboards require active engagement (users must visit)
- Takes 5-10 minutes to interpret visualizations
- Requires learning curve
- Most analytics dashboards go unused
- Violates "Human-Centered Reporting" principle
- Significantly more complex to build
- Doesn't align with target user (busy managers)

### Hybrid: Report + Dashboard

Provide both written report and interactive dashboard.

**Rejected because:**
- Doubles development effort
- Splits focus between two interfaces
- Risk of inconsistency between report and dashboard
- Violates "Incremental Intelligence" principle
- Dashboard will likely go unused anyway
- Can add dashboard later if reports prove insufficient

### Report with Embedded Charts

Written report with inline visualizations.

**Rejected for MVP because:**
- Adds complexity to report generation
- Charts require interpretation (slows consumption)
- Text-only reports are sufficient for MVP
- Can add charts later if needed
- Keeps report generation simple

## Implementation Guidelines

### Report Structure

Every report must:
1. Be readable in under 60 seconds
2. Use business language (no technical jargon)
3. Provide actionable insights
4. Answer "So what?"
5. Be consumable without context

### Report Sections

**Required**:
- Executive Summary (2-3 sentences)
- Projects Worked On (bullet list)
- Contributors (brief summaries, no rankings)
- Management Notes (observations)

**Forbidden**:
- Charts or graphs
- Technical metrics
- Developer rankings
- Raw data dumps

### Delivery Methods

**MVP**:
- Web view (simple HTML page)
- Database storage

**Future**:
- Email delivery
- Slack integration
- PDF export
- Mobile app

### Report Quality Criteria

A good report:
- Manager can read it during morning coffee
- Answers "What happened?" without additional context
- Identifies what requires attention
- Uses language a non-technical CEO understands
- Provides value in 60 seconds or less

## Dashboard Future (Maybe)

If dashboards become necessary later:

### When to Add Dashboard

Only if:
- Reports prove insufficient for specific use cases
- Users explicitly request interactive exploration
- Specific questions cannot be answered by reports
- Power users need detailed analytics

### Dashboard Principles

If built, dashboard must:
- Supplement reports, not replace them
- Be optional (reports remain primary)
- Serve specific use cases
- Not become the primary interface

### Potential Dashboard Use Cases

- Historical trend analysis (multi-month patterns)
- Repository comparison
- Contributor activity over time
- Custom date range exploration

But these are future enhancements, not MVP requirements.

## Relationship to Other ADRs

This decision reinforces:
- **ADR-002 (Business Language)**: Reports use business language
- **ADR-004 (Signals Over Surveillance)**: Reports avoid ranking metrics
- **ADR-006 (Daily Report First)**: Daily report is primary output

This decision is reinforced by:
- **Principle 6: Human-Centered Reporting**: Reports readable in minutes
- **Principle 8: Actionability Over Information**: Reports drive decisions
- **MVP Philosophy**: Validate value with simplest solution

## Key Insight

**Most analytics products become dashboards nobody reads.**

This is the analytics product graveyard:
1. Build sophisticated dashboard
2. Users explore it initially
3. Novelty wears off
4. Dashboard requires too much effort
5. Users stop visiting
6. Dashboard becomes unused

Reports avoid this trap:
1. Generate report
2. Deliver to user
3. User reads in 60 seconds
4. User takes action
5. Repeat daily

The best analytics product is one that actually gets used.

## Revisit Conditions

This decision should be reconsidered when:

1. **Reports prove insufficient**: If users consistently cannot answer questions from reports
2. **Interactive exploration needed**: If specific use cases require drill-down
3. **Power user segment emerges**: If subset of users need detailed analytics
4. **Competitive pressure**: If lack of dashboard becomes sales obstacle
5. **Report consumption drops**: If users stop reading reports (unlikely if well-designed)

Even if dashboard is added:
- Reports remain primary interface
- Dashboard supplements, doesn't replace
- Report quality is never compromised for dashboard features

## Success Metric

The success of this decision is measured by:

**Report consumption rate**: Percentage of users who read reports regularly

If 80%+ of users read reports weekly, this decision is validated.

If users ignore reports and request dashboards, reconsider.

But bet on reports. They work.