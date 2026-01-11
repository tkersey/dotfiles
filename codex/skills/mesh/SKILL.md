---
name: mesh
description: Orchestrate multiple Codex sub-agents via cx to work beads in parallel and deliver PRs; use whenever a bead (or set of beads) is being worked and multi-agent coordination, dependency scheduling, or progress consolidation is needed.
---

# mesh

## Purpose
Mesh orchestrates multiple Codex sub-agents to work an epic's bead DAG in
parallel. The coordinator owns all `bd` writes; sub-agents never run `bd`.

## Preconditions (must pass)

1. Confirm a beads repo:
   `rg --files -g '.beads/**' --hidden --no-ignore`
2. Coordinator-only `bd`:
   - Sub-agents run in jj workspaces and **do not** run `bd`.
   - The coordinator performs all bead updates, comments, and status changes.
3. Agree on a concurrency cap (max agents per wave).

## Formula contracts (mesh vNext)

Mesh vNext uses two formulas under `.beads/formulas/`:

- `mol-mesh-run.formula.json` (formula name: `mol-mesh-run`)
- `mol-mesh-arm.formula.json` (formula name: `mol-mesh-arm`)

`mol-mesh-run` variables:
- `target_id`
- `target_kind`
- `concurrency`
- `workspace_backend` (default: `worktree`)
- `audit_level` (default: `full`)

`mol-mesh-run` step list (order):
- `resolve-target` (gate)
- `validate-target` (gate)
- `run-waves`
- `closeout`

`mol-mesh-arm` minimal structure:
- single step: `arm`
- intended to be bonded with `--ephemeral`

Examples:
```bash
bd cook .beads/formulas/mol-mesh-run.formula.json
bd mol pour mol-mesh-run --var target_id=<id> --var target_kind=epic --var concurrency=3
bd mol bond mol-mesh-arm <mesh-run-id> --ephemeral
```

## 1) Select the epic (scope contract)

Mesh is epic-first: it swarms an epic and its child DAG. A single bead can be
auto-wrapped into a one-child epic, but mesh never auto-beadifies.

### Supported inputs (how to resolve the target)

- Explicit epic ID: use it directly.
  - `bd swarm validate <epic-id>`
  - `bd list --parent <epic-id> --pretty`
- Current bead (from in-progress work):
  - `bd list --status in_progress --pretty`
  - If exactly one is in progress, `bd show <id>` and resolve its parent.
  - If it has a parent epic, use the epic ID; otherwise use the bead ID.
  - If multiple are in progress, stop and ask for the target.
- List of bead IDs:
  - `bd show <id>` for each to confirm a common parent epic.
  - If no shared epic exists, stop and ask the user to create/assign one first.

### Auto-wrap behavior + limitations

- `bd swarm create <bead-id>` auto-wraps a non-epic bead into a 1-child epic.
- Auto-wrap is **only** for a single bead with no epic; it does not create child
  beads or dependencies.
- If there is no parallelism (one child or no DAG), stop and recommend
  `$gen-beads` before swarming.

### Scope confirmation checklist (must complete before spawning)

1. `bd show <epic-id>` to confirm intent.
2. `bd list --parent <epic-id> --pretty` to enumerate children.
3. `bd swarm validate <epic-id>` to verify DAG + parallelism.
4. Ask the user to confirm: epic ID, child list, expected parallelism.
5. Then run `bd swarm create <epic-id>` (or `<bead-id>` for auto-wrap).

## 2) Plan waves (epic-first swarming)

Use this decision procedure when selecting a wave. The goal is repeatable
ordering with a human override.

1. Build the status map:
   - `bd swarm status <epic-id>` to compute Ready/Blocked/Active/Completed.
   - If the DAG changed since scope confirmation, re-run
     `bd swarm validate <epic-id>` to surface fronts (integration or checkpoint
     bottlenecks).
2. Ask the user for a concurrency cap (max agents for this wave). Mesh must not
   assume a default.
3. From the Ready set, rank candidates using the fixed heuristic order:
   1) Priority first (bd priority).
   2) Maximize unlocks (high-fanout beads).
   3) Prefer checkpoint/integration beads when Ready.
   4) Manual pick always wins (present the recommendation, then ask to confirm
      or override).
4. Contention check: if two Ready beads touch the same files, serialize them or
   explicitly define a lock order. Mention `bd merge-slot` if the team uses it.
5. Announce the wave + status summary using the template below.

### Wave status summary

```text
Wave status
- Ready: <ids>
- Blocked: <id -> reason>
- Active: <id -> agent>
- Completed: <id -> PR link>
- Recommended wave: <ids> (cap: <n>; heuristic: priority -> unlocks -> checkpoints -> manual)
```

## 3) Workspaces + dispatch (jj + cx)

Mesh uses per-bead jj workspaces so agents do not collide in the same working
copy. The default workspace path convention is:

`../workspaces/<repo>/<bead-id>/`

Create and enter the workspace from the repo root:

```bash
jj workspace add ../workspaces/<repo>/<bead-id>/ [-r <rev>]
cd ../workspaces/<repo>/<bead-id>/
```

Dispatch the sub-agent from inside the workspace so edits land in the correct
working copy:

```bash
codex/skills/cx/scripts/cx-exec.sh "..."
```

Notes:
- Use `-r <rev>` to pin the starting revision when needed (default is current).
- The sub-agent prompt must include bead context (copied from `bd show`) and the
  rule: **do not run `bd`**.
- Sub-agents must use the `jujutsu` skill for all VCS operations.

## 4) Agent lifecycle (beads-native, coordinator-only)

Sub-agents do not run `bd` inside their jj workspaces. The coordinator owns all
beads write operations and liveness tracking.

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
5. Cleanup:
   ```bash
   bd slot clear <agent-id> hook
   ```

## 5) Coordination guardrails

- Prefer one bead per agent to avoid overlapping diffs.
- Do not start blocked beads; queue them behind prerequisites.
- Treat bead comments as the canonical progress log.
- If two beads touch the same files, serialize them or define a lock order.

## Agent prompt template

```text
Work bead <ID>. Use skill <work|imp|resolve> as appropriate.
Context: <paste relevant bd show output here so the agent can work offline>.
Do NOT run bd in this workspace; coordinator owns bead updates.
Use the jujutsu skill for all VCS operations. Open a PR when done.
Restate done-means + acceptance criteria. Keep diffs bead-scoped.
If blocked, state why and what is needed.

Final output block (required):
PR: <url>
Verify: <command>  # <pass/fail>
Changed: <paths>
Blockers: <none|details>
```

## Coordinator comment templates

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

## Worked example (end-to-end)

Scenario: swarm epic `mesh-epic` with three children `mesh-1`, `mesh-2`,
`mesh-3`, concurrency cap = 2.

1) Select the epic and validate the DAG:
```bash
bd show mesh-epic
bd list --parent mesh-epic --pretty
bd swarm validate mesh-epic
bd swarm create mesh-epic
```
Example output shape:
```text
Children: mesh-1, mesh-2, mesh-3
Validation: OK (parallelism detected)
Swarm: created
```

2) Build status + pick the wave (priority -> unlocks -> checkpoints -> manual):
```bash
bd swarm status mesh-epic
```
Example output shape:
```text
Ready: mesh-1, mesh-2
Blocked: mesh-3 -> mesh-2
Active: (none)
Completed: (none)
```

Wave status (cap: 2):
```text
Wave status
- Ready: mesh-1, mesh-2
- Blocked: mesh-3 -> mesh-2
- Active: (none)
- Completed: (none)
- Recommended wave: mesh-1, mesh-2 (cap: 2; heuristic: priority -> unlocks -> checkpoints -> manual)
```

3) Create ephemeral agent beads + hook slots:
```bash
bd create --type=agent --ephemeral --role-type polecat --agent-rig codex \
  --labels agent,agent:mesh-1,role:polecat \
  --title "mesh-1"
bd slot set <agent-id-1> hook mesh-1

bd create --type=agent --ephemeral --role-type polecat --agent-rig codex \
  --labels agent,agent:mesh-2,role:polecat \
  --title "mesh-2"
bd slot set <agent-id-2> hook mesh-2
```
Example output shape:
```text
Created: agent-123
Created: agent-124
```

4) Launch sub-agents from per-bead jj workspaces:
```bash
jj workspace add ../workspaces/dotfiles/mesh-1/
cd ../workspaces/dotfiles/mesh-1/
codex/skills/cx/scripts/cx-exec.sh "Work bead mesh-1. Use skill work. Context: <bd show mesh-1> ..."

jj workspace add ../workspaces/dotfiles/mesh-2/
cd ../workspaces/dotfiles/mesh-2/
codex/skills/cx/scripts/cx-exec.sh "Work bead mesh-2. Use skill work. Context: <bd show mesh-2> ..."
```

5) Record PR + verification signals into beads:
```bash
bd comments add mesh-1 "$(cat <<'EOF'
Checkpoint: implemented mesh-1 outcome
- PR: https://example.com/pr/101
- Verify: rg -n \"mesh\" codex/skills/mesh/SKILL.md  # pass
- Notes: doc-only change
EOF
)"

bd comments add mesh-epic "$(cat <<'EOF'
Swarm status
- Completed: mesh-1 -> https://example.com/pr/101
- Active: mesh-2 -> agent-124
- Blocked: mesh-3 -> mesh-2
- Next wave: mesh-2
- Verify: bd swarm validate mesh-epic  # pass
EOF
)"
```

6) Cleanup when agents finish:
```bash
bd slot clear agent-123 hook
bd slot clear agent-124 hook
```
