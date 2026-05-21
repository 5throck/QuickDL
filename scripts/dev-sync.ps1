# dev-sync.ps1 — QuickDL full sync pipeline (PowerShell)
# Usage: .\scripts\dev-sync.ps1 "feat: description"
#
# Pipeline:
#   1. audit.ps1         — abort on failure
#   2. memory/YYYY-MM-DD.md — auto-create if missing
#   3. MEMORY.md index   — update entry
#   4. git add + commit
#   5. On master/main → create pr/<date>-<slug> branch, reset master to HEAD~1
#   6. git push + gh pr create

param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

# ── 1. Audit ─────────────────────────────────────────────────────────────────
Write-Host "==> Running audit..."
& "$PSScriptRoot\audit.ps1"
if ($LASTEXITCODE -ne 0) { exit 1 }

# ── 2. Ensure today's memory log exists ──────────────────────────────────────
$today = Get-Date -Format "yyyy-MM-dd"
$logFile = "memory\$today.md"
New-Item -ItemType Directory -Force -Path "memory" | Out-Null

if (-not (Test-Path $logFile)) {
    @"
## $today — Development Log

<!-- Fill in: Files, Purpose, Decisions, Issues -->

## Session Summary
- **Files**:
- **Purpose**:
- **Decisions**:
- **Issues**:
"@ | Set-Content -Path $logFile -Encoding UTF8
    Write-Host "==> Created $logFile"
}

# ── 3. Update MEMORY.md index ─────────────────────────────────────────────────
$memoryIndex = "memory\MEMORY.md"
if (Test-Path $memoryIndex) {
    $content = Get-Content $memoryIndex -Raw
    if ($content -notmatch [regex]::Escape($today)) {
        Add-Content -Path $memoryIndex -Value "| [$today]($today.md) | $Message |"
        Write-Host "==> Updated MEMORY.md"
    }
}

# ── 4. Stage and commit ──────────────────────────────────────────────────────
Write-Host "==> Staging changes..."
git add -A
$commitMsg = "$Message`n`nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git commit -m $commitMsg

# ── 5. Branch strategy: PR branch from master ────────────────────────────────
$branch = git branch --show-current
if ($branch -eq "master" -or $branch -eq "main") {
    $slug = $Message -replace '[^a-zA-Z0-9]', '-' `
                     -replace '-+', '-' `
                     -replace '^-|-$', ''
    $slug = $slug.ToLower().Substring(0, [Math]::Min(40, $slug.Length))
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $prBranch = "pr/$timestamp-$slug"

    Write-Host "==> Creating PR branch: $prBranch"
    git checkout -b $prBranch
    git checkout $branch
    git reset --hard HEAD~1

    # ── 6. Push PR branch and open PR ───────────────────────────────────────
    git checkout $prBranch
    git push -u origin $prBranch

    $body = "## Summary`n`n- $Message`n`n## Test Plan`n`n- [ ] Tests pass`n- [ ] i18n audit clean`n`n:robot: Generated with [Claude Code](https://claude.com/claude-code)"
    Write-Host "==> Opening PR..."
    gh pr create --title $Message --body $body
} else {
    git push
}

Write-Host "==> Done."
