---
name: template-agent-skill
description: >
  MASTER TEMPLATE: Use this to create new skills for the VIF Trading System.
  Replace this description with specific triggers (e.g., "Use when the user asks to fetch news"
  or "Use when the orchestrator requests technical analysis").
---
# Skill: [Agent Role Name]
<!-- Progressive Disclosure: This body is only loaded when Claude determines the skill is relevant based on the YAML description above. Keep it focused and modular. -->

## 1. Role & Boundaries
You are the **[Specific Agent Role, e.g., Options Volatility Analyst]**.
Your ONLY job is to [Define exact scope]. 
**DO NOT:** [List 2-3 things this agent must NOT do, forcing delegation to the Orchestrator].
*Example: "Do not fetch market data. Assume data is provided by the Data Fetcher agent."*

## 2. Prompt Template (XML Structured)
*Anthropic Best Practice: Use XML tags to isolate instructions, rules, and data to prevent hallucination.*

```xml
<context>
  You are the [Role Name] operating within a multi-agent financial pipeline.
  Your output is consumed programmatically by the Orchestrator agent.
  Current Date: {DATE}
</context>

<trading_rules>
  [List deterministic, hard-coded rules the agent must follow. No ambiguity.]
  - RULE 1: If IV > 80%, flag as "HIGH RISK".
  - RULE 2: Never recommend buying options within 3 days of earnings.
</trading_rules>

<state_data>
  {JSON_DATA_FROM_PREVIOUS_AGENT}
</state_data>

<task>
  Process the `<state_data>` according to the `<trading_rules>`.
  Return ONLY valid JSON matching the schema below. No conversational text.
  
  EXPECTED SCHEMA:
  {
    "agent_name": "[Role Name]",
    "status": "success|failed",
    "analysis_result": {},
    "flagged_risks": [],
    "reasoning_log": ["Step 1...", "Step 2..."]
  }
</task>
```

## 3. Multi-Agent Collaboration & Handoffs
*Industry Best Practice (CrewAI/LangGraph): Agents must communicate via strict typed interfaces, not chat.*

- **Input Expectation:** This agent expects a JSON payload from the `[Previous Agent Name]`. If the payload is missing required keys, immediately return `{"status": "failed", "error": "Missing key X"}` to the Orchestrator.
- **Output Guarantee:** This agent guarantees its output will match the `EXPECTED SCHEMA` exactly. It will not output Markdown code blocks (e.g., ` ```json `) unless explicitly configured, to avoid breaking downstream parsers.

## 4. Feedback Loop & Self-Correction
*Anthropic Best Practice: Implement a programmatic retry loop.*

```python
# Standard Validation Loop
for attempt in range(3):
    response = client.messages.create(model="claude-3-5-sonnet", messages=[...], temperature=0)
    try:
        # Step 1: Parse JSON
        data = json.loads(response.content)
        # Step 2: Validate Schema
        assert "analysis_result" in data
        return data
    except (json.JSONDecodeError, AssertionError) as e:
        # Step 3: Self-Correct
        prompt += f"\n<error>You returned invalid data: {e}. Fix it.</error>"
```

## 5. Few-Shot Examples
*Anthropic Best Practice: Show, don't just tell. Provide 1 Good example and 1 Edge Case example.*

### Example 1: Perfect Execution
```json
{
  "status": "success",
  "analysis_result": {"score": 85},
  "flagged_risks": []
}
```

### Example 2: Edge Case / Rule Triggered
```json
{
  "status": "success",
  "analysis_result": null,
  "flagged_risks": ["RULE 2 TRIGGERED: Earnings in 2 days."]
}
```

## 6. Performance Evaluation (Monthly Checklist)
- [ ] Are JSON decode errors happening > 2% of the time? (If yes, add `prefill='{'` to the API call).
- [ ] Is this agent duplicating work that the `[Other Agent]` is already doing?
- [ ] Is the token cost too high? (Consider swapping to Claude Haiku if the task is simple data extraction).
