# Owned Invariant Method

## Invariant record

```yaml
owned_invariant:
  invariant_id:
  statement:
  owner:
  source_of_truth:
  initialization:
  preserving_transitions: []
  violating_counterexamples: []
  enforcement_boundary:
  current_enforcement: []
  missing_or_late_enforcement: []
  exception_ownership:
  proof_surface_ids: []
  evidence_refs: []
  confidence:
```

## Discovery

Start with a concrete bad trace:

```text
valid state
-> transition
-> invalid observable state
```

Then ask:

- which transition first permits the violation?
- which owner had enough information to prevent it?
- is the invalid state representable by design?
- which readers compensate for it?
- what proof would catch recurrence?

## Gate

Reject/downgrade when missing:

```text
owner
counterexample
initialization
transition coverage
enforcement boundary
proof
```

## Enforcement preference

```text
representation/type
constructor
canonical transition
transaction boundary
static tool
runtime validation
downstream tolerance
```

Prefer earlier/stronger enforcement when it does not distort valid semantics.

## Exception ownership

Every exception states who may authorize it, under what evidence, and how it is proved.
