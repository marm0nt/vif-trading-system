#!/usr/bin/env python3
"""
Options Trading Execution Plan - FCEL & MRVL
Automated tracking and execution monitoring for no-spread options strategies
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(
    format='%(asctime)s [OPTIONS] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger()

# ============================================================================
# OPTIONS TRADING PLAN - EXECUTION CHECKLIST
# ============================================================================

EXECUTION_PLAN = {
    "FCEL_STRADDLE": {
        "name": "FCEL June 18 Long Straddle",
        "ticker": "FCEL",
        "strategy": "Long Straddle (ATM)",
        "conviction": "30% (Speculative)",
        "status": "READY_TO_EXECUTE",

        "position": {
            "long_call": {
                "symbol": "FCEL",
                "expiration": "2026-06-18",
                "strike": 13.00,
                "type": "CALL",
                "quantity": 1,
                "entry_price_range": [1.00, 1.25],
                "entry_price_mid": 1.125,
            },
            "long_put": {
                "symbol": "FCEL",
                "expiration": "2026-06-18",
                "strike": 13.00,
                "type": "PUT",
                "quantity": 1,
                "entry_price_range": [0.75, 1.00],
                "entry_price_mid": 0.875,
            }
        },

        "capital_required": 175.00,  # ~$1.75 per share × 100
        "max_profit": None,  # Unlimited
        "max_loss": 225.00,  # Total premium paid

        "catalysts": {
            "earnings_date": "2026-06-06",
            "earnings_type": "Q2 2026",
            "expected_move_30d": 6.33,  # 48.3%
        },

        "entry_plan": {
            "step_1": "Today (May 1): Enter both legs at market",
            "step_2": "Set exit alert: 50% profit target ($2.25-2.75 straddle value)",
            "step_3": "Exit 50% position if straddle gains 30% before June 1",
            "step_4": "Hold 50% position through June 6 earnings for volatility spike",
            "step_5": "Exit remaining 50% next trading day after earnings (IV crush)"
        },

        "exit_plan": {
            "profit_target_1": {
                "trigger": "Straddle value reaches $2.25-2.75",
                "action": "Exit 50% of position (1/2 call + 1/2 put)",
                "expected_profit": 75.00,  # 50% of cost
                "timing": "Around May 15-20 (pre-earnings)"
            },
            "profit_target_2": {
                "trigger": "Straddle value reaches $3.25-3.75",
                "action": "Exit remaining 50% of position",
                "expected_profit": 150.00,  # 100% of cost
                "timing": "Around May 20-June 6"
            },
            "stop_loss": {
                "trigger": "Straddle value drops to $0.75",
                "action": "Exit entire position (cut loss)",
                "max_loss": 100.00,  # 50% of premium
                "timing": "If thesis breaks before June 1"
            },
            "earnings_exit": {
                "trigger": "Earnings announced (June 6)",
                "action": "Exit all remaining position next trading day",
                "reason": "IV crush will devastate straddle value despite move",
                "timing": "June 7, 2026 (Day after earnings)"
            }
        },

        "risk_management": {
            "max_contracts": 2,
            "max_portfolio_allocation": "5%",
            "liquidity_warning": "Wide bid-ask spreads ($0.10-0.25) - use limit orders",
            "position_sizing": "100 shares per contract"
        }
    },

    "MRVL_CALL_SPREAD": {
        "name": "MRVL May 29 Post-Earnings Call Spread",
        "ticker": "MRVL",
        "strategy": "Long Call Spread (Bullish)",
        "conviction": "80% (Strong)",
        "status": "AWAITING_EARNINGS_CONFIRMATION",

        "position": {
            "long_call": {
                "symbol": "MRVL",
                "expiration": "2026-05-29",
                "strike": 167.50,
                "type": "CALL",
                "quantity": 1,
                "entry_price_range": [2.00, 2.50],
                "entry_price_mid": 2.25,
            },
            "short_call": {
                "symbol": "MRVL",
                "expiration": "2026-05-29",
                "strike": 175.00,
                "type": "CALL",
                "quantity": -1,
                "entry_price_range": [0.50, 0.75],
                "entry_price_mid": 0.625,
            }
        },

        "capital_required": 175.00,  # Net debit ~$1.75 × 100
        "max_profit": 575.00,  # $7.50 width - $1.75 debit = $5.75 × 100
        "max_loss": 175.00,  # Net debit paid

        "catalysts": {
            "earnings_date": "2026-05-21 to 2026-05-28",
            "earnings_type": "Q1 FY2027",
            "expected_move_30d": 43.32,  # 26.08%
            "consensus_expectation": "Beat + raise guidance (data center 40% growth)"
        },

        "entry_plan": {
            "step_0": "WAIT for earnings announcement (May 21-28)",
            "step_1": "Verify beat on revenue + data center growth",
            "step_2": "If confirmed beat: Enter spread on May 29 morning (post-gap-up)",
            "step_3": "Buy $167.50 call @ $2.25 mid-price",
            "step_4": "Sell $175.00 call @ $0.625 mid-price",
            "step_5": "Net debit target: $1.625 (best case) to $1.875 (worst case)"
        },

        "exit_plan": {
            "profit_target_1": {
                "trigger": "Stock reaches $170",
                "action": "Exit 50% of spread (buy to close short call, sell to close long call)",
                "expected_profit": 150.00,  # Roughly $1.50 gain
                "timing": "May 30-June 1 (post-earnings pop)"
            },
            "profit_target_2": {
                "trigger": "Stock reaches $175+",
                "action": "Exit remaining 50% of spread (max profit achieved)",
                "expected_profit": 575.00,  # Full max profit
                "timing": "June 1-5 (if momentum continues)"
            },
            "stop_loss": {
                "trigger": "Stock drops to $165 (earnings miss signal)",
                "action": "Exit entire spread (cut loss)",
                "max_loss": 175.00,  # Full debit at risk
                "timing": "If downside thesis plays out"
            },
            "time_decay_exit": {
                "trigger": "May 29 expiration approaching (if not profitable)",
                "action": "Close spread at market to avoid assignment risk",
                "timing": "May 29 end of day if position not profitable"
            }
        },

        "risk_management": {
            "max_contracts": 5,
            "max_portfolio_allocation": "7%",
            "liquidity_note": "Excellent liquidity - tight spreads ($0.05-0.15)",
            "position_sizing": "100 shares per contract"
        }
    },

    "MRVL_LONG_CALL_ALTERNATIVE": {
        "name": "MRVL June 18 Long Call (Lower Risk Alternative)",
        "ticker": "MRVL",
        "strategy": "Long Call (Bullish/Unlimited Upside)",
        "conviction": "75% (Strong)",
        "status": "BACKUP_STRATEGY",

        "position": {
            "long_call": {
                "symbol": "MRVL",
                "expiration": "2026-06-18",
                "strike": 170.00,
                "type": "CALL",
                "quantity": 1,
                "entry_price_range": [4.00, 5.00],
                "entry_price_mid": 4.50,
            }
        },

        "capital_required": 450.00,  # ~$4.50 per share × 100
        "max_profit": None,  # Unlimited
        "max_loss": 500.00,  # Premium paid

        "entry_plan": {
            "step_1": "Enter post-earnings (May 29+) if earnings beat confirmed",
            "step_2": "OR enter immediately if you want to avoid earnings risk",
            "step_3": "Buy $170 call at market (target $4.50 max entry)"
        },

        "exit_plan": {
            "profit_target_1": {
                "trigger": "Stock reaches $175",
                "action": "Exit 50% of call (take profit)",
                "expected_profit": 150.00,  # ~$1.50 gain
            },
            "profit_target_2": {
                "trigger": "Stock reaches $180+",
                "action": "Exit remaining 50% of call (ride trend)",
                "expected_profit": 600.00,  # $6+ gain (120%+)
            },
            "stop_loss": {
                "trigger": "Call value drops to $2.50",
                "action": "Exit entire position (cut loss)",
                "max_loss": 200.00,  # ~50% of premium
            }
        }
    }
}

def generate_execution_report():
    """Generate human-readable execution plan"""

    report = []
    report.append("=" * 80)
    report.append("OPTIONS TRADING EXECUTION PLAN")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")

    # FCEL Strategy
    fcel = EXECUTION_PLAN["FCEL_STRADDLE"]
    report.append("1. FCEL JUNE 18 LONG STRADDLE")
    report.append("-" * 80)
    report.append(f"   Strategy: {fcel['strategy']}")
    report.append(f"   Conviction: {fcel['conviction']}")
    report.append(f"   Status: {fcel['status']}")
    report.append("")
    report.append("   POSITION:")
    report.append(f"   - Buy 1x $13 Call (June 18) @ $1.00-1.25")
    report.append(f"   - Buy 1x $13 Put  (June 18) @ $0.75-1.00")
    report.append(f"   - Total Cost: $175-225 per contract")
    report.append("")
    report.append("   EXECUTION STEPS:")
    for step, action in fcel['entry_plan'].items():
        report.append(f"   {step}: {action}")
    report.append("")
    report.append("   EXIT PLAN:")
    report.append("   • Sell 50% @ Straddle value $2.25-2.75 (Pre-earnings, around May 15-20)")
    report.append("   • Sell 50% @ Straddle value $3.25-3.75 (Hold through June 6 earnings)")
    report.append("   • Stop Loss @ Straddle value $0.75 (Cut loss if thesis breaks)")
    report.append("   • Exit ALL on June 7 (Next day after earnings, IV crush)")
    report.append("")
    report.append("")

    # MRVL Strategy
    mrvl = EXECUTION_PLAN["MRVL_CALL_SPREAD"]
    report.append("2. MRVL MAY 29 POST-EARNINGS CALL SPREAD ⭐ PRIMARY")
    report.append("-" * 80)
    report.append(f"   Strategy: {mrvl['strategy']}")
    report.append(f"   Conviction: {mrvl['conviction']}")
    report.append(f"   Status: {mrvl['status']}")
    report.append("")
    report.append("   POSITION (ENTER AFTER EARNINGS CONFIRMED):")
    report.append(f"   - Buy 1x $167.50 Call (May 29) @ $2.00-2.50")
    report.append(f"   - Sell 1x $175.00 Call (May 29) @ $0.50-0.75")
    report.append(f"   - Net Debit: $1.50-1.75 per contract")
    report.append(f"   - Max Profit: $575 (+329%)")
    report.append(f"   - Max Loss: $175 (-100% if earnings miss)")
    report.append("")
    report.append("   CRITICAL: WAIT FOR EARNINGS ANNOUNCEMENT (May 21-28)")
    report.append("   - Only enter IF beat confirmed")
    report.append("   - Enter May 29 morning (post-gap-up)")
    report.append("")
    report.append("   EXIT PLAN:")
    report.append("   • Sell 50% @ Stock $170 (Exit at ~$1.50 profit)")
    report.append("   • Sell 50% @ Stock $175+ (Max profit achieved)")
    report.append("   • Stop Loss @ Stock $165 (Earnings miss, cut loss)")
    report.append("")
    report.append("")

    # MRVL Alternative
    mrvl_alt = EXECUTION_PLAN["MRVL_LONG_CALL_ALTERNATIVE"]
    report.append("3. MRVL JUNE 18 LONG CALL (BACKUP - Lower Risk)")
    report.append("-" * 80)
    report.append(f"   Strategy: {mrvl_alt['strategy']}")
    report.append(f"   Conviction: {mrvl_alt['conviction']}")
    report.append(f"   Status: {mrvl_alt['status']}")
    report.append("")
    report.append("   POSITION:")
    report.append(f"   - Buy 1x $170 Call (June 18) @ $4.00-5.00")
    report.append(f"   - Total Cost: $400-500 per contract")
    report.append(f"   - Max Profit: Unlimited")
    report.append(f"   - Max Loss: $500 per contract")
    report.append("")
    report.append("   USE CASE: Avoid earnings risk, enter post-June 1")
    report.append("   - Lower conviction than call spread but less earnings binary risk")
    report.append("   - Better for risk-averse traders")
    report.append("")
    report.append("")

    # Risk Management
    report.append("4. RISK MANAGEMENT RULES (NON-NEGOTIABLE)")
    report.append("-" * 80)
    report.append("   Position Sizing:")
    report.append("   - FCEL: Max 2 contracts (limited liquidity)")
    report.append("   - MRVL: Max 5 contracts (excellent liquidity)")
    report.append("")
    report.append("   Stop Loss Discipline:")
    report.append("   - FCEL Straddle: Exit at $0.75 value (-$100 loss)")
    report.append("   - MRVL Spread: Exit at $165 stock (-$175 loss)")
    report.append("")
    report.append("   Profit Taking:")
    report.append("   - Always exit 50% at first profit target")
    report.append("   - Trail stops on remaining 50% with 20% trailing stop")
    report.append("   - Never hold overnight without stop losses")
    report.append("")
    report.append("")

    # Calendar
    report.append("5. EXECUTION CALENDAR")
    report.append("-" * 80)
    report.append("   TODAY (May 1):")
    report.append("   ✓ Enter FCEL June 18 straddle at market")
    report.append("   ✓ Set alert: Exit 50% on 30% gain")
    report.append("")
    report.append("   May 15-19:")
    report.append("   ✓ Monitor FCEL straddle for 30% gain")
    report.append("   ✓ Exit 50% if target hit")
    report.append("")
    report.append("   May 21-28 (Earnings Week):")
    report.append("   ✓ Monitor FCEL for Q2 earnings announcement")
    report.append("   ✓ Monitor MRVL for Q1 earnings announcement")
    report.append("")
    report.append("   May 28-29 (Post-Earnings):")
    report.append("   ✓ If MRVL beat: Enter call spread on May 29 morning")
    report.append("   ✓ If FCEL beat: Straddle will spike, exit 50% for profit")
    report.append("")
    report.append("   June 1-7:")
    report.append("   ✓ Manage MRVL spread (profit targets, stops)")
    report.append("   ✓ Exit FCEL straddle (IV crush post-earnings)")
    report.append("")
    report.append("=" * 80)

    return "\n".join(report)

def main():
    logger.info("=" * 80)
    logger.info("OPTIONS TRADING EXECUTION PLAN")
    logger.info("=" * 80)

    # Generate report
    report = generate_execution_report()
    print(report)

    # Save to file
    report_path = Path("reports") / f"options_execution_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)

    logger.info(f"[SAVED] {report_path}")

    # Save structured JSON for automation
    json_path = Path("reports") / f"options_execution_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(EXECUTION_PLAN, f, indent=2, default=str)

    logger.info(f"[SAVED] {json_path}")

    logger.info("")
    logger.info("NEXT STEPS:")
    logger.info("1. Review execution plan above")
    logger.info("2. Open your broker (TD Ameritrade, E*Trade, etc.)")
    logger.info("3. Enter FCEL straddle TODAY @ market prices")
    logger.info("4. Set calendar alerts for May 21-28 earnings")
    logger.info("5. Wait for MRVL earnings before entering call spread")
    logger.info("")

if __name__ == "__main__":
    main()
