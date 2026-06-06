# How to start using `$lean`

Use `$lean` when you want checked Lean artifacts, not just mathematical prose. The most effective prompts specify target, boundary, allowed edits, and check command.

## Minimal prompt template

```text
Use $lean.
Goal: ...
Target file/module: ...
Current failure or desired theorem: ...
Allowed changes: ...
Check command: ...
Proof boundary: ...
```

## Proof repair

```text
Use $lean to repair theorem `foo_eq_spec` in `MyProj/Foo.lean` without weakening the statement. Preserve the pinned toolchain and local proof style. Run `lake env lean MyProj/Foo.lean` and report the first real error if it still fails.
```

## Verified implementation

```text
Use $lean to write a pure specification for `normalize`, implement `normalizeFast`, and prove `normalizeFast_eq_spec`. Keep IO outside the proof boundary, avoid `sorry`/new axioms, and report `#print axioms` for the top theorem.
```

## External implementation model

```text
Use $lean to model this TypeScript validator as a pure Lean specification. Prove the stated case obligations and any general normalization/error-priority law that is tractable. Do not claim the TypeScript implementation is proved; state the adapter/test boundary explicitly.
```

## State-machine verification

```text
Use $lean to model the workflow state machine, define the invariant `Inv`, prove `initial_inv` and `step_preserves_inv`, then lift preservation over a list of inputs if the one-step proof succeeds.
```

## Trust audit

```text
Use $lean to audit `MyProj/Foo.lean` for placeholders, custom axioms, native evaluation, unsafe/partial/noncomputable code, implemented_by/csimp, and proof-boundary overclaims. Do not edit files; produce an evidence-based report with theorem names and `#print axioms` results where possible.
```

## Learning loop

Start with small, checked exercises:

1. Ask `$lean` to explain the project setup and prove one small local lemma.
2. Ask it to repair one failing theorem without changing the statement.
3. Ask it to add a spec/impl/proof trio for a pure helper.
4. Ask it to run a trust audit and explain what each trust item means.

A good first real task is proof repair for one file. A good second task is turning one pure function into a spec/implementation/refinement proof. Save external-code verification until you are comfortable reading the boundary report.
