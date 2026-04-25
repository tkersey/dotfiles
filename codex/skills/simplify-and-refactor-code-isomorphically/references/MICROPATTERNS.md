# Micropatterns — small, specific simplifications with copy-paste code

> A catalog of 80+ named micropatterns. Each is 3–10 LOC of reducible shape with exact before/after snippets. Scan this file with Cmd-F; each pattern has a searchable keyword.

**How to use:** when a duplication scan surfaces a candidate, identify which micropattern(s) apply, then apply them in the order listed. Each micropattern is tagged by language and by abstraction-ladder rung.

## Contents

1. [Rust micropatterns (M-R)](#rust-micropatterns-m-r)
2. [TypeScript / JS micropatterns (M-T)](#typescript--js-micropatterns-m-t)
3. [Python micropatterns (M-P)](#python-micropatterns-m-p)
4. [Go micropatterns (M-G)](#go-micropatterns-m-g)
5. [C++ micropatterns (M-C)](#c-micropatterns-m-c)
6. [Cross-language micropatterns (M-X)](#cross-language-micropatterns-m-x)

---

## Rust micropatterns (M-R)

### M-R1 — `match Err ladder` → `?`

```rust
// before
let f = match open(p) { Ok(f) => f, Err(e) => return Err(e) };
let n = match f.read(&mut buf) { Ok(n) => n, Err(e) => return Err(e) };
// after
let mut f = open(p)?;
let n = f.read(&mut buf)?;
```
Rung 1. Δ: −5 to −8 per ladder.

### M-R2 — hand-rolled `impl PartialEq` → `#[derive(PartialEq)]`

```rust
// before
impl PartialEq for Color {
    fn eq(&self, o: &Self) -> bool { self.r == o.r && self.g == o.g && self.b == o.b }
}
// after
#[derive(PartialEq)]
struct Color { r: u8, g: u8, b: u8 }
```
Rung 1. Δ: −5 per derive. **Audit:** the derived impl compares all fields; hand-rolled may have skipped private ones intentionally.

### M-R3 — hand-rolled error chain → `thiserror`

```rust
// before
#[derive(Debug)] pub enum MyError { Db(DbError), Io(std::io::Error), Parse(String) }
impl std::fmt::Display for MyError { ... 20 lines ... }
impl std::error::Error for MyError { ... 10 lines ... }
impl From<DbError> for MyError { ... }
impl From<std::io::Error> for MyError { ... }
// after
use thiserror::Error;
#[derive(Error, Debug)]
pub enum MyError {
    #[error("db: {0}")]    Db(#[from] DbError),
    #[error("io: {0}")]    Io(#[from] std::io::Error),
    #[error("parse: {0}")] Parse(String),
}
```
Rung 2. Δ: −25 to −50 per error type.

### M-R4 — sibling `fn parse_X` → generic `fn parse<T: FromStr>`

```rust
// before
fn parse_u32(s: &str) -> Result<u32, ParseIntError> { s.parse() }
fn parse_i32(s: &str) -> Result<i32, ParseIntError> { s.parse() }
fn parse_f64(s: &str) -> Result<f64, ParseFloatError> { s.parse() }
// after
fn parse<T: FromStr>(s: &str) -> Result<T, T::Err> { s.parse() }
```
Rung 5. Δ: −3 per sibling. **Audit:** callers that matched on the concrete error now match on `T::Err`.

### M-R5 — `Box<dyn Trait>` for closed set → `enum`

```rust
// before
trait Shape { fn area(&self) -> f64; }
impl Shape for Circle { ... }
impl Shape for Square { ... }
fn render(s: Box<dyn Shape>) { ... }
// after
enum Shape { Circle(Circle), Square(Square) }
impl Shape { fn area(&self) -> f64 { match self { ... } } }
fn render(s: Shape) { ... }
```
Rung 3. Δ: −10; kills vtable. **Audit:** no external crate adds a new `impl Shape`.

### M-R6 — `String` param → `impl AsRef<str>`

```rust
// before
fn greet(name: String) { println!("hi {}", name); }  // forces caller to alloc
// after
fn greet(name: impl AsRef<str>) { println!("hi {}", name.as_ref()); }
```
Rung 1. Δ: 0 (same LOC) but kills callsite `.to_string()` clutter.

### M-R7 — builder chain → `#[derive(Default)]` + struct update

```rust
// before
let req = RequestBuilder::new().url("...").method("POST").timeout(30).build()?;
// after — struct update syntax
let req = Request { url: "...".into(), method: Method::Post, timeout: 30, ..Request::default() };
```
Rung 2. Δ: varies. **When to use:** the builder had no invariants the struct-update loses.

### M-R8 — repeated `.clone()` → restructure ownership

```rust
// before (shows up in vibe-coded Rust)
let a = data.clone();
let b = data.clone();
process(a); process(b);
// after — if process doesn't need ownership
let a = &data;
let b = &data;
process(a); process(b);
```
Rung 1. Δ: 0 LOC but **big runtime savings**. Grep `.clone()` counts per file.

### M-R9 — `Vec::new() + push loop` → `collect`

```rust
// before
let mut out = Vec::new();
for x in xs { if x > 0 { out.push(x * 2); } }
// after
let out: Vec<_> = xs.iter().filter(|&&x| x > 0).map(|x| x * 2).collect();
```
Rung 1. Δ: −3 to −5.

### M-R10 — `unwrap()` in hot path → `expect("why")`

Not a simplification, but a related hygiene pass often done at the same time. Leave unwraps only where truly unreachable; everywhere else, either handle or `.expect("reason")` for the panic message.

```bash
rg '\.unwrap\(\)' -t rust -n | head -40
```

### M-R11 — `trait Foo { fn noop() {} }` blanket extension → plain helper function

```rust
// before — extension trait added by AI "for discoverability"
trait StrExt { fn is_hex(&self) -> bool; }
impl StrExt for str { fn is_hex(&self) -> bool { ... } }
// after — just a function
fn is_hex(s: &str) -> bool { ... }
```
Rung 1. Δ: −5. **When:** the trait has one method used by one caller.

### M-R12 — orphan `mod.rs` files → merge into `parent.rs`

When a module has just `pub use submod::*;` and nothing else, inline it.

---

## TypeScript / JS micropatterns (M-T)

### M-T1 — `<PrimaryButton>` / `<SecondaryButton>` → `<Button variant=…>`

See [TECHNIQUES.md §2.1](TECHNIQUES.md#21-component-variants-ui). Rung 3. Δ: −120 to −200.

### M-T2 — function overload set → generic

```typescript
// before
function get(key: 'name'): string;
function get(key: 'age'): number;
function get(key: 'email'): string;
function get(key: keyof Profile) { return profile[key]; }
// after
function get<K extends keyof Profile>(key: K): Profile[K] { return profile[key]; }
```
Rung 5. Δ: −3 per overload.

### M-T3 — `JSON.parse(JSON.stringify(x))` → `structuredClone(x)`

Node 17+. Preserves Map, Set, Date, RegExp. Faster than round-trip.

### M-T4 — `.map(...).filter(...).map(...)` chain → single pass

```typescript
// before (traverses N× M times)
const out = xs.map(normalize).filter(valid).map(transform);
// after — single pass
const out = xs.reduce<T[]>((acc, x) => {
  const n = normalize(x);
  if (valid(n)) acc.push(transform(n));
  return acc;
}, []);
```
Rung 2. Δ: 0 LOC but eliminates 2 allocations and 2 passes. **When:** on hot paths with large arrays.

### M-T5 — `useEffect(() => fetch, [])` boilerplate → custom hook

See [TECHNIQUES.md §2.2](TECHNIQUES.md#22-custom-hook-react). Rung 1. Δ: −30 to −50.

### M-T6 — `as any` at boundary → `zod.parse`

```typescript
// before
const body: any = JSON.parse(req.body);
const userId = body.user.id;     // type = any, silent crash later
// after
const schema = z.object({ user: z.object({ id: z.string() }) });
const { user: { id: userId } } = schema.parse(JSON.parse(req.body));   // typeof userId === 'string'
```
Rung 2. Δ: +2 LOC at boundary, **−many** downstream `any`s.

### M-T7 — interface merge via discriminated union

```typescript
// before
interface Cat { species: 'cat'; meow(): void; scratching: boolean; }
interface Dog { species: 'dog'; bark(): void; wagging: boolean; }
type Animal = Cat | Dog;
function isCat(a: Animal): a is Cat { return a.species === 'cat'; }
// after (cleanup) — use the discriminant
function act(a: Animal) {
  switch (a.species) {
    case 'cat': a.meow(); break;   // narrowed automatically
    case 'dog': a.bark(); break;
  }
}
```
Rung 3. Δ: remove `isCat`/`isDog` narrower helpers when the switch does narrowing.

### M-T8 — `Object.keys().map()` → `Object.entries().map()`

```typescript
// before
Object.keys(obj).map(k => [k, obj[k]]).filter(...).map(([k,v]) => ...);
// after
Object.entries(obj).filter(...).map(([k, v]) => ...);
```
Rung 1. Δ: −1 LOC, eliminates `obj[k]` lookup.

### M-T9 — `setState(s => ({ ...s, x: v }))` → `useReducer` when many

When a component has 5+ setState calls that all touch the same object, switch to `useReducer`. Δ: small at 5 calls, positive at 15+.

### M-T10 — prop drilling → context (carefully)

See [VIBE-CODED-PATHOLOGIES.md §P17](VIBE-CODED-PATHOLOGIES.md#p17--prop-drilling-5-levels-deep-for-a-singleton). Rung 3. Audit re-render implications.

### M-T11 — `import _ from 'lodash'` → native ES

```typescript
// before — 70 KB gzip for _.uniq + _.groupBy
import _ from 'lodash';
_.uniq(xs);
// after
[...new Set(xs)];
```
Rung 1. Δ: a few LOC; **huge bundle savings** for frontends.

### M-T12 — `async function returning Promise<T | null>` → `Result<T, E>`

```typescript
// before
async function getUser(id: string): Promise<User | null> { ... }
// after (neverthrow, or Rust-style Result)
import { ok, err, Result } from 'neverthrow';
async function getUser(id: string): Promise<Result<User, GetUserError>> { ... }
```
Rung 2. Δ: small LOC; callers now distinguish "not found" from "error". **Behavior change** — ship separately.

### M-T13 — barrel `index.ts` depth → flat imports

When `export * from './a'` in `index.ts` recurses 3+ levels deep, delete intermediate barrels. Named imports from deep paths are clearer in IDE.

---

## Python micropatterns (M-P)

### M-P1 — `try / finally` cleanup → `@contextmanager`

See [TECHNIQUES.md §2.5](TECHNIQUES.md#25-hoist-tryfinally-with-a-context-manager--raii). Rung 1. Δ: −3 per site − helper.

### M-P2 — class with only `__init__` → `@dataclass`

```python
# before
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
# after
from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float
```
Rung 1. Δ: −5 to −15 per class. Bonus: `slots=True` reduces memory, `frozen=True` makes hashable.

### M-P3 — `if/elif` on type → `match` (3.10+) or `singledispatch`

```python
# before
if isinstance(x, int):     handle_int(x)
elif isinstance(x, str):   handle_str(x)
elif isinstance(x, dict):  handle_dict(x)
else:                      raise TypeError
# after (3.10+)
match x:
    case int():    handle_int(x)
    case str():    handle_str(x)
    case dict():   handle_dict(x)
    case _:        raise TypeError
```
Rung 2. Δ: small LOC but exhaustive-like patterns.

### M-P4 — `for ... append` → comprehension

See SKILL.md Tier 1. Rung 1. Δ: −3.

### M-P5 — Dict-of-dicts record → `TypedDict` / `dataclass`

```python
# before
user = {'id': 'u1', 'email': 'a@b.com', 'created_at': dt.now()}
def email(u): return u['email']   # dict access, no typing
# after
from typing import TypedDict
class User(TypedDict): id: str; email: str; created_at: datetime
def email(u: User) -> str: return u['email']
```
Rung 1. Δ: +2 LOC at type def, **much stronger typing**.

### M-P6 — manual `__eq__ / __hash__` → `@dataclass(eq=True, frozen=True)`

Δ: −10 per class.

### M-P7 — `pd.DataFrame.iterrows()` → vectorize

```python
# before — slow, wrong types
for i, row in df.iterrows():
    df.at[i, 'x2'] = row['x'] * 2
# after
df['x2'] = df['x'] * 2
```
Rung 1. Δ: −3 LOC; **100× speedup** is typical.

### M-P8 — `logger.info(f"{x}")` f-string → lazy `%` format

When log level is off in prod, f-strings still evaluate. `logger.info("foo %s", x)` defers formatting.

### M-P9 — mutable default argument bug

```python
# before — SHARED across calls
def make(items=[]):
    items.append(1)
    return items
# after
def make(items=None):
    if items is None: items = []
    ...
```
Not a simplification — a **bug fix**. Often surfaces during refactor scans.

### M-P10 — `assert` in production code → explicit raise

`python -O` strips `assert`. If the assert is load-bearing, convert to `if not cond: raise ...`.

---

## Go micropatterns (M-G)

### M-G1 — `Max/Min/Clamp` per type → generic

See [TECHNIQUES.md §2.4](TECHNIQUES.md#24-generic-over-identical-impls). Rung 5. Δ: −15.

### M-G2 — per-handler logger embed → middleware

```go
// before — every handler:
func HandleUser(w http.ResponseWriter, r *http.Request) {
    log.Printf("[%s] %s %s", reqID, r.Method, r.URL)
    defer log.Printf("[%s] done", reqID)
    // ...
}
// after — middleware:
func Logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        reqID := uuid.New().String()
        log.Printf("[%s] %s %s", reqID, r.Method, r.URL)
        next.ServeHTTP(w, r)
        log.Printf("[%s] done", reqID)
    })
}
```
Rung 2. Δ: −4 per handler.

### M-G3 — `for i := 0; i < len(s); i++ { s[i] }` → `for _, v := range s`

Rung 1. Δ: 0 LOC; clearer. **Audit:** if code mutates `s[i]`, keep the indexed form.

### M-G4 — concrete types for interface where only one impl

If `interface X { ... }` has exactly one implementor and no tests mock it, delete the interface. Callers take the concrete type.
Rung 1. Δ: −5 to −15 per interface.

### M-G5 — repeated error format → `%w` wrap

```go
// before
return fmt.Errorf("failed to get user %s: %s", id, err.Error())
// after
return fmt.Errorf("failed to get user %s: %w", id, err)
```
Rung 1. Δ: 0 LOC; preserves error chain for `errors.Is`/`errors.As`.

### M-G6 — table-driven tests

See [TECHNIQUES.md §Test-suite simplification](TECHNIQUES.md#test-suite-simplification). Rung 1. Δ: −50 to −200.

### M-G7 — `interface{}` → `any` (style only, 1.18+)

```go
func Process(x interface{}) { ... }  // -> func Process(x any)
```
Rung 0. Δ: 0; cosmetic. Skip if mixed with actual generic refactor.

---

## C++ micropatterns (M-C)

### M-C1 — raw `new`/`delete` → `std::unique_ptr` + `std::make_unique`

Rung 2. Δ: kills leaks; −3 LOC per pair.

### M-C2 — closed class hierarchy → `std::variant` + `std::visit`

Rung 3. Δ: −50. See [TECHNIQUES.md §2.3](TECHNIQUES.md#23-replace-inheritance-hierarchy-with-match--enum).

### M-C3 — `for (size_t i = 0; i < v.size(); ++i) v[i]` → range-for

Rung 1. Δ: 0 LOC; fewer off-by-one errors.

### M-C4 — `typedef struct X X;` → `using X = struct X;` or drop in C++

Rung 1. Δ: −1 per.

### M-C5 — SFINAE → `concepts` (C++20)

```cpp
// before — 10 lines of SFINAE
template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>
T double_it(T x) { return x * 2; }
// after
template<std::integral T>
T double_it(T x) { return x * 2; }
```
Rung 5. Δ: −10 per SFINAE block.

### M-C6 — hand-rolled visitor → `std::visit`

Rung 3. Δ: −30 per visitor family.

### M-C7 — C-style array → `std::span` (C++20) or `std::array`

Rung 1. Δ: eliminates length bookkeeping.

---

## Cross-language micropatterns (M-X)

### M-X1 — magic number → named constant at ≥3 sites

```rust
const BLOCK_SIZE: usize = 16;
```
Rung 1. Δ: small but clarity-multiplying.

### M-X2 — dead feature flag → remove the branch

```
if OLD_PATH_ENABLED { legacy() } else { new_path() }
→
new_path()
```
See [VIBE-CODED-PATHOLOGIES.md §P6](VIBE-CODED-PATHOLOGIES.md#p6--dead-feature-flags-behind-shipped-features). Rung 1. Δ: −10 to −30 per flag.

### M-X3 — pass-through wrapper → inline at sole callsite

See [VIBE-CODED-PATHOLOGIES.md §P8](VIBE-CODED-PATHOLOGIES.md#p8--helper-that-calls-itself-with-one-wrapper-per-caller). Rung 1. Δ: −5 per wrapper.

### M-X4 — config drift → single typed source

See [VIBE-CODED-PATHOLOGIES.md §P20](VIBE-CODED-PATHOLOGIES.md#p20--config-drift-between-files). Rung 2. Δ: varies.

### M-X5 — repeated validation → decorator / middleware / parser

All languages have this: N handlers each do the same 5 validation steps. Lift once.

### M-X6 — stringly-typed enum → real enum

```typescript
// before
function setState(s: 'idle' | 'pending' | 'success' | 'error') { ... }
// worse — not unioned, just a plain string
function setState(s: string) { if (!KNOWN.includes(s)) throw ... ; }
// after — either of the above but typed, with an exhaustive switch
```
Rung 2. Δ: small LOC; **big correctness** from exhaustiveness checking.

### M-X7 — copy-pasted test fixtures → factory

```python
def make_user(**overrides):
    return {**DEFAULT_USER, **overrides}

# callers
u = make_user(email='test@example.com')
```
Rung 1. Δ: −10 per test.

### M-X8 — stale deprecated function + new one → kill the deprecated

Per AGENTS.md, no backwards compat in early development. If the deprecated function has no external consumers, remove (after user permission).

### M-X9 — repeated log format → structured logging

```rust
// before
info!("user={} action={} status=ok", id, action);
info!("user={} action={} status=ok", id2, action2);
// after
info!(user = %id, action = %action, "request ok");
```
Rung 1. Δ: 0 LOC; huge downstream savings in log parsing.

### M-X10 — `if x == null return ...; if x.field == null return ...; ...` → early return + validator

```typescript
// before
function do(x) {
  if (x == null) return null;
  if (x.a == null) return null;
  if (x.b == null) return null;
  return x.a + x.b;
}
// after — validate once, narrow downstream
function do(x: { a: number; b: number }) {
  return x.a + x.b;
}
// caller uses the validator
```
Rung 2. Δ: −3 per null-check ladder.

---

## How to cite a micropattern in a refactor commit

```
refactor(users): M-T2 + M-T6 — function overload set and boundary validators

Apply M-T2: replace 4 `get` overloads with a single generic.
Apply M-T6: replace `as any` at POST /users handler with zod validator.

[isomorphism card … ]

LOC: -37. Tests: unchanged. Bundle: -3.1 KB gz.
```

The micropattern IDs make later mining (via cass) straightforward: `cass search "M-T2" --robot --limit 5` finds recent sessions that applied this specific collapse without opening the TUI.
