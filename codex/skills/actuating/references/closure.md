# Live Closure

Closure is a current judgment over owner facts, not stored workflow state.

Let:

```text
G = current accepted Goal
H = exact clean Git head and tree
V = exact validation results bound to H
R = exact CAS review receipts bound to H and the current review context
P = current Ship/provider publication evidence
F = current applicable Review Fold
A = current architecture reconciliation judgment
S = current counterexample topology and correctness delta when bug-driven
```

Then:

```text
Close(G, H, V, R, P, F, A, S)
  -> continue | ready-to-ship | complete | blocked
```

## Local implementation

`$actuating implement` is locally complete only when:

- the accepted Goal permits mutation and its local terminal outcome is met;
- the current tree realizes the selected target architecture;
- every required retirement is absent or deliberately successor-mapped;
- every required validation command passes on the exact current head;
- every accepted bug witness is rejected through sanctioned paths;
- every selected counterexample family is excluded at its canonical owner or
  its unavoidable residual invalidity is explicit, owned, and tested;
- every material escape path selected for retirement is absent;
- no requested local operation remains open;
- no applicable current blocker remains.

It requires neither publication nor closure-grade review unless the accepted
Goal explicitly requires them.

## Final closeout

Final `complete` additionally requires:

- the exact current head is publicly represented by Ship when publication is
  required;
- the current review context binds the exact Goal, base, head, Review Contract,
  and optional pre-review Ship observation;
- all four auxiliary requests have current terminal semantic verdicts;
- five consecutive distinct standard attempts are clean for the exact unchanged
  head;
- every finding has been classified by `$review-fold`;
- no applicable accepted finding remains unresolved;
- no semantic hotspot remains answered only by another independent downstream
  guard when an admissible owner-level exclusion was selected;
- no material later evidence invalidates the Goal, architecture, realization,
  validation, publication, or review result.

A current implementation satisfying every non-public predicate but not yet
published is `ready-to-ship`.

## Blockers

Return `blocked` for:

- missing source authority;
- unknown or conflicting current repository identity;
- architecture underdetermination requiring external choice;
- an unresolved admission frontier material to the selected correction;
- counterexample-family or witness-independence claims unsupported by current
  owner evidence;
- applicable evidence that cannot be classified safely;
- validation failure;
- incomplete family elimination, bypass retirement, realization, or retirement;
- publication mismatch;
- missing or stale review evidence;
- exhausted request-local review recovery;
- any claimed review count that cannot be resolved to exact CAS receipts.

## Invalidation

No invalidation event is needed:

```text
Goal changed -> recompile
head changed -> rerun head-bound validation and review
review context changed -> prior request bindings do not match
publication changed -> provider readback does not match
new bug or finding arrived -> Review Fold, semantic-hotspot analysis,
                              and architecture closure reopen
```

Actuating reports the live verdict and its current premises in the user-facing
closeout. It does not materialize a closure receipt.
