# Derived Closure

Closure is a deterministic projection of the current Goal Contract,
Construction Contract, Counterexample Sets, Evidence Ledger, static Review
Contract, and repository subject. It is not an independently authored decision.

~~~text
Close(G, K, Q, E, R, current_subject)
  -> continue | ready-to-ship | complete | blocked
~~~

## Projection path

Use the explicit artifact-kernel goal surface:

~~~bash
ledger --source actuation --goal GOAL_ID state
ledger --source actuation --goal GOAL_ID decide
~~~

`state` and `decide` replay the Evidence Ledger and recompute current repository
identity. Use the JSON verdict, not prose or exit-code folklore, as the workflow
result.

## Closure theorem

Derive a legal terminal route only when all are true:

1. The current Goal has not been superseded, and the current Construction
   references it.
2. The Construction and repository subject are current.
3. Every Goal law has a corresponding construction and proof obligation. Each
   implementation or acceptance obligation has independent passing verifier
   and `<obligation_id>#falsifier` observations on the current subject; review
   and Ship obligations retain their external-owner proof projections.
4. Every applicable accepted Counterexample is excluded by the current
   Construction; every rejected class has evidence; every blocked class remains
   an explicit blocker.
5. Every preservation obligation passes.
6. Every progress obligation passes.
7. Every required retirement passes.
8. No declared dominated construct, duplicate owner, bypass, or predecessor
   proof path remains live.
9. The Evidence Ledger proves that the current subject realizes the current
   Construction.
10. No operation or capability is pending.
11. No proof obligation is outstanding.
12. When the Goal requires publication, a current successful Ship receipt is
    observed for the exact Construction and subject. Ship owns the immutable
    owner receipt. Ledger grants currentness only while live `HEAD^{commit}` and
    symbolic branch equal its `head_sha` and `branch`, and Goal
    `scope.base_ref` resolves to the branch denoted by `base_branch`. A
    mismatch, detached HEAD, unresolved base, or Git query failure returns a
    complete local proof to `ready-to-ship` and blocks review admission.
13. When final review is required, all auxiliaries are current, the trailing
    standard streak contains five consecutive fresh clean attempts on the
    current subject, no request-local recovery remains, and no accepted or
    blocked Counterexample remains unresolved.
14. No later material event invalidates any proof input.

Return `blocked` with concrete reasons when a required input is invalid or a
blocker exists. Return `continue` and the next legal transition when the fold is
valid but incomplete. Return `ready-to-ship` only for a publication-required
Goal whose implementation proof is complete and current but whose public
effect is not yet observed. Return `complete` only for the Goal's terminal
route.

## Closure receipt

A serialized `actuating-closure-receipt/v1` is a cacheable view. Bind at least:

~~~text
Goal Contract
Construction Contract
current subject digest
goal-local Evidence Ledger head
static Review Contract
review campaign and owner-issued publication projection when present
projected verdict and blockers
~~~

The receipt grants no new authority. Any later event for that goal makes it
historical and requires a fresh projection. Events for an unrelated goal may
advance a shared physical store without changing this goal's material fold.

`$proof-patch` may render only a current terminal receipt. It is a human view,
not closure or publication authority.

## Mode projections

| Mode point | Expected projection |
|---|---|
| Open or incomplete construction | `continue` |
| Missing/stale authority, proof, recovery, retirement, or review | `blocked` |
| Complete publication-required proof without current Ship evidence | `ready-to-ship` |
| Explicit `implement` with complete local proof | `complete` |
| Bare/review-closeout with current Ship and review convergence | `complete` |

One observed operation may discharge obligations but never completes the
parent goal by itself.

## Publication continuation

Hand `ready-to-ship` to `$ship`; no other owner may mutate a public tracker.
For `artifact-kernel-v1`, the transient Ship input projects:

~~~text
actuation_binding.actuation_run_id = closure_receipt.receipt_id
actuation_binding.state_fingerprint = closure_receipt.subject_digest
~~~

The compatibility pair grants no authority and is not persisted as a peer
artifact. Append the successful current `SHIP-v1` receipt as external evidence.
If the published subject differs, all review credit resets and final review
begins with a fresh concurrent 1+4 wave on that subject.

## Post-closure learning

Delivery closure and its handoff/report precede source-memory evaluation:

~~~text
closure -> handoff/report -> source-memory checkpoint and learning
~~~

Learnings, Synesthesia, Negative Ledger, and compiled memory may consume the
closed artifact lineage. Optional learning or admission failure does not change
or roll back the code closure verdict. A later tracked learning write inside
Goal scope is an ordinary material subject change; an excluded Ledger control
write is not.

## Failure behavior

Malformed artifacts, broken event continuity, invalid transitions, stale
subject or authority, capability replay, verifier substitution, path escape,
unresolved Counterexamples, incomplete retirements, stale review/publication,
and custody failure must fail closed. A failed verifier is an observation, not
proof discharge. A timed-out or verdictless external attempt receives no
semantic credit.
