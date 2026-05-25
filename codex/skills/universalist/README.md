# universalist

Drop-in replacement skill for structural, universal-construction-driven codebase architecture, now centered on Universal Composition Doctrine, Composition Certificates, and Boundary Normal Form.

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

## Worlds and boundaries practice

This version makes worlds and boundaries the first Track D step. Before selecting Kan, Freyd/AFT, Yoneda/Coyoneda, defunctionalization, effects, or coalgebras, the skill asks for worlds, objects, transformations, invariants, observations, primitives, composition rules, boundary kind, what is preserved/forgotten/generated/observed, and the law that would catch drift.

The rule is:

```text
Allow arbitrary primitives.
Do not allow arbitrary composition across architecture boundaries.
```

## Presentation strategy update

This version adds semantic compression and dense-dual presentation diagnostics. Track D now asks not only which canonical artifact belongs at a boundary, but how the artifact is presented: algebraically, codensity/dense-dual, mixed, or primitive. Track E Composition Certificates now include a Presentation section with probes, dual/observation bridge, reconstruction law, domain-specific assumptions, and falsifier.

Useful command:

```bash
./scripts/emit_presentation_diagnostic.sh compare typescript
```

## Exact Context Doctrine

This version treats context preparation as a first-class universal-architecture concern. Use Track F when a model, human, policy engine, planner, workflow, or tool selector needs exactly the right data at exactly the right time. The core rule is: **Allow arbitrary sources. Forbid uncertified semantic consumption.**

A context is prepared by compiling candidate source data into a task-indexed, schema-shaped, constraint-closed, provenance-preserving, freshness-valid, observationally minimal context instance before rendering it to a prompt, dashboard, JSON payload, decision packet, or tool argument.
