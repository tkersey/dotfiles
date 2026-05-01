# Trust audit

Use this reference when the task involves production verification, high-assurance claims, foundational trust, or proof certificates.

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
- `implemented_by`
- `@[implemented_by]`
- `csimp`
- `@[csimp]`

These are not all forbidden, but they must be reported when relevant to the claim.

## Axiom footprint

For each top-level theorem supporting the final correctness claim, inspect:

```lean
#print axioms theorem_name
```

Report the result.

Useful classifications:

- no axioms
- only accepted imported axioms
- classical reasoning or choice
- project-local axioms
- native-code trust
- unsafe implementation trust
- external model-correspondence assumptions

## Interpreting common cases

### `axiom`

Project-local axioms are assumptions. They can make Lean accept false propositions if inconsistent. Avoid them for correctness claims unless the user explicitly wants an axiomatized model.

### `noncomputable`

Often fine in pure mathematics. Usually not appropriate for executable verified programs.

### `partial`

Usually unsuitable for logic-facing correctness proofs. Prefer total functions with explicit fuel, measures, or well-founded recursion.

### `native_decide`

Can be useful for large finite decisions, but it increases the trusted code base by relying on native compilation. Prefer kernel-checkable reduction, `decide`, `simp`, or explicit proof when foundational trust matters.

### `@[implemented_by]`

This can replace the compiled implementation of a definition. It does not itself prove that the replacement implementation matches the logical definition. Audit carefully for executable-correctness claims.

### `@[csimp]`

This can affect compiled behavior. Audit carefully when the claim is about executable code, not only the logical theorem.

### `unsafe`

Unsafe code may be necessary at runtime boundaries, but it should not be treated as kernel-checked proof evidence. Isolate it behind a pure checked model when possible.

## Final audit format

```text
Placeholder status: none found.
Axiom/trust status: theorem `foo_eq_spec` uses no project-local axioms. No `unsafe`, `partial`, `native_decide`, `@[implemented_by]`, or `@[csimp]` appears in the changed files.
```

If there are assumptions:

```text
Axiom/trust status: `foo_sound` depends on classical choice through imported library theorem X. The executable wrapper uses IO and is outside the proof boundary.
```
