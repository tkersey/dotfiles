---
name: mesh
description: Orchestrate multiple Codex sub-agents via cx to work beads in parallel and deliver PRs; use whenever a bead (or set of beads) is being worked and multi-agent coordination, dependency scheduling, or progress consolidation is needed.
---

# mesh

## Purpose
Mesh orchestrates multiple Codex sub-agents to work an epic's bead DAG in
parallel. The coordinator owns all `bd` writes; sub-agents never run `bd`
directly.

## Preconditions (must pass)

1. Confirm a beads repo:
   `rg --files -g '.beads/**' --hidden --no-ignore`
2. Coordinator-only `bd`:
   - Sub-agents run in jj workspaces and **do not** run `bd` directly.
     Read-only access must go through `mesh-bd-ro` (see contract below).
   - The coordinator performs all bead updates, comments, and status changes.
3. Agree on a concurrency cap (max agents per wave).

## Sub-agent bd read-only wrapper (mesh-bd-ro) — Contract

Sub-agents may only read beads via the wrapper. The wrapper always executes:

`bd --readonly --sandbox <command...>`

Allowlisted command paths (exact):
- `show`
- `list`
- `ready`
- `blocked`
- `search`
- `count`
- `status`
- `state`
- `dep list`
- `dep tree`
- `dep cycles`
- `mol show`
- `mol current`
- `mol progress`
- `swarm status`
- `swarm validate`
- `swarm list`
- `epic status`

Rules:
- Reject any other top-level command, alias, or subcommand.
- Reject bare `dep`, `mol`, `swarm`, or `epic` without an allowlisted subcommand.
- Global flag allowlist: `-h/--help`, `--json`, `-q/--quiet`, `-v/--verbose`.
  Disallow all other global flags (e.g., `--actor`, `--db`, `--profile`,
  `--no-*`, `--allow-stale`, `--lock-timeout`).
- Command-specific flags are allowed only for allowlisted commands.
- Positional arguments are limited to those required by the allowlisted command
  (e.g., `show <id...>`, `search <query>`).

Examples (allowed):
- `mesh-bd-ro show bd-123 --thread`
- `mesh-bd-ro list --status in_progress --pretty`
- `mesh-bd-ro dep tree bd-123`
- `mesh-bd-ro mol progress bd-mol-1`
- `mesh-bd-ro swarm status bd-epic-1`

Examples (rejected):
- `mesh-bd-ro dep bd-123 --blocks bd-456`
- `mesh-bd-ro comments add bd-123 "nope"`
- `mesh-bd-ro update bd-123 --status in_progress`

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

## Audit logging contract (bd audit record)

Mesh audit entries are written to `.beads/interactions.jsonl` via `bd audit record`
using **flags-only** (no `--stdin` until the schema is pinned). This contract is
the minimal, repeatable pattern for provenance.

**Kinds in use**
- `llm_call`: prompts + completions
- `tool_call`: orchestration tool events
- `label`: applied via `bd audit label`

**Always include** `--issue-id <bead-id>` to associate the event with the mesh
run/step bead that caused it.

### Command templates

Spawn prompt (agent prompt captured at launch):
```bash
bd audit record --kind llm_call --issue-id <bead-id> --model <model> \
  --prompt "$(cat <prompt-file>)"
```

Completion response (agent final block):
```bash
bd audit record --kind llm_call --issue-id <bead-id> --model <model> \
  --response "$(cat <response-file>)"
```

Orchestration tool event (input/output encoded as JSON payload):
```bash
bd audit record --kind tool_call --issue-id <bead-id> --tool-name <tool> \
  --exit-code <code> --error '<json-payload>'
```

`<json-payload>` is a JSON string (stored in `--error`, the only freeform field
available for `tool_call`):
```json
{"ok":true,"input":{...},"output":{...}}
```
On failure:
```json
{"ok":false,"error":"<message>","input":{...},"output":null}
```

### Labeling guidance

Use labels to mark human-reviewed or suspicious entries:
```bash
bd audit label <entry-id> --label <value> --reason "<why>"
```
To capture `<entry-id>`:
```bash
bd audit record --json ... | jq -r '.id'
```
Or, without assuming output format:
```bash
tail -n 1 .beads/interactions.jsonl | jq -r '.id'
```
Recommended labels:
- `gold`: approved, reusable completion
- `needs_review`: failed tool call or questionable output

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
4. Contention check:
   - Lock groups are label-based: `mesh-lock:<group>`.
   - Never schedule two Ready beads together if their lock labels overlap.
   - If lock labels are missing but file overlap is likely, serialize them or
     explicitly define a lock order. Mention `bd merge-slot` if the team uses it.
5. Announce the wave + status summary using the template below.

### Lock groups (mesh-lock:<group>)

Lock groups prevent unsafe parallel work by declaring coarse-grained
contention domains. A bead may carry one or more `mesh-lock:<group>` labels
(kebab-case). Scheduling rule: **do not** place two Ready beads in the same
wave if they share any lock group label.

Default lock groups for this repo (initial, conservative):
- `mesh-lock:core-config` (Brewfile, gitconfig, gitignore, brew-aliases,
  lazygit/, links.conf, README.md, AGENTS.md)
- `mesh-lock:codex` (codex/)
- `mesh-lock:editor` (nvim/)
- `mesh-lock:shell` (fish/)
- `mesh-lock:terminal` (ghostty/)
- `mesh-lock:install` (install/, assets/)

If a bead spans multiple domains, add multiple lock labels. If no default fits,
define a new lock group and keep it narrow.

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
  rule: **do not run `bd` directly; use `mesh-bd-ro` for read-only if needed**.
- Sub-agents must use the `jujutsu` skill for all VCS operations.

## 4) Agent lifecycle (beads-native, coordinator-only)

Sub-agents do not run `bd` directly inside their jj workspaces. The coordinator
owns all beads write operations and liveness tracking.

### Durable agent pool (contract)

- Names: `mesh-1`, `mesh-2`, … (stable pool identities).
- Required labels: `agent`, `agent:<name>`, `role:polecat`.
- Lookup: `bd list --label agent:<name> --all` before creating a new pool agent.
- State transitions: `bd agent state <agent-id> idle|working|stuck|done`.
- Slot semantics: `bd slot set <agent-id> hook <bead-id>` is the single source of
  “what am I doing?”; clear the hook when work completes.
- Actor attribution: when writing on behalf of an agent, use
  `bd --actor agent:<name>`.

1. Create the durable agent bead if it does not exist (do not use `--ephemeral`
   for pool agents):
   ```bash
   bd create --type=agent --role-type polecat --agent-rig <rig> \
     --labels agent,agent:<name>,role:polecat \
     --title "<name>"
   ```
2. Attach the work bead to the agent via the hook slot:
   ```bash
   bd slot set <agent-id> hook <bead-id>
   ```
3. Track liveness/state during execution:
   ```bash
   bd agent state <agent-id> idle|working|stuck|done
   bd agent heartbeat <agent-id>  # optional
   ```
4. Coordinator writes progress (sub-agents never call `bd` directly):
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
Do NOT run bd directly in this workspace; use mesh-bd-ro for read-only if needed.
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

3) Ensure durable agent beads exist + hook slots:
```bash
bd create --type=agent --role-type polecat --agent-rig codex \
  --labels agent,agent:mesh-1,role:polecat \
  --title "mesh-1"
bd slot set <agent-id-1> hook mesh-1

bd create --type=agent --role-type polecat --agent-rig codex \
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
