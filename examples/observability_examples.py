#!/usr/bin/env python3
"""
Real-world examples of using the observability system.
Copy these patterns into your agents and scripts.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta

# Example 1: Basic Agent with Telemetry
def example_1_basic_agent():
    """
    Pattern: Wrap an agent with start/end logging
    """
    from utils.telemetry import get_telemetry

    tel = get_telemetry()
    start_time = time.time()

    # Log agent start
    tel.log_agent("example_agent", "start", "Processing 50 tickers from watchlist")

    try:
        # Your actual work here
        signals_generated = 12
        time.sleep(2)  # Simulate work

        # Log agent end
        duration = time.time() - start_time
        tel.log_agent(
            "example_agent", "end",
            "Analysis complete",
            duration_sec=duration,
            metrics={"signals_generated": signals_generated}
        )

        return {"status": "success", "signals": signals_generated}

    except Exception as e:
        tel.log_error(
            "example_agent",
            type(e).__name__,
            str(e),
            traceback=str(e.__traceback__)
        )
        raise


# Example 2: API Calls with Token Tracking
def example_2_api_calls():
    """
    Pattern: Log every API call with tokens and latency
    """
    from utils.telemetry import get_telemetry
    import anthropic

    tel = get_telemetry()
    client = anthropic.Anthropic()

    start = time.time()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": "What is 2+2?"}]
    )
    latency_ms = (time.time() - start) * 1000

    # Log the API call with actual token counts
    tel.log_api_call(
        operation="test_query",
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=latency_ms,
        model="claude-sonnet-4-6",
        success=True
    )

    return response


# Example 3: Pipeline with Multiple Stages
def example_3_pipeline():
    """
    Pattern: Log pipeline start, multiple stages, and completion
    """
    from utils.telemetry import get_telemetry

    tel = get_telemetry()
    start_time = time.time()

    # Pipeline start
    tel.log_pipeline("swing_trade_analysis", "start", stage="initialization")

    try:
        # Stage 1: Data fetching
        stage1_start = time.time()
        tickers_to_analyze = 50
        time.sleep(1)  # Simulate fetch
        tel.log_pipeline(
            "swing_trade_analysis", "end",
            stage="data_fetching",
            tickers_processed=tickers_to_analyze,
            duration_sec=time.time() - stage1_start
        )

        # Stage 2: Analysis
        stage2_start = time.time()
        tokens_used = 1500
        time.sleep(1)  # Simulate analysis
        tel.log_pipeline(
            "swing_trade_analysis", "end",
            stage="analysis",
            tickers_processed=tickers_to_analyze,
            tokens_used=tokens_used,
            duration_sec=time.time() - stage2_start
        )

        # Stage 3: Report generation
        stage3_start = time.time()
        time.sleep(0.5)  # Simulate report
        tel.log_pipeline(
            "swing_trade_analysis", "end",
            stage="reporting",
            duration_sec=time.time() - stage3_start
        )

    except Exception as e:
        tel.log_error("swing_trade_analysis", type(e).__name__, str(e))
        raise

    total_duration = time.time() - start_time
    print(f"Pipeline completed in {total_duration:.1f}s, {tokens_used} tokens")


# Example 4: Skill Invocation
def example_4_skill_invocation():
    """
    Pattern: Log when a skill is used (agent calls a skill)
    """
    from utils.telemetry import get_telemetry

    tel = get_telemetry()

    # An agent is invoking a skill
    try:
        # Call the skill (hypothetical)
        result = {"setup_count": 5, "failed": 0}

        # Log successful skill invocation
        tel.log_skill(
            skill_name="swing_setup_screener",
            invoked_by="watchlist_watcher",
            success=True,
            setups_found=result["setup_count"],
            errors=result["failed"]
        )

        return result

    except Exception as e:
        # Log failed skill invocation
        tel.log_skill(
            skill_name="swing_setup_screener",
            invoked_by="watchlist_watcher",
            success=False,
            error=str(e)
        )
        raise


# Example 5: Report Generation
def example_5_report_generation():
    """
    Pattern: Log when reports are generated
    """
    from utils.telemetry import get_telemetry

    tel = get_telemetry()

    # Generate a report
    report_path = "reports/daily/swing_trade_recommendations.md"
    sections = ["Overview", "Top Setup", "Risk Analysis", "Watch List"]

    tel.log_report_generated(
        report_name="swing_trade_recommendations",
        report_type="markdown",
        file_path=report_path,
        sections=len(sections),
        tickers_analyzed=85,
        signals_generated=8
    )

    print(f"Report generated: {report_path} ({len(sections)} sections)")


# Example 6: Error Tracking with Full Context
def example_6_error_tracking():
    """
    Pattern: Comprehensive error logging
    """
    from utils.telemetry import get_telemetry
    import traceback

    tel = get_telemetry()

    try:
        # Simulate an error
        result = 1 / 0

    except ZeroDivisionError as e:
        tel.log_error(
            component="data_fetcher",
            error_type="ZeroDivisionError",
            message="Division by zero when calculating RSI",
            traceback=traceback.format_exc(),
            ticker="NVDA",
            operation="calculate_indicator"
        )
        print("Error logged to telemetry")


# Example 7: Workflow Run (Full Execution)
def example_7_workflow_run():
    """
    Pattern: Log a complete workflow execution
    """
    from utils.telemetry import get_telemetry

    tel = get_telemetry()
    start_time = time.time()

    total_steps = 5
    steps_completed = 0

    # Simulate workflow steps
    for step in range(total_steps):
        steps_completed += 1
        time.sleep(0.5)  # Simulate work

    duration = time.time() - start_time

    tel.log_workflow_run(
        workflow_name="daily_premarket",
        triggered_by="scheduler",
        steps_completed=steps_completed,
        total_steps=total_steps,
        duration_sec=duration,
        watchlists_analyzed=3,
        total_signals=15
    )


# Example 8: Reading Telemetry Summary
def example_8_read_telemetry():
    """
    Pattern: Query telemetry for monitoring/analytics
    """
    from utils.telemetry import get_telemetry

    tel = get_telemetry()

    # Get summary of last 24 hours
    summary = tel.get_telemetry_summary(hours=24)

    print("=== 24-Hour Summary ===")
    print(f"Total events: {summary['total_events']}")
    print(f"\nBy event type:")
    for event_type, count in summary['by_event_type'].items():
        print(f"  {event_type}: {count}")
    print(f"\nBy component:")
    for component, count in summary['by_component'].items():
        print(f"  {component}: {count}")
    print(f"\nErrors: {len(summary['errors'])}")
    for error in summary['errors'][:3]:
        print(f"  - [{error['timestamp']}] {error['component']}: {error['error']}")


# Example 9: Cost Analysis
def example_9_cost_analysis():
    """
    Pattern: Analyze costs from telemetry
    """
    from utils.telemetry import get_telemetry
    import json

    tel_file = Path("logs/telemetry.jsonl")

    if not tel_file.exists():
        print("No telemetry data yet")
        return

    total_tokens = 0
    api_calls = 0
    avg_latency = 0

    with open(tel_file) as f:
        for line in f:
            event = json.loads(line)

            if event['event_type'] == 'api_call':
                api_calls += 1
                tokens = event.get('metrics', {}).get('total_tokens', 0)
                total_tokens += tokens
                latency = event.get('metrics', {}).get('latency_ms', 0)
                avg_latency += latency

    if api_calls > 0:
        avg_latency = avg_latency / api_calls
        cost = (total_tokens * 0.003) / 1_000_000  # $0.003 per 1M tokens

        print("=== Cost Analysis ===")
        print(f"API Calls: {api_calls}")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"Total Cost: ${cost:.4f}")
        print(f"Cost per Call: ${cost / api_calls:.5f}")
        print(f"Avg Latency: {avg_latency:.0f}ms")


# Example 10: Component Performance Analysis
def example_10_performance_analysis():
    """
    Pattern: Find slowest/fastest components
    """
    from utils.telemetry import get_telemetry
    import json

    tel_file = Path("logs/telemetry.jsonl")

    if not tel_file.exists():
        print("No telemetry data yet")
        return

    durations = {}

    with open(tel_file) as f:
        for line in f:
            event = json.loads(line)

            if event['event_type'] in ['agent_end', 'pipeline_end'] and event.get('duration_sec'):
                component = event['component']
                duration = event['duration_sec']

                if component not in durations:
                    durations[component] = []
                durations[component].append(duration)

    print("=== Performance Analysis ===")
    for component, times in sorted(durations.items()):
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        runs = len(times)

        print(f"\n{component}:")
        print(f"  Runs: {runs}")
        print(f"  Avg: {avg_time:.1f}s")
        print(f"  Min: {min_time:.1f}s")
        print(f"  Max: {max_time:.1f}s")


# Run all examples
if __name__ == '__main__':
    print("=" * 60)
    print("OBSERVABILITY EXAMPLES")
    print("=" * 60)

    print("\n[1] Basic Agent with Telemetry")
    try:
        result = example_1_basic_agent()
        print(f"✓ Result: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[2] API Calls with Token Tracking")
    try:
        response = example_2_api_calls()
        print(f"✓ Response received")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[3] Pipeline with Multiple Stages")
    try:
        example_3_pipeline()
        print(f"✓ Pipeline completed")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[4] Skill Invocation")
    try:
        result = example_4_skill_invocation()
        print(f"✓ Skill result: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[5] Report Generation")
    try:
        example_5_report_generation()
        print(f"✓ Report logged")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[6] Error Tracking")
    try:
        example_6_error_tracking()
        print(f"✓ Error logged")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[7] Workflow Run")
    try:
        example_7_workflow_run()
        print(f"✓ Workflow logged")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[8] Reading Telemetry Summary")
    try:
        example_8_read_telemetry()
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[9] Cost Analysis")
    try:
        example_9_cost_analysis()
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n[10] Performance Analysis")
    try:
        example_10_performance_analysis()
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("All examples completed")
    print("See logs/telemetry.jsonl for event details")
    print("=" * 60)
