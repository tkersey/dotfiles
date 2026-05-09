# Negative Ledger and `.learnings.jsonl`

Use `.learnings.jsonl` as the default durable store for negative evidence. Do not create a separate persistent negative-ledger file unless volume, query shape, or schema pressure proves `.learnings.jsonl` insufficient.

## Read path
Use the `learnings` CLI as a source before choosing a new route in search-heavy work.

### Implementation preflight
```bash
run_learnings_tool recall --query "<component failure-surface hypothesis-family>" --limit 8 --drop-superseded
```

### Browse recent negative evidence
```bash
run_learnings_tool recent --limit 15
```

### Query/rank learnings
```bash
run_learnings_tool query --spec "@$LEARNINGS_SPECS_DIR/status-rank.json"
run_learnings_tool query --spec "@$LEARNINGS_SPECS_DIR/top-tags.json"
run_learnings_tool query --spec "@$LEARNINGS_SPECS_DIR/top-paths.json"
```

## Interpreting hits
A `learnings` row is candidate evidence. To promote it into an active Negative Evidence Ledger entry, verify:
- the row has evidence anchors, not just a narrative claim
- the component/path/benchmark/invariant still matches the current artifact state
- the old failure mechanism is still possible
- the exclusion rule can be made narrow
- reopening criteria are clear

If those checks fail, record the hit as `stale`, `superseded`, `unknown`, or `need-evidence`.

## Write path
Append through `learnings append`; do not hand-edit `.learnings.jsonl`.

Use a conditional-action learning statement:

```bash
run_learnings_tool append \
  --status avoid_for_now \
  --learning "When <condition>, avoid <approach> unless <reopening criterion> because <witnessed failure>." \
  --evidence "<command/log/benchmark/revert/review anchor>" \
  --application "Before retrying <approach>, check <condition> and run <proof>." \
  --tag negative-evidence \
  --tag failed-attempt
```

## Status mapping
- `avoid_for_now`: active entry that should prune the route until reopening criteria are met.
- `investigate_more`: possible negative evidence with incomplete witness or applicability.
- `do_less`: repeated low-value or no-effect approach.
- `codify_now`: recurring negative evidence should become a durable rule, fixture, or skill guardrail.
- `review_later`: weak but potentially useful evidence; should not prune routes yet.

## Tag recommendations
Use two to five tags. Prefer:
- `negative-evidence`
- `failed-attempt`
- `benchmark-regression`
- `reverted-change`
- `no-effect`
- `unsound`
- `too-complex`
- domain tags such as `perf`, `mvcc`, `auth`, `migration`, `flaky-test`

## Example row intent
The CLI writes the actual JSONL row. The resulting row should effectively encode:

```json
{
  "status": "avoid_for_now",
  "learning": "When optimizing MVCC small-write throughput, avoid same-leaf bookkeeping batching unless the small-N regression fixture or bookkeeping path has changed because the prior prototype regressed the representative write loop.",
  "evidence": [
    "bench: write-small-n regressed 7% on run 2026-05-09 after same-leaf batching prototype",
    "revert: abc123 removed same-leaf batching after regression"
  ],
  "application": "Before proposing same-leaf batching again, verify the benchmark fixture and MVCC bookkeeping path changed, then rerun the representative small-N benchmark.",
  "tags": ["negative-evidence", "benchmark-regression", "perf"]
}
```

## Capture proof line
When a durable write is attempted, report one proof line:
- `appended: id=...`
- `duplicate-skip: ...`
- `0 records appended: ...`

If no write is attempted because the evidence is in-session only, say `not-attempted: evidence not durable enough` or `not-attempted: non-repo cwd`.
