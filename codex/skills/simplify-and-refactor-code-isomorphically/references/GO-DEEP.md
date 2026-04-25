# Go Refactor Deep Dive

> Go's explicit style makes many refactors safer, but some idioms (interface embedding, goroutine leaks, struct tags) are subtler than they look.

## Contents

1. [The Go isomorphism axes](#the-go-isomorphism-axes)
2. [Interface composition refactors](#interface-composition-refactors)
3. [Generics (1.18+) adoption](#generics-118-adoption)
4. [Goroutine ownership and leaks](#goroutine-ownership-and-leaks)
5. [Channel idiom collapses](#channel-idiom-collapses)
6. [errors.Is / errors.As / errors.Join](#errorsis--errorsas--errorsjoin)
7. [context.Context propagation](#contextcontext-propagation)
8. [Struct tag refactors](#struct-tag-refactors)
9. [Module path moves](#module-path-moves)
10. [Build constraints](#build-constraints)
11. [Race detector as refactor oracle](#race-detector-as-refactor-oracle)

---

## The Go isomorphism axes

In addition to the general axes, Go-specific:

| Axis | What changes if you break it |
|------|------------------------------|
| **Interface-satisfaction set** | a type may stop satisfying an interface silently |
| **Method set on pointer vs value receiver** | `*T` has `T`'s value-receiver methods; `T` doesn't have `*T`'s pointer-receiver methods |
| **Goroutine leaks** | context cancellation path changes |
| **Channel buffer size** | goroutine-blocking semantics change |
| **Struct tag strings** | JSON / SQL / validator libraries parse these; renaming breaks wire format |
| **Build tags** | per-platform compilation |
| **`init()` ordering** | unchanged by refactor in most cases, but package import order matters |
| **Zero-value semantics** | `var x T` initializes; changing `T` may break callers that assumed zero-value was meaningful |
| **Nil interface vs nil pointer** | `(*T)(nil)` != `(any)(nil)` when stored in `interface{}`; refactors can silently change which you produce |

---

## Interface composition refactors

### Pattern: extract a narrow interface

```go
// before — function takes a concrete DB type
func GetUser(db *sql.DB, id string) (*User, error) { ... }

// after — function takes an interface it actually needs
type UserFetcher interface {
    QueryRow(query string, args ...any) *sql.Row
}
func GetUser(f UserFetcher, id string) (*User, error) { ... }
```

**Benefit:** test doubles become trivial. Caller can pass `*sql.DB` or `*sql.Tx` — both satisfy.

**Isomorphism:** callers with `*sql.DB` keep working. Callers with `*sql.Tx` now work (they didn't before).

### Pattern: interface embedding to compose

```go
// before — two unrelated interfaces
type Reader interface { Read(p []byte) (int, error) }
type Closer interface { Close() error }

// after — composed interface
type ReadCloser interface {
    Reader
    Closer
}
```

Go's stdlib uses this extensively. Collapses boilerplate.

### Anti-pattern: empty-interface-everywhere

```go
// before
func process(x interface{}) error { ... }   // Go 1.17 and earlier

// after (Go 1.18+)
func process(x any) error { ... }           // same thing, clearer name
```

Pure cosmetic; zero behavior change. OK to bulk-change via `gofmt -s` replace.

Real anti-pattern: keeping `interface{}` / `any` in parameters when generics would constrain it:
```go
// before
func Max(a, b any) any {
    if ai, ok := a.(int); ok { bi := b.(int); if ai > bi { return ai }; return bi }
    if af, ok := a.(float64); ok { /* ... */ }
    ...
}
// after — generics
func Max[T cmp.Ordered](a, b T) T { if a > b { return a }; return b }
```

---

## Generics (1.18+) adoption

### When to use generics vs interfaces

| Want | Use |
|------|-----|
| One implementation for many types at compile time | generics |
| Many implementations for an abstraction at runtime | interface |
| A function that works on ordered types | `[T cmp.Ordered]` |
| A function that works on numeric types | define `Number` constraint |
| A container that holds heterogeneous values | `any` (or a sum type via interface) |

### Common refactor

```go
// before — type-specific functions
func SumInts(xs []int) int     { var s int;     for _, x := range xs { s += x }; return s }
func SumFloats(xs []float64) float64 { var s float64; for _, x := range xs { s += x }; return s }
// after
type Number interface { ~int | ~int64 | ~float32 | ~float64 }
func Sum[T Number](xs []T) T { var s T; for _, x := range xs { s += x }; return s }
```

**Isomorphism:** identical machine code per instantiation (Go uses "gcshape stenciling"; same-shape instantiations share code).

**Caution:** generics inflate binary size if many instantiations. For 10+ types, binary grows noticeably.

### When NOT to use generics

Go's generics are deliberately constrained. Don't force them:

- A single implementation with a single type → plain function.
- Runtime dispatch needed → interface.
- Heterogeneous collections → interface.
- Type that needs method dispatch per-variant → interface.

---

## Goroutine ownership and leaks

### The 3 rules

1. **Every goroutine needs a way to stop.** Context, channel-close, or done-channel.
2. **The spawner owns the lifecycle.** If function `Start()` launches a goroutine, it must return a `Stop()` or a context cancel.
3. **Never leak in error paths.** If the spawning function returns early with an error, cancel first.

### Refactor: extract a goroutine-owning function

```go
// before — goroutine inline, hard to cancel
func Process(events <-chan Event) {
    go func() {
        for e := range events { handle(e) }
    }()
}

// after
type Processor struct { done chan struct{} }
func NewProcessor(events <-chan Event) *Processor {
    p := &Processor{done: make(chan struct{})}
    go func() {
        defer close(p.done)
        for e := range events { handle(e) }
    }()
    return p
}
func (p *Processor) Wait() { <-p.done }
```

**Isomorphism:** caller now can wait for the goroutine to finish. That's an API addition, not a behavior removal.

### Context cancellation

```go
// before
func LongTask(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done(): return ctx.Err()
        default:
            doOneStep()
        }
    }
}

// refactor: check context before each blocking call, not as a default-case
func LongTask(ctx context.Context) error {
    for {
        if err := ctx.Err(); err != nil { return err }
        doOneStep()
    }
}
```

**Isomorphism:** both handle cancellation. The second is simpler; the first has a subtle polling-interval effect (`default` case returns immediately, so it busy-loops if `doOneStep` is fast).

---

## Channel idiom collapses

### Pattern: wrap sender in a struct

```go
// before — three channels, scattered goroutines
events := make(chan Event)
errs := make(chan error)
done := make(chan struct{})

// after — compose into one
type Sink struct {
    events chan Event
    errs   chan error
    done   chan struct{}
}
```

### Pattern: `select` loop with cancelation

```go
// before — naive for-range
for e := range events { process(e) }

// after — selectable with cancel
for {
    select {
    case <-ctx.Done(): return
    case e, ok := <-events:
        if !ok { return }
        process(e)
    }
}
```

**Isomorphism axes:**
- Cancellation: the second can stop mid-drain; the first can't.
- Error propagation: neither passes errors out; add another channel if needed.
- Closing behavior: `for range` exits when the channel closes; `select` with `ok` check does too.

### Unbounded channels are usually wrong

```go
// before
ch := make(chan Event)       // unbuffered; sender blocks until receiver ready
// after (load testing / high traffic)
ch := make(chan Event, 1024) // buffered; sender doesn't block until buffer full
```

**Isomorphism:** behavior identical as long as sender rate ≤ receiver rate. Changes under backpressure — can mask bugs.

**Rule:** buffered channels need a reason. If you can't explain why the buffer is 1024 (not 1, not 100000), it's cargo-culted.

---

## errors.Is / errors.As / errors.Join

Go 1.13+ shipped `errors.Is` / `errors.As`. Go 1.20+ shipped `errors.Join`.

### Refactor: `==` error comparison → `errors.Is`

```go
// before — breaks if err is wrapped
if err == io.EOF { return }
// after — works with wrapped errors
if errors.Is(err, io.EOF) { return }
```

**Behavior change:** previously, wrapping hid the sentinel; now it's reachable. Audit whether any caller depended on the old behavior.

### Pattern: `%w` wrapping

```go
// before
return fmt.Errorf("failed to get user %s: %s", id, err.Error())   // loses err
// after
return fmt.Errorf("failed to get user %s: %w", id, err)            // preserves err; errors.Is / errors.As work
```

Pure improvement; no behavior change.

### errors.Join for collecting multiple errors

```go
// before — returns the first error, loses others
for _, step := range steps {
    if err := step(); err != nil { return err }
}
// after — collects and returns all
var errs []error
for _, step := range steps {
    if err := step(); err != nil { errs = append(errs, err) }
}
return errors.Join(errs...)
```

**Behavior change:** callers see more errors. `errors.Is` still works against any joined error. But the surface is wider — don't do this blindly.

---

## context.Context propagation

### Rule: ctx is always the first parameter

```go
// anti-pattern
func GetUser(id string, ctx context.Context) (*User, error)
// convention
func GetUser(ctx context.Context, id string) (*User, error)
```

Refactor that reorders to put `ctx` first is zero-behavior change, pure readability.

### Rule: never store ctx in a struct

```go
// anti-pattern
type Processor struct { ctx context.Context; ... }
// correct
type Processor struct { ... }
func (p *Processor) Start(ctx context.Context) error { ... }
```

Context is request-scoped. Storing it in long-lived structs causes stale cancellation.

### Rule: propagate to every call

```go
// before
func (s *Service) Process(ctx context.Context, input Input) Output {
    raw := s.fetch(input.ID)                      // fetch doesn't take ctx!
    return transform(raw)
}
// after
func (s *Service) Process(ctx context.Context, input Input) (Output, error) {
    raw, err := s.fetch(ctx, input.ID)            // propagated
    if err != nil { return Output{}, err }
    return transform(ctx, raw)
}
```

**Isomorphism:** when nothing currently blocks on IO inside `fetch`, behavior is identical. When blocking exists, the new version can be cancelled. Always adopt; never remove.

---

## Struct tag refactors

### Pattern: renaming a struct field that has JSON tags

```go
type User struct {
    ID   string `json:"id"`
    Name string `json:"name"`
}
// rename Name → DisplayName
type User struct {
    ID          string `json:"id"`
    DisplayName string `json:"name"`    // tag preserves wire format
}
```

**Isomorphism:** wire format unchanged. Callers that use `user.DisplayName` need updating.

### Pattern: renaming the JSON key (wire-format change)

```go
type User struct {
    DisplayName string `json:"displayName"`    // was "name"; now "displayName"
}
```

**Behavior change:** every serialized `User` JSON object has a different key. Every consumer of the JSON breaks. Treat as a schema migration; ship with compatibility (accept both via `json:"displayName"` + `Aliases`).

### SQL / validator / protobuf tags

Same rules. Renaming fields means audit every tag-consuming library. Migration-test the serialization.

---

## Module path moves

### Pattern: moving a package to a new import path

```go
// before: github.com/org/oldrepo/pkg/foo
// after:  github.com/org/newrepo/pkg/foo

// go.mod: update the module directive
// every importer: update import paths
```

**Every downstream consumer** (inside and outside the repo) needs the path change. This is a Tier-3 refactor.

**Tool:** `gopls rename` or the go tool:
```bash
gofmt -r 'import "old/path" -> import "new/path"' -w .
```

(But per AGENTS.md: no script-based changes. Use parallel subagents or manual.)

### Vendor directory implications

If the project uses `vendor/`, module path changes break vendor sync. Run `go mod vendor` after; commit separately.

---

## Build constraints

```go
//go:build linux && !arm64
package myapp
```

### Refactor: unify build-constrained files

Two files with nearly-identical code and differing build tags:
```go
// foo_unix.go: //go:build unix
// foo_windows.go: //go:build windows
```

Can they be one file with a runtime switch (`runtime.GOOS`)? Only if the implementations don't import platform-specific packages. Often they do — leave separate.

### Removing a build constraint

```go
// before
//go:build !nolegacy
package foo
```

**Behavior change:** builds with `-tags nolegacy` now include this file (previously excluded). Audit whether that matters.

---

## Race detector as refactor oracle

```bash
go test -race ./...
go run -race main.go
```

The race detector catches data races that static analysis misses. Run it:
- Before a concurrency refactor — baseline: any pre-existing races?
- After a concurrency refactor — must not introduce new races.

**Performance:** 10-20× slowdown, 5-10× memory. Use in CI on a representative test suite, not on every test run.

### Common catches

- Slice/map read + write from two goroutines without lock.
- Goroutine captures a loop variable that mutates under it (closure trap).
- `sync.Map` used where `sync.RWMutex` + `map` was needed, or vice versa.

---

## Common Go refactor smells

- **Mega-packages (>1000 LOC in one file)** — split; Go encourages many small files per package.
- **init() functions doing setup** — prefer explicit setup in main.
- **Unused interfaces** (no implementations) — remove.
- **Empty struct returns** (`func F() struct{}`) — usually signal of a misdesigned API.
- **Interface with one method named `Do...`** — usually a function type is clearer: `type DoFn func() error`.
- **Returning `interface{}`** — prefer a concrete type or a generic.
- **Using `panic()` for control flow** — Go idiom is error returns; never panic across package boundaries except truly unrecoverable state.

For each: score via Opportunity Matrix, fill isomorphism card, verify.
