# `$actuating` 2.0 — Frontier Control

## Governing correction

Material execution now requires:

```text
current executable GCR-v1
+ valid AFR-v1 bound to that GCR/artifact/task set
```

A failed/stale graph enters graph-repair mode and cannot degrade into delivery mutation.

## Added

- AFR-v1 counterexample quotient, owner, route, surface budget, and proof DAG.
- ASR-v2 run/ship state.
- ARH-v1 realization handoff.
- SDR-v1-compatible route projection.
- compaction-safe resume packet.
- tiered slice/wave/ship proof cadence.
- conditional read-only frontier/proof/wave specialists.
- deterministic AFR/ASR gates and tests.

## Corrected

- Current `$st` intake sequence replaces deprecated intake-plan usage.
- `update_plan` is exactly one GCR projection rather than substitute state.
- `$actuating`, not `$fixed-point-driver`, owns route selection.
- New observations stop realization and return to frontier.
- ready PR remains default after full closure.
