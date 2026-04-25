# Performance-Aware Refactor — when this skill intersects with optimization

> Cross-links: [profiling-software-performance](../../profiling-software-performance/SKILL.md) and [extreme-software-optimization](../../extreme-software-optimization/SKILL.md). This skill preserves behavior; those skills change it for speed. This file is how to avoid accidentally entering their territory.

## Contents

1. [The perf-isomorphism axis](#the-perf-isomorphism-axis)
2. [Refactors that typically preserve perf](#refactors-that-typically-preserve-perf)
3. [Refactors that typically change perf (beware)](#refactors-that-typically-change-perf-beware)
4. [The perf smoke-test step](#the-perf-smoke-test-step)
5. [When a refactor reveals a hot path](#when-a-refactor-reveals-a-hot-path)
6. [Property tests for perf invariants](#property-tests-for-perf-invariants)
7. [Handoff to optimization](#handoff-to-optimization)

---

## The perf-isomorphism axis

Strict isomorphism means behavior is preserved. **Perf is not part of strict isomorphism** — a refactor that slows code by 30% while preserving behavior satisfies the skill's definition of success. But in practice:

- A 30% slowdown is a user-observable regression.
- A 100x slowdown is a bug.
- A 3x speedup that "comes for free" from a refactor is welcome but needs accounting.

This skill adds a **perf smoke-test** as an optional verify gate. If you skip it and the refactor regresses perf, you'll discover it in prod.

---

## Refactors that typically preserve perf

Safe-by-default (barring pathological edge cases):

| Pattern | Why perf is roughly preserved |
|---------|--------------------------------|
| Extract constant | zero runtime cost |
| Extract function (monomorphic) | inliner usually inlines back |
| `match Err(e) => Err(e)` → `?` | identical codegen |
| Hand-rolled `impl Clone` → `#[derive(Clone)]` | same ops |
| Generic over identical impls | monomorphized per instantiation; no dispatch cost |
| Inline single-call wrapper | inliner does this anyway |
| `collect()` → iterator passthrough | avoids one intermediate collection (often faster) |
| Type rename | compile-time only |
| Thiserror lift from hand-rolled Display | same string formatting work |
| `if let` → `match` | same codegen |
| `match` → `if let` for single-arm | same codegen |
| Variant `<Button>` component merge | one React component instead of N; usually slight win |

None of these need perf verification beyond a smoke test.

---

## Refactors that typically change perf (beware)

These need explicit attention:

### Always slower (unless audited)

| Pattern | Why slower |
|---------|------------|
| `Box<dyn Trait>` added | heap alloc + vtable dispatch |
| `Rc`/`Arc` added | refcount overhead |
| `Vec::with_capacity(0)` → `Vec::new()` | reallocation on first push |
| Lazy iterator → eager `.collect()` | allocates a Vec |
| Static `regex!` moved inside function body | recompiles on each call (P29) |
| Recursion introduced | stack frame cost + cache-unfriendly |
| Interior mutability via `RefCell` | runtime borrow checking |

### Always faster

| Pattern | Why faster |
|---------|------------|
| Inline single-call wrapper | removes call overhead |
| Hoist regex / config out of loop | amortized compile |
| `Vec<Box<T>>` → `Vec<T>` for small T | cache-friendly; no allocs |
| Closed-set `Box<dyn T>` → `enum` | no vtable |
| N+1 → batch | fewer round-trips |

### Depends on usage pattern

| Pattern | When slower / faster |
|---------|----------------------|
| `HashMap::get(&k)` → `BTreeMap::get(&k)` | hashmap faster for lookup; btreemap for range |
| `&str` → `&[u8]` | depends on Unicode handling |
| `Arc<Mutex<T>>` → `RwLock<T>` | read-heavy: faster; write-heavy: similar or slower |
| `String` → `SmolStr` | depends on string-size distribution |
| Async → sync (P39) | faster if no IO; slower if there was IO |

For these, run `hyperfine --runs 30` before and after to see.

---

## The perf smoke-test step

Add to `verify_isomorphism.sh` for any candidate tagged as "perf-sensitive" (e.g., any change to a loop, hot-path algorithm, or allocator):

```bash
# Phase F-perf: perf smoke test
if command -v hyperfine >/dev/null 2>&1; then
    # Precondition: capture this before editing. Do not stash or checkout over
    # another agent's dirty work during verification.
    test -f refactor/artifacts/<run-id>/perf/main_perf.json || {
        echo "missing pre-edit perf baseline; record BLOCKED in the card"
        exit 1
    }

    # Measure current refactor branch.
    hyperfine --warmup 3 --runs 20 "./bin scenario1" \
      --export-json refactor/artifacts/<run-id>/perf/pr_perf.json

    # Compare mean runtime.
    python3 -c "
import json
m = json.load(open('refactor/artifacts/<run-id>/perf/main_perf.json'))['results'][0]
p = json.load(open('refactor/artifacts/<run-id>/perf/pr_perf.json'))['results'][0]
ratio = p['mean'] / m['mean']
print(f'perf ratio (new/old): {ratio:.2f}x')
if ratio > 1.1:
    print(f'⚠️  REGRESSION: >10% slowdown')
    exit(1)
elif ratio < 0.9:
    print(f'improvement: >10% faster')
"
fi
```

**Thresholds:**
- `ratio ≤ 1.02`: unchanged (within noise)
- `1.02 < ratio ≤ 1.10`: small slowdown; reviewer flag
- `ratio > 1.10`: fail; the refactor regressed perf materially

**Thresholds are conservative** — perf smoke tests are noisy. For real regressions, hand off to [profiling-software-performance](../../profiling-software-performance/SKILL.md) for diagnosis.

### Scenarios matter

`hyperfine './bin scenario1'` measures whatever scenario1 exercises. If the refactor changed a code path scenario1 doesn't hit, perf shows no change — but there might still be regression elsewhere.

Pick scenarios that cover the refactored code. Often this means running the project's existing benchmark suite:
```bash
cargo bench --bench relevant_bench    # Rust
pnpm bench                             # TS (if set up)
pytest --benchmark-only                # Python (pytest-benchmark)
go test -bench=. -benchmem ./...       # Go
```

---

## When a refactor reveals a hot path

Scenario: you're collapsing `sendText` / `sendImage` / `sendFile` into `send(kind, ...)` [TECHNIQUES.md §1.2](TECHNIQUES.md#12-collapse-type-ii-clones-same-shape-different-literals). The refactor works. Verify passes.

Incidentally, while running the perf smoke-test, you notice:
```
hyperfine shows `send` is taking 12ms p95. Messages are tiny.
That's 1000× slower than expected.
```

**Do NOT optimize inline.** That violates:
- R-005 (one lever per commit) — refactor + optimize in same commit
- The boundary between this skill and [extreme-software-optimization](../../extreme-software-optimization/SKILL.md)

**Do this instead:**

1. Finish the refactor commit. Verify green. Land.
2. File a bead: `[perf] send takes 12ms p95 on 1KB messages; investigate`. Label `perf`.
3. Hand off to the profiling skill. Let the bead sit until someone picks it up with profiling discipline.

The refactor shouldn't have *introduced* the slowness (verify proves that), so the slowness was pre-existing. Separate concern, separate PR.

---

## Property tests for perf invariants

Some refactors have perf invariants that deserve pinning:

```rust
proptest! {
    #[test]
    fn batch_is_not_slower_than_serial_above_10_items(
        ids in prop::collection::vec(any::<u32>(), 10..100)
    ) {
        let t_batch = time(|| db.users_batch(&ids));
        let t_serial = time(|| ids.iter().map(|id| db.user(*id)).collect::<Vec<_>>());
        prop_assert!(t_batch <= t_serial * 1.1);  // batch should be ≤ serial (plus 10% noise)
    }
}
```

**Caveat:** these are slow and flaky. Use them for hot paths only. Usually a benchmark suite is better than property tests for perf.

---

## Handoff to optimization

### What a refactor-to-optimization handoff looks like

```markdown
## Refactor pass <run-id> — perf observations

During the verify phase, we observed:

- Scenario `process_large_csv`: p95 unchanged (within 2%).
- Scenario `send_message`: p95 unchanged.
- Scenario `bulk_import`: **PR p95 was 1.17× main's p95** (3.1s → 3.6s).

Analysis: the refactor touched `parse_bulk_import_row` (collapsed into generic
`parse_row<T>`). Monomorphization produced larger instantiated code; likely
icache effects on a hot path.

Action filed: bead `perf-42` — profile `bulk_import` and compare
pre/post-refactor flamegraphs. Hand off to extreme-software-optimization for
the fix.

The refactor itself ships: it's behavior-isomorphic, LOC-reduced by 40, lint-
clean, and the perf regression is isolated to one scenario that the
optimization skill will address.
```

### What the optimization skill will do

Per [extreme-software-optimization/SKILL.md](../../extreme-software-optimization/SKILL.md):
1. Re-capture perf baseline against current state (post-refactor).
2. Profile with `cargo flamegraph` or equivalent.
3. Identify the specific hot frame.
4. Propose a fix (un-monomorphize? inline? restructure?).
5. Apply the fix with its own isomorphism proof.

The two skills compose. Both are one-lever-per-commit. Neither touches the other's domain.

---

## Perf-aware scoring

When scoring a candidate in Phase C, ask:

> Does this candidate cross a perf boundary?

Examples:
- Changing a tight loop's allocation pattern.
- Changing a hash map's hasher.
- Introducing Box / Rc / Arc where there was none.
- Removing Box / Rc / Arc (inlining values).
- Changing async / sync.

If yes → add **+1 to Risk**. Perf regressions are a class of behavior change that standard isomorphism doesn't catch.

Formula reminder:
```
Score = (LOC_saved × Confidence) / Risk
```
A candidate with `(3 × 4) / 2 = 6.0` drops to `12 / 3 = 4.0` — still acceptable but less certain. A candidate with `(2 × 3) / 2 = 3.0` drops to `6 / 3 = 2.0` — right at the threshold.

---

## Common perf-related refactor gotchas

### G-1: `.clone()` added "to simplify lifetimes"

Agent hits a borrow-checker error during refactor. Adds `.clone()`. Keeps going.

In hot paths, `.clone()` accumulates. See `CASS_SEARCHES_RELATED_TO_CONCURRENCY.md`; the fleet's been through this pattern.

**Rule:** if a refactor requires `.clone()`, add it with a comment explaining why the borrow issue forced it. In the card, note "added clone in <fn>". A reviewer can flag if it's in a hot path.

### G-2: `Vec::new()` replaced capacity hint

```rust
// before
let mut out = Vec::with_capacity(N);
// during a "simplification"
let mut out = Vec::new();
// leads to N-log-N reallocations as it grows
```

Capacity hints are load-bearing. Don't strip them.

### G-3: `iter()` → `into_iter()` (or vice versa)

Different ownership semantics; usually caught by the borrow checker, but sometimes both compile. The perf differs: `into_iter()` consumes, `iter()` borrows. In a hot path with expensive drops, `into_iter()` can be slower due to drops per item.

### G-4: `unwrap_or_else` → `unwrap_or`

```rust
x.unwrap_or_else(|| expensive_default())   // default computed only if needed
// vs
x.unwrap_or(expensive_default())            // default computed always
```

Collapsing them swaps semantics. Don't, unless `expensive_default` is actually cheap.

### G-5: Hashmap hasher changed

```rust
use std::collections::HashMap;      // SipHash (DoS-resistant but slow)
use ahash::AHashMap as HashMap;    // fast but not DoS-resistant
```

If the refactor swaps for perf reasons, that's optimization, not refactor. Hand off. Also security-relevant (DoS via hash collisions on SipHash-less maps).

---

## Integration with the skill's loop

### Phase B

Flag candidates in perf-sensitive modules (hot paths, tight loops, per-request critical path) for special attention.

### Phase D

Add a perf axis to the isomorphism card for these candidates:
```
### Perf axis
- Expected perf impact: none / small / moderate / large
- Scenarios to smoke-test: ...
- Benchmark suite to run: cargo bench / pytest --benchmark-only / etc.
```

### Phase F

Run the perf smoke test per above. If it fails, refactor reverts OR lands with a linked perf bead.

### Phase G

In the dashboard, include a "perf delta" row. Trend over months shows whether the skill is net-positive, -neutral, or -negative on perf.
