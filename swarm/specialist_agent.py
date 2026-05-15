"""
Specialist Agent - Base Class for Swarm Agents

All agents inherit from this. Provides KV cache binding, latent memory interface,
and async execution model.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
from functools import lru_cache


class PromptLoader:
    """
    Load compiled prompt strings from config/prompts_compiled.json.

    Zero dspy import at runtime. DSPy optimizer runs offline and exports to JSON.
    """

    PROMPTS_PATH = Path("config/prompts_compiled.json")
    EXPECTED_PROMPT_VERSION = "1.0"

    @classmethod
    @lru_cache(maxsize=1)
    def load(cls) -> dict:
        """Load prompts JSON file (cached)."""
        if cls.PROMPTS_PATH.exists():
            try:
                return json.loads(cls.PROMPTS_PATH.read_text())
            except Exception as e:
                print(f"WARNING: Failed to load compiled prompts: {e}")
                return {}
        return {}

    @classmethod
    def get_system_prompt(cls, prompt_key: str, fallback: str = "") -> str:
        """Get system prompt for a specific key (e.g., 'vif_signal', 'catalyst')."""
        data = cls.load()
        return data.get(prompt_key, {}).get("system", fallback)

    @classmethod
    def get_few_shots(cls, prompt_key: str) -> list:
        """Get few-shot examples for a specific key."""
        data = cls.load()
        return data.get(prompt_key, {}).get("few_shots", [])

    @classmethod
    def prompt_version(cls) -> str:
        """Get compiled prompts version."""
        return cls.load().get("version", "unknown")

    @classmethod
    def validate_version(cls, expected: str = None) -> bool:
        """Check if prompt version matches expected (or EXPECTED_PROMPT_VERSION if not specified)."""
        if expected is None:
            expected = cls.EXPECTED_PROMPT_VERSION
        actual = cls.prompt_version()
        if actual != expected:
            print(f"WARNING: Compiled prompt version mismatch. Expected {expected}, got {actual}. Run 'python research/dspy_compiler.py --export' to refresh.")
            return False
        return True


class SpecialistAgent:
    """
    Base class for all specialist agents in the swarm.

    Handles:
    - KV cache binding (shared backbone + LoRA-specific)
    - Latent hidden state reading/writing
    - Async execution with task context
    """

    def __init__(self, agent_id: str, agent_type: str, role_description: str):
        """
        Initialize specialist agent.

        Args:
            agent_id: Unique identifier (e.g., "vif-analyst-1")
            agent_type: Type (e.g., "vif-analyst", "catalyst-monitor", "swing-screener")
            role_description: Human-readable role description
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.role_description = role_description

        # Execution context (set during orchestration)
        self.kv_cache_binding = None
        self.latent_memory = None
        self.task_context = {}

        # Anthropic client for agents that call Claude directly (e.g., Munger inversion audit)
        try:
            import anthropic
            self.client = anthropic.Anthropic()
        except Exception:
            self.client = None

        # Metrics
        self.execution_count = 0
        self.last_execution_time = None
        self.last_result = None

    def execute(self,
                subtasks: List[Dict],
                kv_cache_binding: Any,
                latent_memory: Any,
                task_context: Dict) -> Dict[str, Any]:
        """
        Execute agent with swarm context.

        Args:
            subtasks: List of subtasks assigned to this agent
            kv_cache_binding: Shared KV cache binding from orchestrator
            latent_memory: Shared latent working memory from orchestrator
            task_context: Task-level context (watchlists, period, etc.)

        Returns:
            Result dict with signals, metrics, hidden states
        """
        self.kv_cache_binding = kv_cache_binding
        self.latent_memory = latent_memory
        self.task_context = task_context

        start_time = datetime.utcnow()

        try:
            # 1. Read latent context from other agents
            latent_context = self._read_latent_context()

            # 2. Execute subtasks with KV cache binding
            result = self._execute_subtasks(subtasks, latent_context)

            # 3. Write hidden states for downstream agents
            self._write_latent_states(result)

            # 4. Update metrics
            self.execution_count += 1
            self.last_execution_time = datetime.utcnow()
            self.last_result = result

            return {
                "agent_id": self.agent_id,
                "status": "success",
                "signals": result.get("signals", {}),
                "metrics": result.get("metrics", {}),
                "hidden_states": result.get("hidden_states", {}),
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            }

        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "status": "failed",
                "error": str(e),
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            }

    def _read_latent_context(self) -> Dict[int, Any]:
        """
        Read latent hidden states from peer agents.

        Returns:
            Dict mapping layer → hidden state tensor (or empty if none available)
        """
        if self.latent_memory is None:
            return {}

        # Read from default layers (8, 16, 24)
        return self.latent_memory.read_hidden_states(
            agent_id=self.agent_id,
            source_agents=None  # Read from all other agents
        )

    def _execute_subtasks(self, subtasks: List[Dict], latent_context: Dict) -> Dict[str, Any]:
        """
        Execute assigned subtasks with KV cache binding + latent context.

        Subclasses override this to implement task-specific logic.

        Args:
            subtasks: List of subtask dicts
            latent_context: Hidden states from peer agents

        Returns:
            Result dict with "signals", "metrics", "hidden_states" keys
        """
        # Default implementation: no-op
        # Subclasses (VIFAnalyst, CatalystMonitor, etc.) override this
        return {
            "signals": {},
            "metrics": {},
            "hidden_states": {},
        }

    def _write_latent_states(self, result: Dict):
        """
        Write hidden states to latent working memory for downstream agents.

        Args:
            result: Result dict containing "hidden_states" key
        """
        if self.latent_memory is None:
            return

        hidden_states = result.get("hidden_states", {})
        if hidden_states:
            self.latent_memory.write_hidden_states(
                agent_id=self.agent_id,
                hidden_states_dict=hidden_states
            )

    def with_cache_binding(self, binding: Any) -> "SpecialistAgent":
        """Convenience: set cache binding for manual execution."""
        self.kv_cache_binding = binding
        return self

    def with_latent_memory(self, memory: Any) -> "SpecialistAgent":
        """Convenience: set latent memory for manual execution."""
        self.latent_memory = memory
        return self

    def health_check(self) -> Dict[str, Any]:
        """Return agent health status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution_time.isoformat() if self.last_execution_time else None,
            "last_status": "success" if self.last_result and self.last_result.get("status") == "success" else "unknown",
        }
