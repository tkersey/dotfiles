# Performance Checklists

## Preflight

- [ ] Performance contract defined.
- [ ] Workload command selected.
- [ ] Dataset and environment recorded.
- [ ] Correctness oracle selected.
- [ ] Existing tests or proof command run before changes.
- [ ] Resource/cost ceilings known.
- [ ] Mode selected: measured, unmeasured, or audit.

## Baseline

- [ ] Warmup performed.
- [ ] Enough samples collected.
- [ ] p50/p95/p99/max or throughput/RSS recorded.
- [ ] Raw sample path captured when feasible.
- [ ] Noise floor estimated.
- [ ] Secondary metrics recorded.

## Profile

- [ ] Primary profiler run.
- [ ] Secondary signal captured.
- [ ] Top hot paths or wait points listed.
- [ ] Bound classified.
- [ ] Evidence maps directly to candidate changes.

## Opportunity Matrix

- [ ] Candidates ranked.
- [ ] Impact, confidence, effort scored.
- [ ] Only Score >= 2.0 accepted unless user overrides.
- [ ] Proof burden documented for accepted candidate.

## Behavior Proof

- [ ] Golden outputs, differential tests, property tests, or invariants defined.
- [ ] Ordering and tie-breaking addressed.
- [ ] Floating-point semantics addressed.
- [ ] RNG/time/concurrency determinism addressed.
- [ ] Error handling and edge cases addressed.
- [ ] Correctness command passes after change.

## Implementation

- [ ] One lever only.
- [ ] Minimal reversible diff.
- [ ] No unrelated cleanup or semantic change.
- [ ] Rollback path clear.

## Verification

- [ ] Correctness rerun.
- [ ] Benchmark rerun on same workload.
- [ ] Profile rerun or sufficient targeted confirmation.
- [ ] Secondary regressions checked.
- [ ] Result accepted/rejected based on noise floor.

## Shipping

- [ ] Regression guard added or documented.
- [ ] Report includes baseline, after, delta, confidence, proof, and artifacts.
- [ ] Trade-offs and residual risks documented.
- [ ] `lift_compliance` line included.

## Bound-Specific Quick Checks

### CPU

- [ ] algorithmic complexity reviewed
- [ ] redundant work removed
- [ ] hot loops inspected
- [ ] branch/locality/vectorization considered

### Memory / GC

- [ ] allocation hot sites identified
- [ ] live heap and peak RSS measured
- [ ] reuse/prealloc/arena/pool considered
- [ ] cache bounds checked

### I/O

- [ ] round trips counted
- [ ] bytes and syscalls measured
- [ ] batching/buffering considered
- [ ] retry/error semantics preserved

### Lock / Tail

- [ ] wait time measured
- [ ] queue depths measured
- [ ] saturation checked
- [ ] sharding/backpressure/timeouts considered
