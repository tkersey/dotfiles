# Structures and Universal-Property Catalog

## Table of contents
- Products and terminal objects
- Coproducts and initial objects
- Equalizers and refined types
- Pullbacks
- Exponentials
- Free constructions and initial algebras
- ADD sub-lens
- Advanced reference tier

## Products and terminal objects
**Property**
- A product `A x B` is the best way to hold `A` and `B` together.
- To give `X -> A x B` is equivalent to giving both `X -> A` and `X -> B`.
- A terminal object is the unique no-information payload.

**Use**
- Independent fields, grouped parameters, return bundles, shared context, `unit` or `struct{}` payloads.

**Code shape**
- Record, struct, tuple, or object with projections.

**Validation**
- Constructor and projection consistency.
- If fields are meant to be independent, avoid hidden conditional coupling between them.

**Avoid when**
- The fields are really alternatives or some combinations are illegal without extra checks.

## Coproducts and initial objects
**Property**
- A coproduct `A + B` is the best way to say a value is either `A` or `B`.
- To give `A + B -> X` is equivalent to giving one handler for `A` and one for `B`.
- An initial object is the impossible case with no inhabitants.

**Use**
- Workflows, typed errors, event variants, state machines, partial parsing results.

**Code shape**
- Tagged union, enum with payload, sealed interface, interface plus discriminant, or visitor.

**Validation**
- Exhaustive handling.
- Disjointness: every value is exactly one variant.

**Avoid when**
- The cases are actually a record with optional independent fields.

## Equalizers and refined types
**Property**
- An equalizer is the best subset where two observations agree.
- In code, this usually appears as a refined type or checked constructor for values satisfying one stable predicate.

**Use**
- Email addresses, non-empty strings, normalized identifiers, versioned payloads, validated ranges.

**Code shape**
- Smart constructor, parser, value object, normalized wrapper, constructor plus error.

**Validation**
- Accept valid inputs.
- Reject invalid inputs.
- If normalization exists, prove idempotence.

**Avoid when**
- The predicate depends on mutable external context or is too unstable to capture once.

## Pullbacks
**Property**
- A pullback is the best way to hold `X` and `Y` together while forcing their projections into `Z` to agree.
- In code, this is a checked witness that two views belong to the same account, tenant, locale, schema version, or other shared key.

**Use**
- Joining two records over a shared identifier, reconciling cache and DB views, pairing request and permission context.

**Code shape**
- Checked composite struct, witness object, validated pair with preserved projections.

**Validation**
- Preserve both projections.
- Reject mismatches.
- Keep the agreement proof in one constructor.

**Avoid when**
- A plain pair plus occasional assertions is enough and there is no stable shared projection worth encoding.

## Exponentials
**Property**
- An exponential `B^A` internalizes functions from `A` to `B`.
- To give `X -> B^A` corresponds to giving `X x A -> B`.

**Use**
- Closures, strategy objects, dependency injection, render functions, policy callbacks, composable handlers.

**Code shape**
- Function, closure, callable object, strategy interface, or configuration plus callable.

**Validation**
- Exercise application behavior with representative fixtures.
- Check composition or adapter rules when the repo already composes these functions.

**Avoid when**
- The problem is really data modeling or state classification rather than behavior parameterization.

## Free constructions and initial algebras
**Property**
- A free construction gives syntax with no extra equations beyond the chosen operations.
- An initial algebra gives the canonical fold out of that syntax into any interpreter.

**Use**
- Query builders, command ASTs, rule engines, workflows, compiler IR, serialization formats with multiple interpreters.

**Code shape**
- AST or IR nodes plus explicit interpreters, folds, or evaluators.

**Validation**
- Interpreter consistency.
- Fold or evaluation laws.
- Round-trip or differential tests against legacy behavior.

**Avoid when**
- There is only one hard-coded execution path and the syntax tree adds no separation benefit.

## ADD sub-lens
Use Algebra-Driven Design after choosing the outer construction.

**Semigroup**
- `op(a, op(b, c)) == op(op(a, b), c)`
- Use for logs, config merges, validation accumulation.

**Monoid**
- Semigroup plus identity `empty`
- Laws:
  - `a <> (b <> c) == (a <> b) <> c`
  - `empty <> a == a`
  - `a <> empty == a`
- Use for aggregation, folds, accumulation.

**Join or meet semilattice**
- associative, commutative, idempotent
- Use for permissions, conflict resolution, feature flags.

**Semiring**
- additive and multiplicative structure with distributivity and zero annihilation
- Use for costs, scoring, path weights, policy composition.

**Functor, Applicative, Monad**
- Use when the repo already works with mapped, lifted, or sequenced computations.
- Keep the language and ecosystem idiomatic; do not force these names into codebases that do not use them.

**Homomorphisms and normal forms**
- `h(op(a, b)) == op'(h(a), h(b))`
- `normalize(normalize(x)) == normalize(x)`
- Use these as refactor criteria and regression checks.

## Advanced reference tier
- **Pushouts, coequalizers, and quotients**: good for merge and identification problems, especially schema or API gluing.
- **Adjunctions**: useful to explain free versus forgetful relationships and best approximations.
- **Representables and Yoneda**: useful for generic-element reasoning and some polymorphic representation theorems.
- **Kan extensions**: useful for schema migration, data transport, and shape-changing semantics.
- **Monads and comonads as categorical abstractions**: useful when effects or contexts are already first-class in the repo.
- **Ends, coends, and optics**: useful when the codebase already uses profunctors, lenses, prisms, or advanced encodings.
- **Higher-categorical coherence**: keep in reserve for explicit homotopy or dependent-type semantics prompts.

Do not lead with the advanced tier unless the prompt or codebase already operates there.
