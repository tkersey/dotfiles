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
```

Then:

```text
Close(G, H, V, R, P, F, A)
  -> continue | ready-to-ship | complete | blocked
```

## Local implementation

`$actuating implement` is locally complete only when:

- the accepted Goal permits mutation and its local terminal outcome is met;
- the current tree realizes the selected target architecture;
- every required retirement is absent or deliberately successor-mapped;
- every required validation command passes on the exact current head;
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
- no material later evidence invalidates the Goal, architecture, realization,
  validation, publication, or review result.

A current implementation satisfying every non-public predicate but not yet
published is `ready-to-ship`.

## Blockers

Return `blocked` for:

- missing source authority;
- unknown or conflicting current repository identity;
- architecture underdetermination requiring external choice;
- applicable evidence that cannot be classified safely;
- validation failure;
- incomplete realization or retirement;
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
new finding arrived -> Review Fold and architecture closure reopen
```

Actuating reports the live verdict and its current premises in the user-facing
closeout. It does not materialize a closure receipt.
