---
name: universalist
description: "Algebra-Driven Design (ADD): model domains via minimal algebra + laws; encode in types; test laws."
---

# Universalist

## Intent
Use Algebra-Driven Design (ADD) to find the smallest algebra that fits the domain, encode it in types, and enforce laws with tests.

## Core workflow (ADD)
1. Frame the domain: observations, invariants, operations.
2. Pick the minimal algebra; avoid overfitting.
3. Define types: make illegal states unrepresentable.
4. State laws: identity, associativity, distributivity, absorption, round-trip, homomorphism.
5. Derive operations from the algebra (map/fold/compose) to reduce ad hoc branching.
6. Refactor architecture to match algebra boundaries.
7. Test the laws (property/model/metamorphic checks).
8. Iterate: if laws are hard to state or test, the algebra is likely wrong.

## Minimal-algebra decision guide
- Alternatives/variants → coproduct (tagged union)
- Independent fields → product (record/struct)
- Combine + identity → monoid
- Combine, no identity → semigroup
- Ordering/permissions → poset/lattice
- Add+multiply structure → semiring
- Structure-preserving map → functor
- Effectful apply → applicative
- Sequenced effects → monad

## Testing expectations
- Include law/property tests for the chosen algebra.
- Prefer property-based checks when the repo already supports them.
- If not, write minimal deterministic law checks in the existing test framework.
- Don’t assume tooling exists; propose new dependencies only with user approval.

## References
- `references/addd-overview.md`
- `references/addd-sources.md`
- `references/structures-and-laws.md`
- `references/testing-playbook.md`
- `references/case-studies.md`
- `references/examples-haskell.md`
- `references/examples-go.md`
- `references/examples-typescript.md`

## Scripts
- `scripts/emit_law_test_stub.sh` prints illustrative law-test stubs for Haskell, Go, or TypeScript.
