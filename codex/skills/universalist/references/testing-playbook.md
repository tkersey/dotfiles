# Universalist Testing Playbook

## Table of contents
- Start with the repo you have
- Turn diagrams into tests
- Construction-specific checks
- ADD sub-lens checks
- Model, round-trip, golden, and differential tests
- Tool discovery by language

## Start with the repo you have
Before you recommend tests or changes, verify tooling exists in the repo.
- Prefer the existing test runner and assertion style.
- Prefer table-driven, model-based, or deterministic checks when no property-testing tool is present.
- Only propose new dependencies after explicit user approval.

## Turn diagrams into tests
Universal properties rarely show up as one magic assertion. Turn them into small executable proxies.
- **Product**: constructor and projection consistency.
- **Coproduct**: exhaustive handling and one-variant-only checks.
- **Equalizer or refined type**: accept valid, reject invalid, and normalize idempotently if normalization exists.
- **Pullback**: preserve both projections and reject mismatched witnesses.
- **Exponential**: show application behavior and composition on representative fixtures.
- **Free construction**: compare interpreters, folds, or legacy behavior on the same syntax tree.

## Construction-specific checks
**Products and terminal objects**
- Projection tests: building then reading fields gives back the original parts.
- If a terminal payload exists, prove it carries no meaningful information in the surrounding API.

**Coproducts and initial objects**
- Exhaustiveness: every case is handled once.
- Disjointness: no value is simultaneously two variants.
- Migration: legacy flags or nullable fields map to exactly one variant.
- Use deterministic fixtures for invalid legacy combinations, not just happy-path cases.
- Add `decode -> encode` or equivalent boundary checks when a legacy wire shape is being staged behind a tagged union.

**Equalizers and refined types**
- Construction is the only way in.
- Invalid values fail at the boundary.
- Normalization, if present, is idempotent.

**Pullbacks**
- Checked constructor rejects mismatched keys or projections.
- The resulting witness exposes both original views without losing information.
- Mutating operations preserve the shared witness or force reconstruction.
- In Go or mutable OO code, package visibility and field mutability determine whether the constructor is truly the only way in.

**Exponentials**
- Functions, closures, or strategies produce the same outputs as the old branchy implementation on agreed fixtures.
- If behavior is composed, test the composition order explicitly.

**Free constructions and initial algebras**
- Multiple interpreters agree where they should.
- A fold-based interpreter matches the old evaluator on a sample corpus.
- Explanation or pretty-print interpreters stay consistent with evaluation on the same syntax tree.
- Serialization or pretty-printing round-trips if the syntax is persisted.

## ADD sub-lens checks
When the chosen construction contains algebraic structure, include executable laws.
- Monoid: identity and associativity.
- Semiring: distributivity and zero annihilation.
- Lattice: associativity, commutativity, and idempotence.
- Functor: identity and composition.
- Monad: left identity, right identity, and associativity when the repo already uses that abstraction.
- Homomorphism: `h(op(a, b)) == op'(h(a), h(b))`.

## Model, round-trip, golden, and differential tests
- **Model-based**: compare behavior to a small trusted model.
- **Round-trip**: `decode(encode(x)) == x` or parser/printer equivalents.
- **Metamorphic**: `f(x)` and `f(g(x))` preserve a required relation.
- **Golden**: snapshot canonical forms or rendered output when readability matters.
- **Differential**: compare the new universal-construction-based implementation against the legacy implementation during migration.

## Tool discovery by language
Always confirm the best tool in the target language and ecosystem.
- First, scan the repo for existing test frameworks; prefer the current stack.
- If no property-testing tool is present, write deterministic checks using the current test runner.
- Search for standard library support before third-party libraries.

Known baselines to verify in repo context:
- Haskell: QuickCheck, Hedgehog
- Go: `testing/quick` in the standard library; `rapid` or `gopter` if already present
- TypeScript: `fast-check`
