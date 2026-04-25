# Language Guides — duplication scans, common shrinks, false positives

> Each language has a different "best" tool, a different idiom for collapsing duplication, and a different list of false-positive traps.

## Contents

1. [Rust](#rust)
2. [TypeScript / JavaScript / React](#typescript--javascript--react)
3. [Python](#python)
4. [Go](#go)
5. [C / C++](#c--c)
6. [Cross-language: configuration & infra](#cross-language-configuration--infra)

---

## Rust

### Detect duplication

```bash
# Token-based — fast, decent
similarity-rs -p 80 src/

# Long files (often hide internal duplication)
scc --by-file --format json . | jq '.[] | select(.Lines > 300) | {Filename,Lines,Complexity}'

# Hand-rolled-instead-of-derive
rg 'impl (PartialEq|Eq|Hash|Ord|PartialOrd|Default|Debug|Clone) for' --type rust

# `match Err(e) => Err(e)` — reinvented `?`
rg 'match .*\{.*Err\(e\) => Err\(e\)' --type rust -U

# `if let Ok(_) = x { ... }` — reinvented `if let`
rg 'if let Ok\(_\) =' --type rust

# Per-field getters in internal modules
ast-grep run -l Rust -p 'pub fn $NAME(&self) -> &$T { &self.$FIELD }' --json

# Wrappers calling exactly one other function
ast-grep run -l Rust -p 'pub fn $NAME($$$ARGS) $$$RET { $OTHER($$$PARAMS) }'
```

### Common shrinks

| From | To | Δ |
|------|-----|---|
| Multiple `fn parse_X(s: &str) -> Result<X, E>` | Generic `fn parse<T: FromStr>(s: &str) -> Result<T, T::Err>` | -5 LOC × N |
| Hand-rolled `impl PartialEq` | `#[derive(PartialEq)]` | -5 to -15 |
| Hand-rolled `impl Display` | Keep — derived `Debug` is a different format | (no change) |
| Manual error variant + `From` chain | `thiserror` derive | -20 to -50 per error type |
| `Box<dyn Trait>` for closed set | `enum` with one variant per type | -10, kills vtable |
| Multiple `fn send_*` | Enum payload + one `fn send` | -100+ |
| `Vec<T>` then `.dedup()` after sort | `BTreeSet<T>` if order isn't important | -3 to -5 |
| `Result` ladder with `match`+`return` | `?` operator | -5 per ladder |
| Repeated `.clone()` to dodge borrow checker | Restructure ownership; or `Cow<str>` | -allocs as bonus |
| Hand-rolled `Iterator` impl | `std::iter` combinators (`chain`, `zip`, `take_while`) | -20 to -50 |

### False positives — DO NOT merge

- **Two `#[derive]` blocks that look the same** — derives are cheap; merging them would mean abstracting *over the type*, which Rust's macro system doesn't help with cleanly.
- **Two `match` arms for variants that diverge later** — premature merge into a fallthrough loses pattern-match exhaustiveness.
- **`unsafe` blocks** — even byte-identical `unsafe` blocks may carry different invariants. Read the safety comment.
- **Test fixtures** — `tempfile`, `setup_db()` glue is rarely worth extracting; readability of the test wins.

### Specific Rust idioms that read as duplication but aren't

- `impl<T: Trait1> Foo for T {}` and `impl<T: Trait2> Bar for T {}` — these are extension trait patterns; they're features, not duplication.
- Multiple `From<T>` impls for the same target — these are conversions, not copy-paste; merging them would mean dynamic dispatch.

### Tools to install

```bash
cargo install similarity-rs tokei scc
# ast-grep separately: brew install ast-grep / cargo install ast-grep
```

---

## TypeScript / JavaScript / React

### Detect duplication

```bash
# Token-based, well-known
npx jscpd --min-tokens 50 --min-lines 5 --reporters json,html --output reports/jscpd src/
# AST-based, sees Type II
npx similarity-ts -p 80 src/

# Find `as any` (often = lost types from a "simplification")
rg 'as any\b|as unknown as\b' --type ts --type tsx

# Find component pairs (e.g., XxxButton)
ast-grep run -l TypeScript -p 'export function $NAME$_Button($$$P) { return $$$JSX }' --json

# Find duplicate hooks
rg 'const \[.*\] = useState' --type tsx -A 2 -B 1 | sort | uniq -c | sort -rn | head -20

# Render props / HOC duplication
rg 'function with[A-Z]\w+\(' --type ts

# CSS class strings repeated
rg 'className=("([^"]+)")' --type tsx -o -r '$2' | sort | uniq -c | sort -rn | head -30
```

### Common shrinks

| From | To | Δ |
|------|-----|---|
| `<PrimaryButton>` / `<SecondaryButton>` / `<DangerButton>` | `<Button variant=...>` | -120 to -200 |
| Same fetch+state+effect in 5 components | Custom hook `useResource(url)` | -50 to -80 |
| Function overloads | Generic `<K extends keyof T>(k: K): T[K]` | -10 per overload |
| `JSON.parse(JSON.stringify(...))` | `structuredClone(...)` | -1, faster, types preserved |
| `Object.keys(x).reduce(...)` / `Object.entries(x).map(...)` | Loop or `for...of` if branchy | clarity > LOC |
| `interface User { ... }` defined separately + `type UserDTO` | Single `User` if all fields identical | -10 to -30 |
| Imports of `lodash.someFn` | Native ES (e.g., `lodash.uniq` → `[...new Set(arr)]`) | -1 import + bundle savings |
| Repeated discriminator switch | Discriminated union + helper that narrows once | -20 |

### React-specific

```tsx
// Anti-pattern: prop drilling 5 levels
function Page() { return <A user={user}/>; }
function A({user}) { return <B user={user}/>; }
function B({user}) { return <C user={user}/>; }
// ...

// Better: context for cross-cutting state, props for shape
const UserCtx = createContext<User|null>(null);
function Page() { return <UserCtx.Provider value={user}><A/></UserCtx.Provider>; }
```

But: **don't** put feature-specific state in context. Context is for app-shell concerns (auth, theme, locale). Per-feature state in context creates cross-component re-render storms.

### False positives — DO NOT merge

- **`useEffect` cleanups that look identical** — the dependency arrays differ, and getting them wrong is a leak.
- **Tailwind class strings** — long `className` strings often look duplicate but are page-specific layouts.
- **Two components with the same JSX shape but different a11y attributes** — `aria-labelledby`, `role`, `tabIndex` matter.

### Tools to install

```bash
npm install -D jscpd similarity-ts
# also useful for refactor:
npm install -D ts-morph
# bundle stats:
npx source-map-explorer dist/**/*.js
```

---

## Python

### Detect duplication

```bash
# Pylint's duplicate-code (decent, often good enough)
pylint --disable=all --enable=duplicate-code --output-format=json src/ > reports/pylint_dup.json

# AST-based
similarity-py -p 80 src/

# Dead code (often duplicated and unused)
vulture src/

# Long functions / high complexity
radon cc -s -a -n B src/        # show only B+ complexity
radon mi src/                   # maintainability index

# Repeated try/finally cleanup -> needs context manager
rg 'try:' -A 5 --type py | rg 'finally:'

# `if x is None: return None` instead of returning Optional and using `?`
rg 'is None.*return None' --type py
```

### Common shrinks

| From | To | Δ |
|------|-----|---|
| `dict()` literal | `{}` literal | -1 char, faster |
| `for x in xs: result.append(transform(x))` | `[transform(x) for x in xs]` | -3 |
| `dict([(k, v) for k, v in ...])` | `{k: v for k, v in ...}` | -10 chars, faster |
| Class with only `__init__` storing fields | `@dataclass` (or `@dataclass(frozen=True, slots=True)`) | -10 to -20 |
| `try/finally` resource cleanup at N sites | `@contextmanager` + `with` | -3 × N |
| `if`/`elif` chain on type | `match` (3.10+) or `singledispatch` | -varies |
| Manual `__eq__`/`__hash__` | `@dataclass(eq=True, frozen=True)` | -10 each |
| Multiple validation functions | Single `pydantic` model or `attrs` validators | -50+ |
| `def func_int(x: int): ...` / `def func_float(x: float): ...` | Single `def func(x: int|float): ...` (with `numbers.Number` constraint if needed) | -3 per shadow |
| Dict-of-dicts as poor-man's record | `TypedDict` or `dataclass` | typing wins |

### Python-specific gotcha

`mutable default argument` — a refactor sometimes inadvertently introduces this when consolidating signatures:

```python
# Before — explicit at every call
def make(items=None):
    if items is None: items = []

# "Simplified" — bug
def make(items=[]):  # shared across calls!
    ...
```

The "simpler" version is wrong. Don't make this trade.

### False positives — DO NOT merge

- **Test fixtures** — `pytest.fixture` setup; the duplication is intentional, each fixture is independent.
- **Property definitions** — `@property` getters that look identical but bind to different attributes.
- **Module-level config dicts** — they're read by import order; consolidating into one creates load-order dependencies.
- **Decorators** — three `@functools.wraps` decorators that look the same; they're targeting different functions, and the decorator IS the function's behavior.

### Tools to install

```bash
pip install pylint vulture radon similarity-py
# refactoring assist:
pip install rope libcst
```

---

## Go

### Detect duplication

```bash
# dupl is the canonical tool
dupl -threshold 50 -plumbing ./...

# Find unused code (often duplicated)
staticcheck -checks U1000 ./...

# Long functions / high complexity
gocyclo -avg -over 10 .

# Per-package dependency stats (highly-coupled = likely duplication source)
go list -f '{{.ImportPath}}: {{join .Deps " "}}' ./... | awk '{ print NF-1, $0 }' | sort -rn | head

# Find error-handling boilerplate ladder
rg 'if err != nil \{' --type go -c | sort -t: -k2 -rn | head -10
```

### Common shrinks

| From | To | Δ |
|------|-----|---|
| `func MaxInt(a, b int) int` / `MaxFloat` / `MaxString` | `func Max[T cmp.Ordered](a, b T) T` (Go 1.18+) | -20 |
| Three near-identical structs with embedded logger/metrics | Embed a `BaseHandler` struct (composition) | -30 |
| `if err != nil { return err }` ladder | `errors.Join(err1, err2)` for collection; otherwise leave (Go's idiom) | varies |
| Hand-rolled `String()` methods | `fmt.Stringer` only where needed; don't over-implement | -5 each |
| Manual JSON marshal/unmarshal | `json.Marshal` with struct tags | -50 if hand-rolled |
| Per-test setup boilerplate | `t.Run` table-driven tests | -50 to -200 |
| Mutex + wrapper-method pattern repeated | Embed `sync.RWMutex` once, methods on wrapper | -10 |
| HTTP handler with manual req parsing | `chi`/`gin` + struct-binding | -varies |

### Go-specific guidance

- Go's idiom is **explicit over abstract**. Resist the urge to introduce interfaces "for testability" — `interface{}`/`any` is rarely a refactor win.
- **Generics (1.18+) are conservative tools.** The compile cost of generic code is non-trivial; a few duplicate functions are often cheaper than one generic.
- `sync.Pool` deduplicates allocator pressure but **adds reset complexity** — don't extract a helper to "share" a pool unless callers genuinely co-locate.

### False positives — DO NOT merge

- **`if err != nil { return err }` blocks** — these are Go's `?`. Don't replace with `must` helpers (loses caller context in stack traces).
- **Two handlers that share parsing** — the parsing is part of the handler's contract; extracting it usually obscures the request shape.
- **Test fixtures shaped the same** — keep table-driven if intentional, but don't unify two unrelated test packages.

### Tools to install

```bash
go install github.com/mibk/dupl@latest
go install honnef.co/go/tools/cmd/staticcheck@latest
go install github.com/fzipp/gocyclo/cmd/gocyclo@latest
```

---

## C / C++

### Detect duplication

```bash
# clang-tidy modernize/readability checks
clang-tidy -checks='modernize-*,readability-*' -p build src/**/*.cc

# Simian (multi-language, still maintained for legacy)
simian -threshold=6 -reportDuplicateText src/**/*.{c,cc,cpp,h,hpp}

# Lizard (cyclomatic complexity)
lizard -X . > reports/lizard.xml

# Find C-style typedefs (replace with `using`)
rg 'typedef\s' --type cpp

# Macro sprawl
rg '^#define ' --type cpp

# Repeated raw resource management (replace with RAII)
rg 'malloc\(|free\(' --type cpp -c
rg 'new \w+\[' --type cpp
```

### Common shrinks

| From | To | Δ |
|------|-----|---|
| `typedef struct X X;` C-style | `using X = struct X;` (or just `struct X` in C++) | -1 each |
| Raw `new`/`delete` pairs | `std::unique_ptr` / `std::make_unique` | -varies, kills leaks |
| Hand-rolled `Visitor` pattern | `std::variant<...>` + `std::visit` | -50 |
| Class hierarchy with virtual dispatch (closed set) | `std::variant` | -30 to -100 |
| Templated free functions returning `iterator pair` | C++20 ranges | -5 to -10 each |
| `for (size_t i = 0; i < v.size(); ++i)` | `for (auto& x : v)` | -1 per loop, fewer bugs |
| Manual `std::lock_guard` followed by raw mutex ops | RAII with `std::scoped_lock` | -3 per critical section |
| Repeated SFINAE + traits | `concepts` (C++20) | -10 to -30 |
| Manual `enum`+`switch` for state | `std::variant` + visitor | -20 |
| `printf`-based logging | `std::format` (C++20) | -3 per site, type-safe |

### CRTP for static polymorphism

```cpp
// Use CRTP when:
// - You need polymorphism but vtable cost matters
// - The set of derived classes is closed and known at compile time
template<typename Derived>
class Base {
public:
    void process() { static_cast<Derived*>(this)->doWork(); }
};
class Concrete : public Base<Concrete> { void doWork(); };
```

When the set is open or runtime-dispatched, use virtual functions.

### False positives — DO NOT merge

- **Move constructor + copy constructor** — they look similar but enforce different semantics; merging is meaningless.
- **`#include` blocks** — sorting / deduplicating with `clang-format` is fine; merging by purpose isn't.
- **Two template specializations** — even if bodies are identical, the specialization is the abstraction's escape hatch.

### Tools to install

```bash
# clang-tidy ships with LLVM
brew install llvm
# lizard:
pip install lizard
```

---

## Cross-language: configuration & infra

Duplication in YAML/JSON/TOML/HCL configs is easy to spot, easy to merge **wrong**.

```bash
# Find similar yaml blocks
rg --type yaml '^[a-z]+:' -A 5 -B 0 | sort | uniq -c | sort -rn | head -20

# Terraform: duplicate resource definitions
rg --type tf 'resource "[^"]+" "[^"]+"' -A 10
```

**Common refactor:** YAML anchors + aliases.

```yaml
# Before — three almost-identical job definitions
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [{uses: actions/checkout@v4}, {run: cargo test}]
  test_release:
    runs-on: ubuntu-latest
    steps: [{uses: actions/checkout@v4}, {run: cargo test --release}]
  test_nightly:
    runs-on: ubuntu-latest
    steps: [{uses: actions/checkout@v4}, {run: cargo +nightly test}]

# After — anchor + override
defaults: &test_base
  runs-on: ubuntu-latest
  steps: [{uses: actions/checkout@v4}]
jobs:
  test:         {<<: *test_base, steps: [{uses: actions/checkout@v4}, {run: cargo test}]}
  test_release: {<<: *test_base, steps: [{uses: actions/checkout@v4}, {run: cargo test --release}]}
  test_nightly: {<<: *test_base, steps: [{uses: actions/checkout@v4}, {run: cargo +nightly test}]}
```

**Caveat:** GitHub Actions YAML doesn't fully support YAML aliases for steps. Test before committing; falling back to a composite action is often cleaner.

For Terraform, prefer **modules** over `for_each` when the resources have meaningfully different lifecycles. `for_each` saves LOC but couples destroy semantics.

For Dockerfile, prefer **multi-stage builds** to repeated `RUN` blocks.
