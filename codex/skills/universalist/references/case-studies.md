# Universalist Case Studies

## Case 1 — Workflow flags to coproduct (TypeScript)

**Symptom**
A document lifecycle is represented by `status`, `approvedBy`, `publishedAt`,
and `archivedReason`.

**Construction**
Coproduct for lifecycle + product for shared metadata.

**Seam**
Legacy DTO decoder -> internal `DocState`.

**Proof**
- invalid legacy combinations rejected
- legal transitions preserved
- one consumer handles variants exhaustively

## Case 2 — Shared-id join to pullback witness (Go)

**Symptom**
A `Customer` and `Subscription` are paired repeatedly with manual `AccountID` checks.

**Construction**
Pullback-shaped witness over `AccountID`.

**Seam**
`NewCustomerSubscription` checked constructor.

**Proof**
- matching accepted
- mismatches rejected
- both projections preserved

## Case 3 — Repeated validation to refined type (Java or Python)

**Symptom**
Email addresses or non-empty identifiers are revalidated across layers.

**Construction**
Refined type or equalizer at the boundary.

**Seam**
Controller / serializer parse boundary.

**Proof**
- parse once
- valid accepted
- invalid rejected
- normalization idempotent

## Case 4 — Branchy policy logic to exponential (Java or C#)

**Symptom**
Pricing or policy logic uses long branches to pick behavior.

**Construction**
Exponential encoded as strategy, callable object, or closure.

**Seam**
One policy selection site plus one consumer.

**Proof**
- fixture parity against old behavior
- explicit composition order when policies chain

## Case 5 — Rule engine to free construction (TypeScript or Python)

**Symptom**
Workflow syntax, evaluation, and explanation are tangled together.

**Construction**
Free construction / initial algebra via AST + interpreters.

**Seam**
One rule family translated into the AST.

**Proof**
- evaluation parity on shared corpus
- explanation aligns with evaluation
