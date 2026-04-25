# Python Refactor Deep Dive

> Python's dynamism (duck typing, monkey patching, runtime attribute access) makes some refactors safer than in Rust/TS, and some dramatically less safe. This file is the complete Python-specific playbook.

## Contents

1. [The Python isomorphism axes](#the-python-isomorphism-axes)
2. [Async / sync split refactors](#async--sync-split-refactors)
3. [dataclass / TypedDict / Protocol / NamedTuple](#dataclass--typeddict--protocol--namedtuple)
4. [Decorator pattern refactors](#decorator-pattern-refactors)
5. [Context manager refactors](#context-manager-refactors)
6. [Generator / iterator materialization](#generator--iterator-materialization)
7. [contextvars / threadlocal / asyncio.Task](#contextvars--threadlocal--asynciotask)
8. [Metaclass and `__init_subclass__` land](#metaclass-and-__init_subclass__-land)
9. [Type system tightening with mypy strict](#type-system-tightening-with-mypy-strict)
10. [GIL implications of refactors](#gil-implications-of-refactors)
11. [pytest fixture refactors](#pytest-fixture-refactors)

---

## The Python isomorphism axes

In addition to the general axes, Python-specific:

| Axis | What changes if you break it |
|------|------------------------------|
| **Import-time side effects** | modules register decorators, import other modules, open files |
| **Attribute resolution order (MRO)** | changes in inheritance chains shift which `__init__` runs |
| **Monkey-patched attributes** | external code may have replaced a class method at runtime |
| **`__slots__`** | adding/removing changes memory layout; subclasses may break |
| **Mutable default arguments** | changes between refactors cause shared-state bugs |
| **Name binding in closures** | late-binding loops have the canonical lambda trap |
| **`__del__` finalization order** | GC-observed; async cleanup especially fragile |
| **`weakref` / `WeakValueDictionary`** | changing lifetimes moves weakref collections |
| **Iterator laziness** | `map`/`filter` are lazy; `list` comprehensions are eager |
| **Async loop identity** | `asyncio.get_event_loop()` changed semantics in 3.10+ |
| **`pickle` protocol** | struct field reorder / rename breaks deserialization of old data |
| **`importlib` / `__all__`** | determines what `from module import *` exposes |

---

## Async / sync split refactors

Python's split between sync and async functions is rigid. `await` only inside `async def`. Crossing the boundary needs explicit tooling.

### Pattern: making a sync function async

```python
# before
def fetch_user(id: str) -> User:
    return requests.get(f"/users/{id}").json()

# after
async def fetch_user(id: str) -> User:
    async with httpx.AsyncClient() as c:
        r = await c.get(f"/users/{id}")
        return r.json()
```

**Every caller now needs to `await`.** Count callers first:
```bash
rg 'fetch_user\(' -t py -c | sort -t: -k2 -rn
```

If >20, the async migration is Tier-3. Plan + swarm + one commit per caller family.

### Pattern: bridging sync→async (anyio, asyncio.to_thread)

When a function must stay sync (e.g., called from a sync-only framework), but the code it calls is async:

```python
import anyio

def sync_wrapper(id: str) -> User:
    return anyio.from_thread.run(async_fetch_user, id)
```

This works from code running in `anyio.from_thread` context only. It's a bridging pattern — document the invariant.

### Common refactor: calling sync blocking IO from async code

```python
# anti-pattern: calling requests.get() from async code — blocks event loop
async def fetch(id: str):
    return requests.get(f"/api/{id}").json()   # BLOCKS

# correct: offload to thread pool
import asyncio
async def fetch(id: str):
    return await asyncio.to_thread(lambda: requests.get(f"/api/{id}").json())
```

Or switch to `httpx` / `aiohttp` (async-native).

**Isomorphism:** going from `requests` → `httpx.AsyncClient` is rarely 1:1:
- Default timeouts differ.
- SSL handling differs (httpx is stricter).
- Retry behavior differs.
- Connection-pool semantics differ.

Audit each call.

---

## dataclass / TypedDict / Protocol / NamedTuple

Python offers several ways to describe record-shaped data:

| Form | Use when |
|------|----------|
| `@dataclass` | mutable record, methods attached, subclass-able |
| `@dataclass(frozen=True, slots=True)` | immutable, hashable, low memory |
| `TypedDict` | dict with known keys; zero runtime overhead |
| `NamedTuple` | immutable, iterable, hashable, comes with positional access |
| `Protocol` | structural typing; "duck type" documented |
| `pydantic.BaseModel` | validates at runtime; for data from outside (JSON, YAML) |

### Common refactor: bare dict → TypedDict or dataclass

```python
# before — AI-generated; typing weak
user = {'id': 'u1', 'email': 'a@b.com'}
def email_of(u: dict) -> str: return u['email']
# after — dataclass
from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class User:
    id: str
    email: str
def email_of(u: User) -> str: return u.email
```

**Isomorphism:**
- `dict['email']` and `user.email` at runtime behave the same for valid inputs.
- **Serialization differs.** `json.dumps(user)` fails on dataclass without `dataclasses.asdict(user)` first. Audit every JSON boundary.
- **Equality differs.** Two dicts with same keys/values are `==`. Two dataclasses require both to be the same class.

### Refactor: dataclass → frozen dataclass + slots

```python
# before
@dataclass
class User: id: str; email: str
# after
@dataclass(frozen=True, slots=True)
class User: id: str; email: str
```

**Behavior changes:**
- Instances are now hashable — usable as dict keys.
- Instances are now immutable — `user.email = 'x'` raises FrozenInstanceError.
- Memory is lower (no `__dict__`).
- Dynamic attribute addition (`user.extra = ...`) raises AttributeError.

If any existing code mutates or adds attributes to `User`, the refactor breaks it.

---

## Decorator pattern refactors

Decorators are sometimes-invisible behavior. Common refactors:

### Moving a decorator to a new location

```python
# before
@log_calls
@retry(times=3)
def fetch(url: str): ...
```

```python
# after (order matters!)
@retry(times=3)
@log_calls
def fetch(url: str): ...
```

**Order effects:** decorators wrap bottom-up. Moving `@retry` above `@log_calls` means log events fire per-retry instead of once. Different observability.

### Extracting a decorator

```python
# before — boilerplate repeated
def get_user(req):
    t0 = time.time()
    try:
        result = _get_user(req)
        log.info("get_user", duration=time.time()-t0)
        return result
    except Exception as e:
        log.error("get_user", err=str(e), duration=time.time()-t0)
        raise
# after — extract
def instrumented(name):
    def deco(fn):
        def wrap(*a, **kw):
            t0 = time.time()
            try:
                result = fn(*a, **kw); log.info(name, duration=time.time()-t0); return result
            except Exception as e:
                log.error(name, err=str(e), duration=time.time()-t0); raise
        return wrap
    return deco

@instrumented("get_user")
def get_user(req): return _get_user(req)
```

**Isomorphism:**
- Preserves logging events ✓
- Preserves error propagation ✓
- But: `functools.wraps` must be used, or `fn.__name__` changes → frameworks that introspect names (Flask, Celery, FastAPI) break.

```python
from functools import wraps
def instrumented(name):
    def deco(fn):
        @wraps(fn)                           # critical
        def wrap(*a, **kw): ...
        return wrap
    return deco
```

---

## Context manager refactors

```python
# before — try/finally boilerplate
conn = pool.acquire()
try:
    do_work(conn)
finally:
    pool.release(conn)

# after
@contextmanager
def borrowed():
    c = pool.acquire()
    try: yield c
    finally: pool.release(c)

with borrowed() as conn: do_work(conn)
```

See [MICROPATTERNS.md §M-P1](MICROPATTERNS.md#m-p1--try--finally-cleanup--contextmanager).

### Async context managers

```python
# async version
from contextlib import asynccontextmanager
@asynccontextmanager
async def borrowed_async():
    c = await pool.acquire()
    try: yield c
    finally: await pool.release(c)

async with borrowed_async() as conn: await do_work(conn)
```

**Don't mix:** `async with` on a sync context manager (or vice versa) is a runtime error.

### ExitStack for variable-count resources

```python
# before — deeply nested
with open(a) as fa:
    with open(b) as fb:
        with open(c) as fc:
            process(fa, fb, fc)

# after
from contextlib import ExitStack
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    process(*files)
```

**Isomorphism:** cleanup happens in LIFO order in both. ExitStack is clearer for N>3.

---

## Generator / iterator materialization

Iterators are lazy in Python. Materializing (`list(x)`) or refusing to (`for y in x:`) changes memory + sometimes correctness.

### Pattern: `.map(x)` vs `[m for ...]`

```python
# lazy
squared = map(lambda x: x*x, range(1_000_000))
# eager
squared = [x*x for x in range(1_000_000)]
```

If you materialize when you didn't need to: peak RSS grows.
If you don't materialize when you needed to: re-iteration fails silently (iterator exhausted after first pass).

### Pattern: generator function → list-returning function

```python
# before — lazy, memory-friendly
def rows():
    for line in open('huge.csv'):
        yield parse(line)

# after — eager
def rows():
    return [parse(line) for line in open('huge.csv')]   # loads everything
```

**Isomorphism:** behavior identical for callers that iterate once. Different for:
- Memory pressure on large files
- Callers that call `rows()` twice (lazy: works; eager: re-reads the file each call because `open()` is re-invoked)
- Callers that catch `StopIteration` (different timing)

### Don't `.close()` on a generator you still need

```python
rows = generator_fn()
for r in rows:
    if bad(r):
        rows.close()   # closes; subsequent iteration raises
        break
```

If later code assumes you can keep iterating: `.close()` breaks that. Usually it's fine; audit if you're not sure.

---

## contextvars / threadlocal / asyncio.Task

Python 3.7+ provides `contextvars` for async-safe context propagation. Many refactors involve migrating from threadlocals to contextvars.

```python
# before — uses threading.local; wrong in async
import threading
_current = threading.local()
def set_user(u): _current.user = u

# after — contextvar; works for both sync and async
from contextvars import ContextVar
_user: ContextVar[User | None] = ContextVar('user', default=None)
def set_user(u): _user.set(u)
```

**Isomorphism axes:**
- Per-request isolation: both work for sync-per-thread. Only contextvars works for async.
- Sub-task inheritance: `asyncio.Task` copies the context at creation. Child tasks see the parent's context at spawn time; changes don't propagate back.
- Threadpool: `asyncio.to_thread` does propagate context (3.10+); older versions don't.

---

## Metaclass and `__init_subclass__` land

Metaclasses are invisible machinery. Refactors that touch them often break in strange ways.

```python
# Metaclass that auto-registers subclasses
class RegistryMeta(type):
    registry = {}
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        RegistryMeta.registry[name] = cls

class Handler(metaclass=RegistryMeta): pass
class UserHandler(Handler): pass      # auto-registered under "UserHandler"
```

Renaming `UserHandler` → `UserAction` changes the registry key. Every caller that does `RegistryMeta.registry['UserHandler']` breaks.

**Rule:** when refactoring a class whose `type(cls).__mro__[1:]` contains a metaclass (not `type`), read the metaclass before editing. The metaclass may embed the class name, module, or something else in runtime state.

### `__init_subclass__` — the modern alternative

```python
class Handler:
    registry = {}
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        Handler.registry[cls.__name__] = cls

class UserHandler(Handler): pass   # same registration, no metaclass
```

Rarely encountered as the target of a refactor, but if you see it: same rules as metaclasses.

---

## Type system tightening with mypy strict

See [RESCUE-MISSIONS.md §Phase 0.5](RESCUE-MISSIONS.md#phase-05-fix-the-type-system) for the gradual approach.

### Mypy overrides

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = false       # permissive default

[[tool.mypy.overrides]]
module = "myproject.core.*"
disallow_untyped_defs = true
strict_equality = true
warn_return_any = true
```

Monotonically grow the strict list as modules clean up.

### `Any` vs `object` vs `Unknown`

- `Any` — mypy silently accepts everything. Avoid.
- `object` — mypy requires narrowing. Use when truly unknown shape.
- `Unknown` — not a real type. Users who write this mean `Any` or should use `object` + narrow.

### Protocol vs ABC

```python
# ABC — nominal typing
from abc import ABC, abstractmethod
class Writer(ABC):
    @abstractmethod
    def write(self, s: str) -> None: ...

# Protocol — structural typing
from typing import Protocol
class Writer(Protocol):
    def write(self, s: str) -> None: ...
```

**Structural advantage:** any class with a `write(str) -> None` satisfies the Protocol without explicit inheritance. Test doubles, stdlib types, etc. work.

**Migration direction:** ABC → Protocol is usually a simplification. Protocol → ABC is usually a behavior tightening (runtime `isinstance` checks differ).

---

## GIL implications of refactors

### Free-threaded Python (3.13+ experimental)

Python 3.13 ships an optional no-GIL build. Most refactors work identically, but:

- Classes with mutable class-level state become data-race targets.
- `dict.setdefault` is atomic on GIL build, not on no-GIL. Use `threading.Lock`.
- `collections.defaultdict` has the same issue.

**Audit before refactoring shared state in a no-GIL-targeted codebase.**

### CPU-bound vs IO-bound

Refactors that parallelize CPU-bound work via `threading` on CPython (GIL build) do nothing. Use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor`.

For IO-bound work, `threading` / `asyncio` both work.

Rule of thumb: if the `async def` refactor changes a CPU-bound function to async, the work still runs serially on one core. Async doesn't parallelize CPU.

---

## pytest fixture refactors

### Common anti-pattern: bulk-sharing fixtures that shouldn't be shared

```python
# conftest.py
@pytest.fixture
def db():
    conn = connect()
    yield conn
    conn.close()    # shared across every test in the module — expensive if every test gets a fresh conn

# refactor: session-scoped DB, function-scoped transaction
@pytest.fixture(scope="session")
def db():
    conn = connect(); yield conn; conn.close()

@pytest.fixture
def db_tx(db):
    tx = db.begin(); yield db; tx.rollback()
```

**Isomorphism:** each test sees a clean DB state (tx rollback) while the connection is shared. 10-100x faster test suite.

### Fixture extraction in conftest

Moving a fixture to `conftest.py` makes it auto-discovered by every test in the directory. Too aggressive:
- Fixtures bleed to tests that never wanted them.
- Order of fixture application changes.

**Rule:** the topmost conftest only hosts fixtures used by ≥3 test files in that directory. Others stay local.

### `autouse=True` is dangerous

```python
@pytest.fixture(autouse=True)
def seed_db():
    reset_database()
```

Now every single test pays the cost of `reset_database()`, even tests that don't touch the DB. Most "autouse" fixtures should be opt-in.

---

## Common Python refactor smells

- **`**kwargs` everywhere** — replace with explicit parameters; use `TypedDict` for kwargs bags.
- **`eval()` / `exec()`** — almost always refactorable. Security risk.
- **Module-level mutable state** — usually lives through `import` caching; refactor into a class or singleton pattern.
- **`global` keyword** — replace with class attribute or pass-in parameter.
- **Deeply nested class hierarchies** — Python supports multi-inheritance; most refactors flatten to composition.
- **`setattr(obj, name, value)`** — magic attribute setting; refactor to explicit `__init__` or dataclass.
- **`functools.partial` chains** — often hide what's going on; inline for clarity.

For all of these: score via the Opportunity Matrix, fill the isomorphism card, Edit only, one lever per commit.
