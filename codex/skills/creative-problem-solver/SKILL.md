---
name: creative-problem-solver
description: "Generate a compact five-tier strategy portfolio when the next task is choosing among materially different paths. Implicitly invoke for explicit requests for options, alternatives, trade-offs, reframing, or help escaping repeated failure. A skill-name mention is not invocation. Do not activate for direct implementation, single-answer advice, skill analysis/tuning, repository-evidence opportunity mining ($ideate), or detailed planning ($plan)."
---

# Creative Problem Solver

Purpose: when a strategy choice is still open, generate a five-tier portfolio that escapes the default solution basin, compounds through an Artifact Spine, and stops for a human choice.

## Activation boundary

Implicit invocation is enabled. The activation signal is an **unresolved strategy choice plus a request for divergent options**. Difficulty, uncertainty, or creativity language alone is not enough.

### Activate when

- The user asks for options, alternatives, trade-offs, fresh angles, reframing, a strategy portfolio, or "what else could we try?"
- Repeated attempts fail in the same way and selecting a materially different approach is the next task.
- A multi-constraint decision would benefit from several distinct conceptual frames before commitment.
- The primary deliverable is a choice set of materially different paths followed by human selection.
- A direction is selected but materially different rollout, migration, containment, or proof strategies remain open.

### Do not activate; route elsewhere

- Direct implementation, debugging, review, or execution after an approach is selected: use the owning workflow.
- Mixed requests where options are subordinate to "choose and implement now": the execution owner may use this reasoning internally, but this skill must not seize the turn and discard the requested execution.
- A factual answer, ordinary creative generation such as names or copy, or comparison of a small known set where a portfolio adds ceremony: answer directly.
- Evidence-backed repository or product opportunity mining, ranked improvement discovery, or choosing what to plan next: use `$ideate`.
- Turning a selected direction into a detailed implementation plan, specification, or work graph: use `$plan` or `$spec-pipeline`.
- Architecture or codebase understanding without a request for divergent paths: use direct analysis or `$codebase-archaeology`.
- Analysis, explanation, review, tuning, testing, or editing of this skill itself: use direct analysis, `$tune`, or `$refine` as appropriate.
- The user already chose a tier or path and asks to execute it: hand off to the execution owner; do not regenerate the portfolio.

### Skill-name rule

- Imperative requests such as "use", "run", or "apply `$creative-problem-solver`" count as explicit invocation.
- Merely mentioning, quoting, explaining, reviewing, tuning, or editing `$creative-problem-solver` does not invoke it.

### Tie-breakers

- Explicit imperative invocation wins unless safety, a domain-specific owner, or a contradictory execution request requires another route.
- `$ideate` wins when repository evidence mining and ranked opportunities are central.
- `$plan` wins when the direction is selected and the requested output is an execution policy or detailed plan.
- `$tune` / `$refine` win when the object of work is the skill package itself.
- Activate when the requested outcome is a choice set; do not activate when the outcome is one answer, one plan, or one implementation.

## Contract

- Name the lane and Double Diamond stage.
- State the problem, success criteria, and evidence posture: known facts versus assumptions or hypotheses.
- Reframe once, then run an Aha Check: name the restructuring insight and its evidence status. Never promote an unsupported mechanism, bottleneck, or causal story to fact.
- Name the default solution basin and ensure at least two tiers use genuinely different conceptual frames.
- Include all five tiers: Quick Win, Strategic Play, Advantage Play, Transformative Move, Moonshot.
- For every tier: accretive artifact, falsifiable expected signal with a timebox, and escape hatch.
- Give conditional selection guidance, then stop for human input before execution.
- Keep the visible process proportional: Fast Spark targets <=45 lines; Full Session targets <=70 lines.

## Workflow

1. Choose stage: Discover / Define / Develop / Deliver.
2. Choose lane: Fast Spark or Full Session.
3. Define gate: one-line problem statement + success criteria; mark material unknowns.
4. Evidence posture: separate facts from assumptions and hypotheses.
5. Reframe using the stage default or the user's requested technique.
6. Aha Check. State the restructuring insight, representational shift, and evidence status. If no material Aha appears, run one second and final pass with a different operator.
7. Diversity gate: name the default basin and at least two distinct frames.
8. Define an Artifact Spine of 1-3 durable assets that higher tiers can reuse.
9. Generate the five-tier portfolio.
10. Give selection guidance and ask the user to choose a tier or update constraints.

## Double Diamond alignment

- Discover: relevant facts, actors, or problem topology are unclear; tiers are learning and observation moves.
- Define: the decision definition, success criteria, or constraints are unclear; tiers test competing definitions.
- Develop: the problem is sufficiently defined and materially different solution paths remain open.
- Deliver: the core direction is selected, but rollout, migration, containment, or proof strategies remain open. Do not use Deliver to regenerate competing core solutions.

## Mode check

- Pragmatic (default): every tier is a bounded, reversible next move that can produce evidence this week.
- Visionary: use only when the user asks for long-horizon strategy or systemic change.
- Tiers describe the ambition of the hypothesis, not the size of the first commitment. A Moonshot is the smallest proof-bearing probe of discontinuous upside, not an unbounded rewrite.

## Lane selector

- Fast Spark: skip broad candidate generation and surface only the minimum decision-useful structure.
- Full Session: generate 10-30 candidates, cluster by frame, winnow, and surface the assumptions and trade-offs that changed the selection.

## Reframe selection

- Discover default -> Assumption Mapping.
- Define default -> How Might We.
- Develop default -> SCAMPER for an existing system; First Principles for greenfield work.
- Deliver default -> Pre-mortem.
- Second pass -> choose a materially different operator, usually First Principles, Inversion, or Analogy.
- Honor a user-requested technique when it is usable; do not silently replace it with a "nearest supported" technique.
- Chat disclosure: `Reframe used: <technique>` plus one line explaining why.

## Aha Check

- **Aha is the restructuring insight**: the moment the problem is re-represented so a different candidate field becomes visible.
- Make the representational change explicit: from the baseline frame to the alternative frame.
- Output one compact line: `Aha: <restructuring insight> [evidence: fact | supported inference | hypothesis]`.
- An Aha is material only if it changes the candidate field, proof surface, ordering, or decision criteria.
- An Aha may be a hypothesis. Creative force does not upgrade its factual status.
- If the mechanism is unverified, label it as a hypothesis and make validation part of the expected signal.
- If no material Aha appears after the second pass, state `Aha: N/A after second pass`, continue with the strongest grounded portfolio available, and mark same-basin honestly. Do not manufacture an Aha or diversity.

## Diversity guard

- Name the default solution basin before generating tiers.
- Ensure at least two tiers shift frame, not merely cost or scope.
- Useful frame shifts include substrate, interface, constraint, proof surface, incentive, time horizon, operating model, user ritual, or authority boundary.
- Put the frame in each option heading, for example `Quick Win — Instrument first [proof surface]`.
- If the five tiers cannot honestly diverge, say so and mark the portfolio as same-basin.

## Accretion

- An accretive artifact is a durable asset retained even when an option is wrong: measurement, harness, spec, test, automation, interface, dataset, or decision record.
- Define 1-3 Artifact Spine assets shared across tiers. Each tier's artifact must belong to the spine or explicitly justify a different spine.
- Fast Spark: give each spine asset's purpose and home; put the timebox in the option signal.
- Full Session: also give the minimal interface and explain how the ladder compounds.
- Expected signals must be falsifiable and timeboxed. Do not promise an outcome that the current evidence cannot support.

## Tier semantics

- Quick Win: cheapest reversible move that improves the decision or outcome now.
- Strategic Play: strongest path within the current operating model.
- Advantage Play: creates a reusable capability, compounding asset, or asymmetric option.
- Transformative Move: changes an interface, operating model, governing constraint, or user ritual.
- Moonshot: tests discontinuous upside through the smallest bounded proof-bearing probe.

## Option template

```text
Quick Win — <move> [frame: <frame>]
- Accretive artifact (spine):
- Expected signal + timebox:
- Escape hatch:

Strategic Play — <move> [frame: <frame>]
- Accretive artifact (spine):
- Expected signal + timebox:
- Escape hatch:

Advantage Play — <move> [frame: <frame>]
- Accretive artifact (spine):
- Expected signal + timebox:
- Escape hatch:

Transformative Move — <move> [frame: <frame>]
- Accretive artifact (spine):
- Expected signal + timebox:
- Escape hatch:

Moonshot — <move> [frame: <frame>]
- Accretive artifact (spine):
- Expected signal + timebox:
- Escape hatch:
```

## Selection guidance

- Fast Spark: name the best learning bet, best near-term outcome bet, and boldest bounded probe; give a conditional recommendation.
- Full Session: optionally score Impact, Information, Accretion, Confidence, Reversibility, and Time-to-signal from 1-5. Do not rank by a summed total; identify Pareto leaders and explain the trade-off.
- A recommendation is not execution authorization.

## Deliverable format

### Fast Spark

- Lane + stage.
- Problem + success criteria + evidence posture.
- Reframe used + Aha Check + default basin.
- Compact Artifact Spine.
- Five-tier portfolio.
- Selection guidance + `Human Input Required`.

### Full Session

- Everything in Fast Spark.
- Candidate-field summary and the frames that survived winnowing.
- Optional scorecard with brief rationale.
- Compact facts / risks / assets and assumptions / constraints.
- Detailed Artifact Spine ladder.

After human selection:

- If the direction needs an execution policy or detailed plan, hand off to `$plan`.
- If it is directly implementable and execution is authorized, hand off to the owning implementation workflow.
- This skill never owns repository mutation.

## Fast Spark example

```text
Lane: Fast Spark
Stage: Develop

Problem: Search API p95 latency is ~800ms; target <=200ms at current infra cost.
Success: p95<=200ms, p99<=400ms, CPU +<=10%, no relevancy regression.
Evidence: latency and targets are known; the bottleneck is unknown.

Reframe used: SCAMPER
Why: mutate the existing request path before assuming a replacement is necessary.
Aha: latency is a budget-allocation problem across the whole request path, not necessarily a query-engine problem. [evidence: hypothesis]
Why it matters: query, serialization, payload, cache, and transport become competing hypotheses; tracing decides which budget dominates.
Default basin: tune the query engine directly.
Frames: proof surface, constraint budget, operating model, interface, substrate.

Artifact Spine:
- bench/search/: fixed dataset + p50/p95/p99 + relevancy diff; home: repo benchmark suite.
- perf/tracing/: query/serialization/transport breakdown; home: repo performance tooling.

Quick Win — Instrument the latency budget [frame: proof surface]
- Accretive artifact (spine): baseline run + three worst traces in perf/tracing/.
- Expected signal + timebox: stable budget breakdown and top contributors within 1 day.
- Escape hatch: disable high-overhead tracing; retain the harness and sampled traces.

Strategic Play — Attack the measured largest budget [frame: constraint]
- Accretive artifact (spine): harness-backed optimization in the measured dominant stage.
- Expected signal + timebox: >=30% p95 improvement on the harness within 2 days, with no relevancy regression.
- Escape hatch: feature flag or revert; retain the benchmark and diagnosis.

Advantage Play — Make latency a continuous contract [frame: operating model]
- Accretive artifact (spine): performance budget check and trend history in bench/search/.
- Expected signal + timebox: a seeded regression is caught before merge within 2 days.
- Escape hatch: begin as an advisory check; keep the trend data if gating is noisy.

Transformative Move — Change the response contract [frame: interface]
- Accretive artifact (spine): opt-in streaming or pagination contract measured by the harness.
- Expected signal + timebox: first useful bytes arrive <=200ms on large-result fixtures within 3 days.
- Escape hatch: retain the current response as default and keep the prototype opt-in.

Moonshot — Run an architecture bakeoff [frame: substrate]
- Accretive artifact (spine): reusable evaluation kit comparing engines and transport shapes.
- Expected signal + timebox: one candidate shows >=3x tail improvement on fixed fixtures within 1 week.
- Escape hatch: stop before migration; keep the kit as durable decision evidence.

Selection guidance: Quick Win is the best learning bet; Strategic is the best near-term outcome bet once traces identify the budget; Moonshot is the boldest bounded probe.
Conditional recommendation: start with Quick Win, then choose Strategic or Transformative from measured evidence.
Human Input Required: choose a tier or update the constraints.
```

## Routing examples

### Should activate

- "Give me several materially different ways to reduce onboarding drop-off before we choose one."
- "We have tried tuning the query twice and are still stuck. What else could we try?"
- "Reframe this migration problem and show the trade-offs among distinct paths."
- "The problem is ambiguous; give me learning moves rather than a build plan."
- "We selected event sourcing; show materially different rollout and containment strategies before execution."

### Should not activate

- "Do a deep analysis of my `$creative-problem-solver` skill." -> direct analysis / `$tune`
- "Patch `$creative-problem-solver` so it stops over-triggering." -> `$tune` / `$refine`
- "I am blocked by this compiler error. What else can I try?" -> debugging owner
- "Brainstorm twenty names for this command." -> direct creative generation
- "Give me options, choose the best, and implement it now." -> execution owner; portfolio may be internal
- "Mine this repository for evidence-backed product and DX opportunities." -> `$ideate`
- "Turn the chosen event-sourcing direction into a detailed implementation plan." -> `$plan`
- "Explain this repository's architecture and data flow." -> direct analysis / `$codebase-archaeology`
- "Review this pull request for defects." -> review owner
- "We chose the Quick Win. Build it now." -> execution owner