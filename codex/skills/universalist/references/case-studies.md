# ADD Case Studies

## Table of contents
- Case 1: Pricing and promotions (Haskell)
- Case 2: Access control policies (Go)
- Case 3: Workflow state machine (TypeScript)

## Case 1: Pricing and promotions (Haskell)
**Domain**: A checkout pipeline with discounts, taxes, and fees.

**Algebra**: Monoid (composition of adjustments), Semiring (add/multiply for totals).

**Types**
```haskell
newtype Amount = Amount Int
newtype Adjust = Adjust { runAdjust :: Amount -> Amount }

instance Semigroup Adjust where
  Adjust f <> Adjust g = Adjust (g . f)

instance Monoid Adjust where
  mempty = Adjust id
```

**Laws**
- Identity: mempty <> a == a
- Associativity: a <> (b <> c) == (a <> b) <> c

**Architecture change**
- Replace a chain of conditionals with a list of Adjust.
- Fold adjustments into a single function via mconcat.
- Delete bespoke ordering code by using associativity law.

**Testing**
- Property test: applying mconcat of adjusts equals folding them sequentially.
- Round-trip: normalize promotions (sorted by priority) and prove idempotence.

## Case 2: Access control policies (Go)
**Domain**: Permissions from multiple sources (roles, feature flags, overrides).

**Algebra**: Join/meet semilattice on sets.

**Types**
```go
type PermSet map[string]struct{}

type Policy struct { Allow PermSet }

func Join(a, b Policy) Policy { /* union */ }
func Meet(a, b Policy) Policy { /* intersection */ }
```

**Laws**
- Commutative: Join(a,b) == Join(b,a)
- Idempotent: Join(a,a) == a
- Associative: Join(a, Join(b,c)) == Join(Join(a,b), c)

**Architecture change**
- Replace precedence rules with algebraic joins.
- Eliminate "override" flags; encode them as elements in the lattice.
- Co-locate policy merge logic in a single module with laws + tests.

**Testing**
- Property tests for commutative/idempotent/associative.
- Model-based test: compare policy evaluation to a simple reference interpreter.

## Case 3: Workflow state machine (TypeScript)
**Domain**: Document lifecycle with review, approval, publish, archive.

**Algebra**: Sum type for state, product for metadata, monoid for audit log.

**Types**
```ts
type State =
  | { tag: "Draft" }
  | { tag: "InReview"; reviewers: string[] }
  | { tag: "Approved"; approver: string }
  | { tag: "Published"; url: string }
  | { tag: "Archived"; reason: string };

type Doc = { state: State; title: string; body: string };
```

**Laws**
- Transition totality: every State must be handled.
- No illegal states: cannot be both Approved and Archived.

**Architecture change**
- Remove "status" string flags and boolean fields.
- Centralize transitions in a single pure function.
- Use exhaustive pattern matching to prevent illegal transitions.

**Testing**
- Property test: transitions preserve invariants (e.g., Published has url).
- Model-based test: state transition graph vs reference table.

