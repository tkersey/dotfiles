# Agent Coordination — running a multi-agent refactor swarm

> Large refactor passes parallelize cleanly: each candidate → one agent → one commit. This file specifies how to coordinate a swarm via NTM + Agent Mail + Beads, keeping conflicts and duplicated work to near zero.

## Contents

1. [When to swarm vs. run solo](#when-to-swarm-vs-run-solo)
2. [Architecture: NTM + Agent Mail + Beads + this skill](#architecture)
3. [Launch recipe](#launch-recipe)
4. [File reservations and collision policy](#file-reservations-and-collision-policy)
5. [Thread-id conventions](#thread-id-conventions)
6. [Ledger aggregation](#ledger-aggregation)
7. [Recovery: stuck / rate-limited panes](#recovery-stuck--rate-limited-panes)

---

## When to swarm vs. run solo

**Solo:**
- < 5 candidates in the duplication map
- Candidates touch overlapping files
- You don't have NTM / Agent Mail / Beads set up
- First time using this skill (get the sequence right first)

**Swarm:**
- ≥ 5 independent candidates
- Candidates partition cleanly by directory / crate / feature
- User has the agentic infrastructure: `ntm`, `mcp-agent-mail`, `br`
- Time-to-merge matters — a swarm of 8 agents finishes in ~N minutes what serial does in ~8N

**Mixed:** serialize the high-risk candidates (data model unification, error refactor), parallelize the mechanical ones (dead imports, stale types, pass-through wrappers).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (you, or one agent)                           │
│  - runs Phase 0 (bootstrap) + Phase A (baseline)             │
│  - runs Phase B (duplication map)                            │
│  - runs Phase C (scoring) — writes scored_candidates.md     │
│  - files one bead per accepted candidate                    │
│  - launches N NTM panes with marching orders                │
└─────────────────────────────────────────────────────────────┘
        │                                │
        ▼                                ▼
  ┌──────────────┐                ┌──────────────┐
  │  Beads (br)  │                │  Agent Mail  │
  │ - candidates │ ←─── poll ───▶ │ - inbox      │
  │ - deps       │                │ - file locks │
  │ - status     │                │ - threads    │
  └──────────────┘                └──────────────┘
        ▲                                ▲
        │                                │
  ┌──────────────┐                ┌──────────────┐
  │  Agent 1     │ <------------> │  Agent N     │
  │ (NTM pane)   │                │ (NTM pane)   │
  │  - br ready  │                │              │
  │  - claim     │                │              │
  │  - do loop   │                │              │
  │  - commit    │                │              │
  │  - release   │                │              │
  │  - br close  │                │              │
  └──────────────┘                └──────────────┘
```

**Source of truth**: Beads owns "what to do next." Agent Mail owns "who's touching what." This skill's `LEDGER.md` is the human artifact.

---

## Launch recipe

### Step 1 — orchestrator preps

```bash
# Phase 0
./scripts/check_skills.sh refactor/artifacts/2026-04-23-pass-1
./scripts/install_missing_skills.sh refactor/artifacts/2026-04-23-pass-1

# Phase A (baseline)
./scripts/baseline.sh 2026-04-23-pass-1

# Phase B (map)
./scripts/dup_scan.sh 2026-04-23-pass-1 src/

# Fill duplication_map.md by hand (or prompt an agent to)

# Phase C (score)
./scripts/score_candidates.py refactor/artifacts/2026-04-23-pass-1/duplication_map.md

# File one bead per accepted candidate
br create --title "[refactor D1] collapse 3x send_* in messaging.rs" --type task --priority 2 --label refactor
br create --title "[refactor D2] unify <Button> variants" --type task --priority 2 --label refactor
# ... etc

# Optional: add dependencies
br dep add D4 D1       # D4 waits for D1 to land
```

### Step 2 — orchestrator launches swarm

```bash
# Spawn one NTM pane per available agent slot
ntm spawn refactor-worker-01 --dir $PWD
ntm spawn refactor-worker-02 --dir $PWD
# ... up to 8 panes

# Send marching orders — one per pane, each with a distinct scope
ntm send refactor-worker-01 "$(cat <<'EOF'
You are refactor-worker-01 participating in a simplify-and-refactor-code-isomorphically swarm.

Read AGENTS.md first. Then:
  1. register with Agent Mail: ensure_project(<abs-path>); register_agent(...)
  2. loop:
     a. br ready --json            # pick highest-priority unblocked refactor bead
     b. br update <id> --status=in_progress
     c. reserve files via agent-mail:
        file_reservation_paths(...,  paths=[<candidate's paths>],
                                    ttl_seconds=3600, exclusive=true,
                                    reason="beads-<id>")
     d. run the skill's loop on that candidate:
        - fill isomorphism card (./scripts/isomorphism_card.sh <id>)
        - Edit-only changes; no Write
        - ./scripts/verify_isomorphism.sh
        - git commit -m "refactor(...)..." including full card
        - append to LEDGER.md (append-only, no conflicts)
     e. release_file_reservations(...)
     f. br close <id>
     g. if no ready beads remain: exit

Honor AGENTS.md invariants:
  - no file deletion without user approval
  - no script-based changes
  - one lever per commit
  - never pause on "unexpected changes" — other agents are editing too
EOF
)"

# Repeat for each pane
```

### Step 3 — orchestrator monitors

```bash
# Watch beads progress
watch -n 10 'br list --status in_progress --json | jq length'

# Watch Agent Mail inbox for any escalation
watch -n 10 'resource://inbox/orchestrator | jq length'

# When all beads are closed + no new ones being discovered
br list --status open --label refactor | grep -c '' | awk '{print "remaining: "$1}'
```

---

## File reservations and collision policy

### Reservation scope

Reserve **all** files a candidate will touch, not just the main one. Include:
- The file(s) being edited
- Callers (who need their import paths updated)
- Tests exercising the symbol
- Any public `index.ts` / `mod.rs` re-exports

```
file_reservation_paths(
  project_key=<abs>,
  agent_name="refactor-worker-01",
  paths=["crates/mcp-agent-mail-tools/src/messaging.rs",
         "crates/mcp-agent-mail-tools/src/lib.rs",        # re-exports
         "crates/mcp-agent-mail-tools/tests/**"],          # tests
  ttl_seconds=3600,
  exclusive=true,
  reason="beads-D1"
)
```

### Collision resolution

If `file_reservation_paths` returns `FILE_RESERVATION_CONFLICT`:
1. **Don't** wait — the other agent is actively editing.
2. **Don't** steal the lock.
3. Close the bead back to `open` (`br update <id> --status=open`).
4. Pick a different bead (`br ready`).
5. Come back to this one later.

**Never** try to race with another agent on a file. Sequential is better than corrupt.

### Reservation lifecycle

```
reserve → edit → verify → commit → release
            │
            └── if verify fails: release + revert + mark bead blocked with reason
```

TTL default 1h. Renew via `renew_file_reservations` if a complex candidate needs longer.

---

## Thread-id conventions

Per AGENTS.md Agent Mail pattern:

| Artifact | Value | Example |
|----------|-------|---------|
| Mail `thread_id` | `refactor-<bead-id>` | `refactor-D1` |
| Mail subject | `[refactor-<id>] <title>` | `[refactor-D1] collapse 3× send_*` |
| File-reservation `reason` | `refactor-<bead-id>` | `refactor-D1` |
| Commit message prefix | `refactor(<scope>): <title>` | `refactor(mail): collapse 3× send_*` |
| Commit trailer | `Beads: D1` | — |

Everything links via the bead id. You can answer "who touched that code and why" with one query in either system.

---

## Ledger aggregation

Each worker appends to `refactor/artifacts/<run>/LEDGER.md`. Appends to markdown are conflict-free if each worker adds their row atomically.

### Safe append pattern

```bash
# per worker — atomic append via fcntl lock (flock) or a dedicated script
flock refactor/artifacts/<run>/LEDGER.md -c \
  "echo '| <order> | <id> | <sha> | <paths> | <LOC before> | <LOC after> | <Δ> | <tests> | ✓ | 0Δ |' >> refactor/artifacts/<run>/LEDGER.md"
```

Or use a Python helper:
```python
import fcntl
with open('LEDGER.md', 'a') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    f.write(row + '\n')
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

Worker scripts should use `flock` or equivalent. Never concurrent writes without coordination — markdown tables corrupt easily.

---

## Recovery: stuck / rate-limited panes

### Stuck pane detection

```bash
# Panes whose last log event is > 10 min old
ntm list --json | jq '.[] | select((now - .last_event_ts) > 600) | .name'
```

### Rate-limited pane

Claude Max accounts hit limits at unpredictable times. Symptoms:
- pane shows "rate limit reached"
- no progress for > 20 min

Response: per [vibing-with-ntm](../../vibing-with-ntm/SKILL.md):
1. Note the pane's held beads
2. Release file reservations on behalf of the stuck agent:
   ```
   force_release_file_reservation(project_key, path=<p>, reason="stuck worker-01")
   ```
3. Revert the bead to `open`:
   ```
   br update <id> --status=open
   ```
4. Kill and respawn the pane (or migrate to a different account via [caam](../../caam/SKILL.md)).

### Orphaned commits

A worker may have committed and pushed mid-task when rate-limited. Before respawning, inspect:
```bash
git log --author="refactor-worker-01" --since="1 hour ago" --oneline
```
If the commit is good, close the bead as done. If partial, revert (with user approval).

---

## Integration with sibling skills

| Skill | Role |
|-------|------|
| [ntm](../../ntm/SKILL.md) | spawn, send marching orders, monitor panes |
| [agent-mail](../../agent-mail/SKILL.md) | file reservations, inbox, threads |
| [br](../../br/SKILL.md) / [beads-workflow](../../beads-workflow/SKILL.md) | bead CRUD + dependency graph |
| [bv](../../bv/SKILL.md) | graph-aware triage to pick the right candidate order |
| [vibing-with-ntm](../../vibing-with-ntm/SKILL.md) | orchestrator-loop tending and stuck-pane recovery |
| [multi-agent-swarm-workflow](../../multi-agent-swarm-workflow/SKILL.md) | the canonical swarm setup tutorial |
| [caam](../../caam/SKILL.md) | switch Claude/Codex accounts when one rate-limits |

If none of these are installed, **fall back to solo sequential mode** — this skill's whole loop runs perfectly well for one agent at a time. Parallelism is an accelerant, not a prerequisite.
