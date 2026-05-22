#!/usr/bin/env bash
# scripts/sync-md.sh
# PostToolUse hook wrapper — runs audit.sh after every Write/Edit.
# Cross-platform: executed inside bash context on all platforms.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Temporary file skip logic ---
WRITTEN_FILE="${CLAUDE_FILE_PATHS:-}"
if [ -n "$WRITTEN_FILE" ]; then
  SKIP_PATTERNS=("scratch/" "memory/" "docs/superpowers/")
  for pattern in "${SKIP_PATTERNS[@]}"; do
    if [[ "$WRITTEN_FILE" == *"$pattern"* ]]; then
      echo "  [skip] Temporary/generated file — audit skipped: $WRITTEN_FILE"
      exit 0
    fi
  done
fi

echo "--- Post-Edit Audit Hook ---"
bash "$SCRIPT_DIR/audit.sh"
exit $?
