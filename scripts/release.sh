#!/usr/bin/env bash
# Create a new release: bump version, update CHANGELOG, tag the commit.
#
# Usage:
#   scripts/release.sh patch     # 0.2.0 → 0.2.1
#   scripts/release.sh minor     # 0.2.0 → 0.3.0
#   scripts/release.sh major     # 0.2.0 → 1.0.0
#   scripts/release.sh 0.5.0     # explicit version
#
# After running, push the tag with:
#   git push origin v<version>

set -euo pipefail

CHANGELOG="CHANGELOG.md"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# ── 1. Determine current version from last tag ────────────────────────────────
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
CURRENT="${LAST_TAG#v}"   # strip leading 'v'

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

# ── 2. Compute new version ────────────────────────────────────────────────────
BUMP="${1:-}"
case "$BUMP" in
  major)       NEW_VERSION="$((MAJOR + 1)).0.0" ;;
  minor)       NEW_VERSION="${MAJOR}.$((MINOR + 1)).0" ;;
  patch)       NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))" ;;
  [0-9]*.*.*)  NEW_VERSION="$BUMP" ;;
  *)
    echo "Usage: $0 <patch|minor|major|x.y.z>"
    echo "Current version: v${CURRENT}  (last tag: ${LAST_TAG})"
    exit 1
    ;;
esac

TAG="v${NEW_VERSION}"
DATE=$(date +%Y-%m-%d)

echo "Current:  ${LAST_TAG}"
echo "New:      ${TAG}"
echo ""

# ── 3. Check working tree is clean ───────────────────────────────────────────
if ! git diff --quiet || ! git diff --staged --quiet; then
  echo "ERROR: Working tree has uncommitted changes. Commit or stash first."
  exit 1
fi

# ── 4. Collect commits since last tag ────────────────────────────────────────
COMMITS=$(git log "${LAST_TAG}..HEAD" --oneline --no-decorate)

if [ -z "$COMMITS" ]; then
  echo "ERROR: No commits since ${LAST_TAG}. Nothing to release."
  exit 1
fi

# Bucket by conventional-commit prefix
section() {
  echo "$COMMITS" | grep -E "^[0-9a-f]+ ${1}" \
    | sed -E "s/^[0-9a-f]+ ${1}[^:]*: /- /" || true
}

FEATS=$(section "feat")
FIXES=$(section "fix")
DOCS=$(section "docs")
CHORES=$(echo "$COMMITS" \
  | grep -E "^[0-9a-f]+ (chore|build|refactor|perf|test|ci)" \
  | sed 's/^[0-9a-f]* /- /' || true)

# ── 5. Build changelog entry ──────────────────────────────────────────────────
ENTRY="## [${NEW_VERSION}] — ${DATE}"$'\n'
[ -n "$FEATS" ]  && ENTRY+=$'\n### Added\n'"$FEATS"$'\n'
[ -n "$FIXES" ]  && ENTRY+=$'\n### Fixed\n'"$FIXES"$'\n'
[ -n "$DOCS" ]   && ENTRY+=$'\n### Docs\n'"$DOCS"$'\n'
[ -n "$CHORES" ] && ENTRY+=$'\n### Chores\n'"$CHORES"$'\n'

echo "──────────────────────────────────────────"
echo "$ENTRY"
echo "──────────────────────────────────────────"
read -r -p "Prepend to ${CHANGELOG} and tag ${TAG}? [y/N] " CONFIRM
[[ "$CONFIRM" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

# ── 6. Update CHANGELOG.md ───────────────────────────────────────────────────
if [ ! -s "$CHANGELOG" ]; then
  printf '# Changelog\n\nAll notable changes are documented here.\n\n%s\n' "$ENTRY" > "$CHANGELOG"
else
  TMP=$(mktemp)
  awk -v entry="$ENTRY" '
    /^## \[/ && !inserted { print entry; print ""; inserted=1 }
    { print }
    END { if (!inserted) { print ""; print entry } }
  ' "$CHANGELOG" > "$TMP"
  mv "$TMP" "$CHANGELOG"
fi

git add "$CHANGELOG"
git commit -m "chore(release): ${TAG}"

# ── 7. Annotated tag ─────────────────────────────────────────────────────────
git tag -a "$TAG" -m "Release ${TAG}"

echo ""
echo "Tagged ${TAG}. Push with:"
echo "  git push origin ${TAG}"
