# Simplification Techniques Catalog

> Apply only after the duplication map says where. Each technique lists shape, languages, code, and the isomorphism axis it most often breaks.

## Contents

1. [Tier 1 — Mechanical](#tier-1--mechanical)
2. [Tier 2 — Structural](#tier-2--structural)
3. [Tier 3 — Architectural](#tier-3--architectural)
4. [UI / Component-specific](#ui--component-specific)
5. [Data-model unification](#data-model-unification)
6. [Type-system shrinks](#type-system-shrinks)
7. [Test-suite simplification](#test-suite-simplification)

---

## Tier 1 — Mechanical

Low risk. Low cognitive load. High LOC yield. Always do these first because they shrink the surface for the harder passes.

### 1.1 Extract constant

When a magic number/string appears at ≥3 sites:

```rust
// Before
if buf.len() < 16 { ... }
write_with_padding(&mut buf, 16);
header.set_block_size(16);

// After
const BLOCK_SIZE: usize = 16;
if buf.len() < BLOCK_SIZE { ... }
write_with_padding(&mut buf, BLOCK_SIZE);
header.set_block_size(BLOCK_SIZE);
```

**Isomorphism:** zero behavior change. Risk = 1.

### 1.2 Collapse Type II clones (same shape, different literals)

Most common. Three near-identical functions, only the literal differs.

```rust
// Before — 3×40 LOC
fn send_text(to: &str, body: &str) -> Result<MessageId> {
    let env = build_envelope(to, body, "text/plain")?;
    let id = next_id();
    archive(id, &env)?;
    notify_subscribers(id, "text")?;
    Ok(id)
}
fn send_image(to: &str, bytes: &[u8]) -> Result<MessageId> { /* same shape, "image/png" */ }
fn send_file(to: &str, path: &Path)  -> Result<MessageId> { /* same shape, "application/octet-stream" */ }
```

```rust
// After — 1×45 LOC + 3 thin wrappers
enum Payload<'a> {
    Text(&'a str),
    Image(&'a [u8]),
    File(&'a Path),
}
impl Payload<'_> {
    fn mime(&self) -> &'static str { match self {
        Payload::Text(_)  => "text/plain",
        Payload::Image(_) => "image/png",
        Payload::File(_)  => "application/octet-stream",
    } }
}
fn send(to: &str, payload: Payload<'_>) -> Result<MessageId> {
    let env = build_envelope(to, payload.bytes(), payload.mime())?;
    let id = next_id();
    archive(id, &env)?;
    notify_subscribers(id, payload.tag())?;
    Ok(id)
}
```

**Isomorphism axes to check:**
- `notify_subscribers` got `"text" | "image" | "file"` — must keep getting the same string.
- Order: previously `archive` then `notify`; preserved.
- Errors: `build_envelope` could fail with different error variants for different mimes — confirm in tests.

**Δ LOC:** ~120 → ~50 = **-70**.

### 1.3 Inline a single-call wrapper

```typescript
// Before
function getDisplayName(user: User): string { return formatDisplayName(user); }
function formatDisplayName(user: User): string {
  return user.firstName ? `${user.firstName} ${user.lastName}` : user.email;
}
// callers: only `getDisplayName` is used

// After
function getDisplayName(user: User): string {
  return user.firstName ? `${user.firstName} ${user.lastName}` : user.email;
}
```

**Isomorphism:** identical. The wrapper hop existed for "future-proofing" that never came.
**Δ LOC:** -3 to -8 per wrapper. Hunt them with a "single-callsite + single-line body" grep.

### 1.4 Replace conditional ladder with `match`

```rust
// Before — easy to add a variant and forget a branch
fn parse(token: Token) -> Node {
    if token.kind == TokenKind::Number { return Node::num(token.text); }
    if token.kind == TokenKind::Ident  { return Node::ident(token.text); }
    if token.kind == TokenKind::String { return Node::str(token.text); }
    panic!("unhandled");
}
// After — exhaustiveness is now a compile-time check
fn parse(token: Token) -> Node {
    match token.kind {
        TokenKind::Number => Node::num(token.text),
        TokenKind::Ident  => Node::ident(token.text),
        TokenKind::String => Node::str(token.text),
    }
}
```

**Isomorphism:** identical for valid inputs. `panic!` becomes "doesn't compile" — strictly better but a behavior change at the type level (a subtle one). Note in the card.
**Δ LOC:** small, but fixes a class of bugs. Score it as Risk=1.

### 1.5 Replace error-Result ladder with `?`

```rust
// Before
let f = match fs::open(p) {
    Ok(f) => f,
    Err(e) => return Err(e),
};
let n = match f.read_to_end(&mut buf) {
    Ok(n) => n,
    Err(e) => return Err(e),
};

// After
let f = fs::open(p)?;
let n = f.read_to_end(&mut buf)?;
```

**Isomorphism:** identical when error types are the same. If they differ, you'd need a `From` impl — which is itself good cleanup.
**Δ LOC:** ~6 lines per ladder.
**Spot the pattern:** `rg 'match .* Err\(e\) => Err\(e\)' -t rust`

### 1.6 Replace `Vec::new() + push loop` with comprehension/iterator

```python
# Before
result = []
for x in items:
    if x.active:
        result.append(transform(x))

# After
result = [transform(x) for x in items if x.active]
```

```rust
// Before
let mut result = Vec::new();
for x in items {
    if x.active { result.push(transform(x)); }
}
// After
let result: Vec<_> = items.iter().filter(|x| x.active).map(transform).collect();
```

**Isomorphism:** identical iff `transform` is pure and `result.len()` capacity isn't load-bearing. Iterator order preserved.
**Δ LOC:** -3 to -4 per loop.

### 1.7 Remove dead branches behind shipped feature flags

```typescript
// Before
if (FEATURE_NEW_AUTH_ENABLED) {
  return await newAuth(req);
} else {
  return await legacyAuth(req);
}

// After (flag has been on for 6 months, every account migrated)
return await newAuth(req);
```

Then grep for `legacyAuth` — if it's not called elsewhere, ask permission to remove it (per AGENTS.md, deletion needs explicit approval).

**Isomorphism:** depends on flag truly being globally on. Verify with telemetry / config audit before scoring high confidence.

### 1.8 Replace hand-rolled Equality/Display/Serialize with `derive`

```rust
// Before
impl PartialEq for Color {
    fn eq(&self, o: &Self) -> bool { self.r == o.r && self.g == o.g && self.b == o.b }
}
impl fmt::Display for Color {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Color({}, {}, {})", self.r, self.g, self.b)
    }
}
// After (only if Debug format is acceptable)
#[derive(PartialEq, Debug)]
struct Color { r: u8, g: u8, b: u8 }
```

**Isomorphism caution:** the derived `Debug` formats differently from the hand-rolled `Display`. **If any test or log line depends on the exact output, the change is observable.** Snapshot tests will catch it; if you have none, write one first.

---

## Tier 2 — Structural

Higher payoff. Higher risk. Always score and prove.

### 2.1 Component variants (UI)

```tsx
// Before — 3 components × ~60 LOC each
export function PrimaryButton({ children, onClick, disabled }) {
  return <button className="btn btn-primary" onClick={onClick} disabled={disabled}>{children}</button>;
}
export function SecondaryButton(...) { /* same, "btn btn-secondary" */ }
export function DangerButton(...)    { /* same, "btn btn-danger" + extra confirm */ }
```

```tsx
// After — 1 component, 1 variant prop
type Variant = 'primary' | 'secondary' | 'danger';
const variantClass: Record<Variant, string> = {
  primary: 'btn btn-primary',
  secondary: 'btn btn-secondary',
  danger: 'btn btn-danger',
};
export function Button({ variant = 'primary', children, onClick, disabled, requireConfirm }: Props) {
  const handle = requireConfirm ? () => confirm('Are you sure?') && onClick?.() : onClick;
  return <button className={variantClass[variant]} onClick={handle} disabled={disabled}>{children}</button>;
}
```

**Isomorphism axes:**
- The danger-button's confirm dialog must trigger on the same condition. Pull the `requireConfirm` to the prop, default false.
- If `<DangerButton>` had a custom `onMouseEnter` or `aria-*`, fold those in too.
- React reconciliation: changing element identity (different component name) can blow away local state in callers that mounted them conditionally. Search for patterns like `{showDanger ? <DangerButton/> : <PrimaryButton/>}` — those will now share state. Usually fine; sometimes not.

**Δ LOC:** -120 to -180 across a typical UI.

### 2.2 Custom hook (React)

```tsx
// Before — same 12 lines in 5 components
function ProductPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error|null>(null);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`/api/product/${id}`).then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch(e => { if (!cancelled) { setError(e); setLoading(false); } });
    return () => { cancelled = true; };
  }, [id]);
  // …render
}

// After
function useResource<T>(url: string): { data: T|null; loading: boolean; error: Error|null } {
  const [data, setData] = useState<T|null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error|null>(null);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(url).then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch(e => { if (!cancelled) { setError(e); setLoading(false); } });
    return () => { cancelled = true; };
  }, [url]);
  return { data, loading, error };
}
function ProductPage() {
  const { data, loading, error } = useResource<Product>(`/api/product/${id}`);
}
```

**Isomorphism axes:**
- Hook order: every component still calls hooks in the same order (the hook is one slot, just like the three useState calls were).
- Cancellation behavior preserved.
- If any caller depended on `setData` being available externally, hoist the setter — the hook can return `{ ..., refetch }`.

**Δ LOC:** -10 lines × N components - 18 lines for the hook = ~-30 to -50 for typical N=5.

### 2.3 Replace inheritance hierarchy with `match` / `enum`

```rust
// Before — Box<dyn Trait> hierarchy with 4 implementors
trait Shape { fn area(&self) -> f64; fn perimeter(&self) -> f64; }
struct Circle { r: f64 }
struct Square { s: f64 }
struct Rect { w: f64, h: f64 }
struct Triangle { b: f64, h: f64 }
// + 4× impl blocks, 8 functions

// After — one enum, two methods
enum Shape {
    Circle { r: f64 },
    Square { s: f64 },
    Rect { w: f64, h: f64 },
    Triangle { b: f64, h: f64 },
}
impl Shape {
    fn area(&self) -> f64 { match self {
        Shape::Circle { r } => std::f64::consts::PI * r * r,
        Shape::Square { s } => s * s,
        Shape::Rect { w, h } => w * h,
        Shape::Triangle { b, h } => 0.5 * b * h,
    } }
    fn perimeter(&self) -> f64 { match self { /* … */ } }
}
```

**Isomorphism axes:**
- Trait dispatch removed → no more vtable. Behavior identical for closed sets.
- If users were extending `Shape` externally (e.g. plugins), they can't anymore. That's a public-API change — only do this for closed sets.
- `Box<dyn Shape>` of size 16 bytes becomes `Shape` of size = max-variant + tag. Sometimes larger; rarely matters.

### 2.4 Generic over identical impls

```go
// Before (Go 1.17 era)
func MaxInt(a, b int) int       { if a > b { return a }; return b }
func MaxFloat(a, b float64) float64 { if a > b { return a }; return b }
func MaxString(a, b string) string  { if a > b { return a }; return b }

// After (Go 1.18+)
func Max[T cmp.Ordered](a, b T) T { if a > b { return a }; return b }
```

**Isomorphism:** identical behavior; identical machine code per instantiation.

```rust
// Before
fn parse_u32(s: &str) -> Result<u32, ParseIntError> { s.parse() }
fn parse_i32(s: &str) -> Result<i32, ParseIntError> { s.parse() }
fn parse_f64(s: &str) -> Result<f64, ParseFloatError> { s.parse() }

// After
fn parse<T: FromStr>(s: &str) -> Result<T, T::Err> { s.parse() }
```

**Caution:** the unified function has a different error type (`T::Err`). Callers that branched on the old concrete error types now branch on a generic associated type — usually fine, occasionally awkward.

### 2.5 Hoist try/finally with a context manager / RAII

```python
# Before — 6 places have the same try/finally cleanup
conn = pool.acquire()
try:
    do_work(conn)
finally:
    pool.release(conn)

# After
@contextmanager
def borrowed(pool):
    c = pool.acquire()
    try: yield c
    finally: pool.release(c)

with borrowed(pool) as conn:
    do_work(conn)
```

**Isomorphism:** identical iff the `try`/`finally` order is preserved (it is — context managers guarantee it).
**Δ LOC:** -3 per site - the helper.

### 2.6 Replace recursion with iteration when stack-depth varies

This isn't pure simplification — it's a stack-safety fix that often shrinks code. Score it carefully (Risk ≥ 3 because behavior at extreme inputs changes).

### 2.7 Replace dynamic config with typed constants

```typescript
// Before
const config = JSON.parse(fs.readFileSync('config.json', 'utf-8'));
if (config.features.newAuth) { ... }
const apiUrl = config.api.url;

// After (config is static, frozen at build time)
import { config } from './config';   // a typed module
if (config.features.newAuth) { ... }
const apiUrl = config.api.url;
```

**Δ LOC:** small per-call, but kills a whole class of "field doesn't exist" runtime errors.
**Isomorphism axis:** runtime errors become compile errors — stricter. Document in the card.

---

## Tier 3 — Architectural

Don't do these inside the simplification skill alone — write a plan doc, get review, and split into multiple labelled commits. The skill's role is to *recognize* when these are warranted and *score* them, not to *execute* them in one pass.

### 3.1 Collapse two services that share 80% of a codebase

Trigger: two binaries that read the same DB, share logging/auth code, and differ only in routing.
Plan: one binary, one of two subcommands; redeploy as one unit; observability re-wired.
Why this needs a plan doc: deploy story, rollback story, DB migration story, on-call story.

### 3.2 Replace inheritance hierarchy with composition

When the hierarchy has diamonds, mixins, or implicit `super()` ordering, the sticky bugs are LSP violations. Composition replaces the hierarchy with explicit handlers. Risk = 5.

### 3.3 Replace ORM with typed query builder

ORMs encode many invariants implicitly (lazy loading, identity map, cascading saves). A direct-SQL refactor surfaces these — by breaking them. Don't undertake unless you have integration tests with real DB state.

### 3.4 Monorepo consolidation

Three packages that re-publish the same `utils.ts`. Worth merging when the per-package CI cache savings dominate the maintenance cost. Worth NOT merging when each package has independent release cadence with different SemVer guarantees.

---

## UI / Component-specific

### UI snapshot baseline

For UI work, "goldens" means screenshot diffs. Use Playwright + `expect(page).toHaveScreenshot()` or VHS + `cass` snapshots for TUIs. The baseline is the snapshot set before the refactor; the verifier is `--update-snapshots` reporting **zero** changes.

```bash
# Baseline
npx playwright test --update-snapshots
git add -A tests/snapshots/
git commit -m "snapshot baseline pre-refactor"

# Verify
npx playwright test
# zero pixel diff = bit-identical UI = component refactor was isomorphic
```

For TUIs, use VHS + the [tui-inspector](../../tui-inspector/SKILL.md) skill's `record-snapshot` recipe.

### CSS dedup

`purgecss` after refactor often removes 30–60% of unused styles introduced by the old, scattered components. Run it as a separate commit.

### Tailwind / utility-class dedup

Long class strings repeat at every site. Don't extract to `@apply` directives; extract to a typed `clsx()` helper or to a `variant` prop. `@apply` strings tend to grow into the same kind of debt the components had.

---

## Data-model unification

### When to unify

Only when every field of the merged model means the same thing in every consumer. Specifically:

- **Same units** (cents vs dollars, ms vs seconds, UTC vs local time)
- **Same nullability semantics** (a missing field means the same thing)
- **Same required vs optional** (optional in one consumer + required in another → not unifiable without a default that may be wrong)
- **Same identity / equality semantics**

If two of these differ, the unified type silently lies to half its consumers.

### Decision aid

```markdown
## Should we unify `OrderV1`, `OrderV2`?

- All fields shared?  yes (12 fields)
- Field meanings identical? mostly:
  - V1.amount is in cents, V2.amount is in cents — OK
  - V1.notes is optional, V2.notes is required (defaults to "") — DRIFT
- Nullability: OK
- Identity:  V1 hashed by (user_id, ts); V2 hashed by id — DRIFT

→ DO NOT UNIFY. Keep both. Document the divergence in a doc comment.
```

### Migration shape when you do unify

```rust
// Step 1: add a new merged type, parse from both sources
struct Order { /* unified */ }
impl From<OrderV1> for Order { /* … */ }
impl From<OrderV2> for Order { /* … */ }

// Step 2: convert callers one by one (separate commits)
// Step 3: remove OrderV1/V2 only after all callers migrated AND user approves removal
```

---

## Type-system shrinks

### TypeScript

```typescript
// Before — overloaded function with 4 explicit signatures
function get(key: 'name'): string;
function get(key: 'age'): number;
function get(key: 'email'): string;
function get(key: 'active'): boolean;
function get(key: keyof Profile) { return profile[key]; }

// After — one generic signature
function get<K extends keyof Profile>(key: K): Profile[K] {
  return profile[key];
}
```

**Isomorphism:** identical at runtime. Stronger at type level (the body can no longer return the wrong type).

```typescript
// Before — `any` chain
const userId: any = (req.body as any).user.id;

// After — narrow + validate at boundary
import { z } from 'zod';
const schema = z.object({ user: z.object({ id: z.string() }) });
const { user: { id: userId } } = schema.parse(req.body);
```

The validator is **more code**, not less. But it eliminates a class of runtime crashes and erases all the `any`s downstream — net LOC savings come from the cascade.

### Rust

```rust
// Before — duplicate getter for every field
impl Config {
    fn name(&self) -> &str { &self.name }
    fn host(&self) -> &str { &self.host }
    fn port(&self) -> u16 { self.port }
    // … 20 more
}
// After — derive accessors via macro, OR just make fields pub(crate)
pub(crate) struct Config { pub(crate) name: String, pub(crate) host: String, pub(crate) port: u16 /* … */ }
```

The "encapsulation" of a getter that returns a borrow of a field is theatre. If the struct is internal, just make fields visible to the crate.

### Python

```python
# Before — 5 dataclasses with the same shape
@dataclass
class CreateUserRequest:
    email: str
    name: str
@dataclass
class UpdateUserRequest:
    email: str
    name: str
# … etc

# After — generic if the shape is genuinely identical
@dataclass
class UserPayload:
    email: str
    name: str
# Or, if the shapes diverge later, leave them — typing > LOC.
```

---

## Test-suite simplification

Tests are code too. Same techniques, with extra caution: a "simplified" test that no longer hits the original branch is a worse test.

### Table-driven tests

```go
// Before — 8 nearly identical test funcs
func TestParse_Empty(t *testing.T) { /* ... */ }
func TestParse_Whitespace(t *testing.T) { /* ... */ }
// ...

// After
func TestParse(t *testing.T) {
    for _, tc := range []struct{ name, in string; want Node; err error }{
        {"empty",      "",      Node{}, nil},
        {"whitespace", "   ",   Node{}, nil},
        {"number",     "42",    Node{Num: 42}, nil},
        {"trailing",   "42 ",   Node{Num: 42}, nil},
        {"invalid",    "abc",   Node{}, ErrInvalid},
    } {
        t.Run(tc.name, func(t *testing.T) {
            got, err := Parse(tc.in)
            if !errors.Is(err, tc.err) { t.Fatalf("err: got %v want %v", err, tc.err) }
            if got != tc.want { t.Errorf("got %v want %v", got, tc.want) }
        })
    }
}
```

**Isomorphism for test code:** every original case must remain a separate `t.Run` subtest, otherwise CI's per-test reporting changes (and many CI tools key on test names — those names appear in dashboards and PR comments).

### Don't merge tests with different *fixtures*

If two tests have the same body but set up the world differently (e.g., one with a logged-in user, one without), keep them separate. The body looking the same is a coincidence; the fixtures are the test.
