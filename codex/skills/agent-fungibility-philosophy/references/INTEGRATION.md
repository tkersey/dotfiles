# Integration with Agent Flywheel Tools

## Table of Contents
- [Tool Roles](#tool-roles)
- [br (Beads Rust)](#br-beads-rust)
- [bv (Beads Viewer)](#bv-beads-viewer)
- [ntm (Named Tmux Manager)](#ntm-named-tmux-manager)
- [Agent Mail](#agent-mail)
- [Full Workflow](#full-workflow)

---

## Tool Roles

| Tool | Role in Fungibility |
|------|---------------------|
| **br** | Shared task pool — all agents read/write same beads |
| **bv** | Decentralized prioritization — each agent independently finds optimal work |
| **ntm** | Agent lifecycle — spawn, manage, replace identical agents |
| **Agent Mail** | Coordination — agents communicate without central dispatcher |

---

## br (Beads Rust)

### Why br Enables Fungibility

Beads are the unit of work. They exist independently of agents:

```bash
# Any agent can see all beads
br list

# Any agent can claim work
br update bd-abc123 --status in_progress

# Any agent can complete work
br close bd-abc123 --reason "Implemented feature"
```

### Key Commands for Fungible Agents

```bash
# See what's ready to work on
br ready

# See what's in progress (maybe stuck)
br list --status in_progress

# Claim a bead
br update BEAD --status in_progress --assignee "$(whoami)"

# Complete a bead
br close BEAD --reason "Description of what was done"

# Mark blocked
br update BEAD --status blocked --reason "Waiting on dependency"
```

---

## bv (Beads Viewer)

### Why bv Enables Fungibility

No central dispatcher needed. Each agent independently asks "what should I work on next?"

```bash
# Any agent finds optimal next bead
bv --robot-next

# Any agent sees full triage
bv --robot-triage

# JSON output for programmatic use
bv --robot-next --json
```

### bv Prioritization

bv considers:
- Priority levels (P0-P4)
- Dependencies (blocked beads excluded)
- Labels (domain grouping)
- Age (older beads surface)

Any agent gets the same prioritization. No role-based filtering.

---

## ntm (Named Tmux Manager)

### Why ntm Enables Fungibility

All agents spawned identically. Same init prompt, same environment.

```bash
# Spawn identical agents
ntm spawn PROJECT --cc=3 --cod=2 --gmi=1

# Give ALL agents same prompt
ntm send PROJECT --all "$(cat init_prompt.txt)"

# Add more when scaling
ntm add PROJECT --cc=2

# Replace dead agent — no role assignment
ntm add PROJECT --cc=1
```

### Agent Types Are Interchangeable

`--cc` (Claude), `--cod` (Codex), `--gmi` (Gemini) are different CLI tools but:
- Same init prompt
- Same bead pool
- Same Agent Mail
- Fully interchangeable for most tasks

---

## Agent Mail

### Why Agent Mail Enables Fungibility

Agents coordinate without central dispatcher:

```bash
# Send to specific agent
ntm mail send PROJECT --to BlueLake "Can you review my changes to auth?"

# Broadcast to all
ntm mail send PROJECT --all "I'm starting on bd-abc123 (auth refactor)"

# Check inbox
ntm mail inbox PROJECT
```

### Coordination Patterns

| Pattern | How |
|---------|-----|
| Claiming work | "I'm starting bd-X" broadcast |
| Requesting help | Direct message to relevant agent |
| Handoff | "I'm stuck on X, anyone can take it" |
| Sync | "All agents: report current status" |

No agent "owns" any domain. Messages are about beads, not roles.

---

## Full Workflow

### Phase 1: Planning (Human-Intensive)

```bash
# Create comprehensive plan
# (Use planning-workflow methodology)

# Convert to beads
# Plan → markdown → beads with dependencies
br create "Implement auth" --type feature --priority 1
br create "Add tests for auth" --type task --priority 2
br dep add bd-tests bd-auth  # tests depend on auth
```

### Phase 2: Execution (Agent-Intensive)

```bash
# Spawn fungible swarm
ntm spawn myproject --cc=5 --cod=2

# Initialize all identically
ntm send myproject --all "$(cat init_prompt.txt)"

# Agents autonomously:
# 1. Read AGENTS.md
# 2. Register with Agent Mail
# 3. Run bv, find optimal bead
# 4. Claim and work
# 5. Coordinate via mail
# 6. Complete, find next bead
```

### Phase 3: Monitoring (Periodic)

```bash
# Dashboard overview
ntm dashboard myproject

# Check progress
br stats
bv --robot-triage

# Replace dead agents as needed
ntm add myproject --cc=1
```

### Phase 4: Completion

```bash
# All beads closed
br list --status open  # Should be empty

# Final sync
br sync --flush-only
git add .beads/ && git commit -m "All beads complete"
```

---

## Integration Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    FUNGIBLE AGENT SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│   │ Agent 1 │    │ Agent 2 │    │ Agent 3 │    │ Agent N │     │
│   │ (cc)    │    │ (cod)   │    │ (gmi)   │    │ (any)   │     │
│   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘     │
│        │              │              │              │           │
│        └──────────────┼──────────────┼──────────────┘           │
│                       │              │                          │
│                       ▼              ▼                          │
│              ┌────────────────────────────────┐                 │
│              │         SHARED STATE           │                 │
│              ├────────────────────────────────┤                 │
│              │  br: Bead pool (tasks)         │                 │
│              │  bv: Prioritization engine     │                 │
│              │  Agent Mail: Coordination      │                 │
│              │  AGENTS.md: Project context    │                 │
│              └────────────────────────────────┘                 │
│                                                                 │
│   All agents identical. All read same state. Any can do any    │
│   work. Failures recovered by starting new identical agent.    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
