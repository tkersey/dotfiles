# Trust audit

Use this reference for production verification, high-assurance claims, foundational trust, proof certificates, generated-code claims, or external-code claims.

## Toolchain soundness and provenance

For this audit lane, record the selected Lean version, project pin, dependency revisions, and any checker versions/origins used. Consult official release notes or soundness advisories relevant to that toolchain and validation path. Do this for high-assurance/untrusted validation or upgrade decisions, not as a release-checking ritual during every ordinary proof edit.

Lean 4.34.0 fixes three soundness issues involving crafted input: two in the kernel and one in runtime reference counting. This does not establish that ordinary existing developments are invalid. Determine which fixes or backports apply to the environment being audited; report the affected path, evidence, and a patched version when needed. Preserve project pins during ordinary work and recommend a separate upgrade rather than silently changing the environment.

For untrusted artifacts, including unreviewed generated proofs, isolate builds and elaboration before executing them: tactics, macros, imports, and build steps can execute code. Do not first run an untrusted build on the host and sandbox only its final checker. For high-risk validation, use a trusted statement/challenge and a sandboxed comparator/external-checker workflow when available; report unavailable validation steps rather than substituting a clean build for them.

An empty `#print axioms` result does not establish checker soundness, runtime safety, or fidelity of the formal statement. A second checker is additional evidence, not a guarantee that it cannot share a bug. Record the actual checks and remaining assumptions.

Sources: [reviewed 4.34.0 release notes](https://github.com/leanprover/reference-manual/blob/6624868291800878b94b5e58ad57bf642880ec39/Manual/Releases/v4_34_0.lean) and [Lean proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/). For another version, check its own sources and advisories.

## Placeholder scan

Search changed Lean files for:

- `sorry`
- `admit`
- `axiom`
- unsolved goals
- temporary `example` declarations that should not remain
- intentionally weakened theorem statements

No verification claim should depend on a placeholder unless the user explicitly requested a sketch.

## Trust-expanding feature scan

Search for:

- `unsafe`
- `partial`
- `noncomputable`
- `native_decide`
- `decide +native`
- `bv_decide` / `bv_decide?`
- `bv_check`
- `implemented_by`
- `@[implemented_by]`
- `csimp`
- `@[csimp]`
- `extern`
- IO, FFI, filesystem, network, clock, randomness, environment, concurrency, or adapter boundaries when the theorem is being presented as software correctness.

These are not all forbidden, but they must be reported when relevant to the final claim. Use `scripts/lean_trust_audit.sh` for the packaged lexical scan. It prints matches for review; findings and no matches both exit zero, while scan errors exit nonzero. It is line-based and may match comments/strings or miss indirect, generated, imported, or multiline uses. Its identifier boundaries are a portable approximation, not a Lean lexer. Inspect actual declarations and theorem dependencies; absence of matches is not a trust certificate.

## Axiom footprint

For every top-level theorem supporting the final correctness claim, inspect:

```lean
#print axioms theorem_name
```

Report the result. Useful classifications:

- no axioms;
- only standard accepted axioms, such as propositional extensionality, quotients, or classical choice;
- `sorryAx` or other incomplete proof dependency;
- project-local/custom axioms;
- native-evaluation/compiler trust, including older `Lean.trustCompiler` or newer native-computation assertion axioms;
- unsafe/runtime/compiler/FFI trust;
- external model-correspondence assumptions.

## Interpreting common cases

### `axiom`

Project-local axioms are assumptions. They can make Lean accept false propositions if inconsistent. Avoid them for correctness claims unless the user explicitly wants an axiomatized model.

### `noncomputable`

Often fine in pure mathematics. Usually inappropriate for executable verified programs unless the theorem is intentionally non-executable or the noncomputable part is outside the execution claim.

### `partial`

Usually unsuitable for logic-facing correctness proofs. Prefer total functions with structural recursion, fuel, measures, or well-founded recursion.

### Native evaluation

`native_decide`, `decide +native`, and `bv_decide` can increase the trusted computing base through native compilation and computation assertions. Include `bv_decide?` and `bv_check` certificate workflows in this review; replay does not by itself prove the result is kernel-only. Inspect `#print axioms` on the resulting theorem, including imported dependencies.

Since Lean 4.29.0, `decide +native` and `bv_decide` introduce dedicated axioms for individual native computations rather than the older `Lean.trustCompiler` dependency. Do not whitelist an unfamiliar generated axiom just because that older name is absent. Distinguish these computation assertions from standard logical axioms and arbitrary project-local assumptions. Prefer kernel-checkable reduction, ordinary `decide`, `simp`, or an explicit proof when native trust is unacceptable.

### `@[implemented_by]`

This can replace the compiled implementation of a definition. It does not itself prove the replacement implementation matches the logical definition. Audit carefully for executable-correctness claims.

### `@[csimp]`

This can affect compiled behavior. Audit carefully when the claim is about executable code, not only the logical theorem.

### `unsafe`

Unsafe code may be necessary at runtime boundaries, but it is not kernel-checked proof evidence. Isolate it behind a pure checked model when possible.

## Validation ladder

After selecting an appropriate toolchain and isolating any untrusted execution as above, use the lowest level appropriate to risk:

1. `lake env lean path/to/File.lean` or `lake build +Module.Name` succeeds.
2. Placeholder scan is clean.
3. `#print axioms` for theorem dependencies is reviewed.
4. `lake build` succeeds.
5. `lean4checker --fresh Module.Name` succeeds when available and appropriate.
6. For adversarial/untrusted proof artifacts, use sandboxed comparator/external checker workflows and inspect statement fidelity, notation, typeclasses, and imported axioms.

## Final audit format

```text
Placeholder status: none found.
Axiom/trust status: theorem `foo_eq_spec` has no project-local axioms. No `unsafe`, `partial`, `native_decide`, `decide +native`, `bv_decide`, `bv_check`, `@[implemented_by]`, or `@[csimp]` appears in the changed files. This source scan alone does not establish absence of imported native-computation assumptions.
```

If there are assumptions:

```text
Axiom/trust status: `foo_sound` depends on classical choice through imported library theorem X. The executable wrapper uses IO and filesystem state outside the Lean proof boundary.
```
