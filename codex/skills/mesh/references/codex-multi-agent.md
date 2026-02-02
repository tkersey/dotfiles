# Codex Multi-Agent Reference (Codex CLI)

## Roles
- `default`: inherit parent configuration.
- `worker`: task-executing agent.
- `explorer`: fast repo research agent (optimized for search/reading).

Notes:
- Codex defines an `orchestrator` role internally, but it is not currently advertised as a stable/primary role in the collab tool schema (it is excluded from the enum values Codex prints in tool descriptions). Treat it as experimental.
- Current Codex depth guard is very tight (see "Spawn depth" below): child agents should be assumed unable to spawn further agents.

## Core Tools
- `spawn_agent`: create a new agent.
  - Args: `{ "message": string, "agent_type"?: string }`
  - Recommended `agent_type` values (snake_case): `default`, `worker`, `explorer`.
  - `agent_type="orchestrator"` may exist but should be considered experimental.
  - Returns: `{ "agent_id": string }`
- `send_input`: send follow-up.
  - Args: `{ "id": string, "message": string, "interrupt"?: boolean }`
  - Notes: when `interrupt=false` (default), the message is queued; when `interrupt=true`, Codex interrupts the agent's current task and handles the message immediately.
- `wait`: wait for one or more agents.
  - Args: `{ "ids": string[], "timeout_ms"?: number }`
  - Returns: `{ "status": { <thread_id>: <AgentStatus> }, "timed_out": boolean }`
  - Notes: returns when *any* id reaches a final status; completed statuses include the agent's final message payload.
  - Use longer timeouts (minutes) to avoid tight loops.
  - Timeout clamp: min 10_000ms, default 30_000ms, max 300_000ms.
- `close_agent`: close an agent when its work is fully integrated.
  - Args: `{ "id": string }`
  - Returns: `{ "status": <AgentStatus> }`

## Execution Semantics
- Agents share the same workspace; instruct them to avoid conflicting edits.
- While a worker runs, you cannot observe intermediate state.
- `send_input` is queued unless `interrupt=true`.
- To redirect a running worker, use `send_input(interrupt=true)`.

## Limits / Feature Flags
- Multi-agent tools are gated behind the under-development feature flag `[features].collab = true`.
- Concurrency can be capped by config: `[agents].max_threads`.

Spawn depth:
- Codex enforces a thread spawn depth limit (currently `MAX_THREAD_SPAWN_DEPTH = 1` in the Codex repo).
- When the depth limit would be exceeded, `spawn_agent` fails.
- When an agent is spawned at the maximum depth, Codex disables collab tools for that child agent (so it cannot spawn further agents).

## Defaults and Guardrails
- Codex enforces a thread limit (`[agents].max_threads`) and a spawn-depth limit; spawns fail when limits are hit.
- By default, workers must not spawn sub-agents unless explicitly allowed.
- Always `close_agent` after integrating results to release slots.

## Example Calls
```json
{"message":"Scan repo for entry points and report findings.","agent_type":"worker"}
```

```json
{"id":"<agent-id>","message":"Focus on tests for module X.","interrupt":true}
```
