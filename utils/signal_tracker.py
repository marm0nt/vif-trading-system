#!/usr/bin/env python3
"""Signal accuracy tracking system. Records every VIF signal and tracks outcomes."""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path("data/signals.db")

class SignalTracker:
    """SQLite-based signal persistence and outcome tracking."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    signal TEXT NOT NULL CHECK(signal IN ('BUY', 'SELL', 'HOLD')),
                    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 100),
                    gamma_regime TEXT NOT NULL,
                    price_at_signal REAL NOT NULL,
                    kill_switches TEXT,
                    model_used TEXT,
                    batch_id TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS outcomes (
                    id INTEGER PRIMARY KEY,
                    signal_id INTEGER NOT NULL,
                    days_out INTEGER NOT NULL,
                    price_at_check REAL NOT NULL,
                    pct_change REAL NOT NULL,
                    was_correct INTEGER,
                    check_timestamp TEXT NOT NULL,
                    FOREIGN KEY (signal_id) REFERENCES signals(id)
                )
            """)
            conn.commit()

    def record_signal(self, ticker, signal, confidence, price, gamma_regime,
                      kill_switches=None, model_used="sonnet", batch_id=None):
        """Record a generated VIF signal."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO signals
                (timestamp, ticker, signal, confidence, gamma_regime, price_at_signal,
                 kill_switches, model_used, batch_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat(),
                ticker.upper(),
                signal.upper(),
                float(confidence),
                gamma_regime.lower(),
                float(price),
                json.dumps(kill_switches or []),
                model_used,
                batch_id
            ))
            conn.commit()
            last_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            logger.debug(f"Recorded {signal} signal for {ticker} (id={last_id})")
            return last_id

    def update_outcome(self, ticker, signal_date_str, days_out=5, current_price=None):
        """Update outcome for signals from a specific date."""
        import yfinance as yf

        with sqlite3.connect(self.db_path) as conn:
            # Find signals matching ticker and date
            cursor = conn.execute("""
                SELECT id, signal, price_at_signal, confidence
                FROM signals
                WHERE ticker = ? AND DATE(timestamp) = ?
            """, (ticker.upper(), signal_date_str))
            signals = cursor.fetchall()

            if not signals:
                logger.debug(f"No signals found for {ticker} on {signal_date_str}")
                return

            # Fetch current price if not provided
            if current_price is None:
                try:
                    data = yf.download(ticker, period="1d", progress=False)
                    if data is not None and not data.empty:
                        current_price = float(data['Close'].iloc[-1])
                    else:
                        logger.warning(f"Could not fetch {ticker} price")
                        return
                except Exception as e:
                    logger.warning(f"yfinance error for {ticker}: {e}")
                    return

            for signal_id, signal_type, entry_price, confidence in signals:
                pct_change = ((current_price - entry_price) / entry_price) * 100

                # Determine correctness
                was_correct = None
                if signal_type == "BUY" and pct_change > 0:
                    was_correct = 1
                elif signal_type == "BUY" and pct_change < 0:
                    was_correct = 0
                elif signal_type == "SELL" and pct_change < 0:
                    was_correct = 1
                elif signal_type == "SELL" and pct_change > 0:
                    was_correct = 0
                elif signal_type == "HOLD":
                    was_correct = 1 if abs(pct_change) < 2 else 0

                conn.execute("""
                    INSERT INTO outcomes
                    (signal_id, days_out, price_at_check, pct_change, was_correct, check_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    signal_id,
                    days_out,
                    current_price,
                    pct_change,
                    was_correct,
                    datetime.utcnow().isoformat()
                ))
            conn.commit()

    def get_win_rate(self, signal_type="BUY", lookback_days=90):
        """Get win rate for a signal type."""
        cutoff_date = (datetime.utcnow() - timedelta(days=lookback_days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(DISTINCT s.id) as total,
                    SUM(CASE WHEN o.was_correct = 1 THEN 1 ELSE 0 END) as wins
                FROM signals s
                LEFT JOIN outcomes o ON s.id = o.signal_id
                WHERE s.signal = ? AND s.timestamp >= ?
            """, (signal_type.upper(), cutoff_date))

            total, wins = cursor.fetchone()
            if total == 0:
                return {"signal_type": signal_type, "total": 0, "wins": 0, "win_rate": 0}

            win_rate = (wins / total) * 100 if wins else 0
            return {
                "signal_type": signal_type,
                "total": total,
                "wins": wins or 0,
                "win_rate": round(win_rate, 2),
                "lookback_days": lookback_days
            }

    def get_accuracy_report(self, lookback_days=90):
        """Get comprehensive accuracy report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "lookback_days": lookback_days,
            "buy_signals": self.get_win_rate("BUY", lookback_days),
            "sell_signals": self.get_win_rate("SELL", lookback_days),
            "hold_signals": self.get_win_rate("HOLD", lookback_days)
        }

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    s.signal,
                    AVG(CASE WHEN o.was_correct = 1 THEN o.pct_change ELSE NULL END) as avg_win_pct,
                    AVG(CASE WHEN o.was_correct = 0 THEN o.pct_change ELSE NULL END) as avg_loss_pct
                FROM signals s
                LEFT JOIN outcomes o ON s.id = o.signal_id
                WHERE s.timestamp >= ?
                GROUP BY s.signal
            """, ((datetime.utcnow() - timedelta(days=lookback_days)).isoformat(),))

            for signal_type, avg_win, avg_loss in cursor:
                report[f"{signal_type.lower()}_avg_win_pct"] = round(avg_win, 2) if avg_win else None
                report[f"{signal_type.lower()}_avg_loss_pct"] = round(avg_loss, 2) if avg_loss else None

        return report


if __name__ == "__main__":
    # Demo: create tracker and show report
    tracker = SignalTracker()
    report = tracker.get_accuracy_report(lookback_days=30)
    print(json.dumps(report, indent=2))
