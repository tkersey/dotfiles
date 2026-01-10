---
name: mesh
description: Orchestrate multiple Codex sub-agents via cx to work beads in parallel and deliver PRs; use whenever a bead (or set of beads) is being worked and multi-agent coordination, dependency scheduling, or progress consolidation is needed.
---

# mesh

## Workflow

1. Confirm a beads repo by running
   `rg --files -g '.beads/**' --hidden --no-ignore`; if no matches, stop and ask
   for direction.
2. Identify the target beads (explicit IDs, or `bd ready`/`bd in-progress`) and
   confirm scope with the user.
3. Build a dependency-aware batch plan (ready now vs blocked) and list the
   first wave.
4. Decide concurrency and prioritization; if unspecified, ask for a cap and a
   priority rule.
5. Compose one agent prompt per bead using the template below.
6. Dispatch each agent with `codex/skills/cx/scripts/cx-exec.sh "..."` (or the
   user’s chosen Opencode equivalent).
7. Monitor updates and require each agent to post a bead comment with PR link +
   verification.
8. Consolidate a single status summary: completed PRs, active blockers, and the
   next wave.

## Scheduling & Wave Planning

Use this decision procedure when selecting a wave. The goal is repeatable
ordering with a human override.

1. Build the status map:
   - `bd swarm status <epic-id>` to compute Ready/Blocked/Active/Completed.
   - Optional: `bd swarm validate <epic-id>` to surface fronts (integration or
     checkpoint bottlenecks).
2. Ask the user for a concurrency cap (max agents for this wave). Mesh must not
   assume a default.
3. From the Ready set, rank candidates using the fixed heuristic order:
   1) Priority first (bd priority).
   2) Maximize unlocks: prefer high-fanout beads that unblock many dependents
      (contract/infrastructure beads).
   3) Prefer checkpoint/integration beads when they are Ready.
   4) Manual pick always wins: present the recommendation, then ask the user to
      confirm or override.
4. Contention check: if two Ready beads touch the same files, serialize them or
   explicitly define a lock order. Mention `bd merge-slot` as the conflict
   primitive if the team uses it.
5. Announce the wave + status summary using the template below.

### Wave Status Summary

```text
Wave status
- Ready: <ids>
- Blocked: <id -> reason>
- Active: <id -> agent>
- Completed: <id -> PR link>
- Recommended wave: <ids> (cap: <n>; heuristic: priority -> unlocks -> checkpoints)
```

## Entrypoints & Scope Contract

Mesh is epic-first: it swarms an epic and its child DAG. A single bead can be
auto-wrapped, but mesh never auto-beadifies.

### Supported inputs (how to resolve the target)

- Explicit epic ID: use it directly.
  - `bd swarm validate <epic-id>`
  - `bd list --parent <epic-id> --pretty`
- Current bead: resolve from in-progress work and confirm with the user.
  - `bd list --status in_progress --pretty`
  - If exactly one is in progress, run `bd show <id>` and resolve its parent.
  - If it has a parent epic, use the epic ID; otherwise use the bead ID
    (auto-wrap is only for beads without an epic).
  - If multiple are in progress, ask for the target.
- List of bead IDs: require a shared epic and confirm the child list.
  - `bd show <id>` for each bead to confirm a common parent epic.
  - If no shared epic exists, stop and ask the user to create/assign one first.

### Epic-first orchestration (default)

- Always create the swarm from an epic.
  - `bd swarm create <epic-id>`
- If given a non-epic ID, `bd swarm create <bead-id>` will auto-wrap it into a
  1-child epic.

### No auto-beadify (hard constraint)

- Mesh does not split a bead into children or infer dependencies.
- It expects a pre-built DAG (epic + child issues + deps).
- If the epic has only one child or no parallelism, stop and recommend using
  `$gen-beads` to create child beads + dependencies before swarming.

### Scope confirmation checklist (must complete before spawning)

1. `bd show <epic-id>` to confirm the epic’s intent.
2. `bd list --parent <epic-id> --pretty` to enumerate children.
3. `bd swarm validate <epic-id>` to verify the DAG and parallelism.
4. Ask the user to confirm: epic ID, child list, and expected parallelism.
5. Then run `bd swarm create <epic-id>` (or `<bead-id>` for auto-wrap).

## Agent Prompt Template

```text
Work bead <ID>. Use skill <work|imp|resolve> as appropriate.
Restate done-means + acceptance criteria.
Keep diffs bead-scoped; open a PR when done.
Record verification and PR link in the bead comment.
If blocked, state why and what is needed.
```

## Coordination Guardrails

- Prefer one bead per agent to avoid overlapping diffs.
- Do not start blocked beads; queue them behind their prerequisites.
- Treat bead comments as the canonical progress log.
- If two beads touch the same files, serialize them or explicitly define the
  lock order.

## Agent Lifecycle (Beads-native, coordinator-only)

Sub-agents do not run `bd` inside their jj workspaces. The coordinator owns all
beads writes and liveness tracking.

### Runbook

1. Create an ephemeral agent bead per spawned sub-agent run:
   ```bash
   bd create --type=agent --ephemeral --role-type polecat --agent-rig <rig> \
     --labels agent,agent:<name>,role:polecat \
     --title "<name>"
   ```
2. Attach the work bead to the agent via the hook slot:
   ```bash
   bd slot set <agent-id> hook <bead-id>
   ```
3. Track liveness/state during execution:
   ```bash
   bd agent state <agent-id> spawning|running|working|stuck|done
   bd agent heartbeat <agent-id>  # optional
   ```
4. Coordinator writes progress (sub-agents never call `bd`):
   - Per-bead comment with PR link + verification signal.
   - Epic-level swarm status comment aggregating PRs/blockers/next wave.

### Coordinator Comment Templates

Per-bead:
```text
Checkpoint: <short outcome>
- PR: <link>
- Verify: <command>  # <pass/fail>
- Notes: <limits or follow-ups>
```

Epic-level swarm status:
```text
Swarm status
- Completed: <bead -> PR>
- Active: <bead -> agent>
- Blocked: <bead -> reason>
- Next wave: <bead ids>
```

### Cleanup

- Clear the hook slot when the agent finishes:
  ```bash
  bd slot clear <agent-id> hook
  ```
- Optionally close or delete ephemeral agent beads after the work is merged.

## Status Summary Format

```text
Wave 1: <IDs>
In progress: <ID -> agent>
Blocked: <ID -> reason>
PRs: <ID -> link>
Next wave: <IDs>
```
