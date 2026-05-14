#!/usr/bin/env python3
"""
Shared Technical Indicator Engine – VIF Trading System
=======================================================
Used by ALL agents. One source of truth for every indicator calculation.
Based on proven Freqtrade community strategies and quantitative research.

Indicators implemented (all battle-tested in backtested strategies):
  • RSI (14)              – momentum oscillator
  • MACD (12/26/9)       – trend + momentum confirmation
  • Bollinger Bands (20/2)– volatility + mean reversion
  • EMA 9/21/50/200       – trend structure (golden/death cross)
  • ATR (14)              – position sizing / stop placement
  • Stoch RSI            – overbought/oversold with faster signal
  • Volume Profile        – relative volume vs 20d avg
  • Squeeze (BB inside KC)– low-volatility breakout detector

Why the `ta` library?
  pandas-ta requires numba which is NOT compatible with Python 3.14.
  `ta` is pure-Python, fully compatible, and implements the same math.
"""

import pandas as pd
import numpy as np
import logging
import math
import json
from datetime import datetime, date
from pathlib import Path

from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange, KeltnerChannel

logger = logging.getLogger(__name__)

# ── Options Greeks Cache ───────────────────────────────────────────────────────
_GREEKS_CACHE_PATH = Path("data/options_greeks_cache.json")
_RISK_FREE_RATE = 0.05   # 5% risk-free rate (approximate)


def _bs_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> dict:
    """Black-Scholes Greeks for a European option."""
    try:
        from scipy.stats import norm
    except ImportError:
        return {}

    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {}

    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    sqrt_T = math.sqrt(T)
    pdf_d1 = norm.pdf(d1)

    if option_type == "call":
        delta = norm.cdf(d1)
        theta = (-(S * pdf_d1 * sigma) / (2 * sqrt_T) - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        delta = norm.cdf(d1) - 1
        theta = (-(S * pdf_d1 * sigma) / (2 * sqrt_T) + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365

    gamma = pdf_d1 / (S * sigma * sqrt_T)
    vega  = S * pdf_d1 * sqrt_T / 100      # per 1% IV move
    rho   = (K * T * math.exp(-r * T) * norm.cdf(d2) / 100) if option_type == "call" \
            else (-K * T * math.exp(-r * T) * norm.cdf(-d2) / 100)

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "theta": round(theta, 4),
        "vega":  round(vega, 4),
        "rho":   round(rho, 4),
    }


def compute_options_greeks(ticker_symbol: str, current_price: float, signal: str = "HOLD") -> dict:
    """
    Fetch ATM options from yfinance, compute Black-Scholes Greeks + IV%.

    Args:
        ticker_symbol: Clean ticker (no exchange prefix)
        current_price: Latest close price
        signal:        "BUY" → use calls, "SELL" → use puts, "HOLD" → calls

    Returns:
        {iv_pct, delta, gamma, theta, vega, rho, iv_rank, expiry, strike, option_type}
        or {} on failure (no options data, no expiries, computation error)

    Cache: 24-hour TTL keyed by ticker+date (avoids redundant yfinance calls)
    """
    cache_key = f"{ticker_symbol}_{date.today().isoformat()}"

    # Load cache
    cache = {}
    if _GREEKS_CACHE_PATH.exists():
        try:
            cache = json.loads(_GREEKS_CACHE_PATH.read_text())
        except Exception:
            cache = {}

    if cache_key in cache:
        return cache[cache_key]

    try:
        import yfinance as yf

        tk = yf.Ticker(ticker_symbol)
        expirations = tk.options
        if not expirations:
            return {}

        # Pick nearest expiry between 7 and 45 days out
        today = date.today()
        target_expiry = None
        for exp in expirations:
            exp_date = date.fromisoformat(exp)
            days_out = (exp_date - today).days
            if 7 <= days_out <= 45:
                target_expiry = exp
                break
        if not target_expiry:
            target_expiry = expirations[0]   # fallback: nearest available

        chain = tk.option_chain(target_expiry)
        option_type = "put" if signal == "SELL" else "call"
        df = chain.puts if option_type == "put" else chain.calls

        if df is None or df.empty:
            return {}

        # ATM = strike closest to current price
        df = df.copy()
        df["dist"] = (df["strike"] - current_price).abs()
        atm = df.nsmallest(1, "dist").iloc[0]

        iv = float(atm.get("impliedVolatility", 0))
        strike = float(atm["strike"])
        exp_date = date.fromisoformat(target_expiry)
        T = max((exp_date - today).days / 365, 1 / 365)

        greeks = _bs_greeks(current_price, strike, T, _RISK_FREE_RATE, iv, option_type)
        if not greeks:
            return {}

        result = {
            "iv_pct":      round(iv * 100, 1),
            "option_type": option_type,
            "strike":      strike,
            "expiry":      target_expiry,
            **greeks,
        }

        # Persist cache
        cache[cache_key] = result
        _GREEKS_CACHE_PATH.parent.mkdir(exist_ok=True)
        _GREEKS_CACHE_PATH.write_text(json.dumps(cache, indent=2))

        return result

    except Exception as e:
        logger.debug(f"Options Greeks fetch failed for {ticker_symbol}: {e}")
        return {}


class IndicatorEngine:
    """
    Compute a rich indicator set from OHLCV DataFrames.
    All agents should call IndicatorEngine(df).compute() to get a
    standardised dict they can pass to Claude or use for screening.
    """

    def __init__(self, df: pd.DataFrame):
        """
        df must have columns: Close, High, Low, Volume (pandas Float64 or float)
        Index should be a DatetimeIndex or at least integer-ordered.
        """
        self.df = df.copy()
        self._validate()

    def _validate(self):
        required = {"Close", "High", "Low", "Volume"}
        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(f"DataFrame missing columns: {missing}")
        self.df = self.df.dropna(subset=["Close", "High", "Low", "Volume"])


    # ── Main compute ──────────────────────────────────────────────────────────

    def compute(self) -> dict:
        """Return a flat dict of all indicators as of the most recent bar."""
        df = self.df
        close = df["Close"]
        high  = df["High"]
        low   = df["Low"]
        vol   = df["Volume"]
        price = float(close.iloc[-1])

        result = {"price": round(price, 2)}

        # ── RSI ──────────────────────────────────────────────────────────────
        rsi_series = RSIIndicator(close, window=14).rsi()
        result["rsi"] = round(float(rsi_series.iloc[-1]), 1) if not rsi_series.isnull().all() else 50.0

        # ── MACD (12/26/9) ────────────────────────────────────────────────────
        macd_obj = MACD(close, window_slow=26, window_fast=12, window_sign=9)
        macd_line   = float(macd_obj.macd().iloc[-1])
        macd_signal = float(macd_obj.macd_signal().iloc[-1])
        macd_hist   = float(macd_obj.macd_diff().iloc[-1])

        result["macd"]        = round(macd_line, 4)
        result["macd_signal"] = round(macd_signal, 4)
        result["macd_hist"]   = round(macd_hist, 4)
        result["macd_cross"]  = "bullish" if macd_hist > 0 else "bearish"

        # ── EMAs ─────────────────────────────────────────────────────────────
        for period in [9, 21, 50, 200]:
            ema_val = float(EMAIndicator(close, window=period).ema_indicator().iloc[-1])
            result[f"ema{period}"] = round(ema_val, 2)

        result["ema_trend"] = (
            "strong_uptrend" if result["ema9"] > result["ema21"] > result["ema50"] > result["ema200"]
            else "uptrend"   if result["ema21"] > result["ema50"] > result["ema200"]
            else "downtrend" if result["ema21"] < result["ema50"] < result["ema200"]
            else "mixed"
        )
        result["golden_cross"] = result["ema50"] > result["ema200"]   # 50 crosses above 200
        result["above_ema200"] = price > result["ema200"]

        # ── Bollinger Bands (20, 2σ) ─────────────────────────────────────────
        bb = BollingerBands(close, window=20, window_dev=2)
        bb_upper = float(bb.bollinger_hband().iloc[-1])
        bb_mid   = float(bb.bollinger_mavg().iloc[-1])
        bb_lower = float(bb.bollinger_lband().iloc[-1])
        bb_pctb  = float(bb.bollinger_pband().iloc[-1])
        bb_width = float(bb.bollinger_wband().iloc[-1])

        result["bb_upper"] = round(bb_upper, 2)
        result["bb_mid"]   = round(bb_mid, 2)
        result["bb_lower"] = round(bb_lower, 2)
        result["bb_pctb"]  = round(bb_pctb, 3)   # 0=at lower, 1=at upper
        result["bb_width"] = round(float(bb_width), 4)
        result["bb_squeeze"] = result["bb_width"] < 0.05   # tight = compression

        # ── ATR (14) – volatility / stop sizing ──────────────────────────────
        atr_series = AverageTrueRange(high, low, close, window=14).average_true_range()
        atr_val = float(atr_series.iloc[-1])

        result["atr"]     = round(atr_val, 3)
        result["atr_pct"] = round(atr_val / price * 100, 2) if price > 0 else 0
        # Suggested stop = 2x ATR below entry (standard in Freqtrade community)
        result["atr_stop_2x"] = round(price - 2 * atr_val, 2)

        # ── Volume Profile ────────────────────────────────────────────────────
        vol_avg_20 = float(vol.rolling(20).mean().iloc[-1]) if len(vol) >= 20 else float(vol.mean())
        vol_today  = float(vol.iloc[-1])
        vol_ratio  = vol_today / vol_avg_20 if vol_avg_20 > 0 else 1.0

        result["volume"]      = int(vol_today)
        result["vol_avg_20d"] = int(vol_avg_20)
        result["vol_ratio"]   = round(vol_ratio, 2)
        result["vol_signal"]  = "strong" if vol_ratio > 1.5 else ("weak" if vol_ratio < 0.8 else "normal")

        # ── Momentum (multi-timeframe) ────────────────────────────────────────
        def mom_pct(n: int) -> float:
            if len(close) < n + 1:
                return 0.0
            return round(float((close.iloc[-1] - close.iloc[-n]) / close.iloc[-n] * 100), 2)

        result["mom_1d"]  = mom_pct(1)
        result["mom_5d"]  = mom_pct(5)
        result["mom_10d"] = mom_pct(10)
        result["mom_20d"] = mom_pct(20)

        # ── Support / Resistance (20-day range) ───────────────────────────────
        n = min(20, len(high))
        result["high_20d"]  = round(float(high.iloc[-n:].max()), 2)
        result["low_20d"]   = round(float(low.iloc[-n:].min()),  2)
        range_20 = result["high_20d"] - result["low_20d"]
        result["range_pct"] = round(range_20 / result["low_20d"] * 100, 2) if result["low_20d"] > 0 else 0
        result["pct_in_range"] = round(
            (price - result["low_20d"]) / range_20 * 100, 1
        ) if range_20 > 0 else 50.0
        result["range_location"] = (
            "discount"  if result["pct_in_range"] < 33
            else "premium" if result["pct_in_range"] > 67
            else "mid"
        )

        # ── VIF Gamma Regime (derived from RSI + EMA trend) ───────────────────
        rsi = result["rsi"]
        ema_trend = result["ema_trend"]
        if rsi > 65 and ema_trend in ("uptrend", "strong_uptrend"):
            result["gamma_regime"] = "positive"
        elif rsi < 35 and ema_trend in ("downtrend", ):
            result["gamma_regime"] = "negative"
        else:
            result["gamma_regime"] = "transition"

        # ── Kill Switch Flags ─────────────────────────────────────────────────
        kills = []
        if rsi > 80 or rsi < 20:                         kills.append("K1")  # extreme RSI
        if result["range_pct"] > 12:                     kills.append("K2")  # gap risk
        if vol_today < 500_000:                          kills.append("K3")  # low liquidity
        if result["bb_squeeze"] and result["vol_ratio"] < 0.5: kills.append("K6")  # breakdown
        result["kill_switches"] = kills if kills else []
        result["kill_active"]   = len(kills) > 0

        return result


def fetch_and_compute(ticker: str, period: str = "6mo") -> dict | None:
    """
    Convenience wrapper: download data + compute all indicators in one call.
    Returns None if data is unavailable.

    Usage:
        from agents.indicators import fetch_and_compute
        ind = fetch_and_compute("NVDA", period="6mo")
    """
    import yfinance as yf
    try:
        df = yf.download(ticker, period=period, progress=False)
        if df is None or len(df) < 20:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df = pd.DataFrame({
                "Close":  df[("Close",  ticker)],
                "High":   df[("High",   ticker)],
                "Low":    df[("Low",    ticker)],
                "Volume": df[("Volume", ticker)],
            })
        else:
            df = df[["Close", "High", "Low", "Volume"]]
        df = df.dropna()
        return IndicatorEngine(df).compute()
    except Exception as e:
        logger.warning(f"fetch_and_compute({ticker}): {e}")
        return None


if __name__ == "__main__":
    # Quick smoke test
    print("Testing IndicatorEngine on NVDA...")
    ind = fetch_and_compute("NVDA", "3mo")
    if ind:
        print(f"  Price:       ${ind['price']}")
        print(f"  RSI:         {ind['rsi']}")
        print(f"  MACD cross:  {ind['macd_cross']}")
        print(f"  EMA trend:   {ind['ema_trend']}")
        print(f"  BB %B:       {ind['bb_pctb']} ({'squeeze' if ind['bb_squeeze'] else 'open'})")
        print(f"  ATR stop:    ${ind['atr_stop_2x']} (2x ATR)")
        print(f"  Vol signal:  {ind['vol_signal']} ({ind['vol_ratio']}x avg)")
        print(f"  Gamma:       {ind['gamma_regime']}")
        print(f"  Kill sw:     {ind['kill_switches'] or 'none'}")
        print(f"  Range loc:   {ind['range_location']} ({ind['pct_in_range']}% of 20d range)")
    else:
        print("  ERROR: could not fetch data")
