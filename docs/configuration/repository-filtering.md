# Repository Filtering Configuration

**Version:** 1.0.0  
**Last Updated:** 2026-06-24  
**Applies to:** MVP-v2+

---

## Overview

Repository filtering allows Cogence to track only specific repositories from your Git platform (Gitea), ignoring personal repositories, public repositories, or repositories from other organizations.

**Goal:** Focus on organizational repositories that matter for engineering reports.

---

## Why Filter Repositories?

### Problems Without Filtering

Without filtering, Cogence may track:
- ❌ Personal repositories of team members
- ❌ Public repositories the user has access to
- ❌ Repositories from other organizations
- ❌ Test/experimental repositories
- ❌ Archived repositories

### Benefits of Filtering

With filtering, Cogence only tracks:
- ✅ Repositories from specified organizations
- ✅ Active project repositories
- ✅ Repositories relevant to engineering reports
- ✅ Repositories you want to monitor

---

## Configuration

### Environment Variables

**Required (MVP-v2+):**
```bash
# Comma-separated list of organization names to track
GITEA_ORGANIZATIONS=acme,widgets,internal-tools

# Whether to include personal repositories (default: false)
GITEA_INCLUDE_PERSONAL=false
```

**Optional:**
```bash
# Exclude specific repositories by name (comma-separated)
GITEA_EXCLUDE_REPOSITORIES=test-repo,experimental,sandbox

# Include archived repositories (default: false)
GITEA_INCLUDE_ARCHIVED=false

# Repository name pattern to include (regex)
GITEA_REPOSITORY_PATTERN=^(api|ui|service)-.*

# Repository name pattern to exclude (regex)
GITEA_EXCLUDE_PATTERN=^(test|temp|demo)-.*
```

---

## Configuration Examples

### Example 1: Single Organization

**Scenario:** Track only repositories from "acme" organization

```bash
GITEA_ORGANIZATIONS=acme
GITEA_INCLUDE_PERSONAL=false
```

**Result:**
- ✅ Tracks: acme/customer-portal, acme/api-gateway
- ❌ Ignores: john/personal-project, public/open-source

---

### Example 2: Multiple Organizations

**Scenario:** Track repositories from multiple organizations

```bash
GITEA_ORGANIZATIONS=acme,widgets,internal-tools
GITEA_INCLUDE_PERSONAL=false
```

**Result:**
- ✅ Tracks: acme/*, widgets/*, internal-tools/*
- ❌ Ignores: other-org/*, personal repositories

---

### Example 3: Include Personal Repositories

**Scenario:** Track organization repos AND personal repos

```bash
GITEA_ORGANIZATIONS=acme
GITEA_INCLUDE_PERSONAL=true
```

**Result:**
- ✅ Tracks: acme/*, john/personal-project, jane/side-project
- ❌ Ignores: other-org/*

**Warning:** This may include many irrelevant repositories. Use with caution.

---

### Example 4: Exclude Specific Repositories

**Scenario:** Track organization but exclude test repositories

```bash
GITEA_ORGANIZATIONS=acme
GITEA_EXCLUDE_REPOSITORIES=test-repo,sandbox,experimental
```

**Result:**
- ✅ Tracks: acme/customer-portal, acme/api-gateway
- ❌ Ignores: acme/test-repo, acme/sandbox, acme/experimental

---

### Example 5: Pattern-Based Filtering

**Scenario:** Only track production services

```bash
GITEA_ORGANIZATIONS=acme
GITEA_REPOSITORY_PATTERN=^(api|service|ui)-.*
GITEA_EXCLUDE_PATTERN=^(test|demo|temp)-.*
```

**Result:**
- ✅ Tracks: acme/api-gateway, acme/service-auth, acme/ui-portal
- ❌ Ignores: acme/test-api, acme/demo-app, acme/temp-project

---

## How Filtering Works

### Filter Evaluation Order

1. **Organization Check** - Is repository in GITEA_ORGANIZATIONS?
2. **Personal Check** - If personal repo, is GITEA_INCLUDE_PERSONAL=true?
3. **Archived Check** - If archived, is GITEA_INCLUDE_ARCHIVED=true?
4. **Exclude List** - Is repository in GITEA_EXCLUDE_REPOSITORIES?
5. **Include Pattern** - Does repository match GITEA_REPOSITORY_PATTERN?
6. **Exclude Pattern** - Does repository match GITEA_EXCLUDE_PATTERN?

### Filter Logic

```python
def should_track_repository(repo: Repository) -> bool:
    # 1. Must be in specified organizations (if not personal)
    if not repo.is_personal:
        if repo.organization not in GITEA_ORGANIZATIONS:
            return False
    
    # 2. Personal repos only if explicitly enabled
    if repo.is_personal and not GITEA_INCLUDE_PERSONAL:
        return False
    
    # 3. Archived repos only if explicitly enabled
    if repo.is_archived and not GITEA_INCLUDE_ARCHIVED:
        return False
    
    # 4. Exclude specific repositories
    if repo.name in GITEA_EXCLUDE_REPOSITORIES:
        return False
    
    # 5. Include pattern (if specified)
    if GITEA_REPOSITORY_PATTERN:
        if not re.match(GITEA_REPOSITORY_PATTERN, repo.name):
            return False
    
    # 6. Exclude pattern (if specified)
    if GITEA_EXCLUDE_PATTERN:
        if re.match(GITEA_EXCLUDE_PATTERN, repo.name):
            return False
    
    return True
```

---

## Validation

### Startup Validation

Cogence validates configuration on startup:

```
✓ GITEA_ORGANIZATIONS configured: acme, widgets
✓ Found 15 repositories in specified organizations
✓ Filtered to 12 repositories (3 excluded)
✓ Repository filtering active
```

### Validation Errors

**Missing Organizations:**
```
ERROR: GITEA_ORGANIZATIONS is required but not set
Set GITEA_ORGANIZATIONS=org1,org2 in environment
```

**Invalid Pattern:**
```
ERROR: GITEA_REPOSITORY_PATTERN is invalid regex: ^(api|service
Fix regex pattern in GITEA_REPOSITORY_PATTERN
```

**No Repositories Found:**
```
WARNING: No repositories found for organizations: acme, widgets
Check organization names and Gitea API access
```

---

## Monitoring

### Filtered Repository Logs

Cogence logs filtering decisions:

```json
{
  "event": "repository_filtered",
  "repository": "acme/test-repo",
  "reason": "excluded_by_name",
  "organization": "acme"
}

{
  "event": "repository_filtered",
  "repository": "john/personal-project",
  "reason": "personal_repository_disabled",
  "owner": "john"
}

{
  "event": "repository_tracked",
  "repository": "acme/customer-portal",
  "organization": "acme"
}
```

### Filtering Statistics

View filtering statistics:

```bash
# Check logs for filtering summary
grep "repository_filtering_summary" logs/cogence.log

# Example output:
{
  "event": "repository_filtering_summary",
  "total_repositories": 25,
  "tracked_repositories": 12,
  "filtered_repositories": 13,
  "filter_reasons": {
    "wrong_organization": 5,
    "personal_repository": 4,
    "archived": 2,
    "excluded_by_name": 2
  }
}
```

---

## Best Practices

### 1. Start Specific, Expand Later

**Good:**
```bash
# Start with one organization
GITEA_ORGANIZATIONS=acme
```

**Bad:**
```bash
# Too broad, includes everything
GITEA_INCLUDE_PERSONAL=true
GITEA_INCLUDE_ARCHIVED=true
```

### 2. Use Organization Filtering First

**Preferred:**
```bash
# Simple, clear
GITEA_ORGANIZATIONS=acme,widgets
```

**Avoid (unless necessary):**
```bash
# Complex, hard to maintain
GITEA_REPOSITORY_PATTERN=^(acme|widgets)-.*
GITEA_EXCLUDE_PATTERN=^(test|demo)-.*
```

### 3. Exclude Test Repositories

**Recommended:**
```bash
GITEA_ORGANIZATIONS=acme
GITEA_EXCLUDE_REPOSITORIES=test-repo,sandbox,playground
```

### 4. Don't Include Personal Repositories (Usually)

**Default (Recommended):**
```bash
GITEA_INCLUDE_PERSONAL=false
```

**Only if needed:**
```bash
# Use only if team works on personal repos
GITEA_INCLUDE_PERSONAL=true
```

### 5. Monitor Filtering Logs

Regularly check logs to ensure filtering is working as expected:

```bash
# Check what's being filtered
grep "repository_filtered" logs/cogence.log | tail -20

# Check what's being tracked
grep "repository_tracked" logs/cogence.log | tail -20
```

---

## Troubleshooting

### Problem: No Repositories Found

**Symptoms:**
```
WARNING: No repositories found for organizations: acme
```

**Solutions:**
1. Check organization name spelling
2. Verify Gitea API access
3. Check GITEA_API_TOKEN permissions
4. Verify organizations exist in Gitea

**Debug:**
```bash
# Test Gitea API access
curl -H "Authorization: token ${GITEA_API_TOKEN}" \
  ${GITEA_URL}/api/v1/orgs/acme/repos
```

---

### Problem: Too Many Repositories Tracked

**Symptoms:**
- Reports include irrelevant repositories
- Personal projects in reports
- Test repositories in reports

**Solutions:**
1. Set `GITEA_INCLUDE_PERSONAL=false`
2. Add repositories to `GITEA_EXCLUDE_REPOSITORIES`
3. Use `GITEA_EXCLUDE_PATTERN` for test repos

**Example:**
```bash
GITEA_ORGANIZATIONS=acme
GITEA_INCLUDE_PERSONAL=false
GITEA_EXCLUDE_REPOSITORIES=test-repo,sandbox
GITEA_EXCLUDE_PATTERN=^(test|demo|temp)-.*
```

---

### Problem: Important Repository Not Tracked

**Symptoms:**
- Repository missing from reports
- Expected commits not appearing

**Solutions:**
1. Check if repository is in specified organizations
2. Check if repository is in exclude list
3. Check if repository matches exclude pattern
4. Check if repository is archived

**Debug:**
```bash
# Check filtering logs for specific repository
grep "customer-portal" logs/cogence.log | grep "repository_"
```

---

### Problem: Pattern Not Working

**Symptoms:**
- Pattern doesn't match expected repositories
- Regex errors in logs

**Solutions:**
1. Test regex pattern separately
2. Check regex syntax
3. Use simpler patterns
4. Use exclude list instead of pattern

**Test Pattern:**
```python
import re

pattern = r"^(api|service)-.*"
test_names = ["api-gateway", "service-auth", "ui-portal"]

for name in test_names:
    if re.match(pattern, name):
        print(f"✓ {name} matches")
    else:
        print(f"✗ {name} doesn't match")
```

---

## Migration Guide

### From MVP-v1 to MVP-v2

**MVP-v1 (No Filtering):**
- Tracked all visible repositories
- No configuration needed
- May include irrelevant repos

**MVP-v2 (With Filtering):**
- Requires `GITEA_ORGANIZATIONS` configuration
- Only tracks specified organizations
- Excludes personal/public repos by default

**Migration Steps:**

1. **Identify Organizations:**
   ```bash
   # List all organizations in Gitea
   curl -H "Authorization: token ${GITEA_API_TOKEN}" \
     ${GITEA_URL}/api/v1/user/orgs
   ```

2. **Configure Organizations:**
   ```bash
   # Add to .env
   GITEA_ORGANIZATIONS=acme,widgets,internal-tools
   ```

3. **Test Configuration:**
   ```bash
   # Restart Cogence and check logs
   docker-compose restart cogence
   docker-compose logs cogence | grep "repository_filtering_summary"
   ```

4. **Verify Reports:**
   - Generate a test report
   - Verify only expected repositories appear
   - Check for missing repositories

5. **Adjust if Needed:**
   - Add excluded repositories
   - Adjust patterns
   - Enable personal repos if needed

---

## Configuration Reference

### Complete Configuration Example

```bash
# .env

# Required: Organizations to track
GITEA_ORGANIZATIONS=acme,widgets,internal-tools

# Optional: Personal repositories (default: false)
GITEA_INCLUDE_PERSONAL=false

# Optional: Archived repositories (default: false)
GITEA_INCLUDE_ARCHIVED=false

# Optional: Exclude specific repositories
GITEA_EXCLUDE_REPOSITORIES=test-repo,sandbox,playground,demo

# Optional: Include pattern (regex)
GITEA_REPOSITORY_PATTERN=^(api|service|ui|lib)-.*

# Optional: Exclude pattern (regex)
GITEA_EXCLUDE_PATTERN=^(test|demo|temp|wip)-.*
```

### Configuration Validation

```python
# Validate configuration
from app.core.config import settings

# Check required settings
assert settings.gitea_organizations, "GITEA_ORGANIZATIONS required"

# Check patterns are valid regex
if settings.gitea_repository_pattern:
    re.compile(settings.gitea_repository_pattern)

if settings.gitea_exclude_pattern:
    re.compile(settings.gitea_exclude_pattern)
```

---

## Related Documentation

- [Development Setup](../development/setup.md) - Initial configuration
- [Gitea Integration](../architecture/gitea-integration.md) - Gitea API details
- [Data Collection](../architecture/data-collection.md) - How repositories are collected

---

**Last Updated:** 2026-06-24  
**Version:** 1.0.0  
**Next Review:** After MVP-v2 deployment