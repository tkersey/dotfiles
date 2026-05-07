# Workflow

This skill combines repository signal harvesting with mandatory Glaze and ASI escalation gates. It should produce a ranked codebase opportunity portfolio, an escalation ledger, and one plan seed, not a task list.

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
- what level of behavior change is acceptable

If a missing answer materially changes the ranking and cannot be inferred, ask. Otherwise proceed with an explicit assumption.

## Phase 4 — Generate 30 baseline candidates

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

## Phase 5 — First winnow 30 → 5 → 15

Use `RUBRIC.md` to score and cut aggressively.

Suggested sequence:

1. Remove anything with a fatal flaw.
2. Remove ideas with weak or generic evidence.
3. Score the remainder.
4. Rank by weighted score and rationale quality.
5. Keep the strongest 5.
6. Add the next 10 or the strongest complements.
7. Re-rank the 15-set.
8. Choose a preliminary leading direction.

The preliminary leader is not final. It is the best ordinary idea before escalation.

## Phase 6 — Mandatory Glaze gate

Use `ESCALATION_GATES.md`.

Run the Glaze pass over the preliminary top 5 and the preliminary leader.

For each top idea, produce:

- why the obvious version loses
- material delta
- stronger move
- why it wins
- next evaluation step

Cut or demote any top idea that cannot produce a material delta.

The Glaze pass should make the portfolio qualitatively stronger, not merely louder. The pass is successful only when it introduces a new frame, invariant, mechanism, interface, artifact, architecture move, or ordering strategy.

## Phase 7 — Mandatory ASI gate

Use `ESCALATION_GATES.md`.

Run the ASI pass over the strongest Glaze survivors, usually the top 3.

For each, produce:

- why the current answer still underperforms
- 10x horizon
- systemic frame
- leverage point
- smallest proof-bearing artifact
- cash-out type
- why the artifact preserves the 10x insight
- first proof signal

Cut or demote any idea that cannot be collapsed into a small proof-bearing artifact.

The ASI pass should increase ambition while shrinking the first move. The ideal outcome is a small artifact that opens a new capability surface, coordination surface, proof surface, or strategic ordering.

## Phase 8 — Breakthrough synthesis and second winnow

Re-score escalated candidates with the ordinary codebase rubric and the breakthrough criteria.

Ask:

- Did Glaze add a material delta?
- Did ASI expose a 10x frame?
- Did ASI compress that frame into a small artifact?
- Is the artifact still grounded in repository evidence?
- Is the result meaningfully better than the baseline idea?
- Does it create a mechanism, interface, proof surface, or strategy?
- Can the proof signal be observed before a full implementation bet?

Rank the final top 5 by both practical value and breakthrough quality.

## Phase 9 — Overlap scan without `br`

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

Do this after escalation because the escalated idea may have different overlap from its baseline ancestor.

If certainty is impossible because the repo or artifacts are thin, say so explicitly.

## Phase 10 — Plan-space refinement

Refine the chosen direction before turning it into a plan seed.

Use at least five passes:

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

### Pass 4 — Did Glaze materially improve it?

- material delta
- stronger move
- why it dominates the obvious alternative
- what weaker variants were cut

### Pass 5 — Did ASI cash it out?

- 10x frame
- smallest proof-bearing artifact
- mechanism / interface / proof surface / strategy
- first proof signal

Optional:

### Pass 6 — Can the seed be sharper?

- better title
- tighter framing
- cleaner workstream grouping
- narrower non-goals

## Final output

The final artifact is a **codebase opportunity portfolio plus escalation ledger plus one plan seed**, not a roadmap, ticket set, or implementation plan.

A good portfolio is:

- grounded in repo evidence
- diverse across idea types
- explicit about why top ideas beat alternatives
- explicit about the Glaze and ASI transformations
- honest about assumptions, risks, and thin evidence
- useful for choosing what to plan next

A good escalation ledger is:

- compact
- specific
- free of hype
- clear about the material delta
- clear about the 10x frame
- clear about the smallest proof-bearing artifact
- clear about the first proof signal

A good plan seed is:

- specific enough to guide a later planning pass
- bounded enough not to sprawl
- honest about risks and assumptions
- explicit about why it won
- grounded in existing context
- shaped by both the Glaze material delta and the ASI compression

See `OPPORTUNITY_PORTFOLIO_TEMPLATE.md`, `ESCALATION_GATES.md`, and `PLAN_SEED_TEMPLATE.md`.
