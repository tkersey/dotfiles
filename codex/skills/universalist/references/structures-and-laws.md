# Structures and Universal-Property Catalog

## Products and terminal objects

**Plain-language contract**
A product is the best way to hold independent things together. To build one,
you provide each part. To consume one, you project each part.

**Use for**
- grouped parameters
- shared context
- return bundles
- stable metadata products around a state coproduct

**Validation**
- constructor and projection consistency
- independence of fields when that independence is claimed

**Avoid when**
- fields are really alternatives
- some combinations are illegal and central validation matters

## Coproducts and initial objects

**Plain-language contract**
A coproduct is the best way to say a value is one of several exclusive cases.

**Use for**
- lifecycles
- typed errors
- event variants
- impossible-state elimination

**Validation**
- exhaustive handling
- disjointness
- migration from legacy flag or nullable shapes into exactly one variant

**Avoid when**
- cases are actually a record with independent optional fields

## Equalizers and refined types

**Plain-language contract**
A refined type is the legal subset captured once at construction.

**Use for**
- non-empty identifiers
- emails, slugs, and normalized keys
- validated ranges
- versioned payload checks

**Validation**
- accept valid
- reject invalid
- normalization idempotence when normalization exists
- constructor-only entry

**Avoid when**
- the predicate depends on mutable external context
- the rule changes too fast to freeze into a stable type

## Pullbacks

**Plain-language contract**
A pullback witness is the best checked pair of two values that must agree on a
shared projection.

**Use for**
- same account / tenant / locale / schema version
- reconciling cache and DB views
- pairing request and permission context

**Validation**
- preserve both projections
- reject mismatches
- keep the proof in one constructor

**Avoid when**
- there is no stable shared projection worth encoding

## Exponentials

**Plain-language contract**
An exponential internalizes behavior from input to output.

**Use for**
- strategies
- renderers
- policy callbacks
- composable handlers

**Validation**
- fixture-based behavior tests
- parity against the old branchy implementation
- composition-order checks when composition matters

**Avoid when**
- the real issue is data or state modeling

## Free constructions and initial algebras

**Plain-language contract**
A free construction gives syntax without hidden execution. An interpreter or
fold gives one meaning for that syntax.

**Use for**
- rule engines
- workflows
- query builders
- AST or IR based subsystems

**Validation**
- interpreter consistency
- fold behavior on a sample corpus
- explanation output aligned with evaluation
- differential tests against the legacy evaluator during migration

**Avoid when**
- there is only one fixed execution path and no reuse benefit

## ADD sub-lens

Apply Algebra-Driven Design *inside* the chosen outer construction.

Common checks:

- **Semigroup**: associativity
- **Monoid**: associativity + identity
- **Join / meet semilattice**: associative + commutative + idempotent
- **Semiring**: distributivity + zero annihilation
- **Homomorphism**: structure preserved across mapping
- **Normalization**: idempotence

Use ADD after the shape is right, not as a substitute for the shape.
