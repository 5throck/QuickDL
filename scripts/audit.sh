#!/usr/bin/env bash
# audit.sh — QuickDL quality gate
# Runs automatically via PostToolUse hook after Write/Edit.
# Also called by dev-sync.sh before committing.
# Exit code non-zero → abort commit.

set -euo pipefail
cd "$(dirname "$0")/.."

FAIL=0

# ── 1. CHANGELOG.md must exist ──────────────────────────────────────────────
if [[ ! -f CHANGELOG.md ]]; then
  echo "[audit] FAIL: CHANGELOG.md not found" >&2
  FAIL=1
fi

# ── 2. locales/ key parity (all files must match en.json) ───────────────────
if command -v python &>/dev/null || command -v python3 &>/dev/null; then
  PY=$(command -v python3 2>/dev/null || command -v python)
  RESULT=$($PY - <<'PYEOF'
import json, pathlib, sys
base_path = pathlib.Path("locales/en.json")
if not base_path.exists():
    print("SKIP: locales/en.json not found")
    sys.exit(0)
base = json.loads(base_path.read_text(encoding="utf-8"))
failed = False
for p in sorted(pathlib.Path("locales").glob("*.json")):
    other = json.loads(p.read_text(encoding="utf-8"))
    missing = set(base) - set(other)
    extra   = set(other) - set(base)
    if missing or extra:
        print(f"FAIL: {p.name} — missing={missing} extra={extra}")
        failed = True
    else:
        print(f"OK:   {p.name}")
sys.exit(1 if failed else 0)
PYEOF
  )
  echo "$RESULT"
  if echo "$RESULT" | grep -q "^FAIL"; then
    FAIL=1
  fi
fi

# ── Result ───────────────────────────────────────────────────────────────────
if [[ $FAIL -ne 0 ]]; then
  echo "[audit] FAILED — fix issues above before committing" >&2
  exit 1
fi

echo "[audit] OK"
exit 0
