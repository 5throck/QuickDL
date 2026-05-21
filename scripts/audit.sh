#!/usr/bin/env bash
# scripts/audit.sh — QuickDL quality gate
# Runs automatically via PostToolUse hook (sync-md.sh wrapper) after Write/Edit.
# Also called by dev-sync.sh before committing.
# Exit code non-zero → abort commit.
# Intentionally omits 'set -e' — runs all checks to report every issue at once.

cd "$(dirname "$0")/.."

FAIL=0
echo "--- Documentation Audit ---"

# ── 1. CHANGELOG.md must exist ──────────────────────────────────────────────
if [[ ! -f CHANGELOG.md ]]; then
  echo "  [!] CHANGELOG.md not found — run /changelog to create it"
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
        print(f"  [!] {p.name}: missing={missing} extra={extra}")
        failed = True
sys.exit(1 if failed else 0)
PYEOF
  )
  if [[ -n "$RESULT" ]]; then
    echo "$RESULT"
    FAIL=1
  fi
fi

# ── 3. Absolute path check in markdown files ─────────────────────────────────
ABS_PATHS=$(grep -rEi "[A-Z]:\\\\|/Users/|/home/" . \
  --include="*.md" \
  | grep -vE "node_modules|\.git|\.claude|\.venv|CLAUDE\.md|GEMINI\.md|docs/superpowers" \
  2>/dev/null || true)
if [[ -n "$ABS_PATHS" ]]; then
  echo "  [!] Absolute paths detected in docs:"
  echo "$ABS_PATHS" | head -n 5
  FAIL=1
fi

# ── 4. Broken markdown link check ────────────────────────────────────────────
while IFS= read -r file; do
  # Backslash in markdown links (Windows-only style)
  if grep -q '\[.*\](.*\\\\.*)'  "$file" 2>/dev/null; then
    echo "  [!] Backslash in link: $file — use forward slashes"
    FAIL=1
  fi

  links=$(grep -o '\[.*\]([^#)]*)' "$file" 2>/dev/null \
    | sed -E 's/.*\]\(([^# )]+)\).*/\1/' \
    | grep -vE "^http|^mailto:|^#|YYYY-MM-DD" || true)
  for link in $links; do
    decoded=$(echo "$link" | sed 's/%20/ /g')
    dir=$(dirname "$file")
    target="$dir/$decoded"
    if [[ ! -e "$target" ]]; then
      echo "  [!] Broken link in $file → $link"
      FAIL=1
    fi
  done
done < <(find . -name "*.md" \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/.claude/*" \
  -not -path "*/.venv/*" \
  -not -path "*/docs/superpowers/*" \
  2>/dev/null)

# ── 5. Script pairing check (.sh must have .ps1 and vice versa) ──────────────
for script in scripts/*; do
  base=$(basename "$script" | sed 's/\.[^.]*$//')
  ext="${script##*.}"
  if [[ "$ext" == "sh" ]]; then
    if [[ ! -f "scripts/${base}.ps1" ]]; then
      echo "  [!] Missing .ps1 pair for scripts/${base}.sh"
      FAIL=1
    fi
  elif [[ "$ext" == "ps1" ]]; then
    if [[ ! -f "scripts/${base}.sh" ]]; then
      echo "  [!] Missing .sh pair for scripts/${base}.ps1"
      FAIL=1
    fi
  fi
done

# ── Result ───────────────────────────────────────────────────────────────────
if [[ $FAIL -ne 0 ]]; then
  echo "Audit FAILED."
  exit 1
fi

echo "Audit PASSED."
exit 0
