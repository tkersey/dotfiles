# Trust audit

Use this reference for production verification, high-assurance claims, foundational trust, proof certificates, generated-code claims, or external-code claims.

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
- `implemented_by`
- `@[implemented_by]`
- `csimp`
- `@[csimp]`
- `extern`
- IO, FFI, filesystem, network, clock, randomness, environment, concurrency, or adapter boundaries when the theorem is being presented as software correctness.

These are not all forbidden, but they must be reported when relevant to the final claim.

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

`native_decide`, `decide +native`, and tactics that rely on native computation can increase the trusted computing base by depending on native compilation or native-computation assertion axioms. Prefer kernel-checkable reduction, ordinary `decide`, `simp`, or explicit proof when foundational trust matters.

### `@[implemented_by]`

This can replace the compiled implementation of a definition. It does not itself prove the replacement implementation matches the logical definition. Audit carefully for executable-correctness claims.

### `@[csimp]`

This can affect compiled behavior. Audit carefully when the claim is about executable code, not only the logical theorem.

### `unsafe`

Unsafe code may be necessary at runtime boundaries, but it is not kernel-checked proof evidence. Isolate it behind a pure checked model when possible.

## Validation ladder

Use the lowest level appropriate to risk:

1. `lake env lean path/to/File.lean` or `lake build +Module.Name` succeeds.
2. Placeholder scan is clean.
3. `#print axioms` for theorem dependencies is reviewed.
4. `lake build` succeeds.
5. `lean4checker --fresh Module.Name` succeeds when available and appropriate.
6. For adversarial/untrusted proof artifacts, use sandboxed comparator/external checker workflows and inspect statement fidelity, notation, typeclasses, and imported axioms.

## Final audit format

```text
Placeholder status: none found.
Axiom/trust status: theorem `foo_eq_spec` has no project-local axioms. No `unsafe`, `partial`, `native_decide`, `decide +native`, `@[implemented_by]`, or `@[csimp]` appears in the changed files.
```

If there are assumptions:

```text
Axiom/trust status: `foo_sound` depends on classical choice through imported library theorem X. The executable wrapper uses IO and filesystem state outside the Lean proof boundary.
```
