# ALSR/HYL/HSR Reference

## Summary

```text
ALSR-v1 = loop contract
HYL-v1  = actuation hylomorphism / loop machine
HSR-v1  = per-step transition receipt
ATCG-v1 = terminal closure reducer
```

## The no-hidden-loop invariant

```text
No material mutation without unfold.
No continuation without fold.
No completion without terminal algebra.
```

## Why this exists

Audits showed `$agent-loop-schemes` was known and sometimes activated, but not reliably governing true `$actuating` runs. The fix is to make loop shape a typed, current, auditable receipt consumed by `$actuating`, `$goal-actuating`, ATCG, and `seq`.

## Direct action fusion

Direct, one-shot work may fuse ALSR/HYL into the final proof-patch when all are true:

```text
one legal work item
known verifier
no review requirement
no parallelism
no $st requirement
no public side effect
no repeated class/migration/branch choice
```

## Unfusion

If evidence reveals repeated classes, review campaign, migration shape, branch choice, proof fanout, parallel frontier, `$st` requirement, or unclear stop rule, emit `replan` and compile ALSR/HYL.

## Review quotient

Review findings should be quotiented into classes before implementation:

```text
Finding* / equivalence -> LiabilityClass -> WorkNode
```

Equivalence relations:

```text
same owner boundary
same counterexample
same proof gap
same refactor kernel
same canonical owner
same invalid transition
```

## `$st` as continuation

`$st` is emitted by HYL as an escape continuation when local actuation cannot safely own resource claims, fencing, worktrees, or serialized integration.

## `$ship` as terminal effect

`$ship` is only a terminal publication/update effect handler after proof and ATCG permit closure and PR publication/update is requested.
