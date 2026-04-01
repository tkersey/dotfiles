---
name: agent-fungibility-philosophy
description: >-
  Fungible agent architecture for multi-agent coding. Use when scaling agent swarms,
  designing multi-agent workflows, recovering from agent failures, or choosing
  specialized vs. interchangeable agent patterns.
---

<!-- TOC: Philosophy | THE EXACT PROMPT | Quick Reference | When to Use | Core Properties | Integration | Failure Recovery | Anti-Patterns | References -->

# Agent Fungibility — Scalable Multi-Agent Architecture

> **Core Insight:** "Fungibility bestows a LOT of really good properties automatically in a computer system."
>
> The goal: Build the machine once, set it running, move on. The swarm handles the rest.

## The Philosophy

All agents are **identical generalists**. Any agent can work on any bead. There are no "frontend agents" or "testing agents" — just agents executing beads from a shared pool.

**Why this wins:**
- **Failure resilience** — Dead agent? Start another. No role replacement needed
- **Linear scaling** — 3→10→30 agents requires no rebalancing
- **No bottlenecks** — No "critical specialist" blocking the pipeline
- **Reduced human involvement** — Front-load planning, then step away

---

## THE EXACT PROMPT — Agent Initialization

Give this to **every agent** regardless of type (Claude Code, Codex, Gemini):

```
First read ALL of the AGENTS.md file and README.md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code, technical architecture and purpose of the project. Then register with MCP Agent Mail and introduce yourself to the other agents.

Be sure to check your agent mail and promptly respond if needed to any messages; then proceed meticulously with your next assigned beads, working on the tasks systematically and tracking your progress via beads and agent mail messages.

Don't get stuck in "communication purgatory" where nothing is getting done; be proactive about starting tasks that need to be done, but inform your fellow agents via messages when you do so and mark beads appropriately.

When you're not sure what to do next, use bv to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Make sure to acknowledge all communication requests from other agents. Use ultrathink.
```

### Why This Prompt Works

| Element | Purpose |
|---------|---------|
| **Read AGENTS.md first** | Full project context before any action |
| **Register with Agent Mail** | Coordination layer established |
| **Check mail, respond** | Prevents coordination gaps |
| **"Communication purgatory"** | Explicit anti-pattern to avoid |
| **Use bv for next bead** | Decentralized task selection |
| **Mark beads appropriately** | Status visible to all agents |

---

## Quick Reference

| Scenario | Action |
|----------|--------|
| Spawn swarm | `ntm spawn PROJECT --cc=3 --cod=2 --gmi=1` |
| Initialize all | `ntm send PROJECT --all "$(cat init_prompt.txt)"` |
| Agent dies | Start new session, give same init prompt |
| Need to scale | Just add more: `ntm add PROJECT --cc=2` |
| Check what's ready | `bv --robot-next` (any agent can run this) |
| Claim work | `br update BEAD --status in_progress` |

---

## When to Use Fungibility

| Situation | Fungible? | Why |
|-----------|-----------|-----|
| Software development | **Yes** | Output matters, not discourse |
| Large codebase, many tasks | **Yes** | No specialist bottleneck |
| Need fault tolerance | **Yes** | Any agent replaces any agent |
| Scientific debate simulation | No | Role-based discourse IS the mechanism |
| Strict compliance review | No | Separation of duties required |

---

## Model Mix Recommendations

All agents are fungible, but models have different strengths:

| Mix | Best For |
|-----|----------|
| 3 Claude (Opus) + 2 Codex + 1 Gemini | General development |
| 5 Claude (Opus) | Complex reasoning tasks |
| 3 Claude + 3 Codex | High-throughput coding |
| 2 Claude + 2 Codex + 2 Gemini | Cross-validation diversity |

**Start small:** 3-6 agents. Scale up as coordination stabilizes.

```bash
# Recommended starting swarm
ntm spawn myproject --cc=3 --cod=2 --gmi=1
```

---

## Core Properties

### Robustness

Agents fail constantly:
- Crashes, closed tabs, context rot
- Rate limits, stuck loops
- "Euthanized" for fresh start

**With fungibility:** When an agent dies:
1. Bead remains marked in-progress
2. Any other agent can resume it
3. No special replacement logic
4. No dependency on that specific agent

### Scaling

| Agents | Specialized System | Fungible System |
|--------|-------------------|-----------------|
| 3→10 | Rebalance roles | Just add 7 more |
| 10→30 | Complex orchestration | Just add 20 more |
| Role imbalance | Bottleneck | N/A — no roles |

### The Fountain Code Analogy

Like RaptorQ fountain codes:
- Turn work into a stream of fungible tasks (beads)
- Any agent catches any bead
- No "rarest chunk" bottleneck
- System resilient to partial failures

---

## Integration with Flywheel Tools

| Tool | Role in Fungibility |
|------|---------------------|
| **br** | Shared bead pool — any agent reads/claims |
| **bv** | Decentralized prioritization — each agent asks "what's next?" |
| **ntm** | Spawn/manage identical agents |
| **Agent Mail** | Coordination without central dispatcher |

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. PLANNING (human-intensive)                                  │
│     └─► Create comprehensive markdown plan                      │
│     └─► Convert to beads with dependencies                      │
├─────────────────────────────────────────────────────────────────┤
│  2. EXECUTION (agent-intensive, human-free)                     │
│     └─► Spawn N fungible agents                                 │
│     └─► Each agent: read AGENTS.md → bv next → claim → work    │
│     └─► Agent Mail for coordination                             │
├─────────────────────────────────────────────────────────────────┤
│  3. MONITORING (periodic check-ins)                             │
│     └─► ntm dashboard PROJECT                                   │
│     └─► Replace dead agents as needed                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Failure Recovery

### Agent Dies Mid-Task

```bash
# Check what was in progress
br list --status in_progress

# Spawn replacement
ntm add PROJECT --cc=1

# Give same init prompt — it will:
# 1. Read AGENTS.md
# 2. Run bv, see the stuck bead
# 3. Either resume or mark blocked
```

### Mass Failure (Context Compaction)

```bash
# All agents hit context limits simultaneously
# No panic — just restart each

ntm send PROJECT --all "/compact"
# or
# Spawn fresh: ntm spawn PROJECT --cc=5
# Give init prompt, they pick up where things left off
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Assigning roles | Creates specialist bottleneck | All agents do all tasks |
| Central dispatcher | Single point of failure | Agents use bv independently |
| Agent-specific context | Replacement requires recreation | All context in AGENTS.md + beads |
| "Only Alice can do auth" | Blocks on Alice | Any agent reads auth docs, claims auth beads |

---

## Comparison

| Property | Specialized Agents | Fungible Agents |
|----------|-------------------|-----------------|
| Failure handling | Complex: identify role, recreate | Simple: start another |
| Scaling | Requires role balancing | Just add more |
| Replacement | Need matching specialist | Any agent works |
| Single point of failure | Yes (each role) | No |
| Coordination overhead | High | Low (beads + mail) |
| Human involvement | Ongoing orchestration | Front-loaded in planning |

---

## References

| Topic | Reference |
|-------|-----------|
| Full philosophy & rationale | [PHILOSOPHY.md](references/PHILOSOPHY.md) |
| Prompt variations | [PROMPTS.md](references/PROMPTS.md) |
| Failure scenarios | [RECOVERY.md](references/RECOVERY.md) |
| Integration patterns | [INTEGRATION.md](references/INTEGRATION.md) |

---

## Validation

A healthy fungible swarm:
- All agents running same init prompt
- No agent "owns" any domain
- Dead agents replaced without role matching
- Work continues even when agents die
