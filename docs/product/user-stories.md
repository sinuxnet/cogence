# Cogence User Stories — Pilot (MVP v1)

## Overview

This document contains **pilot-only** user stories for MVP v1. Stories marked **Pilot** are in scope for the first release.

Deferred and future stories live in [backlog.md](backlog.md).

Format:

```
As a [persona],
I want [goal],
So that [benefit].
```

**Pilot constraints:**

- No dashboard — reports via API or Rocket.Chat
- Daily delivery at **21:00 Asia/Tehran**
- No commit-count rankings or activity sorting
- Reports encourage atomic commits with clear messages

---

## Pilot Stories

### Story P1: Daily Engineering Summary

**Status:** Pilot

**As a CEO,**  
I want a daily summary of engineering activity,  
So I can understand what the team accomplished without attending technical meetings.

**Acceptance Criteria:**

- Summary is readable in under 60 seconds
- Uses business language, not technical jargon
- Highlights key accomplishments
- Delivered by API and Rocket.Chat at 21:00 Asia/Tehran

---

### Story P2: Strategic Progress Visibility

**Status:** Pilot

**As a Founder,**  
I want to see which repositories received engineering attention,  
So I can verify alignment with strategic priorities.

**Acceptance Criteria:**

- Lists all active repositories for the report day
- Provides a brief business-language summary per repository
- Identifies focus areas without volume rankings

---

### Story P3: Quick Status Check

**Status:** Pilot

**As an Executive,**  
I want a report readable in under one minute,  
So I can stay informed without disrupting my schedule.

**Acceptance Criteria:**

- API response loads in under 2 seconds
- Key information is easy to scan
- Executive summary is concise (2–4 sentences)
- No technical knowledge required

---

### Story P4: Repository Activity Tracking

**Status:** Pilot

**As an Engineering Manager,**  
I want to know which repositories were active today,  
So I can track where engineering effort is focused.

**Acceptance Criteria:**

- Shows all repositories with commits for the report day
- Provides a brief description of work per repository
- Does not sort or rank repositories by commit volume

---

### Story P5: Team Activity Overview

**Status:** Pilot

**As an Engineering Manager,**  
I want to see what each team member worked on,  
So I can understand individual contributions without micromanaging.

**Acceptance Criteria:**

- Lists all contributors with activity for the report day
- Summarizes work areas in business terms
- Does NOT rank, score, or compare contributors
- Does NOT surface commit counts as a comparison signal

---

### Story P6: Historical Report Access

**Status:** Pilot

**As an Engineering Manager,**  
I want to access previous daily reports by date,  
So I can recall what happened on a specific day.

**Acceptance Criteria:**

- Can retrieve reports by date via API
- Reports retained for 90+ days
- Consistent JSON format across dates

---

### Story P7: Rocket.Chat Delivery

**Status:** Pilot

**As a Manager,**  
I want the daily report posted to Rocket.Chat,  
So I receive it in our existing communication channel without opening a dashboard.

**Acceptance Criteria:**

- Report posted automatically at 21:00 Asia/Tehran
- Message is readable in under 60 seconds
- Includes executive summary and key sections
- Failure is logged if delivery fails

---

### Story P8: Programmatic Access

**Status:** Pilot

**As a Developer,**  
I want to access reports via API,  
So I can integrate them into other tools if needed.

**Acceptance Criteria:**

- RESTful API available
- JSON format responses
- Authentication supported
- OpenAPI documentation available

---

### Story P9: System Health Monitoring

**Status:** Pilot

**As a DevOps Engineer,**  
I want to verify the report generation system is working,  
So I can ensure stakeholders receive timely information.

**Acceptance Criteria:**

- Health check endpoints available (`/health`, `/health/ready`)
- Collection and report generation status logged
- Errors include enough context for troubleshooting

---

## User Journey: Nightly Report (Primary Flow)

1. **21:00 Asia/Tehran — report is generated**
   - System collects commits for the calendar day
   - AI generates business-readable sections

2. **Report is delivered**
   - Posted to configured Rocket.Chat channel
   - Available via API (`/api/v1/reports/daily/latest`)

3. **Manager reads the report (under 60 seconds)**
   - Scans executive summary (~15 seconds)
   - Reviews active repositories (~30 seconds)
   - Checks contributor summary (~15 seconds)
   - Optionally reads management notes

No dashboard visit required.

---

## User Journey: API Access

1. Consumer calls `GET /api/v1/reports/daily/latest` or `GET /api/v1/reports/daily/{date}`
2. Parses JSON response
3. Uses report data in a custom integration (if needed)

---

## Story Mapping

| Priority | Stories |
|----------|---------|
| **Pilot (MVP v1)** | P1–P9 |
| **Backlog** | See [backlog.md](backlog.md) |

---

## Related Documentation

- [MVP v1 Specification](mvp/MVP-v1.md)
- [Product Slices](mvp/product-slices.md)
- [Backlog](backlog.md)
- [Product Requirements](requirements.md)
- [Acceptance Criteria](acceptance-criteria.md)

---

**Last Updated:** 2026-06-18

**Version:** 1.1.0 (Pilot scope)
