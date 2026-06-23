# Source Anchors

## Local actuation audit

The supplied 2026-06-23 `$seq` report found:

```text
70 turns
19 compactions
20 failures in 21 st compile aperture attempts
192 update_plan calls
264+ apply_patch calls
63/70 turns patching
0 subagent calls
0 structured decision episodes
repeated full proof lanes
```

Its central evidence was repeated discovery of adjacent `LoadedSessionImage` and continuation/frame validation combinations without a durable whole-frontier artifact.

## Current contracts reviewed

- `$actuating` plan-to-PR contract before this replacement.
- `$st` graph-control contract requiring current GCR-v1 for material projection/execution.
- `$fixed-point-driver` realization-only kernel/RC contract.
- `$accretive-implementer` smallest-sufficient-owned-surface contract.
- `$learnings` inflection-only capture contract.
- `seq 0.3.8` current audit/decision surfaces.

## Design conclusion

The durable task graph already exists.

The missing layer is a thin, GCR-bound domain-frontier artifact—not another task ledger.
