# Architecture Decisions Quick Reference

This document provides a quick overview of all Architecture Decision Records (ADRs) for Cogence. For detailed information, see the individual ADR documents.

---

## Core Decisions

### [ADR-001: Commits as Source of Truth](../adr/ADR-001-commits-as-source-of-truth.md)
**Decision:** Use Git commits as the only data source for MVP v1  
**Rationale:** Simplifies scope, universal availability, validates core hypothesis  
**Impact:** No PR, Jira, or deployment integration in MVP

### [ADR-002: Business Language in Reporting](../adr/ADR-002-business-language-reporting.md)
**Decision:** Reports use business language, not technical jargon  
**Rationale:** Target audience is non-technical managers  
**Impact:** AI summaries must translate technical activity to business terms

### [ADR-003: No Code Analysis in MVP](../adr/ADR-003-no-code-analysis-in-mvp.md)
**Decision:** No static analysis, code quality metrics, or embeddings in MVP  
**Rationale:** Focus on activity reporting, not code quality  
**Impact:** No code scanning, no vector databases, no complexity analysis

### [ADR-004: Signals Over Surveillance](../adr/ADR-004-signals-over-surveillance.md)
**Decision:** Never rank, score, or monitor individual developers  
**Rationale:** Build trust, respect privacy, focus on work not people  
**Impact:** No productivity metrics, no developer rankings, no surveillance features

### [ADR-005: AI Generates Summaries, Not Facts](../adr/ADR-005-ai-generates-summaries-not-facts.md)
**Decision:** LLMs interpret existing data, don't create new facts  
**Rationale:** Maintain trust and accuracy  
**Impact:** AI only generates human-readable summaries from structured data

### [ADR-006: Daily Report First](../adr/ADR-006-daily-report-first.md)
**Decision:** Start with daily reports before weekly/monthly  
**Rationale:** Simplest cadence, fastest validation  
**Impact:** No weekly or monthly aggregation in MVP

### [ADR-007: Human Readability Over Analytics](../adr/ADR-007-human-readability-over-analytics.md)
**Decision:** Written reports are primary output, not dashboards  
**Rationale:** Reports get read, dashboards get ignored  
**Impact:** No interactive dashboards, charts, or visualizations in MVP

### [ADR-008: Single-Tenant, Internal-First](../adr/ADR-008-single-tenant-internal-first.md)
**Decision:** Build for one organization (your own) before multi-tenancy  
**Rationale:** Simpler architecture, real validation, faster MVP  
**Impact:** No multi-tenant features, organization management, or billing

---

## Technical Decisions

### [ADR-009: FastAPI Backend](../adr/ADR-009-fastapi-backend.md)
**Decision:** Use FastAPI as backend framework  
**Rationale:** Modern Python, async support, automatic API docs  
**Impact:** Python 3.11+, async/await patterns, Pydantic validation

### [ADR-010: PostgreSQL as System of Record](../adr/ADR-010-postgresql-system-of-record.md)
**Decision:** PostgreSQL is the single source of truth  
**Rationale:** Reliable, mature, excellent for structured data  
**Impact:** All data stored in PostgreSQL, no external caches or stores in MVP

### [ADR-011: Scheduled Data Collection](../adr/ADR-011-scheduled-data-collection.md)
**Decision:** Poll Gitea API on schedule, don't use webhooks  
**Rationale:** Simpler architecture, no Gitea configuration needed  
**Impact:** Daily batch collection, not real-time updates

---

## Decision Matrix

| ADR | Category | Status | Impact Level |
|-----|----------|--------|--------------|
| ADR-001 | Data Sources | Accepted | High |
| ADR-002 | Product | Accepted | High |
| ADR-003 | Scope | Accepted | High |
| ADR-004 | Ethics | Accepted | Critical |
| ADR-005 | AI/LLM | Accepted | High |
| ADR-006 | Product | Accepted | Medium |
| ADR-007 | Product | Accepted | High |
| ADR-008 | Architecture | Accepted | High |
| ADR-009 | Technology | Accepted | Medium |
| ADR-010 | Technology | Accepted | Medium |
| ADR-011 | Architecture | Accepted | Medium |

---

## Decision Categories

### Product Decisions
- **ADR-002:** Business language in reports
- **ADR-004:** Signals over surveillance
- **ADR-006:** Daily reports first
- **ADR-007:** Reports over dashboards

### Scope Decisions
- **ADR-001:** Commits only (no PRs, Jira, etc.)
- **ADR-003:** No code analysis
- **ADR-008:** Single-tenant first

### Technical Decisions
- **ADR-009:** FastAPI backend
- **ADR-010:** PostgreSQL database
- **ADR-011:** Scheduled collection

### AI/LLM Decisions
- **ADR-005:** AI for summaries only

---

## Key Principles Reflected in ADRs

### 1. Business First
- ADR-002: Business language
- ADR-007: Human-readable reports

### 2. Signals Over Surveillance
- ADR-004: No developer monitoring

### 3. Incremental Intelligence
- ADR-001: Commits only
- ADR-003: No code analysis
- ADR-006: Daily reports first
- ADR-008: Single-tenant first
- ADR-011: Scheduled collection

### 4. Trust Is Mandatory
- ADR-004: Respect privacy
- ADR-005: AI transparency

### 5. Actionability Over Information
- ADR-007: Reports over dashboards

---

## Common Patterns

### Simplicity Over Sophistication
Multiple ADRs choose simpler approaches:
- Commits only (not multi-source)
- Reports only (not dashboards)
- Single-tenant (not multi-tenant)
- Scheduled collection (not webhooks)
- No code analysis (not full intelligence)

**Rationale:** Validate core value before adding complexity

### Incremental Approach
Every ADR includes "Revisit Conditions" for when to reconsider:
- After MVP validation
- When user needs emerge
- When proven necessary

**Rationale:** Build what's needed, not what might be needed

### User-Centric
Decisions prioritize user needs:
- Business language for managers
- 60-second readable reports
- No surveillance features
- Transparent AI summaries

**Rationale:** Solve real problems for real users

---

## Decision Dependencies

```
ADR-001 (Commits Only)
  ↓
ADR-011 (Scheduled Collection)
  ↓
ADR-006 (Daily Reports)
  ↓
ADR-007 (Reports Over Dashboards)
  ↓
ADR-002 (Business Language)
  ↓
ADR-005 (AI Summaries)

ADR-008 (Single-Tenant)
  ↓
ADR-009 (FastAPI)
  ↓
ADR-010 (PostgreSQL)
```

---

## What We're NOT Building (MVP)

Based on ADR decisions:

**Data Sources:**
- ❌ Pull requests
- ❌ Jira/tickets
- ❌ Deployments
- ❌ CI/CD
- ❌ Monitoring/incidents

**Features:**
- ❌ Code analysis
- ❌ Static analysis
- ❌ Code quality metrics
- ❌ Developer rankings
- ❌ Productivity scores
- ❌ Interactive dashboards
- ❌ Real-time updates
- ❌ Weekly/monthly reports

**Infrastructure:**
- ❌ Multi-tenancy
- ❌ Organization management
- ❌ Billing system
- ❌ Webhooks
- ❌ Real-time collection

---

## What We ARE Building (MVP)

Based on ADR decisions:

**Data Collection:**
- ✅ Git commits from Gitea
- ✅ Scheduled daily collection
- ✅ Commit metadata storage

**Report Generation:**
- ✅ Daily business-readable reports
- ✅ AI-generated summaries
- ✅ Executive summary
- ✅ Project summaries
- ✅ Contributor summaries
- ✅ Management notes

**Technical Stack:**
- ✅ FastAPI backend
- ✅ PostgreSQL database
- ✅ Single-tenant deployment
- ✅ Async/await patterns

---

## Using This Reference

### For Developers
When implementing features:
1. Check relevant ADRs
2. Follow established patterns
3. Don't build excluded features
4. Maintain consistency with decisions

### For Product Decisions
When considering new features:
1. Check if ADR exists
2. Understand rationale
3. Consider if revisit conditions are met
4. Create new ADR if needed

### For Architecture Changes
When proposing changes:
1. Review related ADRs
2. Understand consequences
3. Document new decision
4. Update this reference

---

## Creating New ADRs

Use the [ADR Template](../adr/ADR-000-Template.md):

1. Copy template to new file: `ADR-XXX-title.md`
2. Fill in all sections
3. Consider alternatives
4. Document consequences
5. Define revisit conditions
6. Update this reference document

---

## ADR Lifecycle

### Proposed
New ADR under discussion

### Accepted
Decision made and implemented

### Deprecated
Superseded by newer ADR

### Superseded
Replaced by specific ADR

---

## Questions?

- **Understanding a decision:** Read the full ADR document
- **Proposing changes:** Create new ADR or propose revisiting existing one
- **Implementation questions:** Check ADR "Implementation Guidelines" section
- **Conflicts between ADRs:** Raise for team discussion

---

## Related Documentation

- [Product Vision](../product/vision.md)
- [Product Principles](../product/principles.md)
- [System Architecture](system-overview.md)
- [Requirements](../product/requirements.md)
- [MVP Specification](../product/mvp/MVP-v1.md)

---

**Last Updated:** 2026-06-17

**Total ADRs:** 11 (ADR-001 through ADR-011)