# Example Invocations

## New plan

```text
Use $actuating.

Plan: docs/plan.md

Compile it into canonical $st graph state, require a current GCR, prepare
bounded ASL slices, realize them through bounded execution, run focused/wave/final
proof, and open a ready PR when complete. Do not merge.
```

## Resume

```text
Use $actuating.

Resume the existing .ledger/st/st-plan.jsonl and .ledger/actuating checkpoint.
Verify the current GCR and ASL before mutation. Continue to a ready PR.
```

## Implementation only

```text
Use $actuating for implementation only. Stop after proof-complete graph closure;
do not call $ship.
```
