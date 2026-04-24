# Algorithms and Data Structures

## Complexity-First Thinking

A complexity-class improvement usually dominates local tuning. Start by asking:

- Is the hot path doing repeated work?
- Is there a monotone/sorted structure to exploit?
- Can queries be answered by an index, precomputation, or streaming state?
- Is the exact result required, or is a bounded approximation acceptable?
- Can the workload be partitioned without coordination?

## Tier 1 Patterns

| Pattern | Recognition | Typical win | Proof concern |
|---|---|---|---|
| N+1 -> batch | repeated external calls | fewer round trips | order, retries, errors |
| scan -> hash/index | repeated keyed lookup | O(n) -> O(1)/O(log n) | key equality, order |
| memoization | repeated pure call | avoid recompute | purity, invalidation |
| preallocation | growth in hot loop | fewer allocs | bounds, memory cap |
| stream instead of materialize | large one-pass data | lower RSS | chunk semantics |
| compile regex once | regex in loop | lower CPU/allocs | same flags/pattern |

## Tier 2 Algorithmic Patterns

| Pattern | Use when | Complexity shift |
|---|---|---|
| binary search | sorted or monotone predicate | O(n) -> O(log n) |
| two-pointer | sorted pair/range problem | O(n²) -> O(n) |
| sliding window | fixed/monotone window | O(nk) -> O(n) |
| prefix sums | repeated static range sums | O(n) query -> O(1) |
| Fenwick/segment tree | dynamic range queries | O(n) -> O(log n) |
| heap/top-k | select best k | O(n log n) -> O(n log k) |
| union-find | connectivity/merge queries | near O(1) amortized |
| topological DP | DAG repeated traversal | O(V+E) after ordering |
| Dijkstra/A* | weighted shortest path | guided graph search |

## Tier 3 Structure and Layout Patterns

| Access pattern | Structure |
|---|---|
| point lookup | hash map / perfect hash |
| ordered/range lookup | B-tree / skip list / segment tree |
| prefix lookup | trie / radix tree / FST |
| top-k/min/max | binary heap / pairing heap |
| FIFO/sliding window | deque / ring buffer |
| sparse set ops | hash set / bitset / roaring bitmap |
| mostly-small collections | small-vector / inline array |
| many same-lifetime objects | arena / bump allocator |
| approximate membership | Bloom/Cuckoo/Xor filter |
| distinct counting | HyperLogLog |
| heavy hitters | Count-Min Sketch |

## Locality and Layout

- Prefer ID-indexed arrays over pointer-heavy maps when the key domain permits.
- Store hot fields together and cold fields separately.
- Use SoA for field-wise numeric operations and AoS for whole-record operations.
- Traverse in memory order and reduce random pointer chasing.
- Flatten recursion or graph storage when stack/cache behavior dominates.

## Approximation and Relaxation

Approximation requires explicit acceptance in the contract. Document:

- false-positive/false-negative behavior
- error bound
- memory bound
- fallback authoritative check
- effect on user-visible behavior

## Parallel-Friendly Algorithms

- Partition input into independent chunks.
- Use map/reduce instead of shared mutation.
- Avoid global locks and per-item synchronization.
- Make merge order deterministic if output order is observable.
- Measure overhead; parallelism can regress small workloads.
