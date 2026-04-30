---
name: dueling-idea-wizards
description: >-
  Multi-agent adversarial idea generation and scoring via NTM swarm. Use when
  "dueling idea wizards", "competing ideas", "adversarial brainstorm", or
  cross-model idea evaluation for any project.
---

<!-- TOC: Overview | Arguments | Pre-Flight | Phase 1: Detect Agents | Phase 2: Spawn | Phase 3: Study | Phase 4: Ideate | Phase 5: Cross-Score | Phase 6: Reveal | Phase 7: Synthesize | Anti-Patterns | Troubleshooting | References -->

# Dueling Idea Wizards

> **Core insight:** Two different AI models independently generate their best ideas, then score each other's ideas adversarially. Where they strongly agree, the ideas are genuinely good. Where they trash each other, the ideas are suspect. This kills mediocre ideas fast and surfaces the real winners.

> **Why it works:** Models have different blind spots and biases. A single model's "best ideas" are contaminated by its own confirmation bias. Cross-model adversarial scoring is a cheap, fast triangulation mechanism that exploits disagreement as signal.

> **You are the orchestrator.** You detect agents, spawn the swarm, relay outputs between agents, monitor progress, and compile the final synthesis. The swarm agents do the deep thinking; you do the logistics and final report.

## Why This Is Different From Single-Agent Ideation

The standard `idea-wizard` (single agent, 30->5 winnowing) produces good ideas but suffers from a fundamental flaw: **the same model that generated the idea also evaluates it.** This is like grading your own homework. Models have systematic biases -- Claude over-weights safety and nuance, Codex gravitates toward implementation-heavy features, Gemini tends toward breadth over depth. No single model can see its own blind spots.

The dueling approach creates an **adversarial market for ideas**. Each model must defend its ideas against a genuinely different intelligence. Ideas that survive adversarial cross-model scoring are qualitatively different from ideas that merely survived a single model's internal winnowing. The places where models *strongly agree* -- despite having different biases, different training data, different reasoning styles -- represent a signal that is much closer to "objectively good" than any single model can produce.

**The catty disagreements are the point.** When one model gives an idea 900 and the other gives it 350, that gap is pure information. Either one model sees something the other doesn't, or one model has a systematic bias the other corrects for. The reveal phase (showing each model how the other scored *their* ideas) is where models are forced to confront this gap honestly -- and the concessions they make are the highest-signal output of the entire process.

## Arguments

Parse from invocation text. Defaults:

| Argument | Default | Description |
|----------|---------|-------------|
| `--project=PATH` | cwd | Target project to analyze |
| `--ideas=N` | 30 | Starting idea count before winnowing |
| `--top=N` | 5 | Ideas each agent winnows to |
| `--expand` | false | Run Phase 4b to expand from 5 to 15 ideas per agent |
| `--rounds=N` | 1 | Number of duel rounds (kill/relaunch between rounds) |
| `--mode=MODE` | `ideas` | Duel type: `ideas`, `architecture`, `security`, `ux`, `performance` |
| `--output=PATH` | `DUELING_WIZARDS_REPORT.md` | Report filename |
| `--focus=TOPIC` | (none) | Optional focus area to bias ideation |
| `--beads` | false | Auto-create beads from consensus winners after synthesis |

## Pre-Flight

1. **Read the target project** -- you need to understand it to judge the synthesis:
   ```bash
   cat README.md AGENTS.md CLAUDE.md 2>/dev/null | head -500
   git log --oneline -20
   ```

2. **Verify NTM:**
   ```bash
   ntm deps -v
   ```

3. **Determine PROJECT** from the target directory basename.

## Phase 1: Detect Available Agents

Check which agent CLIs are installed and working. Need **at least 2 different types**.

```bash
# Check each agent type
which cc >/dev/null 2>&1 && echo "cc: available" || echo "cc: missing"
which cod >/dev/null 2>&1 && echo "cod: available" || echo "cod: missing"
which gemini >/dev/null 2>&1 && echo "gmi: available" || echo "gmi: missing"
```

### Agent Selection Priority

Pick exactly 2 agents (or 3 if all available), preferring maximum model diversity:

| Available | Spawn |
|-----------|-------|
| cc + cod + gmi | `--cc=1 --cod=1 --gmi=1` (3-way duel) |
| cc + cod | `--cc=1 --cod=1` (classic duel) |
| cc + gmi | `--cc=1 --gmi=1` |
| cod + gmi | `--cod=1 --gmi=1` |
| Only 1 type | **ABORT** -- dueling requires at least 2 different model types |

**Record which agent types and pane indices are used.** You need this to route prompts correctly.

## Phase 2: Spawn the Swarm

```bash
ntm spawn $PROJECT \
  --cc=$NUM_CC --cod=$NUM_COD --gmi=$NUM_GMI \
  --no-user \
  --stagger-mode=smart
```

Wait for ready:
```bash
ntm --robot-wait=$PROJECT --condition=idle --timeout=120
```

## Phase 3: Project Study

Send ALL agents the same study prompt:

```bash
ntm send $PROJECT --all "First read ALL of the AGENTS.md file and README.md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code, and technical architecture and purpose of the project."
```

Wait for all agents to finish studying:
```bash
ntm --robot-wait=$PROJECT --condition=idle --timeout=180
```

## Phase 4: Independent Ideation (The Idea Wizard Prompt)

Send each agent the ideation prompt. If `--focus` is set, append the focus topic. If `--mode` is set, use the mode-specific variant from [VARIANTS.md](references/VARIANTS.md).

```bash
ntm send $PROJECT --all "Come up with your very best ideas for improving this project to make it more robust, reliable, performant, intuitive, user-friendly, ergonomic, useful, compelling, etc. while still being obviously accretive and pragmatic. Come up with $NUM_IDEAS ideas and then really think through each idea carefully, how it would work, how users are likely to perceive it, how we would implement it, etc; then winnow that list down to your VERY best $NUM_TOP ideas. Explain each of the $NUM_TOP ideas in order from best to worst and give your full, detailed rationale and justification for how and why it would make the project obviously better and why you're confident of that assessment. Write your final top $NUM_TOP ideas to a file called WIZARD_IDEAS_[YOUR_AGENT_TYPE].md (e.g., WIZARD_IDEAS_CC.md or WIZARD_IDEAS_COD.md or WIZARD_IDEAS_GMI.md). Use ultrathink."
```

Wait for all agents to produce their files:
```bash
ntm --robot-wait=$PROJECT --condition=idle --timeout=300
```

**Collect outputs:**
```bash
ls -la WIZARD_IDEAS_*.md
```

Read ALL output files completely. You need the full text for the cross-scoring phase.

### Phase 4b: Expansion (when --expand is set)

The #6-15 ideas are often the most interesting -- they're complementary angles that the top 5 don't cover. More material means richer cross-scoring.

```bash
ntm send $PROJECT --all "Ok and your next best 10 ideas and why. Add them to your WIZARD_IDEAS_[TYPE].md file."
```

Wait, then re-read the expanded files. Now each agent has 15 ideas and the cross-scoring has much more surface area to work with.

### Phase 4c: Overlap Check (recommended)

Before cross-scoring, check if both agents generated the same ideas. If the top 5 are identical, the duel will be boring. Read both files and check.

```bash
br list --json | jq '.[].title'    # Also check against existing beads
```

If >3 ideas overlap, note this as strong independent convergence in the report. For the cross-scoring, the *different* ideas are where the real value is.

## Phase 5: Cross-Scoring (The Duel)

This is the critical phase. Show each agent the OTHER agent's ideas and ask them to score 0-1000.

For each agent, send a prompt containing the other agent(s)' ideas. Use `--pane=N` to target.

### 2-Agent Duel

```bash
# Send Agent B's ideas to Agent A
ntm send $PROJECT --pane=$PANE_A "I asked another model the same thing and it came up with this list:

\`\`\`
$(cat WIZARD_IDEAS_$TYPE_B.md)
\`\`\`

Now, I want you to very carefully consider and evaluate each of them and then give me your candid evaluation and score them from 0 (worst) to 1000 (best) as an overall score that reflects how good and smart the idea is, how useful in practical, real-life scenarios it would be for humans and AI coding agents like yourself, how practical it would be to implement it all correctly, whether the utility/advantages of the new feature/idea would easily justify the increased complexity and tech debt, etc. Write your scores and evaluations to WIZARD_SCORES_${TYPE_A}_ON_${TYPE_B}.md. Use ultrathink."

# Send Agent A's ideas to Agent B (simultaneously)
ntm send $PROJECT --pane=$PANE_B "I asked another model the same thing and it came up with this list:

\`\`\`
$(cat WIZARD_IDEAS_$TYPE_A.md)
\`\`\`

Now, I want you to very carefully consider and evaluate each of them and then give me your candid evaluation and score them from 0 (worst) to 1000 (best) as an overall score that reflects how good and smart the idea is, how useful in practical, real-life scenarios it would be for humans and AI coding agents like yourself, how practical it would be to implement it all correctly, whether the utility/advantages of the new feature/idea would easily justify the increased complexity and tech debt, etc. Write your scores and evaluations to WIZARD_SCORES_${TYPE_B}_ON_${TYPE_A}.md. Use ultrathink."
```

### 3-Agent Duel

Each agent scores BOTH other agents' ideas. 6 scoring files total. Send all 3 prompts simultaneously -- each agent gets a combined file of the other two agents' ideas.

Wait for scoring to complete:
```bash
ntm --robot-wait=$PROJECT --condition=idle --timeout=300
ls -la WIZARD_SCORES_*.md
```

Read ALL scoring files.

## Phase 6: The Reveal (Fireworks Phase)

Show each agent how the OTHER agent scored THEIR ideas. This is where it gets interesting.

```bash
ntm send $PROJECT --pane=$PANE_A "I asked the other model the exact same thing, to score YOUR ideas using the same grading methodology; here is what it came up with:

\`\`\`
$(cat WIZARD_SCORES_${TYPE_B}_ON_${TYPE_A}.md)
\`\`\`

Now give me your honest reaction. Where do you agree with their assessment? Where do you think they're wrong, and why? Are there any ideas where you now think the other model made a good point that changes your own evaluation? Write your reactions to WIZARD_REACTIONS_${TYPE_A}.md. Use ultrathink."
```

Send the symmetric prompt to Agent B (and Agent C if 3-way). Wait for completion.

```bash
ntm --robot-wait=$PROJECT --condition=idle --timeout=300
ls -la WIZARD_REACTIONS_*.md
```

Read ALL reaction files.

## Phase 6.5: Rebuttal Round (optional, recommended)

After the reveal, have each agent write a formal rebuttal defending their most underrated ideas and attacking the opponent's weakest. This is where the methodology produces the most honest, technically specific output. See [PROMPTS.md](references/PROMPTS.md) for the full prompt. Outputs `WIZARD_REBUTTAL_*.md`.

## Phase 6.75: Steelman Challenge (optional, high-value)

Force each agent to write the **strongest possible case** for their opponent's #1 idea. Counterintuitive but incredibly valuable -- an agent forced to steelman its opponent's idea often discovers why it's actually good, and the resulting steelman is more compelling than the originator's own pitch. See [PROMPTS.md](references/PROMPTS.md). Outputs `WIZARD_STEELMAN_*.md`.

## Phase 6.9: The Blind Spot Probe (optional, creative goldmine)

After the full adversarial exchange, ask BOTH agents: "What important idea did NEITHER of us think of?" The adversarial pressure has expanded both models' understanding beyond their original framing. The ideas that emerge here are often the most creative of the entire session because they're generated from a richer, adversarially-expanded context. See [PROMPTS.md](references/PROMPTS.md). Outputs `WIZARD_BLINDSPOTS_*.md`.

## Phase 7: Synthesis (The Orchestrator's Job)

You now have a rich set of artifacts. Compile the final report.

### Artifacts to Synthesize

| File Pattern | Contents |
|-------------|----------|
| `WIZARD_IDEAS_*.md` | Each agent's top ideas |
| `WIZARD_SCORES_*_ON_*.md` | Cross-scoring evaluations |
| `WIZARD_REACTIONS_*.md` | Post-reveal reactions |
| `WIZARD_REBUTTAL_*.md` | Formal rebuttals (Phase 6.5) |
| `WIZARD_STEELMAN_*.md` | Forced steelman arguments (Phase 6.75) |
| `WIZARD_BLINDSPOTS_*.md` | Ideas neither model initially thought of (Phase 6.9) |

### Synthesis Process

1. **Build the score matrix.** For each idea from each agent, record: self-ranking, opponent's score (0-1000), any score changes post-reveal, rebuttal outcome, steelman strength.

2. **Identify strong consensus** -- ideas scored 700+ by ALL agents. These are the real winners.

3. **Identify contested ideas** -- high self-score but low opponent score (or vice versa). Cross-reference with rebuttals: did the defense hold? Flag for human judgment with the strongest argument from each side.

4. **Identify mutual kills** -- ideas scored below 300 by the opponent AND the originator conceded post-reveal. These are dead.

5. **Integrate blind spot ideas** -- the Phase 6.9 blind spots are some of the most creative output. Score them yourself against the rubric; they haven't been cross-scored, so they need extra scrutiny.

6. **Rank the surviving ideas** by average cross-model score, weighting consensus higher than unilateral enthusiasm. Steelmanned ideas that survived rebuttal get a bonus.

7. **Extract the meta-insights** -- what patterns do the disagreements reveal about each model's biases? What did the steelman challenge reveal about hidden value? What blind spots did neither model catch until pushed? See [DYNAMICS.md](references/DYNAMICS.md) for how to read the tea leaves.

### Write the Report

Write `DUELING_WIZARDS_REPORT.md` (or custom `--output` path) with this structure:

```markdown
# Dueling Idea Wizards Report: [PROJECT_NAME]

## Executive Summary
[1 paragraph: how many ideas generated, how many survived, top 3 consensus picks]

## Methodology
- Agents used: [types and models]
- Ideas generated: [N] per agent, winnowed to [top]
- Scoring: adversarial cross-model 0-1000 scale
- Phases: study -> ideate -> cross-score -> reveal -> synthesize

## Consensus Winners (scored 700+ by all agents)
[Ranked list with average scores, each agent's score, and key arguments for/against]

## Contested Ideas (large score gap between agents)
[List with each side's reasoning -- leave for human judgment]

## Killed Ideas (mutual agreement they're weak)
[Brief list with why they died]

## Score Matrix
| Idea | Origin | Self-Rank | Agent A Score | Agent B Score | Avg | Verdict |
...

## Meta-Analysis
- What biases did each model show?
- Where did adversarial pressure improve idea quality?
- What categories of ideas did each model favor?

## Recommended Next Steps
[Top 3-5 ideas to pursue, with implementation notes]
```

## Phase 8: Operationalize Winners (when --beads is set)

Turn consensus winners into actionable beads. This is the bridge from "good ideas" to "actual work."

For each consensus winner (scored 700+ by all agents):

```bash
br create "Epic: [IDEA_TITLE]" -p 1 -t epic --body "
## Background
[Summary of the idea from both agents' perspectives]

## Cross-Model Validation
- Agent A score: [X]/1000 -- [key argument]
- Agent B score: [Y]/1000 -- [key argument]
- Consensus verdict: [STRONG/WIN]

## Goals
[Derived from both agents' rationale]

## Implementation Approach
[Synthesized from both agents' suggested approaches]

## Risks and Concerns
[Aggregated from cross-scoring criticism -- the opponent's objections are the most honest risk assessment you'll get]

## Success Criteria
[How to know this idea worked]
"
```

Then create subtasks and dependencies per the `idea-wizard` Phase 5 pattern. After creating all beads:

```bash
bv --robot-insights | jq '.Cycles'      # Must be empty
bv --robot-plan | jq '.plan.summary'    # Sanity check
br ready --json | jq 'length'           # Verify work exists
```

For contested ideas (large score gap), create beads with priority 3 (low) and add a comment noting the disagreement. These are "parking lot" items for future re-evaluation.

## Multi-Round Dueling (when --rounds > 1)

For deeper exploration, run multiple rounds with fresh agent sessions between rounds. Each round explores different territory.

### Round Lifecycle

```
Round 1: Standard duel (broad ideation)
  → Kill sessions, collect all artifacts
Round 2: Focused duel (use --focus on area Round 1 flagged as contested)
  → Kill sessions, collect
Round N: Continue until diminishing returns
```

Between rounds:
1. Capture all output: `ntm --robot-tail=$PROJECT --lines=200`
2. Kill and relaunch: `ntm --robot-restart-pane=$PROJECT`
3. Adjust focus based on previous round's contested areas
4. Each round appends `_R2`, `_R3` etc. to filenames

Multi-round dueling exploits prompt caching (fresh context = fresh ideas) and prevents the "exhausted mine" problem where agents keep rephrasing the same ideas.

## Duel Modes (--mode variants)

The default `ideas` mode runs the standard Idea Wizard. Other modes swap the ideation prompt for domain-specific variants. See [VARIANTS.md](references/VARIANTS.md) for all prompts.

| Mode | What agents generate | Best for |
|------|---------------------|----------|
| `ideas` | General improvement ideas (default) | Feature brainstorming, roadmap planning |
| `architecture` | Architectural proposals and refactors | Design decisions, tech debt |
| `security` | Security hardening ideas and threat models | Pre-launch audit, attack surface reduction |
| `ux` | UX/ergonomic improvements | CLI tools, user-facing products |
| `performance` | Optimization opportunities with profiling targets | Hot-path code, latency-sensitive systems |

## Monitoring

Set up a monitoring cron after spawning:

```
CronCreate(
  cron: "*/3 * * * *",
  recurring: true,
  prompt: "Check dueling wizards swarm for $PROJECT. Run ntm --robot-is-working=$PROJECT and ntm --robot-tail=$PROJECT --lines=60. Check for WIZARD_IDEAS_*.md and WIZARD_SCORES_*.md files. Report which phase each agent is in (studying/ideating/scoring/reacting) and whether they're working or idle. If idle agents haven't produced their expected output file, nudge them."
)
```

Cancel with `CronDelete` once Phase 6 is complete.

## Anti-Patterns

### Love-Fest Scoring
**Problem:** Agents rate each other's ideas generously to avoid conflict.
**Fix:** The prompt explicitly asks for "candid" evaluation. If scores cluster above 800 for all ideas, send a nudge: "Be more critical. Some of these ideas must have weaknesses. Score them honestly."

### Tribal Defensiveness
**Problem:** Agent rates all its own ideas high and all opponent ideas low reflexively.
**Fix:** The reveal phase catches this -- if an agent can't articulate why the opponent's low scores are wrong, their defensiveness is exposed.

### Convergent Ideation
**Problem:** Both agents generate the same 5 ideas (common for obvious projects).
**Fix:** Good signal! Strong convergence = strong validation. Note in the report. For more diversity, re-run with `--focus` on different areas.

### Skip the Reveal
**Problem:** Tempting to stop after cross-scoring, but the reveal is where agents refine their positions.
**Fix:** Always run Phase 6. The reaction files often contain the most honest assessments.

### Orchestrator Bias
**Problem:** You (the orchestrator) editorialize in the synthesis instead of letting the scores speak.
**Fix:** Report scores and arguments faithfully. Add your own assessment only in the Meta-Analysis section.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Only 1 agent type available | Cannot duel -- need 2+ types. Install another agent CLI |
| Agent won't write output file | Nudge: "Write your ideas to WIZARD_IDEAS_[TYPE].md NOW" |
| Agent scores everything 500 | Send depth nudge asking for more granular, honest scores |
| NTM spawn fails | Check `ntm config get projects_base`, `ntm deps -v` |
| Agent reads opponent's file directly | Output files are in the same directory; agents might peek. The prompts relay content explicitly to avoid this, but it's not a concern -- the scoring prompt provides the full text |
| Gemini falls back to Flash | Retire that agent; see `code-review-gemini-swarm-with-ntm` for Flash detection |

## Reference Index

| Topic | Reference |
|-------|-----------|
| All prompt templates with exact wording and variants | [PROMPTS.md](references/PROMPTS.md) |
| Scoring rubric, idea evaluation criteria, and calibration guidance | [SCORING.md](references/SCORING.md) |
| Agent detection, swarm management, monitoring, and 3-way duel logistics | [OPERATIONS.md](references/OPERATIONS.md) |
| Mode-specific ideation prompts (architecture, security, UX, performance) | [VARIANTS.md](references/VARIANTS.md) |
| Bead creation pipeline, iterative refinement, and operationalization | [BEADS.md](references/BEADS.md) |
| Epistemological framework, adversarial dynamics, and methodology theory | [METHODOLOGY.md](references/METHODOLOGY.md) |
| Model personalities, disagreement taxonomy, reveal patterns, cattiness | [DYNAMICS.md](references/DYNAMICS.md) |
| Pre-duel prep, post-duel validation, full pipeline, cross-skill integration | [INTEGRATION.md](references/INTEGRATION.md) |

## Related Skills

- `idea-wizard` for the single-agent (non-dueling) version
- `multi-model-triangulation` for general cross-model validation
- `ntm` for NTM command reference
- `vibing-with-ntm` for swarm orchestration patterns
- `code-review-gemini-swarm-with-ntm` for similar NTM swarm skill
- `modes-of-reasoning-project-analysis` for multi-perspective analysis
- `operationalizing-expertise` for turning findings into reusable artifacts
