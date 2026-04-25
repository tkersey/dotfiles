# Isomorphism — what "behavior preserved" actually means

> "Behavior" has many axes. A refactor that preserves only the obvious one is not isomorphic.

## Contents

1. [The axes](#the-axes)
2. [Per-axis decision rules](#per-axis-decision-rules)
3. [How to capture goldens per language](#how-to-capture-goldens-per-language)
4. [Property-test patterns that pin behavior](#property-test-patterns-that-pin-behavior)
5. [When you must change behavior to simplify](#when-you-must-change-behavior-to-simplify)
6. [The checklist of last resort](#the-checklist-of-last-resort)

---

## The axes

For every change, ask: does it preserve …

| Axis | Question | Common breaker |
|------|----------|----------------|
| **Output equality** | Same input → same output bytes? | Reordered iteration, different stringification |
| **Output ordering** | Sequence elements emitted in same order? | HashMap iteration replacing Vec, parallel `for` |
| **Tie-breaking** | Equal-rank items resolved the same way? | Replacing stable sort with unstable, hashing over indices |
| **Error semantics** | Same error variants raised under same conditions? | `?` collapsing, `From` impls widening Err type |
| **Error vs panic** | What used to throw still throws (vs. now silently OK)? | `unwrap_or_default()` swallowing |
| **Laziness** | Was lazy → still lazy? | `.collect::<Vec<_>>()` materializing an Iterator |
| **Short-circuit eval** | `a && b` — does `b` still not run when `a` is false? | Refactor to `[a,b].all(…)` evaluates both |
| **Floating-point** | Bit-identical `f64` outputs? | Reordering sums, fused-multiply-add, libm version |
| **Integer overflow** | Same panic/wrap behavior in debug vs release? | `as` cast vs `try_into()` |
| **RNG state** | Same seed → same sequence? | Switching Vec→HashMap reorders RNG draws |
| **Hash iteration** | Iteration order over a HashMap unchanged? | Different hasher, different insertion order |
| **Side effects** | Same logs / metrics / spans / DB writes / file syscalls? | Hoisting code out of a try-block, removing a `tracing::info!` |
| **Side-effect ordering** | Side effects in the same temporal order? | Reordering writes when collapsing two branches |
| **Side-effect cardinality** | Same number of writes/queries? | Batching N+1 collapses N writes into 1 |
| **Async / Future identity** | Same Future graph (cancelation, drop order)? | Replacing `select!` with `join!` changes cancel propagation |
| **Type narrowing** | Discriminant checks still narrow in the same places? | Merging two enums weakens narrowing in callers |
| **Public API** | Same exported symbols, same signatures? | Renaming, deleting, changing visibility |
| **ABI / FFI** | Same struct layout, same calling convention? | Adding a field, changing `repr(C)` |
| **Compile-time guarantees** | Same set of compile errors for misuse? | Loosening generic bounds |
| **React semantics** | Same hook order, same memo keys, same reconciler identity? | Conditional hook, different component identity |
| **Serialization** | Same wire format (JSON keys, field order if it matters)? | `#[serde(rename)]` removed, struct field reordered for serde with field-order semantics |
| **Concurrency** | Same lock acquisition order, no new races? | New shared field that wasn't there before |
| **Resource lifecycle** | Same Drop / __del__ / `defer` order? | Restructuring scopes |
| **Telemetry** | Same span names, same trace IDs propagated? | Removing a span boundary |

If a refactor doesn't touch an axis, mark "N/A" — but only after you've thought about it. Reflexive "N/A" is the most common way bugs ship.

---

## Per-axis decision rules

### Ordering

If callers consume the output as a `Vec` / `Array` / `Iterator`, the order is part of the contract. Even if no test asserts it, downstream code may rely on it.

- Switching `Vec` → `HashSet` for "we don't care about order" requires confirming no caller iterates with a positional assumption.
- Replacing `.iter()` with `.par_iter()` (rayon) or `Promise.all()` is **not** isomorphic on output ordering unless explicitly re-collected with `.collect_into_vec()` preserving input order.

### Error semantics

Common subtle break: callers `match err { Foo(_) => …, _ => … }`. After refactor, errors that used to be `Foo(_)` now arrive as `Bar(_)` (because of a new `From` impl) and silently fall into the `_` arm.

- Always grep callers for `match`/`if let` on the error type.
- TS: callers may catch by `instanceof` — same risk.
- Python: `except FooError` similarly.

### Laziness

Generators and iterators carry latency and memory characteristics. Materialization changes them:

```rust
// Lazy — peak memory ~1 row
fn rows() -> impl Iterator<Item = Row> { … }
// Eager — peak memory ~all rows
fn rows() -> Vec<Row> { … .collect() }
```

If callers `take(10)` then drop, the lazy version did 10 rows of work; the eager version did all of them.

### Short-circuit

```typescript
// Before — second operand only runs if first is null
const value = required ?? compute();
// "Cleaner" — both run, then choose. Different program.
const fallback = compute();
const value = required ?? fallback;
```

Don't move side-effecting calls out of short-circuit positions.

### Floating-point

Even reordering a sum changes the result:

```python
sum_loop  = ((a + b) + c) + d   # left-fold
sum_kahan = sum_kahan_correction(a, b, c, d)   # different bits

# numpy / pandas .sum() may use pairwise summation; map(sum) does straight reduction
```

If the program is consumed by something that hashes its output (e.g., training-data pipelines, content-addressed storage), bit-equality is the contract. Document with property tests.

### React semantics

The most common hidden break:

- **Hook order** — moving a hook into a conditional block. ESLint's `react-hooks/rules-of-hooks` will catch the obvious cases; subtle ones (early `return`) it won't.
- **Component identity** — `{cond ? <A/> : <B/>}` mounts and unmounts. If you unify `A` and `B` into `<C variant=…/>`, callers like `{cond ? <A/> : <B/>}` become `<C variant={cond ? 'a' : 'b'}/>` — now state is *preserved* across the toggle. May or may not be desired.
- **`useMemo` / `useCallback` deps** — when extracting a hook, the dep array's identity may change shape.
- **Suspense boundaries** — extracting code across Suspense boundaries changes loading UX.

### Serialization

`serde_json` is field-order-stable for structs but not for `HashMap<String, Value>`. If your wire format is consumed by anything that compares strings (signature checks, log greps, downstream ETL), preserve key order — `IndexMap`/`BTreeMap` instead of `HashMap`.

---

## How to capture goldens per language

### CLI / pipe-style programs

```bash
# Capture
mkdir -p goldens/{in,out}
for f in goldens/in/*; do
  name=$(basename "$f")
  ./bin "$f" > "goldens/out/$name.stdout" 2> "goldens/out/$name.stderr"
  echo "$?" > "goldens/out/$name.exit"
done
( cd goldens/out && sha256sum * ) > goldens/checksums.txt

# Verify post-refactor
for f in goldens/in/*; do
  name=$(basename "$f")
  diff <(./bin "$f") "goldens/out/$name.stdout" || { echo "DIFF $name"; exit 1; }
done
sha256sum -c goldens/checksums.txt
```

### HTTP services

Use [VCR](https://github.com/kevin1024/vcrpy) (Python), [betamax](https://github.com/SeparateConcerns/betamax) (Ruby), or simple `mitmproxy` recordings. Snapshot 50–100 representative request/response pairs. Verify by replaying and diffing response bodies + status codes + headers (excluding `Date`-like headers).

### React / web UI

```bash
# Playwright snapshot baseline
npx playwright test --update-snapshots
git add tests/__snapshots__/

# Verify
npx playwright test     # zero pixel diff = isomorphic
```

For component-level isolation, use `@storybook/test-runner` or Vitest snapshots:

```typescript
import { render } from '@testing-library/react';
expect(render(<Button variant="primary">go</Button>).asFragment()).toMatchSnapshot();
```

### TUIs

Use [tui-inspector](../../tui-inspector/SKILL.md) — VHS-driven `.cast`/`.png` snapshots compared deterministically.

### Library / data structure work

Property tests via `proptest` (Rust), `hypothesis` (Python), `fast-check` (TS), `quickcheck` (Haskell), `gopter` (Go) pin invariants better than examples can:

```rust
proptest! {
    #[test]
    fn round_trip(input in any::<Order>()) {
        let bytes = serialize(&input);
        let back  = deserialize(&bytes);
        prop_assert_eq!(input, back);
    }

    #[test]
    fn sort_stable(items in prop::collection::vec(any::<Item>(), 0..1000)) {
        let mut a = items.clone(); my_sort(&mut a);
        let mut b = items.clone(); b.sort_by_key(|i| i.key);  // std::sort is stable
        prop_assert_eq!(a, b);
    }
}
```

---

## Property-test patterns that pin behavior

| Property | Encodes |
|----------|---------|
| `f(g(x)) == x` | Round-trip identity (encode/decode) |
| `f(x) == f(x)` | Determinism |
| `sort(f(xs)) == sort(g(xs))` | Set-equality (order doesn't matter) |
| `len(f(xs)) == len(g(xs))` | Cardinality preserved |
| `f(xs ++ ys) == f(xs) ++ f(ys)` | Distributes over concat (suitable for parallelism) |
| `try_from(into(x)) == Ok(x)` | Lossless conversion |
| `partial_order(a,b) == partial_order(f(a), f(b))` | Order-preserving |

Add these **before** the refactor. They become the regression net.

---

## When you must change behavior to simplify

Sometimes the behavior **is** wrong and the refactor fixes it incidentally. That's not isomorphic — it's a bug fix wearing a refactor hat.

**Rule:** Ship the behavior change in its own commit, with its own message ("fix: X used to silently swallow Y"). Then ship the simplification in a separate commit on top, with its isomorphism card honestly marked "now isomorphic to fixed behavior, not original."

Don't bury bug fixes inside refactors. Bisect breaks; reviewers miss them; release notes lie.

---

## The checklist of last resort

If the change is small and you're tempted to skip the card:

```
□ Ran the test suite                                    (most basic)
□ Ran an end-to-end CLI invocation against one input    (catches integration bugs)
□ Diffed stdout against pre-refactor output             (catches output drift)
□ Eyeballed the diff for "I changed a string literal"   (catches log-message drift)
□ Checked git diff has zero unrelated changes           (catches scope creep)
```

If any of those reveal a difference: stop, classify it, decide whether it's intentional, then re-baseline or roll back.
