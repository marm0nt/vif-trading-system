@echo off
REM ============================================================
REM  VIF BRAIN SYNC — Global Cross-Device Synchronization
REM  Implements the claude-brain + atxtechbro pattern:
REM  "Spilled Coffee Principle" — destroy any machine, be back
REM  up and running that afternoon with full AI context intact.
REM
REM  Syncs EVERYTHING:
REM    - All project code
REM    - .claude/memory/   (AI learned context)
REM    - .claude/skills/   (custom skill definitions)
REM    - .claude/agents/   (agent configurations)
REM    - .claude/hooks/    (automation hooks)
REM    - .claude/settings.json (shared settings)
REM    - CLAUDE.md         (persistent instructions)
REM    - config/           (VIF framework parameters)
REM    - watchlists/       (ticker lists)
REM
REM  Does NOT sync (machine-local):
REM    - .env              (contains your API key)
REM    - .claude/settings.local.json
REM    - data/ logs/ reports/ (regenerated automatically)
REM    - venv/             (reinstall with pip install -r requirements.txt)
REM ============================================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════╗
echo ║       VIF BRAIN SYNC  ·  %COMPUTERNAME%
echo ╚══════════════════════════════════════════════╝
echo.

REM ── Step 1: Verify git repo ──────────────────────────────────
git rev-parse --git-dir >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Not inside a git repository.
    echo         Make sure you run this from C:\Users\marti\vif-trading-system
    pause & exit /b 1
)

REM ── Step 2: Stage and commit ALL changes (code + brain) ──────
echo [1/4] Checking for uncommitted changes...
git add -A
git diff --cached --quiet
if %errorlevel% neq 0 (
    echo       Found changes — committing brain snapshot...
    for /f "tokens=1-3 delims=/ " %%a in ("%DATE%") do set DSTAMP=%%c-%%a-%%b
    for /f "tokens=1-2 delims=: " %%a in ("%TIME%") do set TSTAMP=%%a:%%b
    git commit -m "brain-sync: %COMPUTERNAME% snapshot %DSTAMP% %TSTAMP%"
    echo       [OK] Committed.
) else (
    echo       [OK] Nothing to commit.
)
echo.

REM ── Step 3: Fetch + pull from GitHub ─────────────────────────
echo [2/4] Fetching from GitHub...
git fetch origin 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Cannot reach GitHub. Check internet connection.
    pause & exit /b 1
)

for /f %%i in ('git rev-list HEAD..origin/main --count 2^>nul') do set BEHIND=%%i
if !BEHIND! gtr 0 (
    echo       Pulling !BEHIND! new commit(s) from GitHub...
    git pull --rebase origin main
    if %errorlevel% neq 0 (
        echo [ERROR] Rebase conflict detected. Resolve manually:
        echo         git status  — see conflicting files
        echo         git rebase --abort  — to cancel and start over
        pause & exit /b 1
    )
    echo       [OK] Pulled !BEHIND! commits.
) else (
    echo       [OK] Already up to date with GitHub.
)
echo.

REM ── Step 4: Push to GitHub ───────────────────────────────────
echo [3/4] Pushing to GitHub...
for /f %%i in ('git rev-list origin/main..HEAD --count 2^>nul') do set AHEAD=%%i
if !AHEAD! gtr 0 (
    git push origin main
    if %errorlevel% neq 0 (
        echo [ERROR] Push failed. See above for details.
        pause & exit /b 1
    )
    echo       [OK] Pushed !AHEAD! commit(s).
) else (
    echo       [OK] Nothing to push.
)
echo.

REM ── Step 5: Status report ────────────────────────────────────
echo [4/4] Brain sync status:
echo.
echo       Machine:  %COMPUTERNAME%
echo       Branch:   main
for /f %%i in ('git log --oneline -1 --format^=%%H') do set HASH=%%i
for /f "delims=" %%i in ('git log --oneline -1 --format^=%%s') do set MSG=%%i
echo       Latest:   %HASH:~0,8% — %MSG%
echo.

REM ── Count what's synced ───────────────────────────────────────
for /f %%i in ('git ls-files .claude\memory\ 2^>nul ^| find /c /v ""') do set MEM_COUNT=%%i
for /f %%i in ('git ls-files .claude\skills\ 2^>nul ^| find /c /v ""') do set SKILL_COUNT=%%i
for /f %%i in ('git ls-files .claude\agents\ 2^>nul ^| find /c /v ""') do set AGENT_COUNT=%%i

echo       Synced brain:
echo         Memory files:  !MEM_COUNT!
echo         Skills:        !SKILL_COUNT!
echo         Agents:        !AGENT_COUNT!
echo.
echo ╔══════════════════════════════════════════════╗
echo ║  Brain sync complete. Both devices are now  ║
echo ║  running identical context + code.          ║
echo ╚══════════════════════════════════════════════╝
echo.
echo  On your OTHER device, run:
echo    git pull origin main
echo  That's it — full brain transferred.
echo.
pause
