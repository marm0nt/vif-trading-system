#!/bin/bash
# ============================================================
# VIF Brain — post-commit auto-push hook
# Implements the atxtechbro "Global Configuration Bias" principle:
# every commit automatically syncs to GitHub so no device
# can ever fall behind by 670 commits again.
#
# Install: copy to .git/hooks/post-commit (chmod +x)
# Or run:  scripts/setup_hooks.ps1
# ============================================================

# Push quietly in the background — don't block the terminal
(git push origin main --quiet 2>&1 | while IFS= read -r line; do
    echo "[brain-sync] $line"
done) &

exit 0
