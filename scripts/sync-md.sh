#!/usr/bin/env bash
# scripts/sync-md.sh
# PostToolUse hook wrapper — runs audit.sh after every Write/Edit.
# Cross-platform: executed inside bash context on all platforms.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "--- Post-Edit Audit Hook ---"
bash "$SCRIPT_DIR/audit.sh"
exit $?
