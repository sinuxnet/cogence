# ADR-006: Daily Report First

## Status

Accepted

## Date

2026-06-16

## Context

Engineering intelligence can be delivered at multiple time scales:

- **Real-time**: Continuous updates as commits happen
- **Hourly**: Updates every hour
- **Daily**: Once per day summary
- **Weekly**: End of week rollup
- **Monthly**: Monthly retrospective
- **Quarterly**: Strategic overview

Each time scale serves different purposes:
- Real-time: Operational monitoring
- Daily: Recent activity awareness
- Weekly: Sprint/iteration review
- Monthly: Trend analysis
- Quarterly: Strategic planning

The question is: Which time scale should Cogence prioritize for MVP?

### Considerations

**Daily Reports**:
- Answers "What happened yesterday?"
- Manageable information volume
- Frequent enough to be relevant
- Not overwhelming
- Natural cadence for managers

**Weekly Reports**:
- Aligns with sprint cycles
- More comprehensive view
- Less frequent interruption
- Risk of information overload

**Real-time**:
- Immediate visibility
- Complex infrastructure
- May be too noisy
- Not aligned with manager workflow

The MVP must validate core value with minimal complexity.

## Decision

**Daily reports are the primary output.**

Cogence MVP v1 will generate one report per day, summarizing engineering activity from the previous 24 hours.

Weekly and monthly reports are explicitly excluded from MVP and will be derived later as aggregations of daily reports.

### Report Timing

- Generated once per day
- Covers previous 24-hour period
- Delivered at consistent time (e.g., 8 AM local time)
- No real-time updates
- No on-demand generation (for MVP)

## Consequences

### Positive

- **Clear scope**: One report type to build and perfect
- **Manageable information**: 24 hours of activity is digestible
- **Frequent feedback**: Daily cadence enables rapid iteration
- **Natural rhythm**: Aligns with daily standup culture
- **Validates core value**: If daily reports aren't useful, longer periods won't help
- **Simple architecture**: No complex aggregation logic needed
- **Consistent delivery**: Predictable schedule for users
- **Aligns with "Incremental Intelligence"**: Start with simplest useful cadence

### Negative

- **No weekly summaries**: Cannot see sprint-level patterns
- **No monthly trends**: Cannot identify long-term trends
- **Limited historical context**: Each report is isolated
- **May miss multi-day patterns**: Some work spans multiple days
- **No real-time alerts**: Cannot notify about urgent issues immediately
- **Fixed schedule**: Cannot generate reports on-demand

## Alternatives Considered

### Weekly Reports First

Start with weekly summaries instead of daily.

**Rejected because:**
- Longer feedback loop for MVP validation
- More information to process (harder to consume)
- Misses daily activity visibility
- Weekly reports can be built from daily reports later
- Daily is more fundamental unit

### Multiple Cadences from Day One

Build daily, weekly, and monthly reports simultaneously.

**Rejected because:**
- Triples MVP complexity
- Requires aggregation logic
- Delays validation of core value
- Violates "Incremental Intelligence" principle
- Can add weekly/monthly later if daily proves valuable

### Real-Time Activity Stream

Continuous updates as commits happen.

**Rejected because:**
- Complex infrastructure (webhooks, streaming)
- Too noisy for managers
- Not aligned with manager workflow
- Requires always-on monitoring
- Significantly more complex than batch processing

### On-Demand Reports

Generate reports when user requests them.

**Rejected for MVP because:**
- Requires interactive UI
- Adds complexity to report generation
- Managers want consistent delivery, not on-demand
- Can be added later as enhancement
- Scheduled delivery is simpler

## Implementation Guidelines

### Report Generation

- Run once per day at scheduled time
- Collect commits from previous 24 hours
- Generate structured data
- Generate AI summary
- Store report
- Deliver to users

### Time Window

- Fixed 24-hour window
- Based on UTC or organization timezone
- Consistent start/end time daily
- No overlap between reports
- No gaps between reports

### Delivery

For MVP:
- Store in database
- Display in web UI
- (Optional) Email notification

Future enhancements:
- Slack integration
- Email with full report
- Mobile notifications

## Future Evolution

### Weekly Reports (Post-MVP)

Can be derived from daily reports:
- Aggregate 7 daily reports
- Identify weekly patterns
- Highlight week-over-week changes
- Useful for sprint retrospectives

### Monthly Reports (Post-MVP)

Can be derived from daily/weekly reports:
- Aggregate 30 daily reports
- Identify monthly trends
- Compare month-over-month
- Useful for strategic planning

### Real-Time Alerts (Post-MVP)

Can be added for specific scenarios:
- Unusual activity patterns
- Security concerns
- Critical incidents
- Not for routine activity

### On-Demand Reports (Post-MVP)

Can be added for flexibility:
- Custom date ranges
- Specific repositories
- Specific contributors
- Ad-hoc analysis

## Relationship to Other ADRs

This decision reinforces:
- **ADR-001 (Commits Are Source of Truth)**: Daily batch collection from Git
- **ADR-011 (Scheduled Collection)**: Aligns with periodic polling model

This decision is reinforced by:
- **Principle 5: Incremental Intelligence**: Start with simplest useful cadence
- **Principle 6: Human-Centered Reporting**: Daily reports are consumable

## Revisit Conditions

This decision should be reconsidered when:

1. **Daily reports validated**: After proving daily reports provide value
2. **Weekly patterns needed**: When users consistently ask for weekly summaries
3. **Trend analysis required**: When understanding long-term patterns becomes important
4. **Real-time needs emerge**: When immediate notification becomes critical
5. **Custom timeframes requested**: When users need flexible date ranges

Weekly and monthly reports should be added when:
- Daily reports are proven valuable
- Users explicitly request longer timeframes
- Implementation can reuse daily report infrastructure
- Aggregation logic is straightforward

Daily reports remain the foundation. All other cadences are derived from or supplement daily reports.