# Cogence Acceptance Criteria

## Overview

This document defines the acceptance criteria for Cogence MVP v1 features. Each criterion must be met for the feature to be considered complete and ready for release.

**Definition of Done:** A feature is complete when all acceptance criteria are met, tests pass, documentation is updated, and code is reviewed.

---

## Feature: Data Collection from Gitea

### AC-1.1: Connect to Gitea Instance

**Given** a valid Gitea URL and API token  
**When** the system starts  
**Then** it successfully connects to Gitea  
**And** validates the connection  
**And** logs connection status

**Verification:**
- [ ] Connection succeeds with valid credentials
- [ ] Connection fails gracefully with invalid credentials
- [ ] Error messages are clear and actionable
- [ ] Connection status is logged

---

### AC-1.2: Discover Repositories

**Given** a successful Gitea connection  
**When** repository discovery runs  
**Then** all accessible repositories are found  
**And** repository metadata is stored  
**And** repository count is logged

**Verification:**
- [ ] All accessible repositories are discovered
- [ ] Repository metadata includes: name, URL, description
- [ ] Inaccessible repositories are skipped gracefully
- [ ] Discovery completes within 2 minutes for 100 repositories

---

### AC-1.3: Fetch Commit Metadata

**Given** a list of repositories  
**When** commit collection runs  
**Then** commits from the last 24 hours are fetched  
**And** commit metadata is complete  
**And** no duplicate commits are stored

**Verification:**
- [ ] Commits include: SHA, author, timestamp, message, stats
- [ ] Only commits from last 24 hours are collected
- [ ] Duplicate commits are detected and skipped
- [ ] Collection completes within 5 minutes for 10,000 commits

---

### AC-1.4: Handle API Rate Limiting

**Given** Gitea API rate limits  
**When** rate limit is reached  
**Then** system waits appropriately  
**And** retries the request  
**And** logs rate limit events

**Verification:**
- [ ] Rate limit detection works correctly
- [ ] System waits before retrying
- [ ] Exponential backoff is implemented
- [ ] Rate limit events are logged

---

### AC-1.5: Retry Failed Requests

**Given** a failed API request  
**When** the failure is transient  
**Then** system retries with exponential backoff  
**And** succeeds on retry  
**Or** logs permanent failure after max retries

**Verification:**
- [ ] Transient failures trigger retry
- [ ] Exponential backoff is used (1s, 2s, 4s)
- [ ] Max 3 retries before giving up
- [ ] Permanent failures are logged with context

---

## Feature: Data Storage

### AC-2.1: Store Repository Metadata

**Given** repository data from Gitea  
**When** storing in database  
**Then** all required fields are saved  
**And** referential integrity is maintained  
**And** duplicates are handled correctly

**Verification:**
- [ ] All repository fields are stored
- [ ] Gitea ID is unique constraint
- [ ] Updates work for existing repositories
- [ ] Foreign key constraints are enforced

---

### AC-2.2: Store Commit Metadata

**Given** commit data from Gitea  
**When** storing in database  
**Then** all required fields are saved  
**And** commit SHA is unique  
**And** repository relationship is maintained

**Verification:**
- [ ] All commit fields are stored
- [ ] SHA is unique constraint
- [ ] Repository foreign key is valid
- [ ] Timestamps are stored in UTC
- [ ] Duplicate SHAs are rejected

---

### AC-2.3: Query Commits by Date Range

**Given** commits in database  
**When** querying by date range  
**Then** only commits in range are returned  
**And** results are ordered by timestamp  
**And** query completes quickly

**Verification:**
- [ ] Date range filtering works correctly
- [ ] Results are ordered by timestamp DESC
- [ ] Query uses index (< 100ms for 10k commits)
- [ ] Edge cases handled (empty range, future dates)

---

## Feature: Daily Report Generation

### AC-3.1: Generate Executive Summary

**Given** commits from last 24 hours  
**When** generating executive summary  
**Then** summary is 2-4 sentences  
**And** uses business language  
**And** highlights key accomplishments  
**And** is readable in under 15 seconds

**Verification:**
- [ ] Summary length is 2-4 sentences
- [ ] No technical jargon present
- [ ] Key accomplishments are mentioned
- [ ] Reading time < 15 seconds
- [ ] Summary is factually accurate

---

### AC-3.2: Generate Project Summaries

**Given** commits grouped by repository  
**When** generating project summaries  
**Then** each repository has a summary  
**And** summaries use business language  
**And** commit counts are accurate

**Verification:**
- [ ] All active repositories are included
- [ ] Each summary is one sentence
- [ ] No technical jargon present
- [ ] Commit counts match actual commits
- [ ] Summaries describe business value

---

### AC-3.3: Generate Contributor Summaries

**Given** commits grouped by author  
**When** generating contributor summaries  
**Then** each contributor has a summary  
**And** summaries are respectful  
**And** no ranking or scoring is present

**Verification:**
- [ ] All contributors are included
- [ ] Each summary is one sentence
- [ ] No ranking language present
- [ ] No productivity metrics mentioned
- [ ] No comparisons between contributors
- [ ] Summaries are neutral and respectful

---

### AC-3.4: Generate Management Notes

**Given** overall commit activity  
**When** generating management notes  
**Then** notes highlight important observations  
**And** identify potential concerns  
**And** provide actionable recommendations

**Verification:**
- [ ] Notes are 2-3 sentences
- [ ] Important patterns are highlighted
- [ ] Concerns are identified (if any)
- [ ] Recommendations are actionable
- [ ] Language is constructive

---

### AC-3.5: Complete Report in Under 30 Seconds

**Given** commits from last 24 hours  
**When** generating complete report  
**Then** generation completes in under 30 seconds  
**And** all sections are present  
**And** report is stored in database

**Verification:**
- [ ] Total generation time < 30 seconds
- [ ] Executive summary is present
- [ ] Projects summary is present
- [ ] Contributors summary is present
- [ ] Management notes are present
- [ ] Report is saved to database

---

## Feature: Report Delivery

### AC-4.1: Retrieve Daily Report by Date

**Given** a generated report for a date  
**When** requesting report via API  
**Then** report is returned in JSON format  
**And** response time is under 2 seconds  
**And** all sections are included

**Verification:**
- [ ] GET /api/v1/reports/daily/{date} works
- [ ] Response is valid JSON
- [ ] Response time < 2 seconds
- [ ] All report sections are present
- [ ] 404 returned for missing reports

---

### AC-4.2: Retrieve Latest Report

**Given** multiple generated reports  
**When** requesting latest report  
**Then** most recent report is returned  
**And** response time is under 2 seconds

**Verification:**
- [ ] GET /api/v1/reports/daily/latest works
- [ ] Returns most recent report by date
- [ ] Response time < 2 seconds
- [ ] 404 returned if no reports exist

---

### AC-4.3: Report Readable in Under 60 Seconds

**Given** a generated daily report  
**When** a manager reads the report  
**Then** they can understand key information in under 60 seconds  
**And** no technical knowledge is required

**Verification:**
- [ ] Executive summary readable in 15 seconds
- [ ] Projects section scannable in 30 seconds
- [ ] Contributors section scannable in 15 seconds
- [ ] Total reading time < 60 seconds
- [ ] No technical jargon present

---

## Feature: System Configuration

### AC-5.1: Configure via Environment Variables

**Given** environment variables are set  
**When** system starts  
**Then** configuration is loaded  
**And** validated  
**And** errors are reported clearly

**Verification:**
- [ ] GITEA_URL is required
- [ ] GITEA_TOKEN is required
- [ ] DATABASE_URL is required
- [ ] Invalid config prevents startup
- [ ] Error messages are clear

---

### AC-5.2: Validate Configuration on Startup

**Given** system configuration  
**When** system starts  
**Then** all required settings are validated  
**And** external services are checked  
**And** startup fails if invalid

**Verification:**
- [ ] Gitea connection is tested
- [ ] Database connection is tested
- [ ] LLM API is tested (if configured)
- [ ] Invalid config prevents startup
- [ ] Validation errors are logged

---

## Feature: Scheduled Data Collection

### AC-6.1: Run Collection on Schedule

**Given** a configured schedule  
**When** scheduled time arrives  
**Then** data collection runs automatically  
**And** completes successfully  
**And** logs execution status

**Verification:**
- [ ] Collection runs at scheduled time
- [ ] Collection completes successfully
- [ ] Execution is logged
- [ ] Failures trigger alerts
- [ ] Schedule is configurable

---

### AC-6.2: Avoid Duplicate Collection

**Given** commits already collected  
**When** collection runs again  
**Then** duplicate commits are skipped  
**And** only new commits are stored  
**And** no errors occur

**Verification:**
- [ ] Duplicate detection works correctly
- [ ] Duplicates are skipped silently
- [ ] New commits are stored
- [ ] No database errors occur
- [ ] Performance is acceptable

---

## Feature: Error Handling

### AC-7.1: Handle Gitea API Failures

**Given** Gitea API is unavailable  
**When** collection runs  
**Then** error is logged  
**And** system retries later  
**And** operators are alerted

**Verification:**
- [ ] API failures are detected
- [ ] Errors are logged with context
- [ ] Retry is scheduled
- [ ] Alerts are sent (if configured)
- [ ] System remains stable

---

### AC-7.2: Handle LLM API Failures

**Given** LLM API is unavailable  
**When** report generation runs  
**Then** fallback summary is used  
**And** error is logged  
**And** report is still generated

**Verification:**
- [ ] LLM failures are detected
- [ ] Fallback template is used
- [ ] Error is logged
- [ ] Report is generated (basic version)
- [ ] System remains stable

---

### AC-7.3: Handle Database Failures

**Given** database is unavailable  
**When** operations are attempted  
**Then** errors are logged  
**And** operations are retried  
**And** system degrades gracefully

**Verification:**
- [ ] Database failures are detected
- [ ] Errors are logged with context
- [ ] Retry logic is triggered
- [ ] Read-only mode if possible
- [ ] System remains stable

---

## Feature: API Health Checks

### AC-8.1: Basic Health Check

**Given** system is running  
**When** health check endpoint is called  
**Then** 200 OK is returned  
**And** response includes status

**Verification:**
- [ ] GET /health returns 200
- [ ] Response includes "status": "healthy"
- [ ] Response time < 100ms
- [ ] No authentication required

---

### AC-8.2: Readiness Check

**Given** system is running  
**When** readiness check is called  
**Then** all dependencies are checked  
**And** status reflects actual state  
**And** 503 returned if not ready

**Verification:**
- [ ] GET /health/ready checks database
- [ ] Checks Gitea connectivity
- [ ] Checks LLM availability
- [ ] Returns 200 if ready, 503 if not
- [ ] Response includes check details

---

## Feature: Security

### AC-9.1: Secure API Endpoints

**Given** API endpoints  
**When** requests are made  
**Then** authentication is required  
**And** unauthorized requests are rejected  
**And** rate limiting is enforced

**Verification:**
- [ ] Bearer token authentication works
- [ ] Unauthorized requests return 401
- [ ] Invalid tokens return 401
- [ ] Rate limiting is enforced
- [ ] Rate limit headers are present

---

### AC-9.2: Protect Sensitive Data

**Given** sensitive data (tokens, credentials)  
**When** stored or transmitted  
**Then** data is encrypted  
**And** access is logged  
**And** data is never exposed in logs

**Verification:**
- [ ] Gitea tokens are encrypted at rest
- [ ] Database connections use SSL/TLS
- [ ] API uses HTTPS in production
- [ ] Tokens not logged
- [ ] Access is audited

---

## Feature: Performance

### AC-10.1: API Response Time

**Given** API requests  
**When** under normal load  
**Then** 95th percentile response time is under 2 seconds  
**And** system handles 10 concurrent requests

**Verification:**
- [ ] P95 response time < 2 seconds
- [ ] P99 response time < 5 seconds
- [ ] 10 concurrent requests handled
- [ ] No timeouts under normal load
- [ ] Performance is monitored

---

### AC-10.2: Report Generation Performance

**Given** 10,000 commits  
**When** generating daily report  
**Then** generation completes in under 30 seconds  
**And** system remains responsive

**Verification:**
- [ ] Generation time < 30 seconds
- [ ] API remains responsive during generation
- [ ] Memory usage is acceptable
- [ ] CPU usage is acceptable
- [ ] Performance is consistent

---

## Feature: Data Quality

### AC-11.1: Accurate Commit Data

**Given** commits from Gitea  
**When** stored in database  
**Then** all data is accurate  
**And** no data is lost  
**And** timestamps are correct

**Verification:**
- [ ] Commit SHAs match Gitea
- [ ] Author information is correct
- [ ] Timestamps are in UTC
- [ ] Message content is complete
- [ ] Statistics are accurate

---

### AC-11.2: Accurate Report Data

**Given** commits in database  
**When** report is generated  
**Then** all counts are accurate  
**And** summaries reflect actual commits  
**And** no data is invented

**Verification:**
- [ ] Commit counts match database
- [ ] Repository counts are correct
- [ ] Contributor counts are correct
- [ ] Summaries based on actual commits
- [ ] No hallucinated data

---

## MVP v1 Release Criteria

### Must Have (Blocking)

All of the following must be met for MVP v1 release:

- [x] AC-1.1 through AC-1.5: Data Collection
- [x] AC-2.1 through AC-2.3: Data Storage
- [x] AC-3.1 through AC-3.5: Report Generation
- [x] AC-4.1 through AC-4.3: Report Delivery
- [x] AC-5.1 through AC-5.2: Configuration
- [x] AC-6.1 through AC-6.2: Scheduled Collection
- [x] AC-7.1 through AC-7.3: Error Handling
- [x] AC-8.1 through AC-8.2: Health Checks
- [x] AC-10.1 through AC-10.2: Performance
- [x] AC-11.1 through AC-11.2: Data Quality

### Should Have (Important)

- [x] AC-9.1 through AC-9.2: Security

### Could Have (Nice to Have)

- [ ] Email delivery
- [ ] Slack integration
- [ ] Custom report templates
- [ ] Weekly reports

---

## Testing Requirements

### Unit Tests

- [ ] 80%+ code coverage
- [ ] All business logic tested
- [ ] Edge cases covered
- [ ] Mocks for external services

### Integration Tests

- [ ] Database operations tested
- [ ] API endpoints tested
- [ ] End-to-end flows tested
- [ ] Error scenarios tested

### Performance Tests

- [ ] Load testing completed
- [ ] Response times validated
- [ ] Concurrent request handling tested
- [ ] Resource usage acceptable

### User Acceptance Testing

- [ ] Managers can read reports in < 60 seconds
- [ ] Reports use business language
- [ ] Reports are actionable
- [ ] System is reliable

---

## Documentation Requirements

- [ ] API documentation complete
- [ ] Setup guide complete
- [ ] User guide complete
- [ ] Architecture documentation complete
- [ ] ADRs documented
- [ ] Code is commented

---

## Related Documentation

- [Product Requirements](requirements.md)
- [User Stories](user-stories.md)
- [System Architecture](../architecture/system-overview.md)
- [API Documentation](../api/README.md)
- [Testing Strategy](../testing/strategy.md)

---

**Last Updated:** 2026-06-17

**Version:** 1.0.0