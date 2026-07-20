---
name: creative-problem-solver
description: "Generate a compact five-tier strategy portfolio when the next task is choosing among materially different paths. Implicitly invoke for explicit requests for options, alternatives, trade-offs, reframing, or help escaping repeated failure. A name-only or meta mention does not authorize the portfolio route. Do not activate for direct implementation, single-answer advice, skill analysis/tuning, repository-evidence opportunity mining ($ideate), or detailed planning ($plan)."
---

# Creative Problem Solver

Purpose: when a strategy choice is still open, generate a five-tier portfolio that escapes the default solution basin, compounds through an Artifact Spine, and stops for a human choice.

## Activation boundary

Implicit invocation is enabled. Host loading is not portfolio authorization. The portfolio route requires an **unresolved strategy choice plus a request for divergent options**. Difficulty, uncertainty, creativity language, or a name-only or meta mention is not enough.

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

- Imperative requests to "use", "run", or "apply `$creative-problem-solver`" **to generate a strategy portfolio** explicitly authorize the portfolio route.
- A name-only or meta mention may load the package under host policy, but it routes to the task owner—or to direct clarification when no task exists—and does not authorize portfolio generation.

### Tie-breakers

- Explicit imperative portfolio invocation wins unless safety, a domain-specific owner, a meta-task owner, or a contradictory execution request requires another route.
- `$ideate` wins when repository evidence mining and ranked opportunities are central.
- `$plan` wins when the direction is selected and the requested output is an execution policy or detailed plan.
- `$tune` / `$refine` win when the object of work is the skill package itself.
- Activate when the requested outcome is a choice set; do not activate when the outcome is one answer, one plan, or one implementation.

## Contract

- Name the lane and Double Diamond stage.
- State the problem, success criteria, and evidence posture: known facts versus assumptions or hypotheses.
- Reframe once, then run an Aha Check: state the restructuring insight separately from its evidence basis and any empirical claim. Never promote an unsupported mechanism, bottleneck, or causal story to fact.
- Name the default solution basin and use at least two genuinely different conceptual frames when honest; otherwise mark the portfolio same-basin rather than manufacturing diversity.
- Include all five tiers: Quick Win, Strategic Play, Advantage Play, Transformative Move, Moonshot.
- For every tier: accretive artifact, falsifiable expected signal with a timebox, and escape hatch.
- Give conditional selection guidance, then stop for human input before execution.
- Keep the visible process proportional: Fast Spark must fit <=45 non-empty output lines; Full Session must fit <=70 non-empty output lines. Count before replying and compress optional detail rather than exceed the lane budget.

## Workflow

1. Choose stage: Discover / Define / Develop / Deliver.
2. Choose lane: Fast Spark or Full Session.
3. Define gate: one-line problem statement + success criteria; mark material unknowns.
4. Evidence posture: separate facts from assumptions and hypotheses.
5. Reframe using the stage default or the user's requested technique.
6. Aha Check. State the restructuring insight, then classify its basis and any empirical claim. If no material Aha appears, run one second and final pass with a different operator.
7. Diversity gate: name the default basin and at least two distinct frames, or explicitly mark same-basin when honest divergence is unavailable.
8. Define an Artifact Spine of 1-3 durable assets that higher tiers can reuse.
9. Generate the five-tier portfolio, then silently verify exact spine-name reuse, mutually exclusive and exhaustive outcomes, retained proof, evidence labels, literal entailment of every fact, and the lane line count; repair every miss before replying.
10. Give selection guidance and ask the user to choose a tier or update constraints.

Definition Gate fields are: domain; symptom, actors, and problem topology; desired outcome and success criteria; metric, threshold, and measurement basis; representative workload population and selection rule; constraints and guardrails. If any field in the first two groups is missing, use Discover; if every field there is recorded or inapplicable but any later field is missing, use Define. In either case, add `Interpretation (assumption): ...` and do not silently choose a domain or metric. When target success is unknown, output `Target success: unknown` separately from `Portfolio success: <decision progress>`; never substitute process success for the target outcome. While any Definition Gate field is missing, all five tiers must reduce uncertainty without proposing solution prototypes: do not choose an index, cache, interface, engine, substrate, or other implementation candidate. The Quick Win signal passes only when every Definition Gate field is explicitly recorded or marked inapplicable; make every later tier conditional on that gate. The Quick Win signal and every later prerequisite clause must spell out all six field groups rather than refer to "the gate," "each field," or a nearby artifact. Preserve tier semantics even here: a Transformative probe must test a changed interface, operating model, governing constraint, or user ritual rather than merely inventorying the current one. The Moonshot may test discontinuous learning or proof leverage, but its signal still needs a predeclared discontinuous threshold rather than mere completeness.

## Double Diamond alignment

- Discover: relevant facts, actors, or problem topology are unclear; tiers are learning and observation moves.
- Define: the decision definition, success criteria, or constraints are unclear; tiers test competing definitions.
- Develop: the problem is sufficiently defined and materially different solution paths remain open.
- Deliver: the core direction is selected, but rollout, migration, containment, or proof strategies remain open. Do not use Deliver to regenerate competing core solutions.

## Mode check

- Pragmatic (default): every tier is a bounded, reversible next move that can produce evidence this week.
- Visionary: use only when the user asks for long-horizon strategy or systemic change.
- Tiers describe the ambition of the hypothesis, not the size of the first commitment. A Moonshot is the smallest proof-bearing probe of discontinuous upside, not an unbounded rewrite.
- In Pragmatic mode, every tier's expected-signal timebox covers a first probe of at most one week. A longer rollout horizon may be context, but cannot replace this first signal.
- Put every escape hatch before an irreversible boundary. Quarantine or containment after authority or data has crossed that boundary is not reversibility.

## Lane selector

- Fast Spark: default when context is sufficient and the user wants decision-useful options without exhaustive candidate work; skip broad generation and surface only the minimum decision-useful structure.
- Full Session: use when the user explicitly asks for deep or exhaustive exploration, or when high stakes, irreversibility, or coupled constraints make candidate generation and winnowing decision-relevant; generate 10-30 candidates, cluster by frame, and surface what changed the selection.
- If lane choice is unclear, choose Fast Spark. Difficulty alone does not justify Full Session.

## Reframe selection

- Discover default -> Assumption Mapping.
- Define default -> How Might We.
- Develop default -> SCAMPER for an existing system; First Principles for greenfield work.
- Deliver default -> Pre-mortem.
- Second pass -> only when the first yields no material Aha, choose a materially different operator, declare `Second reframe used: <technique>` before the Aha, and never credit an undeclared operator later.
- Honor a user-requested technique when it is usable; do not silently replace it with a "nearest supported" technique.
- Chat disclosure: `Reframe used: <technique>` plus one line explaining why.

## Aha Check

- **Aha is the restructuring insight**: the moment the problem is re-represented so a different candidate field becomes visible.
- Make the representational change explicit: from the baseline frame to the alternative frame.
- Output `Aha: <restructuring insight>` without an epistemic label; a representational operation is not itself a factual proposition.
- Follow with `Aha basis: <why this shift is warranted> [evidence: fact | supported inference]`.
- Put any testable mechanism or outcome on a separate optional line: `Claim: <claim> [evidence: fact | supported inference | hypothesis]`.
- An Aha is material only if it changes the candidate field, proof surface, ordering, or decision criteria.
- Creative force does not upgrade a basis or claim's factual status. Use `hypothesis` only for a concrete claim with a real falsifier.
- For a `Claim` labeled fact or supported inference, name its source or support in the evidence posture or adjacent to the Claim.
- If a claim is an unverified mechanism or outcome, label it as a hypothesis and make validation part of an expected signal.
- For every `Claim` labeled hypothesis, one expected signal must include `Claim falsifier: <observation>` and test that exact claim, not a neighboring assertion.
- If no material Aha appears after the second pass, state `Aha: N/A after second pass`, continue with the strongest grounded portfolio available, and mark same-basin honestly. Do not manufacture an Aha or diversity.

## Diversity guard

- Name the default solution basin before generating tiers.
- Ensure at least two tiers shift frame, not merely cost or scope.
- Useful frame shifts include substrate, interface, constraint, proof surface, incentive, time horizon, operating model, user ritual, or authority boundary.
- Put the frame in each option heading, for example `Quick Win — Instrument first [frame: proof surface]`.
- If the five tiers cannot honestly diverge, say so and mark the portfolio as same-basin.

## Accretion

- An accretive artifact is a durable asset retained even when an option is wrong: measurement, harness, spec, test, automation, interface, dataset, or decision record.
- Define 1-3 Artifact Spine assets shared across tiers, each with a stable name and home. Every `Accretive artifact` line must repeat at least one exact declared asset name or home; an unqualified new artifact is invalid. If reuse is honestly impossible, declare and justify a replacement spine before the portfolio.
- Every escape hatch must name the proof artifact retained after a prototype or production change is removed. Retaining only an undeclared by-product does not satisfy accretion. The retained artifact proves only observations bound by the signal; do not call ritual or artifact completion proof of benefit without a comparator and outcome predicate.
- Fast Spark: give each spine asset's purpose and home; put the timebox in the option signal.
- Full Session: repeat each asset's purpose and home, add its minimal interface, and explain how the ladder compounds.
- Expected signals must be timeboxed and partition every outcome with mutually exclusive, exhaustive clauses. Use `Inconclusive iff any of <named prerequisites> is missing -> <next disposition>; otherwise Pass iff <success>; Fail otherwise`; for a legitimate measured third state, use `Pass iff <success>; Fail iff <falsifier>; Inconclusive otherwise -> <next disposition>`; omit Inconclusive when Pass and Fail are complements. Every value or predicate consumed by Pass must be established or named separately in Inconclusive. Every missing-prerequisite Inconclusive clause must use the exact `any of ... is missing` form and put all missing prerequisites in that one list, never an ambiguous combined negation. Quantified item outcomes use integer counts such as `at least 1 of n`, not fractional item grammar. Relative terms such as dominant, material, acceptable, stable, comparable, beyond noise, best, ranking, or percentage improvement require a named baseline or denominator, comparison rule, predeclared threshold, and replication count repeated in the signal; references to recorded or agreed criteria do not satisfy this rule. Terms such as `complete`, `representative`, `correct`, or `compatible` require their operational fields or selection rule in the signal, not an adjective standing in for a predicate. Any use of `falsify` or `falsifier` must state the predeclared observation predicate for each hypothesis. A universal, `every`, `all`, or Cartesian-product predicate must predeclare a nonzero finite denominator; an empty set is Inconclusive or Fail, never Pass. When a required threshold is unknown, resolve that threshold instead of claiming an unspecified target will be met. Do not promise an outcome that the current evidence cannot support.

## Tier semantics

- Quick Win: cheapest reversible move that improves the decision or outcome now.
- Strategic Play: strongest path within the current operating model.
- Advantage Play: creates a reusable capability, compounding asset, or asymmetric option.
- Transformative Move: changes an interface, operating model, governing constraint, or user ritual.
- Moonshot: tests discontinuous upside through the smallest bounded proof-bearing probe.

## Option template

```text
Quick Win — <move> [frame: <frame>]
- Accretive artifact (spine): <exact declared spine name/home> — <addition>
- Expected signal + timebox: <time>; Inconclusive iff any of <named prerequisites> is missing -> <next disposition>; otherwise Pass iff <success>; Fail otherwise
- Escape hatch: <pre-irreversible stop>; retain <exact spine proof>

Strategic Play — <move> [frame: <frame>]
- Accretive artifact (spine): <exact declared spine name/home> — <addition>
- Expected signal + timebox: <time>; Inconclusive iff any of <named prerequisites> is missing -> <next disposition>; otherwise Pass iff <success>; Fail otherwise
- Escape hatch: <pre-irreversible stop>; retain <exact spine proof>

Advantage Play — <move> [frame: <frame>]
- Accretive artifact (spine): <exact declared spine name/home> — <addition>
- Expected signal + timebox: <time>; Inconclusive iff any of <named prerequisites> is missing -> <next disposition>; otherwise Pass iff <success>; Fail otherwise
- Escape hatch: <pre-irreversible stop>; retain <exact spine proof>

Transformative Move — <move> [frame: <frame>]
- Accretive artifact (spine): <exact declared spine name/home> — <addition>
- Expected signal + timebox: <time>; Inconclusive iff any of <named prerequisites> is missing -> <next disposition>; otherwise Pass iff <success>; Fail otherwise
- Escape hatch: <pre-irreversible stop>; retain <exact spine proof>

Moonshot — <move> [frame: <frame>]
- Accretive artifact (spine): <exact declared spine name/home> — <addition>
- Expected signal + timebox: <time>; Inconclusive iff any of <named prerequisites> is missing -> <next disposition>; otherwise Pass iff <success>; Fail otherwise
- Escape hatch: <pre-irreversible stop>; retain <exact spine proof>
```

## Selection guidance

- Fast Spark: name the best learning bet, best near-term outcome bet, and boldest bounded probe; give a conditional recommendation. When target success is unknown, output `Best near-term outcome bet: none; basis: target success is undefined. [evidence: fact]` rather than relabeling decision progress as the target outcome. Treat every unmeasured `best` or recommendation ranking as supported inference or hypothesis, never fact; name its basis and end it with that evidence label.
- Full Session: optionally score Impact, Information, Accretion, Confidence, Reversibility, and Time-to-signal from 1-5. Use 5 for the more favorable end of every dimension; for Time-to-signal, 5 means faster. Do not rank by a summed total. Compute dominance across all displayed dimensions and output `Pareto leaders: <every non-dominated tier by name>` plus the trade-off; if dominance was not checked, omit the Pareto claim. End every `best` selection and recommendation line with `[evidence: fact | supported inference | hypothesis]` and name its basis.
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
- Candidate-field summary and frames that survived winnowing; evidence-label every causal or decision-shaping inference, including stage choice, reframe `Why`, winnowing, diversity/same-basin disposition, score interpretation, and recommendations.
- Optional scorecard with brief rationale.
- Explicit compact lines labeled `Facts:`, `Risks:`, `Assets:`, `Assumptions:`, and `Constraints:`.
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
Definition Gate: domain=Search API; symptom/actors/topology=p95 ~800ms across API clients -> search service -> query engine -> serialization/transport; desired outcome/success=p95<=200ms and p99<=400ms; metric/threshold/basis=pooled fixed-fixture latency and relevancy diff across exactly 5 batches; representative workload population/selection rule=fixed dataset stratified by current request-size and filter-shape distributions; constraints/guardrails=current infra cost, CPU +<=10%, and no relevancy regression.
Evidence: latency, gate fields, and targets are known; the bottleneck is unknown.

Reframe used: SCAMPER
Why: mutate the existing request path before assuming a replacement is necessary.
Aha: shift from query-only optimization to whole-path budget allocation.
Aha basis: the reported p95 spans the listed request path, and the bottleneck is unknown. [evidence: fact]
Claim: across repeated fixed-fixture batches, the pooled mean non-query share among requests in each batch's slowest 1% is >=10%. [evidence: hypothesis]
Why it matters: query, serialization, payload, cache, and transport become competing hypotheses; tracing decides which budget dominates.
Default basin: tune the query engine directly.
Frames: proof surface, constraint budget, operating model, interface, substrate.
Artifact Spine:
- bench/search/: fixed dataset + immutable pre-change baseline + candidate adapters + p50/p95/p99 + relevancy diff; home: repo benchmark suite.
- perf/tracing/: query/serialization/transport breakdown; home: repo performance tooling.
- contracts/search-response/: opt-in response contract + conformance fixtures; home: repo contract tests.
Quick Win — Instrument the latency budget [frame: proof surface]
- Accretive artifact (spine): exactly 5 fixed-fixture batch results and all 50 slowest-1% request decompositions in perf/tracing/, keyed to the bench/search/ harness.
- Expected signal + timebox: within 1 day, run exactly 5 fixed-fixture batches of exactly 1,000 requests and decompose the 10 slowest requests in each batch; Pass iff the 95% bootstrap CI lower bound for pooled mean non-query share is >=10%; Claim falsifier: Fail iff its upper bound is <10%; Inconclusive otherwise -> run one additional predeclared set of exactly 5 such batches before selection.
- Escape hatch: disable high-overhead tracing; retain the bench/search/ harness plus perf/tracing/ batch results and every slowest-1% request decomposition.

Strategic Play — Attack the measured largest budget [frame: constraint]
- Accretive artifact (spine): measured-stage experiment fixture + before/after result in bench/search/.
- Expected signal + timebox: within 2 days, run the candidate and immutable pre-change bench/search/ baseline for exactly 5 fixed-fixture batches of exactly 1,000 requests each, including exactly 100 predeclared relevancy cases per batch; let B=baseline pooled p95 and C=candidate pooled p95; Pass iff (B-C)/B >=30% and all 500 candidate relevancy results match baseline; Fail otherwise.
- Escape hatch: feature flag or revert the production change; retain the bench/search/ fixture, result, and diagnosis.

Advantage Play — Make latency a continuous contract [frame: operating model]
- Accretive artifact (spine): predeclared >=20%-over-baseline seeded fixture, performance budget check, and trend history in bench/search/.
- Expected signal + timebox: within 2 days, inject a predeclared fixture whose p95 is >=20% above the fixed bench/search/ baseline; Pass iff two consecutive check runs both reject it before merge; Fail otherwise.
- Escape hatch: begin as an advisory check; keep the bench/search/ seeded fixture, check, and trend data if gating is noisy.

Transformative Move — Change the response contract [frame: interface]
- Accretive artifact (spine): opt-in contract + conformance fixtures in contracts/search-response/, measured by bench/search/.
- Expected signal + timebox: within 3 days, across two runs per fixture, Pass iff first useful bytes arrive <=200ms on all exactly 10 predeclared fixtures with a >=1 MiB response body; Fail otherwise.
- Escape hatch: disable the opt-in endpoint, retain the current response as default, and keep contracts/search-response/ fixtures plus bench/search/ results.

Moonshot — Run an architecture bakeoff [frame: substrate]
- Accretive artifact (spine): evaluation adapter + fixed fixtures in bench/search/ comparing engines and transport shapes.
- Expected signal + timebox: within 1 week, run exactly 3 candidates and the immutable pre-change bench/search/ baseline for exactly 5 fixed-fixture batches each; let B=baseline pooled p99 and C_i=each candidate's pooled p99; Pass iff at least one of the 3 satisfies 3*C_i <= B; Fail otherwise.
- Escape hatch: stop before migration; keep the bench/search/ adapter, fixtures, and results as durable decision evidence.

Best learning bet: Quick Win, because it identifies which path budget owns the uncertainty. [evidence: supported inference]
Best near-term outcome bet: Strategic after tracing, because it attacks the measured largest budget against the fixed baseline. [evidence: supported inference]
Boldest bounded probe: Moonshot, because three candidates test discontinuous latency upside before migration. [evidence: supported inference]
Conditional recommendation: start with Quick Win, then choose Strategic or Transformative from measured evidence because both preserve the shared proof spine. [evidence: supported inference]
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

- "`$creative-problem-solver`" -> direct clarification; no portfolio object is authorized.
- "Use `$creative-problem-solver`." -> direct clarification until a portfolio object is supplied.
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
