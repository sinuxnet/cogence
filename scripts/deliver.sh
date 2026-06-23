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

# Yesterday in Asia/Tehran
DATE=$(TZ=Asia/Tehran date -d "yesterday" +%Y-%m-%d 2>/dev/null \
    || TZ=Asia/Tehran date -v-1d +%Y-%m-%d)

echo "Generating report for ${DATE}..."

REPORT=$(curl -sf -X POST \
    -H "Authorization: Bearer ${COGENCE_API_KEY}" \
    -H "Content-Type: application/json" \
    "${COGENCE_API_URL}/api/v1/reports/daily/${DATE}/generate")

if [ -z "$REPORT" ]; then
    echo "ERROR: empty response from generate endpoint" >&2
    exit 1
fi

# Build Rocket.Chat message from report fields
EXEC_SUMMARY=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('executive_summary',''))")
MGMT_NOTES=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('management_notes',''))")
TOTAL=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['metadata']['total_commits'])")
REPOS=$(echo "$REPORT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['metadata']['total_repositories'])")

REPO_LINES=$(echo "$REPORT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('repositories',[]):
    print(f\"  • {r['name']}: {r['summary']}\")
")

CONTRIB_LINES=$(echo "$REPORT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for c in d.get('contributors',[]):
    print(f\"  • {c['name']}: {c['summary']}\")
")

MESSAGE=$(cat <<EOF
*Daily Engineering Report — ${DATE}*

${EXEC_SUMMARY}

*Active Repositories (${REPOS}):*
${REPO_LINES:-  No active repositories.}

*Contributors:*
${CONTRIB_LINES:-  No activity recorded.}

*Management Notes:*
${MGMT_NOTES}

_${TOTAL} commit(s) collected • Cogence_
EOF
)

PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1]}))" "$MESSAGE")

curl -sf -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "${ROCKETCHAT_WEBHOOK}"

echo "Report delivered for ${DATE}."
