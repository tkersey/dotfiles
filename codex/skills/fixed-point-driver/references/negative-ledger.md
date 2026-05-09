# Negative Evidence Ledger

Use the Negative Evidence Ledger to preserve disconfirmed search paths during fixed-point work. Its purpose is search-space pruning: prevent the loop from spending tokens, implementation effort, or review budget on hypotheses that already failed under comparable conditions.

## Trigger

Create or refresh this ledger only when negative evidence would materially change routing:

- prior failed or reverted attempts are mentioned by the user, commit history, PR comments, logs, benchmarks, or `.learnings.jsonl`
- a previous loop produced a benchmark regression, no-effect result, unsoundness finding, or review rejection
- the task is optimization-heavy, debugging-heavy, flaky-test-heavy, or otherwise likely to rediscover dead ends
- the one-change challenge risks proposing a previously-disconfirmed route

Do not create this ledger for simple one-pass implementation tasks.

## `negative-ledger-mapper` role

`negative-ledger-mapper` is a read-only specialist. It maps prior failed attempts into current, evidence-backed routing constraints. It must not implement code, run final proof gates, adjudicate closure, or veto current work without current-state applicability evidence.

The specialist answers five questions:

1. What has already been tried?
2. What concrete evidence showed failure, regression, no material effect, unsoundness, or revert?
3. Does that evidence still apply to the current `artifact_state_id`?
4. Which routes should be excluded, discounted, or reopened only under explicit criteria?
5. Which adjacent search frontier remains promising?

## Applicability gate

A negative-evidence entry is active only when all are true:

- it has a witness: benchmark result, failing test, revert, review rationale, trace, diff, command output, or other concrete evidence
- it names the hypothesis and attempted change narrowly enough to avoid overbroad suppression
- it states applicability conditions tied to the current artifact state
- it includes reopening criteria

If any condition is missing, mark the entry `unknown`, `stale`, or `need-evidence`; do not use it as an exclusion rule.

## Ledger entry shape

```yaml
- neg_id: NEG-001
  hypothesis: "Batch same-leaf mutation bookkeeping to improve small-write throughput"
  attempted_change: "same-leaf mutation-run operator prototype"
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

## Status values

- `active`: witnessed and applicable to the current artifact state
- `stale`: evidence exists but no longer binds the current artifact state
- `superseded`: replaced by a more precise entry or by changed architecture
- `reopened`: reopening criteria were met; the route may be reconsidered with current proof
- `unknown`: evidence or applicability is incomplete

## Failure classes

- `no-effect`: did not materially move the target signal
- `local-regression`: helped one surface but harmed an in-scope surface
- `global-regression`: worsened the main target or broad regression surface
- `unsound`: weakened a correctness, preservation, progress, or invariant obligation
- `too-complex`: added complexity disproportionate to observed value
- `stale`: failed under conditions no longer known to hold
- `unknown`: evidence is incomplete

## Specialist packet footer

Every `negative-ledger-mapper` packet must end with the standard specialist footer:

```md
artifact_state_id: branch=... head=... diff=... paths=... phase=...
artifact_state_label: loop-02-prepatch
scope: prior failed attempts touching ...
top_material_signals:
  - NEG-001: ...
unresolved_signals:
  - ...
agreement_pressure: aligned | mixed | conflicting | unknown
stale: no | yes | unknown
final_call: ...
```

Reject the packet as `transport-invalid`, `wrong-scope`, or `stale` when it violates the common specialist packet rules.

## Interaction with one-change challenge

Before accepting a one-change candidate, check whether it matches an active Negative Evidence Ledger entry. If it does, either choose a different candidate or explicitly show that reopening criteria are now satisfied and that current verification will cover the previously failed mechanism.

## Interaction with learnings

Use the campaign ledger for current routing. If the negative evidence is durable and transferable, optionally capture it through `$learnings` as evidence-backed execution memory. Do not require `$learnings` availability for fixed-point-driver operation.

## Guardrails

- Do not record vibes, hunches, or unevidenced agent preferences as negative evidence.
- Do not let "we tried X" suppress a broader family of strategies unless the evidence covers that family.
- Do not let microbenchmark failure suppress an end-to-end route without explaining benchmark relevance.
- Do not silently delete stale entries; mark them stale or superseded.
- Do not use the ledger as proof of closure. Root-owned verification remains authoritative.
