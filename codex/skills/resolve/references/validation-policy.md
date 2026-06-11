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
3. otherwise route through `$fixed-point-driver`;
4. run targeted validation for the fix;
5. reset clean streak;
6. restart review loop.

## No validation found

If no validation command exists, do not treat validation as passed.

Allowed outcomes:

- `blocked`: no credible validation route exists.
- `validation-only`: add/discover the smallest credible proof if mutation authority permits.
- `manual-only`: only when user explicitly accepts manual proof for this branch, and final report states the limitation.

Commit/push is blocked for `blocked` validation.

Manual-only proof must be named and tied to current artifact state.
