# Claim map

Every claim made with this skill should be marked as mathematical, programming, architecture inference, or repo observation.

## Foundational claims

- Claim: `Lan_K F` is left adjoint to restriction/precomposition along `K`, and `Ran_K F` is right adjoint to it when these adjoints exist.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`, `[KAN-MACLANE-CWM]`.

- Claim: Pointwise `Lan` and `Ran` can be computed by comma-category colimits and limits when the relevant pointwise Kan extensions exist.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`.

- Claim: Global Kan lifts are adjoints to postcomposition by a fixed functor/projection.
  - Type: mathematical.
  - Sources: `[KAN-NLAB-LIFT]`.

- Claim: Freyd/AFT gives conditions under which a functor is a right adjoint and therefore has a left adjoint/free builder.
  - Type: mathematical.
  - Sources: `[KAN-RIEHL-CTIC]`, `[KAN-NLAB-AFT]`.

## Architecture inferences

- Claim: `Lan` is useful for generated/free pushforward architecture.
  - Required witness: `C`, `D`, `K`, `F`, unit law.

- Claim: `Ran` is useful for compatibility facades and coherent observation records.
  - Required witness: `C`, `D`, `K`, `F`, counit law.

- Claim: Kan lifts are useful for outside-in refactors where public behavior is fixed and internals are unknown.
  - Required witness: `A`, `B`, `C`, `P`, `F`, comparison law.

- Claim: Freyd/AFT practice disciplines a lift projection by checking constraints, preservation, and bounded templates.
  - Required witness: projection `P`, constraints in `B`, preservation test, solution-set-like templates, `Free` law.

Unsafe: saying a repository “is a Kan extension/lift” without explicit data and tests.
