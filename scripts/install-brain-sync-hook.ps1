# ============================================================
# VIF Brain Sync — Hook Installer
# Run once on each device to install the post-commit auto-push hook.
# After this, every git commit automatically pushes to GitHub.
# ============================================================

$repoRoot = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "VIF Brain Sync — Hook Installer" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check we're in the right place
if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Host "[ERROR] Not a git repository: $repoRoot" -ForegroundColor Red
    exit 1
}

# As of Phase 1 fix (May 15, 2026), post-commit is already wired in .githooks/post-commit
# which is the active hook path (core.hooksPath=.githooks). This script is now a no-op.
# It remains for historical reference and to document the migration from .git/hooks to .githooks.

Write-Host "[INFO] post-commit auto-push is already configured in .githooks/" -ForegroundColor Green
Write-Host "[INFO] Active hook path: core.hooksPath=.githooks" -ForegroundColor Green
Write-Host ""
Write-Host "To sync hooks to a new device:" -ForegroundColor Yellow
Write-Host "  git pull origin main" -ForegroundColor White
Write-Host ""
Write-Host "No further action needed. Every 'git commit' will auto-push." -ForegroundColor Green
Write-Host ""
