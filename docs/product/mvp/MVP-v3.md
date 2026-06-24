# MVP-v3: Enhanced Commit Intelligence + Jira Context

**Status:** Planning  
**Target:** Post MVP-v2  
**Focus:** Deeper commit analysis, optional Jira context enrichment

---

## Overview

MVP-v3 enhances Cogence's core strength (commit-based reporting) while adding optional Jira integration for additional context. **Commits and code remain the primary source of truth** - Jira is supplementary context only.

**Key Principle:** Better commit intelligence first, Jira context second.

---

## Vision

### Primary Goal: Better Commit-Based Reports

Improve the quality and depth of reports generated from Git commits and code changes:

1. **Commit Pattern Analysis** - Identify work patterns from commit history
2. **Code Change Context** - Better understanding of what changed and why
3. **Cross-Repository Insights** - Track work spanning multiple repos
4. **Technical Debt Signals** - Identify refactoring vs feature work
5. **Collaboration Patterns** - Understand team dynamics from commits

### Secondary Goal: Optional Jira Context

Add Jira as a **supplementary data source** to enrich reports with business context:

1. **Link commits to business initiatives** - What epic/story is this work for?
2. **Understand priority** - Is this urgent work or planned work?
3. **Track completion** - Are stories moving to done?
4. **Business language mapping** - Translate technical commits using story descriptions

**Important:** Jira is optional. Reports must work perfectly without Jira data.

---

## Guiding Principles

1. **Commits First, Always** - Git commits are the source of truth
2. **Jira is Context, Not Truth** - Jira enriches, doesn't replace commit data
3. **Work Without Jira** - All features must work without Jira integration
4. **No Jira Metrics** - Don't report on Jira velocity, story points, etc.
5. **Privacy Preserved** - No individual tracking, even with Jira data

---

## Product Slices

### Phase 1: Enhanced Commit Intelligence (Priority)

#### Slice 1.1: Commit Pattern Analysis

**Goal:** Identify patterns in commit behavior to provide better insights.

**Patterns to Detect:**
- **Refactoring work** - Commits with high churn, no feature additions
- **Bug fixes** - Commits with "fix", "bug", "issue" in messages
- **Feature work** - Commits with "feat", "add", "implement"
- **Documentation** - Commits touching only docs
- **Configuration** - Commits touching only config files
- **Testing** - Commits touching only test files

**Value:**
- Managers understand what type of work is happening
- Distinguish between feature development and maintenance
- Identify technical debt reduction efforts

**Implementation:**
```python
# Analyze commit messages and file patterns
def classify_commit(commit: Commit) -> CommitType:
    # Check message patterns
    # Check file patterns
    # Return: FEATURE, BUGFIX, REFACTOR, DOCS, CONFIG, TEST
```

**Acceptance Criteria:**
- [ ] Commits classified by type
- [ ] Report shows work distribution (40% features, 30% bugs, 20% refactor, 10% other)
- [ ] Classification accuracy > 80%

**Estimated Effort:** 8 hours

---

#### Slice 1.2: Code Change Context Analysis

**Goal:** Provide better context about what changed in code, not just commit messages.

**Analysis:**
- **File type distribution** - Backend vs frontend vs infrastructure
- **Change magnitude** - Small tweaks vs major rewrites
- **Change locality** - Focused changes vs scattered changes
- **Dependency updates** - Package.json, requirements.txt changes
- **Schema changes** - Database migrations detected

**Value:**
- Understand scope of changes beyond commit messages
- Identify risky changes (large, scattered)
- Detect infrastructure/dependency work

**Implementation:**
```python
# Analyze diff content and file patterns
def analyze_change_context(commit: Commit, diff: str) -> ChangeContext:
    # Analyze file types
    # Measure change magnitude
    # Detect special file types (migrations, configs)
    # Return structured context
```

**Acceptance Criteria:**
- [ ] Changes categorized by file type
- [ ] Change magnitude calculated
- [ ] Special changes detected (migrations, deps)
- [ ] Context included in report

**Estimated Effort:** 12 hours

---

#### Slice 1.3: Cross-Repository Work Tracking

**Goal:** Identify work that spans multiple repositories.

**Detection:**
- Same contributor, same time window, multiple repos
- Related commit messages across repos
- Coordinated changes (API + UI)

**Value:**
- Understand full scope of features
- Identify integration work
- See coordinated releases

**Implementation:**
```python
# Group related commits across repositories
def detect_cross_repo_work(commits: list[Commit]) -> list[WorkGroup]:
    # Group by contributor + time window
    # Analyze message similarity
    # Return grouped work items
```

**Acceptance Criteria:**
- [ ] Cross-repo work detected
- [ ] Grouped in report
- [ ] Shows coordinated changes

**Estimated Effort:** 10 hours

---

#### Slice 1.4: Technical Debt Signals

**Goal:** Identify technical debt reduction vs feature work.

**Signals:**
- Refactoring commits (high churn, no new features)
- Test additions without feature changes
- Documentation improvements
- Dependency updates
- Code cleanup commits

**Value:**
- Managers see investment in code quality
- Distinguish maintenance from features
- Justify technical debt work

**Implementation:**
```python
# Detect technical debt reduction work
def detect_technical_debt_work(commit: Commit) -> bool:
    # Check for refactoring patterns
    # Check for test-only changes
    # Check for cleanup patterns
    # Return true if technical debt work
```

**Acceptance Criteria:**
- [ ] Technical debt work identified
- [ ] Shown separately in report
- [ ] Percentage of total work calculated

**Estimated Effort:** 6 hours

---

### Phase 2: Optional Jira Integration (Secondary)

#### Slice 2.1: Jira Connection Setup

**Goal:** Allow optional Jira integration for context enrichment.

**Configuration:**
```bash
# .env
JIRA_ENABLED=true
JIRA_URL=https://company.atlassian.net
JIRA_API_TOKEN=xxx
JIRA_PROJECT_KEYS=PROJ,TEAM
```

**Features:**
- Optional Jira connection
- Validate connection on startup
- Graceful degradation if Jira unavailable
- Clear logs when Jira is disabled

**Acceptance Criteria:**
- [ ] Jira connection configurable
- [ ] Connection validated
- [ ] Works without Jira (default)
- [ ] Clear error messages

**Estimated Effort:** 4 hours

---

#### Slice 2.2: Commit-to-Issue Linking

**Goal:** Link commits to Jira issues using commit message patterns.

**Detection:**
- Parse issue keys from commit messages (PROJ-123)
- Fetch issue details from Jira API
- Cache issue data to reduce API calls
- Handle missing/invalid issue keys gracefully

**Data Retrieved:**
- Issue key, summary, type (story, bug, task)
- Epic link (if exists)
- Status (to do, in progress, done)
- Priority (if relevant)

**Value:**
- Understand business context of commits
- Link technical work to business initiatives
- See which stories are progressing

**Implementation:**
```python
# Extract issue keys from commit messages
def extract_jira_keys(message: str) -> list[str]:
    # Regex: PROJ-\d+
    # Return list of issue keys

# Fetch issue details from Jira
async def fetch_jira_issues(keys: list[str]) -> dict[str, JiraIssue]:
    # Batch fetch from Jira API
    # Cache results
    # Return issue details
```

**Acceptance Criteria:**
- [ ] Issue keys extracted from commits
- [ ] Issue details fetched from Jira
- [ ] Cached to reduce API calls
- [ ] Graceful handling of missing issues
- [ ] Works without Jira data

**Estimated Effort:** 8 hours

---

#### Slice 2.3: Business Context Enrichment

**Goal:** Use Jira data to add business context to reports.

**Enrichment:**
- Show which epic/initiative work belongs to
- Indicate priority of work (if high priority)
- Show story completion (commits moving stories to done)
- Use story summary for business language translation

**Report Enhancement:**
```
## Projects
### Organization 1
#### Repository A (10 updates)
- Authentication improvements (PROJ-123: User Login Epic)
- Bug fixes (PROJ-456: High Priority)
- 2 stories completed

Business Context:
- Work focused on User Login Epic (Q1 priority)
- 2 high-priority bugs resolved
```

**Important Rules:**
- Don't report Jira metrics (velocity, story points)
- Don't track individual Jira activity
- Only use Jira for context, not facts
- Commits remain source of truth

**Acceptance Criteria:**
- [ ] Epic/initiative shown in report
- [ ] Priority indicated for high-priority work
- [ ] Story completion tracked
- [ ] Business language improved using story summaries
- [ ] No Jira metrics reported
- [ ] Works without Jira data

**Estimated Effort:** 10 hours

---

#### Slice 2.4: Jira Data Privacy

**Goal:** Ensure Jira integration respects privacy principles.

**Privacy Rules:**
- No individual Jira activity tracking
- No story point reporting
- No velocity metrics
- No developer rankings based on Jira
- Aggregate data only
- Clear what Jira data is used

**Implementation:**
- Document what Jira data is collected
- Document what is NOT collected
- Add privacy audit log
- Allow Jira integration to be disabled

**Acceptance Criteria:**
- [ ] Privacy policy documented
- [ ] No individual tracking
- [ ] No productivity metrics from Jira
- [ ] Audit log for Jira data access
- [ ] Can be disabled anytime

**Estimated Effort:** 4 hours

---

## Implementation Order

### Phase 1: Enhanced Commit Intelligence (Priority)
1. **Slice 1.1: Commit Pattern Analysis** (8h)
2. **Slice 1.2: Code Change Context** (12h)
3. **Slice 1.3: Cross-Repository Work** (10h)
4. **Slice 1.4: Technical Debt Signals** (6h)

**Phase 1 Total:** 36 hours (~5 days)

### Phase 2: Optional Jira Integration (Secondary)
5. **Slice 2.1: Jira Connection Setup** (4h)
6. **Slice 2.2: Commit-to-Issue Linking** (8h)
7. **Slice 2.3: Business Context Enrichment** (10h)
8. **Slice 2.4: Jira Data Privacy** (4h)

**Phase 2 Total:** 26 hours (~3 days)

**MVP-v3 Total:** 62 hours (~8 days)

---

## Success Criteria

### Phase 1: Commit Intelligence
- [ ] Commits classified by type (feature, bug, refactor, etc.)
- [ ] Code change context analyzed and reported
- [ ] Cross-repository work detected and grouped
- [ ] Technical debt work identified and quantified
- [ ] Reports provide deeper insights from commits alone

### Phase 2: Jira Integration
- [ ] Jira integration is optional and configurable
- [ ] Commits linked to Jira issues
- [ ] Business context added to reports
- [ ] Privacy principles maintained
- [ ] System works perfectly without Jira

### Overall
- [ ] Report quality improved significantly
- [ ] Managers get better insights from commits
- [ ] Jira adds value when available
- [ ] No degradation when Jira unavailable

---

## Non-Goals (Deferred to Future)

- ❌ Jira-first reporting (commits always primary)
- ❌ Jira velocity/story point metrics
- ❌ Individual Jira activity tracking
- ❌ Jira workflow automation
- ❌ Jira issue creation from Cogence
- ❌ Other project management tools (Linear, Asana, etc.)
- ❌ Code quality analysis (complexity, coverage)
- ❌ Pull request analysis
- ❌ CI/CD integration

---

## Architecture Considerations

### Data Model Changes

**New Tables:**
```sql
-- Commit classifications
CREATE TABLE commit_classifications (
    commit_sha VARCHAR(40) PRIMARY KEY,
    type VARCHAR(50),  -- FEATURE, BUGFIX, REFACTOR, etc.
    confidence FLOAT,
    detected_at TIMESTAMP
);

-- Jira issues (optional)
CREATE TABLE jira_issues (
    issue_key VARCHAR(50) PRIMARY KEY,
    summary TEXT,
    issue_type VARCHAR(50),
    epic_key VARCHAR(50),
    status VARCHAR(50),
    priority VARCHAR(50),
    fetched_at TIMESTAMP
);

-- Commit-to-issue links
CREATE TABLE commit_jira_links (
    commit_sha VARCHAR(40),
    issue_key VARCHAR(50),
    PRIMARY KEY (commit_sha, issue_key)
);
```

### Service Architecture

**New Services:**
- `app/services/commit_analyzer.py` - Commit pattern analysis
- `app/services/code_context.py` - Code change analysis
- `app/services/jira.py` - Jira API integration (optional)
- `app/services/enrichment.py` - Report enrichment with Jira data

**Service Dependencies:**
```
report.py
  ├── commit_analyzer.py (always)
  ├── code_context.py (always)
  └── enrichment.py (optional)
        └── jira.py (optional)
```

### Configuration

**New Settings:**
```python
# Commit analysis
COMMIT_CLASSIFICATION_ENABLED: bool = True
CODE_CONTEXT_ANALYSIS_ENABLED: bool = True

# Jira integration (optional)
JIRA_ENABLED: bool = False
JIRA_URL: str | None = None
JIRA_API_TOKEN: str | None = None
JIRA_PROJECT_KEYS: list[str] = []
JIRA_CACHE_TTL: int = 3600  # 1 hour
```

---

## Testing Strategy

### Phase 1: Commit Intelligence

**Unit Tests:**
- Commit classification accuracy
- Code context analysis correctness
- Cross-repo work detection
- Technical debt signal detection

**Integration Tests:**
- End-to-end report with classifications
- Multiple commit types in one report
- Cross-repo work in report
- Technical debt percentage calculation

### Phase 2: Jira Integration

**Unit Tests:**
- Issue key extraction from messages
- Jira API client
- Issue caching logic
- Privacy rule enforcement

**Integration Tests:**
- Report with Jira context
- Report without Jira (degradation)
- Jira API failure handling
- Cache behavior

**Manual Tests:**
- Real Jira integration
- Various commit message formats
- Missing/invalid issue keys
- Jira unavailable scenarios

---

## Migration Strategy

### Phase 1 Deployment
1. Deploy commit analysis features
2. Run analysis on historical commits
3. Generate reports with new insights
4. Collect feedback
5. Tune classification algorithms

### Phase 2 Deployment
1. Deploy Jira integration (disabled by default)
2. Enable for pilot team
3. Verify privacy compliance
4. Test with real Jira data
5. Collect feedback
6. Enable for all teams (optional)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Commit classification inaccurate | Medium | Tune algorithms, collect feedback, allow manual override |
| Jira API rate limits | Medium | Aggressive caching, batch requests, graceful degradation |
| Jira data privacy concerns | High | Clear documentation, audit logs, optional feature |
| Performance impact of analysis | Medium | Async processing, caching, configurable depth |
| Jira unavailable breaks reports | High | Graceful degradation, Jira is optional |

---

## Future Enhancements (Post MVP-v3)

### Commit Intelligence
- Machine learning for better classification
- Code complexity analysis
- Dependency graph analysis
- Security vulnerability detection
- Performance impact estimation

### Integration Expansion
- Linear integration
- GitHub Issues integration
- Azure DevOps integration
- Custom webhook integrations

### Advanced Features
- Predictive analytics (when will feature complete?)
- Risk detection (high-risk changes)
- Team health metrics (collaboration patterns)
- Custom report templates
- Interactive dashboards

---

## Documentation Updates

- [ ] Create `docs/features/commit-analysis.md`
- [ ] Create `docs/features/jira-integration.md`
- [ ] Create `docs/architecture/jira-integration.md`
- [ ] Update `docs/api/README.md` with new endpoints
- [ ] Create `docs/privacy/jira-data-handling.md`
- [ ] Update `README.md` with MVP-v3 features

---

## Success Metrics

### Commit Intelligence
- Classification accuracy > 80%
- Managers report better understanding of work types
- Technical debt work is visible and valued
- Cross-repo work is clearly identified

### Jira Integration
- 50%+ of teams enable Jira integration
- Business context improves report clarity
- No privacy complaints
- System remains stable without Jira

---

## Post-MVP-v3 Retrospective Questions

1. Did commit intelligence improve report quality?
2. Is commit classification accurate enough?
3. Is Jira integration valuable?
4. What percentage of teams use Jira integration?
5. Are privacy principles maintained?
6. What's the performance impact?
7. What should we build next?

---

**Last Updated:** 2026-06-24  
**Status:** Planning  
**Next Review:**  After MVP-v2 completion

---

## Appendix: Commit Classification Examples

### Feature Commits
```
feat: add user authentication
feat(api): implement OAuth2 flow
add: new dashboard component
implement: payment processing
```

### Bug Fix Commits
```
fix: resolve login timeout issue
fix(ui): correct button alignment
bugfix: handle null pointer exception
resolve: memory leak in worker
```

### Refactoring Commits
```
refactor: simplify authentication logic
refactor(db): optimize query performance
cleanup: remove unused imports
improve: code readability in parser
```

### Documentation Commits
```
docs: update API documentation
docs(readme): add setup instructions
documentation: clarify configuration
```

### Test Commits
```
test: add unit tests for auth
test(integration): add API tests
tests: improve coverage for parser
```

### Configuration Commits
```
config: update database settings
chore: bump dependency versions
ci: update GitHub Actions workflow