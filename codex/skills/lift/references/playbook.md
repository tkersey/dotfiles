# Lift Playbook

## Doctrine

Lift treats performance as a product requirement with a proof obligation. A
change is not an optimization until it has a baseline, bottleneck evidence,
behavior proof, measured after-state, and a guard against regression.

Core doctrine:

- Preserve correctness, safety, and determinism before speed.
- Measure reality, not intuition.
- Optimize the current bottleneck.
- Prefer algorithmic and architectural wins over micro-tuning.
- Keep changes reversible, isolated, and small enough to attribute causality.
- Re-profile after each accepted change because bottlenecks move.

## Performance Contract

Define the contract before editing code.

- **Metric:** latency, throughput, wall time, CPU, RSS, allocation rate, GC pause,
  startup, queue depth, or tail percentile.
- **Target:** user-provided SLO or “improve versus baseline; report delta.” Do not
  invent fake SLOs.
- **Percentile:** p50/p95/p99/max for latency; throughput or wall time for batch;
  RSS/allocs/GC for memory.
- **Workload:** production-like command, dataset, shape, skew, concurrency, and
  warmup.
- **Environment:** hardware, OS, runtime, compiler flags, feature flags, load.
- **Constraints:** correctness, determinism, precision, cost, resource ceiling,
  rollout, compatibility.

## Mandatory Loop

1. **Preflight:** verify tests, workload, environment capture, and correctness
   oracle.
2. **Baseline:** collect stable repeated samples and secondary metrics.
3. **Profile:** identify the bound with evidence: CPU, memory, I/O, lock, queue,
   tail, GC, serialization, or external dependency.
4. **Prove:** capture golden outputs or define an invariant/property/differential
   oracle.
5. **Score:** rank opportunities with Impact x Confidence / Effort.
6. **Patch:** implement one accepted lever only.
7. **Verify:** run correctness and performance again.
8. **Re-profile:** confirm the target bottleneck moved or pick the next scored
   opportunity.
9. **Guard:** add a benchmark, budget, CI check, alert, or documented rollout.
10. **Report:** before/after, evidence, proof, trade-offs, and residual risk.

## Optimization Ladder

Move from high leverage to low leverage.

1. Delete work.
2. Reduce complexity class.
3. Shrink input, precompute, index, or cache.
4. Improve data structure and data layout.
5. Reduce allocations, GC pressure, and working set.
6. Reduce contention, queueing, or coordination.
7. Reduce I/O, serialization, syscalls, and round trips.
8. Reduce tail variance and backpressure failures.
9. Use micro-architecture tactics: branch, cache, SIMD, prefetch, alignment.
10. Tune compiler/runtime: PGO, LTO, JIT warmup, GC knobs, inlining.

## Bottleneck Classification

| Bound | Evidence | First levers |
|---|---|---|
| CPU | hot frames, cycles, low I/O wait | delete work, algorithm, vectorize, branch |
| Memory/cache | LLC misses, high RSS, stalls | locality, layout, prealloc, working-set shrink |
| Allocation/GC | alloc profile, GC pauses | reuse, arenas, pooling, fewer temporaries |
| I/O/network | syscalls, waits, bytes, round trips | batch, buffer, compress, cache, async |
| Lock/contention | mutex/block profile, queue wait | shard, reduce scope, RCU, message passing |
| Tail | p99 spikes, HOL blocking, variance | bound queues, timeouts, cancel, admission |
| Serialization | JSON/codec frames, copy counts | binary formats, streaming, zero-copy, cache |

## Experiment Design

- Use one variable per experiment.
- Keep control variables fixed: input, runtime flags, concurrency, machine, cache
  warmup, build profile, and dependency versions.
- Use enough samples to separate signal from noise.
- Reject or re-run when variance hides the effect.
- Record rejected experiments; they prevent repeated dead ends.

## Round Escalation

- **Round 0:** stabilize measurement and correctness.
- **Round 1:** low-risk wins: indexing, batching, caching, preallocation,
  materialization removal, logging/formatting cleanup.
- **Round 2:** algorithm/data/architecture changes that alter structure but not
  semantics.
- **Round 3:** advanced techniques: mathematical recasts, probabilistic data
  structures, specialized indexes, PGO/LTO/SIMD, cache-oblivious algorithms.

## Stop Conditions

Stop when:

- The next opportunity scores below 2.0 and no user mandate overrides it.
- Remaining wins require higher resource/cost ceilings.
- The bottleneck is outside the system boundary.
- Correctness, determinism, safety, or maintainability risk exceeds benefit.
- Measurement noise makes the result unverifiable.
