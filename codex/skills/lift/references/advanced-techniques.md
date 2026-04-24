# Advanced Optimization Techniques

Use these after Round 1 tactics are exhausted and profiling still points to a
structural bottleneck. Advanced techniques carry a higher proof burden.

## Mathematical Recasting

- **Convex optimization:** allocation, scheduling, fitting, or resource planning
  with convex constraints.
- **Submodular greedy:** diminishing returns set selection; useful when a greedy
  approximation is acceptable.
- **Matroid greedy:** greedy is optimal when hereditary and exchange properties
  hold.
- **Min-cost max-flow / assignment:** scheduling, matching, resource allocation.
- **2-SAT / implication graph:** pairwise boolean constraints and configuration
  validity.
- **Semiring generalization:** shortest paths, transitive closure, dataflow, and
  dynamic programs expressed with alternate add/multiply operations.

## Advanced Dynamic Programming

| Technique | Recognition | Shift |
|---|---|---|
| DP as shortest path | implicit DAG with weighted transitions | structured graph search |
| Convex Hull Trick / Li Chao | linear-cost DP recurrence | O(n²) -> O(n log n) |
| Knuth optimization | monotone optimal split + quadrangle inequality | O(n³) -> O(n²) |
| Divide-and-conquer DP | monotone argmin in 1D transition | O(n²) -> O(n log n) |
| Hirschberg | sequence alignment/diff memory bound | O(nm) space -> O(min(n,m)) |

## Exotic Data Structures

- suffix arrays / suffix automata for substring queries
- wavelet trees/matrices for rank/select/quantile queries
- heavy-light decomposition for static tree path queries
- link-cut trees for dynamic tree connectivity
- lazy segment trees for range update/query
- monotone deque for sliding-window min/max
- minimal perfect hashing for static key sets
- roaring bitmaps for compressed set operations

## Streaming and Sublinear Structures

- Bloom/Cuckoo/Xor filters: membership prefiltering.
- Count-Min Sketch: approximate frequencies/heavy hitters.
- HyperLogLog: distinct counting.
- Reservoir sampling: uniform sample of an unknown-length stream.
- Locality-sensitive hashing: approximate nearest neighbor.

Always document false-positive/false-negative behavior and fallback checks.

## Algebraic Techniques

- FFT/NTT convolution for polynomial multiplication and correlation.
- Matrix exponentiation for linear recurrences.
- Zeta/Möbius transforms for subset DP.
- Linear algebra over GF(2) for XOR/toggle systems.

## Graph Optimizations

- bidirectional BFS / meet-in-the-middle for exponential branching
- A* when an admissible heuristic exists
- centroid decomposition for path queries on trees
- offline range queries with Mo's algorithm
- union-find with rollback for undoable connectivity

## Cache-Oblivious and Layout Techniques

- recursive decomposition for locality without fixed block size
- van Emde Boas layout for trees
- tiled/blocked algorithms for matrix and stencil workloads
- flat arrays and ID maps for graph processing

## Runtime/Compiler Escalation

- PGO: representative workload profile -> optimized build.
- LTO: reduce call overhead and improve inlining across compilation units.
- SIMD/vectorized libraries: only after data layout and floating-point proof.
- Custom allocator: only after allocation profile proves general allocator bound.
