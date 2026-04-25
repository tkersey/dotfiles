# Rust Refactor Deep Dive

> Rust has a stronger type system and a borrow checker; that changes the shape of safe refactors. This file is the complete Rust-specific playbook.

## Contents

1. [The Rust isomorphism axes](#the-rust-isomorphism-axes)
2. [Borrow-checker-safe refactors](#borrow-checker-safe-refactors)
3. [Lifetimes: widening safely](#lifetimes-widening-safely)
4. [Trait bounds: tightening vs loosening](#trait-bounds-tightening-vs-loosening)
5. [Generic vs dyn vs enum — the decision](#generic-vs-dyn-vs-enum--the-decision)
6. [Derive macro refactors](#derive-macro-refactors)
7. [thiserror / anyhow migration](#thiserror--anyhow-migration)
8. [Async runtime refactors](#async-runtime-refactors)
9. [const generics](#const-generics)
10. [Drop impls — the invisible behavior](#drop-impls--the-invisible-behavior)
11. [Unsafe boundary refactors](#unsafe-boundary-refactors)
12. [Cargo workspace refactors](#cargo-workspace-refactors)

---

## The Rust isomorphism axes

In addition to the general axes in [ISOMORPHISM.md](ISOMORPHISM.md), Rust-specific ones:

| Axis | What changes if you break it |
|------|------------------------------|
| **Borrow checker result** | code that compiled before doesn't |
| **Lifetime variance** | `'static` bounds silently widen or narrow |
| **Trait bound set** | generic callers get stricter/looser errors |
| **Drop order** | RAII cleanup order differs; can cause deadlocks or corrupted state |
| **Panic safety** | a refactor may expose a previously-unreachable panic |
| **`#[repr(...)]` layout** | struct size/alignment changes break FFI |
| **Send / Sync bounds** | thread-boundary compatibility changes |
| **Trait object coercion** | `dyn Trait` vs `&dyn Trait` vs `Box<dyn Trait>` all carry different semantics |
| **`async fn` vs `fn -> impl Future`** | callers see different Send bounds |
| **Macro expansion** | proc-macros produce code that might differ across `derive` combinations |
| **cfg predicates** | a refactor that touches `#[cfg(...)]` changes per-platform compilation |

---

## Borrow-checker-safe refactors

The borrow checker is your oracle. When in doubt, compile.

### Pattern: "split borrow" to avoid self-conflict

```rust
// before — can't compile; borrows `self` twice
fn process(&mut self) {
    for item in &self.items {
        self.handle(item);    // E0502: cannot borrow `self` as mutable (for handle) while immutable (in items)
    }
}

// after — refactor to split the borrow
fn process(&mut self) {
    let items = std::mem::take(&mut self.items);   // move out
    for item in &items {
        self.handle(item);                          // free to borrow
    }
    self.items = items;                             // move back
}

// OR — extract the state you need by value/ref before the loop
fn process(&mut self) {
    let handlers = &self.handlers;
    for item in &self.items {
        handlers.dispatch(item);                    // no self reborrow needed
    }
}
```

### Pattern: extracting a function that takes too many borrows

```rust
// The extracted function tries to borrow 5 fields — often fails the borrow checker
fn helper(&mut self, ...) { /* uses self.a, self.b, self.c, self.d, self.e */ }

// Better — pass the borrows explicitly:
fn helper(a: &A, b: &mut B, c: &C, d: &D, e: &E) { ... }
// call site:
let Self { a, b, c, d, e, .. } = self;   // destructure (with mutability where needed)
helper(a, b, c, d, e);
```

This is the **field-destructuring extract** — Rust-specific, counterintuitive to TypeScript refugees, but standard.

### Isomorphism: borrow-checker changes are behavior axes

If a refactor makes previously-compiling code fail the borrow checker, that's a compile-time behavior change. Fix the borrow issue — don't work around it with `clone()` unless you've accepted the allocation cost.

---

## Lifetimes: widening safely

### Pattern: remove explicit lifetimes where elision works

Rust's lifetime elision rules (2021+ edition) often eliminate explicit annotations. Good for readability — just confirm the elided form is the same.

```rust
// before
fn parse<'a>(s: &'a str) -> &'a str { s.trim() }
// after (elided)
fn parse(s: &str) -> &str { s.trim() }   // same behavior, fewer characters
```

**Confirm with `cargo expand`** (install `cargo-expand`) if the function is non-trivial. Elision rules don't apply to:
- Functions with multiple input lifetimes
- Methods that mix `&self` and explicit arg lifetimes
- Generic lifetimes tied to trait bounds

### Pattern: widen `'static` to a named lifetime

```rust
// before — `'static` is a constraint that limits who can hold an instance
struct Cache { value: &'static str }
// after — parameterize
struct Cache<'a> { value: &'a str }
```

**Audit:** every caller that passed `'static` data still passes. Every caller that wanted non-`'static` couldn't before and can now.

### Pattern: narrow `'static` to something shorter

```rust
// before
struct Ctx { cb: Box<dyn Fn() + Send + 'static> }
// after — does the closure really need 'static? if it's local, no.
struct Ctx<'a> { cb: Box<dyn Fn() + Send + 'a> }
```

Narrowing a lifetime is a behavior change in the type sense — previously-valid callers (holding things that outlived `'a`) won't compile. In practice this is rare; the usual direction is widening to be more permissive.

---

## Trait bounds: tightening vs loosening

### Tightening (adding a bound)

```rust
// before
fn process<T>(t: T) { ... }
// after
fn process<T: Clone + Send>(t: T) { ... }
```

**Effect:** previous callers with non-Clone types now fail to compile. Isomorphism violation at the type-system level.

**When it's OK:** if you verified no callers actually pass non-Clone types (or if the "before" function secretly required clone anyway via a hidden operation).

### Loosening (removing a bound)

```rust
// before
fn process<T: Clone + Send>(t: T) { ... }
// after (if body doesn't actually clone or send)
fn process<T>(t: T) { ... }
```

**Effect:** pure improvement. More callers can use it.

### Rust idiom: "as narrow as needed" trait bounds

```rust
// before — overly broad
fn len_of<T: std::fmt::Debug + Clone + Default>(x: &T) -> usize { ... }
// after — just what's needed
fn len_of<T: AsRef<[u8]>>(x: &T) -> usize { x.as_ref().len() }
```

This is a refactor that's often both a simplification and an isomorphism: the body only needed `AsRef<[u8]>`; the other bounds were copy-pasted cruft.

---

## Generic vs dyn vs enum — the decision

The Rust-specific abstraction choice, roughly analogous to union-type decisions in TS.

| Form | When |
|------|------|
| **Enum** | Closed set of variants, known at compile time. Fastest. |
| **Generic** | Single call-site monomorphization; many types, each specialized. |
| **`dyn Trait`** | Open set, runtime polymorphism. Vtable cost. |
| **`impl Trait` (return position)** | Single type, hidden from callers. Cheap. |

### Refactor direction matrix

| From → To | Meaning | Risks |
|-----------|---------|-------|
| `Box<dyn T>` → `enum` | Closed the set; removed vtable | External crates can't add variants |
| `enum` → `Box<dyn T>` | Opened the set | Runtime cost + need Send/Sync declarations |
| `Box<dyn T>` → `impl T` | Single-type return | Callers can't hold heterogeneous collection |
| Generic → `dyn T` | Runtime dispatch | Codegen smaller, runtime slower |
| `dyn T` → Generic | Compile-time dispatch | Codegen larger, per-call faster |

### The common refactor

`Box<dyn Shape>` for a closed set of shapes → enum. See [MICROPATTERNS.md §M-R5](MICROPATTERNS.md#m-r5--boxdyn-trait-for-closed-set--enum).

**Isomorphism:** for closed sets with no external impls, identical behavior + less indirection. For open sets, you lose extensibility — that's a public API change.

---

## Derive macro refactors

### Adding `#[derive(...)]`

Usually safe:
```rust
// before
struct Point { x: f64, y: f64 }
impl Clone for Point { fn clone(&self) -> Self { Point { x: self.x, y: self.y } } }

// after
#[derive(Clone)]
struct Point { x: f64, y: f64 }
```

**Isomorphism caveat:** if the hand-rolled impl did anything nonstandard (logged, mutated globals, had different semantics), derive is NOT equivalent. Read the hand-rolled body. Every line must be either "the derive does this" or "move to a separate function called explicitly."

### Removing a derive

```rust
// before
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct Id(u64);
// after — wait, did any caller .hash() this?
```

Check: `rg 'Id.*\.hash\(|HashMap<Id|HashSet<Id' -t rust`. If removing `Hash`, confirm no caller uses the type as a map key.

### `#[derive(Default)]` pitfall

Deriving `Default` sets every field to its type's `Default`. If a hand-rolled `Default` set non-zero initial values, derive is wrong:

```rust
// hand-rolled Default
impl Default for Config {
    fn default() -> Self { Config { port: 8080, host: "localhost".into(), ... } }
}

// wrong: derived Default — port becomes 0, host becomes ""
#[derive(Default)]
struct Config { port: u16, host: String }
```

### `#[derive(serde::Serialize, serde::Deserialize)]`

Serialization is part of the API contract. Before changing struct fields (reorder, rename, remove), check:
- `rg '#\[serde(rename'`, `#[serde(alias`, `#[serde(default`, `#[serde(skip_serializing_if`
- Any external consumer of the JSON?

---

## thiserror / anyhow migration

Common simplification: hand-rolled error chain → `thiserror`. See [MICROPATTERNS.md §M-R3](MICROPATTERNS.md#m-r3--hand-rolled-error-chain--thiserror).

### When anyhow is right vs thiserror

- **`anyhow::Result<T>`**: for applications / binaries. Callers want "did it work?" not "which variant?"
- **`thiserror::Error`**: for libraries. Callers want to `match` on specific variants.

Mixed approach: internal fns return `anyhow`, public API returns `thiserror::Error`. When the public API catches from internal, use `.context(...)` on the anyhow err and wrap into a thiserror variant.

### Migration order

1. Add `thiserror` dependency. Pin it.
2. Define `pub enum MyError` with `#[derive(thiserror::Error, Debug)]`.
3. Move existing variants one at a time. Each gets an `#[error("...")]` attribute and a `#[from]` attribute on any inner-error types.
4. Update return types in the public API.
5. Remove hand-rolled `impl Display` / `impl Error` / `impl From`.

Each step is one commit. Each commit has an isomorphism card.

**Behavior change:** the `Display` output usually changes (thiserror uses your `#[error]` format string). If callers parse error messages, that's a break — fix separately.

---

## Async runtime refactors

### The big choice: `tokio` vs `async-std` vs `smol`

Migrating between runtimes is a Tier-3 refactor. Plan; don't do it casually.

### Common within-tokio refactor: `async fn` vs `fn -> impl Future`

```rust
// before
async fn process(x: i32) -> Result<String> { ... }
// equivalent
fn process(x: i32) -> impl Future<Output = Result<String>> { async move { ... } }
```

For a **library** API, `fn -> impl Future` can be nicer because you can add `+ Send` bounds:
```rust
fn process(x: i32) -> impl Future<Output = Result<String>> + Send { async move { ... } }
```

For a **binary**, `async fn` is cleaner.

**Trait methods**: the rules differ. Until recently, `async fn` in traits wasn't stable. Now (Rust 1.75+) it is, but without Send bound, so many traits still use `fn -> Pin<Box<dyn Future<Output = _> + Send>>` (manually) or the `async-trait` macro.

### Removing `async` from a sync-inside function (P39)

```rust
// before
async fn hash(s: &str) -> String {
    // only does sync work
    format!("{:x}", md5::compute(s))
}
// after
fn hash(s: &str) -> String {
    format!("{:x}", md5::compute(s))
}
```

**Isomorphism:** callers change from `.await` to direct call — that's every caller. Verify before landing:
- `rg 'hash\(.*\).await' -t rust -c`
- Count must equal 0 after refactor.

### Hoisting `.await` out of a loop (N+1 elimination)

```rust
// before — sequential
for id in ids {
    let user = db.user(id).await?;
    ...
}
// after — concurrent (bounded)
use futures::stream::{self, StreamExt};
let users: Vec<_> = stream::iter(ids)
    .map(|id| db.user(id))
    .buffer_unordered(10)
    .collect::<Vec<_>>()
    .await;
```

**Isomorphism axes broken:**
- Order: `buffer_unordered` doesn't preserve input order. If callers depend on ordering, use `buffered` instead.
- Error handling: first error still kills the stream; concurrent failures may be racy. `try_buffered` + careful handling.
- DB contention: 10 concurrent queries may overwhelm a small pool.

Ship as a perf `fix:` (or Tier-2 refactor) with measurements.

---

## const generics

Rust has stable const generics (1.51+, with more stable features in 1.75+). Sometimes lets you collapse:

```rust
// before — one fn per size
fn sum_4(xs: &[i32; 4]) -> i32 { xs.iter().sum() }
fn sum_8(xs: &[i32; 8]) -> i32 { xs.iter().sum() }
// after
fn sum<const N: usize>(xs: &[i32; N]) -> i32 { xs.iter().sum() }
```

**Isomorphism:** identical machine code per monomorphization. Pure LOC win when applicable.

**Limitation:** const generics still have restrictions on computation. `const_generic_exprs` is nightly-only.

---

## Drop impls — the invisible behavior

The horror story HS#4 ([REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md#hs4--logsink-panic-flush-behavior-lost)) was a lost `Drop` impl. In Rust, `Drop` is load-bearing for:

- File handles (flush on drop)
- Locks (release on drop)
- Async runtimes (panic on dropped futures in some configs)
- Allocators (return memory on drop)
- Metrics collectors (flush on drop)
- Database pool connections (return to pool on drop)
- `panic::catch_unwind` guards (recover state on drop during panic)

### Refactor safety rule

**Before refactoring any type with an `impl Drop` or that contains types with `Drop` impls:**
```bash
rg 'impl.*Drop.*for <TypeName>|<TypeName>.*: .*(Drop|File|Mutex|RwLock|Connection|Runtime)' -t rust
```

If `Drop` exists, list it in the isomorphism card under "Resource lifecycle" explicitly. Never mark N/A.

### Moving a field out of a `Drop`-impl type

```rust
struct Collector { buf: Vec<Event>, flusher: Flusher }
impl Drop for Collector { fn drop(&mut self) { self.flusher.flush(&self.buf); } }

// Refactor: move `buf` to an internal submodule
// If you don't also move the Drop impl (or keep it working), flush never happens.
```

---

## Unsafe boundary refactors

`unsafe` blocks are load-bearing for reasons that are invisible on the surface. Before touching one:

1. Read the safety comment (`// SAFETY: ...`). If there isn't one, that's a bug; flag it before refactoring.
2. Understand the invariant the unsafe block relies on.
3. If the refactor changes the invariant's reasoning, either update the safety comment or don't refactor.
4. Never merge two unsafe blocks with "looks similar safety comments" — they may rely on different invariants.

### Miri

Run tests under Miri if unsafe is in the refactor surface:
```bash
cargo +nightly miri test
```

Miri catches undefined behavior the regular test suite won't.

---

## Cargo workspace refactors

### Splitting a crate

```bash
# Before: monolithic crate `myapp`
# After:  workspace with myapp-core (lib), myapp-cli (bin), myapp-tools (dev-only)
```

Steps:
1. `cargo new --lib crates/myapp-core`
2. Move files (`git mv` — preserves history).
3. Update `Cargo.toml` dependencies — the tricky part.
4. Inter-crate imports need to change: `use crate::module` → `use myapp_core::module`.
5. Update every workspace-level script, CI, etc.

**This is Tier-3. Plan; multi-agent swarm + beads for coordination.**

### Merging crates

Opposite direction, same caution.

### Changing `edition = "2018"` → `"2021"`

```bash
cargo fix --edition
```

Apply; one commit for the edition bump. Don't combine with refactors.
