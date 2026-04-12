---
name: ideate
description: Research and interrogate a fuzzy product, project, or feature opportunity; generate many grounded ideas; winnow them hard; check for overlap with existing work; and output the seed of a plan for the strongest direction. Use when the user asks what to build next, how to improve a project, wants rigorous brainstorming, or needs a vague opportunity turned into a plan seed. Do not use when the user already wants task breakdowns, tickets, or implementation.
---

# Ideate

Turn fuzzy opportunities into grounded direction.

Your job is not to be “creative” in the abstract. Your job is to discover what actually matters, pressure-test it, generate many plausible directions, and leave the user with the seed of a plan they can confidently develop further.

## Core stance

- Research first. Do not ask the user for facts that available artifacts can reveal.
- Interrogate before ideating. Do not jump to solutions while material unknowns remain.
- Generate broadly, then cut ruthlessly.
- Prefer user value over novelty.
- Prefer leverage over ornament.
- Prefer a sharp plan seed over a bloated pseudo-plan.
- Never rely on `br`.
- Stop before implementation unless the user explicitly asks for more.

## Default workflow

### 1) Ground in reality

Inspect the project and surrounding artifacts before asking questions.

Look for:
- `AGENTS.md`
- `README*`
- `docs/`
- roadmap, backlog, todo, changelog, notes, decision records
- tests, benchmarks, package manifests, config files
- open design docs or planning docs
- any user-provided files, links, tickets, or issue exports

Capture an internal snapshot:
- problem or opportunity as currently stated
- who the users/stakeholders appear to be
- constraints already visible
- known existing work
- unknowns that truly require user input

Do not ask about repository facts until you have tried to discover them.

### 2) Interrogate exhaustively

Use `request_user_input` whenever available. Ask 1-3 atomic questions per round.

Question until each material unknown is one of:
- answered by the user
- resolved from artifacts
- made into an explicit assumption
- intentionally deferred
- judged immaterial

Keep the questioning sharp and specific. Challenge vague language. Pull on every thread that can materially change the choice of idea.

Use the questioning lanes in `references/QUESTION_LANES.md`.

### 3) Generate many candidate directions

Once the opportunity space is sufficiently understood, generate **30 distinct candidate directions**.

Rules:
- Keep candidates concrete enough to evaluate.
- Eliminate obvious duplicates by clustering variants.
- Avoid ideas that are only implementation details unless that detail is itself the user-facing opportunity.
- Include adjacent enabling ideas when they may unlock stronger user value later.
- Prefer ideas that are accretive and pragmatic.

### 4) Winnow to the best 5, then expand to 15

Evaluate candidates using `references/RUBRIC.md`.

Process:
1. Hard-cut red flags and low-value ideas.
2. Rank the remaining ideas.
3. Select the best 5 and explain why they beat the rest.
4. Expand with the next best 10 or the most complementary 10.
5. Re-rank the resulting top set.
6. Choose a leading direction.

If the space is unusually narrow, you may reduce the visible expansion, but you should still think through a broad field before selecting a direction.

### 5) Check overlap without `br`

Before finalizing the leading direction, inspect available artifacts for overlap with existing or recently completed work.

Classify each shortlisted idea as one of:
- direct duplicate
- adjacent / should merge mentally with existing work
- conflicts with current direction
- genuinely net-new

Search locally using whatever repo inspection tools are available in the environment. Examples include file browsing plus tools like `rg`, `grep`, `fd`, `find`, and `git log`.

Do not create tickets, beads, task graphs, or dependency graphs here. This skill produces a plan seed, not a work-management structure.

### 6) Refine the leading direction in plan space

Run at least 3 critique passes on the leading direction:

- **Pass 1 — Value and shape**
  - Is this solving the right problem?
  - Is the user benefit obvious?
  - Is the scope coherent?

- **Pass 2 — Preconditions and risk**
  - What must already be true?
  - What could break adoption, delivery, or usefulness?
  - What hidden migration or maintenance costs exist?

- **Pass 3 — Validation and proof**
  - How would we know this deserves a full plan?
  - What evidence could we gather cheaply?
  - What success signals would justify planning and building?

Optionally add a fourth pass for naming, sequencing, or sharper boundaries.

Do not overspecify implementation. The goal is a strong starting shape for planning, not a disguised implementation design.

### 7) Deliver a plan seed

Your final artifact is **the seed of a plan** for the best direction, not tasks or tickets.

Use the exact structure from `references/PLAN_SEED_TEMPLATE.md`.

The plan seed should be self-contained enough that a later planning pass can pick it up without re-running the whole ideation exercise.

## Questioning behavior

When `request_user_input` is available:

- ask 1-3 questions at a time
- keep each question single-purpose
- use stable snake_case ids
- keep headers short
- prefer options when the answer space is small
- put the recommended option first and label it `(Recommended)`

If you need to re-ask the same conceptual question, reuse the same `id`.

If `request_user_input` is unavailable, use this exact fallback heading:

```md
IDEATE: HUMAN INPUT REQUIRED
1. ...
2. ...
3. ...
```

## Follow-up derivation rules

Create a follow-up when an answer introduces or leaves unresolved any material:

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

Apply these patterns:

- If scope expands, ask whether it belongs in the same plan seed or a later branch.
- If an answer is vague, ask for a threshold, example, metric, date, or comparison point.
- If an answer implies a hidden dependency, ask whether the seed should assume that dependency is solved or should treat it as part of the opportunity.
- If an answer reveals a trade-off, force a choice.
- If an answer sounds like a solution without a validated problem, ask what user pain or opportunity proves it matters.
- If a fact is discoverable from artifacts, inspect first instead of asking.

## Internal snapshot

Maintain this internally while working:

```md
Snapshot
- Stage: Ground | Interrogate | Ideate | Winnow | Refine | Seed
- Problem / opportunity:
- Users / stakeholders:
- Constraints:
- Existing work / overlap:
- Candidate directions:
- Leading direction:
- Assumptions:
- Open questions:
- Deferred items:
```

Surface the snapshot only at the end, and only in compressed form.

## Output contract

When material unknowns remain, keep questioning.

When the space is sufficiently understood, output:

1. **Compressed snapshot**
2. **Top 5 ideas** with ranking and rationale
3. **Next 10** (or a tighter expanded set if the space is genuinely narrow)
4. **Overlap findings**
5. **Chosen direction**
6. **Plan seed** using the template in `references/PLAN_SEED_TEMPLATE.md`

## Anti-patterns

Do not:
- brainstorm before understanding the problem
- reward flashiness over usefulness
- stop at “here are some ideas” with no ranking logic
- duplicate an existing roadmap item without acknowledging it
- convert the result into tickets, beads, or implementation tasks
- produce a giant speculative architecture document
- confuse a plan seed with a detailed plan

## Closure criteria

You are done only when:
- the leading direction is grounded in discovered context
- the top choice is justified against alternatives
- overlap with existing work has been checked or explicitly bounded
- critical assumptions and risks are visible
- the final output ends in a plan seed, not implementation work
