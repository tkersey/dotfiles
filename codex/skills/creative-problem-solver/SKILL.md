---
name: creative-problem-solver
description: "Generate a compact five-tier strategy portfolio when the next task is choosing among materially different paths. Implicitly invoke for explicit requests for options, alternatives, trade-offs, reframing, or help escaping repeated failure. A name-only or meta mention does not authorize the portfolio route. Do not activate for direct implementation, single-answer advice, skill analysis/tuning, repository-evidence opportunity mining ($ideate), or detailed planning ($plan)."
---

# Creative Problem Solver

Purpose: when a strategy choice is still open, transform the incumbent into materially different candidate paths, project the honest survivors into a five-tier portfolio, and stop for a human choice.

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
- Turning a selected direction into a detailed implementation plan, specification, or execution decomposition: use `$plan`.
- Architecture or codebase understanding without a request for divergent paths: use direct analysis or `$codebase-archaeology`.
- Analysis, explanation, review, tuning, testing, or editing of this skill itself: use direct analysis or `$tune` as appropriate.
- The user already chose a tier or path and asks to execute it: hand off to the execution owner; do not regenerate the portfolio.

### Skill-name rule

- Imperative requests to "use", "run", or "apply `$creative-problem-solver`" **to generate a strategy portfolio** explicitly authorize the portfolio route.
- A name-only or meta mention may load the package under host policy, but it routes to the task owner—or to direct clarification when no task exists—and does not authorize portfolio generation.

### Tie-breakers

- Explicit imperative portfolio invocation wins unless safety, a domain-specific owner, a meta-task owner, or a contradictory execution request requires another route.
- `$ideate` wins when repository evidence mining and ranked opportunities are central.
- `$plan` wins when the direction is selected and the requested output is an execution policy or detailed plan.
- `$tune` wins when the object of work is the skill package itself.
- Activate when the requested outcome is a choice set; do not activate when the outcome is one answer, one plan, or one implementation.

## Method

1. **Bind** only what governs the choice:
   ```text
   Objective: <outcome or decision to improve>
   Hard constraints: <non-negotiable boundaries>
   Incumbent/default basin: <the approach or representation most likely to be repeated>
   Material unknowns: <unknowns that could change the choice>
   ```
2. **Diverge before formalizing**: transform the incumbent across several orthogonal operator axes. Do not use the five tiers as idea prompts.
3. **Quotient**: collapse candidates that share a governing mechanism and differ only by cost, scope, implementation size, rollout speed, timeline, or ambition.
4. **Aha Check** after the initial field exists. If a material re-representation changes the field, proof surface, ordering, or decision criteria, regenerate once under it and quotient again. Otherwise report `Aha: N/A` without penalty.
5. **Winnow** pairwise non-subsumed candidates that would lead to meaningfully different commitments.
6. **Validate proportionally**: attach the smallest reversible probe, decision discriminator, kill criterion, retained asset, and pre-irreversible escape hatch appropriate to each survivor.
7. **Project** survivors onto Quick Win through Moonshot without changing their governing mechanisms to fit the labels. Preserve every heading, but never fabricate a candidate merely to fill a tier.
8. **Recommend conditionally**, then stop for human input before execution.

An unknown blocks solution candidates only when it could invert the decision, makes comparison meaningless, crosses a serious safety/legal/irreversibility boundary, or leaves no concrete decision surface. Otherwise state the assumption, branch conditionally, or resolve it through a probe. Never silently choose a domain, metric, threshold, denominator, population, repetition count, causal mechanism, or factual basis. Separate decision-shaping facts, supported inferences, assumptions, and hypotheses; label only those that affect the choice.

## Lanes

- **Fast Spark**: default. Perform a hidden micro-divergence pass across at least four operator axes, including a subtractive move and a boundary or representation shift when admissible. Show only the decision-useful survivors.
- **Full Session**: use when the user explicitly requests deep or exhaustive exploration, or when high stakes, irreversibility, or coupled constraints make the candidate field itself decision-relevant. Generate roughly 10-30 raw candidates, cluster by governing mechanism, and expose only the clusters or transformations that changed winnowing.
- Difficulty alone does not justify Full Session. Visible brevity never authorizes shallow search.

## Divergence kernel

Treat these as search transformations, not headings to fill:

- **Subtract** — eliminate the need, component, coordination, handoff, or inherited assumption.
- **Invert** — reverse a governing assumption, default, control direction, dependency, or value exchange.
- **Move the boundary** — change the owner, authority, interface, trust boundary, or substrate.
- **Re-represent** — change the model, data shape, abstraction, unit of work, or problem statement.
- **Change time** — precompute, defer, batch, stream, amortize, speculate, or make work event-driven.
- **Change the actor or incentive** — alter who acts, who benefits, who pays, or what behavior the system rewards.
- **Change the proof surface** — solve for a different observable, contract, falsifier, or acceptance boundary.
- **Split, compose, or transfer** — decompose the problem, combine separate moves, or import a mechanism from a structurally analogous domain.

Honor a user-requested creative technique when usable, but use it to transform the incumbent rather than as visible process theater.

## Material diversity

- Selecting one survivor instead of another must change at least one of: governing mechanism, owner, representation, authority boundary, admitted domain, unit of work, proof obligation, or falsifier.
- Retain at least one subtractive candidate and at least one boundary or representation shift when those moves are admissible.
- A candidate subsumed by a stronger candidate is not separate unless it creates a materially different reversible entry point.
- If honest divergence is unavailable, say so. A same-basin portfolio or an empty tier is preferable to fabricated novelty.

## Aha Check

- **Aha is the restructuring insight**: the problem is re-represented so a different candidate field becomes visible.
- Output `Aha: <restructuring insight>` or `Aha: N/A`.
- Follow a material Aha with `Aha basis: <why the shift is warranted> [evidence: fact | supported inference]`.
- Put any empirical proposition on a separate optional line: `Claim: <claim> [evidence: fact | supported inference | hypothesis]`.
- A material Aha must introduce a previously unavailable candidate, change a discriminator or proof surface, or reorder the surviving field. Regenerate once under it; otherwise it is commentary, not an Aha.
- Creative force never upgrades a basis or claim's factual status. A hypothesis needs a concrete disconfirming observation in a relevant probe.

## Probes, evidence, and accretion

Every populated option must contain:

- **Probe** — the smallest reversible commitment that can change the decision; include a timebox when it materially improves control.
- **Discriminator** — the observation or comparison that would favor this path over its live alternatives.
- **Kill criterion** — the observation that defeats the path, its governing claim, or its admissibility.
- **Retained asset** — durable evidence, data, interface, prototype, test, model, specification, or decision record kept even when the path loses.
- **Escape hatch** — the stop, flag, isolation boundary, or pre-commitment that exists before irreversible authority, data, compatibility, or organizational commitment crosses the boundary.

Strengthen only as the claim requires: quantitative comparisons need whatever baseline, denominator, comparison rule, threshold, and repetition make the result interpretable; qualitative inquiry needs an evidence source, interpretation rule, and disconfirming evidence; causal hypotheses need falsifiers; irreversible commitments need abort boundaries and consequence containment. Do not force benchmark grammar onto qualitative or strategic decisions.

An **Evidence Spine** may hold neutral facts, baselines, examples, criteria, or evaluation harnesses that compare candidates without prescribing their construction. Each candidate may instead retain its own **Option Artifact** when its representation, interface, owner, or proof surface differs. Never force a transformative path to inherit the Quick Win's construction merely to share an artifact. Completion alone is not proof of benefit, and post-hoc quarantine is not reversibility.

## Tier projection

- **Quick Win** — cheapest reversible move that improves the decision or outcome now.
- **Strategic Play** — strongest path within the current operating model.
- **Advantage Play** — creates a reusable capability, compounding asset, or asymmetric option.
- **Transformative Move** — changes an interface, operating model, governing constraint, authority boundary, or user ritual.
- **Moonshot** — tests discontinuous upside through the smallest bounded proof-bearing probe.

Project after winnowing. Do not escalate one mechanism through five sizes. If no honest candidate fits a tier, write `No honest <tier> survived divergence` and explain the missing distinction in one sentence.

## Option card

```text
<Tier> — <path> [shift: <mechanism, boundary, representation, or proof surface>]
- Probe: <smallest reversible test; timebox when meaningful>
- Decide by: <discriminator>; kill if <disconfirming observation>
- Retain: <durable option artifact>; escape before <irreversible boundary>
```

Add an assumption or evidence label only when it changes how the option should be interpreted.

## Selection and output

- State the condition under which each leading path dominates and give one conditional recommendation.
- Prefer qualitative trade-off dominance over pseudo-precision. Use numeric scoring or Pareto language only when the user supplies criteria, scale anchors, and evidence that make the values meaningful.
- Fast Spark shows the compact binding, Aha or honest N/A, five tier headings with concise cards or honest gaps, one recommendation, and `Human Input Required: choose a path or update the constraints.`
- Full Session adds a compact candidate-field summary: mechanisms explored, equivalence classes collapsed, and transformations that changed winnowing.
- Do not expose the full operator checklist or discarded idea dump unless the user asks.
- A recommendation is not execution authorization. After selection, hand detailed planning to `$plan` and authorized implementation to the owning workflow. This skill never owns repository mutation.

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
- "Patch `$creative-problem-solver` so it stops over-triggering." -> `$tune`
- "I am blocked by this compiler error. What else can I try?" -> debugging owner
- "Brainstorm twenty names for this command." -> direct creative generation
- "Give me options, choose the best, and implement it now." -> execution owner; portfolio may be internal
- "Mine this repository for evidence-backed product and DX opportunities." -> `$ideate`
- "Turn the chosen event-sourcing direction into a detailed implementation plan." -> `$plan`
- "Explain this repository's architecture and data flow." -> direct analysis / `$codebase-archaeology`
- "Review this pull request for defects." -> review owner
- "We chose the Quick Win. Build it now." -> execution owner
