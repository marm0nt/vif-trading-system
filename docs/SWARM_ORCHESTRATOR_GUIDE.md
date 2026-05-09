# Swarm Orchestrator - Phase 3 Integration Guide

## Quick Start

The swarm orchestrator is now integrated into the daily pipeline. All scheduled jobs automatically use it.

### Manual Execution (Testing)

```bash
# Premarket pipeline: Catalyst + VIF + Swing screener
python agents/orchestrator_swarm.py --mode premarket

# After-hours: 5-day VIF + daily conviction
python agents/orchestrator_swarm.py --mode afterhours

# Full analysis: All components
python agents/orchestrator_swarm.py --mode full

# Weekend catalyst briefing
python agents/orchestrator_swarm.py --mode weekend

# Market-open swing screener
python agents/orchestrator_swarm.py --mode market_open
```

## Architecture

```
schedule_daily.py (scheduler)
    ↓
orchestrator_swarm.py (SwarmOrchestrator)
    ├─ KVCacheManager (shared backbone cache + per-agent LoRA)
    ├─ LatentWorkingMemory (hidden state exchange, layers 8/16/24)
    ├─ GossipRouter (decentralized task routing)
    ├─ ConfidenceWeightedConsensus (signal conflict resolution)
    └─ Agent Pool:
        ├─ VIFAnalystAgent (wraps watchlist_watcher.py)
        ├─ CatalystMonitorAgent (wraps catalyst_analysis.py)
        └─ SwingScreenerAgent (wraps swing_trade_screener_v2.py)
```

## Monitoring

Each run produces a JSON report in `reports/swarm_result_*.json`:

```json
{
  "mode": "premarket",
  "trace_id": "5d2e8f4a-9c61-4e7b-b8d9-f7c3a5e6b1d2",
  "timestamp": "2026-05-09T14:35:42.123456",
  "metrics": {
    "duration_ms": 12345,
    "agents_executed": 3,
    "agents_total": 3,
    "success_rate": 1.0,
    "kv_cache_hit_rate": 0.47,
    "consensus_conflicts": 2
  },
  "consensus_signals": {
    "NVDA": {"signal": "BUY", "confidence": 85},
    "TSLA": {"signal": "HOLD", "confidence": 62}
  },
  "conflicts": [
    {"ticker": "QXO", "agents": [...], "consensus": {...}}
  ]
}
```

### Key Metrics to Monitor

| Metric | Target | Status |
|--------|--------|--------|
| `duration_ms` | <15000 | Latency (40-50% improvement vs 25s) |
| `kv_cache_hit_rate` | >0.45 | Cache effectiveness (45-50% target) |
| `agents_executed` | = agents_total | All agents succeeded |
| `consensus_conflicts` | <5% of tickers | Low disagreement rate |
| `success_rate` | 1.0 | 100% execution success |

## Log Files

- **Main orchestrator log**: `logs/orchestrator_swarm.log`
- **Scheduler log**: `logs/scheduler.log`
- **Run history**: `logs/run_history.json`

## Performance Expectations

### Before Swarm (Baseline)
- Tokens: ~13,000/day (~$0.13 USD)
- Latency: ~25 seconds
- Cost: $0.13/day

### After Swarm (Phase 3)
- KV Cache Hit Rate: 45-50%
- Effective Tokens: ~7,000/day (cached backbone doesn't count)
- Latency: 12-15 seconds (40-50% faster)
- Cost: ~$0.07/day (50% reduction)

## Troubleshooting

### ImportError: swarm module not found
The swarm framework module is missing. Ensure:
```bash
ls -la swarm/
# Should show: __init__.py, orchestrator.py, specialist_agent.py, etc.
```

### Agent timeout
Individual agents may timeout (300s default). Check agent logs:
```bash
tail -20 logs/orchestrator_swarm.log
```

### Low cache hit rate (<35%)
Cache may not be warming up correctly. Check:
- Are multiple agents executing sequentially? (Good for cache reuse)
- Is agent pool properly initialized? (3 agents expected)
- Cache size sufficient? (500MB default, adjustable)

### High conflict rate (>10%)
Agents disagreeing on signals. This is normal during integration. Monitor:
- Do conflicts correlate with controversial tickers (earnings-sensitive, high IV)?
- Confidence levels in conflicting signals (should strongly favor one side)

## Integration Status

✅ **Phase 1**: Architecture design + core components
✅ **Phase 2**: KVCacheManager, LatentWorkingMemory, consensus logic
✅ **Phase 3**: Specialist agents + orchestrator integration + scheduler wiring

### Phase 4 (Next)
- [ ] Production validation on live schedule
- [ ] Performance baseline vs subprocess orchestrator
- [ ] OTel metrics collection (agent utilization, cache eviction, gossip delays)
- [ ] Gradual migration of agents to native SpecialistAgent implementations

## Configuration

Edit `swarm/orchestrator.py` to customize:

```python
# KV Cache settings
kv_cache = KVCacheManager(max_cache_mb=500, max_recompute_layers=3)

# Latent memory layers
latent_memory = LatentWorkingMemory(layers_to_share=[8, 16, 24])

# Gossip protocol settings
gossip_router = GossipRouter(gossip_timeout_ms=500, max_agents_per_subtask=2)

# Consensus signal priority
consensus = ConfidenceWeightedConsensus(
    signal_priority={"BUY": 3, "SELL": 2, "HOLD": 1}
)
```

## Support

- **Logs**: `logs/orchestrator_swarm.log` (detailed execution trace)
- **Results**: `reports/swarm_result_*.json` (metrics + signals)
- **Errors**: Check agent subprocess output in logs (each agent captures stderr)

## References

**ArXiv Papers (Implementation Foundation)**
- LRAgent (2602.01053): KV cache sharing for multi-LoRA agents
- LatentMAS (2511.20639): Layer-wise hidden state collaboration
- DroidSpeak (2411.02820): Selective layer recomputation
- Multi-Agent Collaboration Survey (2501.06322): Coordination mechanisms

**Codebase**
- `swarm/` — Swarm intelligence framework (all components)
- `agents/orchestrator_swarm.py` — Main orchestrator entry point
- `schedule_daily.py` — Daily scheduler (uses swarm orchestrator)
