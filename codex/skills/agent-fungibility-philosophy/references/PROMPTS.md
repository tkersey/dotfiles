# Agent Initialization Prompts

## Table of Contents
- [Standard Init Prompt](#standard-init-prompt)
- [Minimal Init Prompt](#minimal-init-prompt)
- [Recovery Init Prompt](#recovery-init-prompt)
- [Context Rotation Prompt](#context-rotation-prompt)
- [Focused Work Prompt](#focused-work-prompt)

---

## Standard Init Prompt

The full initialization prompt for fungible agents:

```
First read ALL of the AGENTS.md file and README.md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code, technical architecture and purpose of the project. Then register with MCP Agent Mail and introduce yourself to the other agents.

Be sure to check your agent mail and promptly respond if needed to any messages; then proceed meticulously with your next assigned beads, working on the tasks systematically and tracking your progress via beads and agent mail messages.

Don't get stuck in "communication purgatory" where nothing is getting done; be proactive about starting tasks that need to be done, but inform your fellow agents via messages when you do so and mark beads appropriately.

When you're not sure what to do next, use bv to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Make sure to acknowledge all communication requests from other agents. Use ultrathink.
```

---

## Minimal Init Prompt

When agents already know the codebase or for quick restarts:

```
Read AGENTS.md, register with Agent Mail, check your inbox, then use bv to find your next bead and get to work. Use ultrathink.
```

---

## Recovery Init Prompt

When replacing a failed agent that was mid-task:

```
Read AGENTS.md carefully. Check agent mail for any messages from other agents. Run `br list --status in_progress` to see what beads are currently being worked on.

If a bead has been in-progress for too long without commits, it may be orphaned from a crashed agent. Check git log to see recent activity. If the bead appears stuck, either resume it or mark it blocked with a reason.

Use bv to find the next optimal bead and continue working. Coordinate via agent mail.
```

---

## Context Rotation Prompt

When an agent hits context limits and compacts:

```
Your context was just compacted. Reread AGENTS.md to refresh your understanding.

Check agent mail for any messages you may have forgotten. Check bead status to see what you were working on.

If you had a bead in-progress, verify its status and either continue or mark appropriately. Use bv for next steps.
```

---

## Focused Work Prompt

When you want agents to focus on a specific domain without assigning roles:

```
Read AGENTS.md, register with Agent Mail. Use bv to find beads.

Preference beads with labels: [frontend, ui, react] — but if none are ready, work on ANY ready bead. You are a generalist who happens to have frontend context right now, not a "frontend agent."

Coordinate via agent mail if you need to hand off or need help.
```

Note: This gives soft preference without creating specialist bottlenecks.

---

## Prompt Elements Explained

| Element | Why It's There |
|---------|---------------|
| `Read AGENTS.md` | All context lives here, not in agent memory |
| `Register with Agent Mail` | Enables coordination |
| `Check inbox` | Prevents missed messages |
| `Use bv` | Decentralized task selection |
| `Mark beads` | State visible to all agents |
| `Communication purgatory` | Named anti-pattern to avoid |
| `ultrathink` | Maximum reasoning for complex tasks |

---

## Prompt Delivery Methods

### Via NTM (Preferred)

```bash
# All agents at once
ntm send PROJECT --all "$(cat init_prompt.txt)"

# Specific agent type
ntm send PROJECT --cc "$(cat init_prompt.txt)"
```

### Via Direct Paste

Copy prompt directly into agent terminal. Works for any CLI agent.

### Via Agent Mail Broadcast

```bash
# From any agent, broadcast to all
ntm mail send PROJECT --all "INIT: Please reread AGENTS.md and check bv for next beads"
```
