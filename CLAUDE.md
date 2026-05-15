# CLAUDE.md

Master development guide for VIF Trading System. For new LLM instances (Claude.ai, Cursor, Gemini), **start here → then read [`ONBOARDING.md`](ONBOARDING.md) → then `.ai-context.yaml`**.

**Zero-Friction Context Layer (May 11, 2026):**
- **`.ai-context.yaml`** — Portable project metadata for Cursor, Gemini, Claude.ai (414 lines, all core concepts)
- **`ONBOARDING.md`** — New contributor guide (5-min read, hands-on tasks)
- **CLAUDE.md** — This file (deep technical reference, architecture details)

**Note:** At the start of every session, Claude reads all files in `.claude/memory/` for project context continuity. This enables memory and conversation history to sync across desktop and laptop.

## Cross-Device Brain Sync (May 13, 2026)

This repo implements the **claude-brain + atxtechbro "Spilled Coffee Principle"** pattern:
> Destroy any device → pull this repo on a new machine → be fully operational with complete AI context in under 15 minutes.

**What syncs via GitHub (tracked in git):**
- All project code (`agents/`, `scripts/`, `config/`, `watchlists/`)
- `.claude/memory/` — all AI learned context and preferences
- `.claude/skills/` — custom skill definitions
- `.claude/agents/` — agent configurations
- `.claude/hooks/` — automation hooks
- `.claude/settings.json` — shared Claude settings
- `CLAUDE.md` — this file

**What stays machine-local (gitignored):**
- `.env` — your API key (copy manually between devices)
- `.claude/settings.local.json` — machine-specific overrides
- `.claude/worktrees/` — ephemeral worktree state
- `data/`, `logs/`, `reports/` — regenerated automatically
- `venv/` / `.venv/` — NOT used anymore (see venv-free architecture below)

### CRITICAL: Venv-Free Architecture (May 15, 2026)

**All scheduled task failures before May 15 were caused by hardcoded venv paths.** This has been permanently fixed.

**New policy: No venv activation, no path lookups, ever.**

**How it works:**
- Dependencies installed **globally** via `pip install -r requirements.txt`
- `pyproject.toml` declares all dependencies (Poetry standard)
- All agents use `python` command directly (or `sys.executable`)
- No subprocess should ever reference `venv/Scripts` or `.venv/bin`

**On a new device:**
```bash
git clone ...
pip install -r requirements.txt  # Install all deps to system Python
python schedule_daily.py        # Works immediately, no venv needed
```

**If you accidentally create a venv:**
- Delete it: `rm -rf venv .venv`
- Pre-commit hook prevents hardcoded venv paths from entering git
- `bootstrap.py` guards all agents at startup

**Why this prevents failures:**
- Venv paths are machine-specific, always break when moving branches/devices
- System Python is portable, works everywhere
- No path resolution needed = no `[WinError 3]` failures
- See `bootstrap.py` for automatic environment validation

**Sync commands:**
```bash
# On any device, any time — syncs everything:
brain-sync.bat          # Windows (double-click or run from terminal)

# On the OTHER device after someone else synced:
git pull origin main    # That's it — full brain transferred
```

**First-time setup on a new device:**
1. `git clone https://github.com/marm0nt/vif-trading-system.git`
2. Copy `.env` from your other machine (or recreate it with your API key)
3. `pip install -r requirements.txt`
4. `powershell scripts\install-brain-sync-hook.ps1` — installs auto-push on commit
5. All memory, skills, agents, and context are already there from git.

## Project Overview

**VIF Trading System** is an AI-powered watchlist monitoring engine that applies the Volatility Imbalance Framework (v4.0) to analyze stock setups and generate trading signals. The system runs on a daily schedule (via `schedule_daily.py`) and outputs structured analysis for swing trade opportunities, macro themes, and catalyst-driven setups.

The entire signal generation pipeline runs via Claude API (Sonnet 4.6), making it cost-efficient (~$0.13/day) while maintaining analytical rigor.

---

## Quick Start Commands

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### Verify Installation
```bash
python tests/test_api_key.py       # Validate API key & connectivity
python tests/test_harness.py       # Run offline mock analysis (no API credits)
```

### Run Analysis
```bash
# Single watchlist (real API call)
python agents/watchlist_watcher.py --watchlist vantage_portfolio

# Run specific analysis script
python scripts/swing_trade_screener_v2.py
python scripts/catalyst_analysis.py

# Full scheduler (runs on daily cron)
python schedule_daily.py
```

### Development / Debugging
```bash
# Test a specific agent in isolation
python -m agents.watchlist_watcher --watchlist ai_verticals --period 1mo

# Check what the next scheduled run would be
python schedule_daily.py --dry-run  # (if implemented)
```

---

## Report Format Preferences

**All reports should be generated in HTML format by default** (not Markdown, JSON, or plain text).

### Report Output Requirements
- **Primary Format:** HTML with professional CSS styling
- **Why:** Professional appearance, easy browser viewing, table/chart rendering, interactive navigation
- **Generator Script:** `scripts/html_report_generator.py`
- **Output Location:** `reports/*.html`

### HTML Report Features
- Professional gradient header with title and metadata
- Tabbed navigation for multi-section reports
- Styled tables with hover effects
- Color-coded alerts (success, warning, danger, info)
- Badges and metrics cards for key numbers
- Responsive mobile-friendly design
- Print-friendly CSS for PDF export from browser

### When Generating Reports
1. Use `scripts/html_report_generator.py` as the template generator
2. Generate all analysis, strategy guides, and summaries as `.html` files
3. Save to `reports/` directory with descriptive naming
4. Provide HTML file path to user (they can open directly in browser)

### Example Report Generation
```python
from scripts.html_report_generator import create_html_template, save_html_report

sections = [
    {"heading": "Section 1", "html": "<p>Content here</p>"},
    {"heading": "Section 2", "html": "<table>...</table>"}
]

html = create_html_template("Report Title", sections)
save_html_report("report_name", html)
```

---

## Standard Operating Procedures (SOP)

### Unattended Operation Mode

This repository runs across multiple parallel terminal windows in `bypassPermissions` mode (configured in `.claude/settings.local.json`). Permission prompts should not appear for trusted operations.

**If a tool call is unexpectedly blocked:**
- Report the exact rule that fired and stop.
- Do **not** retry with different flags or invoke `--resume` (that is a session-launch flag, not a recovery mechanism).
- Do **not** write to `.env` or push to remote without explicit user instruction.

**For long-running tasks** (19 screeners, async agents, scheduled jobs):
- Write all progress and errors to `logs/<task_name>.log` with timestamps.
- This allows parallel terminal sessions to read task state without coordination through Claude.
- Each agent/script should configure `logging.FileHandler(f'logs/<task_name>.log')` at startup.

**Cross-terminal synchronization:**
- Do **not** rely on fictional state files (e.g., `.claude_state` UUID). Claude Code does not read such files.
- For resuming a session across terminals, use: `claude --resume <session-id>` or `claude --continue`
- Real state should live in `logs/` (JSON activity logs) or actual files your scripts read.

---

## High-Level Architecture

### Three-Tier Agent Pipeline

The system processes watchlists through three sequential stages:

1. **Watchlist Parser** (`agents/watchlist_watcher.py` - parse stage)
   - Loads CSV/TXT exports from TradingView
   - Deduplicates and normalizes ticker symbols (e.g., NASDAQ:NVDA → NVDA)
   - Validates ticker format
   - Output: Clean list of 50–85 tickers per watchlist

2. **Data Fetcher** (`agents/indicators.py` + caching layer)
   - Fetches OHLCV data from Yahoo Finance (free, no API key needed)
   - Computes technical indicators: RSI, MACD, Bollinger Bands, EMA, ATR
   - Caches to disk (24-hour TTL) to minimize redundant API calls
   - Batches 10–15 tickers per Claude call
   - Output: Structured indicator snapshot for each ticker

3. **VIF Analyst** (`agents/watchlist_watcher.py` - Claude analysis stage)
   - Runs the full VIF framework:
     - **Gamma regime detection** (positive/negative/transition) from price action
     - **Structural levels** (support/resistance from 20-day lookback)
     - **Volume confirmation** (current volume vs. 20-day MA)
     - **Kill switches** (K1–K6 override conditions; see `config/vif_config.yml`)
   - Generates BUY/SELL/HOLD signals with confidence scores
   - All analysis happens via Claude API calls (cost: ~100–200 tokens per ticker)

### Data Flow

```
Watchlist File (.txt)
    ↓
[Watchlist Parser] → Deduplicated tickers
    ↓
[Data Fetcher] → yfinance + caching → OHLCV + indicators
    ↓
[Claude VIF Analyst] → Framework analysis → BUY/SELL/HOLD + confidence
    ↓
[Report Generator] → JSON + Markdown output to reports/
```

### Supporting Agents

- **Orchestrator** (`agents/orchestrator.py`) — Hierarchical coordinator for multi-agent pipelines; supports `--mode premarket`, `--mode full`, or `--ticker NVDA` for focused analysis
- **Weekend Catalyst Agent** (`agents/weekend_catalyst_agent.py`) — Scans macro events, earnings dates, sector rotation; runs Friday evening
- **Research Agent** (`agents/claude_research_agent.py`) — Interactive Q&A for ad-hoc VIF queries
- **Report UI Agent** (`agents/report_ui_agent.py`) — Converts raw JSON to readable Markdown summaries

### Scheduler (Entry Point)

`schedule_daily.py` runs the entire workflow on a daily schedule:
- **07:00 weekdays** → Catalyst scan (macro + earnings)
- **08:45 weekdays** → Premarket VIF (1-month data)
- **09:35 weekdays** → Swing trade screener (2–4 week setups)
- **16:05 weekdays** → After-hours conviction + 5-day update
- **Friday 16:30** → Full end-of-week sweep
- **Saturday 08:00** → Weekend macro briefing
- **Sunday 18:00** → Monday morning prep

---

## Configuration & Environment

### `.env` file (Required)
```
ANTHROPIC_API_KEY=sk-ant-...
```

### `config/vif_config.yml` (Framework Parameters)

All VIF thresholds, kill switches, and API settings live here. Key sections:

- `gamma_regime.positive_threshold` — Threshold for positive gamma signal (default: 0.5)
- `kill_switches.k1–k6` — Override conditions (extreme volatility, gaps, low liquidity, earnings risk, correlation, technical breakdown)
- `api.model` — Claude model (currently `claude-sonnet-4-6`)
- `api.max_tokens` — Token limit per call (1024)
- `data_fetching.batch_size` — Tickers per Claude call (15)
- `data_fetching.cache_ttl_hours` — Cache expiration (24 hours)

**To modify framework behavior:** Edit `config/vif_config.yml`, reload it via `yaml.safe_load()` in Python, and re-run analysis.

### Watchlists

Three pre-configured watchlists in `watchlists/`:
- `vantage_portfolio.txt` — 85 mixed holdings
- `ai_verticals.txt` — AI & semiconductor focus
- `energy_ai.txt` — Energy + AI convergence

Add new watchlists as `.txt` files with comma- or newline-separated tickers.

---

## Token Budget & Cost

- **Daily total**: ~13,000 tokens (~$0.13 USD)
- **Monthly**: ~390,000 tokens (~$3.90 USD)
- Well under $20/month for continuous monitoring

**Cost-saving strategies** (already implemented):
- Batching: 10–15 tickers per Claude call (not individual calls)
- Caching: Local storage of yfinance data (24-hour TTL)
- Summaries: Pass indicator snapshots, not raw price data
- Selective analysis: Only analyze tickers meeting volatility thresholds

---

## File Structure Reference

```
vif-trading-system/
├── agents/
│   ├── watchlist_watcher.py     # Core VIF pipeline (parser + fetcher + analyst)
│   ├── orchestrator.py          # Multi-agent coordinator
│   ├── weekend_catalyst_agent.py # Macro & earnings briefing
│   ├── indicators.py            # Shared technical indicator library
│   ├── claude_research_agent.py  # Ad-hoc research Q&A
│   └── report_ui_agent.py       # JSON→Markdown converter
├── scripts/
│   ├── swing_trade_screener_v2.py # 5 setup types, ranked by R:R
│   ├── catalyst_analysis.py      # Government & policy catalysts
│   ├── advanced_analysis.py      # Multi-framework technical analysis
│   └── daily_watchlist_analysis.py # Conviction scoring
├── tests/
│   ├── test_harness.py          # Offline mock testing (no API calls)
│   └── test_api_key.py          # Validate API key & credentials
├── config/
│   └── vif_config.yml           # All VIF parameters, kill switches, model config
├── watchlists/
│   ├── vantage_portfolio.txt
│   ├── ai_verticals.txt
│   └── energy_ai.txt
├── data/                        # Caches (yfinance OHLCV, pickled DataFrames)
├── reports/
│   ├── raw/                     # JSON output (structured data)
│   ├── daily/                   # Markdown summaries (human-readable)
│   └── options/                 # Options strategy analysis
├── logs/                        # Scheduler logs
├── docs/
│   ├── AGENTS.md               # Agent architecture details
│   ├── SKILLS.md               # Trading analysis skills reference
│   ├── SETUP.md                # Installation & troubleshooting
│   └── QUICKSTART.md           # Beginner guide
├── schedule_daily.py           # Master scheduler (main entry point)
├── run_delayed_start.py        # Scheduler launcher utility
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── DEPLOYMENT_STATUS.txt       # Operational reference
```

---

## Key Dependencies

- **Claude API**: `anthropic>=0.97.0` — Core signal generation
- **Market Data**: `yfinance` — Free OHLCV data (no API key required)
- **Indicators**: `ta` (pure-Python) — RSI, MACD, Bollinger Bands, ATR, EMA
- **Processing**: `pandas`, `numpy`, `scipy` — Data manipulation & analysis
- **Config**: `PyYAML` — Framework parameter loading
- **Scheduling**: `schedule` — Cron-style job automation
- **Reporting**: `rich` — Terminal output formatting

---

## Common Development Patterns

### Adding a New Analysis Framework

1. Create a new agent in `agents/` or `scripts/`
2. Import indicator snapshots from `agents/indicators.py`
3. Call Claude API with context (see `watchlist_watcher.py` for examples)
4. Save output to `reports/raw/` (JSON) and `reports/daily/` (Markdown)
5. Update `config/vif_config.yml` if new thresholds are needed
6. Register in scheduler if it should run on a cadence

### Modifying Kill Switches

Kill switches (K1–K6) are stored in `config/vif_config.yml`. To add or change:

1. Edit the kill switch condition in `config/vif_config.yml`
2. Update the VIF analyst prompt in `watchlist_watcher.py` to reference the new logic
3. Test with `python tests/test_harness.py` (offline) or a single ticker (`--watchlist` on a small list)

### Adding a New Watchlist

1. Create a new `.txt` file in `watchlists/` (comma- or newline-separated tickers)
2. Run: `python agents/watchlist_watcher.py --watchlist <filename_without_txt>`
3. To add to scheduler, edit `schedule_daily.py` and add a new job entry

### Debugging API Calls

1. Set `ANTHROPIC_API_LOG=true` in your environment for verbose logging (if implemented)
2. Use `test_api_key.py` to validate connectivity before running full pipelines
3. Use `test_harness.py` to test offline with mock data (no API credits consumed)

---

## Testing Strategy

### Offline Testing (No API Credits)
```bash
python tests/test_harness.py
```
- Mock watchlist parsing, data fetching, and VIF analysis
- Useful for rapid iteration on framework logic

### API Testing (Uses Credits)
```bash
python tests/test_api_key.py
python agents/watchlist_watcher.py --watchlist <small_list>
```
- Validates actual Claude API integration
- Test with a small watchlist first to catch errors cheaply

### Scheduler Validation
```bash
python schedule_daily.py
```
- Runs the full daily pipeline once (not on cron schedule)
- Check `logs/` for any errors or skipped jobs

---

## Important Context for Future Work

### Token Efficiency is Critical

Every Claude API call costs tokens. The system is optimized to stay under $20/month. When adding features:
- Prefer batching (10–15 tickers per call) over individual ticker analysis
- Use summaries/snapshots, not raw OHLCV data
- Cache data aggressively (24-hour TTL is standard)
- Test offline first with `test_harness.py` before running live

### Signal Quality Over Volume

The VIF framework is designed to be **selective** and **confident**. It's better to flag 3 high-conviction setups than 30 low-conviction signals. When modifying analysis logic, maintain this bias toward precision.

### Framework Determinism

API calls use `temperature=0` (deterministic output). This ensures consistent signal generation across runs. Changing this could introduce variance in trading signals—use caution.

---

## External Alpha Audit Capability (Phase 4.5 — May 9, 2026)

**NEW:** The system integrates GitHub and Hugging Face MCPs for external research validation.

### How It Works
- Critic agent calls `audit_vif_signal()` for low-confidence signals (< 55%)
- Searches Hugging Face for relevant academic papers
- Searches GitHub for reference implementation repositories
- Extracts and compares trading factors to VIF baseline
- Boosts confidence if research confirms signal (+5 max), downgrades if contradicts (-10 floor)
- Flags novel factors for Week 2-3 integration roadmap

### Key Files
- `agents/external_alpha_auditor.py` — MCP wrapper + factor comparison engine
- `docs/skills/external-alpha-audit.md` — Audit workflow and integration points
- `docs/skills/repo-navigation.md` — Repository parsing and factor extraction patterns
- `data/external_repos_catalog.json` — Cached repository analysis (auto-populated)
- `data/external_papers_cache.json` — Cached paper search results (30-day TTL)

### Token Efficiency
- Monthly cost: ~1,900 tokens (~$0.019) — negligible overhead
- Papers cached 30 days, repos cached indefinitely (updated weekly)
- Audits only run for signals < 55% confidence (cost-optimized)

### Integration Status
- **Phase 1** ✓ Complete (May 9, 2026): Infrastructure + catalogs
- **Phase 2** ⏳ Scheduled (Week 2): Critic agent integration
- **Phase 3** ⏳ Scheduled (Week 3+): Novel factor backtesting

### Configuration
GitHub and Hugging Face MCP servers configured in `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here" }
    },
    "huggingface": {
      "command": "npx",
      "args": ["-y", "hf-mcp-server"],
      "env": { "HF_TOKEN": "your_token_here" }
    }
  }
}
```

---

## Operational Reference

For deployment and monitoring:
- See `DEPLOYMENT_COMPLETE.md` for latest system status and signal generation fixes
- See `docs/SETUP.md` for troubleshooting installation issues
- See `docs/QUICKSTART.md` for beginner workflows
- See `docs/skills/external-alpha-audit.md` for research validation workflow
