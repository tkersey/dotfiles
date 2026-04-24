# Optimization Tactics Catalog

Use this catalog after profiling identifies a bound. Every tactic still requires a
score gate and behavior proof.

## Delete Work

- Remove redundant parsing, validation, serialization, logging, or sorting.
- Short-circuit when the result is known.
- Hoist invariant checks out of loops.
- Cache stable expensive results with explicit invalidation.
- Avoid materializing collections that are consumed once.

## Algorithmic Tactics

- Replace repeated scans with indexes or hash maps.
- Use binary search on sorted/monotone data.
- Use two-pointer or sliding-window techniques on ordered sequences.
- Use prefix sums or Fenwick/segment trees for repeated range queries.
- Use heaps or selection algorithms for top-k instead of full sort.
- Use graph reductions, DP, or shortest-path formulations when structure exists.
- Use streaming/sublinear sketches only when approximation is acceptable.

## Data Structure and Layout Tactics

- Prefer contiguous arrays/buffers for hot traversal.
- Use `HashMap` for point lookup and `BTreeMap`/ordered index for ranges.
- Use `VecDeque` for FIFO and heap for priority scheduling.
- Use tries/FSTs for prefix lookups.
- Use structure-of-arrays for vectorizable numeric loops.
- Replace pointer-heavy graphs with flat storage or ID-indexed arrays.
- Use bounded probabilistic filters to avoid expensive authoritative checks.

## Memory and Allocation Tactics

- Pre-size vectors/maps/builders.
- Reuse buffers outside hot loops.
- Use arenas for many same-lifetime allocations.
- Pool expensive objects with clear reset semantics and caps.
- Avoid temporary strings and format calls on hot paths.
- Reduce live heap and working set before tuning GC.
- Cap caches and document eviction policy.

## Concurrency Tactics

- Batch small tasks to amortize scheduling and synchronization.
- Use bounded queues for backpressure.
- Shard locks/state by key.
- Reduce lock scope and lock frequency.
- Prefer immutable snapshots/RCU for read-heavy paths.
- Avoid goroutine/task per tiny item unless overhead is proven acceptable.
- Verify reductions are associative/commutative or merge deterministically.

## I/O and Serialization Tactics

- Eliminate N+1 calls and duplicate requests.
- Batch reads/writes and use buffered or vectored I/O.
- Reduce payload size and copies.
- Stream large payloads rather than materializing full objects.
- Prefer compact/binary encoding internally when schema/compatibility permits.
- Cache external responses only with correct invalidation and bounds.

## Tail-Latency Tactics

- Bound queue length and batch size.
- Add timeouts and cancellation propagation.
- Reduce head-of-line blocking.
- Apply admission control when saturation drives p99.
- Remove convoying locks and long critical sections.
- Separate cold-start and warm steady-state paths.

## Micro-Architecture Tactics

- Improve branch predictability.
- Traverse memory in cache-friendly order.
- Align and pad to avoid false sharing where proven.
- Use SIMD/vectorized libraries for bulk numeric/string operations.
- Reduce dependencies in tight loops.
- Use prefetch only after counters show cache misses and simpler layout wins are
  exhausted.

## Runtime and Compiler Tactics

- Enable release/optimized builds before comparing.
- Use PGO/LTO only after workload and correctness are stable.
- Tune GC only after allocation reductions.
- Avoid reflection/dynamic dispatch/boxing in hot paths.
- Verify runtime flags do not trade unacceptable memory or startup cost.
