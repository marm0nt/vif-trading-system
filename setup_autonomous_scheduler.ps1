# VIF Trading System - Autonomous Scheduler Setup (Windows Task Scheduler)
$ErrorActionPreference = "Stop"
$SchedulerName = "VIF-Trading-System"
$RepoPath = "C:\Users\marti\vif-trading-system"
$PythonExe = "python"

Write-Host "VIF TRADING SYSTEM - AUTONOMOUS SCHEDULER SETUP`n" -ForegroundColor Cyan

function New-VIFTask {
    param([string]$Name, [string]$Time, [int[]]$Days, [string]$Mode, [string]$Desc)

    try {
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time -DaysOfWeek $Days -ErrorAction Stop
        $action = New-ScheduledTaskAction -Execute $PythonExe -Argument "agents/orchestrator_swarm.py --mode $Mode" -WorkingDirectory $RepoPath
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -RunOnlyIfNetworkAvailable -Compatibility Win8

        Register-ScheduledTask -TaskName $Name -TaskPath "\$SchedulerName\" -Trigger $trigger -Action $action -Settings $settings -Description $Desc -User $env:USERNAME -RunLevel Highest -Force -ErrorAction Stop | Out-Null
        Write-Host "[OK] $Name ($Time)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[FAIL] $Name : $_" -ForegroundColor Red
        return $false
    }
}

$tasks = @(
    @{Name="Premarket-Catalyst-0700"; Time="07:00"; Days=@(1,2,3,4,5); Mode="premarket"; Desc="07:00 CT Catalyst Monitor"},
    @{Name="Premarket-VIF-0845"; Time="08:45"; Days=@(1,2,3,4,5); Mode="premarket"; Desc="08:45 CT VIF Analyst"},
    @{Name="MarketOpen-Swing-0935"; Time="09:35"; Days=@(1,2,3,4,5); Mode="market_open"; Desc="09:35 CT Swing Screener"},
    @{Name="AfterHours-Conviction-1605"; Time="16:05"; Days=@(1,2,3,4,5); Mode="afterhours"; Desc="16:05 CT After-Hours"},
    @{Name="Weekend-Sat-0800"; Time="08:00"; Days=@(6); Mode="weekend"; Desc="SAT 08:00 CT Catalyst"},
    @{Name="Weekend-Sun-1800"; Time="18:00"; Days=@(0); Mode="weekend"; Desc="SUN 18:00 CT Monday Prep"}
)

$count = 0
foreach ($t in $tasks) { if ((New-VIFTask $t.Name $t.Time $t.Days $t.Mode $t.Desc)) { $count++ } }

Write-Host "`nScheduler Status: $count/6 tasks created" -ForegroundColor Green
Write-Host "Command to verify:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskPath '\$SchedulerName\'" -ForegroundColor Gray
Write-Host "`nAutonomous operation ready! System will run on schedule tomorrow." -ForegroundColor Cyan
