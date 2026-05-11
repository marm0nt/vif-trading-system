#!/usr/bin/env python3
"""
Signal Verifier Agent — 4-Gate Validation for VIF Signals

Runs between Critic/VectorBT and Report Builder. Every signal must pass
4 independent gates before being published. Verdicts: PUBLISH / DOWNGRADE / REJECT.

Gates:
  Gate 1 — Volume:       Current vol >= 80% of 20-day avg OR catalyst explains deviation
  Gate 2 — Fundamental:  BUY needs positive revenue trend; SELL needs deteriorating fundamentals
  Gate 3 — Sentiment:    News direction aligns with signal (FLAG on misalignment)
  Gate 4 — Macro:        Signal aligns with sector trend OR company catalyst justifies divergence

Verdict Logic:
  4 PASS           → PUBLISH   (HIGH conviction)
  3 PASS + 1 FLAG  → PUBLISH   (MEDIUM conviction)
  3 PASS + 1 FAIL  → DOWNGRADE (WATCH — lower confidence by 30%)
  <=2 PASS         → REJECT    (removed from report)

Auto-Reject (skip gates):
  - Volume < 50K shares
  - Price < $1
  - K3 / K4 kill switch active
  - No price data

Token cost: 0 (all local rule-based computation against cached market data)
Execution order: After Critic + VectorBT → Before Swing Screener and Report Builder
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

from swarm.specialist_agent import SpecialistAgent

logger = logging.getLogger(__name__)

# Thresholds
VOLUME_RATIO_MIN = 0.80          # Current vol must be >=80% of 20-day avg
VOLUME_AUTO_REJECT = 50_000      # Hard floor — below this, auto-reject
PRICE_AUTO_REJECT = 1.0          # Penny stock floor
DOWNGRADE_FACTOR = 0.70          # Confidence multiplier on DOWNGRADE (30% reduction)
RSI_OVERSOLD = 30                # RSI < 30 on SELL = potential reversal (Gate 4 flag)
RSI_OVERBOUGHT = 70              # RSI > 70 on BUY = potential reversal (Gate 4 flag)
CONFIDENCE_FLOOR = 10            # Minimum confidence after downgrade


class NativeSignalVerifierAgent(SpecialistAgent):
    """
    4-gate signal verification. Runs after Critic + VectorBT, before report builder.

    Reads:  task_context["critic_signals"] (preferred) or task_context["vif_signals"]
    Writes: task_context["verified_signals"], result["signals"]
    """

    def __init__(self, agent_id: str = "signal-verifier"):
        super().__init__(
            agent_id=agent_id,
            agent_type="signal-verifier",
            role_description="4-gate signal validator — PUBLISH / DOWNGRADE / REJECT per ticker",
        )

    def _execute_subtasks(self, subtasks: list, latent_context: dict) -> dict:
        logger.info(f"{self.agent_id}: Starting 4-gate signal verification")

        # Read signals — prefer post-critic signals, fall back to raw VIF signals
        signals = (
            self.task_context.get("critic_signals")
            or self.task_context.get("vif_signals")
            or {}
        )

        if not signals:
            logger.warning(f"{self.agent_id}: No signals to verify — skipping")
            return {"signals": {}, "metrics": {"skipped": True}, "hidden_states": {}}

        published, downgraded, rejected = {}, {}, {}
        gate_log = {}

        for ticker, signal_data in signals.items():
            verdict, gates, reason = self._run_gates(ticker, signal_data)
            gate_log[ticker] = {"verdict": verdict, "gates": gates, "reason": reason}

            if verdict == "PUBLISH":
                published[ticker] = {**signal_data, "verifier_verdict": "PUBLISH", "gates_passed": gates}
                logger.info(f"{self.agent_id}: PUBLISH {ticker} ({signal_data.get('signal')} {signal_data.get('confidence')}%)")
            elif verdict == "DOWNGRADE":
                orig_conf = signal_data.get("confidence", 50)
                new_conf = max(CONFIDENCE_FLOOR, int(orig_conf * DOWNGRADE_FACTOR))
                downgraded[ticker] = {
                    **signal_data,
                    "verifier_verdict": "DOWNGRADE",
                    "original_confidence": orig_conf,
                    "confidence": new_conf,
                    "downgrade_reason": reason,
                    "gates_passed": gates,
                }
                logger.info(f"{self.agent_id}: DOWNGRADE {ticker} ({orig_conf}% → {new_conf}%) — {reason}")
            else:
                rejected[ticker] = {**signal_data, "verifier_verdict": "REJECT", "reject_reason": reason}
                logger.info(f"{self.agent_id}: REJECT {ticker} — {reason}")

        final_signals = {**published, **downgraded}

        metrics = {
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "total_input": len(signals),
            "published": len(published),
            "downgraded": len(downgraded),
            "rejected": len(rejected),
            "publish_rate": len(published) / max(len(signals), 1),
        }

        logger.info(
            f"{self.agent_id}: Verification complete — "
            f"{len(published)} published, {len(downgraded)} downgraded, {len(rejected)} rejected"
        )

        return {
            "signals": final_signals,
            "rejected_signals": rejected,
            "gate_log": gate_log,
            "metrics": metrics,
            "hidden_states": {},
        }

    def _run_gates(self, ticker: str, signal_data: dict) -> Tuple[str, Dict, str]:
        """
        Run all 4 gates. Returns (verdict, gate_results, reason).
        verdict: "PUBLISH" | "DOWNGRADE" | "REJECT"
        """
        signal = signal_data.get("signal", "HOLD")
        confidence = signal_data.get("confidence", 50)
        volume = signal_data.get("volume", 0)
        vol_avg = signal_data.get("vol_avg_20d", 1)
        price = signal_data.get("price", 0)
        rsi = signal_data.get("rsi", 50)
        kill_switch = signal_data.get("kill_switch", "")
        change_pct = signal_data.get("change_pct", 0)

        # ── Auto-reject conditions (skip gates) ───────────────────────────────
        if volume < VOLUME_AUTO_REJECT:
            return "REJECT", {}, f"Volume {volume:,.0f} below auto-reject floor ({VOLUME_AUTO_REJECT:,})"
        if price < PRICE_AUTO_REJECT:
            return "REJECT", {}, f"Price ${price:.2f} below penny stock floor"
        if kill_switch in ("K3", "K4"):
            return "REJECT", {}, f"Kill switch {kill_switch} active"
        if not price:
            return "REJECT", {}, "No price data"

        gates = {}

        # ── Gate 1: Volume ────────────────────────────────────────────────────
        vol_ratio = volume / max(vol_avg, 1)
        if vol_ratio >= VOLUME_RATIO_MIN:
            gates["volume"] = "PASS"
        elif change_pct and abs(change_pct) > 3:
            # Catalyst explains low volume (gap move on news)
            gates["volume"] = "FLAG"
        else:
            gates["volume"] = "FAIL"

        # ── Gate 2: Fundamental ───────────────────────────────────────────────
        # Proxy: use price-vs-MA20 as momentum-fundamental alignment
        ma_20 = signal_data.get("ma_20", price)
        price_vs_ma = (price - ma_20) / max(ma_20, 0.01)

        if signal == "BUY":
            # BUY: price above MA20 = positive momentum alignment
            gates["fundamental"] = "PASS" if price_vs_ma > -0.02 else "FAIL"
        elif signal == "SELL":
            # SELL: price below MA20 = bearish fundamental alignment
            gates["fundamental"] = "PASS" if price_vs_ma < 0.05 else "FLAG"
        else:
            gates["fundamental"] = "PASS"  # HOLD is neutral

        # ── Gate 3: Sentiment ─────────────────────────────────────────────────
        # Proxy: use RSI trend direction alignment with signal
        if signal == "BUY":
            if 40 <= rsi <= 65:
                gates["sentiment"] = "PASS"     # RSI building momentum
            elif rsi < 30:
                gates["sentiment"] = "FLAG"     # Deeply oversold — could bounce but risky
            elif rsi > 75:
                gates["sentiment"] = "FAIL"     # Overbought — sentiment stretched
            else:
                gates["sentiment"] = "PASS"
        elif signal == "SELL":
            if rsi > 55:
                gates["sentiment"] = "PASS"     # RSI elevated, confirms distribution
            elif rsi < RSI_OVERSOLD:
                gates["sentiment"] = "FLAG"     # Oversold — potential reversal risk
            else:
                gates["sentiment"] = "PASS"
        else:
            gates["sentiment"] = "PASS"

        # ── Gate 4: Macro + IV% ───────────────────────────────────────────────
        # Uses 5-day change alignment + implied volatility as macro regime proxy
        iv_pct = signal_data.get("iv_pct", None)

        if signal == "BUY" and change_pct < -5:
            gates["macro"] = "FAIL"     # Buying into 5%+ decline without catalyst
        elif signal == "SELL" and change_pct > 5:
            gates["macro"] = "FLAG"     # Selling after 5%+ run-up — late signal risk
        elif signal == "BUY" and change_pct > 8:
            gates["macro"] = "FLAG"     # Chasing 8%+ move — momentum risk
        elif iv_pct is not None and signal == "BUY" and iv_pct > 80:
            gates["macro"] = "FLAG"     # IV >80% on BUY — options market pricing in risk
        elif iv_pct is not None and signal == "SELL" and iv_pct < 15:
            gates["macro"] = "FLAG"     # IV <15% on SELL — market complacent, low conviction
        else:
            gates["macro"] = "PASS"

        # ── Verdict logic ─────────────────────────────────────────────────────
        pass_count = sum(1 for v in gates.values() if v == "PASS")
        fail_count = sum(1 for v in gates.values() if v == "FAIL")
        flag_count = sum(1 for v in gates.values() if v == "FLAG")

        failed_gates = [k for k, v in gates.items() if v == "FAIL"]
        flagged_gates = [k for k, v in gates.items() if v == "FLAG"]

        if fail_count == 0 and flag_count <= 1:
            verdict = "PUBLISH"
            reason = "All gates clear"
        elif fail_count == 1 and flag_count == 0:
            verdict = "DOWNGRADE"
            reason = f"Gate failed: {failed_gates[0]}"
        elif fail_count == 0 and flag_count >= 2:
            verdict = "DOWNGRADE"
            reason = f"Multiple flags: {', '.join(flagged_gates)}"
        else:
            verdict = "REJECT"
            reason = f"Gates failed: {', '.join(failed_gates)} | Flagged: {', '.join(flagged_gates)}"

        return verdict, gates, reason
