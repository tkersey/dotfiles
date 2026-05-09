# universalist

Drop-in replacement skill for structural, universal-construction-driven codebase architecture.

It keeps the Universalist intent—choose the smallest honest construction—and includes Track D for universal architecture boundaries: free syntax, coherent observations, transported semantics, lifted implementations, Freyd/AFT-style free-builder diagnostics, explicit IR, and law tests.

## Install

From your repo root:

```bash
rm -rf codex/skills/universalist
unzip universalist-freyd-dropin-replacement.zip -d .
cd codex/skills/universalist
chmod +x scripts/*.sh
./scripts/check_universalist.sh
```

## Use

Ask for `$universalist` when code smells indicate a structural refactor rather than an ordinary fix.

Use `$kan` after `$universalist` selects a Track D boundary and the task becomes detailed Kan extension/lift, Freyd/AFT, Yoneda/Coyoneda, codensity, or defunctionalization mechanics.

## New Freyd/AFT practice

For lift-shaped refactors, `universalist` now asks whether the projection

```text
P : internal implementation world -> observable behavior world
```

is disciplined enough to support a canonical free builder

```text
Free : observable behavior world -> internal implementation world
```

It reports either a candidate builder/realizer or an obstruction such as lost evidence, missing internal constraint structure, or unbounded implementation templates.
