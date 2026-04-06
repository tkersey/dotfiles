---
name: reality-check-for-project
description: >-
  Assess project status against README/plan vision. Use when "where are we", "reality check",
  "what's missing", "are we on track", "gap analysis", or "does this actually work".
---

<!-- TOC: Core Insight | THE EXACT PROMPTS | Quick Start | Phase Details | Beads | Ambition | Anti-Patterns | Checklist | References -->

# Reality Check for Project

> **Core Insight:** After days or weeks of methodically cranking on beads with agent swarms, you need periodic "come to Jesus" moments where you step back and honestly assess: **Is the actual implemented code delivering on the project's vision?** Whether or not you already have a sense of the answer, the value is in getting the agent — who has been knee-deep in the code — to articulate the current state from its deep-in-the-trenches perspective. That reveals things the bead count alone can't show, and it lets you **steer** so the swarm stays pointed in the right direction.

## The Problem

Long-running multi-agent projects develop a dangerous blind spot: agents complete beads, tests pass, code compiles — but nobody steps back to ask whether the *aggregate* of all that work actually delivers on the original vision. Beads track tactical progress; this skill tracks strategic alignment. Without periodic reality checks, projects drift: 72% of beads might be complete while 0% of the core value proposition is actually working end-to-end.

The reality check is primarily a **steering mechanism** — not just an audit. The goal is course correction: ensuring that all the concurrent agents aren't collectively drifting away from the vision while individually making progress on their assigned beads.

**Key principle: Code = ground truth for current state; docs = measuring stick for vision.** When README/plan docs diverge from what the code actually does, code tells you where you ARE. Docs tell you where you promised to BE. The gap between them is the entire point of this skill.

## The Complete Flow (read this first)

```
Phase 1: Reality Check Question          → "Where are we REALLY?"
    ↓
Phase 2: Bridge Plan                     → "Close every single conceivable gap"
    ↓
Phase 3a: Bead Creation (FROZEN)         → Always go through beads, never skip to code
    ↓
Phase 4: Ambition Rounds × 2-3          → "decent start but... MUCH MUCH MUCH better"
    ↓                                     → Always "revise in-place", never new doc
Phase 3a again: Re-generate beads
    ↓
Phase 5: Refinement × 4-5 (FROZEN)      → Stop only when round finds nothing
    ↓
bv --robot-triage validation
    ↓
Implementation (agents pick up beads via br ready)
```

**Critical invariants:**
- Ambition → Beads → Refine → Implement. Never skip beads. (120+ sessions, zero exceptions)
- Phase 3a and Phase 5 prompts are **frozen templates** — copy-paste verbatim, do NOT paraphrase
- Phases 4-5 are the **idea-wizard** workflow. If you only need that part, use idea-wizard directly.

---

## THE EXACT PROMPTS

### Phase 1: The Reality Check Question

**Variant A (comprehensive, for first use on a project):**

```
First read ALL of the AGENTS.md, README.md, and every markdown plan/spec document in this project
SUPER carefully and understand them completely. Then use your code investigation agent mode to
fully understand the actual code, architecture, and what's REALLY implemented vs aspirational.

Then I need you to answer honestly:

Where are we REALLY on this project? Does the implemented code actually deliver on the vision
described in the README and plan documents? If not:
1. What specifically IS working right now?
2. What is NOT working or not yet implemented?
3. What is blocking us from getting there?
4. If we were to implement all open and in-progress beads, would we close the gap completely?
   Why or why not?
5. What goals from the vision are NOT covered by ANY existing bead?

Be brutally honest. I need the real picture, not optimistic spin.
```

**Variant B (quicker, for periodic check-ins):**

```
What's the REAL status of this project? Is it essentially finished and living up to the goals and
purpose outlined in the README and plan docs? What is missing still? What isn't yet functioning
properly or completed properly?
```

**Variant C (focused on a specific capability):**

```
Where are we on this project? Do we have a working [X] that can [Y] with [Z quality/performance]?
If not, what is blocking us? If we were to intelligently implement all open and in-progress beads,
would we close that gap completely? Why or why not?
```

**Variant D (integration audit — naming specific libraries/subsystems):**

Real example from CASS project:
```
Where are we on this project? Did we completely replace all the internal search logic with instead
pulling in and integrating completely with /dp/frankensearch? Did we completely replace all the
internal logic for detecting installed agent harnesses by pulling in and integrating
/dp/franken_agent_detection? Have we replaced all database stuff so that it ultimately uses only
/dp/frankensqlite for everything and take full advantage of concurrent writers?
```

**Variant E (stub/wiring audit — checking what's real vs placeholder):**

Real example from frankensearch:
```
I need to understand which CLI commands in [project] are actually wired to real implementations vs
stubs. For each of the N commands, determine if the dispatch handler actually does something real
or is a stub/todo. Report which commands are fully implemented, which are partial/stubs, and which
are missing entirely.
```

**Variant F (marketing claims audit):**

Real example from jeffreys-skills.md:
```
What remains to be done to make this system fully deliver on every single promise and marketing
claim made?
```

**Variant G (mega-prompt — chains Phase 1 → Phase 2 → Phase 3a in one shot):**

This is the speed variant — skips interactive steering and chains the entire flow. Copy-paste ready:
```
I need you to help me fix this. That is, making all the things that are unimplemented but which
SHOULD have been implemented according to the beads and markdown plan. Figure out exactly what
needs to be done to get us over the goal line with a finished, polished, reliable, performant
project in line with the vision described earlier. OK so please take ALL of that and elaborate on
it and use it to create a comprehensive and granular set of beads for all this with tasks,
subtasks, and dependency structure overlaid, with detailed comments so that the whole thing is
totally self-contained and self-documenting (including relevant background, reasoning/justification,
considerations, etc.-- anything we'd want our "future self" to know about the goals and intentions
and thought process and how it serves the over-arching goals of the project.). The beads should be
so detailed that we never need to consult back to the original markdown plan document. Remember to
ONLY use the `br` tool to create and modify the beads and add the dependencies.
```

Use when the agent already has deep context in the project and you want to go straight from assessment to action. For first-time reality checks, use Variant A interactively instead.

**Variant H (performance reality check — with benchmark data):**

Real example from frankensqlite:
```
[paste raw benchmark output here showing specific regressions]

I need you to figure out the underlying root causes of the biggest performance problems, namely:
[list worst regressions with exact numbers], and then come up with a comprehensive, systematic,
radically innovative plan to solve each and every one.
```

### Phase 2: The Bridge Plan

**Variant A (analytical, separate from execution):**

```
OK not great. I need you to come up with a super comprehensive and complete and detailed and
granular plan to close every single conceivable gap so that [project goal] IS fully [done/integrated]
PROPERLY and in an optimal, harmonized, coherent, cohesive way with the absolutely highest quality,
performance, reliability, and robustness.
```

**Variant B (action-oriented, bridge directly into fix mode):**

```
I need you to help me fix this. That is, making all the things that are unimplemented but which
SHOULD have been implemented according to the beads and markdown plan. Figure out exactly what
needs to be done to get us over the goal line with a finished, polished, reliable, performant
project in line with the vision described earlier.
```

**Variant C (for each gap → bead):**

Real example from jeffreys-skills.md:
```
OK for each and every gap, create an ultra comprehensive bead.
```

### Phase 3a: Bead Generation (frozen template — used verbatim across 20+ projects)

This is the second frozen template (along with Phase 5). Do NOT modify it:

```
OK so please take ALL of that and elaborate on it and use it to create a comprehensive and granular
set of beads for all this with tasks, subtasks, and dependency structure overlaid, with detailed
comments so that the whole thing is totally self-contained and self-documenting (including relevant
background, reasoning/justification, considerations, etc.-- anything we'd want our "future self" to
know about the goals and intentions and thought process and how it serves the over-arching goals of
the project.) The beads should be so detailed that we never need to consult back to the original
markdown plan document. Remember to ONLY use the `br` tool to create and modify the beads and add
the dependencies.
```

**Critical addendum** (from flywheel_gateway sessions): It's critical that EVERYTHING from the markdown plan be embedded into the beads so that we never need to refer back to the markdown plan and we don't lose any important context or ideas or insights.

### Phase 3b: Direct Resolution (no beads, short list)

```
OK good, now I need you to come up with an absolutely comprehensive, detailed, and granular plan
for addressing each and every single gap you identified in the most optimal, clever, and
sophisticated way possible. THEN: please resolve ALL of those actionable items now. Keep a super
detailed, granular, and complete TODO list of all items so you don't lose track of anything!
```

### Phase 4: Ambition Rounds (iterate 2-3 times)

The opener is ALWAYS a qualified acknowledgment followed by escalation. Real phrases from 12+ projects:

**Round 1 (the "decent start but" opener):**
```
That's a decent start but it barely scratches the surface and is light years away from being
OPTIMAL. Please try again and revise your existing plan document in-place to make it MUCH, MUCH,
MUCH better in EVERY WAY.
```

**Round 2 (sustained escalation):**
```
That's a lot better than before but STILL is a far cry from being OPTIMAL. Please try yet again
and revise your existing plan document in-place to make it MUCH, MUCH, MUCH better in EVERY WAY.
I believe in you, you can do this!!! Show me how brilliant you really are.
```

**Round 3 (domain-specific depth — inject project-relevant skills/math):**
```
Now, TRULY think even harder. Surely there is some math invented in the last 60 years that would
be relevant and helpful here? Super hard, esoteric math that would be ultra accretive and give a
ton of alpha for the specific problems we're trying to solve here, as efficiently as possible?
REALLY RUMINATE ON THIS!!! DIG DEEP!!
```

Or with skill references: `Use $alien-artifact-coding and $extreme-software-optimization. BE AMBITIOUS.`

Or the full hype-man version — sounds odd on paper but genuinely works as a counter-strategy against trained incrementalism:
```
Your new beads should make heavy use of concepts from [relevant skills], because that's the only
chance we have to BLOW past [competitors] in sophistication, bringing techniques to bear that
those teams would never dream of using because they're too abstruse and esoteric, but by wielding
them with clever and canny brilliance, we will be able to leapfrog past all competing projects!!!
I BELIEVE IN YOU MY FRIEND. LET US CHANGE THE WORLD TOGETHER.
```

**Key:** The transition from ambition to implementation is ALWAYS through bead creation (Phase 3a) — never directly to code. Full phrase corpus: [AMBITION-ROUNDS.md](references/AMBITION-ROUNDS.md).

### Phase 5: Plan-Space Refinement (iterate 4-5 times — this is a frozen template)

This prompt is copy-pasted verbatim across 20+ projects. Do NOT modify it.

**Note:** The idea-wizard variant prepends `Reread AGENTS.md so it's still fresh in your mind.` — use that prefix after context compactions.

```
Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change
anything to make the system work better for users? If so, revise the beads. It's a lot easier and
faster to operate in "plan space" before we start implementing these things! DO NOT OVERSIMPLIFY
THINGS! DO NOT LOSE ANY FEATURES OR FUNCTIONALITY! Also make sure that as part of the beads we
include comprehensive unit tests and e2e test scripts with great, detailed logging so we can be
sure that everything is working perfectly after implementation. Make sure to ONLY use the `br` cli
tool for all changes, and you can and should also use the `bv` tool to help diagnose potential
problems with the beads.
```

**Why 4-5 times:** Each refinement pass finds 11-15 new gaps, test holes, or dependency issues. Evidence from wezterm_automata session: 5 refinement rounds, each creating new beads to fill discovered gaps. Stop only when a round finds nothing to change.

---

## Quick Start

### Step 0: Detect Project Tooling

```bash
# Check for beads
if [ -d ".beads" ] && command -v br &>/dev/null; then
  echo "BEADS_AVAILABLE=true"   # Use Phase 3a workflow
  echo "OPEN=$(br list --status=open --json 2>/dev/null | jq length)"
  echo "CLOSED=$(br list --status=closed --json 2>/dev/null | jq length)"
  echo "IN_PROGRESS=$(br list --status=in_progress --json 2>/dev/null | jq length)"
else
  echo "BEADS_AVAILABLE=false"  # Use Phase 3b workflow
fi

# Check for bv
command -v bv &>/dev/null && echo "BV_AVAILABLE=true"
```

### Step 1: Extract the Vision (DOCUMENTATION FIRST)

Read these files completely and carefully — they define the "promise":

```bash
cat README.md
cat AGENTS.md
# Find all plan/spec documents
find . -maxdepth 3 -name "*.md" | grep -iE "plan|spec|design|architecture|vision|roadmap" | head -20
ls docs/ 2>/dev/null
```

Distill the vision into a **Vision Checklist**: a numbered list of concrete, testable goals that the project promises to deliver. This is your measuring stick.

### Step 2: Assess Beads Landscape (if available)

```bash
br list --status=open --json 2>/dev/null | jq length       # How much is left
br list --status=closed --json 2>/dev/null | jq length      # How much is done
br list --status=in_progress --json 2>/dev/null | jq length # What's active
bv --robot-triage 2>/dev/null | jq '.quick_ref'             # Health snapshot
bv --robot-forecast all 2>/dev/null | jq '.forecast.summary' # ETA
```

**Key question:** Do the open beads, if ALL completed, cover ALL vision goals? Or are there goals with ZERO bead coverage?

### Step 3: Code Reality Check (the hard part)

Actually examine the implemented code. For each vision goal:

1. **Find the code** that supposedly implements it
2. **Read it** — is it real or a stub/placeholder/mock?
3. **Check tests** — are there tests proving it works? Do they pass?
4. **Try to run it** — does the software actually work end-to-end?
5. **Check performance** — does it meet the goals (if performance is part of the vision)?

Use the mock-code-finder methodology here: keyword scan + AST scan + behavioral scan.

### Step 4: Produce the Gap Analysis

For each vision goal, categorize its status. See [GAP-ANALYSIS.md](references/GAP-ANALYSIS.md).

### Step 5: Produce the Bridge Plan

For every gap, specify exactly what needs to change. See [BRIDGE-PLAN.md](references/BRIDGE-PLAN.md).

### Step 6: Ambition Rounds + Refinement

Push past incrementalism, then polish in plan space. See [AMBITION-ROUNDS.md](references/AMBITION-ROUNDS.md).

---

## The Vision Checklist

The most critical artifact. Extract from README + plan docs:

```markdown
## Vision Checklist for [Project Name]

| # | Goal | Source | Status | Evidence |
|---|------|--------|--------|----------|
| 1 | [Concrete, testable goal] | README.md L42 | NOT_STARTED | No code found |
| 2 | [Another goal] | PLAN.md sec3 | PARTIAL | src/foo.rs exists but only 2/7 features |
| 3 | [Performance goal] | README.md L88 | UNPROVEN | Code exists, no benchmarks |
| 4 | [User-facing feature] | docs/DESIGN.md | WORKING | Tests pass, e2e verified |
```

**Status categories:**
- `WORKING` — Code exists, tests pass, e2e verified
- `PARTIAL` — Some implementation exists, incomplete
- `STUB` — Placeholder/mock/todo code only
- `UNPROVEN` — Code exists but no tests or tests don't cover it
- `NOT_STARTED` — No code at all for this goal
- `REGRESSED` — Was working, now broken
- `NO_BEAD` — Not covered by any existing bead (critical gap!)
- `WRONG_APPROACH` — Implemented but architecturally flawed, can't reach the goal this way

---

## Gap Categories

| Category | Meaning | Action |
|----------|---------|--------|
| **Vision gap** | Goal exists in docs, no bead covers it | Create new beads |
| **Implementation gap** | Bead exists, code is stub/incomplete | Revise bead, implement |
| **Proof gap** | Code exists, no tests proving it works | Add comprehensive tests |
| **Performance gap** | Works but doesn't meet performance goals | Profile, optimize |
| **Integration gap** | Parts work in isolation, not end-to-end | Add integration/e2e tests |
| **Design gap** | Implemented but architecturally wrong | Redesign, may need new beads |

---

## Anti-Patterns (from real session failures)

| Don't | Do | Evidence |
|-------|-----|----------|
| Accept "72% beads complete" as progress | Check if ANY vision goal is 100% delivered | jeffreys-skills: 85% complete, entire SSO at stub level |
| Trust passing tests = working software | Actually run the software end-to-end | mcp_agent_mail: binary audit found stubs behind "working" CLI |
| Assume open beads cover everything | Cross-check vision goals against bead coverage | frankenjax: 8 documented features had zero bead coverage |
| Create a new plan doc each ambition round | **Revise in-place** — never proliferate docs | Every CASS session uses "revise your existing plan document in-place" |
| Paraphrase the frozen templates | Copy-paste Phase 3a and Phase 5 **verbatim** | These prompts were refined over 20+ projects |
| Go directly from ambition to implementation | **Always go through beads first** (Phase 3a) | Zero exceptions found in 120+ sessions |
| Do 2 refinement rounds and call it done | Do 4-5 — each round finds 11-15 new gaps | wezterm_automata: 5 rounds before convergence |
| Paste frustration without structured analysis | Channel reaction into Phase 1 → Phase 2 flow | frankensqlite: same benchmarks pasted into 6+ sessions without progress |
| Close beads without verifying the fix works | Require proof (test output, demo run) before closing | GitHub audits: issues "closed WITHOUT actually fixing the bug" |

---

## The Complete Flow (reinforced)

```
Phase 1: Reality Check Question
    ↓
Phase 2: Bridge Plan ("close every gap")
    ↓
Phase 3a: Bead Creation (frozen template)       ← ALWAYS go through beads
    ↓
Phase 4: Ambition Rounds × 2-3 ("decent start but...")
    ↓                                             ← "revise in-place", never new doc
Phase 3a again: Re-generate beads from improved plan
    ↓
Phase 5: Refinement × 4-5 (frozen template)     ← stop when round finds nothing
    ↓
bv --robot-triage validation
    ↓
Implementation (agents pick up beads via br ready)
```

**Critical invariant:** Ambition → Beads → Refine → Implement. Never skip beads. Never go directly from ambition to code. This is the single most consistent pattern across 120+ sessions.

---

## Operator Rules (distilled from 12+ projects via /operationalizing-expertise Track C)

**Rule 1: Always revise in-place, never create new documents.**
- **When:** Ambition rounds, plan refinement, bead revision
- **Action:** "revise your existing plan document in-place" / "revise the beads"
- **Why:** Prevents document proliferation. Each round builds on the last. Evidence: Every ambition prompt from CASS says "revise in-place."
- **Failure if skipped:** Multiple competing plan documents, context fragmentation, agents reading stale versions

**Rule 2: The bead creation and refinement prompts are frozen templates.**
- **When:** Phase 3a and Phase 5
- **Action:** Copy-paste the exact text. Do not paraphrase, shorten, or "improve" it.
- **Why:** These were refined over 20+ projects into a carefully calibrated set of requirements. The "DO NOT OVERSIMPLIFY" / "DO NOT LOSE FEATURES" clause specifically prevents regression during refinement.
- **Failure if modified:** Losing the "future self" clause → beads require context from external docs. Losing "DO NOT OVERSIMPLIFY" → model prunes ambition during refinement.

**Rule 3: Check bead coverage against every vision goal, not just bead completion %.**
- **When:** After Phase 1 reality check
- **Action:** For each vision goal, search `br list` for matching beads. Any goal with zero matches = `NO_BEAD` status (critical).
- **Why:** 72% bead completion means nothing if the remaining 28% includes zero coverage of core goals. Evidence: jeffreys-skills.md was 85% individual / 70% enterprise complete but had entire SSO features at stub-level.
- **Failure if skipped:** The "bead completion illusion" — agents grind on tracked work while untracked vision goals go forever unimplemented.

**Rule 4: Distinguish SHIPPED reality from code reality.**
- **When:** Projects with deployments (SaaS, CLIs with releases)
- **Action:** Check what's actually deployed/released, not just what's in the repo. Evidence: jeffreys-skills.md SSO audit asked "what's the SHIPPED SSO reality?"
- **Why:** Code may exist in a branch, behind a feature flag, or simply never deployed.
- **Failure if skipped:** Claiming a feature "works" when users have never seen it.

**Rule 5: Inject project-specific context BEFORE standard templates, not instead of them.**
- **When:** Ambition rounds that need domain-specific depth
- **Action:** Prefix the escalation prompt with project context (skill names, math domains, quantitative targets), then use the standard escalation phrases.
- **Why:** The standard templates handle the escalation mechanics. Project context tells the model WHERE to dig deeper. Evidence: asupersync injected "Mazurkiewicz traces, region-based memory" before "RUMINATE ON THIS."
- **Failure if skipped:** Generic ambition without direction → model explores random tangents instead of project-relevant depth.

---

## When to Use This Skill vs Adjacent Skills

| Situation | Use This | Not This |
|-----------|----------|----------|
| "Is the project delivering on its README promises?" | **reality-check** | codebase-audit |
| "Find all stubs and mocks" | mock-code-finder | **reality-check** |
| "Audit for security/perf/UX issues" | codebase-audit | **reality-check** |
| "Generate ideas for improvements" | idea-wizard | **reality-check** |
| "What bead should I work on next?" | bv | **reality-check** |
| "Create a comprehensive architecture doc" | comprehensive-codebase-report | **reality-check** |
| "Find and fix all bugs" | multi-pass-bug-hunting | **reality-check** |

**Overlap with idea-wizard:** Phases 4-5 of this skill (ambition rounds + refinement) are the idea-wizard workflow. If you've already done the reality check and just need the ambition→bead→refine cycle, use idea-wizard directly.

---

## Checklist

- [ ] **Read ALL docs:** README.md, AGENTS.md, all plan/spec/design documents
- [ ] **Distill vision:** Create numbered Vision Checklist with testable goals
- [ ] **Assess beads:** Count open/closed/in-progress, check coverage of vision goals
- [ ] **Examine code:** For each vision goal, find and read the implementing code
- [ ] **Check for stubs:** Use mock-code-finder methodology on suspect areas
- [ ] **Run tests:** Do existing tests actually pass?
- [ ] **Run the software:** Does it actually work end-to-end?
- [ ] **Produce gap analysis:** Every vision goal categorized with evidence
- [ ] **Identify NO_BEAD gaps:** Vision goals with zero bead coverage (worst gaps)
- [ ] **Produce bridge plan:** Specific changes needed for every gap
- [ ] **Ambition rounds:** 2-3 rounds of "decent start but..." escalation
- [ ] **Plan-space refinement:** 4-5 rounds of the frozen refinement checklist (stop when a round finds nothing)
- [ ] **Generate beads:** Convert bridge plan into comprehensive beads (if available)
- [ ] **Include test beads:** Every implementation bead needs companion test beads
- [ ] **Validate with bv:** Check dependency graph, find quick wins, spot problems

---

## References

| Need | File |
|------|------|
| Gap analysis methodology and output format | [GAP-ANALYSIS.md](references/GAP-ANALYSIS.md) |
| Bridge plan structure and examples | [BRIDGE-PLAN.md](references/BRIDGE-PLAN.md) |
| Ambition rounds — full phrase corpus and theory | [AMBITION-ROUNDS.md](references/AMBITION-ROUNDS.md) |
| Vision extraction from diverse doc formats | [VISION-EXTRACTION.md](references/VISION-EXTRACTION.md) |
| Lessons from real sessions across 12+ projects | [LESSONS-FROM-SESSIONS.md](references/LESSONS-FROM-SESSIONS.md) |
