# Defunctionalization claim map

## Foundational claims

- Claim: Defunctionalization is a program transformation that represents higher-order function values by first-order data constructors and replaces function application with an apply/interpreter function.
  - Type: programming.
  - Sources: `[KAN-REYNOLDS-1972]`, `[KAN-DANVY-NIELSEN-2001]`.
  - Unsafe use: claiming this transformation alone proves an architecture is correct.

- Claim: Defunctionalization is a bridge between higher-order and first-order specifications.
  - Type: programming.
  - Sources: `[KAN-DANVY-NIELSEN-2001]`.
  - Unsafe use: assuming every higher-order callback should be replaced by a datatype.

- Claim: CPS exposes continuations as functions, and defunctionalization can turn those continuations into explicit frames plus an apply function.
  - Type: programming.
  - Sources: `[KAN-DANVY-FILINSKI-1990]`, `[KAN-DANVY-NIELSEN-2001]`, `[KAN-HINZE-2012]`.
  - Unsafe use: conflating CPS, delimited continuations, defunctionalization, and Kan extensions as identical concepts.

## Kan relationship claims

- Claim: Defunctionalization is not itself a Kan extension or Kan lift; it is an implementation technique for making Kan-shaped higher-order boundary values first-order.
  - Type: architecture inference / programming bridge.
  - Sources: Kan side `[KAN-RIEHL-CTIC]`, `[KAN-NLAB-LIFT]`; defunctionalization side `[KAN-DANVY-NIELSEN-2001]`.
  - Required witness: name the boundary and the first-order constructors/interpreter.

- Claim: For `Lan`-shaped architecture, defunctionalization often turns maps/paths/generators into explicit `Path` or `GeneratedCase` data.
  - Type: architecture inference.
  - Sources: Kan side `[KAN-RIEHL-CTIC]`, `[KAN-MILEWSKI-2017]`; defunctionalization side `[KAN-DANVY-NIELSEN-2001]`.
  - Required witness: unit/old-behavior-preservation test.

- Claim: For `Ran`/codensity-shaped architecture, defunctionalization often turns observations/continuations into explicit `Observation` or `Frame` data.
  - Type: architecture inference / programming bridge.
  - Sources: `[KAN-HINZE-2012]`, `[KAN-DANVY-NIELSEN-2001]`.
  - Required witness: counit/coherence or semantic-equivalence test.

- Claim: For Kan-lift-shaped architecture, defunctionalization often turns implementation builders, predicates, and residuals into explicit `ImplementationPlan`, `Requirement`, or `Obligation` data.
  - Type: architecture inference.
  - Sources: Kan-lift side `[KAN-NLAB-LIFT]`; defunctionalization side `[KAN-DANVY-NIELSEN-2001]`.
  - Required witness: realization or residual soundness test through `P`.

## Unsafe claims

- Claim: A codebase architecture is correct because it uses defunctionalization.
  - Type: unsafe.
  - Required: concrete categories/functors or explicit engineering model, boundary map, constructors, interpreter, and tests.

- Claim: Defunctionalization always improves maintainability or performance.
  - Type: unsafe.
  - Required: maintainability rationale, ergonomics analysis, and performance measurements if performance is claimed.
