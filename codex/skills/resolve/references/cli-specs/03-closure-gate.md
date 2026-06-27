# Closure Gate

`resolve-c3 closure-gate --summary SUMMARY --runs RUNS --format json` verifies
that delivery closure is backed by mechanically closed material work.

## Required Evidence

The gate requires a material run row with:

```text
c3_required=true
c3_entered=true
c3_closed=true
compression_state != NONE
batches_total > 0
kernel.accepted=true
potential.strict_progress > 0
delivery_closed=true
terminal_closed=true
closure_gate.status=passed
```

## Blocking Conditions

The gate fails closed when C3 was not entered, compression is absent, the kernel
was not accepted, strict progress is zero, terminal holdout is absent, closure
gate proof is missing, or unresolved orphan/unmapped/wound-specific evidence
remains.

Semantic surface growth is allowed only when the run explicitly rebases the
acceptance horizon.
