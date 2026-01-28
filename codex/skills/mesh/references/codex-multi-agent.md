# Codex Multi-Agent Reference (Codex CLI)

## Roles
- `default`: inherit parent configuration.
- `worker`: task-executing agent.
- `explorer`: fast repo research agent (optimized for search/reading).
- `orchestrator`: coordination-only; delegates substantive work.

## Core Tools
- `spawn_agent`: create a new agent.
  - Args: `{ "message": string, "agent_type"?: "default"|"worker"|"explorer"|"orchestrator" }`
  - Returns: `{ "agent_id": string }`
- `send_input`: send follow-up.
  - Args: `{ "id": string, "message": string, "interrupt"?: boolean }`
  - Notes: queued unless `interrupt=true`.
- `wait`: wait for one or more agents.
  - Args: `{ "ids": string[], "timeout_ms"?: number }`
  - Notes: returns when *any* id reaches a final status; completed statuses include the agent's final message payload.
  - Use longer timeouts (minutes) to avoid tight loops.
  - Timeout clamp: min 10_000ms, default 30_000ms, max 300_000ms.
- `close_agent`: close an agent when its work is fully integrated.
  - Args: `{ "id": string }`

## Execution Semantics
- Agents share the same workspace; instruct them to avoid conflicting edits.
- While a worker runs, you cannot observe intermediate state.
- `send_input` is processed only after the worker finishes unless `interrupt=true`.
- To redirect a running worker, use `send_input(interrupt=true)`.

## Limits / Feature Flags
- Multi-agent tools are gated behind the under-development feature flag `features.collab`.
- Concurrency can be capped by config: `agents.max_threads`.
- Spawning is also limited by a spawn-depth limit; when the depth limit is reached, `spawn_agent` fails.

## Defaults and Guardrails
- Codex enforces a max number of sub-agents per session; spawns fail when the limit is hit.
- By default, workers must not spawn sub-agents unless explicitly allowed.
- Always `close_agent` after integrating results to release slots.

## Example Calls
```json
{"message":"Scan repo for entry points and report findings.","agent_type":"worker"}
```

```json
{"id":"<agent-id>","message":"Focus on tests for module X.","interrupt":true}
```
