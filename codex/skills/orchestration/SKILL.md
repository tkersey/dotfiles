---
name: orchestration
description: Orchestrate multi-agent swarms with agentic-flow for parallel task execution, dynamic topology, and coordinated state. Use when scaling beyond a single agent, coordinating specialist roles, running parallel or pipeline task graphs, or managing distributed AI workflows.
---

# Orchestration

## Overview
Orchestrate multi-agent swarms with agentic-flow using CLI hooks or SDK calls to coordinate roles, topology, execution mode, shared memory, and resiliency.

## Workflow
1. Confirm prerequisites: agentic-flow v1.5.11+ and Node.js 18+.
2. Define roles and outputs: list agents, responsibilities, and expected artifacts.
3. Choose topology: mesh for peer collaboration, hierarchical for clear ownership, adaptive for mixed workloads.
4. Initialize swarm: run swarm-init with topology and max agent cap.
5. Spawn agents: create specialized roles and verify they register.
6. Orchestrate tasks: pick parallel, pipeline, or adaptive mode based on dependency shape.
7. Coordinate shared memory: store schemas, decisions, and artifacts for cross-agent sync.
8. Monitor and recover: read metrics, enforce timeouts, and enable retries or reassignment.

## Topology and Mode Selection
- Mesh + parallel: use for exploratory, low-dependency work where agents can collaborate freely.
- Hierarchical + pipeline: use for staged deliverables with clear handoffs and a coordinating lead.
- Adaptive + auto-orchestrate: use for mixed task graphs or when the dependency shape is unclear.

## Guardrails
- Cap max agents early; scale only after initial results land.
- Set timeouts on every orchestration call; prefer retries with backoff.
- Use stable memory keys for shared artifacts (schemas, decisions, task status).
- Log task boundaries and outcomes so failures are traceable.

## References
- See `references/agentic-flow-cli.md` for CLI hooks and command templates.
- See `references/agentic-flow-sdk.md` for SDK examples and orchestration patterns.
