---
name: ideate
description: "Mine a codebase for breakthrough, evidence-backed changes, additions, refactors, simplifications, DX, UX, reliability, performance, or architecture cleanup. Always run Glaze and ASI escalation gates before choosing. Output ranked opportunities, escalation ledger, and plan seed; do not implement or create tickets."
---

# Ideate

Turn a repository, product surface, or fuzzy improvement area into a ranked portfolio of original, evidence-backed opportunities and one sharp plan seed.

This skill must not stop at plausible improvement ideas. It must first mine project reality, then force two escalation gates:

1. **Glaze gate** — reject the merely adequate answer and require a material new frame, invariant, mechanism, architecture, or artifact.
2. **ASI gate** — expand the ambition horizon 10x, then collapse that larger frame back into the smallest proof-bearing artifact that can be built, tested, or used next.

The result should feel surprising only because the repository evidence makes it feel obvious in hindsight.

## Core stance

- Research first. Do not ask the user for facts that available artifacts can reveal.
- Default scope is the current repository or the files the user provided.
- Treat code, tests, docs, examples, issue exports, and git history as opportunity evidence.
- Prefer evidence-backed originality over generic cleanup.
- Prefer leverage over ornament.
- Prefer user and maintainer value over novelty.
- Prefer behavior-preserving refactors when refactoring is the opportunity.
- Do not choose a leading direction until it has survived both the Glaze gate and the ASI gate.
- A breakthrough idea must cash out as at least one concrete mechanism, interface, proof surface, or strategy.
- Never rely on `br`.
- Do not create tickets, beads, task graphs, dependency graphs, or implementation plans.
- Stop before implementation unless the user explicitly asks for a separate follow-up.

## Mandatory escalation gates

Use `references/ESCALATION_GATES.md` as governing guidance for the Glaze and ASI passes.

The gates are not optional polish. They are required search operators:

- **Glaze** is applied after the first winnow. It asks why the current portfolio underperforms and forces a materially stronger move.
- **ASI** is applied after Glaze. It expands ambition 10x, identifies the systemic leverage point, and compresses it to a small artifact that preserves the larger insight.

When the exact original escalation text needs to be restated, preserve it verbatim from `references/ESCALATION_GATES.md`. Treat the ASI text as an ambition-expansion cue, not as a claim about actual model status.

A candidate fails escalation if:

- Glaze adds only intensity, adjectives, or generic ambition rather than a material delta.
- ASI cannot identify a concrete mechanism, interface, proof surface, or strategy.
- The 10x framing cannot be collapsed into a credible small artifact.
- The escalated idea loses contact with repository evidence.

If no candidate passes both gates, say so explicitly, then present the strongest grounded portfolio as non-breakthrough rather than manufacturing novelty.

## Default workflow

### 1) Establish scope and posture

Infer the scope from the prompt. If the user points at a repo, directory, issue export, design doc, or source subset, use that as the scope. If scope is unclear, default to the current repository and state the assumption later.

The default final artifact is:

1. a compressed repo snapshot
2. an opportunity map
3. escalation ledger
4. top 5 breakthrough ideas
5. next 10 ideas
6. cut ideas
7. overlap findings
8. chosen direction
9. one plan seed

### 2) Ground in reality

Inspect available artifacts before asking questions.

Look for:

- `AGENTS.md`
- `README*`
- `docs/`, design notes, ADRs, architecture notes
- roadmap, backlog, TODOs, changelog, release notes
- tests, benchmarks, fixtures, examples
- package manifests, build scripts, config files, CI workflows
- public API surfaces, CLI commands, routes, UI entry points
- user-provided links, tickets, issue exports, recordings, or notes
- git history when available and relevant

Optionally run `scripts/ideate-scan.sh` from this skill if shell access is available. Treat its output as a raw signal index, not as conclusions.

Capture an internal snapshot:

```md
Snapshot
- Stage: Scope | Ground | Harvest | Interrogate | Baseline Ideate | Winnow | Glaze | ASI | Overlap | Refine | Portfolio
- Scope:
- Repo shape:
- Primary user-facing surfaces:
- Primary maintainer surfaces:
- Constraints:
- Evidence sources inspected:
- Opportunity signals:
- Existing work / overlap:
- Baseline candidate directions:
- Glaze material deltas:
- ASI 10x frames:
- Leading direction:
- Assumptions:
- Open questions:
- Deferred items:
```

Surface the snapshot only in compressed form in the final output.

### 3) Harvest codebase opportunity signals

Before ideating, perform a read-only signal harvest. The goal is not to audit every file; the goal is to find specific repo evidence that can seed original ideas.

Use `references/CODEBASE_SIGNAL_LANES.md`.

Look especially for:

- **User surface signals**: CLI commands, routes, public APIs, UI flows, examples, docs promises, error messages, onboarding paths.
- **Friction signals**: TODO/FIXME/HACK comments, repeated workarounds, confusing names, defensive code, noisy logs, manual steps in docs.
- **Architecture seam signals**: duplicated logic, unstable boundaries, circular dependencies, large modules, repeated adapters, leaky abstractions.
- **Test intent signals**: tests that reveal intended behavior, missing tests around critical paths, overcomplicated fixtures, repeated setup.
- **Reliability signals**: retry logic, partial failure paths, validation gaps, cleanup paths, state recovery, idempotency assumptions.
- **Performance signals**: hot loops, repeated I/O, unnecessary serialization, expensive startup, N+1-shaped access, slow test/build commands.
- **Developer workflow signals**: package scripts, CI config, local setup pain, flaky tests, poor diagnostics, missing one-shot commands.
- **History signals**: recent churn, repeated fixes, reverted work, abandoned branches, renamed concepts, closed TODOs.
- **Negative-space signals**: names, docs, types, tests, or examples that imply a capability the project does not yet expose.
- **Refactor-enabler signals**: places where behavior-preserving simplification would unlock future feature work.

Capture a compact opportunity map with evidence. Prefer exact `path:line` references when available. If line numbers are not practical, cite the smallest file, symbol, route, command, or test scope.

### 4) Ask only material questions

Use structured interactive input when available; otherwise ask in normal chat. Ask 1-3 atomic questions per round only after inspecting artifacts.

Ask only for decisions that materially change the opportunity portfolio, such as:

- target user or maintainer priority
- appetite for behavior change vs behavior-preserving refactor
- near-term product direction not visible in artifacts
- constraints that cannot be inferred from docs or code
- whether speculative ideas are allowed when evidence is thin

Question until each material unknown is one of:

- answered by the user
- resolved from artifacts
- made into an explicit assumption
- intentionally deferred
- judged immaterial

Use `references/QUESTION_LANES.md` for follow-up prompts. If artifact evidence is enough to proceed, proceed without asking.

### 5) Generate 30 baseline evidence-backed candidate directions

Generate 30 distinct baseline candidates before selecting winners. Each candidate must be concrete enough to evaluate and must include evidence.

Default portfolio quotas:

- 6 user-facing additions or feature ideas
- 5 DX / CLI / API / workflow improvements
- 5 refactor or simplification opportunities
- 4 reliability / correctness / recovery ideas
- 3 observability / diagnostics ideas
- 3 performance / scalability ideas
- 2 documentation / onboarding ideas that are not merely "write more docs"
- 2 wild-card ideas from negative-space or hidden-primitive lenses

If the repo type makes a quota irrelevant, reallocate it and state why in the final assumptions or snapshot.

Use this candidate card internally:

```md
Candidate Card
- Title:
- Category: Feature | Addition | Refactor | Simplification | DX | UX | Reliability | Performance | Observability | Docs | Infrastructure
- Evidence:
- Originality source:
- User / maintainer benefit:
- Why this is not generic:
- Likely implementation shape, briefly:
- Validation path:
- Risks / behavior-change concerns:
- Overlap status:
```

### 6) Apply originality lenses

An original codebase idea should be surprising but evidence-backed. It should usually come from one or more of these lenses:

- **Hidden primitive**: the code already has low-level capability that could become a user-facing feature.
- **Repeated workaround**: several places compensate for the same missing abstraction or affordance.
- **Negative space**: docs, names, tests, or examples imply something that does not exist yet.
- **Sharp edge**: users or maintainers can fall into an avoidable trap.
- **Asymmetric leverage**: a small change makes many future changes easier.
- **Behavior-preserving unlock**: a refactor does not matter by itself, but unlocks safer future work.
- **Diagnostic inversion**: internal state exists but is not exposed in a way that helps users debug.
- **Default-basin escape**: the obvious idea is "add more docs/tests"; propose a more structural improvement when evidence supports it.

Every shortlisted idea must name its originality source and explain why it is not merely generic cleanup.

### 7) First winnow: 30 → 5 → 15

Evaluate baseline candidates using `references/RUBRIC.md`.

Process:

1. Hard-cut ideas with fatal flaws, weak evidence, obvious duplication, or poor fit.
2. Score the remaining ideas.
3. Select the best 5 and explain why they beat the rest.
4. Add the next best 10 or the most complementary 10.
5. Re-rank the resulting top set.
6. Choose a preliminary leading direction.

This preliminary direction is not final. It is the input to Glaze and ASI.

### 8) Mandatory Glaze gate: force a material delta

Run one explicit Glaze escalation pass over the preliminary top 5 and the preliminary leading direction.

For each of the top 5, ask:

- Why is the obvious version merely adequate?
- What new frame, invariant, mechanism, architecture, or artifact was absent from the baseline version?
- What stronger move now dominates the obvious alternative?
- What should be cut because it cannot produce a material delta?

A valid Glaze pass must produce at least one of:

- a new frame that changes how the opportunity is understood
- an invariant that makes future work safer or more powerful
- a concrete mechanism that changes system behavior
- an interface or protocol that changes how users, maintainers, or components coordinate
- an artifact that makes the idea testable, reusable, or adoptable
- an architecture move that opens a higher-leverage path

Intensified wording does not count. If the pass cannot materially improve an idea, cut or demote the idea.

### 9) Mandatory ASI gate: 10x expansion, smallest proof-bearing artifact

Run an ASI ambition-compression pass over the strongest Glaze-surviving ideas, usually the top 3.

For each, produce:

- why the current answer still underperforms
- the 10x ambition horizon
- the civilizational, systemic, institutional, ecosystem, or project-wide frame exposed by that expansion
- the leverage point: mechanism, interface, proof surface, or strategy
- the smallest artifact that preserves the 10x insight
- why the artifact carries the larger frame without relying on grandiosity
- the first proof signal

A valid ASI pass must cash out as at least one of:

- a concrete mechanism that changes how the system behaves
- an interface or protocol that changes how actors or components coordinate
- a proof surface that makes progress measurable or falsifiable
- a strategy that changes the order, incentives, or leverage of action

Do not output hype. Do not claim actual ASI capability. The pass is an ambition-expansion and compression tool.

### 10) Breakthrough synthesis and second winnow

Re-score the escalated candidates with `references/RUBRIC.md`, including the breakthrough criteria.

For each surviving top idea, preserve a compact escalation chain:

```md
Escalation Chain
- Baseline idea:
- Why the obvious version loses:
- Glaze material delta:
- ASI 10x frame:
- Smallest proof-bearing artifact:
- Cash-out type: Mechanism | Interface | Proof surface | Strategy
- First proof signal:
- Evidence anchor:
```

The final leading direction must beat alternatives on both ordinary codebase value and escalation quality. Prefer the idea that creates a new capability surface, coordination protocol, proof surface, or strategic ordering while remaining grounded and testable.

### 11) Check overlap without `br`

Before finalizing, inspect available artifacts for overlap with existing or recently completed work. Do this after escalation because the escalated version may overlap differently from the baseline idea.

Search for:

- matching roadmap items
- TODOs and backlog notes
- closed or open issue exports, if provided
- past attempts or reverted work
- recently completed adjacent changes
- naming collisions and scope collisions
- existing features hidden behind flags, scripts, or undocumented APIs

Classify each shortlisted idea as one of:

- direct duplicate
- adjacent / should merge mentally with existing work
- conflicts with current direction
- genuinely net-new
- unknown due to thin evidence

Search locally using available tools such as file browsing, `rg`, `grep`, `fd`, `find`, and `git log`. Do not use `br`.

### 12) Refine the leading direction in plan space

Run at least 5 critique passes on the leading direction:

- **Pass 1 — Value and shape**
  - Is this solving the right problem?
  - Is the user or maintainer benefit obvious?
  - Is the scope coherent?
- **Pass 2 — Architecture and behavior risk**
  - Does this fit the current architecture?
  - What behavior must remain stable?
  - What hidden migration or maintenance costs exist?
- **Pass 3 — Evidence and originality**
  - Which repo signals support the idea?
  - What makes it non-obvious but grounded?
  - What would disconfirm it?
- **Pass 4 — Glaze material delta**
  - What new frame, invariant, mechanism, architecture, or artifact exists after escalation?
  - Why does that dominate the merely adequate version?
  - What got cut because it was not strong enough?
- **Pass 5 — ASI cash-out and proof**
  - What is the 10x horizon?
  - What smallest artifact preserves the 10x insight?
  - What first proof signal would justify full planning?

Optionally add a sixth pass for naming, sequencing, or sharper boundaries.

Do not overspecify implementation. The goal is a strong starting shape for planning, not a disguised implementation design.

### 13) Deliver opportunity portfolio, escalation ledger, and plan seed

Use the structure in `references/OPPORTUNITY_PORTFOLIO_TEMPLATE.md`.

End with a plan seed using `references/PLAN_SEED_TEMPLATE.md`.

The final artifact should be self-contained enough that a later planning pass can pick it up without re-running the ideation exercise.

## Questioning behavior

When structured input is available:

- ask 1-3 questions at a time
- keep each question single-purpose
- use stable snake_case ids when ids are supported
- keep headers short
- prefer options when the answer space is small
- put the recommended option first and label it `(Recommended)`

If you need to re-ask the same conceptual question, reuse the same id when possible.

If structured input is unavailable and questioning is truly necessary, use this fallback heading:

```md
IDEATE: HUMAN INPUT REQUIRED
1. ...
2. ...
3. ...
```

## Follow-up derivation rules

Create a follow-up question when an answer introduces or leaves unresolved any material:

- ambiguity
- assumption
- dependency
- success criterion
- stakeholder tension
- non-goal
- rollout concern
- maintenance burden
- evidence gap
- overlap concern
- behavior-change risk
- escalation quality gap
- missing proof signal

Apply these patterns:

- If scope expands, ask whether it belongs in the same plan seed or a later branch.
- If an answer is vague, ask for a threshold, example, metric, date, or comparison point.
- If an answer implies a hidden dependency, ask whether the seed should assume that dependency is solved or should treat it as part of the opportunity.
- If an answer reveals a trade-off, force a choice.
- If an answer sounds like a solution without a validated problem, ask what user pain or maintainer friction proves it matters.
- If an escalated idea sounds grand but lacks a proof-bearing artifact, ask what concrete mechanism, interface, proof surface, or strategy makes it real.
- If a fact is discoverable from artifacts, inspect first instead of asking.

## Output contract

When material unknowns remain and cannot be reasonably assumed, ask. Otherwise proceed with explicit assumptions.

When the space is sufficiently understood, output:

1. **Compressed repo snapshot**
2. **Opportunity map** grouped by signal theme
3. **Escalation ledger** showing the Glaze and ASI transformations
4. **Top 5 breakthrough ideas** with ranking, evidence, originality source, material delta, 10x frame, proof-bearing artifact, validation path, and overlap status
5. **Next 10 ideas** in shorter evidence-backed form
6. **Ideas cut** and why they lost, including escalation failures
7. **Overlap findings**
8. **Chosen direction**
9. **Plan seed** using `references/PLAN_SEED_TEMPLATE.md`

## Anti-patterns

Do not:

- brainstorm before inspecting relevant artifacts
- ask the user for facts the repo can answer
- reward flashiness over usefulness
- confuse ambition with scope bloat
- let Glaze become merely stronger rhetoric
- let ASI become grandiosity without a concrete cash-out
- stop at "here are some ideas" with no ranking logic
- propose generic "add tests" or "improve docs" ideas without a sharper underlying opportunity
- duplicate an existing roadmap item without acknowledging it
- treat a refactor as valuable unless it reduces risk, unlocks future work, or preserves behavior while simplifying the system
- convert the result into tickets, beads, or implementation tasks
- produce a giant speculative architecture document
- confuse a plan seed with a detailed plan

## Closure criteria

You are done only when:

- the leading direction is grounded in discovered context
- the top choice is justified against alternatives
- each shortlisted idea has evidence and an originality source
- each top idea has a Glaze material delta or is explicitly demoted
- the chosen direction has an ASI 10x frame, smallest proof-bearing artifact, cash-out type, and first proof signal
- overlap with existing work has been checked or explicitly bounded
- critical assumptions and risks are visible
- the final output ends in a plan seed, not implementation work
