# Graph Control Receipt / Graph Intelligence

GCR-v2 must be an execution authority, not only a projected task list.

A material aperture is complete only when it contains graph intelligence:

```yaml
graph_control_receipt:
  receipt_version: GCR-v2
  workspace:
  plan:
  coordination:
  graph:
    roots: []
    leaves: []
    components: []
    ready_frontier: []
    blocked_frontier: []
    selected_frontier: []
    unselected_ready: []
    critical_path: []
    downstream_unlocks: []
    parallel_width:
    antichain_candidates: []
    high_fanout_nodes: []
    articulation_nodes: []
    graph_debt: []
  proof:
    obligations: []
    missing: []
    minimum_proof_cut: []
    proof_cut_kind:
      exact |
      approximation |
      unavailable
  aperture_decision:
    selected_nodes: []
    why_selected: []
    why_not_parallelized: []
    why_unselected_ready_waits: []
  session_projection:
  execution_allowed:
  denial_reasons: []
```

## Required distinction

```text
ready_frontier
  all currently graph-ready nodes

selected_frontier
  bounded selected aperture

unselected_ready
  ready nodes intentionally not selected
```

A GCR that omits `unselected_ready` cannot prove the selected aperture is a
bounded graph decision rather than a checklist projection.

## Proof cut

The receipt should identify the smallest proof set currently known to certify
the selected work.

When exact proof-cut computation is not implemented, emit:

```text
proof_cut_kind: approximation
```

and explain the approximation basis.

When no proof cut is available:

```text
execution_allowed: no
reason: proof_cut_unavailable
```

unless the operation is explicitly read-only.

## Parallelism

If ready nodes could run in parallel but the scheduler selects only one, the
receipt must explain why:

```text
resource conflict
claim budget
proof dependency
fairness
uncertainty
risk
manual operator choice
```

## Ledger-only mode

A list of task IDs without graph intelligence is `ledger_only`.

`ledger_only` may support reporting, migration, and graph repair.

It does not authorize material mutation.
