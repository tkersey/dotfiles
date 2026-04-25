# Advanced Micropatterns (M41-M80)

> Extends [MICROPATTERNS.md](MICROPATTERNS.md) with 40 additional named collapses. Same format: ID, shape, before/after, ladder rung, Δ LOC, isomorphism note. These are the second-tier patterns — less universally applicable than M1-M40 but high-impact when they match.

## Contents

1. [Advanced Rust (M-R13 to M-R25)](#advanced-rust-m-r13-to-m-r25)
2. [Advanced TypeScript / React (M-T14 to M-T25)](#advanced-typescript--react-m-t14-to-m-t25)
3. [Advanced Python (M-P11 to M-P20)](#advanced-python-m-p11-to-m-p20)
4. [Advanced Go (M-G8 to M-G15)](#advanced-go-m-g8-to-m-g15)
5. [Advanced C++ (M-C8 to M-C15)](#advanced-c-m-c8-to-m-c15)
6. [Advanced cross-language (M-X11 to M-X20)](#advanced-cross-language-m-x11-to-m-x20)

---

## Advanced Rust (M-R13 to M-R25)

### M-R13 — `Result<Result<T, E1>, E2>` → `Result<T, CombinedError>`

```rust
// before
fn parse_and_validate(s: &str) -> Result<Result<u32, ValidationError>, ParseError> {
    let n = s.parse::<u32>()?;      // ParseError
    Ok(validate(n))                  // ValidationError
}

// after
#[derive(Debug, Error)]
enum ParseOrValidateError {
    #[error("parse: {0}")]    Parse(#[from] std::num::ParseIntError),
    #[error("validate: {0}")] Validate(#[from] ValidationError),
}
fn parse_and_validate(s: &str) -> Result<u32, ParseOrValidateError> {
    let n = s.parse::<u32>()?;
    Ok(validate(n)?)
}
```

Rung 2. Δ: -3; much cleaner callers.

### M-R14 — Manual `Iterator::next` impl → `std::iter::from_fn`

```rust
// before
struct Counter { n: u32, max: u32 }
impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<u32> { if self.n < self.max { self.n += 1; Some(self.n) } else { None } }
}

// after (when you don't need the type to be nameable)
fn counter(max: u32) -> impl Iterator<Item = u32> {
    let mut n = 0;
    std::iter::from_fn(move || if n < max { n += 1; Some(n) } else { None })
}
```

Rung 1. Δ: -5 to -10.

### M-R15 — `.map(...).unwrap_or_default()` → `.map_or_default(...)`

Nightly-only; if stable: `.map(...).unwrap_or_default()` is idiomatic.
```rust
x.and_then(|x| x.parse::<u32>().ok()).unwrap_or(0)
// hoist to one match
match x.and_then(|s| s.parse::<u32>().ok()) { Some(n) => n, None => 0 }
```

### M-R16 — `Option<Option<T>>` → `Option<T>` via `.flatten()`

```rust
// before
let x: Option<Option<u32>> = hash.get(&k).map(|v| v.parse().ok());
let x: Option<u32> = x.flatten();
// more idiomatic: .and_then
let x: Option<u32> = hash.get(&k).and_then(|v| v.parse().ok());
```

Rung 1. Δ: -1.

### M-R17 — Hand-rolled `From` tree → `thiserror` `#[from]`

See M-R3 for the full migration. Subpattern: individual `impl From<X> for MyError` blocks → `#[from]` attributes.

### M-R18 — Manual builder → `bon` / `typed-builder` macro

```rust
// before — 50 LOC builder
struct Config { host: String, port: u16, retries: u32 }
impl Config { /* builder with required+optional fields */ }

// after
#[derive(bon::Builder)]
struct Config {
    host: String,
    port: u16,
    #[builder(default = 3)] retries: u32,
}

let c = Config::builder().host("x").port(80).build();
```

Rung 2. Δ: -40+ per builder.

### M-R19 — `Vec<T>` wrapper with 5 delegating methods → `Deref` + newtype

```rust
// before
struct Users(Vec<User>);
impl Users {
    pub fn len(&self) -> usize { self.0.len() }
    pub fn is_empty(&self) -> bool { self.0.is_empty() }
    pub fn iter(&self) -> std::slice::Iter<'_, User> { self.0.iter() }
    pub fn push(&mut self, u: User) { self.0.push(u); }
    // ...
}

// after
struct Users(Vec<User>);
impl std::ops::Deref for Users { type Target = [User]; fn deref(&self) -> &[User] { &self.0 } }
impl std::ops::DerefMut for Users { fn deref_mut(&mut self) -> &mut [User] { &mut self.0 } }
// immutable methods from Vec now accessible on Users; Deref<Target=Vec<T>> if push needed
```

Rung 2. Δ: -20. **Caution:** `Deref<Target=Vec<T>>` leaks all Vec methods including push; may widen public API more than wanted.

### M-R20 — `if let Some(x) = opt { x.method() }` → `opt.inspect(|x| x.method())`

Rust 1.80+:
```rust
// before
if let Some(x) = opt { log::info!("got {}", x); }
// after
opt.inspect(|x| log::info!("got {}", x));
```

Rung 1. Δ: -1; clearer intent.

### M-R21 — String concatenation chain → `format!`

```rust
// before
let url = "https://api.example.com/users/".to_string() + &id + "?mode=" + mode + "&v=" + &version;
// after
let url = format!("https://api.example.com/users/{id}?mode={mode}&v={version}");
```

Rung 1. Δ: minor; clearer.

### M-R22 — `Vec::new(); for { vec.push(...) }` → iterator `collect`

Covered in MICROPATTERNS M-R9; emphasized here because it's the single most common Rust collapse pattern.

### M-R23 — Redundant borrow chain `&(*x)` or `&*x` in method calls

```rust
// before — over-explicit
some_fn(&*some_box);
// after — auto-deref
some_fn(&some_box);
```

Rung 0. Δ: 0 LOC; clarity.

### M-R24 — `matches!(..., variant)` instead of `if let`

```rust
// before
let is_active = match status { Status::Active(_) => true, _ => false };
// after
let is_active = matches!(status, Status::Active(_));
```

Rung 1. Δ: -3 lines.

### M-R25 — Explicit `impl Future` boxing → `async fn` (where stable)

```rust
// before
fn fetch_user(id: u32) -> Pin<Box<dyn Future<Output = User> + Send + '_>> {
    Box::pin(async move { /* ... */ })
}
// after (Rust 1.75+ for traits, immediately for free fns)
async fn fetch_user(id: u32) -> User { /* ... */ }
```

Rung 1. Δ: -3. See [RUST-DEEP.md](RUST-DEEP.md) §"async fn vs impl Future" for trait-method nuances.

---

## Advanced TypeScript / React (M-T14 to M-T25)

### M-T14 — `.reduce` with accumulator object → `Object.fromEntries` + map

```typescript
// before
const byId = items.reduce((acc, item) => ({ ...acc, [item.id]: item }), {} as Record<string, Item>);
// after
const byId = Object.fromEntries(items.map(item => [item.id, item]));
```

Rung 1. Δ: -1 line; clearer; avoids spread-in-reduce quadratic performance.

### M-T15 — `useState` with initial fetcher → `useState(() => fn())`

```typescript
// before — fn runs every render, but setState ignores result after first
const [expensive, setExpensive] = useState(computeExpensive());
// after — fn runs once
const [expensive, setExpensive] = useState(() => computeExpensive());
```

Rung 1. Δ: 0 LOC; significant perf.

### M-T16 — `useCallback` + `useEffect` chain for derived data → `useMemo`

```tsx
// before
const [filtered, setFiltered] = useState<Item[]>([]);
useEffect(() => { setFiltered(items.filter(x => x.active)); }, [items]);
// after
const filtered = useMemo(() => items.filter(x => x.active), [items]);
```

Rung 1. Δ: -3; eliminates a render pass. See VIBE-CODED V-R3.

### M-T17 — `JSX.Element` → `React.ReactNode` for prop types

```tsx
// before
interface Props { children: JSX.Element }   // rejects strings, arrays, fragments
// after
interface Props { children: React.ReactNode }  // accepts all valid children
```

Rung 1. Δ: 0 LOC; more permissive correctly.

### M-T18 — `as const` to narrow literal types

```typescript
// before
const VARIANTS = ['primary', 'danger'];   // type: string[]
type Variant = typeof VARIANTS[number];    // type: string (too wide!)
// after
const VARIANTS = ['primary', 'danger'] as const;   // type: readonly ['primary', 'danger']
type Variant = typeof VARIANTS[number];             // type: 'primary' | 'danger'
```

Rung 1. Δ: +1 char (`as const`); huge correctness win.

### M-T19 — Class component → functional with hooks

Largely a 2020s cleanup if legacy class components remain:
```tsx
// before
class UserProfile extends React.Component<Props, State> {
    state = { ... };
    componentDidMount() { ... }
    render() { return <div>{this.state.x}</div>; }
}
// after
function UserProfile({ ... }: Props) {
    const [x, setX] = useState(...);
    useEffect(() => { ... }, []);
    return <div>{x}</div>;
}
```

Rung 3. Δ: varies. **Isomorphism concerns:** `this.setState` coalescing semantics vs `useState`; componentDidUpdate → useEffect dep array mapping. See [REACT-DEEP.md](REACT-DEEP.md).

### M-T20 — `forEach` + mutate → `map`/`filter`/`reduce`

```typescript
// before
const out: number[] = [];
xs.forEach(x => { if (x > 0) out.push(x * 2); });
// after
const out = xs.filter(x => x > 0).map(x => x * 2);
```

Rung 1. Δ: -1 line; clearer.

### M-T21 — Mutually-exclusive props via discriminated union

```typescript
// before — nothing prevents both onSuccess and onError from being set
interface Props { loading?: boolean; data?: Data; error?: Error }
// after
type Props =
  | { loading: true }
  | { loading?: false; data: Data; error?: never }
  | { loading?: false; data?: never; error: Error };
```

Rung 3. Δ: varies; encodes invariants callers otherwise must maintain.

### M-T22 — Custom hook that wraps a store call (Zustand/Redux)

```tsx
// before — every consumer calls the store directly
function UserBadge() {
  const user = useAppStore(s => s.user);
  const isAdmin = useAppStore(s => s.user?.role === 'admin');
  ...
}
// after
function useCurrentUser() {
  return useAppStore(s => s.user);
}
function useIsAdmin() {
  return useAppStore(s => s.user?.role === 'admin');
}
```

Rung 1. Δ: moderate; encapsulates selector logic; prevents drift.

### M-T23 — `zod.object({})` with manual parsing at each endpoint → shared schema

```typescript
// before — every handler defines its own shape
app.post('/user', (req) => { const body = z.object({name:z.string(), email:z.string()}).parse(req.body); ... });
app.put('/user',  (req) => { const body = z.object({name:z.string(), email:z.string()}).parse(req.body); ... });
// after
const userInput = z.object({ name: z.string(), email: z.string() });
app.post('/user', (req) => userInput.parse(req.body));
app.put('/user',  (req) => userInput.parse(req.body));
```

Rung 1. Δ: -N (N handlers).

### M-T24 — Replace `Record<string, unknown>` with precise types

```typescript
// before
function processConfig(config: Record<string, unknown>) {
    // downstream: lots of type assertions / checks
}
// after — define the type
interface Config { host: string; port: number; debug: boolean }
function processConfig(config: Config) { /* typed downstream */ }
```

Rung 2. Δ: varies; enormous downstream simplification.

### M-T25 — Collapse two similar hooks via generic

```typescript
// before
function useUserList() { /* ... */ }
function useOrderList() { /* same shape, different URL */ }
// after
function useList<T>(url: string) { /* same logic */ }
const users = useList<User>('/users');
const orders = useList<Order>('/orders');
```

Rung 5 (generic). Δ: -20 per hook pair.

---

## Advanced Python (M-P11 to M-P20)

### M-P11 — `@property` chain for computed attrs → `functools.cached_property`

```python
class Order:
    @property
    def total(self):
        return sum(line.amount for line in self.lines)
```

If `total` is called repeatedly and `lines` doesn't change per-instance, cache:
```python
from functools import cached_property
class Order:
    @cached_property
    def total(self):
        return sum(line.amount for line in self.lines)
```

Rung 1. Δ: +1 line (import); significant perf.

### M-P12 — `list(map(f, xs))` → comprehension

```python
# before
result = list(map(lambda x: x.name, users))
# after
result = [u.name for u in users]
```

Rung 1. Δ: -1.

### M-P13 — `copy.deepcopy` mid-flow → explicit immutable types

If deepcopy appears in hot paths, the design fights you. Refactor to `@dataclass(frozen=True)` + `dataclasses.replace`, or pyrsistent.

### M-P14 — `**kwargs` → `TypedDict`

```python
# before
def build(**kwargs):
    name = kwargs.get('name', 'default')
    age = kwargs.get('age', 0)
    # ...
# after
class BuildKwargs(TypedDict, total=False):
    name: str
    age: int
def build(**kwargs: Unpack[BuildKwargs]):
    # mypy knows the keys now
```

Rung 2. Δ: 0 LOC; full type info.

### M-P15 — `dict` used as namespace → `types.SimpleNamespace`

```python
# before
config = {'host': 'x', 'port': 80}
config['host']   # untyped
# after
from types import SimpleNamespace
config = SimpleNamespace(host='x', port=80)
config.host     # typed via reveal_type (kind of)
```

Limited benefit without typing; usually a dataclass is better.

### M-P16 — `except Exception` → specific exceptions

```python
# before
try:
    ...
except Exception:
    ...
# after
try:
    ...
except (ValueError, KeyError) as e:
    ...
```

Rung 1. Δ: 0. Catches bugs where unexpected exceptions are absorbed.

### M-P17 — `__init__` storing fields → `@dataclass` (covered in M-P2, emphasized)

Every Python refactor pass should run this scan:
```bash
rg 'def __init__\(self' -A 10 | head -60
```

Any class whose __init__ is just assigning parameters to `self.x` should be a dataclass.

### M-P18 — `Optional[T] = None` + if None check → Protocol default

See PYTHON-DEEP.md. For callable parameters, Protocol + default often cleaner than Optional[Callable].

### M-P19 — Nested comprehension → generator + consumer

```python
# before — materializes intermediate
result = [process(x) for x in (transform(y) for y in ys) if valid(x)]
# better — nested gen
gen = (transform(y) for y in ys)
result = [process(x) for x in gen if valid(x)]
```

Rung 1. Δ: 0; clearer scoping.

### M-P20 — `print` in logic → `logging`

```python
# before
def process(x):
    print(f"processing {x}")
    # ...
# after
logger = logging.getLogger(__name__)
def process(x):
    logger.debug("processing %s", x)
    # ...
```

Rung 1. Δ: 0; observable side-effect change — per R-014, ship carefully.

---

## Advanced Go (M-G8 to M-G15)

### M-G8 — `time.After` in select → `time.NewTimer` with cleanup

```go
// before — leaks a timer per iteration if not stopped
select {
case <-ch: ...
case <-time.After(5 * time.Second): ...
}

// after — explicit Stop
t := time.NewTimer(5 * time.Second)
defer t.Stop()
select {
case <-ch: ...
case <-t.C: ...
}
```

Rung 1. Δ: +2 lines; eliminates timer leak.

### M-G9 — `sync.WaitGroup` boilerplate → `errgroup`

```go
// before
var wg sync.WaitGroup
for _, t := range tasks {
    wg.Add(1)
    go func(t Task) {
        defer wg.Done()
        t.Do()
    }(t)
}
wg.Wait()

// after — also collects errors
import "golang.org/x/sync/errgroup"
g := new(errgroup.Group)
for _, t := range tasks {
    t := t
    g.Go(func() error { return t.Do() })
}
if err := g.Wait(); err != nil {
    return err
}
```

Rung 2. Δ: similar line count; much better error handling.

### M-G10 — `interface{}` map → `any` union via generics + type param

```go
// before
func getConfig(key string) interface{} { ... }   // callers cast
// after — domain-specific getter
func getConfigString(key string) string { ... }
func getConfigInt(key string) int { ... }
// or generics with a constraint that matches your config
```

Rung 4 (generic). Δ: varies.

### M-G11 — `switch x := y.(type)` over boxed → `reflect.TypeOf` eliminated via generics

```go
// before
func processAny(x interface{}) {
    switch v := x.(type) {
    case int: handleInt(v)
    case string: handleString(v)
    }
}
// after
func processInt(x int) { handleInt(x) }
func processString(x string) { handleString(x) }
```

Rung 1. Δ: varies; simpler overall.

### M-G12 — Test table → `map[string]struct` for named cases

```go
// before
for _, tc := range []struct{ name string; in, out int }{
    {"positive", 5, 25},
    {"zero", 0, 0},
} {
    t.Run(tc.name, ...)
}

// alternative — map form (sorted by iteration)
for name, tc := range map[string]struct{ in, out int }{
    "positive": {5, 25},
    "zero": {0, 0},
} {
    t.Run(name, ...)
}
```

Rung 0. Δ: 0; stylistic. Map form more concise; slice form preserves declared order.

### M-G13 — Nested `if err != nil` → early return / `switch`

```go
// before
if err := step1(); err != nil {
    return err
}
if err := step2(); err != nil {
    return err
}
if err := step3(); err != nil {
    return err
}
// after (same thing but sometimes clearer in a helper)
steps := []func() error{step1, step2, step3}
for _, s := range steps {
    if err := s(); err != nil { return err }
}
```

Rung 1. Δ: varies. Usually the original is fine — Go's explicit style.

### M-G14 — `context.TODO()` → `context.Context` param

```go
// before — ctx not propagated
func (s *Service) Fetch(id string) (*User, error) {
    return s.db.GetWithContext(context.TODO(), id)
}
// after
func (s *Service) Fetch(ctx context.Context, id string) (*User, error) {
    return s.db.GetWithContext(ctx, id)
}
```

Rung 2. Δ: 0; every caller updates. Big correctness win; see [GO-DEEP.md](GO-DEEP.md).

### M-G15 — `errors.New` for sentinel → package-level `var`

```go
// before — creates new error each call; fails errors.Is
if notFound(x) { return errors.New("not found") }
// after
var ErrNotFound = errors.New("not found")
if notFound(x) { return ErrNotFound }
```

Rung 1. Δ: +1 package-level decl; sentinel works with errors.Is.

---

## Advanced C++ (M-C8 to M-C15)

### M-C8 — `std::string` param-by-value + move → avoid copy

See [CPP-DEEP.md §Move semantics refactors](CPP-DEEP.md#move-semantics-refactors). Rung 1.

### M-C9 — Raw array + size → `std::span` (C++20)

```cpp
// before
void process(const int* data, size_t n);
// after
void process(std::span<const int> data);
```

Rung 1. Δ: varies; kills length-bookkeeping bugs.

### M-C10 — Output parameter → return by value (with NRVO)

```cpp
// before (C-style)
void split(const std::string& s, std::vector<std::string>& out) { /* ... */ }
// after
std::vector<std::string> split(const std::string& s) { std::vector<std::string> out; /* ... */ return out; }
```

Rung 1. Δ: similar; RVO/NRVO means no copy.

### M-C11 — `enum` → `enum class`

```cpp
// before
enum Color { RED, GREEN, BLUE };
int x = RED;   // implicit convert — bad
// after
enum class Color { Red, Green, Blue };
int x = Color::Red;   // error — good
int x = static_cast<int>(Color::Red);   // explicit
```

Rung 2. Δ: 0; type safety.

### M-C12 — Manual string formatting → `std::format` (C++20)

```cpp
// before
std::string s = "User " + name + " has " + std::to_string(count) + " items";
// after
std::string s = std::format("User {} has {} items", name, count);
```

Rung 1. Δ: similar; type-safe; faster.

### M-C13 — `std::bind` + lambda → just lambda

```cpp
// before (legacy)
auto f = std::bind(some_fn, std::placeholders::_1, 42);
// after
auto f = [](auto x) { return some_fn(x, 42); };
```

Rung 1. Δ: similar; clearer.

### M-C14 — Hand-rolled `find_if` loop → `std::ranges::find_if`

```cpp
// before
auto it = vec.begin();
for (; it != vec.end(); ++it) {
    if (predicate(*it)) break;
}
// after
auto it = std::ranges::find_if(vec, predicate);
```

Rung 1. Δ: -3.

### M-C15 — Global `std::mutex` → per-instance

Global mutexes serialize everything. Per-instance mutexes enable concurrency where it's safe.

```cpp
// before
std::mutex g_cache_lock;
// after — member
class Cache { std::mutex lock_; ... };
```

Rung 2. Risk: 4 (concurrency refactor). Profile first per [PERF-AWARE-REFACTOR.md](PERF-AWARE-REFACTOR.md).

---

## Advanced cross-language (M-X11 to M-X20)

### M-X11 — Hand-rolled ring buffer → language's built-in or lib

TS: `Array.prototype.splice`. Python: `collections.deque(maxlen=N)`. Rust: `std::collections::VecDeque`. Go: `container/ring`.

### M-X12 — Repeated HTTP request retry logic → library

Every language has a retry library. TS: `p-retry`. Python: `tenacity`. Rust: `retry`. Go: `retry-go`. Replace hand-rolled retry loops.

Rung 1. Δ: -10 to -30 per site.

### M-X13 — Manual JSON → language-native serde

Covered extensively. Canonical collapse.

### M-X14 — Hand-rolled LRU → library

TS: `lru-cache`. Python: `functools.lru_cache` or `cachetools`. Rust: `lru`. Go: `hashicorp/golang-lru`.

### M-X15 — Manual argument parsing → library

CLI: `clap` (Rust), `argparse` (Python), `yargs` (TS), `cobra` (Go).

If your CLI has >5 flags, a hand-rolled parser is almost certainly broken in some corner case.

### M-X16 — Magic string constants in multiple files → typed registry

See M-X6 in MICROPATTERNS.md for base pattern. Advanced: when 30+ constants, consider codegen from a single source-of-truth file (YAML / TOML / SQL schema).

### M-X17 — Ad-hoc feature-flag accesses → typed FlagClient

```typescript
// before — string keys sprinkled everywhere
if (featureFlags.get('NEW_CHECKOUT')) { ... }
// after — typed
const flags = new FlagClient({ newCheckout: boolean });
if (flags.newCheckout) { ... }
```

### M-X18 — Uncommented `assert`s → messages or typed check

```python
assert x > 0    # python -O strips this; silent bug
```

→
```python
if x <= 0:
    raise ValueError(f"x must be positive, got {x}")
```

Or (for invariants):
```python
assert x > 0, f"invariant: x must be positive, got {x}"
```

Rung 1. Δ: +1 per assert.

### M-X19 — Ad-hoc date formatting in every file → one util

Classic dedup pattern. All `toLocaleDateString` / `strftime` / `chrono::format` sites should go through a project util.

### M-X20 — Ad-hoc logging format → structured logger

```python
# before
logger.info(f"user {user.id} did {action} at {time}")
# after
logger.info("user action", extra={"user_id": user.id, "action": action, "timestamp": time})
```

Observable side effect; R-014 applies. Ship carefully.

---

## How to pick a micropattern

Faced with a candidate, scan this file (+ MICROPATTERNS.md M1-M40) by search:

```bash
# Looking for "I have three similar functions"
grep -n "sibling\|N near-identical\|N×" references/*PATTERNS*.md

# Looking for "this string processing is ugly"
grep -n "trim\|normalize\|format\|stringify" references/*PATTERNS*.md

# Looking for "this is too many parameters"
grep -n "parameter\|arg" references/MICROPATTERNS.md references/ADVANCED-MICROPATTERNS.md
```

The goal isn't to apply every micropattern — it's to recognize them in real code so the refactor is pattern-guided, not ad-hoc.
