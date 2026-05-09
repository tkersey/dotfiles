# Freyd/AFT claim map

## Foundational claims

- Claim: A standard adjoint functor theorem gives conditions under which a limit-preserving/continuous functor is a right adjoint and therefore has a left adjoint.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`, `[KAN-NLAB-AFT]`, `[KAN-MACLANE-CWM]`.
  - Unsafe use: claiming a software projection has a left adjoint without modeling the categories, limits, and size assumptions.

- Claim: The solution-set condition weakens the existence of a universal solution to the existence of a small family of weak candidates through which all solutions factor.
  - Type: mathematical / architecture inference.
  - Sources: `[KAN-RIEHL-CTIC]`, `[KAN-NLAB-SOLUTION-SET]`.
  - Architecture reading: each public requirement should have a bounded menu of implementation templates.

- Claim: For a lift-shaped refactor `A --?--> B`, `F : A -> C`, and `P : B -> C`, if `P` has a left adjoint `Free`, then `Free · F : A -> B` is a canonical implementation-side candidate.
  - Type: mathematical/programming bridge when categories are explicit; otherwise architecture inference.
  - Sources: follows from adjunction composition and the lift/postcomposition framing in `[KAN-NLAB-LIFT]` plus AFT sources.
  - Unsafe use: treating `Free · F` as an exact implementation without checking the unit/comparison and projection law.

## Architecture inferences

- Claim: Kan lifts locate outside-in refactor problems, while Freyd/AFT disciplines the projection boundary `P` by asking whether it has enough structure to support a canonical free builder.
  - Type: architecture inference.
  - Sources: grounded in `[KAN-NLAB-LIFT]`, `[KAN-RIEHL-CTIC]`, `[KAN-NLAB-AFT]`.
  - Required witness: concrete `A`, `B`, `C`, `P`, `F`, candidate `Free`, exactness classification, and a projection law test.

- Claim: A solution-set-like implementation-template inventory is useful for agentic architecture because it bounds the search space behind a projection.
  - Type: architecture inference.
  - Required witness: name templates and show how representative requirements factor through them.

- Claim: A no-exact-lift obstruction can often be diagnosed by finding an observation required by `F` that is not stored, derivable, externally obtainable, or projected by `P`.
  - Type: architecture inference.
  - Required witness: one public observation, current internal information sources, and repair options.

## Unsafe claims

- “Freyd's theorem proves this service architecture is correct.” Unsafe unless the architecture is formalized as categories/functors and all hypotheses hold.
- “Every projection has a free implementation builder.” False; AFT gives hypotheses, not a universal guarantee.
- “Free implementation means minimal code.” Misleading; free means universal/general, not necessarily small or efficient.
