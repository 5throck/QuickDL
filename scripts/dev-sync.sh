#!/usr/bin/env bash
# dev-sync.sh — QuickDL full sync pipeline
# Usage: bash scripts/dev-sync.sh "feat: description"
#
# Pipeline:
#   1. audit.sh          — abort on failure
#   2. memory/YYYY-MM-DD.md — auto-create if missing
#   3. MEMORY.md index   — update entry
#   4. git add + commit
#   5. On master/main → create pr/<date>-<slug> branch, reset master to HEAD~1
#   6. git push + gh pr create

set -euo pipefail
cd "$(dirname "$0")/.."

MSG="${1:-}"
if [[ -z "$MSG" ]]; then
  echo "Usage: bash scripts/dev-sync.sh \"<commit message>\"" >&2
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
## $(date +%Y-%m-%d) — Development Log

<!-- Fill in: Files, Purpose, Decisions, Issues -->

## Session Summary
- **Files**:
- **Purpose**:
- **Decisions**:
- **Issues**:
TEMPLATE
  echo "==> Created $LOGFILE"
fi

# ── 3. Update MEMORY.md index ─────────────────────────────────────────────────
SUMMARY="${MSG}"
if ! grep -q "$TODAY" memory/MEMORY.md 2>/dev/null; then
  # Append new entry after the header line
  sed -i "s|^| |; 1s|^ ||" memory/MEMORY.md 2>/dev/null || true
  echo "| [${TODAY}](${TODAY}.md) | ${SUMMARY} |" >> memory/MEMORY.md
  echo "==> Updated MEMORY.md"
fi

# ── 4. Stage and commit ──────────────────────────────────────────────────────
echo "==> Staging changes..."
git add -A
git commit -m "${MSG}

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# ── 5. Branch strategy: PR branch from master ────────────────────────────────
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "master" || "$BRANCH" == "main" ]]; then
  SLUG=$(echo "$MSG" | sed 's/[^a-zA-Z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-40 | tr '[:upper:]' '[:lower:]')
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  PR_BRANCH="pr/${TIMESTAMP}-${SLUG}"

  echo "==> Creating PR branch: $PR_BRANCH"
  git checkout -b "$PR_BRANCH"
  git checkout "$BRANCH"
  git reset --hard HEAD~1

  # ── 6. Push PR branch and open PR ───────────────────────────────────────
  git checkout "$PR_BRANCH"
  git push -u origin "$PR_BRANCH"

  echo "==> Opening PR..."
  gh pr create \
    --title "$MSG" \
    --body "$(printf "## Summary\n\n- %s\n\n## Test Plan\n\n- [ ] Tests pass\n- [ ] i18n audit clean\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)" "$MSG")"
else
  git push
fi

echo "==> Done."
