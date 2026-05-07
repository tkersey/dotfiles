# Workflow

This skill combines repository signal harvesting with a disciplined ideation funnel. It should produce a ranked codebase opportunity portfolio and one plan seed, not a task list.

## Phase 1 — Scope and ground

Infer the working scope from the user prompt. Default to the current repository.

Read:

- `AGENTS.md`
- `README*`
- docs and design notes
- roadmap, backlog, changelog, ADRs, TODOs
- tests, benchmarks, fixtures, examples
- package manifests, build scripts, config files, CI workflows
- public entry points such as commands, routes, exports, and UI flows
- user-provided files, links, tickets, or issue exports

Capture:

- apparent opportunity
- repo shape
- affected users and maintainers
- constraints
- current workarounds
- possible existing plans or overlap
- unknowns that truly require user input

## Phase 2 — Harvest signals

Use `CODEBASE_SIGNAL_LANES.md` to build an opportunity map.

Do not audit every file. Sample strategically across public surfaces, tests, architecture seams, comments, config, docs, and history. Prefer exact evidence.

Signal classes:

- public surface
- maintainer friction
- architecture seam
- test intent
- reliability
- performance
- observability / diagnostics
- negative space
- history / churn
- refactor-enabler

## Phase 3 — Interrogate only material gaps

Before ideating, be able to answer, explicitly or by assumption:

- what problem or opportunity this is about
- who benefits
- what "better" means
- what constraints matter
- what behavior must remain stable
- what is out of scope
- what evidence exists
- what success would look like
- what overlap is already visible

If a missing answer materially changes the ranking and cannot be inferred, ask. Otherwise proceed with an explicit assumption.

## Phase 4 — Generate 30 candidates

Generate a wide field before selecting a direction.

Candidate buckets:

- user-facing additions or feature ideas
- DX / CLI / API / workflow improvements
- refactor or simplification opportunities
- reliability / correctness / recovery ideas
- observability / diagnostics ideas
- performance / scalability ideas
- documentation / onboarding ideas with structural value
- wild-card ideas from negative-space or hidden-primitive lenses

Each candidate should have evidence, originality source, benefit, risk, and validation path.

Avoid:

- duplicate variants
- generic cleanup without leverage
- pure implementation details with no strategic meaning
- feature ideas unsupported by repo evidence unless the user requested speculation
- refactors with no behavior-preservation strategy

## Phase 5 — Winnow 30 → 5 → 15

Use `RUBRIC.md` to score and cut aggressively.

Suggested sequence:

1. Remove anything with a fatal flaw.
2. Remove ideas with weak or generic evidence.
3. Score the remainder.
4. Rank by weighted score and rationale quality.
5. Keep the strongest 5.
6. Add the next 10 or the strongest complements.
7. Re-rank the 15-set.
8. Choose the leading direction.

The value of the 15-set is not merely "more ideas." It reveals complements, enabling bets, and trade-offs around the top candidate.

## Phase 6 — Overlap scan without `br`

Search the repo and provided artifacts for:

- similar roadmap items
- TODOs or backlog notes
- past attempts
- recently completed adjacent work
- existing hidden features
- naming collisions and scope collisions

For each shortlisted idea, classify:

- duplicate
- adjacent / merge mentally
- conflict
- net-new
- unknown due to thin evidence

If certainty is impossible because the repo or artifacts are thin, say so explicitly.

## Phase 7 — Plan-space refinement

Refine the chosen direction before turning it into a plan seed.

Use at least four passes:

### Pass 1 — Is this the right bet?

- sharp user or maintainer benefit
- clear thesis
- sensible boundaries

### Pass 2 — Does it fit the codebase?

- architecture fit
- behavior stability
- migration and compatibility risk
- maintenance cost

### Pass 3 — Is it original and grounded?

- evidence strength
- originality lens
- why it is not generic
- what would disconfirm it

### Pass 4 — What would justify full planning?

- validation path
- measurable success signals
- planning questions that remain open

Optional:

### Pass 5 — Can the seed be sharper?

- better title
- tighter framing
- cleaner workstream grouping
- narrower non-goals

## Final output

The final artifact is a **codebase opportunity portfolio plus one plan seed**, not a roadmap, ticket set, or implementation plan.

A good portfolio is:

- grounded in repo evidence
- diverse across idea types
- explicit about why top ideas beat alternatives
- honest about assumptions, risks, and thin evidence
- useful for choosing what to plan next

A good plan seed is:

- specific enough to guide a later planning pass
- bounded enough not to sprawl
- honest about risks and assumptions
- explicit about why it won
- grounded in existing context

See `OPPORTUNITY_PORTFOLIO_TEMPLATE.md` and `PLAN_SEED_TEMPLATE.md`.
