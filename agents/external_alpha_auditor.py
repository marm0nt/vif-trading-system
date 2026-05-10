#!/usr/bin/env python3
"""
External Alpha Auditor — GitHub & Hugging Face MCP Integration

Critic agent uses this module to:
1. Search academic papers on trading research (Hugging Face)
2. Discover reference implementation repositories (GitHub)
3. Extract and validate trading factors
4. Boost or downgrade VIF signal confidence based on external research

Phase 1 (May 9, 2026): Infrastructure + catalog caching
Phase 2 (Week 2): Integration with critic agent
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parent.parent

# Strict filters to prevent context overflow
REPO_FILTERS = {
    "min_stars": 500,
    "max_size_mb": 500,
    "languages": ["python"],
    "licenses": ["MIT", "Apache-2.0", "GPL-3.0"],
    "max_age_days": 365,
    "exclude_patterns": [
        "test/", "docs/", "__pycache__", ".git/", "node_modules/",
        "*.egg-info", "dist/", "build/", "venv/"
    ]
}

# VIF baseline indicators for comparison
BASELINE_FACTORS = {
    "RSI": {"window": 14, "buy_threshold": 65, "sell_threshold": 35},
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
    "BB": {"window": 20, "dev": 2},
    "EMA": {"periods": [9, 21, 50, 200]},
    "ATR": {"window": 14}
}

# Factor patterns to search for in repos
FACTOR_PATTERNS = {
    "RSI": r"RSI|relative strength|rsi\(",
    "MACD": r"MACD|moving average convergence|macd\(",
    "Bollinger": r"bollinger|bb_|bollingerband",
    "ATR": r"ATR|average true range|atr\(",
    "EMA": r"EMA|exponential moving average|ema\(",
    "Custom": r"class.*Indicator|def.*calculate"
}


class ExternalAlphaAuditor:
    """
    Query external research sources (GitHub, Hugging Face) to validate
    and enhance VIF trading signals.
    """

    def __init__(self):
        self.catalog_path = _REPO_ROOT / "data" / "external_repos_catalog.json"
        self.papers_cache_path = _REPO_ROOT / "data" / "external_papers_cache.json"
        self.logger = logging.getLogger(__name__)
        self._load_catalogs()

    def _load_catalogs(self):
        """Load cached repository and paper catalogs."""
        self.repo_catalog = {}
        self.papers_cache = {}

        if self.catalog_path.exists():
            try:
                with open(self.catalog_path) as f:
                    data = json.load(f)
                    self.repo_catalog = {r["name"]: r for r in data.get("repos", [])}
                    self.logger.debug(f"Loaded {len(self.repo_catalog)} repos from cache")
            except Exception as e:
                self.logger.warning(f"Failed to load repo catalog: {e}")

        if self.papers_cache_path.exists():
            try:
                with open(self.papers_cache_path) as f:
                    self.papers_cache = json.load(f)
                    self.logger.debug(f"Loaded {len(self.papers_cache)} papers from cache")
            except Exception as e:
                self.logger.warning(f"Failed to load papers cache: {e}")

    def search_papers(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search Hugging Face for relevant trading research papers.

        Args:
            query: Search query (e.g., "volatility imbalance gamma regime")
            top_k: Number of top results to return

        Returns:
            List of paper metadata (title, authors, url, year, key_findings)
        """
        # Phase 1: Return cached results or empty (MCP not yet active)
        cache_key = f"query:{query}:k{top_k}"
        if cache_key in self.papers_cache:
            cached = self.papers_cache[cache_key]
            if datetime.fromisoformat(cached["cached_at"]) > datetime.now() - timedelta(days=30):
                self.logger.info(f"Paper search (cached): {query}")
                return cached["papers"]

        self.logger.info(f"Paper search (would use HF MCP): {query}")
        # TODO: Call hf_paper_search() via MCP when tokens are configured
        return []

    def search_repositories(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search GitHub for implementation repositories matching query.

        Args:
            query: Search query (e.g., "volatility imbalance framework")
            top_k: Number of top results

        Returns:
            List of repository metadata (name, url, stars, description, factors_found)
        """
        # Phase 1: Return cached results
        cache_key = f"repos:{query}"
        if cache_key in self.repo_catalog:
            self.logger.info(f"Repo search (cached): {query}")
            return [r for r in self.repo_catalog.values()][:top_k]

        self.logger.info(f"Repo search (would use GitHub MCP): {query}")
        # TODO: Call github_search_repos() via MCP when tokens are configured
        return []

    def calculate_deviation_score(self, repo_factors: Dict) -> int:
        """
        Compare repository factors to VIF baseline.
        Returns 0-100 score (0 = identical, 100 = completely different).
        """
        if not repo_factors:
            return 100

        total_deviation = 0
        matched_factors = 0

        for factor_name, baseline_params in BASELINE_FACTORS.items():
            if factor_name in repo_factors:
                matched_factors += 1
                repo_params = repo_factors[factor_name]

                # Simple deviation: sum of parameter differences
                for key in baseline_params:
                    if key in repo_params:
                        baseline_val = baseline_params[key]
                        repo_val = repo_params[key]

                        if isinstance(baseline_val, int):
                            diff = abs(baseline_val - repo_val)
                            total_deviation += min(diff, 50)  # Cap at 50 per param

        if matched_factors == 0:
            return 100  # No matching factors

        avg_deviation = total_deviation / matched_factors
        return min(int(avg_deviation * 2), 100)

    def audit_signal(self, ticker: str, signal: str, confidence: int) -> Dict:
        """
        Run external alpha audit on a VIF signal.

        Returns:
            {
                "confidence_adjustment": -10 to +5,
                "audit_notes": ["Paper X confirms...", "Repo Y contradicts..."],
                "papers_found": [...],
                "repos_found": [...],
                "novel_factors": [...]
            }
        """
        audit_result = {
            "ticker": ticker,
            "signal": signal,
            "confidence_adjustment": 0,
            "audit_notes": [],
            "papers_found": [],
            "repos_found": [],
            "novel_factors": [],
            "audit_timestamp": datetime.now().isoformat()
        }

        # Only run audit for low-confidence signals (cost optimization)
        if confidence >= 55:
            audit_result["audit_notes"].append("High confidence signal, skipping external audit")
            return audit_result

        # Search for relevant papers
        papers = self.search_papers(f"{signal} signal {ticker}", top_k=2)
        audit_result["papers_found"] = papers

        # Search for relevant repositories
        repos = self.search_repositories("volatility imbalance trading agents", top_k=3)
        audit_result["repos_found"] = repos

        # Analyze findings
        if papers:
            audit_result["audit_notes"].append(
                f"Found {len(papers)} academic paper(s) on {signal} signals"
            )
            audit_result["confidence_adjustment"] += min(len(papers) * 2, 5)

        if repos:
            audit_result["audit_notes"].append(
                f"Found {len(repos)} reference implementation(s)"
            )
            # Check for novel factors in repos
            novel_count = sum(len(r.get("novel_factors", [])) for r in repos)
            if novel_count > 0:
                audit_result["novel_factors"] = [
                    f for r in repos for f in r.get("novel_factors", [])
                ]
                audit_result["audit_notes"].append(
                    f"Discovered {novel_count} novel factor(s) for Week 2 integration"
                )

        # Cap confidence adjustment
        audit_result["confidence_adjustment"] = max(
            min(audit_result["confidence_adjustment"], 5), -10
        )

        self.logger.info(
            f"Audit complete for {ticker} {signal} "
            f"(adjustment: {audit_result['confidence_adjustment']:+d})"
        )

        return audit_result

    def save_catalog(self):
        """Persist repository catalog to disk."""
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        repos_list = list(self.repo_catalog.values())
        with open(self.catalog_path, "w") as f:
            json.dump({"repos": repos_list, "updated": datetime.now().isoformat()}, f, indent=2)
        self.logger.info(f"Saved repo catalog ({len(repos_list)} repos)")

    def save_papers_cache(self):
        """Persist papers cache to disk."""
        self.papers_cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.papers_cache_path, "w") as f:
            json.dump(self.papers_cache, f, indent=2)
        self.logger.info(f"Saved papers cache ({len(self.papers_cache)} entries)")


# Singleton instance for use by critic agent
_auditor = ExternalAlphaAuditor()


def audit_vif_signal(ticker: str, signal: str, confidence: int) -> Dict:
    """
    Convenience function for critic agent to audit low-confidence VIF signals.

    Usage:
        from agents.external_alpha_auditor import audit_vif_signal
        audit = audit_vif_signal("NVDA", "BUY", 48)
        if audit["confidence_adjustment"] > 0:
            print(f"Confidence boosted by {audit['confidence_adjustment']}")
    """
    return _auditor.audit_signal(ticker, signal, confidence)
