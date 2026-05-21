# scripts/audit.ps1 — QuickDL quality gate (PowerShell)
# Runs automatically via PostToolUse hook after Write/Edit (Windows).
# Also called by dev-sync.ps1 before committing.

Set-StrictMode -Version Latest
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$fail = $false
Write-Host "--- Documentation Audit ---"

# ── 1. CHANGELOG.md must exist ──────────────────────────────────────────────
if (-not (Test-Path "CHANGELOG.md")) {
    Write-Host "  [!] CHANGELOG.md not found — run /changelog to create it"
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
        print(f"  [!] {p.name}: missing={missing} extra={extra}")
        failed = True
sys.exit(1 if failed else 0)
'@
$tmpFile = [System.IO.Path]::GetTempFileName() + ".py"
Set-Content -Path $tmpFile -Value $pyScript -Encoding UTF8
try {
    $output = python $tmpFile 2>&1
    if ($output) { Write-Host $output }
    if ($LASTEXITCODE -ne 0) { $fail = $true }
} finally {
    Remove-Item $tmpFile -ErrorAction SilentlyContinue
}

# ── 3. Absolute path check ────────────────────────────────────────────────────
$mdFiles = Get-ChildItem -Recurse -Filter "*.md" | Where-Object {
    $_.FullName -notmatch "node_modules|\.git|\.claude|\.venv|CLAUDE\.md|GEMINI\.md"
}
foreach ($f in $mdFiles) {
    $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match '[A-Z]:\\|/Users/|/home/') {
        Write-Host "  [!] Absolute path detected in $($f.Name)"
        $fail = $true
    }
}

# ── 4. Script pairing check ───────────────────────────────────────────────────
Get-ChildItem scripts -File | ForEach-Object {
    $base = $_.BaseName
    $ext  = $_.Extension
    if ($ext -eq ".sh" -and -not (Test-Path "scripts\$base.ps1")) {
        Write-Host "  [!] Missing .ps1 pair for scripts\$base.sh"
        $fail = $true
    }
    elseif ($ext -eq ".ps1" -and -not (Test-Path "scripts\$base.sh")) {
        Write-Host "  [!] Missing .sh pair for scripts\$base.ps1"
        $fail = $true
    }
}

# ── Result ───────────────────────────────────────────────────────────────────
if ($fail) {
    Write-Host "Audit FAILED."
    exit 1
}

Write-Host "Audit PASSED."
exit 0
