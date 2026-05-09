# VIF Trading System - Minimal Autonomous Scheduler Setup
# Creates one scheduled task that runs schedule_daily.py daily at 07:00 CT
# schedule_daily.py handles all internal job timing internally

$RepoPath = "C:\Users\marti\vif-trading-system"
$PythonExe = "python"
$TaskName = "VIF-Trading-System-Daily"
$TaskPath = "\VIF-Trading-System\"

Write-Host "VIF TRADING SYSTEM - AUTONOMOUS SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host ""

try {
    # Remove existing task if present
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -Force -ErrorAction Stop
        Write-Host "[OK] Removed existing task: $TaskName" -ForegroundColor Yellow
    }

    # Create daily trigger at 07:00 CT
    $trigger = New-ScheduledTaskTrigger -Daily -At 07:00

    # Action: run schedule_daily.py
    $action = New-ScheduledTaskAction -Execute $PythonExe `
        -Argument "schedule_daily.py" `
        -WorkingDirectory $RepoPath

    # Settings with auto-restart and network requirement
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 5) `
        -RunOnlyIfNetworkAvailable `
        -Compatibility Win8

    # Register task
    Register-ScheduledTask -TaskName $TaskName `
        -Trigger $trigger `
        -Action $action `
        -Settings $settings `
        -Description "VIF Trading System - Daily autonomous orchestrator (07:00 CT, internal scheduling for 08:45, 09:35, 16:05)" `
        -User $env:USERNAME `
        -RunLevel Highest `
        -Force `
        -ErrorAction Stop | Out-Null

    Write-Host "[OK] Created scheduled task: $TaskName" -ForegroundColor Green
    Write-Host "     Time: 07:00 CT Daily" -ForegroundColor Green
    Write-Host "     Command: python schedule_daily.py" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task will run schedule_daily.py which internally handles:" -ForegroundColor Cyan
    Write-Host "  - 07:00 CT: Catalyst monitor + VIF analysis + swing screener" -ForegroundColor Gray
    Write-Host "  - 08:45 CT: VIF analysis only" -ForegroundColor Gray
    Write-Host "  - 09:35 CT: Swing screener only" -ForegroundColor Gray
    Write-Host "  - 16:05 CT: After-hours conviction analysis" -ForegroundColor Gray
    Write-Host "  - 08:00 SAT: Weekend macro briefing" -ForegroundColor Gray
    Write-Host "  - 18:00 SUN: Monday preparation analysis" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Verify installation:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Autonomous operation enabled! System ready for tomorrow at 07:00 CT." -ForegroundColor Cyan

} catch {
    Write-Host "[FAIL] Setup failed: $_" -ForegroundColor Red
    exit 1
}
