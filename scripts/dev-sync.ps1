# scripts/dev-sync.ps1 — QuickDL full sync pipeline (PowerShell)
# Usage: .\scripts\dev-sync.ps1 "feat: description"

param(
    [Parameter(Mandatory=$false)]
    [string]$Message = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = Read-Host "Enter commit message (e.g., feat: add feature)"
}
if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-Error "Error: Commit message is required."
    exit 1
}

# ── 1. Audit ─────────────────────────────────────────────────────────────────
Write-Host "==> Running audit..."
& "$PSScriptRoot\audit.ps1"
if ($LASTEXITCODE -ne 0) { exit 1 }

# ── 2. Ensure today's memory log exists ──────────────────────────────────────
$today = Get-Date -Format "yyyy-MM-dd"
$logFile = "memory\$today.md"
New-Item -ItemType Directory -Force -Path "memory" | Out-Null

if (-not (Test-Path $logFile)) {
    $time = Get-Date -Format "HH:mm"
    @"
# Development Log — $today

<!-- Auto-created by dev-sync.ps1. Fill in entries below. -->

## $time — Session

<!-- Describe what was done today -->
"@ | Set-Content -Path $logFile -Encoding UTF8
    Write-Host "==> Created $logFile"
}

# ── 3. Update MEMORY.md index (insert after separator row) ───────────────────
$indexFile = "memory\MEMORY.md"
if ((Test-Path $indexFile) -and -not (Select-String -Path $indexFile -Pattern ([regex]::Escape($today)) -Quiet)) {
    $summary = ($Message -replace '^[^:]+:\s*', '')
    $newEntry = "| [$today]($today.md) | $summary |"
    $lines = Get-Content $indexFile
    $output = @()
    foreach ($line in $lines) {
        $output += $line
        if ($line -match '^\|[-| ]+\|$') {
            $output += $newEntry
        }
    }
    $output | Set-Content -Path $indexFile -Encoding UTF8
    Write-Host "==> Updated MEMORY.md"
}

# ── 4. Stage and commit ──────────────────────────────────────────────────────
Write-Host "==> Committing..."
git add -A
$commitMsg = "$Message"
git commit -m $commitMsg

# ── 5. Branch strategy ───────────────────────────────────────────────────────
$branch = git branch --show-current
$baseBranch = $branch

if ($branch -eq "master" -or $branch -eq "main") {
    $slug = $Message.ToLower() -replace '[^a-z0-9]', '-' -replace '-+', '-' -replace '^-|-$', ''
    $slug = $slug.Substring(0, [Math]::Min(40, $slug.Length))
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $prBranch = "pr/$timestamp-$slug"

    Write-Host "==> Creating PR branch: $prBranch"
    $commitHash = git rev-parse HEAD
    git checkout -b $prBranch $commitHash
    git checkout $baseBranch
    git reset --hard HEAD~1
    git checkout $prBranch
    $branch = $prBranch
}

# ── 6. Push ──────────────────────────────────────────────────────────────────
Write-Host "==> Pushing $branch..."
git push -u origin $branch

# ── 7. Create PR (skip if already exists) ────────────────────────────────────
$existingPr = gh pr view --json number -q '.number' 2>$null
if ($existingPr) {
    Write-Host "==> PR #$existingPr already exists — skipping creation."
    gh pr view --json url -q '.url'
} else {
    $body = "## Summary`n`n- $Message`n`n## Test Plan`n`n- [ ] ``bash scripts/audit.sh`` passes`n- [ ] Tests pass`n`n:robot: Generated with AI Assistant"
    Write-Host "==> Opening PR..."
    gh pr create --title $Message --body $body --base $baseBranch --head $branch
}

Write-Host "==> Done."
