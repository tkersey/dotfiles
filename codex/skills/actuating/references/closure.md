# Closure Theorem

Closure is Actuating's deterministic semantic theorem over current inputs.
Actuating alone applies it, selects the next action, and authors the resulting
`actuating-closure-receipt/v1`. Ledger may replay evidence and emit requested
disposable structural projections, but it never emits a closure verdict or
authors the receipt.

~~~text
Close(G, K, Q, E, R, current_subject)
  -> continue | ready-to-ship | complete | blocked
~~~

`G` is the current Goal Contract, `K` the current Construction Contract, `Q`
the applicable Counterexample Sets, `E` the current Evidence Ledger, and `R`
the static Review Contract.

## Theorem

A terminal judgment is legal only when all applicable statements hold:

1. `K` references the current `G`, is the current Construction for this
   realization, and its `base_artifact_digest` plus the Evidence transition
   chain yields the live subject. The immutable base digest is not required to
   equal the post-effect subject.
2. Every Goal law has a Construction and proof obligation.
3. Every accepted Counterexample is excluded by `K`, rejected with evidence,
   or represented by an explicit blocker.
4. Every preservation and progress obligation passes on the current subject.
5. Every required retirement passes and no declared dominated construct or
   bypass remains.
6. The Evidence Ledger contains current owner-issued observations that realize
   `K`; Actuating has dereferenced their content-addressed evidence and verified
   the exact Construction-selected verifier provenance; no requested operation
   remains unresolved.
7. For a `final-closeout` `complete` verdict when publication is required, the
   work has current Ship evidence for the exact subject; Actuating has resolved
   `publication_observed.receipt_ref`, recomputed the immutable `SHIP-v1`
   digest, and verified its repository, base/head tuple, live readback, and
   complete `actuation_binding` against the exact `ready-to-ship` receipt.
   A `ready-to-ship` judgment deliberately omits this premise: that receipt is
   Ship's required readiness input for producing the publication evidence.
8. For a `final-closeout` `complete` verdict, the work has current auxiliary
   results and five consecutive distinct standard clean attempts whose cited
   CAS receipts Actuating has dereferenced and matched to their exact request,
   attempt, instruction, lens, and current subject tuple; it has no unresolved
   request-local recovery or unresolved accepted Counterexample.
   A `ready-to-ship` judgment also omits this premise because Ship publication
   precedes the independent review campaign.
9. No later material event invalidates authority, subject, proof, publication,
   or review evidence.

Ledger validation, replay, `state`, or `project` can expose structural premises.
They cannot decide semantic adequacy, interpret CAS or Ship, compute review
credit, choose the next action, or pronounce the theorem satisfied. Actuating
performs that evaluation and records the cited evidence in its receipt and
handoff.

## Mode results

- `implement` may return local `complete` without Ship or review-closeout.
- `triage` terminates with a Counterexample Set and report, not code closure.
- `remediation-plan` terminates with a non-executable successor proposal.
- Bare mode and `review-closeout` require publication when selected and the
  full five-clean review theorem before `complete`.
- Missing current publication evidence after otherwise complete
  publication-required implementation yields `ready-to-ship`; it does not
  block on evidence that only Ship can produce from that handoff.
- Missing authority or an unresolved liability yields `blocked`.

## Receipt and rendering

Actuating authors one `actuating-closure-receipt/v1` binding the Goal,
Construction, subject, Evidence head, Review Contract, closure route, semantic
verdict, and cited premises. The receipt grants no new authority and becomes
stale when any bound input changes. Ledger may validate its structure after
authorship; it must not construct it, populate its verdict, or emit it from
`state` or `project`.

~~~yaml
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
~~~

`local-implementation` is the explicit `$actuating implement` terminal route;
review and Ship evidence are not applicable. `final-closeout` covers bare mode
and `review-closeout`; `ready-to-ship` is legal only on this route and omits
publication and review premises, while its `complete` verdict requires the
current publication and five-clean premises selected by the Goal and route.
Proof renderers must use this discriminant and must not infer applicability
from absent fields.

`receipt_id` is the content digest of canonical JSON with `receipt_id` set to
JSON `null`. It is a freshness-bound semantic receipt authored only by
Actuating, not another authoritative artifact family.

`$proof-patch` may render a current `complete` receipt for humans. It never
decides closure, changes state, or publishes.

Complete delivery handoff or reporting before source-memory evaluation. Memory
admission cannot gate, delay, invalidate, or roll back delivery closure.
