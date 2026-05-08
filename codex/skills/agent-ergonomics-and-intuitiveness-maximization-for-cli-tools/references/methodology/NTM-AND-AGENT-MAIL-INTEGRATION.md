# NTM-AND-AGENT-MAIL-INTEGRATION — Coordinating multi-agent audits

For Squad+ orchestration tier (per ORCHESTRATION.md), the audit can spawn many agents in parallel — different scorers per surface, different appliers per rec, different fresh-eyes reviewers across passes.

This file gives the playbook for coordinating those agents using **NTM** (multi-agent tmux orchestration) and **MCP Agent Mail** (file reservations + threaded messaging).

---

## When to escalate to NTM

Per `ORCHESTRATION.md`:

| Tier | When | NTM use |
|------|------|---------|
| Solo | Tiny tools | No |
| Pair | Typical | Optional |
| Squad | Full CLI suite | Recommended |
| Swarm | Multi-binary or T4+ | Required |

NTM gives durable tmux sessions, agent supervision, restart on crash. For short audits (< 1 hour), Agent-tool subagents suffice. For multi-hour swarms, NTM's session-recovery is critical.

---

## Spawning a Squad-tier audit via Agent Mail (no NTM)

Phase 1 example: 4 surface-inventorist agents in parallel, each owning a subtree.

### Step 1 — register the audit's project

```
ensure_project(project_key=<absolute path to sibling>)
register_agent(project_key, program="claude-code", model="opus-4.7", agent_name="aerg-master")
```

### Step 2 — reserve sibling workspace

```
file_reservation_paths(
  project_key=<sibling>,
  agent_name="aerg-master",
  paths=["audit/manifest.json", "audit/HANDOFF.md"],
  ttl_seconds=86400,
  exclusive=true,
  reason="agent-ergo-pass-1 master coordinator"
)
```

### Step 3 — spawn 4 inventorist agents in parallel (Agent tool)

```python
# In the master Claude Code session
agents = ["aerg-inv-1", "aerg-inv-2", "aerg-inv-3", "aerg-inv-4"]
subtrees = ["list", "add", "delete", "doctor"]

# Spawn in parallel via Agent tool
for agent_id, subtree in zip(agents, subtrees):
    Agent(
        description=f"Inventory {subtree}",
        prompt=f"You are {agent_id}. Inventory the {subtree} subtree. Read subagents/surface-inventorist.md. ...",
        # ...
    )
```

### Step 4 — coordinate via Agent Mail

Each subagent:
1. Reserves its partial output file (`audit/partial/inventory_<subtree>.jsonl`)
2. Sends a thread-start message: `subject: [aerg-pass1] Start inventory: <subtree>`
3. Works
4. Releases reservation
5. Sends completion message

The master agent fetches inbox to see who's done.

### Step 5 — concatenate partials

When all 4 send completion messages, the master:
1. Concatenates `audit/partial/inventory_*.jsonl` → `audit/surface_inventory.jsonl`
2. Removes its workspace reservation
3. Proceeds to Phase 2 (scoring)

---

## NTM-orchestrated swarm

For a Swarm-tier audit on a multi-binary family (T4):

### Setup

```bash
# Project-level NTM session
ntm new --project=$SIBLING --name=aerg-pass-1

# Spawn workers per binary
for binary in cargo cargo-audit cargo-deny cargo-machete; do
  ntm spawn --project=$SIBLING --pane=aerg-$binary \
    --agent=claude-code --model=opus-4.7 \
    --prompt="You are auditing $binary. Use subagents/surface-inventorist.md ..."
done

# Spawn cross-cut auditor (the family-level one)
ntm spawn --project=$SIBLING --pane=aerg-family \
  --agent=claude-code --model=opus-4.7 \
  --prompt="You are family-cross-cut-auditor. Wait for per-binary inventories. ..."
```

### Marching orders

```bash
ntm send --project=$SIBLING --pane=aerg-cargo \
  --message='Begin Phase 1 inventory of cargo. Output: audit/family/cargo/surface_inventory.jsonl'

ntm send --project=$SIBLING --pane=aerg-cargo-audit \
  --message='Begin Phase 1 inventory of cargo-audit. Output: audit/family/cargo-audit/surface_inventory.jsonl'

# ... per pane
```

### Convergence detection

After workers complete, the family-cross-cut-auditor pane runs:

```bash
ntm send --project=$SIBLING --pane=aerg-family \
  --message='All per-binary inventories done. Now build cross_cut.jsonl per MULTI-TOOL-FAMILY-AUDIT.md'
```

### Tending the swarm

Per `/vibing-with-ntm`:

```bash
# Check pane health
ntm status --project=$SIBLING --robot

# Find stuck panes
ntm panes --project=$SIBLING --robot --filter=rate-limited

# Restart stuck panes
ntm restart --project=$SIBLING --pane=aerg-cargo-audit
```

### Operator loop

The orchestrator (the human or a "tender" agent) runs an operator loop:
1. Periodically check `ntm status`
2. If a pane is rate-limited or stuck: send marching orders to others; queue restart
3. If a pane completes: send next-phase orders
4. Land the plane when convergence reached

This is the canonical swarm pattern.

---

## Agent Mail patterns within the audit

### Pattern A: Phase-gate messages

```
Subject: [aerg-pass1-phase2] All scorers done; tiebreaker required for verb__list dim intent_inference (spread 150)
From: aerg-master
To: aerg-tiebreaker
Body:
  Surface: verb__list
  Dim: intent_inference
  Scorer-A: 850 (cite: ...)
  Scorer-B: 700 (cite: ...)
  Spread: 150 (>100)
  Action: re-score; we'll take median.
Thread: aerg-pass1-phase2
ack_required: true
```

### Pattern B: Coordination on shared files

When two appliers might touch `src/cli.rs`:

```
file_reservation_paths(
  project_key=<target>,
  agent_name="aerg-applier-R-007",
  paths=["src/cli.rs"],
  ttl_seconds=1800,
  exclusive=true,
  reason="R-007 applying levenshtein-1 typo correction"
)
```

If aerg-applier-R-014 also wants to touch src/cli.rs:
- Reservation fails
- Applier-R-014 picks a different rec OR sends a thread message coordinating order

### Pattern C: Completion announcements

```
Subject: [aerg-pass1-R-007] Applied
From: aerg-applier-R-007
To: aerg-master
Body:
  Commit: abc123
  Test: audit/regression_tests/R-007__levenshtein_typo_hint.test.sh (green)
  Files changed: src/cli.rs (+15 / -2)
  Surfaces touched: flag__list__json, flag__add__json, flag__verbose
Thread: agent-ergo-pass1-R-007
release_file_reservations: ["src/cli.rs"]
```

---

## Workflow coordination via beads + mail + reservations

The full triple-coordination per AGENTS.md:

```
Bead R-007 (br-1234)
   ↓
Mail thread "agent-ergo-pass1-R-007"  (thread_id)
   ↓
File reservation reason="R-007"  (file lock)
   ↓
Commit message "R-007: ... (closes flag__list__json) [br-1234]"
   ↓
Regression test "R-007__levenshtein_typo_hint.test.sh"
```

Every artifact references R-007 OR br-1234. End-to-end traceability.

---

## Spawning multiple audits across multiple targets

For a multi-tool family audit, you may want N audits running concurrently:

```bash
# Create per-target sibling dirs
for tool in tool-a tool-b tool-c; do
  ntm new --project=/data/projects/$tool --name=aerg-$tool
  ntm spawn --project=/data/projects/$tool --pane=master --agent=claude-code \
    --prompt="Audit $tool using agent-ergonomics skill. Run audit-only mode."
done
```

Each tool's audit runs independently. After all complete, run the cross-tool family audit (per MULTI-TOOL-FAMILY-AUDIT.md).

---

## When NTM is overkill

For < 5 hours of audit work, Agent-tool subagents suffice. NTM adds:
- Setup cost (~5 min)
- Pane management overhead
- Need for human / tender agent

Skip NTM if the audit fits in one Claude Code session.

---

## Recovery from failure mid-swarm

If a swarm pane crashes:

```bash
# Check for orphaned reservations
ntm exec --project=$SIBLING --pane=master \
  --message='Run: file_reservation_paths via inspect; find orphaned reservations.'

# Release by path only for reservations owned by the current agent; force-release
# another dead pane only by concrete reservation id after inspecting the holder.
am release_file_reservations --project_key=$SIBLING --agent_name=<same-agent> --paths='[...]'
am force_release_file_reservation --project_key=$SIBLING --agent_name=<operator-agent> --file_reservation_id=<ID> --note='aerg-applier-R-007 pane crashed; reservation orphaned' --notify_previous=true

# Restart the crashed pane
ntm restart --project=$SIBLING --pane=aerg-applier-R-007
```

`/fixing-beads-problems` skill applies if beads also got into a bad state.

---

## Auditing an audit (meta-coordination)

For very large audits (T5), you can audit the audit itself:

- Are the workers spending time efficiently?
- Are reservations being released cleanly?
- Are mail threads getting noisy?

This is `/vibing-with-ntm`'s territory. The "tender" pane reads pane status + reservations + mail; flags inefficiencies; sometimes proactively re-allocates work.

---

## Cross-references

- `/ntm` skill — multi-agent tmux orchestration
- `/vibing-with-ntm` skill — swarm tending
- `/agent-mail` skill — file reservations + messaging
- `/multi-agent-swarm-workflow` skill — swarm patterns
- `/open-beads-weighted-tmux-agent-sessions` skill — weighted swarm allocation
- `/flywheel-with-two-agents-per-repo` skill — paired-agent patterns
- `methodology/ORCHESTRATION.md` — when to escalate to Swarm
- `methodology/BEADS-WORKFLOW.md` — bead-based coordination layer
