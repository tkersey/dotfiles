# Performance Anti-Patterns

## Measurement Failures

- Optimizing without a baseline.
- Reporting only averages for skewed distributions.
- Ignoring warmup, JIT, caches, thermal throttling, or background load.
- Comparing different datasets, machines, flags, or dependency versions.
- Claiming p99 from a tiny sample.
- Treating a win smaller than the noise floor as proven.

## Profiling Failures

- Optimizing code that is not on the hot path.
- Trusting intuition over profiles/traces/counters.
- Using a profiler whose overhead changes the workload without checking.
- Ignoring allocation, lock, I/O, or tail evidence because CPU flamegraphs are
  easier to read.

## Proof Failures

- Changing semantics “while optimizing.”
- Batching without preserving order/error behavior.
- Hashing/indexing when output order was observable.
- Memoizing impure functions or missing invalidation.
- Parallelizing non-associative reductions without deterministic merge.
- Ignoring floating-point, RNG, time, or concurrency nondeterminism.

## Optimization Failures

- Micro-optimizing before algorithmic/data-layout fixes.
- Merging multiple levers so causality cannot be attributed.
- Raising CPU/memory/I/O/external-call cost ceilings without approval.
- Adding unbounded caches or queues.
- Using lock-free code to avoid a simpler sharding/batching fix.
- Hand-writing SIMD before data layout and library options are exhausted.

## Benchmark Failures

- Using unrealistic tiny inputs.
- Benchmarking code the compiler eliminates.
- Measuring setup when setup is not part of the workload, or excluding setup when
  it is.
- Ignoring cold start when users experience cold start.
- Not checking second-order regressions.

## Shipping Failures

- Shipping without a regression guard.
- Failing to document trade-offs and residual risks.
- Failing to keep CLI/docs/install guidance in sync.
- Not recording the evidence needed for future maintainers.
