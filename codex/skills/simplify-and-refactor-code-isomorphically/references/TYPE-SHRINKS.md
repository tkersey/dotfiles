# Type-System Shrinks — narrow your way to less code

> Strong types are a force multiplier for LOC reduction. A well-placed generic, union, or branded type eliminates whole classes of duplication.

## Contents

1. [The type-shrink mental model](#the-type-shrink-mental-model)
2. [TypeScript patterns](#typescript-patterns)
3. [Rust patterns](#rust-patterns)
4. [Python patterns (with pyright / mypy --strict)](#python-patterns)
5. [Go patterns (1.18+)](#go-patterns)
6. [C++ concepts and templates](#c-concepts-and-templates)
7. [Cross-cutting: branded types and phantom types](#cross-cutting-branded-types-and-phantom-types)

---

## The type-shrink mental model

| Form | What it eliminates |
|------|-------------------|
| **Discriminated union** | explicit type tag reads, repeated `if (x.type === …)` chains |
| **Generic function / type** | sibling functions differing only in concrete types |
| **Conditional type** (TS) | repeated function signatures |
| **Trait bound** (Rust/Go) | runtime dispatch → compile-time |
| **Phantom type / branded type** | wrong-type-passed-to-right-slot runtime checks |
| **Literal type** | stringly-typed runtime validation |
| **Mapped type** (TS) | per-field copies of a shape |
| **Template literal type** (TS) | per-prefix/suffix variations |

The test: after the refactor, does the compiler *prevent* a bug that used to need a runtime check? If yes, you've shrunk both code and failure surface.

---

## TypeScript patterns

### T-S1 — overload set → generic

```typescript
// before
function get(key: 'name'): string;
function get(key: 'age'): number;
function get(key: 'email'): string;
function get(key: string): unknown { return profile[key]; }

// after
function get<K extends keyof Profile>(key: K): Profile[K] {
  return profile[key];
}
```

### T-S2 — `Pick` / `Omit` to derive narrow shapes

```typescript
// before — two interfaces drift
interface User { id: string; email: string; passwordHash: string; created: Date; }
interface UserDTO { id: string; email: string; created: Date; }

// after
type UserDTO = Omit<User, 'passwordHash'>;
// can't drift — editor yells if User gains a field not in DTO
```

### T-S3 — discriminated union replaces `isFoo`/`isBar`

```typescript
// before
interface Success<T> { ok: boolean; value?: T; error?: Error; }
function isSuccess<T>(r: Success<T>): r is Success<T> & { value: T } { return r.ok; }
// after
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
// the switch on `ok` narrows automatically; no user-defined type-guard needed
```

### T-S4 — mapped types reshape without duplication

```typescript
// before
interface User  { id: string; email: string; }
interface UserU { id?: string; email?: string; }    // partial-update variant

// after
type User = { id: string; email: string; };
type UserUpdate = Partial<User>;
type UserKeys = keyof User;       // 'id' | 'email'
type UserSetters = { [K in keyof User as `set${Capitalize<K>}`]: (v: User[K]) => void };
// UserSetters = { setId: (v: string) => void; setEmail: (v: string) => void }
```

### T-S5 — `infer` inside conditional types

```typescript
// Instead of duplicating Promise-unwrap logic:
type Awaited2<T> = T extends Promise<infer U> ? Awaited2<U> : T;
// or use built-in Awaited<T> (TS 4.5+)
```

### T-S6 — template literal types eliminate parsing

```typescript
type HttpVerb = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Route = `/${'users' | 'orders' | 'products'}/${string}`;
function request(method: HttpVerb, route: Route): Promise<unknown> { ... }
// Callers get compile-time validation; no runtime regex for routes.
```

### T-S7 — `satisfies` keyword replaces type cast

```typescript
// before — loses literal types
const colors: Record<string, string> = { red: '#f00', green: '#0f0', blue: '#00f' };
// after (TS 4.9+)
const colors = {
  red: '#f00', green: '#0f0', blue: '#00f',
} satisfies Record<string, string>;
// colors.red's type is '#f00', not string — preserves literals
```

### T-S8 — brand a primitive to prevent mix-ups

```typescript
type UserId  = string & { readonly __brand: 'UserId' };
type OrderId = string & { readonly __brand: 'OrderId' };

function getUser(id: UserId) { /* ... */ }
const oid: OrderId = 'order_123' as OrderId;
getUser(oid);                  // compile error — can't pass OrderId where UserId expected
```

### T-S9 — eliminate class hierarchy with structural types

TypeScript is structural. A class hierarchy often exists for no compiler reason.
```typescript
// before
abstract class Event { abstract type: string; ts: number; }
class Click extends Event { type = 'click' as const; x: number; y: number; }
// after — just types
type Click = { type: 'click'; ts: number; x: number; y: number };
type Event = Click | KeyPress | Scroll;
```

---

## Rust patterns

### R-S1 — generic function collapses N typed siblings

See [MICROPATTERNS.md §M-R4](MICROPATTERNS.md#m-r4--sibling-fn-parse_x--generic-fn-parset-fromstr).

### R-S2 — enum for closed set; trait for open

Closed set of alternatives (variant count fixed at compile time) → `enum`. Open extensibility → `trait`.

```rust
// closed — enum
enum Shape { Circle(f64), Square(f64), Rect(f64, f64) }

// open — trait
trait Drawable { fn draw(&self); }
impl Drawable for Circle { ... }
// users of the crate can `impl Drawable for MyCustomShape`
```

### R-S3 — `impl Trait` for return positions

```rust
// before — boxed trait object
fn make_iter(xs: Vec<i32>) -> Box<dyn Iterator<Item = i32>> { Box::new(xs.into_iter().filter(|&x| x > 0)) }
// after — impl Trait
fn make_iter(xs: Vec<i32>) -> impl Iterator<Item = i32> { xs.into_iter().filter(|&x| x > 0) }
```
Δ: 1 LOC; kills Box alloc.

### R-S4 — `newtype` for branded types

```rust
// before — bare strings; easy to mix
fn authorize(token: String, resource: String) { ... }
// after — impossible to mix
struct AuthToken(String);
struct Resource(String);
fn authorize(token: AuthToken, resource: Resource) { ... }
```

### R-S5 — `PhantomData` to tag state machines

```rust
struct Draft;
struct Published;
struct Article<State> { title: String, body: String, _s: PhantomData<State> }
impl Article<Draft> { fn publish(self) -> Article<Published> { ... } }
impl Article<Published> { fn amend(self) -> Article<Draft>   { ... } }
// can't call `publish` twice; types enforce the state machine
```

### R-S6 — `From`/`Into` chains replace conversion functions

```rust
// before — explicit converters
fn dto_from_user(u: &User) -> UserDto { ... }
fn user_from_row(r: Row) -> User { ... }
// after — idiomatic conversions
impl From<&User> for UserDto { ... }
impl From<Row> for User { ... }
// callers: let dto: UserDto = (&user).into();
```

### R-S7 — `Cow<str>` when maybe-owned

```rust
fn normalize(input: &str) -> Cow<str> {
    if needs_lowercase(input) { Cow::Owned(input.to_lowercase()) }
    else                       { Cow::Borrowed(input) }
}
```
Avoids always-allocating when unchanged.

---

## Python patterns

### P-S1 — Protocol for structural typing

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int) -> bytes: ...

def consume(r: Readable) -> bytes:
    return r.read(1024)
# Works for any class with a .read(int) -> bytes; no inheritance.
```

### P-S2 — NewType for brand

```python
from typing import NewType
UserId = NewType('UserId', str)
def get_user(uid: UserId) -> User: ...
# get_user("u1")  # mypy error — must be UserId
# get_user(UserId("u1"))  # ok
```

### P-S3 — TypedDict for dict-records

```python
from typing import TypedDict
class User(TypedDict): id: str; email: str
def email_of(u: User) -> str: return u['email']  # mypy knows shape
```

### P-S4 — Literal types replace stringly-typed

```python
from typing import Literal
def set_mode(m: Literal['read', 'write', 'append']) -> None: ...
# typechecker rejects set_mode('x')
```

### P-S5 — Generics with ParamSpec (3.10+)

```python
from typing import ParamSpec, TypeVar, Callable
P = ParamSpec('P')
R = TypeVar('R')
def retry(n: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        def wrap(*a: P.args, **kw: P.kwargs) -> R:
            for _ in range(n):
                try: return fn(*a, **kw)
                except: pass
            return fn(*a, **kw)
        return wrap
    return deco
# Preserves the decorated function's signature through the decorator.
```

### P-S6 — `overload` for precise return types

```python
from typing import overload, Literal

@overload
def parse(s: str, *, strict: Literal[True]) -> dict: ...
@overload
def parse(s: str, *, strict: Literal[False]) -> dict | None: ...
def parse(s, *, strict=True):
    ...
```

---

## Go patterns

### G-S1 — generics for ordered ops

```go
import "cmp"
func Max[T cmp.Ordered](a, b T) T { if a > b { return a }; return b }
```

### G-S2 — type sets for constrained generics

```go
type Number interface { ~int | ~int64 | ~float32 | ~float64 }
func Sum[T Number](xs []T) T { var s T; for _, x := range xs { s += x }; return s }
```

### G-S3 — embedded interfaces

```go
type ReadCloser interface { io.Reader; io.Closer }
// compose without redeclaring
```

### G-S4 — type aliases for branding (weak)

Go's type aliases are not brands (they're interchangeable at API level). For true branding, use named types:
```go
type UserID string
type OrderID string
func GetUser(id UserID) { ... }
// GetUser(OrderID("o1"))  // compile error
```

---

## C++ concepts and templates

### C-S1 — concept replaces SFINAE

```cpp
template<std::integral T>
T double_it(T x) { return x * 2; }
```

### C-S2 — `std::variant` for closed hierarchy

```cpp
using Shape = std::variant<Circle, Square, Rectangle>;
double area(const Shape& s) {
    return std::visit([](const auto& x) { return x.area(); }, s);
}
```

### C-S3 — CRTP for static polymorphism

```cpp
template<typename D>
class Base { void handle() { static_cast<D*>(this)->doWork(); } };
class Concrete : public Base<Concrete> { void doWork(); };
```

### C-S4 — `std::span` replaces pointer+length pairs

```cpp
// before
void process(const int* data, size_t n);
// after
void process(std::span<const int> data);
```

---

## Cross-cutting: branded types and phantom types

The idea: two values that compile to the same machine type (usually a string or integer) but represent different concepts (UserId vs OrderId, cents vs dollars, UTC vs local seconds). Branding makes them **not interchangeable at the type level**.

**TypeScript (intersection trick):**
```typescript
type Cents  = number & { readonly __brand: 'Cents' };
type Dollars = number & { readonly __brand: 'Dollars' };
const c: Cents = 100 as Cents;
const d: Dollars = c;      // error
```

**Rust (newtype):**
```rust
#[derive(Clone, Copy)] struct Cents(i64);
#[derive(Clone, Copy)] struct Dollars(i64);
```

**Python (NewType):**
```python
Cents = NewType('Cents', int)
Dollars = NewType('Dollars', int)
```

**Go (named type):**
```go
type Cents int64
type Dollars int64
```

### Where to apply

- **Units** — cents/dollars, ms/seconds, bytes/KiB/MiB.
- **Identifiers** — UserId, OrderId, PostId.
- **Validated strings** — Email, HashedPassword, Jwt.
- **State-machine states** — Draft / Published / Archived.
- **Security-sensitive** — Sanitized, Unsanitized (so raw user input can never reach DB).

### Payoff

Every refactor of a typed-boundary pair removes a runtime check, shrinks code, and eliminates a class of bugs. That's the force multiplier: you write fewer lines *and* they're more correct.

---

## Integration with this skill's loop

When the duplication map surfaces a candidate, ask:

1. **Can this be a type, not code?** Is the variance a type parameter? Generic → M-R4, T-S1, G-S1.
2. **Can exhaustiveness replace runtime check?** Discriminated union + switch → T-S3, M-X6.
3. **Can branding replace validation?** Newtype/brand → T-S8, R-S4, cross-cutting above.
4. **Can the compiler prove the invariant?** Phantom type / state machine → R-S5.

Each yes saves LOC and buys correctness. Score these higher than pure-textual collapses — the type system is doing the work forever, not just once.
