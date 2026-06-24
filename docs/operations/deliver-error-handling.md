# deliver.sh Error Handling Specification

**Version:** 1.0.0  
**Last Updated:** 2026-06-24  
**Applies to:** MVP-v2+

---

## Overview

This document specifies error handling improvements for the `deliver.sh` script, which delivers daily reports to Rocket.Chat. The goal is to provide specific, actionable error messages for different failure scenarios.

---

## Current Issues (MVP-v1)

### Problems

1. **Silent Failures** - Uses `curl -sf` which fails silently
2. **Generic Errors** - No distinction between error types
3. **No Context** - Error messages don't help diagnose issues
4. **No Logging** - Difficult to debug failures

### Example Current Behavior

```bash
# Network error - silent failure
$ ./scripts/deliver.sh
(no output, exit code 1)

# API error - generic message
$ ./scripts/deliver.sh
ERROR: empty response from generate endpoint
```

---

## Error Categories

### 1. Network Errors

**Causes:**
- Wrong COGENCE_API_URL
- DNS resolution failure
- Network connectivity issues
- Timeout

**Detection:**
```bash
# curl exit codes:
# 6 - Could not resolve host
# 7 - Failed to connect
# 28 - Timeout
```

**Error Message:**
```
ERROR: Cannot connect to Cogence API
  URL: http://localhost:8000
  Reason: Connection refused
  
Troubleshooting:
  1. Check if Cogence API is running: curl http://localhost:8000/health
  2. Verify COGENCE_API_URL is correct
  3. Check network connectivity
  4. Check firewall rules
```

---

### 2. Authentication Errors (401)

**Causes:**
- Wrong COGENCE_API_KEY
- Missing Authorization header
- Expired token

**Detection:**
```bash
# HTTP status code 401
```

**Error Message:**
```
ERROR: Authentication failed (401 Unauthorized)
  URL: http://localhost:8000/api/v1/reports/daily/2024-01-15/generate
  
Troubleshooting:
  1. Verify COGENCE_API_KEY is correct
  2. Check API key in .env file
  3. Ensure API key matches server configuration (API_SECRET_KEY)
  4. Test authentication: curl -H "Authorization: Bearer $COGENCE_API_KEY" http://localhost:8000/health
```

---

### 3. Not Found Errors (404)

**Causes:**
- No commits collected for date
- Wrong API endpoint
- Report not generated yet

**Detection:**
```bash
# HTTP status code 404
```

**Error Message:**
```
ERROR: Report not found (404 Not Found)
  Date: 2024-01-15
  URL: http://localhost:8000/api/v1/reports/daily/2024-01-15/generate
  
Troubleshooting:
  1. Check if commits were collected for this date
  2. Verify data collection is running: check logs
  3. Try generating report manually: curl -X POST -H "Authorization: Bearer $COGENCE_API_KEY" http://localhost:8000/api/v1/reports/daily/2024-01-15/generate
  4. Check if repositories are configured correctly
```

---

### 4. Server Errors (500)

**Causes:**
- Database connection failure
- LLM API failure
- Internal server error
- Configuration error

**Detection:**
```bash
# HTTP status code 500
```

**Error Message:**
```
ERROR: Server error (500 Internal Server Error)
  URL: http://localhost:8000/api/v1/reports/daily/2024-01-15/generate
  
Troubleshooting:
  1. Check Cogence server logs: docker-compose logs cogence
  2. Check database connectivity
  3. Check OpenAI API status
  4. Verify server configuration
  5. Contact system administrator
```

---

### 5. Empty Response

**Causes:**
- Server crashed during request
- Network interruption
- Timeout without error

**Detection:**
```bash
# curl succeeds but response is empty
```

**Error Message:**
```
ERROR: Empty response from Cogence API
  URL: http://localhost:8000/api/v1/reports/daily/2024-01-15/generate
  
Troubleshooting:
  1. Check if server is running: curl http://localhost:8000/health
  2. Check server logs for crashes: docker-compose logs cogence
  3. Increase timeout if network is slow
  4. Try request again
```

---

### 6. Rocket.Chat Webhook Errors

**Causes:**
- Wrong webhook URL
- Webhook disabled
- Rocket.Chat server down
- Network issues

**Detection:**
```bash
# curl to webhook fails
```

**Error Message:**
```
ERROR: Failed to deliver report to Rocket.Chat
  Webhook: https://chat.example.com/hooks/xxx
  Reason: Connection refused
  
Troubleshooting:
  1. Verify ROCKETCHAT_WEBHOOK is correct
  2. Check if Rocket.Chat is accessible: curl https://chat.example.com
  3. Verify webhook is enabled in Rocket.Chat settings
  4. Check network connectivity to Rocket.Chat server
  
Note: Report was generated successfully but delivery failed.
```

---

## Improved Implementation

### Enhanced Error Handling

```bash
#!/usr/bin/env bash
# Deliver yesterday's daily report to Rocket.Chat.
# Enhanced error handling for MVP-v2

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Check required environment variables
: "${COGENCE_API_URL:?COGENCE_API_URL must be set}"
: "${COGENCE_API_KEY:?COGENCE_API_KEY must be set}"
: "${ROCKETCHAT_WEBHOOK:?ROCKETCHAT_WEBHOOK must be set}"

# Calculate yesterday's date
DATE=$(TZ=Asia/Tehran date -d "yesterday" +%Y-%m-%d 2>/dev/null \
    || TZ=Asia/Tehran date -v-1d +%Y-%m-%d)

log_info "Generating report for ${DATE}..."

# Generate report with detailed error handling
REPORT_URL="${COGENCE_API_URL}/api/v1/reports/daily/${DATE}/generate"
HTTP_CODE=$(curl -w "%{http_code}" -o /tmp/report_response.json -s \
    -X POST \
    -H "Authorization: Bearer ${COGENCE_API_KEY}" \
    -H "Content-Type: application/json" \
    "${REPORT_URL}" 2>/tmp/curl_error.txt || echo "000")

# Check curl exit code
CURL_EXIT=$?
if [ $CURL_EXIT -ne 0 ]; then
    log_error "Cannot connect to Cogence API"
    log_error "  URL: ${REPORT_URL}"
    
    # Parse curl error
    if [ -f /tmp/curl_error.txt ]; then
        CURL_ERROR=$(cat /tmp/curl_error.txt)
        log_error "  Reason: ${CURL_ERROR}"
    fi
    
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if Cogence API is running:"
    echo "     curl ${COGENCE_API_URL}/health"
    echo "  2. Verify COGENCE_API_URL is correct"
    echo "  3. Check network connectivity"
    echo "  4. Check firewall rules"
    
    exit 1
fi

# Check HTTP status code
case $HTTP_CODE in
    200|201)
        log_info "Report generated successfully (HTTP ${HTTP_CODE})"
        ;;
    
    401)
        log_error "Authentication failed (401 Unauthorized)"
        log_error "  URL: ${REPORT_URL}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Verify COGENCE_API_KEY is correct"
        echo "  2. Check API key in .env file"
        echo "  3. Ensure API key matches server configuration"
        echo "  4. Test authentication:"
        echo "     curl -H \"Authorization: Bearer \$COGENCE_API_KEY\" ${COGENCE_API_URL}/health"
        exit 1
        ;;
    
    404)
        log_error "Report not found (404 Not Found)"
        log_error "  Date: ${DATE}"
        log_error "  URL: ${REPORT_URL}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check if commits were collected for this date"
        echo "  2. Verify data collection is running"
        echo "  3. Check repository configuration"
        echo "  4. View server logs: docker-compose logs cogence"
        exit 1
        ;;
    
    500|502|503)
        log_error "Server error (${HTTP_CODE})"
        log_error "  URL: ${REPORT_URL}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check server logs: docker-compose logs cogence"
        echo "  2. Check database connectivity"
        echo "  3. Check OpenAI API status"
        echo "  4. Verify server configuration"
        exit 1
        ;;
    
    000)
        log_error "Empty response from Cogence API"
        log_error "  URL: ${REPORT_URL}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check if server is running"
        echo "  2. Check server logs for crashes"
        echo "  3. Try request again"
        exit 1
        ;;
    
    *)
        log_error "Unexpected HTTP status: ${HTTP_CODE}"
        log_error "  URL: ${REPORT_URL}"
        if [ -f /tmp/report_response.json ]; then
            log_error "  Response: $(cat /tmp/report_response.json)"
        fi
        exit 1
        ;;
esac

# Read and validate response
if [ ! -f /tmp/report_response.json ]; then
    log_error "Response file not found"
    exit 1
fi

REPORT=$(cat /tmp/report_response.json)

if [ -z "$REPORT" ]; then
    log_error "Empty response from generate endpoint"
    exit 1
fi

# Extract report fields
EXEC_SUMMARY=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('executive_summary',''))" 2>/dev/null || echo "")
TOTAL=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['metadata']['total_commits'])" 2>/dev/null || echo "0")
REPOS=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['metadata']['total_repositories'])" 2>/dev/null || echo "0")

if [ -z "$EXEC_SUMMARY" ]; then
    log_error "Invalid report format: missing executive_summary"
    log_error "Response: ${REPORT}"
    exit 1
fi

# Build Rocket.Chat message
REPO_LINES=$(echo "$REPORT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('repositories',[]):
    print(f\"  • {r['name']}: {r['summary']}\")
" 2>/dev/null || echo "")

CONTRIB_LINES=$(echo "$REPORT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for c in d.get('contributors',[]):
    print(f\"  • {c['name']}: {c['summary']}\")
" 2>/dev/null || echo "")

MESSAGE=$(cat <<EOF
*Daily Engineering Report — ${DATE}*

${EXEC_SUMMARY}

*Active Repositories (${REPOS}):*
${REPO_LINES:-  No active repositories.}

*Contributors:*
${CONTRIB_LINES:-  No activity recorded.}

_${TOTAL} update(s) collected • Cogence_
EOF
)

# Send to Rocket.Chat with error handling
PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1]}))" "$MESSAGE")

log_info "Delivering report to Rocket.Chat..."

WEBHOOK_HTTP_CODE=$(curl -w "%{http_code}" -o /tmp/webhook_response.txt -s \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "${ROCKETCHAT_WEBHOOK}" 2>/tmp/webhook_error.txt || echo "000")

WEBHOOK_EXIT=$?

if [ $WEBHOOK_EXIT -ne 0 ] || [ "$WEBHOOK_HTTP_CODE" != "200" ]; then
    log_error "Failed to deliver report to Rocket.Chat"
    log_error "  Webhook: ${ROCKETCHAT_WEBHOOK}"
    log_error "  HTTP Code: ${WEBHOOK_HTTP_CODE}"
    
    if [ -f /tmp/webhook_error.txt ]; then
        WEBHOOK_ERROR=$(cat /tmp/webhook_error.txt)
        log_error "  Reason: ${WEBHOOK_ERROR}"
    fi
    
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify ROCKETCHAT_WEBHOOK is correct"
    echo "  2. Check if Rocket.Chat is accessible"
    echo "  3. Verify webhook is enabled in Rocket.Chat"
    echo "  4. Check network connectivity"
    echo ""
    log_warn "Note: Report was generated successfully but delivery failed"
    log_warn "Report saved to: /tmp/report_response.json"
    
    exit 1
fi

log_info "Report delivered successfully for ${DATE}"

# Cleanup
rm -f /tmp/report_response.json /tmp/curl_error.txt /tmp/webhook_response.txt /tmp/webhook_error.txt

exit 0
```

---

## Testing Error Scenarios

### Test Network Error

```bash
# Set wrong URL
export COGENCE_API_URL=http://invalid-host:8000
./scripts/deliver.sh

# Expected output:
# [ERROR] Cannot connect to Cogence API
#   URL: http://invalid-host:8000/api/v1/reports/daily/2024-01-15/generate
#   Reason: Could not resolve host: invalid-host
# 
# Troubleshooting:
#   1. Check if Cogence API is running...
```

### Test Authentication Error

```bash
# Set wrong API key
export COGENCE_API_KEY=wrong-key
./scripts/deliver.sh

# Expected output:
# [ERROR] Authentication failed (401 Unauthorized)
#   URL: http://localhost:8000/api/v1/reports/daily/2024-01-15/generate
# 
# Troubleshooting:
#   1. Verify COGENCE_API_KEY is correct...
```

### Test Not Found Error

```bash
# Try to generate report for date with no data
export DATE=2020-01-01
./scripts/deliver.sh

# Expected output:
# [ERROR] Report not found (404 Not Found)
#   Date: 2020-01-01
#   URL: http://localhost:8000/api/v1/reports/daily/2020-01-01/generate
# 
# Troubleshooting:
#   1. Check if commits were collected for this date...
```

### Test Server Error

```bash
# Stop database to trigger server error
docker-compose stop postgres
./scripts/deliver.sh

# Expected output:
# [ERROR] Server error (500)
#   URL: http://localhost:8000/api/v1/reports/daily/2024-01-15/generate
# 
# Troubleshooting:
#   1. Check server logs: docker-compose logs cogence...
```

### Test Webhook Error

```bash
# Set wrong webhook URL
export ROCKETCHAT_WEBHOOK=https://invalid-webhook.com/hooks/xxx
./scripts/deliver.sh

# Expected output:
# [INFO] Report generated successfully (HTTP 200)
# [INFO] Delivering report to Rocket.Chat...
# [ERROR] Failed to deliver report to Rocket.Chat
#   Webhook: https://invalid-webhook.com/hooks/xxx
#   HTTP Code: 000
#   Reason: Could not resolve host
# 
# Troubleshooting:
#   1. Verify ROCKETCHAT_WEBHOOK is correct...
# 
# [WARN] Note: Report was generated successfully but delivery failed
# [WARN] Report saved to: /tmp/report_response.json
```

---

## Logging

### Log Format

All operations are logged with timestamps:

```
[2024-01-15 21:00:00] [INFO] Generating report for 2024-01-15...
[2024-01-15 21:00:02] [INFO] Report generated successfully (HTTP 200)
[2024-01-15 21:00:02] [INFO] Delivering report to Rocket.Chat...
[2024-01-15 21:00:03] [INFO] Report delivered successfully for 2024-01-15
```

### Log to File

```bash
# Log to file
./scripts/deliver.sh >> /var/log/cogence/deliver.log 2>&1

# Log with timestamp
./scripts/deliver.sh 2>&1 | ts '[%Y-%m-%d %H:%M:%S]' >> /var/log/cogence/deliver.log
```

---

## Monitoring

### Cron Job Setup

```bash
# /etc/cron.d/cogence-deliver
# Run at 21:00 Asia/Tehran daily

0 21 * * * cogence TZ=Asia/Tehran /opt/cogence/scripts/deliver.sh >> /var/log/cogence/deliver.log 2>&1
```

### Alert on Failures

```bash
# Wrapper script with alerting
#!/bin/bash

if ! /opt/cogence/scripts/deliver.sh; then
    # Send alert email
    echo "Cogence report delivery failed" | mail -s "Cogence Alert" admin@example.com
    
    # Send Slack notification
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Cogence report delivery failed"}' \
        https://hooks.slack.com/services/YOUR/WEBHOOK/URL
fi
```

### Health Check

```bash
# Check if delivery is working
#!/bin/bash

# Check last successful delivery
LAST_SUCCESS=$(grep "Report delivered successfully" /var/log/cogence/deliver.log | tail -1)

if [ -z "$LAST_SUCCESS" ]; then
    echo "ERROR: No successful deliveries found"
    exit 1
fi

# Check if last delivery was within 24 hours
LAST_DATE=$(echo "$LAST_SUCCESS" | grep -oP '\d{4}-\d{2}-\d{2}')
TODAY=$(date +%Y-%m-%d)

if [ "$LAST_DATE" != "$TODAY" ] && [ "$LAST_DATE" != "$(date -d yesterday +%Y-%m-%d)" ]; then
    echo "WARNING: Last successful delivery was on $LAST_DATE"
    exit 1
fi

echo "OK: Delivery is working"
exit 0
```

---

## Troubleshooting Guide

### Common Issues

**Issue: "Cannot connect to Cogence API"**
- Check if Cogence is running: `docker-compose ps`
- Check if port is accessible: `curl http://localhost:8000/health`
- Check firewall rules
- Check COGENCE_API_URL setting

**Issue: "Authentication failed"**
- Verify API key: `echo $COGENCE_API_KEY`
- Check .env file
- Compare with server API_SECRET_KEY
- Test with curl: `curl -H "Authorization: Bearer $COGENCE_API_KEY" http://localhost:8000/health`

**Issue: "Report not found"**
- Check if data collection ran: `docker-compose logs cogence | grep commit_collection`
- Check repository configuration
- Verify commits exist for date
- Check server logs for errors

**Issue: "Failed to deliver to Rocket.Chat"**
- Verify webhook URL
- Check Rocket.Chat accessibility
- Verify webhook is enabled
- Check network connectivity
- Report is saved to /tmp/report_response.json

---

## Related Documentation

- [Development Setup](../development/setup.md) - Initial setup
- [Operations Guide](../operations/README.md) - Production operations
- [Monitoring](../operations/monitoring.md) - Monitoring and alerts

---

**Last Updated:** 2026-06-24  
**Version:** 1.0.0  
**Next Review:** After MVP-v2 deployment