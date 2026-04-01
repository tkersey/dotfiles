# Failure Recovery Patterns

## Table of Contents
- [Single Agent Failure](#single-agent-failure)
- [Mass Context Compaction](#mass-context-compaction)
- [Stuck Beads](#stuck-beads)
- [Communication Breakdown](#communication-breakdown)
- [Rate Limit Recovery](#rate-limit-recovery)

---

## Single Agent Failure

### Symptoms
- Terminal closed/crashed
- Agent went silent
- Context rot (confused, looping)
- Explicit "euthanasia" for fresh start

### Recovery

```bash
# 1. Check what was in progress
br list --status in_progress

# 2. Spawn replacement
ntm add PROJECT --cc=1

# 3. Give standard init prompt
# The new agent will:
#   - Read AGENTS.md
#   - Check agent mail
#   - See in-progress bead via bv
#   - Either resume or pick new work
```

### Key Point

No special logic needed. The bead's in-progress status is visible to all agents. New agent decides whether to resume or mark it blocked.

---

## Mass Context Compaction

### Symptoms
- Multiple agents hit context limits
- "/compact" sent to many agents
- Agents lose track of what they were doing

### Recovery

```bash
# Option A: Compact in place
ntm send PROJECT --all "/compact"

# Then send recovery prompt:
ntm send PROJECT --all "Your context was compacted. Reread AGENTS.md, check agent mail, verify your bead status, and continue."

# Option B: Fresh swarm
ntm kill PROJECT -f
ntm spawn PROJECT --cc=5 --cod=2
ntm send PROJECT --all "$(cat init_prompt.txt)"
```

### Why This Works

All state lives in:
- **AGENTS.md** — Project context
- **Beads (br)** — Task state
- **Agent Mail** — Communication history

No state in agent memory is critical.

---

## Stuck Beads

### Symptoms
- Bead in-progress for too long
- No recent commits touching its files
- Agent that claimed it is gone

### Detection

```bash
# Check in-progress beads
br list --status in_progress --json | jq '.[].id'

# Check recent git activity
git log --oneline -10

# Cross-reference: in-progress bead with no recent commits = likely stuck
```

### Recovery

```bash
# Option A: Different agent resumes
# New agent runs bv, sees stuck bead, claims it

# Option B: Explicitly unstick
br update BEAD_ID --status open
# Now any agent can claim fresh

# Option C: Mark blocked
br update BEAD_ID --status blocked --reason "Previous agent crashed mid-work"
```

---

## Communication Breakdown

### Symptoms
- Agents not responding to mail
- Multiple agents claiming same work
- Coordination conflicts

### Recovery

```bash
# 1. Check agent mail status
ntm mail inbox PROJECT

# 2. Broadcast sync message
ntm mail send PROJECT --all "SYNC: All agents please check mail, report current bead, coordinate."

# 3. Review file reservations
ntm locks PROJECT --all-agents

# 4. If conflicts exist
# Agents coordinate via mail to resolve
```

### Prevention

Standard init prompt includes:
- "Check your agent mail"
- "Don't get stuck in communication purgatory"
- "Inform fellow agents when starting tasks"

---

## Rate Limit Recovery

### Symptoms
- Agent hitting API rate limits
- Slow responses, errors
- Multiple agents competing for same API

### Recovery

```bash
# Check which agents are affected
ntm activity PROJECT --watch

# Reduce agent count temporarily
ntm kill PROJECT:cc_3 PROJECT:cc_4

# Or pause some agents
ntm send PROJECT:cc_1 "Pause for 5 minutes, other agents are rate limited"

# After rate limit clears
ntm add PROJECT --cc=2
```

### Prevention

NTM monitors for rate limit patterns and can alert or auto-throttle.

---

## Recovery Checklist

When any failure occurs:

- [ ] **Identify scope** — Single agent or multiple?
- [ ] **Check beads** — `br list --status in_progress`
- [ ] **Check mail** — `ntm mail inbox PROJECT`
- [ ] **Check activity** — `ntm activity PROJECT`
- [ ] **Spawn replacement if needed** — `ntm add PROJECT --cc=1`
- [ ] **Give init prompt** — Standard or recovery variant
- [ ] **Verify recovery** — Watch for normal bead progression

---

## Key Principle

**Fungibility means simple recovery:**

| Traditional | Fungible |
|-------------|----------|
| Identify failed role | Just start new agent |
| Recreate role context | Give standard prompt |
| Reassign dependencies | Agent finds work via bv |
| Balance roles again | No roles to balance |
