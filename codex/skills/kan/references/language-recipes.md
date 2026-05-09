# Language recipes

## TypeScript

Use tagged unions for `Observation`, `Path`, `Requirement`, and `ImplementationPlan`; centralize interpreters with exhaustive `switch`.

## Python

Use `dataclass(frozen=True)` for boundary cases and plain functions for projection laws.

## Rust

Use enums for defunctionalized cases and traits for interpreters; keep fallible lowering explicit with `Result`.

## Haskell

Use GADTs/existentials for `Lan`, rank-n encodings for `Ran`/codensity/Yoneda, and ordinary ADTs for defunctionalized IR.

## OCaml/Scala

Use variants/sealed traits for boundary cases and module/signature boundaries for projections and interpreters.
