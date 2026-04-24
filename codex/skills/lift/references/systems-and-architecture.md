# Systems and Architecture Tactics

## CPU and Pipelines

- Reduce instruction count on the hottest path.
- Hoist invariant work out of loops.
- Avoid unpredictable branches in tight loops.
- Separate hot fast paths from cold error paths.
- Reduce call overhead only after profiling proves it matters.

## Caches and Memory Hierarchy

- Shrink working set before tuning hardware counters.
- Prefer contiguous traversal and spatial locality.
- Reuse hot data while it remains in cache.
- Avoid random pointer chasing.
- Verify LLC/cache-miss problems with counters.

## Data Layout and Alignment

- Use structure-of-arrays for vectorizable field-wise loops.
- Pack hot fields together and separate cold fields.
- Align or pad only when false sharing or misalignment is measured.
- Prefer flat arrays/IDs over heap-node graphs in hot paths.

## Branch Prediction and Control Flow

- Replace unpredictable branches with table lookup, masks, or split hot/cold
  paths when proof is easy.
- Sort or group data to improve predictability if order is not observable.
- Avoid branch-heavy validation inside tight loops.

## SIMD and Vectorization

- Batch similar operations.
- Use vectorized library routines before hand-written SIMD.
- Keep data aligned/contiguous and avoid aliasing.
- Prove floating-point semantics and tolerances before accepting SIMD math.

## Allocation and GC Pressure

- Remove short-lived allocations in hot paths.
- Reuse buffers with clear lifetime and reset semantics.
- Pool only when construction cost or allocation rate is proven high.
- Avoid unbounded caches and pools.
- Tune GC after reducing allocation rate and live heap.

## Concurrency and Contention

- Reduce lock scope and lock frequency.
- Shard state by key when contention is measured.
- Use bounded queues to enforce backpressure.
- Prefer immutable snapshots for read-heavy workloads.
- Treat lock-free structures as high-proof-burden changes.

## NUMA and Locality

- Pin threads and allocate memory locally only for latency-critical systems where
  counters show cross-node effects.
- Avoid migrating hot state across worker pools.
- Partition state by worker/core where possible.

## I/O and Syscalls

- Batch small reads/writes.
- Use buffered or vectored I/O.
- Reduce context switches and syscalls.
- Avoid synchronous I/O on latency-critical event loops.
- Validate async conversion with tail-latency measurements.

## Network and Serialization

- Reduce payload size, copies, and round trips.
- Cache or prefetch only with correct invalidation.
- Use compact encodings internally when compatibility permits.
- Stream large objects when full materialization is unnecessary.

## Observability Overhead

- Measure logging/tracing/metrics overhead.
- Avoid string formatting on hot paths.
- Sample or aggregate high-cardinality metrics.
- Keep debug instrumentation out of measured release paths unless intentional.
