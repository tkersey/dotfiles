# `$st` Policy Handoff

Only the current commitment horizon becomes active durable work.

Current compatibility path:

```text
EPG + EPS state
-> EPD selected action
-> `$st` semantic intake containing exact policy/state/action refs
-> canonical `.ledger/st/st-plan.jsonl`
-> GCR-v1
```

Map:

```text
policy obligation        -> intent atom / proof obligation
selected action          -> contracted task capsule
requires_actions         -> dependency evidence
mutation boundary        -> scope/location
lock roots               -> lock_roots
proof obligations        -> validation/proof actions
expected observations    -> completion evidence
policy/state/action refs  -> source and lineage
```

Do not materialize dormant conditional branches as ready tasks.

`$st` owns:

```text
critical path
parallel width
selected aperture
proof cut
graph debt
execution_allowed
```

Native policy import/materialization is specified in the package CLI spec.
