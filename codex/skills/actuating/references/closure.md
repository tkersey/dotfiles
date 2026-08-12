# Closure Theorem

Closure is Actuating's deterministic semantic theorem over current inputs.
Actuating alone applies it, selects the next action, and authors
`actuating-closure-receipt/v1`. Ledger may validate, replay, and project
structural facts but never emits the verdict.

```text
Close(G, K4, Q*, E, R, current_subject)
  -> continue | ready-to-ship | complete | blocked
```

`G` is the current Goal Contract. `K4` is the current
`construction-contract/v4`. `Q*` is the complete applicable Counterexample
Theory derived from current and predecessor Sets. `E` is the Evidence Ledger and
`R` the static Review Contract.

## Theorem

A terminal judgment is legal only when every applicable statement holds:

1. `K4` references the current `G`, is the current Construction, and its base
   subject plus recorded effect chain yields the exact clean live subject.
2. `K4.counterexample_class_refs` is the complete set of currently applicable
   accepted classes across the Goal lineage. Every class maps to one causal
   generator or an evidenced instance-specific exception.
3. Every Goal law and causal generator has a selected semantic-model element,
   Construction factor, and strongest-feasible proof obligation.
4. Every accepted Counterexample is excluded by the selected model, rejected
   with current evidence, or represented by an explicit blocker.
5. Candidate comparison carries one complete mandatory obligation core.
   Arrival order cannot change the selected normal form except by exposing the
   same explicit incomparable minima.
6. Realization exactness passes on the current subject:
   - every live correctness-bearing production mechanism maps to one selected
     factor;
   - every live proof mechanism maps to one current proof obligation;
   - `unmapped_production_surface` and `unmapped_proof_surface` are empty;
   - every required retirement and absence verifier passes.
7. All selected implementation, preservation, acceptance, and falsification
   obligations pass on the exact current subject. No requested operation remains
   unresolved.
8. For `final-closeout` `complete` when publication is required, Actuating has
   dereferenced current Ship-owned evidence for the exact repository, base/head
   refs and OIDs, subject, Goal, Construction, and actuation binding.
   `SHIP-v1` and `SHIP-ADOPTION-v1` remain owner-issued; Actuating cannot
   substitute its own live-readback record.
9. For `final-closeout` `complete`, the exact published subject has one current
   terminal result from each auxiliary lens and five consecutive distinct
   standard clean attempts under the static Review Contract. Every credited CAS
   receipt matches its request, instructions, lens, campaign, base/head tuple,
   and subject. No request-local recovery or accepted Counterexample remains
   unresolved.
10. No later material event invalidates authority, cumulative Counterexample
    Theory, semantic model, subject, proof, publication, review evidence, or
    retirement.

A material subject change invalidates all review credit and requires a fresh
concurrent 1+4 wave followed by the complete five-clean streak. The streak is
repeated stochastic falsification and remains mandatory.

## Review evidence law

A finding can affect closure only after `$review-fold` classifies it. Accepted
classes join `Q*`; they never map directly to a patch. Actuating recomputes the
causal basis and selects one Construction against the complete theory.

A closure-grade review binding must be canonical before dispatch. Findings from
an invalid binding cannot authorize mutation. A defect may re-enter through a
lawful independent falsifier or canonical review.

## Publication ordering

Formal Evidence ingestion order is not provider publication time. For a new
campaign, a valid `SHIP-ADOPTION-v1` may be recorded after review when it
ratifies the exact `SHIP-OBSERVATION-v1` recorded before campaign binding.
Observation, campaign, credited receipts, and adoption must exact-match the
stable repository/default-branch/base/head/subject/Goal/Construction/Review
Contract tuple.

For a historical campaign predating `SHIP-OBSERVATION-v1`, require exact
provider-backed publication evidence and an
`actuating-publication-campaign-causality/v1` attachment over one exact Seq
observation proving the publication call completed before the campaign call by
source-line order. Matching endpoints or incomparable wall clocks are
insufficient.

## Mode results

- `implement` may return local `complete` without Ship or review-closeout.
- `triage` terminates with a Counterexample Set and report, not code closure.
- `remediation-plan` terminates with a non-executable Construction proposal.
- Bare mode and `review-closeout` require publication when selected, complete
  realization exactness, and the full five-clean review theorem before
  `complete`.
- Missing publication evidence after otherwise complete
  publication-required implementation yields `ready-to-ship`.
- Incomplete Counterexample Theory, semantic-model novelty hidden inside a local
  repair, incomparable candidates without authority, unmapped surface,
  incomplete retirement, missing proof, or stale review evidence yields
  `blocked`.

## Receipt

Actuating authors one `actuating-closure-receipt/v1` binding the current Goal,
Construction, subject, Evidence head, Review Contract, route, verdict, and cited
premises.

```yaml
closure_receipt:
  schema: actuating-closure-receipt/v1
  receipt_id:
  goal_contract_ref:
  construction_ref:
  subject_digest:
  evidence_head:
  review_contract_digest:
  closure_route: local-implementation | final-closeout
  verdict: continue | ready-to-ship | complete | blocked
  cited_premise_refs: []
  blockers: []
```

The receipt grants no new authority and becomes stale when any bound input
changes. The receipt is the closeout proof; no separate rendering authority is
required.

Complete delivery before source-memory evaluation. Memory admission cannot gate,
delay, invalidate, or roll back closure.
