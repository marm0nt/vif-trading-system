#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated startup script for VIF Trading System with TradingView CDP + MCP integration.

.DESCRIPTION
    Phase 2 of super-agent implementation: Autonomously launches TradingView Desktop,
    enables Chrome DevTools Protocol (CDP), initializes MCP servers, and runs the
    scheduled VIF analysis pipeline.

    Usage:
      .\start_vif.ps1                    # Full startup (TradingView + MCP + pipeline)
      .\start_vif.ps1 -NoTV              # Skip TradingView launch
      .\start_vif.ps1 -NoMCP             # Skip MCP server init
      .\start_vif.ps1 -DryRun            # Show what would execute without running

.PARAMETER NoTV
    Skip TradingView Desktop launch (assumes already running).

.PARAMETER NoMCP
    Skip MCP server initialization (assumes already running).

.PARAMETER DryRun
    Show startup sequence without executing commands.

.PARAMETER Mode
    Pipeline mode: 'premarket' (default), 'market_open', 'afterhours', 'weekend', 'full'

.EXAMPLE
    .\start_vif.ps1 -Mode premarket

.NOTES
    Requires:
    - Python 3.11+ with swarm + orchestrator framework
    - TradingView Desktop (auto-launches if not running)
    - VS Code with MCP server support (optional, for manual MCP launch)
#>

param(
    [switch] $NoTV,
    [switch] $NoMCP,
    [switch] $DryRun,
    [ValidateSet('premarket', 'market_open', 'afterhours', 'weekend', 'full')]
    [string] $Mode = 'premarket'
)

# ─── Setup ────────────────────────────────────────────────────────────────────
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$repoRoot = Split-Path -Parent $PSCommandPath
$tvPath = "$env:APPDATA\..\Local\Programs\TradingView\TradingView.exe"
$cdpPort = 9222
$mcpPort = 3001
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = "$repoRoot\logs\startup_$timestamp.log"

# Ensure logs directory exists
New-Item -ItemType Directory -Path "$repoRoot\logs" -Force | Out-Null

function Write-Log {
    param([string] $Message, [string] $Level = 'INFO')
    $logMsg = "[$timestamp] [$Level] $Message"
    Write-Host $logMsg
    Add-Content -Path $logFile -Value $logMsg
}

function Test-ProcessRunning {
    param([string] $ProcessName)
    return $null -ne (Get-Process -Name $ProcessName -ErrorAction SilentlyContinue)
}

function Wait-ForPort {
    param([int] $Port, [int] $TimeoutSeconds = 30)
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $null = [Net.Sockets.TcpClient]::new('localhost', $Port)
            Write-Log "Port $Port is now accepting connections" 'OK'
            return $true
        }
        catch {
            Start-Sleep -Seconds 1
            $elapsed += 1
        }
    }
    Write-Log "Port $Port did not become available within $TimeoutSeconds seconds" 'WARN'
    return $false
}

# ─── Phase 2.1: Launch TradingView with CDP ─────────────────────────────────
function Start-TradingView {
    Write-Log "=== Phase 2.1: TradingView Desktop Launch (CDP enabled) ===" 'INFO'

    if ($NoTV) {
        Write-Log "Skipping TradingView launch (--NoTV flag)" 'INFO'
        return $true
    }

    if (Test-ProcessRunning 'TradingView') {
        Write-Log "TradingView already running (PID $(Get-Process -Name TradingView -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id))" 'OK'
        return $true
    }

    if (-not (Test-Path $tvPath)) {
        Write-Log "TradingView not found at $tvPath. Install from https://www.tradingview.com/desktop/" 'ERROR'
        return $false
    }

    try {
        Write-Log "Launching TradingView with CDP on port $cdpPort..." 'INFO'
        if ($DryRun) {
            Write-Log "[DRY-RUN] Would execute: & '$tvPath' --remote-debugging-port=$cdpPort" 'DRYRUN'
            return $true
        }

        $process = Start-Process -FilePath $tvPath `
            -ArgumentList "--remote-debugging-port=$cdpPort" `
            -PassThru -WindowStyle Normal

        Write-Log "TradingView launched (PID: $($process.Id))" 'OK'
        Start-Sleep -Seconds 3

        if (Wait-ForPort $cdpPort) {
            Write-Log "TradingView CDP endpoint ready: http://localhost:$cdpPort" 'OK'
            return $true
        }
        return $false
    }
    catch {
        Write-Log "Failed to launch TradingView: $_" 'ERROR'
        return $false
    }
}

# ─── Phase 2.2: Initialize MCP Servers ──────────────────────────────────────
function Start-MCPServers {
    Write-Log "=== Phase 2.2: MCP Server Initialization ===" 'INFO'

    if ($NoMCP) {
        Write-Log "Skipping MCP server init (--NoMCP flag)" 'INFO'
        return $true
    }

    # Create .vscode/mcp.json if missing
    $mpcConfigPath = "$repoRoot\.vscode\mcp.json"
    if (-not (Test-Path $mpcConfigPath)) {
        Write-Log "Creating MCP configuration at $mpcConfigPath" 'INFO'

        $mpcConfig = @{
            'servers' = @{
                'tradingview' = @{
                    'command' = 'node'
                    'args' = @("$(Join-Path $repoRoot '.claude\mcp_servers\tradingview\server.js')")
                    'env' = @{
                        'CDP_PORT' = $cdpPort
                        'MCP_PORT' = $mcpPort
                    }
                }
            }
        } | ConvertTo-Json -Depth 10

        if (-not (Test-Path "$repoRoot\.vscode")) {
            New-Item -ItemType Directory -Path "$repoRoot\.vscode" -Force | Out-Null
        }

        Set-Content -Path $mpcConfigPath -Value $mpcConfig -Force
        Write-Log "MCP config created: $mpcConfigPath" 'OK'
    }

    Write-Log "MCP servers configured for port $mcpPort" 'OK'
    Write-Log "MCP endpoint: localhost:$mcpPort (via .vscode/mcp.json)" 'INFO'
    return $true
}

# ─── Phase 2.3: Verify Environment ──────────────────────────────────────────
function Test-Environment {
    Write-Log "=== Phase 2.3: Environment Verification ===" 'INFO'

    $checks = @(
        @{ Name = 'Python'; Command = 'python --version'; Critical = $true }
        @{ Name = '.env file'; Path = "$repoRoot\.env"; Critical = $true }
        @{ Name = 'requirements.txt'; Path = "$repoRoot\requirements.txt"; Critical = $true }
        @{ Name = 'Swarm framework'; Command = 'python -c "import swarm; print(swarm.__doc__[:30])"'; Critical = $true }
    )

    $passed = 0
    foreach ($check in $checks) {
        if ($check.Path) {
            if (Test-Path $check.Path) {
                Write-Log "✓ $($check.Name)" 'OK'
                $passed++
            }
            else {
                $level = $check.Critical ? 'ERROR' : 'WARN'
                Write-Log "✗ $($check.Name) - missing at $($check.Path)" $level
            }
        }
        elseif ($check.Command) {
            try {
                $result = Invoke-Expression $check.Command -ErrorAction Stop
                Write-Log "✓ $($check.Name): $($result.Trim())" 'OK'
                $passed++
            }
            catch {
                $level = $check.Critical ? 'ERROR' : 'WARN'
                Write-Log "✗ $($check.Name) - $($_.Exception.Message)" $level
            }
        }
    }

    Write-Log "$passed/$($checks.Count) environment checks passed" 'INFO'
    return $passed -eq $checks.Count
}

# ─── Phase 2.4: Run VIF Pipeline ────────────────────────────────────────────
function Start-VIFPipeline {
    Write-Log "=== Phase 2.4: VIF Analysis Pipeline ===" 'INFO'

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would execute: python agents/orchestrator_swarm.py --mode $Mode" 'DRYRUN'
        return $true
    }

    try {
        Push-Location $repoRoot
        Write-Log "Starting pipeline (mode: $Mode)..." 'INFO'
        $output = python agents/orchestrator_swarm.py --mode $Mode 2>&1

        # Log full output
        $output | ForEach-Object { Write-Log $_ 'PIPELINE' }

        # Check for success
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Pipeline completed successfully" 'OK'
            return $true
        }
        else {
            Write-Log "Pipeline exited with code $LASTEXITCODE" 'ERROR'
            return $false
        }
    }
    catch {
        Write-Log "Pipeline execution failed: $_" 'ERROR'
        return $false
    }
    finally {
        Pop-Location
    }
}

# ─── Main Execution ─────────────────────────────────────────────────────────
function Main {
    Write-Log "╔═══════════════════════════════════════════════════════════════════════╗" 'INFO'
    Write-Log "║  VIF Trading System - Phase 2 Startup (Autonomous TradingView + MCP)  ║" 'INFO'
    Write-Log "║                                                                       ║" 'INFO'
    Write-Log "║  Mode: $Mode                                                             ║" 'INFO'
    Write-Log "║  Log:  $logFile                                                         ║" 'INFO'
    Write-Log "╚═══════════════════════════════════════════════════════════════════════╝" 'INFO'

    if ($DryRun) {
        Write-Log "[DRY-RUN MODE] No commands will execute" 'WARN'
    }

    # Execute startup sequence
    $success = @(
        Start-TradingView,
        Start-MCPServers,
        Test-Environment,
        Start-VIFPipeline
    ) | Where-Object { $_ -eq $false }

    if ($success.Count -eq 0) {
        Write-Log "╔═════════════════════════════════════════════════════════════════════╗" 'OK'
        Write-Log "║  ✓ All startup phases completed successfully                       ║" 'OK'
        Write-Log "║                                                                     ║" 'OK'
        Write-Log "║  TradingView CDP:  http://localhost:$cdpPort                       ║" 'OK'
        Write-Log "║  MCP Endpoint:     localhost:$mcpPort                               ║" 'OK'
        Write-Log "║  Pipeline Mode:    $Mode                                                ║" 'OK'
        Write-Log "║  Output Log:       $logFile                                           ║" 'OK'
        Write-Log "╚═════════════════════════════════════════════════════════════════════╝" 'OK'
        return 0
    }
    else {
        Write-Log "╔═════════════════════════════════════════════════════════════════════╗" 'ERROR'
        Write-Log "║  ✗ Startup sequence failed ($($success.Count) critical steps)        ║" 'ERROR'
        Write-Log "║                                                                     ║" 'ERROR'
        Write-Log "║  Review log: $logFile                                              ║" 'ERROR'
        Write-Log "╚═════════════════════════════════════════════════════════════════════╝" 'ERROR'
        return 1
    }
}

# Execute
exit (Main)
