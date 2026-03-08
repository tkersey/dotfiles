# Go Examples

## Table of contents
- Product and terminal object
- Coproduct and initial object
- Refined type
- Pullback witness
- Exponential
- Free construction
- ADD sub-lens

## Product and terminal object
```go
type Money struct {
  Amount   int
  Currency string
}

type NoPayload struct{}
```

## Coproduct and initial object
```go
type DocState interface{ isDocState() }

type Draft struct{}
func (Draft) isDocState() {}

type InReview struct{ Reviewers []string }
func (InReview) isDocState() {}

type Published struct{ URL string }
func (Published) isDocState() {}
```

## Refined type
```go
type Email string

func NewEmail(s string) (Email, error) {
  if s == "" {
    return "", fmt.Errorf("empty email")
  }
  return Email(strings.ToLower(strings.TrimSpace(s))), nil
}
```

## Pullback witness
```go
type AccountID string

type Customer struct {
  AccountID AccountID
  Name      string
}

type Subscription struct {
  AccountID AccountID
  Plan      string
}

type CustomerSubscription struct {
  customer     Customer
  subscription Subscription
}

func NewCustomerSubscription(customer Customer, subscription Subscription) (CustomerSubscription, error) {
  if customer.AccountID != subscription.AccountID {
    return CustomerSubscription{}, fmt.Errorf("account mismatch")
  }
  return CustomerSubscription{customer: customer, subscription: subscription}, nil
}

func (cs CustomerSubscription) Customer() Customer { return cs.customer }
func (cs CustomerSubscription) Subscription() Subscription { return cs.subscription }
func (cs CustomerSubscription) AccountID() AccountID { return cs.customer.AccountID }
```

## Exponential
```go
type Formatter func(string) string

func WithPrefix(prefix string) Formatter {
  return func(body string) string {
    return prefix + body
  }
}
```

## Free construction
```go
type Expr interface{ isExpr() }

type Lit struct{ N int }
func (Lit) isExpr() {}

type Add struct {
  A Expr
  B Expr
}
func (Add) isExpr() {}

func Eval(e Expr) int {
  switch v := e.(type) {
  case Lit:
    return v.N
  case Add:
    return Eval(v.A) + Eval(v.B)
  default:
    return 0
  }
}
```

## ADD sub-lens
```go
type Log struct{ Lines []string }

func EmptyLog() Log { return Log{Lines: []string{}} }

func CombineLog(a, b Log) Log {
  out := make([]string, 0, len(a.Lines)+len(b.Lines))
  out = append(out, a.Lines...)
  out = append(out, b.Lines...)
  return Log{Lines: out}
}
```
