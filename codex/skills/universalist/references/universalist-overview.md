# Universalist Overview

## Table of contents
- Goal and stance
- Default loop
- Core constructions
- Capability-first fallback ladder
- Theory restraint

## Goal and stance
Treat universal constructions as practical design tools. Start from code and API shapes, not from category names. Pick the smallest construction that explains the code, encode it idiomatically, and show how to test it.

Universal constructions are useful because they specify behavior by what maps in or out of a type or API are allowed. In software terms, this means a design choice comes with a stable contract: how values are built, how they are consumed, and what laws or commuting checks should hold after refactors.

## Default loop
1. Inspect the repo's language, framework, type features, and test stack.
2. Find the signal in the code: products, variants, repeated validation, shared-key agreement, configurable behavior, or syntax/interpreter separation.
3. Choose the smallest construction that fits.
4. Translate it into the repo's idioms.
5. Explain the construction in plain engineering language.
6. Turn the universal property into executable tests or proxy checks.

## Core constructions
- **Product plus terminal object**: use for independent fields, grouped parameters, and no-information payloads.
- **Coproduct plus initial object**: use for exclusive cases, workflows, and impossible states.
- **Equalizer or refined type**: use when the same predicate is checked repeatedly at boundaries.
- **Pullback**: use when two views or records must agree on a shared projection.
- **Exponential**: use when behavior should be passed as a closure, function object, or strategy rather than hard-coded.
- **Free construction or initial algebra**: use when syntax should be modeled separately from interpretation.

Apply Algebra-Driven Design after choosing the construction when the inside of that construction wants monoids, lattices, semirings, homomorphisms, or normalization laws.

## Capability-first fallback ladder
Choose the strongest encoding the language and repo can support.
1. Native algebraic data types, exhaustive matching, and generics.
2. Sealed hierarchies, enums with payloads, records, and value objects.
3. Interfaces plus explicit tags, checked constructors, and witness structs.
4. Runtime validators, wrappers, and differential tests in dynamic languages.

Do not force typeclass-heavy or HKT-heavy encodings into languages that do not support them cleanly. Use the nearest honest encoding and say what remains runtime-only.

## Theory restraint
Lead with products, coproducts, equalizers, pullbacks, exponentials, and free constructions. Reach for adjunctions, Yoneda, Kan extensions, optics, monads or comonads as categorical abstractions, or higher-categorical coherence only when the prompt or codebase clearly demands them.
