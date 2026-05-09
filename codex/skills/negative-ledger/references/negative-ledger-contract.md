# Negative Ledger Contract

A Negative Evidence Ledger records **witnessed disconfirmation**, not vibes. It should prune repeated dead ends without turning stale failures into permanent dogma.

## Entry validity test
An entry may affect routing only when all are true:
- the hypothesis is narrow enough to distinguish from adjacent strategies
- the attempted change or decision is named
- evidence is concrete and inspectable
- the observed outcome is stated
- applicability conditions are explicit
- current status is decided against the current artifact state
- exclusion rule is narrow
- reopening criteria are explicit

If any condition is missing, mark the entry `unknown`, `stale`, or `need-evidence`; do not use it as an exclusion rule.

## Ledger entry shape

```yaml
- neg_id: NEG-001
  hypothesis: "Batch same-leaf mutation bookkeeping to improve small-write throughput"
  attempted_change: "same-leaf mutation-run operator prototype"
  source_refs:
    - kind: benchmark
      ref: bench-write-small-n-2026-05-09
      summary: "representative small-N write loop regressed"
    - kind: revert
      ref: abc123
      summary: "reverted same-leaf batching after regression"
    - kind: learning
      ref: lrn-20260509T204312Z-a91f4e2c
      summary: "durable negative-evidence row from .learnings.jsonl"
  learning_source_ids:
    - lrn-20260509T204312Z-a91f4e2c
  evidence:
    - "bench: write-small-n regressed by 7% on run 2026-05-09"
    - "revert: abc123 removed same-leaf batching after regression"
  observed_outcome: "Improved large-N path but regressed single-thread small INSERT loop"
  failure_class: local-regression
  applicability_conditions:
    - "applies while page-level MVCC bookkeeping still dominates small-N writes"
    - "does not apply after the bookkeeping path is structurally replaced"
  current_status: active
  exclusion_rule: "Do not retry this exact same-leaf batching strategy unless benchmark and code-path conditions changed"
  reopening_criteria:
    - "new fixture covers same-leaf batches"
    - "page-state clear cost is eliminated elsewhere"
  confidence: high
  next_search_hint: "Try cursor-open fast path or direct changed-path verification, not page-state clearing"
```

## Source kinds
- `benchmark`: benchmark result, comparison table, profiler output, or run ID
- `test`: failing or passing test result that disconfirms a route
- `revert`: commit, patch, or diff that backed out an attempt
- `review`: review comment or adjudication rationale
- `trace`: runtime trace, log, flamegraph, or diagnostic output
- `diff`: attempted code change or prototype diff
- `learning`: `.learnings.jsonl` row loaded through the `learnings` CLI
- `ledger`: prior fixed-point, closure, or negative-ledger packet
- `user-context`: user-provided report not yet independently witnessed

## Status values
- `active`: witnessed and applicable to the current artifact state
- `stale`: evidence exists but no longer binds the current artifact state
- `superseded`: replaced by a more precise entry or by changed architecture
- `reopened`: reopening criteria were met; the route may be reconsidered with current proof
- `unknown`: evidence or applicability is incomplete
- `need-evidence`: the hypothesis may be negative evidence, but a witness is missing

## Failure classes
- `no-effect`: did not materially move the target signal
- `local-regression`: helped one surface but harmed an in-scope surface
- `global-regression`: worsened the main target or broad regression surface
- `unsound`: weakened a correctness, preservation, progress, or invariant obligation
- `too-complex`: added complexity disproportionate to observed value
- `stale`: failed under conditions no longer known to hold
- `unknown`: evidence is incomplete

## Applicability decision
Classify applicability against the current artifact state:

```yaml
applicability_decision:
  current_state: "branch=... head=... diff=... phase=..."
  still_matches:
    - "same benchmark surface"
    - "same code path"
  no_longer_matches:
    - "old fixture removed"
  decision: active | stale | superseded | reopened | unknown
  rationale: "..."
```

Do not use an old result as an exclusion rule merely because it is memorable. Explain why it still binds the current state.

## Reopening rule
A reopened route needs positive evidence that at least one reopening criterion is satisfied. Examples:
- the benchmark fixture changed
- the failing invariant has a new direct witness
- the old code path was structurally replaced
- a dependency or runtime behavior changed
- the prior failure was narrowed to a different surface

When reopened, the entry should become a proof obligation, not a green light.

## Compaction rule
Compact repeated entries only when they share the same hypothesis family and evidence mechanism. Preserve the strongest witness and list superseded IDs:

```yaml
supersedes:
  - NEG-002
  - NEG-004
compaction_rationale: "Both entries were same-leaf batching regressions on the small-N write loop; NEG-006 keeps the narrower benchmark witness."
```

## Specialist packet footer
When used as a specialist packet, end with:

```md
artifact_state_id: ...
artifact_state_label: ...
scope: ...
top_material_signals:
  - ...
unresolved_signals:
  - ...
agreement_pressure: aligned | mixed | conflicting | unknown
stale: yes | no | unknown
final_call: ...
```
