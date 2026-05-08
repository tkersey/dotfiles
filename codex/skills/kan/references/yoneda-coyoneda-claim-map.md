# Yoneda/Coyoneda claim map

## Mathematical / programming claims

- Claim: `Yoneda f a` has the Haskell-shaped representation `forall b. (a -> b) -> f b` and is naturally isomorphic to `f a` in the usual functor setting.
  - Type: mathematical/programming bridge.
  - Sources: `[KAN-MILEWSKI-YONEDA]`, `[KAN-HASKELL-YONEDA]`.
  - Unsafe use: claiming a TypeScript or Python wrapper is a lawful Yoneda encoding without parametricity or explicit laws.

- Claim: `Coyoneda f a` has the Haskell-shaped representation `exists b. f b × (b -> a)` and acts as a free functor construction over `f` in programming practice.
  - Type: mathematical/programming bridge.
  - Sources: `[KAN-MILEWSKI-YONEDA]`, `[KAN-HASKELL-COYONEDA]`.
  - Unsafe use: treating arbitrary `payload + callback` pairs as useful architecture without a lowering interpreter and tests.

- Claim: Yoneda is right-Kan-like and Coyoneda is left-Kan-like in common Haskell Kan-extension libraries and expositions.
  - Type: programming/expository.
  - Sources: `[KAN-HASKELL-KAN-EXTENSIONS]`, `[KAN-HASKELL-YONEDA]`, `[KAN-HASKELL-COYONEDA]`, `[KAN-MILEWSKI-YONEDA]`.
  - Unsafe use: replacing the actual `Lan`/`Ran` or lift boundary classification with this local representation analogy.

## Architecture inferences

- Claim: Yoneda is useful as an architecture lens for observation-heavy boundaries because it encourages representation by sanctioned observations.
  - Type: architecture inference.
  - Sources: inspired by `[KAN-MILEWSKI-YONEDA]` and `[KAN-HASKELL-YONEDA]`.
  - Required witness: an explicit `Observation` or observer interface and a law test showing representation-independent observation.

- Claim: Coyoneda is useful as an architecture lens for generation-heavy boundaries because it packages raw payloads with deferred transformations.
  - Type: architecture inference.
  - Sources: inspired by `[KAN-MILEWSKI-YONEDA]` and `[KAN-HASKELL-COYONEDA]`.
  - Required witness: an explicit source payload, deferred path/map, lowering function, and fusion/provenance test.

- Claim: In Kan lift architecture, Yoneda can model public observations while Coyoneda can model candidate implementation realizers.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-NLAB-LIFT]` plus the programming representations above.
  - Required witness: a projection `P`, public observation cases, candidate realizer cases, and a realization test.

## Unsafe claims

- Claim: A codebase architecture is correct because it uses Yoneda or Coyoneda.
  - Type: unsafe.
  - Required: explicit boundary, representation, interpreter, and law tests.

- Claim: Yoneda/Coyoneda add value even when they do not change code shape.
  - Type: unsafe.
  - Safer version: use them only when they centralize observers, defer transformations, preserve provenance, support fusion, improve auditability, or make laws testable.
