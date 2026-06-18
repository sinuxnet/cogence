# Cogence Product Backlog

## Overview

Stories and capabilities **deferred from the MVP v1 pilot**. These are valid ideas but must not be implemented until pilot validation is complete — several risk drifting into surveillance or scope creep.

Pilot scope is defined in [user-stories.md](user-stories.md) and [mvp/MVP-v1.md](mvp/MVP-v1.md).

---

## Deferred User Stories

### Story B1: Risk Detection

**Was:** Story 6

**As an Engineering Manager,**  
I want to be alerted to unusual patterns or potential issues,  
So I can address problems before they escalate.

**Why deferred:** Management Notes covers light observations in the pilot. Dedicated risk detection needs calibration to avoid false alarms.

---

### Story B2: Data Collection Alerts

**Was:** Story 13

**As a System Administrator,**  
I want alerts when data collection fails,  
So I can troubleshoot before reports are affected.

**Why deferred:** Pilot relies on logs and health endpoints. Alerting integrations come after operational baseline is stable.

---

### Story B3: Feature Progress Tracking

**Was:** Story 8

**As a Product Manager,**  
I want to understand which features are being developed,  
So I can communicate progress to stakeholders.

**Why deferred:** Requires reliable commit-message conventions and grouping logic beyond repository-level summaries.

---

### Story B4: Cross-Team Coordination

**Was:** Story 9

**As a Product Manager,**  
I want to see which teams are working on related projects,  
So I can identify coordination opportunities.

**Why deferred:** Needs repository grouping and team mapping not defined in pilot.

---

### Story B5: Architecture Evolution

**Was:** Story 10

**As a CTO,**  
I want to understand which systems are receiving attention,  
So I can assess technical debt and architecture decisions.

**Why deferred:** Out of MVP scope per [MVP-v1.md](mvp/MVP-v1.md) non-goals.

---

### Story B6: Resource Allocation

**Was:** Story 11

**As a VP of Engineering,**  
I want to see how engineering effort is distributed,  
So I can optimize resource allocation.

**Why deferred:** Effort distribution and bottleneck analysis imply metrics that conflict with signals-over-surveillance principles in the pilot.

---

## Future Enhancements

### Story F1: Weekly Aggregation

**As an Executive,**  
I want a weekly summary of engineering activity,  
So I can understand trends without reading daily reports.

---

### Story F2: Email Delivery

**As a Manager,**  
I want reports delivered to my email,  
So I don't need to check Rocket.Chat or call the API.

---

### Story F3: Custom Filters

**As a Team Lead,**  
I want to filter reports by team or repository group,  
So I can focus on relevant information.

---

### Story F4: Trend Analysis

**As a CTO,**  
I want to see trends over time,  
So I can identify patterns and make strategic decisions.

---

### Story F5: Slack Integration

**As a Manager,**  
I want reports posted to Slack,  
So my team can discuss them in our existing workflow.

---

### Story F6: Web Dashboard

**As a Manager,**  
I want a web interface to browse reports,  
So I don't need to use Rocket.Chat or API tools.

**Note:** Explicitly excluded from pilot. API + Rocket.Chat are sufficient for validation.

---

### Story F7: Commit Quality Scoring

**As an Engineering Manager,**  
I want feedback on commit message quality,  
So the team improves report accuracy over time.

**Note:** Pilot encourages atomic commits culturally; formal scoring is post-validation.

---

## Deferred Technical Capabilities

| Capability | Notes |
|------------|-------|
| Interactive dashboards | ADR-007 — reports over dashboards |
| HTML report rendering | JSON + Rocket.Chat message for pilot |
| Repository include/exclude filters | Default: all accessible repos |
| Repository grouping (teams) | Needs product definition |
| Prometheus / Grafana | Operational hardening post-pilot |
| Token encryption at rest | Single-tenant pilot; env-based secrets first |
| Multi-channel delivery | Rocket.Chat only in pilot |

---

## Promotion Criteria

Move a backlog item into scope when:

1. Pilot success criteria are met (trust, accuracy, 60-second readability)
2. At least three managers used daily reports for two weeks
3. The item does not introduce surveillance patterns (rankings, scoring, comparisons)
4. Engineering cost is justified by explicit user demand

---

## Related Documentation

- [Pilot User Stories](user-stories.md)
- [MVP v1 Specification](mvp/MVP-v1.md)
- [Product Slices](mvp/product-slices.md)

---

**Last Updated:** 2026-06-18
