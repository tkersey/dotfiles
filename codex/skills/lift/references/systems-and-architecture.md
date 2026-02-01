# Systems and Architecture Tactics

## Table of contents

1. CPU and pipelines
2. Caches and memory hierarchy
3. Data layout and alignment
4. Branch prediction and control flow
5. SIMD and vectorization
6. Allocation and GC pressure
7. Concurrency and contention
8. NUMA and memory locality
9. I/O and syscalls
10. Network and serialization
11. Observability overhead

## 1. CPU and pipelines

- Reduce instruction count in the hottest path.
- Increase instruction-level parallelism by removing dependencies.
- Avoid unpredictable branches in tight loops.

## 2. Caches and memory hierarchy

- Maximize spatial and temporal locality.
- Minimize cache misses and working set size.
- Avoid false sharing across threads.

## 3. Data layout and alignment

- Prefer contiguous buffers over pointer-heavy graphs.
- Use structure-of-arrays for hot numeric loops.
- Align frequently accessed data to cache lines.

## 4. Branch prediction and control flow

- Replace unpredictable branches with table lookups or masks.
- Hoist invariant checks outside loops.
- Flatten hot-path error handling.

## 5. SIMD and vectorization

- Batch similar operations to enable vectorization.
- Prefer fixed-size loops with predictable strides.
- Avoid aliasing that blocks compiler vectorization.

## 6. Allocation and GC pressure

- Reduce short-lived allocations in hot paths.
- Use object pools or arenas when safe and bounded.
- Keep allocation rates below GC threshold triggers.

## 7. Concurrency and contention

- Reduce lock scope and lock frequency.
- Shard by key to reduce contention.
- Avoid global locks on read-heavy paths.
- Use lock-free or wait-free structures when proven safe.

## 8. NUMA and memory locality

- Pin threads to cores when latency matters.
- Keep memory local to the NUMA node that uses it.
- Avoid cross-node memory thrash.

## 9. I/O and syscalls

- Reduce syscalls and context switches.
- Batch I/O and use buffers to amortize overhead.
- Avoid synchronous I/O on latency-critical paths.

## 10. Network and serialization

- Reduce payload size and round trips.
- Prefer binary or compact encodings when safe.
- Avoid redundant serialization and copying.

## 11. Observability overhead

- Measure tracing and logging overhead.
- Sample or aggregate metrics when overhead is high.
- Avoid string formatting in hot paths.
