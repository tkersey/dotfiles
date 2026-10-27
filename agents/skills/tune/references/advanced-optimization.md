# Structural and advanced optimization

Load when the measured workload or scaling behavior warrants a different
formulation, algorithm, or representation. These are first-cycle candidates,
not mandatory later rounds. Recognize structure, establish assumptions, derive
the transformation, then use the simplest native implementation preserving the
required observations. Consult primary algorithm/tool documentation for precise
variants before implementation; names and complexity slogans are not proofs.

Use [software-performance.md](software-performance.md) for the oracle and
[performance.md](../performance.md) for measurement/adjudication. A more elaborate
structure must earn its setup, maintenance, memory, and operational costs.

## Mathematical recastings

| Recognize | Candidate | Obligations before adoption |
|---|---|---|
| Continuous decision variables with a convex feasible problem | Convex optimization; LP/QP where applicable | Establish convexity, feasible domain, solver tolerances, infeasibility behavior, and numerical bounds; do not silently relax integrality |
| Assignment/resource allocation expressible as capacities and costs | Matching or min-cost flow | Preserve capacities, objective, feasibility, integrality assumptions, and tie-breaking; a max-flow-only algorithm does not minimize cost |
| Pairwise Boolean clauses | 2-SAT via implication graph/SCC | Verify every constraint is representable; check assignment as well as satisfiability and handle unconstrained variables |
| Weighted independent-set choice with exchange structure | Matroid greedy | Prove hereditary/exchange properties and the exact weighted objective/weight assumptions; arbitrary independence systems do not suffice |
| Diminishing-return set objective under a supported constraint | Submodular optimization | Establish monotonicity, nonnegativity/normalization and constraint-specific guarantee; an approximation is not unchanged exact behavior |
| Path/closure/dataflow recurrence | Semiring formulation | Identify identities, associativity/distributivity and any closure/idempotence/convergence assumptions; select an algorithm valid for that algebra |

Algebra is useful when it reveals reusable laws, equivalent formulations, or an
implementation that eliminates work. An abstract interface alone is not a speedup.
Respect existing architecture ownership; do not manufacture a new abstraction
layer solely to exhibit a named concept.

## Dynamic programming and sequence problems

| Recognize | Candidate | Preconditions and verification |
|---|---|---|
| Overlapping subproblems / acyclic recurrence | Memoization or topological DP | Complete state key, dependency acyclicity, base cases and reconstruction; include memo storage |
| Search over reachable states | Shortest path on implicit graph | Dijkstra requires nonnegative edge weights; an acyclic graph can use topological relaxation even with negative edges |
| Min/max over affine functions | Convex hull trick or Li Chao tree | Establish slope/query-order assumptions for the chosen variant; handle duplicates, overflow, bounds, and ties |
| Interval DP with monotone optimal split | Knuth optimization | Prove the applicable recurrence and quadrangle/monotonicity conditions; test split bounds against a brute reference |
| Partition DP with monotone argmin | Divide-and-conquer DP optimization | Establish argmin monotonicity for the cost function; do not infer it from a few examples |
| Sequence alignment where full table memory dominates | Hirschberg reconstruction | Preserve scoring and base cases; tie-breaking may change the chosen optimal alignment even when the score matches |
| Repeated subset aggregation | Zeta/Mobius transforms, subset convolution variant | Specify the operation/algebra, transform domain and power-of-two shape; subtraction/inversion must exist when used |

Compare with a simple full-search/table implementation on small exhaustive or
generated cases. Check reconstruction/output identity separately from objective
value. Measure preprocessing and sparse versus dense reachability, not just the
inner recurrence.

## Specialized indexes and dynamic structures

| Recognition | Candidate | Preservation and cost questions |
|---|---|---|
| Many substring queries over stable text | Suffix array + LCP, suffix automaton | Alphabet/Unicode model, construction memory, updates, match intervals and ordering |
| Rank/select/quantile queries on sequences | Wavelet tree/matrix | Alphabet representation, static/dynamic variant, space and output semantics |
| Changing forest links/cuts with path queries | Link-cut tree | Forest invariant, aggregate algebra, lazy updates/reversal, amortized versus tail cost |
| Path queries over a mostly static tree | Heavy-light decomposition | Tree/root semantics, aggregate ordering and update/query mix |
| Sliding min/max | Monotone deque | Expiration/window bounds and tie-breaking when equal values are removed |
| Range updates and aggregates | Segment tree with lazy propagation | Correct action/composition laws, identities, range boundaries and overflow |
| Same key searched across sorted catalogs | Fractional cascading | Stable ordering/cross-links; charge construction and update cost |
| Static known key universe | Minimal perfect hashing | Domain is fixed; verify membership for unknown keys, retain values/key check costs, and do not promise total storage of only hash metadata |

A sophisticated structure can move cost into updates or memory. Test lifecycle,
not only successful queries. Prefer a maintained, suitable implementation over
new low-level machinery when dependency policy and measurements support it.

## Streaming, sketches, and randomized algorithms

Approximation must already be allowed or explicitly authorized with error and
failure bounds. Keep exact verification when the contract requires exact answers.

| Recognition | Candidate | Critical guard |
|---|---|---|
| Expensive authoritative membership lookup | Bloom filter prefilter | Verify positives against the source of truth; preserve freshness and supported insertion/deletion semantics |
| Membership with supported deletion | Cuckoo filter | Handle insertion failure and collisions; deleting an unverified false positive can corrupt membership guarantees |
| Stream frequency estimation | Count-Min sketch | State dimensions, hashing/error assumptions, counter overflow, and update model; negative updates change guarantees |
| Distinct counting under a memory budget | HyperLogLog | State precision/register count, error behavior, hash assumptions, and merge compatibility; not an exact set |
| Approximate neighbor/similarity search | LSH / MinHash with a suitable metric | Measure recall/quality at realistic density and skew; include index/build/transfer costs |
| Uniform sample of unknown-length stream | Reservoir sampling | Validate distribution, sample-size bounds, randomness source and any reproducibility requirement |
| kth value instead of full sort | Quickselect | Preserve selected-value/tie and mutation contracts; expected cost is not a worst-case latency guarantee |

A fixed RNG seed does not make two randomized algorithms observationally equivalent.
Distinguish an exact randomized algorithm (correct answer, random running time)
from a probabilistic/approximate answer. Measure adversarial distributions and
failure probability where they affect the accepted contract.

## Algebraic and graph transformations

| Recognition | Candidate | Conditions / independent oracle |
|---|---|---|
| Dense polynomial or sequence convolution | FFT/NTT | Floating error versus exact modular arithmetic, padding/normalization, root/modulus constraints, coefficient overflow; compare naive convolution |
| Large-index fixed-dimensional linear recurrence | Matrix exponentiation | Correct transition/state, exponent/base cases, semiring and arithmetic; include matrix dimension and multiplication cost |
| XOR constraints | Linear algebra over GF(2), bitsets | Pivot handling for free columns, rank/inconsistency, solution reconstruction; check the original equations |
| Large branching search with reversible transitions | Bidirectional search / meet-in-the-middle | Correct reverse edges/state join, stopping condition and optimality, frontier memory, directed/weighted variants |
| Offline range-query batch with cheap incremental updates | Mo's algorithm | Queries may be reordered internally; restore output order, handle add/remove invariants and update variants |
| Repeated tree path queries amenable to decomposition | Centroid decomposition | Preserve tree/component semantics, aggregation and double-counting rules; charge rebuild/update cost |
| Offline/dynamic connectivity requiring undo | Union-find with rollback | Log every mutation needed for undo; path compression is not free to retain without a compatible rollback scheme |

## Locality, hardware, and amortization

Consider cache-aware tiling, cache-oblivious recursive decomposition, van Emde Boas
layout, vectorization, or native library kernels when bandwidth/locality limits the
workload. State memory model, layout, alignment, base case, aliasing, numerical
semantics, and hardware portability. Recursion alone does not prove cache
optimality; overhead and traversal order can dominate small inputs.

Use potential/accounting arguments to understand amortized costs, then measure
the relevant worst-case/tail behavior. Dynamic arrays, path-compressed union-find,
and splay trees can have expensive individual operations. Do not rule out tuning
because an operation already has a favorable amortized bound.

Before accepting any advanced candidate, verify assumptions against the actual
input domain, run an independent small-instance oracle and representative full
workload, and compare total complexity/maintenance cost to the simplest valid
alternative. Leave unsupported candidates as hypotheses, not prescribed upgrades.
