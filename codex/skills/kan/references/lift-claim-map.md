# Kan lift claim map

Every claim made with this skill should be marked as mathematical, programming, architecture inference, or repo observation.

## Foundational lift claims

- Claim: Given `P : B -> C`, postcomposition induces `P_* : [A, B] -> [A, C]` by `P_*(G) = P · G`.
  - Type: mathematical.
  - Sources: `[KAN-NLAB-LIFT]`.
  - Unsafe use: assuming a software projection is functorial without identifying objects and morphisms.

- Claim: A left Kan lift of `F : A -> C` through `P : B -> C`, when it exists, is a left adjoint value for postcomposition, with `η : F -> P · Lft_P F` and natural bijection `Nat(Lft_P F, G) ≅ Nat(F, P·G)`.
  - Type: mathematical.
  - Sources: `[KAN-NLAB-LIFT]`.
  - Unsafe use: calling any implementation synthesis step a left Kan lift without a comparison cell or factorization property.

- Claim: A right Kan lift of `F : A -> C` through `P : B -> C`, when it exists, is a right adjoint value for postcomposition, with `ε : P · Rft_P F -> F` and natural bijection `Nat(G, Rft_P F) ≅ Nat(P·G, F)`.
  - Type: mathematical.
  - Sources: `[KAN-NLAB-LIFT]`.
  - Unsafe use: treating “weakest obligation” as objective without specifying the order/2-cell direction.

- Claim: If both left and right Kan lifts exist for fixed `P`, they form an adjoint triple around postcomposition: `Lft_P ⊣ P_* ⊣ Rft_P`.
  - Type: mathematical.
  - Sources: `[KAN-NLAB-LIFT]`.

## Programming and architecture inferences

- Claim: A left Kan lift is a useful design lens for synthesizing an internal implementation behind a fixed projection/boundary.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-NLAB-LIFT]`.
  - Required witness: name `A`, `B`, `C`, `P`, `F`, and a test for `F -> P·implementation`.

- Claim: A right Kan lift is a useful design lens for deriving residual obligations, weakest requirements, or sound implementation constraints behind a fixed projection/boundary.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-NLAB-LIFT]`.
  - Required witness: name `A`, `B`, `C`, `P`, `F`, and a test for `P·implementation -> F`.

- Claim: In finite poset approximations, a left lift can be computed as a least implementation whose projection covers a desired behavior, and a right lift as a greatest implementation whose projection remains within a desired behavior.
  - Type: programming/architecture inference.
  - Sources: order-enriched reading of `[KAN-NLAB-LIFT]`.
  - Required witness: state the order direction and test minimality/maximality.

- Claim: A repository architecture “is a Kan lift.”
  - Type: unsafe unless fully modeled.
  - Required: explicit categories, postcomposition boundary `P`, desired behavior `F`, comparison cell, and universal factorization proof or a clear statement that this is only an engineering analogy.

## Architecture-playbook claims

- Claim: Lift-shaped refactors are useful for outside-in architecture changes where public commitments are fixed and internals must change behind a projection.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-NLAB-LIFT]` postcomposition framing.
  - Required witness: inventory public commitments, name `P : B -> C`, name `F : A -> C`, and add a projection law test.
  - Unsafe use: treating a vague public promise as `F` without fixtures, observations, reports, traces, or contract cases.

- Claim: A no-exact-lift report is the correct output when current `B` and `P` cannot produce an observation required by `F`.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-NLAB-LIFT]` best-approximation/residual reading.
  - Required witness: name the missing data, transition, capability, temporal guarantee, projection path, or coherence constraint.
  - Unsafe use: silently inventing behavior or claiming exact realization without information flow through `P`.

- Claim: An obligation ledger helps make right-lift/residual architecture work actionable.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-NLAB-LIFT]`; implementation discipline supplied by this skill.
  - Required witness: every ledger row links an external commitment to an observation in `C`, an internal artifact in `B`, a projection path through `P`, and a test.

- Claim: Yoneda/Coyoneda plus defunctionalization are useful implementation layers for lift-shaped work: observations on the `C` side, candidate realizers on the `B` side, and explicit projection paths through `P`.
  - Type: programming/architecture inference.
  - Sources: `[KAN-NLAB-LIFT]`, `[KAN-HASKELL-YONEDA]`, `[KAN-HASKELL-COYONEDA]`, `[KAN-DANVY-NIELSEN-2001]`.
  - Required witness: `PublicObservation`, `CandidateRealizer`, `ProjectionPath`, and `ImplementationObligation` or their domain-specific equivalents, plus projection law tests.
