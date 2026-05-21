#!/usr/bin/env bash
# scripts/dev-sync.sh — QuickDL full sync pipeline
# Usage: bash scripts/dev-sync.sh "feat: description"
#
# Pipeline:
#   1. audit.sh          — abort on failure
#   2. memory/YYYY-MM-DD.md — auto-create if missing
#   3. MEMORY.md index   — awk insertion after header row
#   4. git add + commit
#   5. On master/main → create pr/<date>-<slug> branch, reset master to HEAD~1
#   6. git push + gh pr create (skip if PR already exists)

set -euo pipefail
cd "$(dirname "$0")/.."

MSG="${1:-}"
if [[ -z "$MSG" ]]; then
  echo -n "Enter commit message (e.g., feat: add feature): "
  read -r MSG
fi
if [[ -z "$MSG" ]]; then
  echo "Error: Commit message is required." >&2
  exit 1
fi

# ── 1. Audit ─────────────────────────────────────────────────────────────────
echo "==> Running audit..."
bash scripts/audit.sh

# ── 2. Ensure today's memory log exists ──────────────────────────────────────
TODAY=$(date +%Y-%m-%d)
LOGFILE="memory/${TODAY}.md"
mkdir -p memory

if [[ ! -f "$LOGFILE" ]]; then
  cat > "$LOGFILE" <<TEMPLATE
# Development Log — ${TODAY}

<!-- Auto-created by dev-sync.sh. Fill in entries below. -->

## $(date '+%H:%M') — Session

<!-- Describe what was done today -->
TEMPLATE
  echo "==> Created $LOGFILE"
fi

# ── 3. Update MEMORY.md index (awk: insert after separator row) ───────────────
INDEX="memory/MEMORY.md"
if [[ -f "$INDEX" ]] && ! grep -q "\[${TODAY}\]" "$INDEX"; then
  SUMMARY="${MSG#*: }"   # strip "type: " prefix for the summary
  NEW_ENTRY="| [${TODAY}](${TODAY}.md) | ${SUMMARY} |"
  awk -v entry="$NEW_ENTRY" '
    /^\|[-| ]+\|$/ { print; print entry; next }
    { print }
  ' "$INDEX" > "$INDEX.tmp" && mv "$INDEX.tmp" "$INDEX"
  echo "==> Updated MEMORY.md"
fi

# ── 4. Stage and commit ──────────────────────────────────────────────────────
echo "==> Committing..."
git add -A
git commit -m "${MSG}

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# ── 5. Branch strategy: PR branch from master ────────────────────────────────
BRANCH=$(git branch --show-current)
BASE_BRANCH="$BRANCH"

if [[ "$BRANCH" == "master" || "$BRANCH" == "main" ]]; then
  SLUG=$(echo "$MSG" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-40)
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  PR_BRANCH="pr/${TIMESTAMP}-${SLUG}"

  echo "==> Creating PR branch: $PR_BRANCH"
  COMMIT_HASH=$(git rev-parse HEAD)
  git checkout -b "$PR_BRANCH" "$COMMIT_HASH"
  git checkout "$BASE_BRANCH"
  git reset --hard HEAD~1
  git checkout "$PR_BRANCH"
  BRANCH="$PR_BRANCH"
fi

# ── 6. Push ──────────────────────────────────────────────────────────────────
echo "==> Pushing $BRANCH..."
git push -u origin "$BRANCH"

# ── 7. Create PR (skip if already exists) ────────────────────────────────────
EXISTING_PR=$(gh pr view --json number -q '.number' 2>/dev/null || true)
if [[ -n "$EXISTING_PR" ]]; then
  echo "==> PR #${EXISTING_PR} already exists — skipping creation."
  gh pr view --json url -q '.url'
else
  COMMITS=$(git log "${BASE_BRANCH}..HEAD" --pretty=format:"- %s" 2>/dev/null | head -20 || git log -1 --pretty=format:"- %s")
  echo "==> Opening PR..."
  gh pr create \
    --title "$MSG" \
    --body "$(printf "## Summary\n\n%s\n\n## Test Plan\n\n- [ ] \`bash scripts/audit.sh\` passes\n- [ ] \`pytest test_i18n.py -v\` passes\n- [ ] \`python test_app.py\` passes\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)" "$COMMITS")" \
    --base "$BASE_BRANCH" \
    --head "$BRANCH"
fi

echo "==> Done."
