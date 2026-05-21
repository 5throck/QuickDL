# scripts/sync-md.ps1
# PostToolUse hook wrapper — runs audit.ps1 after every Write/Edit (PowerShell).

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent

Write-Host "--- Post-Edit Audit Hook ---"
& "$ScriptDir\audit.ps1"
exit $LASTEXITCODE
