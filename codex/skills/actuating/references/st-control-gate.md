# `$st` Control Gate

## Purpose

A GCR-v1 is an execution capability, not a report decoration.

For material work:

```text
no current GCR
or
execution_allowed = no
or
blocking unwaived graph debt
or
selected task not in current aperture
=> no delivery mutation
```

## Currentness

Bind:

```text
durable plan sequence/checkpoint
structure fingerprint
contract fingerprint
coverage fingerprint
execution fingerprint
selected task IDs
proof obligations
projection fingerprint
```

A GCR becomes stale after any durable graph mutation, task/proof/status change, waiver change, or artifact change named by its contract.

## Graph-repair mode

When compile/audit fails:

```text
inspect diagnostic
list graph debt
repair intake/graph/proof contract
recompile
```

Do not route around debt with another `.step/*-st-plan.jsonl`.

## Projection

Only the CLI-emitted native projection is published.

```text
one current GCR
-> one update_plan projection
```

Repeated projection for the same GCR requires an explicit projection-drift reason.

## Evidence

The run state should preserve:

```yaml
st_control:
  plan_ref:
  plan_seq:
  gcr_id:
  gcr_ref:
  current:
  execution_allowed:
  blocking_debt: []
  active_waivers: []
  selected_task_ids: []
  projection_fingerprint:
  update_plan_publications:
```
