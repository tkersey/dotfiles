---
name: actuating
description: "Turn accepted intent and classified review evidence into correct-by-construction software through Goal Contracts, Counterexample Sets, Construction Contracts, and an Evidence Ledger. Use bare $actuating for implementation, publication, and review convergence; use explicit implement, triage, remediation-plan, or review-closeout for bounded routes. Actuating alone selects the Construction and next action; Ledger is non-executing and Ship alone owns public effects."
---
# Actuating

## Mission

Turn accepted intent into one lawful Construction, one directly owned operation
at a time, with independent falsification and evidence-backed closure.

## Authority kernel

Use exactly four authoritative per-goal families:

```text
goal-contract/v3          accepted semantics, authority, scope, laws, proof bar
counterexample-set/v1     classified witnessed falsifications
construction-contract/v3 selected architecture, owners, obligations, retirements
evidence-ledger           current observations bound to the exact subject
```

Supporting views, plans, work graphs, review receipts, and proof summaries do not
become peer authority.

## Routes

Choose exactly one current route:

```text
implement          realize the current Construction
triage             classify new pressure before mutation
remediation-plan   select a successor Construction without editing
review-closeout    converge review, publication, and final closure
```

Bare `$actuating` may traverse the routes required by the accepted goal. An
explicit bounded route must not silently widen itself.

## Common loop

1. Bind the current Goal, Construction, subject identity, evidence head, and
   applicable Counterexample Sets.
2. Recompute the current frontier; cached plans or node state do not authorize
   continuation.
3. When architecture or abstraction is live:
   - **OPERATE ARCHITECTONICALLY**;
   - use `$first-principles` to establish the incumbent-independent basis;
   - obtain a bounded `$universalist` nomination;
   - use one bounded `$metanoetic` pass only for a high-regret initial
     nomination, causal recurrence, accepted structural findings, or cumulative
     review-path accretion.
4. Actuating selects exactly one current Construction and one bounded operation.
5. Execute through the owning implementation surface.
6. Record current evidence, classify any new falsifier through `$review-fold`,
   and fold the cumulative changeset before fresh review.
7. Replace the Construction rather than stacking local repairs when accepted
   findings share an owner, law, or cause.
8. Close only from current subject-bound proof; otherwise continue, regress,
   block, or ask for the missing authority.

Before fresh review after repair, evaluate the whole cumulative delta. Pointwise
small fixes must not compose into a dominated final Construction.

## Public effects and closure

`$ship` alone creates or updates public publication state. Actuating decides
whether the current goal is ready to hand to Ship and whether returned
publication evidence satisfies the Goal.

Local implementation completion is not final closeout. Review convergence,
required publication, retirements, and residual blockers remain route-specific.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for a bounded ordinary
implementation operation.

Load it when exact detail is required for:

- artifact schemas, identities, Ledger definitions, or transaction commands;
- Construction candidate comparison and supersession;
- WorkGraph compilation or multi-owner decomposition;
- CAS review topology, clean-streak accounting, or recovery;
- cumulative review-delta folding and refactor-kernel triggers;
- Ship handoffs, adoption, publication evidence, or closure receipts;
- an unported edge route.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- No mutation without current Goal authority and a selected Construction.
- No raw review comment becomes work before `$review-fold` classifies it.
- No helper, plan, graph, reviewer, or subagent selects the next action.
- No passing command, queued review, or successful publication mutation proves
  goal closure by itself.
- Prefer deletion, owner repair, and shared-cause correction over wound-specific
  accretion.
