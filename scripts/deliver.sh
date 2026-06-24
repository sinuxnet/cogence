#!/usr/bin/env bash
# Deliver yesterday's daily report to Rocket.Chat.
# Schedule via cron at 07:00 Asia/Tehran, e.g.:
#   0 7 * * * TZ=Asia/Tehran /path/to/cogence/scripts/deliver.sh
#
# Required env vars:
#   COGENCE_API_URL      - base URL of the Cogence API (no trailing slash)
#   COGENCE_API_KEY      - bearer token (API_SECRET_KEY)
#   ROCKETCHAT_WEBHOOK   - Rocket.Chat incoming webhook URL

set -euo pipefail

: "${COGENCE_API_URL:?COGENCE_API_URL must be set}"
: "${COGENCE_API_KEY:?COGENCE_API_KEY must be set}"
: "${ROCKETCHAT_WEBHOOK:?ROCKETCHAT_WEBHOOK must be set}"

TS=$(TZ=Asia/Tehran date '+%Y-%m-%dT%H:%M:%S%z')

# Yesterday in Asia/Tehran
DATE=$(TZ=Asia/Tehran date -d "yesterday" +%Y-%m-%d 2>/dev/null \
    || TZ=Asia/Tehran date -v-1d +%Y-%m-%d)

echo "[${TS}] Generating report for ${DATE}..."

# Capture body and HTTP status code separately to give specific error messages
TMP=$(mktemp)
HTTP_CODE=$(curl -s -o "$TMP" -w "%{http_code}" -X POST \
    -H "Authorization: Bearer ${COGENCE_API_KEY}" \
    -H "Content-Type: application/json" \
    "${COGENCE_API_URL}/api/v1/reports/daily/${DATE}/generate" || echo "000")
REPORT=$(cat "$TMP")
rm -f "$TMP"

case "$HTTP_CODE" in
  200) ;;
  000) echo "[${TS}] ERROR: Network failure — could not reach ${COGENCE_API_URL}. Check URL and connectivity." >&2; exit 1 ;;
  401) echo "[${TS}] ERROR: [401] Authentication failed — check COGENCE_API_KEY." >&2; exit 1 ;;
  404) echo "[${TS}] ERROR: [404] No report found for ${DATE} — run the collector first or check the date." >&2; exit 1 ;;
  500) echo "[${TS}] ERROR: [500] Server error — check Cogence server logs." >&2; exit 1 ;;
  *)   echo "[${TS}] ERROR: [${HTTP_CODE}] Unexpected response from ${COGENCE_API_URL}." >&2; exit 1 ;;
esac

if [ -z "$REPORT" ]; then
    echo "[${TS}] ERROR: Empty response from generate endpoint." >&2
    exit 1
fi

# Extract fields from new v2 structure (general / projects / contributors)
TOTAL=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['general']['total_updates'])")
ORGS=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['general']['organizations_count'])")
CONTRIBS=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['general']['contributor_count'])")

PROJECT_LINES=$(echo "$REPORT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for org in d.get('projects', []):
    print(f\"*{org['organization']}:*\")
    for r in org.get('repositories', []):
        n = r['update_count']
        label = 'update' if n == 1 else 'updates'
        print(f\"  • {r['name']} ({n} {label}): {r['summary']}\")
")

CONTRIB_LINES=$(echo "$REPORT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for c in d.get('contributors', []):
    print(f\"  • {c['name']}: {c['summary']}\")
")

MESSAGE=$(cat <<EOF
*Daily Engineering Report — ${DATE}*

*Activity Summary:*
  • ${ORGS} organization(s) active
  • ${CONTRIBS} contributor(s)
  • ${TOTAL} total update(s)

*Projects:*
${PROJECT_LINES:-  No active repositories.}

*Contributors:*
${CONTRIB_LINES:-  No activity recorded.}

_${TOTAL} update(s) collected • Cogence_
EOF
)

PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1]}))" "$MESSAGE")

echo "[${TS}] Sending to Rocket.Chat..."

TMP=$(mktemp)
RC_CODE=$(curl -s -o "$TMP" -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "${ROCKETCHAT_WEBHOOK}" || echo "000")
RC_BODY=$(cat "$TMP")
rm -f "$TMP"

case "$RC_CODE" in
  200|204) ;;
  000) echo "[${TS}] ERROR: Network failure — could not reach Rocket.Chat webhook." >&2; exit 1 ;;
  401) echo "[${TS}] ERROR: [401] Rocket.Chat webhook rejected — check ROCKETCHAT_WEBHOOK URL." >&2; exit 1 ;;
  *)   echo "[${TS}] ERROR: [${RC_CODE}] Rocket.Chat webhook failed. Response: ${RC_BODY}" >&2; exit 1 ;;
esac

echo "[${TS}] Report delivered for ${DATE}."
