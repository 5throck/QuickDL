# audit.ps1 — QuickDL quality gate (PowerShell)
# Runs automatically via PostToolUse hook after Write/Edit (Windows).
# Also called by dev-sync.ps1 before committing.
# Exit code non-zero → abort commit.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$fail = $false

# ── 1. CHANGELOG.md must exist ──────────────────────────────────────────────
if (-not (Test-Path "CHANGELOG.md")) {
    Write-Error "[audit] FAIL: CHANGELOG.md not found"
    $fail = $true
}

# ── 2. locales/ key parity ───────────────────────────────────────────────────
$pyScript = @'
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
        print(f"FAIL: {p.name} - missing={missing} extra={extra}")
        failed = True
    else:
        print(f"OK:   {p.name}")
sys.exit(1 if failed else 0)
'@

$tmpFile = [System.IO.Path]::GetTempFileName() + ".py"
Set-Content -Path $tmpFile -Value $pyScript -Encoding UTF8
try {
    $output = python $tmpFile 2>&1
    Write-Host $output
    if ($output -match "^FAIL") {
        $fail = $true
    }
} finally {
    Remove-Item $tmpFile -ErrorAction SilentlyContinue
}

# ── Result ───────────────────────────────────────────────────────────────────
if ($fail) {
    Write-Error "[audit] FAILED — fix issues above before committing"
    exit 1
}

Write-Host "[audit] OK"
exit 0
