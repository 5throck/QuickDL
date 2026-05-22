# scripts/sync-md.ps1
# PostToolUse hook wrapper — runs audit.ps1 after every Write/Edit (PowerShell).

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent

# --- Temporary file skip logic ---
$writtenFile = $env:CLAUDE_FILE_PATHS
if ($writtenFile) {
    $skipPatterns = @("scratch/", "scratch\", "memory/", "memory\",
                      "docs/specs/", "docs\specs\", "docs/plans/", "docs\plans\")
    foreach ($pattern in $skipPatterns) {
        if ($writtenFile -like "*$pattern*") {
            Write-Host "  [skip] Temporary/generated file — audit skipped: $writtenFile"
            exit 0
        }
    }
}

Write-Host "--- Post-Edit Audit Hook ---"
& "$ScriptDir\audit.ps1"
exit $LASTEXITCODE
