# Optimization techniques by mechanism

Consult after identifying a limiting mechanism, not as a compulsory code-style
checklist. A candidate must have a recognition condition, applicable assumptions,
a preservation argument, and an experiment that can reject it. Read
[advanced-optimization.md](advanced-optimization.md) whenever changing the problem
formulation or algorithm could outperform local tuning, including the first cycle.

## Eliminate work before accelerating it

Ask whether the operation is necessary for the requested observations. Consider
lazy demand, incremental/delta computation, common-subexpression reuse, fusion,
precomputation, indexing, and changing representation. Count creation/update and
invalidation costs. Preserve effects and demand order: laziness, fusion, and
memoization are not automatically equivalent for effectful or partial operations.
A profile explains the incumbent; it does not forbid a better architecture.

## I/O, network, and storage

| Recognition | Transformation | Preconditions and preservation | Experiment |
|---|---|---|---|
| N+1 fetches or tiny writes | Batch, bulk query, buffer, vectored I/O | Preserve association/order, transactional visibility, errors, limits, and partial-write handling | Round trips/syscalls, wall time, tail latency, error cases |
| Repeated query scans | Appropriate index, query-plan change, materialized view | Matching access pattern; account for update/storage cost and stale reads | Plan/rows scanned plus representative reads and writes |
| Independent waits dominate | Async overlap and bounded concurrency | Effects may overlap; preserve cancellation, dependency order, resource bounds | Throughput/latency at fixed load, queue depth, failure rate |
| Unbounded buffering or overload | Backpressure, bounded queues, streaming | Specify blocking/rejection/drop semantics; do not silently discard work | Saturation, memory, latency, and recovery after overload |
| Repeated transfers | Locality, co-location, compression, reduced payload | Authorization, schema, ordering, CPU/latency tradeoffs | End-to-end bytes, CPU, tail latency, not wire size alone |

A batch can change isolation; one vectored write can still be partial. A global
`Promise.all`/unbounded task list is not a substitute for a concurrency budget.

## Memory, allocation, and representation

| Recognition | Transformation | Preconditions and preservation | Experiment |
|---|---|---|---|
| Repeated short-lived allocations | Buffer reuse, capacity reservation, pooling, arena | Ownership/lifetime and cleanup match; no stale sensitive data or escaped arena references | Allocation count, peak/live bytes, pause time, latency |
| Usually-small collections | Inline/small-buffer representation | Distribution supports it; larger instances and copies still fit budget | Real size distribution, cache behavior, worst case |
| Copies dominate | Borrowing, views, copy-on-write, zero-copy decoding | Lifetimes, aliasing, alignment, bounds/validation, buffer retention | Copied bytes, total memory retained, throughput |
| Field-wise scans/cache misses | AoS-to-SoA, packed indexes, tiling, contiguous storage | Preserve ABI where required; alignment and access/update patterns matter | Cache misses/bandwidth plus whole workload |
| Repeated identical strings | Interning, shared representation | Bounded lifetime, eviction, identity/encoding semantics | Lookup cost and retained memory under varied cardinality |

Removing an allocation can extend another object's lifetime. Pooling may retain
more memory and require synchronization. Compact layouts can trade arithmetic,
updates, and alignment for locality; benchmark the actual access pattern.

## Concurrency and scheduling

Prefer eliminating unnecessary sharing or changing ownership before adding a
more elaborate lock. Consider sharding, immutable snapshots, shorter critical
sections, batching, work-stealing, or a sequential fast path when the profile
justifies it. Read-heavy does not prove an RW lock is faster. Lock-free is not
wait-free and need not improve throughput or tail latency.

State atomicity/linearizability or the weaker accepted contract, memory-ordering
requirements, fairness/progress, reclamation, cancellation, and exception safety.
Test contention, false sharing, skewed keys, oversubscription, and shutdown. For
parallel reductions, require the relevant algebraic laws and numerical semantics;
a mathematical associative operation need not be bitwise associative in floats.

## Algorithms and data structures

| Recognition | Candidate | Required condition / cost to include |
|---|---|---|
| Repeated keyed membership/lookup | Hash map/set or static perfect hash | Expected lookup vs construction/memory; ordering and adversarial collision requirements |
| Ordered/range operations | Balanced tree, sorted array, range index | Update/query ratio, comparison semantics, output size |
| Sorted search / monotone feasibility | Binary or parametric search | Sortedness/monotonicity established; duplicates/bounds handled |
| Pair/range scan with monotone movement | Two pointers, sliding window | Movement cannot skip a required answer; empty/boundary cases |
| Repeated static range sums | Prefix sums | Build/update cost, numeric overflow; dynamic updates need another structure |
| Top-k/min/max scheduling | Heap or selection instead of full sort | Stable ties, ordering requirements, update/removal semantics |
| Repeated graph connectivity | Union-find | Updates supported by the structure; deletions/rollback require variants |
| DAG evaluation / repeated traversal | Topological processing or DP | Cycle handling and dependencies; preserve traversal-visible effects |
| Need existence/first valid result only | Early exit, lazy search | Remaining work has no required effects; preserve which result wins |
| Repeated prefix/substring queries | Trie, automaton, suffix index | Alphabet/encoding, index build/update cost, match/tie semantics |

Asymptotic improvement is a hypothesis until workload scale justifies its setup
and constant factors. Small vectors can outperform hash tables. Amortized costs
do not settle worst-case latency, memory pressure, or adversarial behavior.

## Caching and materialization

Memoize repeated pure computations or stateful computations keyed by all relevant
state/version/authority. Specify capacity, invalidation, freshness, eviction,
concurrency, and failure caching. Test hit/miss ratios, churn, stampedes, stale
entries, key collisions, and tenant isolation. TTL alone is not proof of freshness.
Choose LRU, another eviction policy, or no cache from the observed workload.
Agent prefix and semantic caches additionally use
[agent-performance.md](agent-performance.md#cache-aware-experiments).

## Serialization, strings, and generated code

Choose formats from measured parsing/encoding cost, payload size, schema evolution,
validation, interoperability, and trust boundaries. Do not impose a universal
binary-inside/JSON-outside rule or an unconditional fastest-format ranking.
Reuse buffers, avoid repeated encode/decode cycles, and consider streaming or
validated zero-copy access when lifetimes and alignment permit.

Compile stable regex patterns once only when runtime behavior justifies it;
preserve flags, Unicode semantics, and stateful matcher behavior. Use multi-pattern
automata or SIMD search for measured scanning workloads, with correct tails,
alignment, supported instruction sets, and fallback paths. Vectorization must
preserve numerical and exception semantics. Inspect generated code when it can
resolve a measured compiler/code-layout issue, not as a ritual for every edit.

PGO/LTO, inlining, specialization, and dispatch changes are candidates, not defaults.
Use representative training workloads and holdout measurements; include code-size,
compile-time, instruction-cache, portability, and deployment costs. Keep toolchain
flags and provenance reproducible. Verify current APIs for the selected version
rather than copying snippets from a technique catalog.

## Provenance

Capability coverage was informed by
[extreme-software-optimization](https://github.com/tkersey/jeffreys-skills/tree/main/extreme-software-optimization)
(Skill, Methodology, Techniques, Language-Specific, and Advanced references).
This guide independently restates mechanisms with applicability and preservation
obligations; it does not import the source's universal score cutoff, mandatory
round order, unchecked code samples, or claim that output hashes prove equivalence.
