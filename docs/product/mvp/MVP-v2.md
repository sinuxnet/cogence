# MVP-v2: Fixes and Enhancements

**Status:** Done  
**Target:** Post MVP-v1 Pilot  
**Focus:** Address MVP-v1 feedback, improve report quality, add essential features

---

## Overview

MVP-v2 focuses on fixing issues discovered during MVP-v1 pilot testing and adding simple but critical features to improve report quality and system reliability. This is primarily a refinement release, not a feature expansion.

**Key Principle:** Fix what's broken, enhance what works, prepare for MVP-v3.

---

## Goals

1. **Improve Report Quality** - Remove optimistic language, add hierarchical structure
2. **Better Error Handling** - Informative errors in delivery script
3. **Repository Filtering** - Only track organizational repositories
4. **Structured Logging** - Better observability for debugging
5. **API Evolution** - Prepare for proper resource modeling

---

## MVP-v1 Feedback Summary

### Critical Issues (Must Fix)

1. **Report Language Problems**
   - AI uses optimistic/endorsement language ("significant progress", "strong collaboration")
   - Gives managers false hope with phrases like "will improve user experience"
   - Should be purely factual, neutral assistant to managers

2. **Report Structure Problems**
   - Flat structure, no organization grouping
   - Uses "commits" instead of "updates" in user-facing text
   - Includes "management_notes" section (not needed yet)
   - Doesn't show contributor count upfront

3. **Error Handling in deliver.sh**
   - Silent failures, no distinction between error types
   - Can't diagnose network vs API vs authentication errors

### Important Issues (Should Fix)

4. **Repository Filtering**
   - Fetches all visible repos (personal, public, other orgs)
   - Need to filter by organization configuration

5. **Logging**
   - Need structured logging for report generation process
   - Hard to debug issues without detailed logs

### Future Considerations (MVP-v3+)

6. **API Design** - Better resource modeling, proper REST
7. **Versioning** - Semantic versioning, Git tags, changelog

---

## Product Slices

### Slice 1: Fix Report Language (Critical)

**Goal:** Remove all optimistic/endorsement language from AI-generated reports.

**Changes:**
- Update AI prompts to be purely factual
- Remove phrases like "significant progress", "strong collaboration"
- No assumptions about code quality or impact
- Neutral tone - describe what happened, not how good it is

**Files to Update:**
- `app/services/ai.py` - Update all prompt templates
- `docs/ai/report-generation.md` - Update prompt specifications
- Add forbidden phrases list
- Add required neutral language examples

**Acceptance Criteria:**
- [ ] No optimistic language in any generated report
- [ ] No endorsements or blame in contributor summaries
- [ ] No assumptions about code quality
- [ ] Reports describe facts only, no interpretation

**Estimated Effort:** 4 hours

---

### Slice 2: Restructure Report Output (Critical)

**Goal:** Implement hierarchical organization → repository → updates structure.

**New Structure:**
```
## General Report
- X organizations/projects updated
- Y contributors detected  
- Z total updates

## Projects
### Organization/Project 1
#### Repository A (10 updates)
- Factual description
#### Repository B (15 updates)
- Factual description

### Organization/Project 2
...

## Contributors
### Abbas
- Worked on Project X
- Refactored authentication

### Setareh  
- Worked on frontend
- Added validation for user phone number
```

**Changes:**
- Add organization grouping to data model
- Update report generation to group by organization
- Use "updates" instead of "commits" in user-facing text
- Remove "management_notes" section
- Add contributor count to general report
- Show update counts per repository

**Files to Update:**
- `app/models/orm.py` - Add organization concept
- `app/services/aggregator.py` - Group by organization
- `app/services/report.py` - New report structure
- `scripts/deliver.sh` - Update message formatting
- `docs/examples/sample-report.json` - Update example

**Acceptance Criteria:**
- [ ] Reports grouped by organization → repository
- [ ] Uses "updates" not "commits" in user text
- [ ] Shows contributor count at top
- [ ] Shows update count per repository
- [ ] No "management_notes" section

**Estimated Effort:** 8 hours

---

### Slice 3: Improve Error Handling in deliver.sh (High Priority)

**Goal:** Provide specific, actionable error messages for different failure types.

**Error Types to Handle:**
1. Network errors (wrong URL, timeout, DNS failure)
2. HTTP 401 (unauthorized - wrong API key)
3. HTTP 404 (report not found - no data for date)
4. HTTP 500 (server error)
5. Empty response
6. Rocket.Chat webhook failure

**Changes:**
```bash
# Check HTTP status code
# Provide specific error message per status
# Log errors with context
# Exit with appropriate code
```

**Files to Update:**
- `scripts/deliver.sh` - Add error handling logic

**Acceptance Criteria:**
- [ ] Network errors show URL and suggest checking connectivity
- [ ] 401 errors suggest checking COGENCE_API_KEY
- [ ] 404 errors suggest checking date or running collection
- [ ] 500 errors suggest checking server logs
- [ ] Empty responses detected and reported
- [ ] Rocket.Chat failures detected and reported
- [ ] All errors include timestamp and context

**Estimated Effort:** 3 hours

---

### Slice 4: Repository Filtering by Organization (High Priority)

**Goal:** Only track repositories from specified organizations, ignore personal/public repos.

**Configuration:**
```bash
# .env
GITEA_ORGANIZATIONS=acme,widgets,internal
GITEA_INCLUDE_PERSONAL=false
```

**Changes:**
- Add organization filter to Gitea service
- Only fetch repos from specified organizations
- Skip user-owned repositories
- Add configuration validation

**Files to Update:**
- `app/core/config.py` - Add new settings
- `app/services/gitea.py` - Add filtering logic
- `.env.example` - Document new variables
- `docs/development/setup.md` - Update setup guide

**Acceptance Criteria:**
- [ ] Only repos from GITEA_ORGANIZATIONS are tracked
- [ ] Personal repos excluded when GITEA_INCLUDE_PERSONAL=false
- [ ] Configuration validated on startup
- [ ] Clear error if no organizations configured
- [ ] Logs show which repos are filtered out

**Estimated Effort:** 4 hours

---

### Slice 5: Structured Logging (Medium Priority)

**Goal:** Add structured JSON logging for report generation process.

**Log Events:**
- Report generation started/completed
- LLM calls (section, model, tokens, duration)
- LLM failures with fallback
- Repository filtering results
- Commit collection results
- API requests/responses

**Format:**
```json
{
  "timestamp": "2024-01-15T21:00:00+03:30",
  "level": "INFO",
  "event": "report_generation_started",
  "date": "2024-01-15",
  "repositories_count": 3,
  "commits_count": 15
}
```

**Files to Update:**
- `app/core/config.py` - Add logging configuration
- `app/services/report.py` - Add structured logs
- `app/services/ai.py` - Add LLM call logs
- `app/services/gitea.py` - Add collection logs
- `app/collector.py` - Add collection logs
- Create `app/core/logging.py` - Logging utilities

**Acceptance Criteria:**
- [ ] All major operations logged with structured data
- [ ] Logs include context (date, repo, contributor)
- [ ] Errors include stack traces and context
- [ ] Logs are JSON formatted
- [ ] Log level configurable via environment
- [ ] Logs written to file and stdout

**Estimated Effort:** 6 hours

---

### Slice 6: API Versioning Strategy (Low Priority)

**Goal:** Document API versioning approach for future evolution.

**Strategy:**
- Semantic versioning for API (v1.0.0, v1.1.0, v2.0.0)
- URL versioning (/api/v1/, /api/v2/)
- Deprecation policy (6 months notice)
- Changelog maintenance

**Files to Create:**
- `docs/api/versioning.md` - Versioning strategy
- `docs/api/changelog.md` - API changelog
- `CHANGELOG.md` - Product changelog

**Files to Update:**
- `app/main.py` - Add version endpoint
- `docs/api/README.md` - Document versioning

**Acceptance Criteria:**
- [ ] Versioning strategy documented
- [ ] Changelog template created
- [ ] Version endpoint returns current version
- [ ] Deprecation policy defined

**Estimated Effort:** 2 hours

---

## Implementation Order

1. **Slice 1: Fix Report Language** (Critical, 4h)
2. **Slice 2: Restructure Report Output** (Critical, 8h)
3. **Slice 3: Improve Error Handling** (High, 3h)
4. **Slice 4: Repository Filtering** (High, 4h)
5. **Slice 5: Structured Logging** (Medium, 6h)
6. **Slice 6: API Versioning Strategy** (Low, 2h)

**Total Estimated Effort:** 27 hours (~3-4 days)

---

## Success Criteria

### Report Quality
- [ ] No optimistic/endorsement language in reports
- [ ] Hierarchical organization → repository structure
- [ ] Uses "updates" not "commits" in user-facing text
- [ ] Contributor count shown at top
- [ ] Purely factual, neutral tone

### Reliability
- [ ] Specific error messages for all failure types
- [ ] Only organizational repositories tracked
- [ ] Structured logs for debugging
- [ ] No silent failures

### Maintainability
- [ ] Clear versioning strategy
- [ ] Comprehensive logging
- [ ] Configuration validation
- [ ] Updated documentation

---

## Non-Goals (Deferred to MVP-v3+)

- ❌ Jira integration
- ❌ Code analysis beyond commits
- ❌ Weekly/monthly reports
- ❌ Multi-tenancy
- ❌ Dashboard UI
- ❌ Advanced analytics
- ❌ Custom report templates
- ❌ Email delivery
- ❌ Slack integration

---

## Testing Strategy

### Unit Tests
- AI prompt output validation (no forbidden phrases)
- Report structure validation
- Error handling logic
- Repository filtering logic
- Logging output validation

### Integration Tests
- End-to-end report generation
- Error scenarios (network, auth, not found)
- Organization filtering
- Log output verification

### Manual Testing
- Generate reports with new structure
- Test all error scenarios in deliver.sh
- Verify repository filtering
- Review logs for completeness

---

## Deployment Plan

1. **Deploy to staging**
2. **Run full test suite**
3. **Generate sample reports, review quality**
4. **Test error scenarios**
5. **Review logs**
6. **Deploy to production**
7. **Monitor first 3 days of reports**
8. **Collect feedback**

---

## Documentation Updates

- [ ] Update `docs/ai/report-generation.md` with new prompts
- [ ] Update `docs/examples/sample-report.json` with new structure
- [ ] Update `docs/development/setup.md` with new env vars
- [ ] Create `docs/api/versioning.md`
- [ ] Create `docs/engineering/logging.md`
- [ ] Update `README.md` with MVP-v2 status

---

## Migration Notes

### Breaking Changes
- Report structure changed (organization grouping)
- "commits" → "updates" in user-facing text
- "management_notes" removed from API response

### Backward Compatibility
- API version remains v1 (structure change is enhancement)
- Old deliver.sh will still work (fields are additive)
- Database schema unchanged

### Configuration Changes
- New required: `GITEA_ORGANIZATIONS`
- New optional: `GITEA_INCLUDE_PERSONAL`
- New optional: `LOG_LEVEL`, `LOG_FILE`

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI prompt changes break reports | High | Extensive testing, gradual rollout |
| Structure change breaks deliver.sh | Medium | Test with old/new scripts |
| Repository filtering too restrictive | Medium | Make configuration flexible |
| Logging performance impact | Low | Async logging, configurable level |

---

## Post-MVP-v2 Retrospective Questions

1. Are reports now purely factual and neutral?
2. Is the hierarchical structure clearer for managers?
3. Are error messages helpful for debugging?
4. Is repository filtering working as expected?
5. Are logs providing enough debugging information?
6. What feedback did we get from managers?
7. What should we prioritize for MVP-v3?

---

**Last Updated:** 2026-06-24  
**Status:** Done  
**Next Review:** MVP-v3 planning