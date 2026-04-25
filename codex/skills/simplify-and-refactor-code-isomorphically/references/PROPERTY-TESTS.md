# Property-Based Tests — the safety net for aggressive refactors

> When you can't enumerate every caller's expectation, encode the contract as a property. A property test fails on any input that violates it — vastly wider coverage than example-based tests.

## Contents

1. [Why property tests are the right tool for refactors](#why-property-tests-are-the-right-tool-for-refactors)
2. [The 12 canonical properties](#the-12-canonical-properties)
3. [Library cheatsheet per language](#library-cheatsheet-per-language)
4. [Template: lock behavior BEFORE refactor](#template-lock-behavior-before-refactor)
5. [Template: cross-check old vs new](#template-cross-check-old-vs-new-the-oracle-pattern)
6. [Shrinking and counterexamples](#shrinking-and-counterexamples)
7. [When NOT to use property tests](#when-not-to-use-property-tests)

---

## Why property tests are the right tool for refactors

Example-based tests say "this input → this output." A refactor that preserves every pinned example may still break behavior on unpinned inputs. Property tests say **"for every input, this relation holds."** They're the only example-free way to check an invariant.

The canonical flow for risky refactors:
1. **Identify** the property the old code satisfies (even if implicitly).
2. **Encode** it as a property test.
3. **Run** it against the old code — must pass (otherwise the property is wrong).
4. **Refactor** — ideally by making the property a direct statement.
5. **Run** the property test against the new code — must still pass.

---

## The 12 canonical properties

| # | Property | Example | Use when |
|---|----------|---------|----------|
| 1 | **Idempotence** | `f(f(x)) == f(x)` | normalization, dedup, canonicalization |
| 2 | **Round-trip / inverse** | `decode(encode(x)) == x` | serialization, compression, encoding |
| 3 | **Determinism** | `f(x) == f(x)` | any pure function; first property to add |
| 4 | **Associativity** | `f(f(a, b), c) == f(a, f(b, c))` | merging, reductions (safe to reorder) |
| 5 | **Commutativity** | `f(a, b) == f(b, a)` | sets, unions (safe to parallelize) |
| 6 | **Monotonicity** | `a ≤ b ⇒ f(a) ≤ f(b)` | pricing, scoring, priority |
| 7 | **Preservation of total** | `sum(split(xs)) == sum(xs)` | batching, sharding, partitioning |
| 8 | **Length / cardinality** | `len(f(xs)) == len(xs)` | map-like ops that shouldn't add/drop items |
| 9 | **Subset / superset** | `set(uniq(xs)) == set(xs)` | set-ops, dedup |
| 10 | **Type narrowing** | `validate(x).is_ok()` for any well-formed input | parsers, boundary validators |
| 11 | **Oracle: new == old** | `f_new(x) == f_old(x)` | the refactor itself — before/after parity |
| 12 | **Invariant preservation** | `pre(x) ⇒ pre(f(x))` for some predicate | state machines, DB consistency |

---

## Library cheatsheet per language

### Rust — `proptest`

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn idempotent_normalize(s in ".*") {
        let a = normalize(&s);
        let b = normalize(&a);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn round_trip_json(v: Value) {
        let s = to_json(&v);
        let back: Value = from_json(&s).unwrap();
        prop_assert_eq!(v, back);
    }

    // Oracle: hand-written reference vs. optimized implementation
    #[test]
    fn fast_matches_reference(xs in prop::collection::vec(any::<i64>(), 0..200)) {
        prop_assert_eq!(sum_fast(&xs), sum_reference(&xs));
    }
}
```

Configure iterations in `proptest-regressions/`:
```ini
# proptest.toml
cases = 1000
max_shrink_iters = 10000
```

### TypeScript — `fast-check`

```typescript
import * as fc from 'fast-check';

test('idempotent normalize', () => {
  fc.assert(fc.property(fc.string(), (s) => {
    const a = normalize(s);
    expect(normalize(a)).toBe(a);
  }));
});

test('parse preserves length', () => {
  fc.assert(fc.property(
    fc.array(fc.integer()),
    (xs) => parse(serialize(xs)).length === xs.length
  ), { numRuns: 1000 });
});
```

### Python — `hypothesis`

```python
from hypothesis import given, strategies as st
from hypothesis.strategies import lists, text, integers

@given(text())
def test_idempotent_normalize(s):
    a = normalize(s)
    assert normalize(a) == a

@given(lists(integers()))
def test_sum_preserved_by_reorder(xs):
    assert sum(reshuffle(xs)) == sum(xs)

# Oracle: reference vs. fast implementation
@given(lists(integers(), max_size=500))
def test_fast_matches_reference(xs):
    assert sum_fast(xs) == sum(xs)
```

Run more cases:
```bash
HYPOTHESIS_PROFILE=ci pytest   # uses @settings(deadline=None, max_examples=1000)
```

### Go — `gopter` (or testing/quick)

```go
import (
    "testing"
    "github.com/leanovate/gopter"
    "github.com/leanovate/gopter/gen"
    "github.com/leanovate/gopter/prop"
)

func TestIdempotent(t *testing.T) {
    parameters := gopter.DefaultTestParameters()
    parameters.MinSuccessfulTests = 1000
    p := gopter.NewProperties(parameters)

    p.Property("normalize is idempotent", prop.ForAll(
        func(s string) bool {
            a := Normalize(s)
            return Normalize(a) == a
        },
        gen.AnyString(),
    ))

    p.TestingRun(t)
}
```

### C++ — `rapidcheck`

```cpp
#include <rapidcheck.h>

int main() {
  rc::check("idempotent normalize", [](std::string s) {
    auto a = normalize(s);
    RC_ASSERT(normalize(a) == a);
  });
}
```

---

## Template: lock behavior BEFORE refactor

Before you touch the code, add these tests. They fail if the refactor drifts behavior.

```python
# BEFORE the refactor: pin the property the OLD code satisfies
@given(st.lists(st.integers()))
def test_sort_property_pre_refactor(xs):
    result = sort_unstable(xs)                  # the current implementation
    # Property 1: same elements
    assert sorted(result) == sorted(xs)
    # Property 2: non-decreasing
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))
    # Property 3: length preserved
    assert len(result) == len(xs)
```

Run these against the old code. If they pass, commit them. Now any refactor must keep them green.

---

## Template: cross-check old vs new (the "oracle" pattern)

When simplifying a complex implementation, keep the old one as a test oracle. The new one is the "faster/cleaner" version; the old one is the reference.

```rust
// tests/test_refactor_oracle.rs
fn compute_old(input: &[i64]) -> i64 {
    // The original 200-line implementation, kept in a test-only module.
    // Don't delete yet — this is your oracle.
    old_impl::compute(input)
}

fn compute_new(input: &[i64]) -> i64 {
    new_impl::compute(input)
}

proptest! {
    #[test]
    fn oracle_match(xs in prop::collection::vec(-1000i64..1000, 0..500)) {
        prop_assert_eq!(compute_old(&xs), compute_new(&xs));
    }
}
```

This is the gold-standard isomorphism test. If it passes across thousands of random inputs, you have very strong evidence that the refactor preserved behavior.

**After N weeks** (once confidence is high and the new code has been in prod), you can delete the old implementation (with user approval, per AGENTS.md).

---

## Shrinking and counterexamples

When a property test fails, the framework shrinks the failing input to a minimal example:

```
proptest: TEST FAILED:
  minimal failing input: xs = [1, 0]
  property: assert parse(serialize(xs)) == xs
```

That minimal example goes into your example-based test suite as a regression test. The property test stays to catch the next variant.

**Read the shrunk counterexample carefully.** It often reveals a class of bugs the refactor exposed:
- "Shrunk to `xs = []`" → you broke the empty case.
- "Shrunk to `xs = [x]` for any x" → you broke the singleton case.
- "Shrunk to `xs = [x, x]`" → you broke the duplicate-element case.

---

## When NOT to use property tests

| Context | Why not |
|---------|---------|
| **I/O-heavy functions** | each run hits real disk/DB; use hypothesis stateful tests, or mock the boundary |
| **Randomness without a seed** | can't reproduce — fix seeding first |
| **Time-dependent code** | inject the clock; otherwise flakes |
| **Functions with very specific preconditions that strategies can't generate** | write 5 example-based tests; property tests will just reject most inputs |
| **UI components** | property-test the props→rendered-HTML, not the UI — that's visual regression |
| **Functions that interact with many modules** | usually a sign that the function is too big; decompose first |

---

## Integration with this skill's loop

In [METHODOLOGY.md §Phase D — Prove](METHODOLOGY.md#phase-d--prove-isomorphism-card):

- If filling the isomorphism card leaves rows as "I don't know", **write property tests for those rows before editing**.
- The property tests become the empirical confirmation of the card.
- If the property fails post-refactor, roll back. The property is telling you the refactor was not isomorphic.

**Metric to track:** property test count in baseline vs. after the skill's pass. A simplification pass that *adds* property tests while removing LOC is doing double duty — stronger guarantees, less code.
