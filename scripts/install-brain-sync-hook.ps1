# ============================================================
# VIF Brain Sync — Hook Installer
# Run once on each device to install the post-commit auto-push hook.
# After this, every git commit automatically pushes to GitHub.
# ============================================================

$repoRoot = Split-Path $PSScriptRoot -Parent
$hooksDir = Join-Path $repoRoot ".git\hooks"
$hookSource = Join-Path $repoRoot ".claude\hooks\post-commit-sync.sh"
$hookDest = Join-Path $hooksDir "post-commit"

Write-Host ""
Write-Host "VIF Brain Sync — Hook Installer" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check we're in the right place
if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Host "[ERROR] Not a git repository: $repoRoot" -ForegroundColor Red
    exit 1
}

# Copy hook into place
Copy-Item $hookSource $hookDest -Force
Write-Host "[OK] post-commit hook installed at: $hookDest" -ForegroundColor Green

# On Windows, git hooks need to be executable — set via git config
& git -C $repoRoot config core.hooksPath ".git/hooks"
Write-Host "[OK] Git hooks path configured." -ForegroundColor Green

Write-Host ""
Write-Host "From now on, every 'git commit' will automatically push" -ForegroundColor Yellow
Write-Host "to GitHub in the background. Your brain stays in sync."  -ForegroundColor Yellow
Write-Host ""
Write-Host "Run this script on BOTH devices to complete setup." -ForegroundColor White
Write-Host ""
