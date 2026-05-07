# Setup git hooks for auto-syncing IDE settings on pull

$hookSource = ".\scripts\git-hooks\post-merge"
$hookDest = ".\.git\hooks\post-merge"

if (Test-Path $hookSource) {
    Copy-Item $hookSource $hookDest -Force
    Write-Host "✓ Git hook installed: post-merge will auto-sync IDE settings on pull"
} else {
    Write-Host "✗ Hook source not found: $hookSource"
}
