# Behavior Proof and Correctness Oracles

## Purpose

A faster implementation is only acceptable if it preserves the required behavior.
Lift requires a behavior proof for every accepted optimization. The proof can be
a golden output, differential test, property test, invariant proof, or explicit
user-approved semantic trade-off.

## Oracle Types

| Oracle | Use when | Notes |
|---|---|---|
| Existing tests | test suite covers behavior | run before and after |
| Golden outputs | deterministic CLI/batch output | compare checksums or diffs |
| Differential run | old and new implementations coexist | compare outputs over corpus |
| Property tests | many generated inputs | assert invariants and edge cases |
| Invariant proof | output is complex or nondeterministic | document ordering, precision, determinism |
| Production canary | system-level only | combine with guardrails and rollback |

## Golden Output Capture

```bash
mkdir -p golden_outputs
for input in test_inputs/*; do
  ./program "$input" > "golden_outputs/$(basename "$input").out"
done
sha256sum golden_outputs/* > golden_checksums.txt
sha256sum -c golden_checksums.txt
```

For nondeterministic outputs, normalize first:

```bash
./program input | jq -S . > golden_outputs/input.normalized.json
```

## Isomorphism Proof Template

```markdown
## Behavior proof: <change>

### What changed
- Before:
- After:
- Performance intent:

### Equivalence argument
- Input domain covered:
- Output domain preserved:
- Ordering preserved:
- Tie-breaking unchanged:
- Floating-point precision/rounding:
- RNG/time/concurrency determinism:
- Error handling and edge cases:
- Resource/cost ceilings unchanged:

### Verification
- Correctness command(s):
- Golden/differential/property check:
- Result:
```

## Proof Obligations by Pattern

| Pattern | Proof obligation |
|---|---|
| N+1 -> batch | Same requests, same effective ordering, same missing/error behavior |
| Linear scan -> HashMap/index | Same key equality; if order observable, stable order reconstructed |
| Memoization/cache | Function purity over key, invalidation, max size/TTL, concurrency safety |
| Preallocation/reuse | Lifetimes safe, no stale data, aliasing controlled |
| Streaming | Same chunk boundaries are not semantically observable or are preserved |
| Parallelization | No races; reduction is associative/commutative or merge order is stable |
| Lock-free/sharded state | Linearizability or acceptable consistency model documented |
| Serialization change | Schema compatibility, encoding limits, canonicalization, backwards support |
| Approximation/sketch | Error bound and false-positive/negative behavior accepted |
| Floating-point/vectorization | Rounding, NaN, signed zero, associativity, and tolerance documented |

## Nondeterminism Controls

- Freeze RNG seeds.
- Stub or capture time.
- Sort outputs if ordering is intentionally unobservable.
- Normalize JSON/object key order.
- Use tolerances for accepted floating-point drift only when allowed.
- Capture concurrency-sensitive edge cases separately.

## Acceptance Gate

Do not report success unless:

- before correctness passed or known failures are explicitly documented
- after correctness passed
- behavior proof addresses ordering, ties, floating point, RNG/time, and errors
- golden/differential/property checks are attached when feasible
