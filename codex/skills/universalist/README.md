# universalist

Drop-in replacement skill for structural, universal-construction-driven codebase architecture.

It keeps the Universalist intent: **one signal, one seam, one smallest honest construction**. It adds Track D for universal architecture boundaries: free syntax, coherent observations, transported semantics, lifted implementations, Freyd/AFT-style free-builder diagnostics, obstruction reports, behavioral coalgebras, effect signatures with handlers, explicit IR, and law tests.

## Install

From your repo root:

```bash
rm -rf codex/skills/universalist
unzip universalist-universal-architecture-dropin.zip -d .
cd codex/skills/universalist
chmod +x scripts/*.sh scripts/*.py
./scripts/check_universalist.sh
```

## Use

Ask for `$universalist` when code smells indicate a structural refactor rather than an ordinary fix.

The skill decides whether the problem needs:

- product/coproduct/refined type/pullback/exponential/free construction;
- canonical boundary artifact;
- lifted implementation or obstruction report;
- behavioral coalgebra for stateful/protocol behavior;
- effect signature and handlers;
- observation/generation vocabulary;
- explicit first-order IR.

Use `$kan` only after `$universalist` has selected a Track D boundary and the task becomes detailed Kan extension/lift, Freyd/AFT, Yoneda/Coyoneda, codensity, or defunctionalization mechanics.

## Central rule

```text
Allow arbitrary domain primitives.
Do not allow arbitrary composition across architecture boundaries.
```

Ordinary code lives inside boundaries. Universal artifacts live at boundaries.
