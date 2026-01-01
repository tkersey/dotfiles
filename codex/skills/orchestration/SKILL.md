---
name: orchestration
description: Orchestrate multi-agent swarms with agentic-flow (roles, topology, modes, shared state, resiliency).
---

# Orchestration

## When to use
- You need more than one agent.
- Work splits cleanly into parallel lanes or a pipeline.
- You need coordinated outputs, shared memory, or retry/timeout policy.

## Workflow
1. Confirm prerequisites (agentic-flow v1.5.11+, Node.js 18+).
2. Define roles and expected artifacts.
3. Choose topology:
   - Mesh for exploratory, low-dependency collaboration.
   - Hierarchical for clear ownership and handoffs.
   - Adaptive when the dependency graph is unclear.
4. Initialize and spawn agents.
5. Pick execution mode (parallel/pipeline/adaptive).
6. Coordinate shared memory (schemas, decisions, task status).
7. Monitor and recover (timeouts, retries, reassignment).

## Guardrails
- Cap agents early; scale after results land.
- Put timeouts on orchestration calls; retry with backoff.
- Use stable memory keys; log task boundaries.

## References
- `references/agentic-flow-cli.md`
- `references/agentic-flow-sdk.md`
