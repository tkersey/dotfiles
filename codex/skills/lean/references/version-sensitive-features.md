# Version-sensitive features

Lean and mathlib evolve. The repository's pinned toolchain is the source of truth.

## Always check the project

Inspect:

- `lean-toolchain`
- `lake-manifest.json`
- imports in the target file
- syntax used in nearby files
- tactics already accepted by the project

Do not assume current online examples apply to an older pinned project.

## Feature availability

Before using version-sensitive features, test them locally or inspect local files.

Potentially version-sensitive areas include:

- tactic availability and syntax
- `grind`
- `omega`
- `fun_induction`
- equation compiler behavior
- termination syntax
- Lake file syntax
- Std and Mathlib module names
- Hoare-logic or monadic verification facilities
- theorem names in Std and Mathlib

## Fallback strategy

When a modern tactic or feature is unavailable:

1. Try explicit structural proof.
2. Use local helper lemmas.
3. Use `simp`, `rw`, `cases`, and `induction`.
4. Use domain tactics already present in the repo.
5. Refactor the definition or theorem shape.

Do not upgrade the project unless the user explicitly asks for an upgrade or the task cannot reasonably be done under the pinned toolchain.

## Toolchain upgrades

If an upgrade is necessary, report:

- current toolchain
- desired toolchain
- reason for upgrade
- expected dependency impact
- proof files likely to break
- whether the change was requested or merely recommended

For proof repair and correctness work, preserving the pinned environment is usually the right choice.
