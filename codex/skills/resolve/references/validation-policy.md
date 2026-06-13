# Resolve Validation Policy

Review cleanliness is not validation.

After three consecutive clean reviews, run the full project validation suite using repository-native commands.

## Discovery sources

Prefer commands from:

- CI configuration;
- package scripts;
- Makefiles/task runners;
- project docs;
- language/tool skills;
- prior successful validation in the run.

## Validation failure

If validation fails:

1. capture command, output, and artifact state;
2. route contested actionability through `$review-adjudication` when needed;
3. run Review-Closure Abstraction Ladder when production mutation may result;
4. trigger Cluster Normalization Checkpoint when same-cluster failures repeat;
5. route surviving mutation through `$fixed-point-driver`;
6. run targeted validation for the fix;
7. reset clean streak;
8. restart review loop.

## No validation found

If no validation command exists, do not treat validation as passed.

Allowed outcomes:

- `blocked`: no credible validation route exists.
- `validation-only`: add/discover the smallest credible proof if mutation authority permits.
- `manual-only`: only when user explicitly accepts manual proof for this branch, and final report states the limitation.

Commit/push is blocked for `blocked` validation.

Manual-only proof must be named and tied to current artifact state.
