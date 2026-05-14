@echo off
REM ============================================================
REM  VIF Trading System — GitHub Sync Script
REM  Run this at the START and END of every work session.
REM  Works on both desktop and laptop.
REM ============================================================

cd /d "%~dp0"

echo.
echo ========================================
echo  VIF Trading System — GitHub Sync
echo ========================================
echo.

REM --- 1. Check for uncommitted local changes ---
git status --short > nul 2>&1
git diff --quiet --exit-code 2>nul
if %errorlevel% neq 0 (
    echo [!] You have uncommitted changes. Committing them now...
    git add -A
    git commit -m "sync: auto-commit local changes on %COMPUTERNAME% (%DATE% %TIME%)"
    echo [OK] Changes committed.
) else (
    git status --short | findstr /r "." > nul 2>&1
    if %errorlevel% equ 0 (
        echo [!] You have staged/untracked files. Committing them now...
        git add -A
        git commit -m "sync: auto-commit local changes on %COMPUTERNAME% (%DATE% %TIME%)"
        echo [OK] Changes committed.
    ) else (
        echo [OK] No uncommitted changes.
    )
)

echo.

REM --- 2. Fetch latest from GitHub ---
echo [>>] Fetching latest from GitHub...
git fetch origin
if %errorlevel% neq 0 (
    echo [ERROR] Could not reach GitHub. Check your internet connection.
    pause
    exit /b 1
)
echo [OK] Fetch complete.
echo.

REM --- 3. Check if we need to pull or push ---
for /f %%i in ('git rev-list HEAD..origin/main --count 2^>nul') do set BEHIND=%%i
for /f %%i in ('git rev-list origin/main..HEAD --count 2^>nul') do set AHEAD=%%i

echo [i] Status: %AHEAD% commit(s) ahead, %BEHIND% commit(s) behind origin/main
echo.

REM --- 4. Pull if behind ---
if %BEHIND% gtr 0 (
    echo [>>] Pulling %BEHIND% new commit(s) from GitHub...
    git pull --rebase origin main
    if %errorlevel% neq 0 (
        echo [ERROR] Pull failed. You may have conflicts to resolve manually.
        echo         Run: git status
        pause
        exit /b 1
    )
    echo [OK] Pull complete.
    echo.
)

REM --- 5. Push if ahead ---
for /f %%i in ('git rev-list origin/main..HEAD --count 2^>nul') do set AHEAD=%%i
if %AHEAD% gtr 0 (
    echo [>>] Pushing %AHEAD% commit(s) to GitHub...
    git push origin main
    if %errorlevel% neq 0 (
        echo [ERROR] Push failed. See error above.
        pause
        exit /b 1
    )
    echo [OK] Push complete.
    echo.
) else (
    echo [OK] Nothing to push - already up to date.
    echo.
)

echo ========================================
echo  Sync complete! Both devices are now
echo  on the same version.
echo ========================================
echo.
pause
