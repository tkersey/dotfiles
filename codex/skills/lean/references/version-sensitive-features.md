# Version-sensitive features

Lean, Std, Lake, and mathlib evolve. The repository's pinned toolchain is the source of truth.

## Always check the project

Inspect:

- `lean-toolchain`
- `lake-manifest.json`
- imports in the target file
- syntax used in nearby files
- tactics already accepted by the project
- CI commands and build targets

Do not assume current online examples apply to an older pinned project.

## Feature availability

Before using version-sensitive features, test them locally or inspect local files. Potentially version-sensitive areas include:

- tactic availability and syntax;
- `grind`, `bv_decide`, and their interactive integration;
- `omega`;
- `fun_induction`;
- `mvcgen`, `vcgen`, intrinsic contracts, or Hoare-logic facilities;
- equation compiler behavior;
- termination syntax;
- Lake file syntax;
- Std and mathlib module names;
- theorem names in Std and mathlib;
- native-evaluation axiom reporting;
- generated code and compiler attributes.

## Lean 4.34.0 migration notes

This is a release-specific reference, checked on 2026-09-15, not a minimum-version requirement or an instruction to upgrade. Apply only when the selected toolchain supports the feature; older projects keep their existing names and proof style.

| Area | Action under 4.34.0 |
| --- | --- |
| Conditional lemmas | `if_pos` / `if_neg` become `ite_eq_left` / `ite_eq_right`; `dif_pos` / `dif_neg` become `dite_eq_left` / `dite_eq_right`. Old names remain deprecated aliases. Follow actual warnings rather than mass-renaming older projects. |
| Bitvector normalization | `@[bv_normalize]` is now a `Sym.simp` set. Recheck custom normalization lemmas and proofs; do not assume the old matcher accepts exactly the same theorem shapes. |
| `String.toList` transparency | It is no longer implicitly reducible. Repair affected proofs with explicit rewrites rather than weakening the theorem or globally changing transparency. |
| `grind` plus bitvectors | `bv_decide` can consume the state of interactive `grind =>`. See `proof-playbook.md` for routing and `trust-audit.md` for native-computation assumptions. |
| Structured lint | `lake lint --code-quality` emits built-in linter JSON entries, including nonzero findings without a failing exit status. See `setup-and-workflow.md`; retain the project's lint gate. |
| Soundness fixes | The release fixes two kernel issues and one runtime reference-counting issue reachable through crafted input. For high-assurance/untrusted validation, check applicability and patched versions, including backports, using `trust-audit.md`. A version comparison alone is not a security audit. |

Source: [4.34.0 release notes at the reviewed manual revision](https://github.com/leanprover/reference-manual/blob/6624868291800878b94b5e58ad57bf642880ec39/Manual/Releases/v4_34_0.lean).

## Experimental intrinsic verification

`requires`, `ensures`, loop `invariant` clauses, and related `vcgen` facilities are experimental in 4.34.0. Do not infer support or stability from an example on a newer development branch. Inspect the pinned sources/imports and check a minimal example first; `mvcgen` and `vcgen` are not interchangeable names.

Prefer the existing pure spec/implementation/proof or transition-model architecture unless intrinsic contracts are an intentional fit. Do not mechanically migrate modules or imports between `Std.Internal.Do` and newer APIs such as `Std.WP`. In 4.34.0, `set_option experimental.intrinsic true` acknowledges the experimental syntax and silences its warning; it does not stabilize the API or strengthen a proof. Use it only after that choice is explicit, not as a blanket warning suppression.

Sources: the release notes above and [the experimental-syntax backport](https://github.com/leanprover/lean4/pull/14830). For another pin, use its release/tag sources, not moving `latest` documentation.

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

- current toolchain;
- desired toolchain;
- reason for upgrade;
- expected dependency impact;
- proof files likely to break;
- whether the change was requested or merely recommended.

For proof repair and correctness work, preserving the pinned environment is usually the right choice.
