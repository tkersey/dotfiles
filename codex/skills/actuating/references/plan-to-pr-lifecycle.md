# Plan-to-PR Lifecycle

`$actuating` owns the end-to-end workflow from a material plan to a shipped PR.

```text
plan source
  -> $st intake / graph audit
  -> execution aperture
  -> $fixed-point-driver implementation loop
  -> per-task proof-carrying completion
  -> full build/lint/test validation
  -> $ship PR publication
```

## Lifecycle boundaries

- `$st` owns durable task graph state.
- `$fixed-point-driver` owns non-trivial implementation and fixed-point loops.
- Language skills own language/toolchain-specific hazards and proof commands.
- `$verification-closure` owns final readiness when a closure gate is material.
- `$ship` owns PR creation/update and proof summary publication.
- `$land` owns merge/land only when the user explicitly asks.

## Completion meaning

A run is complete only when every in-scope task is complete, blocked, deferred by explicit scope, or removed from scope by an evidence-backed graph update, and the branch has current proof suitable for `$ship`.
