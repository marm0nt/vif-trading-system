# VIF v4.0 Agentic Workflow Diagram

```mermaid
graph TD
    A["🎯 Lead Orchestrator<br/>orchestrator_lead.py"] -->|Task Decomposition<br/>Tree of Thoughts| B["🧠 Task Router<br/>gossip_router.py"]
    
    B -->|Route Subtasks| C["⚡ KV Cache Layer<br/>LRAgent Pattern<br/>45-50% Hit Rate"]
    B -->|Route Subtasks| D["🧠 Latent Memory<br/>LatentMAS<br/>Hidden State Exchange"]
    
    C --> E["Agent Pool<br/>9 Specialists"]
    D --> E
    
    E --> E1["Catalyst Monitor<br/>Earnings & Policy"]
    E --> E2["VIF Analyst<br/>Volatility Framework"]
    E --> E3["FinViz Screener<br/>Fundamentals"]
    E --> E4["Swing Screener<br/>5 Setup Types"]
    E --> E5["Signal Verifier<br/>4-Gate Validation"]
    E --> E6["Critic Agent<br/>Low-Conf Audit"]
    E --> E7["Risk Agent<br/>Position Sizing"]
    E --> E8["VectorBT Analyst<br/>Backtesting"]
    E --> E9["Autoresearch<br/>Research Synthesis"]
    
    E1 --> F["🔍 Consensus Layer<br/>ConfidenceWeightedConsensus<br/><5% Conflicts"]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F
    E7 --> F
    E8 --> F
    E9 --> F
    
    F --> G["📊 Structured Output<br/>JSON + HTML + OTel"]
    G --> H["🎯 Lead Orchestrator Returns<br/>trace_id + metrics + consensus"]
    
    H -->|Execute Mode| H1["premarket<br/>07:00 CT"]
    H -->|Execute Mode| H2["market_open<br/>09:35 CT"]
    H -->|Execute Mode| H3["afterhours<br/>16:05 CT"]
    H -->|Execute Mode| H4["weekend<br/>Sat/Sun"]
    H -->|Execute Mode| H5["full<br/>On-Demand"]
    
    style A fill:#4CAF50,stroke:#2E7D32,color:#fff
    style B fill:#2196F3,stroke:#1565C0,color:#fff
    style C fill:#FF9800,stroke:#E65100,color:#fff
    style D fill:#FF9800,stroke:#E65100,color:#fff
    style E fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style F fill:#F44336,stroke:#C62828,color:#fff
    style G fill:#00BCD4,stroke:#006064,color:#fff
    style H fill:#4CAF50,stroke:#2E7D32,color:#fff
```

## Recovery State Machine (GitOps + Checkpointing)

```mermaid
stateDiagram-v2
    [*] --> DiagnosticPhase: Start Recovery
    
    DiagnosticPhase --> CheckGitConfig: Check repositoryformatversion
    CheckGitConfig --> GitMismatch{Format v0<br/>+ worktreeConfig?}
    
    GitMismatch -->|YES| FixGitFormat: Upgrade to v1
    GitMismatch -->|NO| CheckIDESettings
    
    FixGitFormat --> VerifyWorktrees: Test worktree list
    VerifyWorktrees --> CheckIDESettings
    
    CheckIDESettings --> CheckMCP: Check MCP servers
    CheckMCP --> CheckHooks: Check post-commit hook
    
    CheckHooks --> HookTest: Test hook manually
    HookTest --> HookWorks{Hook<br/>Functional?}
    
    HookWorks -->|YES| RecoveryComplete
    HookWorks -->|NO| FixHook: Enable bash execution
    FixHook --> RecoveryComplete
    
    RecoveryComplete --> Checkpoint: Save Recovery Checkpoint
    Checkpoint --> ValidateAgents: Validate agent pool
    ValidateAgents --> [*]: Ready for Production
    
    note right of DiagnosticPhase
        ReAct Loop: Observe → Diagnose → Act
    end note
    
    note right of RecoveryComplete
        Stateful Recovery: All fixes
        are non-destructive & reversible
    end note
```

## Cost Impact (Pre/Post Recovery)

```mermaid
xychart-beta
    title VIF v4.0 Cost Optimization (Post-Recovery)
    x-axis [Subprocess, Swarm v0, Swarm v1+]
    y-axis "Daily Cost ($)" 0 --> 0.15
    
    line [0.13, 0.10, 0.07]
    
    note: Cost reduction achieved via:
    - KV Cache Sharing (45-50% hit)
    - Latent State Collaboration
    - Gossip Routing Efficiency
    - Confidence-Weighted Consensus
```

---

## Workflow Execution Timeline

| Time (CT) | Mode | Agents Active | Output |
|-----------|------|---------------|--------|
| 07:00 | premarket | Catalyst + VIF + Swing | Breakfast briefing |
| 09:35 | market_open | Swing | Opening setup |
| 12:00 | (custom) | Any agent pool | Ad-hoc analysis |
| 16:05 | afterhours | VIF + Risk | Daily wrap |
| Sat/Sun | weekend | Catalyst + Autoresearch | Monday prep |

---

## Security & Observability

```
Every orchestrator execution generates:
┌─────────────────────────────────────┐
│ trace_id (unique session ID)        │
├─────────────────────────────────────┤
│ OTel spans (agent-level metrics)    │
├─────────────────────────────────────┤
│ Git commit (with trace_id + reason) │
├─────────────────────────────────────┤
│ logs/orchestrator_lead.log          │
├─────────────────────────────────────┤
│ logs/otel/*.jsonl (structured data) │
└─────────────────────────────────────┘

Full audit trail: reproducible & verifiable
```
