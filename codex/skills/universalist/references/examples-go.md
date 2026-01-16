# Go Examples (ADD)

## Table of contents
- Sum types via interfaces
- Product types
- Smart constructors
- Monoid-like combine
- Validation with error accumulation
- Lattice for permissions
- Semiring-like scores
- State machine transitions
- Fold with monoid
- Normalization
- Homomorphism

## Sum types via interfaces
```go
// Coproduct: one of several variants
package domain

type PaymentStatus interface{ isPaymentStatus() }

type Pending struct{}
func (Pending) isPaymentStatus() {}

type Settled struct{ Ref string }
func (Settled) isPaymentStatus() {}

type Failed struct{ Reason string }
func (Failed) isPaymentStatus() {}
```

## Product types
```go
type Money struct {
  Amount   int
  Currency string
}
```

## Smart constructors
```go
func NewNonEmpty(s string) (string, error) {
  if s == "" {
    return "", fmt.Errorf("empty string")
  }
  return s, nil
}
```

## Monoid-like combine
```go
type Log struct { Lines []string }

func EmptyLog() Log { return Log{Lines: []string{}} }

func CombineLog(a, b Log) Log {
  out := make([]string, 0, len(a.Lines)+len(b.Lines))
  out = append(out, a.Lines...)
  out = append(out, b.Lines...)
  return Log{Lines: out}
}
```

## Validation with error accumulation
```go
type Validation[T any] struct {
  Value T
  Errs  []error
}

func (v Validation[T]) Combine(w Validation[T]) Validation[T] {
  if len(v.Errs) > 0 {
    return Validation[T]{Errs: append(v.Errs, w.Errs...)}
  }
  if len(w.Errs) > 0 {
    return Validation[T]{Errs: append(v.Errs, w.Errs...)}
  }
  return v
}
```

## Lattice for permissions
```go
type PermSet map[string]struct{}

type Perm struct { Set PermSet }

func Join(a, b Perm) Perm { // union
  out := Perm{Set: map[string]struct{}{}}
  for k := range a.Set { out.Set[k] = struct{}{} }
  for k := range b.Set { out.Set[k] = struct{}{} }
  return out
}

func Meet(a, b Perm) Perm { // intersection
  out := Perm{Set: map[string]struct{}{}}
  for k := range a.Set {
    if _, ok := b.Set[k]; ok { out.Set[k] = struct{}{} }
  }
  return out
}
```

## Semiring-like scores
```go
type Score int

func Add(a, b Score) Score { return a + b }
func Mul(a, b Score) Score { return a * b }
```

## State machine transitions
```go
type State int

const (
  Draft State = iota
  Review
  Approved
  Published
)

func Step(s State) State {
  switch s {
  case Draft:
    return Review
  case Review:
    return Approved
  case Approved:
    return Published
  default:
    return Published
  }
}
```

## Fold with monoid
```go
func FoldLog(logs []Log) Log {
  acc := EmptyLog()
  for _, l := range logs {
    acc = CombineLog(acc, l)
  }
  return acc
}
```

## Normalization
```go
type Expr struct {
  Op   string
  A, B *Expr
  Lit  *int
}

func Normalize(e *Expr) *Expr {
  if e == nil { return nil }
  if e.Op == "add" && e.A != nil && e.A.Lit != nil && *e.A.Lit == 0 {
    return Normalize(e.B)
  }
  return &Expr{Op: e.Op, A: Normalize(e.A), B: Normalize(e.B), Lit: e.Lit}
}
```

## Homomorphism
```go
// len is a homomorphism from concatenation to addition:
// len(a + b) == len(a) + len(b)
```
