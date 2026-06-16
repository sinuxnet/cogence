# ADR-010: PostgreSQL As System Of Record

## Status

Accepted

## Date

2026-06-16

## Context

Cogence needs to store:
- Commit metadata (SHA, author, timestamp, message, files)
- Repository information
- Generated reports
- AI summaries
- Aggregated statistics
- System configuration

Multiple database options are available:

**Relational Databases**:
- PostgreSQL: Mature, feature-rich, open source
- MySQL: Popular, widely supported
- SQLite: Embedded, simple

**NoSQL Databases**:
- MongoDB: Document store, flexible schema
- Redis: In-memory, fast
- Elasticsearch: Search-optimized

**Time-Series Databases**:
- TimescaleDB: PostgreSQL extension for time-series
- InfluxDB: Purpose-built for time-series

The choice impacts data integrity, query capabilities, analytics potential, and operational complexity.

## Decision

**Use PostgreSQL as the system of record.**

All persistent data will be stored in PostgreSQL:
- Commit metadata
- Repository information
- Daily reports
- AI-generated summaries
- User data (future)
- System configuration

### Version

PostgreSQL 15+ (latest stable)

## Consequences

### Positive

- **Reliable and mature**: Battle-tested in production for decades
- **ACID compliance**: Data integrity guaranteed
- **Rich query capabilities**: Complex queries, joins, aggregations
- **JSON support**: Can store semi-structured data when needed
- **Full-text search**: Built-in search capabilities
- **Analytics-ready**: Supports complex analytical queries
- **Excellent Python support**: SQLAlchemy, asyncpg
- **Future-proof**: Supports advanced features (window functions, CTEs, materialized views)
- **Open source**: No licensing costs
- **Wide ecosystem**: Tools, extensions, hosting options
- **Time-series support**: Can add TimescaleDB extension if needed

### Negative

- **Operational overhead**: Requires database management (backups, monitoring)
- **Heavier than SQLite**: More complex than embedded database
- **Vertical scaling limits**: Eventually needs sharding for massive scale
- **Not optimized for document storage**: Less flexible than MongoDB
- **Setup complexity**: More involved than file-based storage

## Alternatives Considered

### SQLite

Embedded database, no separate server.

**Rejected because:**
- Limited concurrent write performance
- No network access (harder for analytics tools)
- Less suitable for production deployments
- Harder to backup and replicate
- PostgreSQL provides more growth runway
- Can use SQLite for local development if needed

### MongoDB

Document database with flexible schema.

**Rejected because:**
- Commit data is structured and relational
- Don't need schema flexibility
- PostgreSQL's JSON support sufficient for semi-structured data
- Relational queries more natural for our data model
- PostgreSQL more familiar to most developers

### MySQL

Popular relational database.

**Rejected because:**
- PostgreSQL has better JSON support
- PostgreSQL has more advanced features
- PostgreSQL has better full-text search
- No significant advantage over PostgreSQL
- Team preference for PostgreSQL

### Redis

In-memory data store.

**Rejected as primary database because:**
- Not designed for persistent storage
- Limited query capabilities
- Expensive for large datasets
- Can be used as cache layer later if needed
- Not suitable as system of record

### TimescaleDB

PostgreSQL extension for time-series data.

**Not rejected, deferred:**
- Can be added later if time-series queries become important
- PostgreSQL alone is sufficient for MVP
- Commit data has time-series characteristics
- Good future enhancement option

## Database Schema Design

### Core Tables

**repositories**:
- id, name, url, description
- created_at, updated_at

**commits**:
- id, sha, repository_id
- author_name, author_email
- timestamp, message
- files_changed, insertions, deletions
- created_at

**daily_reports**:
- id, date
- commit_count, repository_count, contributor_count
- executive_summary (text)
- structured_data (jsonb)
- created_at

**contributors**:
- id, name, email
- first_seen, last_seen

### Indexes

- commits(timestamp) - for date range queries
- commits(repository_id) - for repository filtering
- commits(author_email) - for contributor queries
- daily_reports(date) - for report lookup

### JSON Storage

Use JSONB for semi-structured data:
- Structured commit data in daily_reports
- AI response metadata
- Configuration settings

## Technology Stack

**Database**:
- PostgreSQL 15+
- Docker container for development
- Managed service for production (optional)

**ORM**:
- SQLAlchemy 2.0+ (async)
- Alembic for migrations

**Connection**:
- asyncpg driver (high performance)
- Connection pooling

## Implementation Details

### Connection Configuration

```python
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/cogence"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
)
```

### Async Queries

```python
async def get_commits_by_date(date: str):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Commit)
            .where(Commit.timestamp >= date)
            .order_by(Commit.timestamp)
        )
        return result.scalars().all()
```

### Migrations

Use Alembic for schema migrations:
```bash
alembic revision --autogenerate -m "Add commits table"
alembic upgrade head
```

## Backup Strategy

**Development**:
- pg_dump for local backups
- Version control for schema

**Production**:
- Automated daily backups
- Point-in-time recovery
- Backup retention policy
- Test restore procedures

## Performance Considerations

For MVP scale (single organization):
- PostgreSQL easily handles millions of commits
- Proper indexes ensure fast queries
- Connection pooling prevents bottlenecks
- No special optimization needed

Future optimizations if needed:
- Partitioning by date
- Materialized views for aggregations
- Read replicas for analytics
- TimescaleDB for time-series queries

## Relationship to Other ADRs

This decision enables:
- **ADR-005 (AI Generates Summaries)**: Store structured facts and AI summaries separately
- **ADR-006 (Daily Report First)**: Efficient date-based queries
- **ADR-009 (FastAPI Backend)**: SQLAlchemy integration

This decision is reinforced by:
- **Principle 7: Trust Is Mandatory**: ACID compliance ensures data reliability
- **MVP Philosophy**: Mature, reliable technology

## Future Enhancements

### TimescaleDB Extension

Add time-series capabilities:
- Automatic partitioning by time
- Time-series specific functions
- Compression for old data
- Continuous aggregates

### Analytics Extensions

- pg_stat_statements: Query performance monitoring
- pg_trgm: Fuzzy text search
- PostGIS: If geographic data needed

### Replication

- Read replicas for analytics
- Streaming replication for high availability
- Logical replication for data distribution

## Revisit Conditions

This decision should be reconsidered when:

1. **Scale exceeds PostgreSQL**: If single instance cannot handle load (unlikely for years)
2. **Specific database features needed**: If specialized database becomes critical
3. **Cost optimization**: If managed PostgreSQL becomes too expensive
4. **Team expertise changes**: If team becomes expert in different database

For MVP and foreseeable future, PostgreSQL is the right choice.

## Migration Path

If database change becomes necessary:

1. **Schema is portable**: SQL DDL can be adapted to other databases
2. **ORM abstraction**: SQLAlchemy supports multiple databases
3. **Data export**: pg_dump, CSV export, ETL tools
4. **Gradual migration**: Can run dual databases during transition

However, database migration is unlikely to be necessary. PostgreSQL scales to massive workloads.