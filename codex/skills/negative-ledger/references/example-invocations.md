# Example invocations

## Query prior failures before another optimization
```md
Use $negative-ledger.
Goal: Before proposing the next optimization, find prior failed attempts and map which ones still apply.
Context:
- target benchmark: write-small-n
- current branch vs main
- changed paths: pager/, btree/, mvcc/
- `.learnings.jsonl` is available
Output:
- active negative evidence
- stale/superseded/reopened entries
- safest next-search frontier
```

## Capture a failed attempt
```md
Use $negative-ledger capture.
Hypothesis: same-leaf batching will improve small-write throughput.
Attempted change: prototype in btree/mutation_run.*
Evidence:
- benchmark command: zig build bench -- write-small-n
- result: regressed 7% versus baseline
- diff: abc123..def456
Need:
- negative ledger entry
- learnings append command if durable capture qualifies
```

## Reopen an old failure
```md
Use $negative-ledger reopen.
Old negative evidence: NEG-004 same-leaf batching regression.
New condition: the MVCC bookkeeping path was replaced and the old fixture no longer exercises the same code.
Need:
- whether NEG-004 is stale, active, or reopened
- proof obligations before retrying the idea
```

## Handoff into fixed-point-driver
```md
Use $negative-ledger, then hand off to $fixed-point-driver.
Goal: Map negative evidence first, then drive the selected route to closure.
Constraints:
- treat learnings hits as candidate evidence only
- do not let stale negative evidence veto current work
- append durable new negative evidence through $learnings only when witnessed
```
