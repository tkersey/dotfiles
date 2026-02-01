# Algorithms and Data Structures

## Table of contents

1. Complexity-first thinking
2. Reduce work
3. Reduce input size
4. Precompute and reuse
5. Data structure leverage
6. Locality and access patterns
7. Approximation and relaxation
8. Parallel-friendly algorithms

## 1. Complexity-first thinking

- Prefer algorithmic improvements over micro-optimizations.
- Change O(n^2) to O(n log n) or O(n) whenever possible.
- Measure constants, but never ignore complexity class.

## 2. Reduce work

- Remove redundant computation and repeated parsing.
- Fuse passes when it preserves clarity and correctness.
- Short-circuit early; exploit monotonicity and bounds.
- Cache intermediate results with explicit invalidation rules.

## 3. Reduce input size

- Filter and prune early.
- Use indexing or partitioning to avoid full scans.
- Stream data instead of materializing full collections.

## 4. Precompute and reuse

- Precompute lookup tables for hot paths.
- Use memoization for repeated calls with identical inputs.
- Pre-sort or bucketize to reduce per-request work.

## 5. Data structure leverage

- Use arrays or contiguous buffers for tight loops and locality.
- Use hash maps for sparse lookups; keep load factor reasonable.
- Use heaps or balanced trees for ordered queries and top-k.
- Replace pointer-heavy structures with flat storage when possible.

## 6. Locality and access patterns

- Traverse in memory order to maximize cache hits.
- Use structure-of-arrays for vectorizable data.
- Avoid random pointer chasing in hot paths.

## 7. Approximation and relaxation

- Use approximate algorithms when exactness is not required.
- Trade precision for speed with bounded error and clear limits.
- Use sampling, sketches, or probabilistic data structures when safe.

## 8. Parallel-friendly algorithms

- Prefer data-parallel designs over shared-state designs.
- Use partitioning and reduce patterns to minimize coordination.
- Avoid global locks and per-item synchronization.
