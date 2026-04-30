# Integration: Combining Dueling Wizards with the Skill Ecosystem

How to chain the dueling-idea-wizards skill with other skills for maximum impact. The duel is powerful on its own, but it becomes transformative when embedded in a larger workflow.

## Pre-Duel Intelligence Gathering

Skills to run BEFORE launching a duel. Better input context produces sharper ideation and more substantive scoring.

### Skill Sequencing Table

| Skill | What It Feeds Into the Duel | When to Use It | Time Cost |
|-------|----------------------------|----------------|-----------|
| `codebase-archaeology` | Deep mental model of project structure, hidden dependencies, architectural patterns | Always for unfamiliar projects; the study phase (Phase 3) is superficial compared to a full archaeology | 15-30 min |
| `reality-check-for-project` | Gap analysis between README vision and actual implementation status | When you want ideas grounded in what actually exists vs. what's aspirational | 10-20 min |
| `modes-of-reasoning-project-analysis` | Multi-perspective findings with contested conclusions | When you want the duel to focus on areas where analytical modes already disagree | 30-60 min |
| `bv --robot-triage` | Current work graph, blocked items, dependency bottlenecks | When ideation should account for existing commitments and priorities | 2-5 min |
| `comprehensive-codebase-report` | Technical architecture document the duel agents can reference | For large/complex codebases where the study phase alone is insufficient | 20-40 min |

### Feeding Pre-Duel Output into the Duel

The pre-duel output shapes the `--focus` argument and the study material:

```bash
# After running reality-check, extract the gap areas
# and feed them as focus topics
dueling-idea-wizards --focus="areas identified as missing by reality-check: [AUTH, TESTING, OBSERVABILITY]"

# After modes-of-reasoning, feed the contested findings
dueling-idea-wizards --focus="contested findings from modes analysis: [TOPIC_1, TOPIC_2]"

# After codebase-archaeology, target the discovered pain points
dueling-idea-wizards --mode=architecture --focus="tech debt clusters identified in archaeology: [MODULE_A, MODULE_B]"
```

### The Deep Preparation Pattern

For high-stakes ideation (roadmap planning, pre-rewrite decisions), run the full preparation sequence:

```
codebase-archaeology        (build mental model)
    |
    v
reality-check-for-project   (ground in reality)
    |
    v
bv --robot-triage            (understand work graph)
    |
    v
dueling-idea-wizards         (adversarial ideation with full context)
```

Each step's output file becomes study material for the duel agents. Copy key findings into the study prompt or place them in the project root where agents will find them during Phase 3.

## Post-Duel Validation

Skills to run AFTER the duel to stress-test the winning ideas before committing to implementation.

### Validation by Duel Mode

| Duel Mode | Validation Skill | What It Catches |
|-----------|-----------------|-----------------|
| `--mode=ideas` (default) | `multi-pass-bug-hunting` on consensus winners | Implementation risks, edge cases the duel missed |
| `--mode=ux` | `ux-audit` on winner proposals | Usability gaps, accessibility issues, Nielsen heuristic violations |
| `--mode=performance` | `extreme-software-optimization` on target code paths | Whether the proposed optimizations actually target the real bottlenecks |
| `--mode=security` | `codebase-audit --domain=security` on affected code | Whether the security ideas address the actual attack surface |
| `--mode=architecture` | `codebase-audit --domain=performance` + code review | Whether proposed refactors introduce regressions |
| `--mode=reliability` | `testing-metamorphic` or `testing-fuzzing` on affected components | Whether reliability improvements actually hold under adversarial input |

### The Validation Handoff

The duel report's "Consensus Winners" section becomes the input spec for validation:

```bash
# 1. Duel produces winners
cat DUELING_WIZARDS_REPORT.md | grep -A 20 "## Consensus Winners"

# 2. For each winner, run the appropriate validation skill
# Example: UX winner about CLI onboarding
/ux-audit --focus="CLI first-run experience as proposed in duel winner #1"

# Example: Performance winner about caching layer
/extreme-software-optimization --focus="caching layer for hot-path queries as proposed in duel winner #3"
```

### Validation Outcomes

| Validation Result | Action |
|-------------------|--------|
| Passes cleanly | Proceed to bead creation (Phase 8) |
| Surfaces minor risks | Add risks to the bead body; proceed with awareness |
| Finds fundamental flaw | Demote from Consensus Winner to Contested; re-evaluate |
| Reveals the idea was already partially implemented | Merge with existing work; update scope |

## The Full Innovation Pipeline

The complete flywheel from "what should we build?" to "ship it."

```
codebase-archaeology          Understand the project deeply
        |
        v
reality-check-for-project     Ground ideation in actual status
        |
        v
dueling-idea-wizards           Adversarial ideation + cross-model scoring
        |
        v
[post-duel validation]         Stress-test winners with domain skills
        |
        v
beads-workflow                 Convert winners to structured beads with deps
        |
        v
vibing-with-ntm                Implementation swarm (agent per bead)
        |
        v
multi-pass-bug-hunting         Systematic bug scan of implemented features
        |
        v
release-preparations           Test suites, version bump, cross-platform builds
```

### How Each Step Feeds the Next

| From | To | What Passes Between |
|------|----|-------------------|
| `codebase-archaeology` | `reality-check` | Mental model of project structure |
| `reality-check` | `dueling-idea-wizards` | Gap analysis used as `--focus` areas |
| `dueling-idea-wizards` | `beads-workflow` | Consensus winners with scores, rationale, and opponent criticism |
| `beads-workflow` | `vibing-with-ntm` | Dependency-ordered beads ready for parallel implementation |
| `vibing-with-ntm` | `multi-pass-bug-hunting` | Implemented features needing audit |
| `multi-pass-bug-hunting` | `release-preparations` | Clean code ready for release |

### Pipeline Timing

| Step | Typical Duration | Can Be Parallelized? |
|------|-----------------|---------------------|
| Archaeology | 15-30 min | No (must run first) |
| Reality check | 10-20 min | No (needs archaeology output) |
| Duel | 30-60 min | No (core step) |
| Validation | 10-30 min per winner | Yes (validate multiple winners in parallel) |
| Beads | 15-30 min | No (sequential bead creation) |
| Implementation swarm | 1-4 hours | Yes (one agent per bead) |
| Bug hunting | 20-40 min | Yes (per module) |
| Release prep | 15-30 min | No (sequential) |

Total wall-clock time for the full pipeline: roughly 3-6 hours for a medium project with 3-5 consensus winners. The duel itself is about 30-60 minutes of that.

## Cross-Project Dueling

Using patterns from one project to generate ideas for another.

### The Pattern Extraction Flow

```
Project A: cross-project-pattern-extraction
        |
        v
Extracted patterns (e.g., "caching strategy", "error recovery pattern", "CLI plugin system")
        |
        v
Project B: dueling-idea-wizards --focus="Apply pattern X from Project A to this project"
```

### Concrete Example

```bash
# In Project A (a Rust CLI tool with excellent error handling)
/cross-project-pattern-extraction --pattern="error recovery and user-facing error messages"

# In Project B (a different Rust CLI tool with poor error handling)
/dueling-idea-wizards --mode=ux --focus="Apply error recovery patterns extracted from [Project A]: structured error types, contextual help text, recovery suggestions"
```

### When Cross-Project Dueling Adds Value

- Two projects in the same language/framework with different maturity levels
- A feature that worked well in Project A and might apply to Project B
- Architectural patterns that are proven in one context and need adversarial evaluation in another
- When you suspect a project is "reinventing the wheel" -- duel the existing wheel vs. the reinvention

## The Recursive Duel

Using `repeatedly-apply-skill` to run the duel multiple times with progressive deepening.

### Setup

```bash
/repeatedly-apply-skill --skill=dueling-idea-wizards --times=3 --strategy=progressive
```

### How Rounds Deepen

| Round | Configuration | Focus |
|-------|--------------|-------|
| 1 | `--mode=ideas` (broad) | Generate the widest possible idea surface |
| 2 | `--focus="contested ideas from Round 1"` | Zoom into areas of disagreement |
| 3 | `--focus="implementation risks for Round 1+2 winners"` | Adversarial stress-test of the strongest ideas |

### What Changes Between Rounds

- Fresh agent sessions (kill and respawn between rounds -- exploits prompt caching for fresh perspective)
- Narrower focus (each round's contested ideas become the next round's focus)
- Higher bar (Round 3 agents know the ideas already survived two rounds of scrutiny)

### Diminishing Returns

Three rounds is usually the sweet spot. By Round 4, agents start rephrasing the same ideas. Signs of diminishing returns:
- Overlap between rounds exceeds 60%
- Score distributions converge (Round 3 looks like Round 2)
- No new contested ideas emerge

## Combining with modes-of-reasoning

The `modes-of-reasoning-project-analysis` skill runs multiple NTM agents in different analytical modes (first-principles, adversarial, integrative, etc.). Its output identifies blind spots, risks, and contested conclusions that are perfect duel fodder.

### The Handoff Pattern

```
modes-of-reasoning-project-analysis
    |
    Produces: MODES_ANALYSIS_REPORT.md with:
    - Areas where modes agreed (high confidence findings)
    - Areas where modes disagreed (contested findings)
    - Blind spots each mode identified
    |
    v
dueling-idea-wizards --focus="[contested findings and blind spots from modes report]"
```

### What Makes This Combination Powerful

Modes-of-reasoning answers "where should we look?" -- it identifies the areas of a project that are problematic, contested, or under-analyzed. The duel answers "what should we build?" -- it generates and adversarially evaluates specific actionable ideas.

Running modes first prevents the duel from wasting time on areas that are already well-understood. Instead, agents focus their ideation energy on the genuinely contested or overlooked dimensions.

### Concrete Integration Steps

1. Run `modes-of-reasoning-project-analysis` and collect the report
2. Extract the contested findings (areas where different reasoning modes disagreed)
3. Extract the identified blind spots
4. Construct a `--focus` argument from these:
   ```bash
   dueling-idea-wizards --focus="Modes analysis found disagreement on: [FINDING_1], [FINDING_2]. Blind spots identified: [BLIND_SPOT_1]. Generate ideas specifically targeting these areas."
   ```
5. In the duel synthesis (Phase 7), cross-reference duel results with modes conclusions -- where the duel and modes analysis converge, confidence is very high

### Anti-Pattern: Running the Duel Without Modes

For large, complex projects, running a broad `--mode=ideas` duel without modes-of-reasoning first often produces ideas that target the obvious problems -- the ones any single model could identify. The modes analysis surfaces the non-obvious problems, and the duel targeting those non-obvious areas is where the real value lives.

## Skill Composition Cheat Sheet

Quick reference for common multi-skill workflows involving the duel.

| Workflow | Skill Chain | When |
|----------|------------|------|
| Feature planning | `reality-check` -> `duel` -> `beads-workflow` | Sprint/roadmap planning |
| Architecture decision | `codebase-archaeology` -> `duel --mode=architecture` -> `codebase-audit` | Before major refactors |
| Security hardening | `codebase-audit --domain=security` -> `duel --mode=security` -> `multi-pass-bug-hunting` | Pre-launch security review |
| UX overhaul | `ux-audit` -> `duel --mode=ux` -> `ux-audit` (post-implementation) | CLI/UI improvement cycles |
| Performance sprint | `extreme-software-optimization` (profile) -> `duel --mode=performance` -> `extreme-software-optimization` (implement) | Latency reduction work |
| Cross-project learning | `cross-project-pattern-extraction` (Project A) -> `duel` (Project B) | Applying proven patterns |
| Deep exploration | `modes-of-reasoning` -> `duel` -> `repeatedly-apply-skill` (recursive duel) | Strategic planning, annual review |
