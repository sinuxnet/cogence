# ADR-011: Scheduled Collection Model

## Status

Accepted

## Date

2026-06-16

## Context

Cogence needs to collect commit data from Gitea. There are two fundamental approaches:

**Push Model (Webhooks)**:
- Gitea sends events when commits happen
- Real-time data collection
- Event-driven architecture
- Requires webhook endpoint
- Requires webhook configuration in Gitea

**Pull Model (Polling)**:
- Cogence periodically queries Gitea API
- Scheduled data collection
- Batch processing
- No Gitea configuration needed
- Simpler architecture

### Webhook Considerations

**Advantages**:
- Real-time updates
- No polling overhead
- Event-driven (modern pattern)
- Immediate data availability

**Disadvantages**:
- Requires webhook configuration in Gitea
- Requires public endpoint or tunnel
- Requires webhook authentication/verification
- Requires handling webhook failures and retries
- Requires idempotency logic
- More complex error handling
- Harder to test locally

### Polling Considerations

**Advantages**:
- No Gitea configuration needed
- Simpler architecture
- Easier to test and debug
- Predictable resource usage
- Can batch process efficiently
- Works with any Git provider

**Disadvantages**:
- Not real-time (delay up to polling interval)
- Periodic API calls (even when no changes)
- Potential for missed data if polling fails

The critical question: Does Cogence need real-time data collection for MVP?

## Decision

**Poll Gitea periodically instead of using webhooks.**

Cogence will use a scheduled collection model:
- Run collection job on fixed schedule (e.g., every hour or daily)
- Query Gitea API for commits since last collection
- Process commits in batch
- Store results in database

No webhook infrastructure will be built for MVP.

### Collection Schedule

For MVP:
- Run once per day (aligned with daily report generation)
- Collect commits from previous 24 hours
- Run at consistent time (e.g., 6 AM)

Future enhancement:
- More frequent collection (hourly)
- On-demand collection via API

## Consequences

### Positive

- **Dramatically simpler architecture**: No webhook endpoint, authentication, or retry logic
- **No Gitea configuration**: Works out of the box with API token
- **Easier testing**: Can trigger collection manually
- **Predictable resource usage**: Known when collection runs
- **Batch efficiency**: Process multiple commits together
- **Provider agnostic**: Works with any Git provider with API
- **Easier debugging**: Clear execution timeline
- **Aligns with daily reports**: Collection schedule matches report schedule
- **No public endpoint needed**: Can run entirely internal

### Negative

- **Not real-time**: Data delayed by up to polling interval
- **Periodic API calls**: Uses API quota even when no changes
- **Potential missed data**: If collection fails, must retry
- **Less "modern"**: Webhooks are more event-driven
- **Polling overhead**: Regular API calls consume resources

## Alternatives Considered

### Webhook-Based Collection

Gitea sends webhook events when commits happen.

**Rejected because:**
- Requires webhook configuration in Gitea (setup friction)
- Requires public endpoint or ngrok tunnel (complexity)
- Requires webhook authentication (security complexity)
- Requires idempotency logic (duplicate events)
- Requires retry mechanism (failed webhooks)
- MVP doesn't need real-time data (daily reports)
- Significantly more complex for uncertain benefit

### Hybrid: Webhooks + Polling Fallback

Use webhooks when available, fall back to polling.

**Rejected because:**
- Doubles complexity (must implement both)
- Harder to test (two code paths)
- Unclear which path is primary
- Violates "Incremental Intelligence" principle
- Can add webhooks later if needed

### Continuous Polling (Very Frequent)

Poll every minute for near-real-time updates.

**Rejected because:**
- Wastes API quota
- Unnecessary for daily reports
- Adds load to Gitea
- No user benefit for MVP
- Can increase frequency later if needed

## Implementation Details

### Scheduler

Use APScheduler (Python scheduling library):

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=6, minute=0)
async def collect_commits():
    """Run daily at 6 AM"""
    await collection_service.collect_all_repositories()
```

### Collection Logic

```python
async def collect_all_repositories():
    # Get all repositories
    repos = await gitea_client.list_repositories()
    
    # Get last collection timestamp
    last_collection = await db.get_last_collection_time()
    
    # Collect commits since last collection
    for repo in repos:
        commits = await gitea_client.get_commits(
            repo=repo,
            since=last_collection
        )
        await db.store_commits(commits)
    
    # Update collection timestamp
    await db.set_last_collection_time(now())
```

### Error Handling

- Log collection failures
- Retry on transient errors
- Alert on repeated failures
- Store collection status in database

### API Rate Limiting

- Respect Gitea API rate limits
- Implement exponential backoff
- Batch requests when possible
- Cache repository list

## Scheduling Options

### MVP Schedule

**Daily Collection**:
- Run once per day at 6 AM
- Collect previous 24 hours
- Aligns with daily report generation
- Minimal API usage

### Future Enhancements

**Hourly Collection**:
- More frequent updates
- Smaller batches
- Better for real-time needs

**On-Demand Collection**:
- Manual trigger via API
- Useful for testing
- Useful for immediate updates

**Smart Scheduling**:
- More frequent during business hours
- Less frequent at night
- Adaptive based on activity patterns

## Relationship to Other ADRs

This decision reinforces:
- **ADR-001 (Commits Are Source of Truth)**: Periodic Git API polling
- **ADR-006 (Daily Report First)**: Daily collection matches daily reports
- **ADR-008 (Single-Tenant)**: Simpler scheduling for single organization
- **ADR-009 (FastAPI Backend)**: APScheduler integrates with FastAPI

This decision is reinforced by:
- **Principle 5: Incremental Intelligence**: Start simple (polling), add complexity (webhooks) if needed
- **MVP Philosophy**: Validate value before building complex infrastructure

## Migration to Webhooks (Future)

If webhooks become necessary:

### Phase 1: Add Webhook Endpoint
- Create webhook receiver endpoint
- Implement webhook authentication
- Store webhook events

### Phase 2: Dual Mode
- Keep polling as fallback
- Process webhooks when received
- Deduplicate events

### Phase 3: Webhook Primary
- Make webhooks primary collection method
- Use polling only for missed events
- Reduce polling frequency

### Phase 4: Webhook Only
- Remove polling (if webhooks proven reliable)
- Keep polling code for emergency fallback

However, polling may be sufficient indefinitely for Cogence's use case.

## Performance Considerations

### API Usage

Daily polling for single organization:
- ~10-50 repositories
- 1 API call per repository per day
- ~50 API calls per day
- Well within typical API limits

### Processing Time

Batch processing is efficient:
- Collect all commits in parallel
- Process in single transaction
- Generate report after collection
- Total time: minutes, not hours

### Resource Usage

Scheduled jobs are lightweight:
- Run once per day
- Process in background
- No impact on API responsiveness
- Minimal memory usage

## Revisit Conditions

This decision should be reconsidered when:

1. **Real-time requirements emerge**: If users need immediate updates (unlikely for daily reports)
2. **Multiple organizations**: If serving many organizations, webhooks may be more efficient
3. **API rate limits**: If polling exceeds API quotas (unlikely)
4. **Gitea provides better webhook support**: If webhook setup becomes trivial
5. **User requests real-time features**: If real-time alerts become valuable

For MVP and foreseeable future, scheduled polling is sufficient.

## Key Insight

**Daily reports don't need real-time data collection.**

If reports are generated once per day, collecting data once per day is perfectly adequate. Real-time collection only matters for real-time features.

Webhooks are a solution looking for a problem in this context. Polling is simpler, more reliable, and sufficient for the use case.

Build webhooks when you need them, not because they're "modern."