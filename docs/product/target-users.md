# Cogence Target Users

## Overview

Primary users for the MVP v1 pilot. Cogence serves **non-technical leaders** who need to understand engineering activity without reading code.

---

## Primary Users (Pilot)

### CEO / Founder

**Needs:**

- Daily understanding of what engineering accomplished
- Confidence that work aligns with business priorities
- Information in under 60 seconds

**Does not want:**

- Technical jargon
- Code or repository browsing
- Developer performance rankings

**Receives reports via:** Rocket.Chat and API (no dashboard in pilot)

---

### Engineering Manager

**Needs:**

- Which repositories were active
- What contributors worked on (areas, not volume)
- Light management observations

**Does not want:**

- Surveillance metrics
- Commit-count comparisons
- Micromanagement tooling

---

### Product Manager

**Needs:**

- Visibility into engineering progress for stakeholder communication
- Business-language summaries tied to repositories

**Does not want:**

- Deep technical implementation details

---

## Secondary Users (Pilot)

### DevOps / Platform Engineer

**Needs:**

- Health endpoints to verify nightly pipeline
- Logs for collection and report generation failures

**Role:** Operates the system, not primary report consumer.

---

### API Consumer (Developer / Tools Engineer)

**Needs:**

- Programmatic access to report JSON
- OpenAPI documentation

**Role:** Integrates Cogence into internal tooling if needed. Not required for pilot validation.

---

## Explicitly Not Target Users (Pilot)

| Persona | Reason |
|---------|--------|
| Individual contributors | Cogence is not a developer monitoring tool |
| HR / performance reviewers | No productivity scoring in pilot |
| External customers | Single-tenant internal deployment |

---

## User Assumptions

1. Users read reports in English
2. Users are in or aligned with `Asia/Tehran` timezone for nightly delivery
3. Users have access to the configured Rocket.Chat channel
4. Users trust reports when commit messages are clear (atomic commit culture)

---

## Related Documentation

- [MVP v1 Specification](mvp/MVP-v1.md)
- [Pilot User Stories](user-stories.md)
- [Product Principles](principles.md)

---

**Last Updated:** 2026-06-18
