# API Versioning Strategy

**Version:** 1.0.0  
**Last Updated:** 2026-06-24  
**Status:** Active

---

## Overview

This document defines the versioning strategy for the Cogence API, including version numbering, deprecation policy, and evolution guidelines.

---

## Versioning Approach

### URL-Based Versioning

Cogence uses URL-based versioning for the API:

```
https://api.cogence.example.com/api/v1/reports/daily/2024-01-15
                                    ^^^
                                    Version
```

**Rationale:**
- Clear and explicit version in URL
- Easy to route different versions
- Simple for clients to understand
- Standard practice in REST APIs

---

## Version Numbering

### API Version Format

**Format:** `v{major}`

**Examples:**
- `v1` - First major version
- `v2` - Second major version
- `v3` - Third major version

**Note:** We use major version only in URLs. Full semantic versioning (v1.2.3) is tracked internally but not exposed in URLs.

### Semantic Versioning (Internal)

**Format:** `MAJOR.MINOR.PATCH`

**Rules:**
- **MAJOR** - Breaking changes (incompatible API changes)
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

**Examples:**
- `1.0.0` - Initial release (MVP-v1)
- `1.1.0` - Added new endpoints (MVP-v2)
- `1.1.1` - Bug fix in report generation
- `2.0.0` - Breaking change in report structure

---

## What Constitutes a Breaking Change

### Breaking Changes (Require Major Version Bump)

❌ **These require a new major version:**

1. **Removing endpoints**
   ```
   # v1
   GET /api/v1/reports/daily/{date}
   
   # v2 - endpoint removed (BREAKING)
   # Endpoint no longer exists
   ```

2. **Removing required fields from responses**
   ```json
   // v1
   {
     "report_date": "2024-01-15",
     "executive_summary": "...",
     "repositories": []
   }
   
   // v2 - removed field (BREAKING)
   {
     "report_date": "2024-01-15",
     "repositories": []
     // executive_summary removed
   }
   ```

3. **Changing field types**
   ```json
   // v1
   {"total_commits": 25}
   
   // v2 - type changed (BREAKING)
   {"total_commits": "25"}
   ```

4. **Renaming fields**
   ```json
   // v1
   {"report_date": "2024-01-15"}
   
   // v2 - renamed (BREAKING)
   {"date": "2024-01-15"}
   ```

5. **Changing URL structure**
   ```
   # v1
   GET /api/v1/reports/daily/{date}
   
   # v2 - URL changed (BREAKING)
   GET /api/v2/daily-reports/{date}
   ```

6. **Changing authentication method**
   ```
   # v1 - Bearer token
   Authorization: Bearer {token}
   
   # v2 - API key header (BREAKING)
   X-API-Key: {key}
   ```

7. **Changing error response format**
   ```json
   // v1
   {"error": "Not found"}
   
   // v2 - format changed (BREAKING)
   {"errors": [{"code": "NOT_FOUND", "message": "Not found"}]}
   ```

### Non-Breaking Changes (Minor/Patch Version)

✅ **These are backward compatible:**

1. **Adding new endpoints**
   ```
   # v1.0.0
   GET /api/v1/reports/daily/{date}
   
   # v1.1.0 - new endpoint (OK)
   GET /api/v1/reports/weekly/{date}
   ```

2. **Adding optional fields to responses**
   ```json
   // v1.0.0
   {
     "report_date": "2024-01-15",
     "repositories": []
   }
   
   // v1.1.0 - new optional field (OK)
   {
     "report_date": "2024-01-15",
     "repositories": [],
     "metadata": {}  // New field
   }
   ```

3. **Adding optional query parameters**
   ```
   # v1.0.0
   GET /api/v1/reports/daily/{date}
   
   # v1.1.0 - new optional param (OK)
   GET /api/v1/reports/daily/{date}?locale=fa
   ```

4. **Bug fixes that don't change behavior**
   ```
   # v1.0.0 - Bug: returns 500 on invalid date
   # v1.0.1 - Fix: returns 400 on invalid date (OK)
   ```

5. **Performance improvements**
   ```
   # v1.0.0 - Report generation takes 5s
   # v1.0.1 - Report generation takes 2s (OK)
   ```

---

## Version Lifecycle

### Version States

1. **Active** - Current version, fully supported
2. **Deprecated** - Still works but will be removed
3. **Sunset** - No longer available

### Lifecycle Timeline

```
v1 Released ──────────────────────────────────────────────────────
              │
              │ 6 months
              │
v2 Released ──┴─────────────────────────────────────────────────
              │                                                  │
              │ v1 enters DEPRECATED state                       │
              │ (still works, but clients should migrate)       │
              │                                                  │
              │ 6 months deprecation period                      │
              │                                                  │
v1 Sunset ────┴──────────────────────────────────────────────────┴
              │
              v1 no longer available
```

**Timeline:**
- **Active Period:** Indefinite (until next major version)
- **Deprecation Period:** 6 months minimum
- **Total Support:** At least 6 months after next version release

---

## Deprecation Policy

### Announcing Deprecation

When a version is deprecated:

1. **Update API Response Headers**
   ```
   Deprecation: true
   Sunset: Sat, 31 Dec 2024 23:59:59 GMT
   Link: <https://docs.cogence.example.com/api/v2>; rel="successor-version"
   ```

2. **Update Documentation**
   - Add deprecation notice to docs
   - Provide migration guide
   - Show examples for new version

3. **Notify Users**
   - Email notification to all API users
   - In-app notification (if applicable)
   - Blog post announcement

4. **Log Warnings**
   ```
   [WARN] API v1 is deprecated and will be sunset on 2024-12-31
   ```

### Migration Support

During deprecation period:

- Both versions remain fully functional
- Documentation for both versions available
- Migration guide provided
- Support team available for questions
- No new features added to deprecated version
- Critical bugs still fixed in deprecated version

---

## Version Discovery

### Version Endpoint

**Endpoint:** `GET /api/version`

**Response:**
```json
{
  "current_version": "v1",
  "api_version": "1.2.3",
  "supported_versions": ["v1"],
  "deprecated_versions": [],
  "sunset_dates": {}
}
```

### Version in Response Headers

All API responses include version information:

```
X-API-Version: 1.2.3
X-API-Major-Version: v1
```

---

## Version Evolution Examples

### Example 1: MVP-v1 to MVP-v2 (Minor Version)

**Changes:**
- New report structure (hierarchical)
- New fields added (organization grouping)
- Existing fields preserved
- No breaking changes

**Version:** `1.0.0` → `1.1.0`

**URL:** Remains `v1`

**Migration:** Optional (clients can continue using old structure)

### Example 2: Future Breaking Change (Major Version)

**Changes:**
- Remove "management_notes" field
- Rename "repositories" to "projects"
- Change authentication method

**Version:** `1.x.x` → `2.0.0`

**URL:** `v1` → `v2`

**Migration:** Required (v1 will be deprecated)

---

## API Evolution Guidelines

### Adding New Features

**Preferred Approach:**
1. Add new optional fields
2. Add new endpoints
3. Add new query parameters
4. Keep existing behavior unchanged

**Example:**
```
# v1.0.0
GET /api/v1/reports/daily/{date}
Response: { "report_date": "...", "repositories": [] }

# v1.1.0 - Add organization grouping (backward compatible)
GET /api/v1/reports/daily/{date}
Response: { 
  "report_date": "...", 
  "repositories": [],
  "organizations": []  // New field
}
```

### Changing Existing Features

**If change is backward compatible:**
- Increment minor version
- Add new field/endpoint
- Keep old field/endpoint (mark as deprecated if needed)

**If change is breaking:**
- Increment major version
- Create new API version (v2)
- Deprecate old version
- Provide migration guide

---

## Client Compatibility

### Client Responsibilities

Clients should:
1. **Specify version in URL** - Always use versioned endpoints
2. **Handle new fields gracefully** - Ignore unknown fields
3. **Monitor deprecation headers** - Check for deprecation warnings
4. **Plan for migrations** - Migrate before sunset date
5. **Test with new versions** - Test against beta/preview versions

### Server Guarantees

Server guarantees:
1. **No breaking changes within major version** - v1 stays compatible
2. **Minimum 6 months deprecation** - Time to migrate
3. **Clear migration path** - Documentation and examples
4. **Backward compatibility** - Old clients continue working

---

## Version Documentation

### Documentation Structure

```
docs/api/
├── README.md              # Current version (v1)
├── versioning.md          # This document
├── changelog.md           # Version history
├── v1/
│   ├── endpoints.md       # v1 endpoints
│   ├── examples.md        # v1 examples
│   └── migration.md       # Migration from v0 (if exists)
└── v2/                    # Future version
    ├── endpoints.md
    ├── examples.md
    └── migration-from-v1.md
```

### Changelog Format

**File:** `docs/api/changelog.md`

**Format:**
```markdown
# API Changelog

## v1.2.0 (2024-02-15)

### Added
- New endpoint: GET /api/v1/reports/weekly/{date}
- New field: organizations in daily report response

### Changed
- Improved performance of report generation (2s → 1s)

### Fixed
- Fixed error handling for invalid date format

## v1.1.0 (2024-01-20)

### Added
- New query parameter: locale for report language

### Fixed
- Fixed timezone handling in report timestamps
```

---

## Testing Strategy

### Version Testing

**Test Matrix:**
```
┌─────────────┬──────────┬──────────┬──────────┐
│ Test Case   │ v1       │ v2       │ v3       │
├─────────────┼──────────┼──────────┼──────────┤
│ Unit Tests  │ ✓        │ ✓        │ ✓        │
│ Integration │ ✓        │ ✓        │ ✓        │
│ E2E Tests   │ ✓        │ ✓        │ ✓        │
│ Backward    │ N/A      │ ✓        │ ✓        │
│ Compat      │          │          │          │
└─────────────┴──────────┴──────────┴──────────┘
```

**Backward Compatibility Tests:**
```python
# Test that v1 clients work with v2 server
def test_v1_client_with_v2_server():
    # Use v1 request format
    response = client.get("/api/v1/reports/daily/2024-01-15")
    
    # Should work and return v1-compatible response
    assert response.status_code == 200
    assert "report_date" in response.json()
    assert "repositories" in response.json()
```

---

## Monitoring and Metrics

### Version Usage Metrics

Track:
- Requests per version
- Unique clients per version
- Deprecated version usage
- Migration progress

**Example Dashboard:**
```
API Version Usage (Last 30 Days)
┌─────────┬──────────┬────────────┬──────────┐
│ Version │ Requests │ % of Total │ Clients  │
├─────────┼──────────┼────────────┼──────────┤
│ v1      │ 1.2M     │ 85%        │ 45       │
│ v2      │ 200K     │ 15%        │ 12       │
└─────────┴──────────┴────────────┴──────────┘

Deprecated Version Usage
┌─────────┬──────────┬─────────────┬──────────┐
│ Version │ Requests │ Sunset Date │ Status   │
├─────────┼──────────┼─────────────┼──────────┤
│ v1      │ 50K      │ 2024-12-31  │ ⚠️ Warn  │
└─────────┴──────────┴─────────────┴──────────┘
```

---

## Future Considerations

### Potential Future Versions

**v2.0.0 (Hypothetical):**
- Remove "management_notes" field
- Restructure error responses
- Change authentication to OAuth2
- Add GraphQL endpoint

**v3.0.0 (Hypothetical):**
- Full GraphQL API
- Real-time subscriptions
- Advanced filtering and pagination
- Multi-tenancy support

---

## References

- [Semantic Versioning](https://semver.org/)
- [API Versioning Best Practices](https://restfulapi.net/versioning/)
- [HTTP Deprecation Header](https://tools.ietf.org/id/draft-dalal-deprecation-header-01.html)

---

**Last Updated:** 2026-06-24  
**Version:** 1.0.0  
**Next Review:** After MVP-v2 release