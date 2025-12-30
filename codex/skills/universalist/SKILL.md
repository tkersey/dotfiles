---
name: universalist
description: Algebra-driven design skill for deriving architecture and APIs from algebraic structures and laws. Use when modeling domains with sum/product types, monoids, functors/applicatives/monads, or lattices; when refactoring toward algebraic clarity; when defining and testing laws with property-based tests; or when you need ADD-driven architectural change in Haskell, Go, or TypeScript.
---

# Universalist

## Overview
Use Algebra-Driven Design (ADD) to discover the smallest algebra that fits the domain, encode it in types, and enforce laws with tests. Prefer minimal constructions (product/coproduct/monoid) before heavier abstractions. Breaking changes are acceptable; prioritize algebraic clarity over backwards compatibility.

## Core Workflow (ADD)
1. **Frame the domain**: list observations, invariants, and operations (verbs). Capture what must always hold.
2. **Pick the minimal algebra**: product, coproduct, monoid/semigroup, lattice, semiring, functor/applicative/monad. Avoid overfitting.
3. **Define types**: make illegal states unrepresentable (newtypes, tagged unions, smart constructors).
4. **State laws**: identity, associativity, distributivity, absorption, round-trip, homomorphism.
5. **Derive operations**: fold/map/compose from the algebra; reduce ad hoc branching.
6. **Architectural refactor**: align modules to algebra boundaries; remove glue layers that violate laws.
7. **Test the laws**: property-based tests, model-based tests, metamorphic checks, and law discovery.
8. **Iterate**: if laws are hard to state or test, your algebra is likely wrong.

## Decision Tree: Minimal Algebra
- Alternatives or variants? -> **Coproduct** (tagged union).
- Independent fields? -> **Product** (record/struct).
- Combine values with a neutral element? -> **Monoid**.
- Combine without neutral element? -> **Semigroup**.
- Ordering or permissions? -> **Lattice/poset**.
- Two combines (add/multiply)? -> **Semiring**.
- Structure-preserving map? -> **Functor**.
- Effectful apply? -> **Applicative**.
- Sequenced effects? -> **Monad**.

## Testing Expectations
- Always include law/property tests for the chosen algebra.
- Prefer property-based checks over example tests for laws.
- Use law discovery (QuickSpec or equivalents) when you can.
- Do not assume tooling exists: detect what the repo already uses, prefer it, and only suggest new dependencies with user approval.
- If no property-testing tool is available, write minimal deterministic law checks in the existing test framework.

## Language Focus
- **Haskell**: read `references/examples-haskell.md`.
- **Go**: read `references/examples-go.md`.
- **TypeScript**: read `references/examples-typescript.md`.

## Deep Dives
- ADD primer and sources: `references/addd-overview.md` and `references/addd-sources.md`.
- Law catalog + checks: `references/structures-and-laws.md`.
- Testing playbook: `references/testing-playbook.md`.
- Larger worked case studies: `references/case-studies.md`.

## Scripts
- `scripts/emit_law_test_stub.sh` prints illustrative law-test stubs for Haskell, Go, or TypeScript.
