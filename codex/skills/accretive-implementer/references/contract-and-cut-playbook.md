# Contract and Cut Playbook

Before non-trivial edits:

```text
Contract:
Invariants:
Right-sized route:
Stable boundary:
Why not smaller:
Why not larger:
Surface budget:
Proof signal:
```

A good cut is stable, owned, reviewable, and paired with a proof signal.

A bad cut makes the symptom disappear while preserving the invalid producer, duplicate owner, additive scaffold, or unwitnessed guarantee.

## Right-sized route

Choose one:

- `no-change`
- `validate-only`
- `delete-collapse-canonicalize`
- `mutate-existing-owner`
- `add-new-surface`

Move right only when routes to the left are insufficient.

## Why not smaller?

A smaller cut is insufficient when it leaves the invalid producer, duplicate owner, missing witness, or broken invariant intact.

## Why not larger?

A larger cut is excessive when it adds new surface that is not needed to satisfy the contract or retire a real duplicate/invalid state.

## Proof signal

Prefer proof tied to the selected cut:

- failing repro then passing regression;
- characterization test;
- constructor/eliminator coverage;
- round-trip or canonicalization check;
- state-transition preservation;
- direct artifact inspection;
- no-code proof when current artifacts already satisfy the contract.
