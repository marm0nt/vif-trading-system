"""
Swarm Intelligence Framework for VIF Trading System

Multi-agent orchestration with KV cache sharing and latent collaboration.
Based on arXiv research:
- LRAgent (2602.01053): Efficient KV cache sharing for multi-LoRA agents
- LatentMAS (2511.20639): Layer-wise hidden state collaboration
- DroidSpeak (2411.02820): Selective layer recomputation
- Gossip Protocols: Decentralized task routing, no central bottleneck
- Consensus: Confidence-weighted voting for conflict resolution
"""

from .kv_cache_manager import KVCacheManager, KVCacheBinding
from .latent_memory import LatentWorkingMemory
from .specialist_agent import SpecialistAgent, PromptLoader
from .gossip_router import GossipRouter
from .consensus import ConfidenceWeightedConsensus
from .orchestrator import SwarmOrchestrator
from .native_catalyst_monitor_agent import NativeCatalystMonitorAgent
from .native_vif_analyst_agent import NativeVIFAnalystAgent
from .native_finviz_screener_agent import NativeFinVizScreenerAgent
from .critic_agent import CriticAgent
from .native_swing_screener_agent import NativeSwingScreenerAgent
from .native_vectorbt_agent import NativeVectorBTAgent
from .native_autoresearch_agent import NativeAutoResearchAgent
from .native_signal_verifier_agent import NativeSignalVerifierAgent
from .risk_agent import RiskAgent

__all__ = [
    "KVCacheManager",
    "KVCacheBinding",
    "LatentWorkingMemory",
    "SpecialistAgent",
    "PromptLoader",
    "GossipRouter",
    "ConfidenceWeightedConsensus",
    "SwarmOrchestrator",
    "NativeCatalystMonitorAgent",
    "NativeVIFAnalystAgent",
    "NativeFinVizScreenerAgent",
    "CriticAgent",
    "NativeSwingScreenerAgent",
    "NativeVectorBTAgent",
    "NativeAutoResearchAgent",
    "NativeSignalVerifierAgent",
    "RiskAgent",
]
