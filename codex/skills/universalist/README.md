# universalist

Single drop-in Universal Architecture skill for structural, universal-construction-driven codebase architecture. This version folds the former `kan` skill into `universalist` as an internal mechanics layer, so `$universalist` is the only top-level skill needed for this doctrine.

It keeps the Universalist intent: **one signal, one seam, one smallest honest construction**. It adds Track D for universal architecture boundaries: free syntax, coherent observations, transported semantics, lifted implementations, Freyd/AFT-style free-builder diagnostics, obstruction reports, behavioral coalgebras, effect signatures with handlers, explicit IR, and law tests.

## Install

From your repo root:

```bash
rm -rf codex/skills/universalist
unzip universalist-unified-architecture-dropin-v9.zip -d .
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

Use `$universalist` for the full workflow. Detailed Kan extension/lift, Freyd/AFT, Yoneda/Coyoneda, codensity, categorical-data, and defunctionalization mechanics now live inside `references/mechanics/` and `scripts/emit_mechanics_report.sh`.

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

This version treats context preparation as a first-class universal-architecture concern. Use Track F when any semantic consumer needs exactly the right data at exactly the right time: model, human reviewer, policy engine, compiler pass, workflow scheduler, deployment controller, BI dashboard, auditor, action selector, or agent runtime.

The core rule is: **Allow arbitrary sources. Forbid uncertified semantic consumption.**

A context is prepared by compiling candidate source data into a task-indexed, schema-shaped, constraint-closed, provenance-preserving, freshness-valid, observationally minimal context instance before rendering it to a prompt, dashboard, JSON payload, review packet, policy input, decision packet, or tool argument.

## Verified Context Plane

This version adds the neutral, universal framing from the CQL/context work:

```text
Operational stores own mutation.
Verified context planes own semantic publication.
```

CQL/categorical databases are treated as a reference technology for verified canonicalization, integration, constraints, and provenance around live operational stores—not as a default live memory substrate.

Useful commands:

```bash
./scripts/emit_verified_context_plane.sh semantic-consumer typescript
./scripts/emit_cql_fit_assessment.sh context-boundary agnostic
./scripts/emit_context_publication_boundary.sh published-context agnostic
```


## Possibility Sheafification

Track G treats the codebase as a usage site. Local uses are sections; shared fields, tests, traces, and observations are overlaps. A correct architecture-level abstraction behaves like a sheaf: compatible local meanings glue uniquely to one global meaning. Use this track to replace inexact abstractions with canonical artifacts and produce a Sheafification Certificate.

## Category Pivot / Syntax-Semantics

Track H adds Easy-World Transfer. Use it when a problem is hard because it is being solved in the ordinary executable-program world even though syntax, semantics, posets, relations, coalgebras, schema instances, resource models, or presheaf sites would make the structure explicit. The most important agentic case is syntax/semantics: plans, tool calls, policies, memory queries, patches, and workflows should be explicit syntax when they need inspection before execution; handlers/interpreters give semantics; laws certify soundness and adequacy.

Useful commands:

```bash
./scripts/emit_category_pivot.sh syntax typescript
./scripts/emit_category_pivot.sh abstract-domain agnostic
./scripts/emit_syntax_semantics_certificate.sh ToolOperation typescript
```


## Unified mechanics layer

The former standalone `kan` skill is now folded into this skill as an internal mechanics layer:

```text
references/mechanics/
templates/mechanics/
scripts/emit_mechanics_report.sh
```

Use the unified workflow:

```text
$universalist identifies the signal, seam, worlds, boundary, artifact, witness, law, falsifier, and certificate.
Mechanics references elaborate Kan/Yoneda/Coyoneda/Freyd/codensity/CQL/sheafification only when needed.
```

Useful mechanics commands:

```bash
./scripts/emit_mechanics_report.sh index
./scripts/emit_mechanics_report.sh kan-lift typescript
./scripts/emit_mechanics_report.sh codensity-presentation agnostic
./scripts/emit_mechanics_report.sh cql-context agnostic
./scripts/emit_mechanics_report.sh sheafification typescript
./scripts/emit_mechanics_report.sh category-pivot agnostic
./scripts/emit_mechanics_report.sh syntax-semantics typescript
```

You can safely remove `codex/skills/kan`; this package is self-contained.

## Invocation metadata

The `SKILL.md` description is intentionally kept below 1024 characters and front-loads trigger words because Codex initially sees the skill name, description, and file path before loading full instructions.
