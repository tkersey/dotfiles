# Claim map

Every claim made with this skill should be marked as mathematical, programming, architecture inference, or repo observation.

## Foundational claims

- Claim: A left Kan extension of `F : C -> E` along `K : C -> D` consists of `Lan_K F : D -> E` and `η : F -> Lan_K F · K` such that `Nat(Lan_K F, G) ≅ Nat(F, G·K)` naturally in `G`.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`.
  - Unsafe use: claiming a codebase satisfies this without explicit categories and natural transformations.

- Claim: A right Kan extension of `F : C -> E` along `K : C -> D` consists of `Ran_K F : D -> E` and `ε : Ran_K F · K -> F` such that `Nat(G, Ran_K F) ≅ Nat(G·K, F)` naturally in `G`.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`.

- Claim: If both exist for fixed `K`, then `Lan_K ⊣ K* ⊣ Ran_K`, where `K*` is precomposition/restriction along `K`.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`.

- Claim: Pointwise `Lan_K F(d)` is computed by a colimit over `K ↓ d`; pointwise `Ran_K F(d)` is computed by a limit over `d ↓ K`.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`.

- Claim: In `Set`, the coend/end formulas are `(Lan_K F)(d) ≅ ∫^c D(Kc,d) × F(c)` and `(Ran_K F)(d) ≅ ∫_c F(c)^{D(d,Kc)}`.
  - Type: mathematical/programming bridge.
  - Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`, `[KAN-MILEWSKI-2017]`.

## Programming claims

- Claim: `Ran k d a` can be encoded in Haskell-style rank-n form as `forall i. (a -> k i) -> d i` under `Set`/Haskell-like interpretation.
  - Type: programming.
  - Sources: `[KAN-MILEWSKI-2017]`, `[KAN-HASKELL-KAN-EXTENSIONS]`.

- Claim: `Lan k d a` can be encoded as an existential package `exists i. (k i -> a, d i)`.
  - Type: programming.
  - Sources: `[KAN-MILEWSKI-2017]`, `[KAN-HASKELL-KAN-EXTENSIONS]`.

- Claim: Codensity is right-Kan/continuation-shaped and supports CPS-style optimization patterns; performance must be measured.
  - Type: programming.
  - Sources: `[KAN-HINZE-2012]`.
  - Unsafe use: promising speedups without workload-specific benchmarks or semantic tests.

## Data migration claims

- Claim: In functorial data migration, for a schema mapping `F : S -> T`, restriction is `Δ_F = precomposition`, with `Σ_F = Lan_F` and `Π_F = Ran_F` when the relevant Kan extensions exist.
  - Type: mathematical/programming bridge.
  - Sources: `[KAN-SPIVAK-WISNESKY-FQL-2014]`, `[KAN-SCHULTZ-WISNESKY-AQL-2015]`, `[KAN-RIEHL-CTIC]`.

## Architecture inferences

- Claim: `Lan` is a useful design lens for generative/free extension across an implementation boundary.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-RIEHL-CTIC]`; implementation analogies also informed by `[KAN-HINZE-2012]`.
  - Required witness: name the boundary `K`, the old semantics `F`, and the unit compatibility test.

- Claim: `Ran` is a useful design lens for conservative/coherent compatibility facades determined by observations.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-RIEHL-CTIC]`.
  - Required witness: name projections/observers and the counit compatibility test.

- Claim: A repository architecture “is a Kan extension.”
  - Type: unsafe unless fully modeled.
  - Required: explicit categories, functors, natural transformations, and a universal factorization proof or a clear statement that this is only an engineering analogy.
