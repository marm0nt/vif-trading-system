# 🌐 IDE Layout Guide — 9-Agent Swarm Visualization

## Quick Setup (30 seconds)

**VS Code:**
```powershell
code vif-swarm-architecture.code-workspace
```

This opens a **multi-folder workspace** showing:
1. 🎯 **ORCHESTRATOR** (center) — `orchestrator_swarm.py`
2. 🔍 **CATALYST MONITOR** — Market catalysts
3. 📊 **VIF ANALYST** — Core signal generation
4. 🔎 **FINVIZ SCREENER** — Fundamental analysis
5. ⚡ **SWING SCREENER** — Setup validation
6. ✅ **SIGNAL VERIFIER** — 4-gate filter
7. 🤖 **CRITIC AGENT** — Research audit
8. ⚖️ **RISK AGENT** — Position sizing
9. 📈 **VECTORBT ANALYST** — Backtesting
10. 🔬 **AUTORESEARCH** — Paper synthesis

---

## Visual Architecture

The orchestrator acts as the **central hub** with all 9 agents connected:

```
                    🎯 ORCHESTRATOR
                         (Hub)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
       🔍 ───────────────📊 ─────────────🔎
        │                 │                 │
       ⚡ ───────────────✅ ─────────────🤖
        │                 │                 │
       ⚖️  ───────────────📈 ─────────────🔬
```

---

## Workspace File Structure

Each folder tab in VS Code contains:

| Tab | Contains | Key Files |
|-----|----------|-----------|
| 🎯 ORCHESTRATOR | Lead agent logic | `orchestrator_swarm.py`, gossip routing, consensus |
| 🔍 CATALYST | Earnings + macro | `*catalyst*.py` |
| 📊 VIF | Signal generation | `watchlist_watcher.py`, `indicators.py` |
| 🔎 FINVIZ | Fundamentals | `*finviz*.py` |
| ⚡ SWING | Setup types | `swing_trade_screener_v2.py` |
| ✅ VERIFIER | 4-gate validation | `*verif*.py` |
| 🤖 CRITIC | Research audit | `external_alpha_auditor.py` |
| ⚖️ RISK | Position sizing | `*risk*.py` |
| 📈 VECTORBT | Backtesting | `*backtest*.py` |
| 🔬 AUTORESEARCH | Paper synthesis | `*research*.py` |

---

## Keyboard Shortcuts (VS Code)

| Action | Shortcut |
|--------|----------|
| Switch between agent folders | `Ctrl+Tab` |
| Open orchestrator log | `Ctrl+P` → `orchestrator_swarm.log` |
| Run full pipeline | `Ctrl+Shift+` ` → `python schedule_daily.py` |
| Monitor cache hits | `Ctrl+Shift+` ` → `tail -f logs/orchestrator_swarm.log \| grep Cache` |
| Open SWARM_ARCHITECTURE_VISUAL | `Ctrl+P` → `SWARM_ARCHITECTURE_VISUAL.md` |

---

## Agent Execution Order

**Premarket Pipeline (07:00 CT):**
```
ORCHESTRATOR
  ├→ 🔍 CATALYST (earnings, policy)
  ├→ 📊 VIF ANALYST (signals)
  ├→ 🔎 FINVIZ (fundamentals)
  └→ ✅ SIGNAL VERIFIER (4-gate check)
```

**Market Open (09:35 CT):**
```
ORCHESTRATOR
  ├→ ⚡ SWING SCREENER (setup types)
  ├→ 🤖 CRITIC AGENT (low-conf audit)
  └→ ⚖️ RISK AGENT (position sizes)
```

**After Hours (16:05 CT):**
```
ORCHESTRATOR
  ├→ 📈 VECTORBT ANALYST (backtest)
  ├→ 🔬 AUTORESEARCH (synthesis)
  └→ ✅ SIGNAL VERIFIER (final filter)
```

---

## Cost Dashboard (Daily)

```
Agent                   Daily Cost   Savings (KV Cache)
─────────────────────────────────────────────────────
Catalyst Monitor        $0.008       $0.002
VIF Analyst             $0.040       $0.020
FinViz Screener         $0.012       $0.004
Swing Screener          $0.010       $0.003
Signal Verifier         $0.008       $0.002
Critic Agent            $0.005       $0.001
Risk Agent              $0.006       $0.002
VectorBT Analyst        $0.010       $0.003
Autoresearch            $0.004       $0.001
─────────────────────────────────────────────────────
TOTAL                   $0.103       → $0.070 ✅
```

**Savings:** 32% cost reduction via KV cache + gossip routing

---

## IDE Pro Tips

### 1. **Pin SWARM_ARCHITECTURE_VISUAL.md**
- Keep it open in a side panel
- Reference it while coding
- Visual reminder of agent dependencies

### 2. **Arrange Panes (VS Code)**
```
Left:     ORCHESTRATOR (main)
Middle:   Current agent folder
Right:    SWARM_ARCHITECTURE_VISUAL.md (pinned)
```

**Command:**
```
Ctrl+K → Ctrl+\  (split editor right)
```

### 3. **Create Run Tasks**

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Full Pipeline",
      "type": "shell",
      "command": "python",
      "args": ["schedule_daily.py"],
      "presentation": {"clear": true}
    },
    {
      "label": "Monitor Cache Hits",
      "type": "shell",
      "command": "tail",
      "args": ["-f", "logs/orchestrator_swarm.log"],
      "presentation": {"reveal": "always"}
    },
    {
      "label": "Run Premarket Mode",
      "type": "shell",
      "command": "python",
      "args": ["agents/orchestrator_swarm.py", "--mode", "premarket"],
      "presentation": {"clear": true}
    }
  ]
}
```

**Run with:** `Ctrl+Shift+D` → Select task

### 4. **File Nesting (Cleaner Explorer)**

VS Code automatically nests related files:
- `orchestrator_swarm.py` → Shows related `.log` files
- `*.py` → Shows `.json`, `.txt` configs

---

## Memory Sync Across Devices

The entire IDE setup syncs via git:

```bash
# On Device A — make changes
git add vif-swarm-architecture.code-workspace
git add .claude/SWARM_IDE_LAYOUT.md
git add SWARM_ARCHITECTURE_VISUAL.md
git commit -m "refactor: update swarm architecture visualization"
git push origin main

# On Device B — pull to sync
git pull origin main
code vif-swarm-architecture.code-workspace  # Ready to use!
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Workspace doesn't open | Check path: `code vif-swarm-architecture.code-workspace` |
| Folder tabs aren't showing | Workspace file is corrupted; regenerate via Claude Code |
| Cache hits not visible | Check `logs/orchestrator_swarm.log` → grep "Cache hit rate" |
| Agents not sequencing | Run `python tests/test_harness.py` first (offline test) |

---

## Next: Integrate GitHub Repos (Week 2)

Once the swarm is stable, add:
1. **TA Library** — Replace hand-rolled indicators
2. **Backtesting.py** — Weekly signal validation
3. **TradingAgents** — Multi-agent debate framework

See `docs/SWARM_ORCHESTRATOR_GUIDE.md` for integration guides.

---

**Status:** ✅ **DEPLOYED** (May 15, 2026)  
**Last Updated:** 2026-05-15  
**Creator:** Martin A.
