# TradingView MCP Launch Reference

**Generated:** 2026-05-06  
**User:** Marti  
**Status:** Ready to execute

---

## 🚀 Quick Launch Commands

### Option 1: PowerShell (Recommended)
```powershell
# From vif-trading-system root:
.\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1
```

### Option 2: Direct Path (If Script Doesn't Work)
1. Find TradingView Store app path
2. Launch with: `TradingView.exe --remote-debugging-port=9222`
3. Verify: Port 9222 is listening

---

## 📋 Pre-Launch Checklist

Before running analysis:
- [ ] TradingView app is closed
- [ ] Port 9222 is available (no other process using it)
- [ ] `.env` has valid `ANTHROPIC_API_KEY`
- [ ] MCP is registered: `claude mcp list | grep tradingview`

---

## 🔍 Verification After Launch

### 1. Port Check
```powershell
netstat -an | findstr 9222
# Expected: TCP    127.0.0.1:9222         0.0.0.0:0              LISTENING
```

### 2. MCP Health Check
```
In Claude Code: tv_health_check
Expected response: { "cdp_connected": true, "api_available": true }
```

### 3. Process Check
```powershell
Get-Process TradingView -ErrorAction SilentlyContinue
# Expected: TradingView process listed
```

---

## 📊 Running Analysis After Launch

### Premarket (Default)
```bash
python agents/orchestrator.py --mode premarket
```

### Market Open
```bash
python agents/orchestrator.py --mode market_open
```

### Afterhours
```bash
python agents/orchestrator.py --mode afterhours
```

### Full Pipeline (All Agents)
```bash
python agents/orchestrator.py --mode full
```

### Single Watchlist
```bash
python agents/watchlist_watcher.py --watchlist ai_verticals
```

---

## 🎯 Expected Output Files

After analysis completes:
```
reports/
├── catalyst_analysis_YYYYMMDD_HHMMSS.json
├── swing_setups_YYYYMMDD_HHMMSS.json
├── orchestrator_premarket_YYYYMMDD_HHMMSS.json
└── DAILY_TRADING_SUMMARY_YYYYMMDD.html  (if full pipeline)
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 9222 already in use | Kill existing TradingView: `Stop-Process -Name TradingView -Force` |
| MCP not registered | Run: `claude mcp list` to check, then re-register if needed |
| CDP connection timeout | Restart TradingView with `launch_tv_windows_store.ps1` |
| API errors | Verify `.env` has valid `ANTHROPIC_API_KEY` |

---

## 💾 Sync Workflow (Desktop ↔ Laptop)

To sync your desktop changes to laptop:

1. **On desktop:** Push code to GitHub
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```

2. **On laptop:** Run sync script
   ```powershell
   .\LAPTOP_SYNC.ps1
   ```

This automatically:
- Pulls latest code
- Updates dependencies
- Re-registers TradingView MCP
- Restores Claude Code permissions

---

## 📝 Laptop-Specific Setup

If setting up on new machine:
```powershell
cd C:\Users\<username>\vif-trading-system
.\LAPTOP_SYNC.ps1
```

Then manually:
1. Copy memory files from desktop (optional)
2. Launch TradingView: `.\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1`
3. Verify: `tv_health_check` in Claude Code

---

## 🔑 Key Files

- **Launch Script:** `tradingview-mcp-jackson/scripts/launch_tv_windows_store.ps1`
- **Sync Script:** `LAPTOP_SYNC.ps1`
- **Main Orchestrator:** `agents/orchestrator.py`
- **Configuration:** `config/vif_config.yml`
- **Watchlists:** `watchlists/*.txt`

---

## 📊 What Antigravity Agent Created

**Recent Commits:**
- `a688d1b` — Added `LAPTOP_SYNC.ps1` (one-command sync)
- `f3f2778` — Added `LAPTOP_SETUP.md` (setup documentation)

These enable seamless synchronization between desktop and laptop through GitHub.

---

**Next Step:** Run `.\tradingview-mcp-jackson\scripts\launch_tv_windows_store.ps1` to start TradingView with debugging enabled.
