#!/usr/bin/env python3
"""
Unified telemetry system for VIF Trading System.
Logs ALL system events (agents, skills, pipelines, workflows) to a central JSONL file.
Designed to answer: "What ran when? What worked? What failed? Why?"
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
import os
import platform
import subprocess
from dataclasses import dataclass, asdict


class EventType(Enum):
    """All possible event types in the system."""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    SKILL_INVOKED = "skill_invoked"
    SUBAGENT_CREATED = "subagent_created"
    API_CALL = "api_call"
    PIPELINE_START = "pipeline_start"
    PIPELINE_END = "pipeline_end"
    WORKFLOW_RUN = "workflow_run"
    DATA_FETCH = "data_fetch"
    REPORT_GENERATED = "report_generated"
    ERROR_OCCURRED = "error_occurred"
    CACHE_HIT = "cache_hit"
    GIT_COMMIT = "git_commit"
    TEST_RUN = "test_run"
    SCHEDULE_TRIGGERED = "schedule_triggered"


class Severity(Enum):
    """Event severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemContext:
    """Captures system state at event time."""
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    git_status_dirty: Optional[bool] = None
    python_version: Optional[str] = None
    platform_info: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class Telemetry:
    """
    Central telemetry logger. Appends JSONL events to logs/telemetry.jsonl.
    Thread-safe. Lightweight.
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.telemetry_file = self.log_dir / "telemetry.jsonl"
        self.logger = logging.getLogger("telemetry")

        # Set up file handler for telemetry
        file_handler = logging.FileHandler(self.telemetry_file, mode='a')
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

        # Also log to console if in debug mode
        if os.environ.get('TELEMETRY_DEBUG'):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('[TELEMETRY] %(message)s'))
            self.logger.addHandler(console_handler)

    @staticmethod
    def get_system_context() -> SystemContext:
        """Capture current git/system state."""
        context = SystemContext(python_version=platform.python_version())

        try:
            context.platform_info = f"{platform.system()} {platform.release()}"

            # Git state (silently fail if not in git repo)
            try:
                git_dir = Path.cwd()
                if (git_dir / ".git").exists():
                    branch = subprocess.check_output(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=git_dir, text=True, stderr=subprocess.DEVNULL
                    ).strip()
                    context.git_branch = branch

                    commit = subprocess.check_output(
                        ["git", "rev-parse", "HEAD"],
                        cwd=git_dir, text=True, stderr=subprocess.DEVNULL
                    ).strip()[:8]
                    context.git_commit = commit

                    status = subprocess.check_output(
                        ["git", "status", "--porcelain"],
                        cwd=git_dir, text=True, stderr=subprocess.DEVNULL
                    ).strip()
                    context.git_status_dirty = len(status) > 0
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass  # Not in git repo or git not available
        except Exception:
            pass  # Silently fail

        return context

    def log_event(
        self,
        event_type: EventType,
        component: str,
        message: str,
        severity: Severity = Severity.INFO,
        duration_sec: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Log a system event.

        Args:
            event_type: Type of event (AGENT_START, SKILL_INVOKED, etc.)
            component: Component name (e.g., "watchlist_watcher", "swing_screener")
            message: Human-readable message
            severity: INFO, WARNING, ERROR, CRITICAL
            duration_sec: How long operation took (if applicable)
            metrics: Dict of numeric metrics (tokens, tickers, confidence, etc.)
            tags: List of tags for filtering (e.g., ["batch", "premarket"])
            error: Error message (if applicable)
            **kwargs: Additional context fields
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type.value,
            "component": component,
            "message": message,
            "severity": severity.value,
            "context": self.get_system_context().to_dict(),
        }

        if duration_sec is not None:
            event["duration_sec"] = round(duration_sec, 2)

        if metrics:
            event["metrics"] = metrics

        if tags:
            event["tags"] = tags

        if error:
            event["error"] = error

        if kwargs:
            event["extra"] = kwargs

        # Write as JSONL (one JSON object per line)
        self.logger.info(json.dumps(event))

    def log_agent(
        self,
        agent_name: str,
        action: str,  # "start", "end"
        message: str = "",
        duration_sec: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log agent lifecycle events (start/end)."""
        event_type = EventType.AGENT_START if action == "start" else EventType.AGENT_END
        severity = Severity.ERROR if error else Severity.INFO

        self.log_event(
            event_type=event_type,
            component=agent_name,
            message=message or f"Agent {action}",
            severity=severity,
            duration_sec=duration_sec,
            metrics=metrics,
            error=error,
            **kwargs
        )

    def log_skill(self, skill_name: str, invoked_by: str, success: bool, **kwargs) -> None:
        """Log skill invocation."""
        self.log_event(
            event_type=EventType.SKILL_INVOKED,
            component=skill_name,
            message=f"Skill invoked by {invoked_by}",
            severity=Severity.ERROR if not success else Severity.INFO,
            tags=["skill", invoked_by],
            **kwargs
        )

    def log_pipeline(
        self,
        pipeline_name: str,
        action: str,  # "start", "end"
        stage: Optional[str] = None,
        tickers_processed: Optional[int] = None,
        tokens_used: Optional[int] = None,
        duration_sec: Optional[float] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log pipeline lifecycle and metrics."""
        metrics = {
            "tickers": tickers_processed,
            "tokens": tokens_used,
        }
        metrics = {k: v for k, v in metrics.items() if v is not None}

        self.log_event(
            event_type=EventType.PIPELINE_START if action == "start" else EventType.PIPELINE_END,
            component=pipeline_name,
            message=f"Pipeline {action}" + (f" (stage: {stage})" if stage else ""),
            severity=Severity.ERROR if error else Severity.INFO,
            duration_sec=duration_sec,
            metrics=metrics or None,
            error=error,
            tags=["pipeline", stage] if stage else ["pipeline"],
            **kwargs
        )

    def log_api_call(
        self,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        model: str = "claude-sonnet-4-6",
        success: bool = True,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log Claude API calls."""
        total_tokens = input_tokens + output_tokens

        self.log_event(
            event_type=EventType.API_CALL,
            component="claude-api",
            message=f"API call: {operation}",
            severity=Severity.ERROR if not success else Severity.INFO,
            metrics={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency_ms,
            },
            error=error,
            tags=["api", model],
            model=model,
            **kwargs
        )

    def log_report_generated(
        self,
        report_name: str,
        report_type: str,  # "html", "json", "markdown"
        file_path: str,
        sections: int = 0,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log report generation."""
        self.log_event(
            event_type=EventType.REPORT_GENERATED,
            component=report_name,
            message=f"Report generated: {report_type}",
            severity=Severity.ERROR if error else Severity.INFO,
            metrics={"sections": sections} if sections > 0 else None,
            tags=["report", report_type],
            file_path=file_path,
            error=error,
            **kwargs
        )

    def log_workflow_run(
        self,
        workflow_name: str,
        triggered_by: str,  # "scheduler", "manual", "api"
        steps_completed: int = 0,
        total_steps: int = 0,
        duration_sec: Optional[float] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log complete workflow execution."""
        self.log_event(
            event_type=EventType.WORKFLOW_RUN,
            component=workflow_name,
            message=f"Workflow run triggered by {triggered_by}",
            severity=Severity.ERROR if error else Severity.INFO,
            duration_sec=duration_sec,
            metrics={
                "steps_completed": steps_completed,
                "total_steps": total_steps,
                "completion_percent": int(100 * steps_completed / total_steps) if total_steps > 0 else 0,
            },
            tags=["workflow", triggered_by],
            error=error,
            **kwargs
        )

    def log_error(
        self,
        component: str,
        error_type: str,
        message: str,
        traceback: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log errors with full context."""
        self.log_event(
            event_type=EventType.ERROR_OCCURRED,
            component=component,
            message=message,
            severity=Severity.ERROR,
            error=error_type,
            tags=["error", error_type],
            traceback=traceback,
            **kwargs
        )

    def get_telemetry_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Read and summarize recent telemetry events.

        Args:
            hours: Look back this many hours

        Returns:
            Dictionary with summary stats
        """
        if not self.telemetry_file.exists():
            return {"error": "No telemetry data yet"}

        cutoff_time = datetime.now(timezone.utc)
        from datetime import timedelta
        cutoff_time = cutoff_time - timedelta(hours=hours)

        stats = {
            "total_events": 0,
            "by_event_type": {},
            "by_component": {},
            "by_severity": {},
            "errors": [],
            "recent_api_calls": [],
        }

        try:
            with open(self.telemetry_file, 'r') as f:
                for line in f:
                    event = json.loads(line)
                    event_time = datetime.fromisoformat(event['timestamp'])

                    if event_time < cutoff_time:
                        continue

                    stats["total_events"] += 1

                    # By event type
                    evt_type = event['event_type']
                    stats["by_event_type"][evt_type] = stats["by_event_type"].get(evt_type, 0) + 1

                    # By component
                    component = event['component']
                    stats["by_component"][component] = stats["by_component"].get(component, 0) + 1

                    # By severity
                    severity = event['severity']
                    stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1

                    # Collect errors
                    if event['severity'] in ['error', 'critical']:
                        stats["errors"].append({
                            "timestamp": event['timestamp'],
                            "component": component,
                            "message": event['message'],
                            "error": event.get('error'),
                        })

                    # Collect API calls
                    if event['event_type'] == 'api_call':
                        stats["recent_api_calls"].append({
                            "timestamp": event['timestamp'],
                            "operation": event['message'],
                            "tokens": event.get('metrics', {}).get('total_tokens'),
                            "latency_ms": event.get('metrics', {}).get('latency_ms'),
                        })
        except Exception as e:
            stats["read_error"] = str(e)

        return stats


# Global telemetry instance
_telemetry = None


def get_telemetry() -> Telemetry:
    """Get or create global telemetry instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry()
    return _telemetry


# Example usage
if __name__ == '__main__':
    tel = get_telemetry()

    # Log some example events
    tel.log_agent("watchlist_watcher", "start", "Starting analysis of 85 tickers")
    tel.log_api_call("vif_analysis", 1200, 450, 2300, success=True)
    tel.log_pipeline("vif_analysis", "start", stage="data_fetching", tickers_processed=85)
    tel.log_skill("vif-screener", invoked_by="watchlist_watcher", success=True)
    tel.log_report_generated("SWING_TRADE_RECOMMENDATIONS", "markdown", "reports/daily/swing.md", sections=5)
    tel.log_agent("watchlist_watcher", "end", "Analysis complete", duration_sec=45.2, metrics={"signals_generated": 12})

    # Print summary
    print("\nTelemetry Summary (last 24h):")
    summary = tel.get_telemetry_summary(hours=24)
    print(json.dumps(summary, indent=2))
