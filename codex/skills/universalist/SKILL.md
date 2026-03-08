---
name: universalist
description: "Use when a repo needs universal-construction-driven modeling or refactors: replace flag matrices with tagged unions, repeated validation with refined types, ad hoc joins with checked witnesses, hard-coded behavior with closures or strategy objects, or mini-DSLs with free ASTs; choose idiomatic encodings and tests in any programming language."
---

# Universalist

## Intent
Identify the smallest universal construction that explains the code, encode it in the target language's idioms, and validate it with executable laws or diagram-shaped proxy tests.

## Core workflow
1. Inspect repo reality: language, type features, framework conventions, serialization boundaries, and test stack.
2. Identify the signal: independent fields, exclusive variants, repeated validation, shared-key agreement, configurable behavior, or syntax/interpreter separation.
3. Choose the smallest construction that fits. Prefer products, coproducts, equalizers or refined types, pullbacks, exponentials, and free constructions before advanced machinery.
4. Encode idiomatically. Use native ADTs when available; otherwise use sealed hierarchies, interfaces, tagged structs, wrappers, validators, or AST/interpreter splits.
5. State the universal property in plain language: what constructors and eliminators exist, and what factorization or uniqueness behavior they buy.
6. Turn the diagram into tests. Prefer the repo's current property, model, table-driven, or differential test stack; add dependencies only with approval.
7. Call out migration edges and adapter-first staging: public API breaks, serialization changes, persistence constraints, runtime-only guarantees, and when a small refactor should keep wire or storage shapes stable behind boundary decoders.
8. Escalate to advanced references only when the prompt or codebase clearly needs adjunctions, Kan extensions, optics, monads or comonads, or higher-categorical coherence.

## Practical decision guide
- Independent fields that must coexist -> product plus terminal object
- Mutually exclusive cases or impossible states -> coproduct plus initial object
- Repeated boundary predicates -> equalizer or refined type
- Two models must agree on a shared id or projection -> pullback-shaped join
- Behavior should be passed rather than branched -> exponential, closure, or function object
- Syntax should be separated from execution -> free construction or initial algebra
- Combine plus identity, lattice rules, semiring structure, or lawful effects -> apply ADD as a sub-lens inside the chosen construction

## Output contract
- Name the observed signal in the repo.
- Name the candidate construction and why nearby alternatives are worse.
- Show the smallest idiomatic encoding for the target language.
- Specify validation: law tests, exhaustive handling, round-trips, commuting-diagram proxies, or differential tests.
- For dynamic or weakly typed languages, name the trusted constructor, the eliminator, and any boundary adapters or decoders.
- Note what remains runtime-only, what breaks public APIs, and what to stage behind adapters.

## Guardrails
- Prefer plain engineering language over category jargon when both say the same thing.
- Do not claim a universal construction without showing constructors, eliminators, or factorization behavior.
- Do not recommend typeclass-heavy or HKT-heavy patterns in languages that cannot support them cleanly.
- Do not add property-testing or effect libraries without explicit user approval.
- Keep advanced theory in `references/sources.md` and the advanced tier of `references/structures-and-laws.md`.

## References
- `references/universalist-overview.md`
- `references/discovery-signals.md`
- `references/language-encoding-matrix.md`
- `references/structures-and-laws.md`
- `references/testing-playbook.md`
- `references/case-studies.md`
- `references/examples-haskell.md`
- `references/examples-go.md`
- `references/examples-typescript.md`
- `references/sources.md`

## Scripts
- `scripts/emit_law_test_stub.sh` prints illustrative algebra-law stubs for Haskell, Go, or TypeScript when the chosen construction is algebraic and the repo already supports those styles.
