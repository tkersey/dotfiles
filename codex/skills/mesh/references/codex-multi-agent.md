# Codex Multi-Agent Reference (Concise)

## Roles
- `default`: inherit parent configuration.
- `orchestrator`: coordination-only; delegate substantive work to workers.
- `worker`: task-executing agent (Codex uses a fixed worker model).

## Core Tools
- `spawn_agent`: create a new agent. Required: `message`. Optional: `agent_type` (`default`, `orchestrator`, `worker`).
- `send_input`: send follow-up; queued unless `interrupt=true`.
- `wait`: wait for one or more agents; use scaled timeouts.
- `close_agent`: close an agent when its work is fully integrated.

## Execution Semantics
- Agents share the same workspace; instruct them to avoid conflicting edits.
- While a worker runs, you cannot observe intermediate state.
- `send_input` is processed only after the worker finishes unless `interrupt=true`.
- To redirect a running worker, use `send_input(interrupt=true)`.

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
