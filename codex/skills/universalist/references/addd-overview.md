# Algebra-Driven Design (ADD) Overview

## Table of contents
- Goal and mindset
- Core moves
- Where ADD changes architecture
- Common pitfalls
- Sources

## Goal and mindset
ADD treats your domain as algebra: you discover the smallest structure that fits, encode it in types, and enforce laws with tests. The goal is to make architecture emerge from equations, not from ad hoc branching.

## Core moves
- **Observe**: list operations and invariants as equations or properties.
- **Algebraize**: choose the smallest structure (product, coproduct, monoid, lattice, semiring, functor).
- **Reify**: encode the structure in types and constructors.
- **Normalize**: define canonical forms and folds.
- **Prove by testing**: law tests, round-trips, homomorphisms, model-based tests.
- **Refactor by laws**: simplify code by algebraic rewrites, not micro-optimizations.

## Where ADD changes architecture
- **Boundaries** align with algebras (modules per structure).
- **Pipelines** become homomorphisms and folds.
- **State machines** become sum types plus lawful transitions.
- **Policies** become lattices/semirings (join/meet, combine).

## Common pitfalls
- Picking an abstraction before you can state laws.
- Modeling exceptions as booleans instead of data.
- Hiding algebra in untyped maps or JSON blobs.
- Treating laws as comments (they must be tests).

## Tooling availability check
Before you recommend tests or changes, verify tooling exists in the repo.
- Scan for existing test frameworks (`package.json`, `go.mod`, `cabal.project`, `stack.yaml`, `*.test.ts`, `*_test.go`).
- Prefer the existing test runner and patterns.
- If no property-testing tool exists, write deterministic law checks instead.
- Only propose new dependencies with explicit user approval.

## Sources
- https://algebradriven.design/
- https://sandymaguire.me/blog/algebra-driven-design/
- https://leanpub.com/algebra-driven-design
- https://www.lulu.com/shop/sandy-maguire-and-john-hughes/algebra-driven-design/hardcover/product-4j4rp4.html
