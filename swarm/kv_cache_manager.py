"""
KV Cache Manager - LRAgent Pattern Implementation

Efficient KV cache sharing for multi-agent systems.
Reference: arXiv 2602.01053 (LRAgent)

Shared pretrained backbone cache + per-agent LoRA-specific cache.
Reduces memory usage and latency while preserving role-specific behavior.
"""

from collections import OrderedDict
from typing import Dict, Optional, Tuple, Any
import json
from datetime import datetime


class KVCacheBinding:
    """Binding context for agent KV cache access."""

    def __init__(self,
                 shared_backbone: Dict,
                 per_agent_lora: Dict,
                 agent_id: str,
                 max_recompute_layers: int = 3):
        self.shared_backbone = shared_backbone
        self.per_agent_lora = per_agent_lora
        self.agent_id = agent_id
        self.max_recompute_layers = max_recompute_layers  # DroidSpeak: only recompute top N layers
        self.hit_count = 0
        self.miss_count = 0

    def get(self, layer: int, key: str = "k") -> Optional[Any]:
        """Get KV cache for layer (check shared backbone first, then LoRA)."""
        cache_key = f"{layer}_{key}"

        # Try LoRA-specific cache first
        if cache_key in self.per_agent_lora:
            self.hit_count += 1
            return self.per_agent_lora[cache_key]

        # Fall back to shared backbone
        if cache_key in self.shared_backbone:
            self.hit_count += 1
            return self.shared_backbone[cache_key]

        self.miss_count += 1
        return None

    def put(self, layer: int, value: Any, key: str = "k", shared: bool = False):
        """Put KV cache (shared backbone or LoRA-specific)."""
        cache_key = f"{layer}_{key}"

        if shared:
            self.shared_backbone[cache_key] = value
        else:
            self.per_agent_lora[cache_key] = value

    def hit_rate(self) -> float:
        """Current session hit rate."""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class LRUCache:
    """LRU cache for KV storage (Least Recently Used eviction)."""

    def __init__(self, max_size_mb: int = 500):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: OrderedDict = OrderedDict()
        self.current_size = 0
        self.eviction_count = 0

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key: str, value: Any, size_bytes: int):
        """Put item in cache, evict LRU if needed."""
        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
            return

        # Add new item
        while self.current_size + size_bytes > self.max_size_bytes and self.cache:
            evict_key, evict_val = self.cache.popitem(last=False)
            self.current_size -= self._estimate_size(evict_val)
            self.eviction_count += 1

        self.cache[key] = value
        self.current_size += size_bytes

    @staticmethod
    def _estimate_size(value: Any) -> int:
        """Estimate tensor/object size in bytes."""
        try:
            import numpy as np
            if hasattr(value, 'nbytes'):
                return value.nbytes
        except:
            pass
        # Conservative estimate: 1KB per object
        return 1024


class KVCacheManager:
    """
    KV Cache Manager implementing LRAgent pattern.

    Manages shared pretrained backbone cache + per-agent LoRA caches.
    Implements selective layer recomputation (DroidSpeak).
    """

    def __init__(self, max_cache_mb: int = 500, max_recompute_layers: int = 3):
        self.shared_backbone_cache = {}  # Shared across all agents
        self.agent_lora_caches: Dict[str, Dict] = {}  # Per-agent task-specific
        self.max_size_mb = max_cache_mb
        self.max_recompute_layers = max_recompute_layers
        self.lru = LRUCache(max_cache_mb)

        # Metrics
        self.sessions_created = 0
        self.total_hits = 0
        self.total_misses = 0
        self.session_history = []

    def create_session(self, agent_id: str, shared_backbone: bool = True, per_agent_lora: bool = True) -> KVCacheBinding:
        """
        Create KV cache binding for an agent.

        Args:
            agent_id: Unique agent identifier
            shared_backbone: Use shared pretrained backbone cache
            per_agent_lora: Use per-agent LoRA-specific cache

        Returns:
            KVCacheBinding ready for use
        """
        # Initialize per-agent LoRA cache if needed
        if agent_id not in self.agent_lora_caches:
            self.agent_lora_caches[agent_id] = {}

        binding = KVCacheBinding(
            shared_backbone=self.shared_backbone_cache if shared_backbone else {},
            per_agent_lora=self.agent_lora_caches[agent_id] if per_agent_lora else {},
            agent_id=agent_id,
            max_recompute_layers=self.max_recompute_layers
        )

        self.sessions_created += 1
        return binding

    def finalize_session(self, binding: KVCacheBinding):
        """Finalize session, update global metrics."""
        self.total_hits += binding.hit_count
        self.total_misses += binding.miss_count

        self.session_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": binding.agent_id,
            "hit_count": binding.hit_count,
            "miss_count": binding.miss_count,
            "hit_rate": binding.hit_rate(),
        })

    def global_hit_rate(self) -> float:
        """Global cache hit rate across all sessions."""
        total = self.total_hits + self.total_misses
        return self.total_hits / total if total > 0 else 0.0

    def eviction_rate(self) -> float:
        """Cache eviction rate (LRU evictions per session)."""
        return self.lru.eviction_count / self.sessions_created if self.sessions_created > 0 else 0.0

    def metrics(self) -> Dict[str, Any]:
        """Return cache metrics for monitoring."""
        return {
            "sessions_created": self.sessions_created,
            "global_hit_rate": self.global_hit_rate(),
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "eviction_count": self.lru.eviction_count,
            "eviction_rate": self.eviction_rate(),
            "max_cache_mb": self.max_size_mb,
            "current_shared_cache_items": len(self.shared_backbone_cache),
            "per_agent_caches": {agent_id: len(cache) for agent_id, cache in self.agent_lora_caches.items()},
        }

    def clear_agent_cache(self, agent_id: str):
        """Clear agent-specific LoRA cache (for memory cleanup)."""
        if agent_id in self.agent_lora_caches:
            self.agent_lora_caches[agent_id].clear()

    def clear_all(self):
        """Clear all caches (full reset)."""
        self.shared_backbone_cache.clear()
        self.agent_lora_caches.clear()
        self.lru.cache.clear()
        self.lru.current_size = 0
