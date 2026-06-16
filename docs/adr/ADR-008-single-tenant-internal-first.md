# ADR-008: Single-Tenant Internal First

## Status

Accepted

## Date

2026-06-16

## Context

SaaS products can be architected in two fundamentally different ways:

**Multi-Tenant Architecture**:
- Multiple organizations share infrastructure
- Data isolation through application logic
- Complex tenant management
- Shared database with tenant_id columns
- Organization switching, billing, permissions

**Single-Tenant Architecture**:
- One organization per deployment
- Data isolation through infrastructure
- Simpler application logic
- No tenant management needed
- Dedicated resources per organization

For a new product, multi-tenancy seems like the "right" way to build SaaS. However, multi-tenancy adds significant complexity:

- Tenant isolation logic in every query
- Organization management UI
- Billing and subscription system
- Data migration between tenants
- Security boundaries
- Performance isolation
- Tenant-specific configuration

The critical insight: **You already work in a real company with real repositories.**

You can build Cogence for your own organization first, validate the value proposition, then add multi-tenancy later if needed.

## Decision

**Build for internal use before multi-tenancy.**

Cogence MVP v1 is a single-tenant application designed for one organization (your own company).

### What This Means

**No Multi-Tenant Features**:
- No organization switching
- No tenant_id in database
- No organization management UI
- No billing system
- No subscription tiers
- No per-tenant configuration

**Single Organization Assumptions**:
- Hardcoded or environment-configured organization name
- All users belong to same organization
- All repositories belong to same organization
- Shared configuration
- No data isolation concerns

**Deployment Model**:
- Self-hosted for your organization
- Single database instance
- Single application instance
- No tenant routing

## Consequences

### Positive

- **Dramatically simpler architecture**: No tenant isolation logic
- **Faster MVP delivery**: Eliminates months of multi-tenant infrastructure
- **Real validation**: Test with actual company data and users
- **Immediate value**: Solve your own problem first
- **Authentic feedback**: Real users with real needs
- **No premature optimization**: Don't build multi-tenancy until proven necessary
- **Simpler database schema**: No tenant_id everywhere
- **Easier debugging**: No tenant-specific issues
- **Focus on core value**: Spend time on intelligence, not infrastructure
- **Aligns with "Incremental Intelligence"**: Start simple, add complexity when proven

### Negative

- **Cannot sell to other companies immediately**: No SaaS offering
- **Architecture migration later**: Will need refactoring for multi-tenancy
- **Limited market validation**: Only one organization's feedback
- **No revenue model**: Cannot charge other companies
- **Potential rework**: Multi-tenant architecture may require significant changes
- **Missed early adopters**: Cannot onboard external beta users easily

## Alternatives Considered

### Multi-Tenant from Day One

Build full multi-tenant architecture in MVP.

**Rejected because:**
- Adds 3-6 months to MVP timeline
- Requires organization management, billing, tenant isolation
- Cannot validate core value until infrastructure is complete
- Violates "Incremental Intelligence" principle
- Risk of building complex infrastructure nobody wants
- You already have a real organization to serve

### Hybrid: Multi-Tenant Database, Single-Tenant UI

Build multi-tenant data model but single-tenant application.

**Rejected because:**
- Still requires tenant_id in every table
- Adds complexity without immediate benefit
- Harder to migrate later (committed to multi-tenant schema)
- No real advantage over pure single-tenant

### Multiple Single-Tenant Deployments

Deploy separate instances for each organization.

**Rejected for MVP because:**
- Still requires deployment automation
- Adds operational complexity
- Not needed when serving only one organization
- Can be considered later as path to multi-tenancy

## Implementation Guidelines

### Configuration

Store organization details in:
- Environment variables
- Configuration file
- Database (single row, no tenant_id)

Example:
```
ORGANIZATION_NAME=Acme Corp
GITEA_URL=https://git.acme.com
GITEA_TOKEN=xxx
```

### Database Schema

No tenant_id columns:
```sql
CREATE TABLE commits (
  id UUID PRIMARY KEY,
  repository VARCHAR,
  author VARCHAR,
  -- No tenant_id or organization_id
);
```

### Authentication

Simple authentication:
- All users belong to same organization
- No organization switching
- No tenant-specific permissions

### Deployment

Single instance:
- One server
- One database
- One application
- No tenant routing

## Path to Multi-Tenancy (Future)

When multi-tenancy becomes necessary:

### Phase 1: Multi-Tenant Data Model
- Add organization_id to tables
- Migrate existing data to first organization
- Add tenant isolation to queries

### Phase 2: Organization Management
- Organization creation/management UI
- User-organization relationships
- Organization switching

### Phase 3: Deployment Infrastructure
- Tenant routing
- Per-tenant configuration
- Resource isolation

### Phase 4: Business Model
- Billing system
- Subscription tiers
- Payment processing

Each phase can be added incrementally based on demand.

## Relationship to Other ADRs

This decision reinforces:
- **ADR-001 (Commits Are Source of Truth)**: Simpler with single organization
- **ADR-011 (Scheduled Collection)**: Easier to schedule for single tenant

This decision is reinforced by:
- **Principle 5: Incremental Intelligence**: Start simple, add complexity when proven
- **MVP Philosophy**: Validate value before building infrastructure

## Revisit Conditions

This decision should be reconsidered when:

1. **MVP validated with internal users**: After proving Cogence provides value to your organization
2. **External demand emerges**: When other companies request access
3. **Revenue opportunity identified**: When business model becomes clear
4. **Scale requirements**: When serving multiple organizations becomes necessary
5. **Investment secured**: When resources available to build multi-tenant infrastructure

Multi-tenancy should only be added when:
- Core value is proven
- External customers are waiting
- Business model is validated
- Resources are available for significant refactoring

## Key Insight

**You already have a real company with real repositories.**

This is an enormous advantage. Most startups build products for hypothetical users. You can build for yourself, validate with real data, and iterate based on authentic feedback.

Exploit this advantage. Build for your organization first. Add multi-tenancy later if the product proves valuable.

Single-tenant is not a limitation for MVP. It's a strategic advantage.