# Operations Guide

## Agent Detection

### Full Detection Script

Run this at the start of every invocation:

```bash
# Detect available agents
CC_AVAILABLE=false; COD_AVAILABLE=false; GMI_AVAILABLE=false
which cc >/dev/null 2>&1 && CC_AVAILABLE=true
which cod >/dev/null 2>&1 && COD_AVAILABLE=true
which gemini >/dev/null 2>&1 && GMI_AVAILABLE=true

# Count available types
AGENT_COUNT=0
$CC_AVAILABLE && AGENT_COUNT=$((AGENT_COUNT + 1))
$COD_AVAILABLE && AGENT_COUNT=$((AGENT_COUNT + 1))
$GMI_AVAILABLE && AGENT_COUNT=$((AGENT_COUNT + 1))

echo "Available: cc=$CC_AVAILABLE cod=$COD_AVAILABLE gmi=$GMI_AVAILABLE (total types: $AGENT_COUNT)"
```

If `AGENT_COUNT < 2`, abort with a clear message explaining which agents are missing and how to install them.

### Agent Installation Hints

| Agent | Install |
|-------|---------|
| cc (Claude Code) | `npm install -g @anthropic-ai/claude-code` or `brew install claude-code` |
| cod (Codex) | `npm install -g @openai/codex` |
| gemini | `npm install -g @google/gemini-cli` |

### Pane-to-Agent Mapping

After `ntm spawn`, NTM assigns pane indices. Record the mapping:

```bash
ntm --robot-snapshot | jq '.sessions[].panes[] | {index, type, model}'
```

Example mapping for a cc+cod duel:
```
Pane 0: cc (claude)
Pane 1: cod (codex)
```

Example for a 3-way duel:
```
Pane 0: cc (claude)
Pane 1: cod (codex)
Pane 2: gmi (gemini)
```

You need this mapping to route `--pane=N` prompts correctly in Phases 5 and 6.

## Swarm Lifecycle

### Phase Timing Budget

| Phase | Expected Duration | Timeout |
|-------|------------------|---------|
| Study (Phase 3) | 2-5 min | 180s |
| Ideation (Phase 4) | 5-15 min | 300s |
| Cross-Scoring (Phase 5) | 5-15 min | 300s |
| Reveal (Phase 6) | 3-10 min | 300s |
| Synthesis (Phase 7) | 5-10 min (you) | N/A |
| **Total** | **20-55 min** | **~80 min hard limit** |

### Session Reuse

If an NTM session already exists for the project:

```bash
ntm list --json 2>/dev/null | grep -q "$PROJECT"
```

Ask user: reuse (skip Phase 2) or kill and recreate. Reusing saves spawn time but agents may have stale context.

### Graceful Degradation

If an agent hits rate limits or errors mid-duel:

- **During Phase 4 (ideation):** Wait up to 5 min. If still broken, proceed with remaining agents.
- **During Phase 5 (scoring):** You can proceed with a 1-sided score. Note in the report that cross-scoring was incomplete.
- **During Phase 6 (reveal):** Skip the reveal for the broken agent. The other agent's reaction to their scores is still valuable.

In all cases, note the degradation in the report's Methodology section.

### Gemini Flash Detection

If using Gemini agents, watch for model downgrade (same as `code-review-gemini-swarm-with-ntm`):

```bash
ntm --robot-tail=$PROJECT --lines=50 --type=gmi | grep -i "fallback model"
```

Exact strings to match:
```
Switched to fallback model gemini-3-flash-preview
Switched to fallback model gemini-2.5-flash
```

If detected, retire the Gemini agent. If it's the only agent of its type, you lose a dueling partner -- proceed with whatever cross-scoring data you have.

## Monitoring Cron

### Cron Prompt (phase-aware)

The monitoring cron should be aware of which phase the swarm is in. The orchestrator (you) tracks phase state and the cron checks progress:

```
CronCreate(
  cron: "*/3 * * * *",
  recurring: true,
  prompt: "Check dueling wizards swarm for $PROJECT. Run: ntm --robot-is-working=$PROJECT and ntm --robot-tail=$PROJECT --lines=60. Check for output files: ls -la WIZARD_IDEAS_*.md WIZARD_SCORES_*.md WIZARD_REACTIONS_*.md 2>/dev/null. Report: (1) which agents are working vs idle, (2) which output files exist, (3) any errors or rate limits visible in tail output. If agents are idle and missing expected files, send the appropriate nudge from PROMPTS.md."
)
```

### Cron Lifecycle

1. Create immediately after `ntm spawn` (Phase 2)
2. The cron fires every 3 minutes while REPL is idle
3. Cancel with `CronDelete` after Phase 6 completes (before synthesis)
4. If all agents error out, cancel early

## 3-Way Duel Logistics

A 3-way duel produces significantly more artifacts and cross-scoring combinations.

### Artifact Count

| Phase | 2-Way | 3-Way |
|-------|-------|-------|
| Ideas files | 2 | 3 |
| Scoring files | 2 | 3 (each scores both others) |
| Reaction files | 2 | 3 |
| **Total** | **6** | **9** |

### Score Matrix for 3-Way

```
| Idea | Origin | CC Score | COD Score | GMI Score | Avg | Consensus |
|------|--------|----------|-----------|-----------|-----|-----------|
| #1   | CC     | (self)   | 850       | 780       | 815 | STRONG    |
| #2   | COD    | 720      | (self)    | 690       | 705 | MODERATE  |
| #3   | GMI    | 400      | 350       | (self)    | 375 | KILL      |
```

### Routing 3-Way Prompts

In Phase 5, each agent gets a combined file of both other agents' ideas. Use the 3-agent prompt variant from [PROMPTS.md](PROMPTS.md).

In Phase 6, each agent gets both other agents' scoring of their ideas. Use the 3-agent reveal variant.

## File Naming Convention

All output files are written to the PROJECT root directory:

| File | Phase | Written By |
|------|-------|-----------|
| `WIZARD_IDEAS_CC.md` | 4 | Claude Code agent |
| `WIZARD_IDEAS_COD.md` | 4 | Codex agent |
| `WIZARD_IDEAS_GMI.md` | 4 | Gemini agent |
| `WIZARD_SCORES_CC_ON_COD.md` | 5 | CC scoring COD's ideas |
| `WIZARD_SCORES_COD_ON_CC.md` | 5 | COD scoring CC's ideas |
| `WIZARD_SCORES_CC_ON_OTHERS.md` | 5 | CC scoring both (3-way) |
| `WIZARD_REACTIONS_CC.md` | 6 | CC reacting to scores of its ideas |
| `DUELING_WIZARDS_REPORT.md` | 7 | Orchestrator's synthesis |

**Do NOT delete any of these files.** They are evidence and appendix material for the report.

## Quality Signals

### Good Duel Indicators

- Scores spread across the full 0-1000 range (not all clustered at 600-700)
- Agents cite specific technical reasons for scores, not vague "this seems good"
- Post-reveal reactions include at least one concession per agent
- Some ideas score high from all agents (consensus exists)
- Some ideas score wildly differently (genuine disagreement, not noise)

### Bad Duel Indicators

- All scores between 500-700 (no conviction)
- Agents score based on surface similarity to their own ideas
- Post-reveal reactions are purely defensive with no concessions
- Both agents generated the same 5 ideas (no diversity to duel over)
- Agents rate implementation difficulty but ignore conceptual quality

### Intervention Triggers

| Signal | Action |
|--------|--------|
| All scores > 700 | Send "be more critical" nudge |
| All scores < 300 | Send "be fair -- what are the genuine merits?" nudge |
| Scores are all 500 | Send "spread your scores -- some must be better than others" nudge |
| No file after 10 min | Send explicit "write your file NOW" nudge |
| Agent editing project code | Send "Do NOT modify project files. Write only WIZARD_*.md files." |
