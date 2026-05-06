# VIF Trading System — Laptop Sync Script
# Run this once from inside C:\Users\marti\vif-trading-system on your laptop
# Handles everything except: .env key (you type it) + memory files (copy from desktop)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "`n=== VIF Trading System — Laptop Sync ===" -ForegroundColor Cyan

# ── 1. Pull latest code ────────────────────────────────────────────────────────
Write-Host "`n[1/6] Pulling latest from GitHub..." -ForegroundColor Yellow
git pull origin main
Write-Host "    Done." -ForegroundColor Green

# ── 2. Activate venv + install any new packages ────────────────────────────────
Write-Host "`n[2/6] Installing/updating Python packages..." -ForegroundColor Yellow
$VenvActivate = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
    & $VenvActivate
} else {
    Write-Host "    venv not found — creating it now..." -ForegroundColor Yellow
    python -m venv venv
    & $VenvActivate
}
pip install -r requirements.txt --quiet
Write-Host "    Done." -ForegroundColor Green

# ── 3. .env check ─────────────────────────────────────────────────────────────
Write-Host "`n[3/6] Checking .env..." -ForegroundColor Yellow
$EnvFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $ProjectRoot ".env.example") $EnvFile
    Write-Host "    Created .env from example." -ForegroundColor Yellow
    $key = Read-Host "    Paste your ANTHROPIC_API_KEY now (sk-ant-...)"
    (Get-Content $EnvFile) -replace "your_api_key_here", $key | Set-Content $EnvFile
    Write-Host "    API key saved." -ForegroundColor Green
} else {
    $existing = Get-Content $EnvFile | Where-Object { $_ -match "ANTHROPIC_API_KEY=sk-ant-" }
    if ($existing) {
        Write-Host "    .env already has API key. Skipping." -ForegroundColor Green
    } else {
        $key = Read-Host "    .env exists but no key found. Paste your ANTHROPIC_API_KEY"
        Add-Content $EnvFile "`nANTHROPIC_API_KEY=$key"
        Write-Host "    API key appended." -ForegroundColor Green
    }
}

# ── 4. tradingview-mcp-jackson ─────────────────────────────────────────────────
Write-Host "`n[4/6] Setting up tradingview-mcp-jackson..." -ForegroundColor Yellow
$McpDir = Join-Path $ProjectRoot "tradingview-mcp-jackson"
$McpServer = Join-Path $McpDir "src\server.js"

if (Test-Path $McpServer) {
    Write-Host "    Already present — pulling updates..." -ForegroundColor Yellow
    Push-Location $McpDir
    git pull origin main 2>$null
    npm install --silent
    Pop-Location
    Write-Host "    Updated." -ForegroundColor Green
} else {
    Write-Host "    Not found — cloning from GitHub..." -ForegroundColor Yellow
    git clone https://github.com/LewisWJackson/tradingview-mcp-jackson.git $McpDir
    Push-Location $McpDir
    npm install --silent
    Pop-Location
    Write-Host "    Cloned and npm installed." -ForegroundColor Green
}

# ── 5. Register TradingView MCP with Claude Code ──────────────────────────────
Write-Host "`n[5/6] Registering TradingView MCP..." -ForegroundColor Yellow
$ServerPath = (Resolve-Path $McpServer).Path
$existing = claude mcp list 2>$null | Select-String "tradingview"
if ($existing) {
    Write-Host "    Already registered. Removing stale entry to refresh path..." -ForegroundColor Yellow
    claude mcp remove tradingview -s user 2>$null
}
$cmd = "claude mcp add -s user tradingview -e TV_PORT=9222 -- node `"$ServerPath`""
Write-Host "    Running: $cmd" -ForegroundColor Gray
Invoke-Expression $cmd
Write-Host "    MCP registered." -ForegroundColor Green

# ── 6. Restore Claude Code local permissions ──────────────────────────────────
Write-Host "`n[6/6] Writing .claude/settings.local.json (auto-allow tools)..." -ForegroundColor Yellow
$ClaudeSettings = Join-Path $ProjectRoot ".claude\settings.local.json"
$permissions = @{
    permissions = @{
        allow = @(
            "Bash(*)",
            "PowerShell(*)",
            "Read(*)",
            "Write(*)",
            "Edit(*)",
            "WebFetch(*)",
            "WebSearch",
            "Agent",
            "Glob",
            "Grep",
            "mcp__tradingview__tv_health_check",
            "mcp__tradingview__tv_launch",
            "mcp__tradingview__chart_get_state",
            "mcp__tradingview__watchlist_get",
            "mcp__tradingview__ui_evaluate"
        )
    }
}
$permissions | ConvertTo-Json -Depth 5 | Set-Content $ClaudeSettings -Encoding utf8
Write-Host "    Done." -ForegroundColor Green

# ── VS Code settings ──────────────────────────────────────────────────────────
$VscodeDir = Join-Path $ProjectRoot ".vscode"
New-Item -ItemType Directory -Force -Path $VscodeDir | Out-Null
$Username = $env:USERNAME
$VscodeSettings = @"
{
  "python.terminal.useEnvFile": true,
  "python.locator": "js",
  "python.venvPath": "C:\\Users\\$Username\\vif-trading-system",
  "python.venvFolders": ["venv"],
  "python.interpreter.infoVisibility": "always",
  "python.terminal.activateEnvironment": true,
  "python.analysis.extraPaths": [
    "C:\\Users\\$Username\\vif-trading-system\\venv\\Lib\\site-packages"
  ],
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.env.windows": {
    "PYTHONUTF8": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "VIRTUAL_ENV": "C:\\Users\\$Username\\vif-trading-system\\venv"
  },
  "git.ignoredRepositories": [
    "C:\\Users\\$Username\\vif-trading-system\\tradingview-mcp-jackson"
  ],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "terminal.integrated.enableImages": true
}
"@
$VscodeSettings | Set-Content (Join-Path $VscodeDir "settings.json") -Encoding utf8
Write-Host "    .vscode/settings.json written." -ForegroundColor Green

# ── Final verification ─────────────────────────────────────────────────────────
Write-Host "`n=== Verification ===" -ForegroundColor Cyan
python --version
python -c "import anthropic, yfinance, ta, pandas; print('  All core packages OK')"
claude mcp list | Select-String "tradingview"
Write-Host "`n=== Done. One manual step remaining ===" -ForegroundColor Cyan
Write-Host "Copy memory files from desktop:" -ForegroundColor White
Write-Host "  Desktop: C:\Users\marti\.claude\projects\C--Users-marti-vif-trading-system\memory\" -ForegroundColor Gray
Write-Host "  Laptop:  C:\Users\$Username\.claude\projects\C--Users-marti-vif-trading-system\memory\" -ForegroundColor Gray
Write-Host "`nThen start TradingView with CDP enabled:" -ForegroundColor White
Write-Host "  .\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1" -ForegroundColor Gray
Write-Host "`nThen verify connection in Claude Code:" -ForegroundColor White
Write-Host "  claude (open session) -> run tv_health_check" -ForegroundColor Gray
