# universalist

Single drop-in Universal Architecture workflow for domain algebra, law discovery, structural refactoring, and universal-construction-driven software synthesis. This version folds the former `kan` skill into `universalist` as an internal mechanics layer, so `$universalist` is the only top-level skill needed for this doctrine.

It keeps the Universalist intent: **one signal, one seam, one smallest honest construction**. It now folds Algebra-Driven Design into Track A0 so local worlds are discovered through carriers, operations, observations, laws, non-laws, interpreters, and property tests before escalation. It adds Track D for universal architecture boundaries: free syntax, coherent observations, pullback witnesses, pushout integration, transported semantics, lifted implementations, Freyd/AFT-style free-builder diagnostics, obstruction reports, behavioral coalgebras, effect signatures with handlers, Freyd/premonoidal effect boundaries, operadic component grammars, explicit IR, and law tests.

## Install

From your repo root:

```bash
rm -rf codex/skills/universalist
unzip universalist-composition-geometry-dropin-v14.zip -d .
cd codex/skills/universalist
chmod +x scripts/*.sh scripts/*.py
./scripts/check_universalist.sh
```

## Use

`$universalist` is implicitly invoked whenever implementation, refactoring, review, migration, or resolution considers a code boundary. Boundary consideration itself is the activation signal, including ordinary feature work and PR/review resolution.

Activation is broad; escalation is proportional. The boundary pass may preserve an already exact seam and return to ordinary delivery. Stronger constructions are justified only when the pass finds drift, invalid states, hidden composition, lossy projection, uncertified context, or another structural liability.

The skill decides whether the boundary should remain ordinary or needs:

- product/coproduct/refined type/pullback/pushout/exponential/free construction;
- canonical boundary artifact;
- lifted implementation or obstruction report;
- behavioral coalgebra for stateful/protocol behavior;
- effect signature and handlers;
- observation/generation vocabulary;
- explicit first-order IR.

Use `$universalist` for the full boundary workflow. Detailed Kan extension/lift, Freyd/AFT, pullback/pushout, Yoneda/Coyoneda, codensity, categorical-data, graph-rewrite, and defunctionalization mechanics now live inside `references/mechanics/` and `scripts/emit_mechanics_report.sh`; load them only after the boundary pass justifies escalation.

## Ledger-addressed plans

Implementation tracks allocate a fresh progress artifact through the
`skills-zig` ledger CLI 0.5.3 or newer:

```bash
./scripts/init_universalist_plan.sh
```

Plans live at
`.ledger/universalist/plan-YYYYMMDDTHHMMSSnnnnnnnnnZ-NNNN.md`. The UTC
timestamp makes recency visible; the collision ordinal and atomic create
prevent one run from overwriting another. Retain the returned plan id during
the run. Use `ledger latest --source universalist` only as a recovery lookup,
then verify the plan's task metadata before resuming it. Existing flat
`.ledger/universalist-plan-*.md` files remain readable legacy addresses and
are not rewritten.

## Track A0 — Domain Algebra Discovery

Use Track A0 when the local world is not yet algebraically clear. The rule is:

```text
Algebra before architecture.
```

Useful commands:

```bash
./scripts/emit_add_pass.sh payment-lifecycle typescript
./scripts/emit_domain_algebra_card.sh shopping-cart typescript
./scripts/emit_law_table.sh EvidenceSet agnostic
./scripts/emit_property_test_plan.sh checkout-idempotency typescript
```

You can safely remove `codex/skills/algebra-driven-design`; this package contains the ADD kernel as an internal workflow.

## Central rule

```text
Allow arbitrary domain primitives.
Do not allow arbitrary composition across architecture boundaries.
```

Ordinary code lives inside boundaries. Universal artifacts live at boundaries.

## Worlds and boundaries practice

This version makes worlds and boundaries the first Track D step. Before selecting Kan, Freyd/AFT, pullback/pushout, Yoneda/Coyoneda, defunctionalization, effects, or coalgebras, the skill asks for worlds, objects, transformations, invariants, observations, primitives, composition rules, boundary kind, what is preserved/forgotten/generated/observed, and the law that would catch drift.

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

## Composition geometry: Freyd categories and operads

Track D now selects not only a canonical artifact but the weakest honest **composition geometry**:

```text
category                sequential transformations
monoidal category       independent/parallel context
Freyd/premonoidal       pure values plus ordered call-by-value effects
colored operad          typed many-input hierarchical assembly
PROP/properad            genuine multiple-input/multiple-output wiring
traced/coalgebraic       feedback and ongoing behavior
resource-sensitive      consumable, graded, or permissioned resources
```

The former `freyd` mechanics name was ambiguous. Use:

```bash
./scripts/emit_mechanics_report.sh freyd-aft agnostic
./scripts/emit_mechanics_report.sh freyd-category typescript
./scripts/emit_mechanics_report.sh operad typescript
```

A bare `freyd` mechanics request fails with a disambiguation message rather than silently selecting the wrong construction.

## Pullbacks, pushouts, and graph rewriting

The mechanics layer now treats these as general software constructions rather than only a context-reconciliation analogy:

```text
pullback        canonical witness that two values agree through a shared projection
pushout         canonical integration that glues two sources along explicit overlap
double pushout  graph/model rewrite with delete-preserve-add structure
```

Use pullbacks for typed joins, authorization contexts, wire/domain compatibility, synchronized views, and evidence attached to required claims. Use pushouts for schema/data integration, modular API or language extension, canonical models, and overlap-based reconciliation. Use double-pushout mechanics when a graph/model rewrite may fail because the preserved interface or pushout complement is invalid.

The distinctive proof obligation is not merely a commuting square. Require factorization through the canonical witness/integrated artifact and approximate uniqueness with opaque constructors, canonical IDs, normalization, and removal of competing public paths.

Useful commands:

```bash
./scripts/emit_mechanics_report.sh pullback typescript
./scripts/emit_mechanics_report.sh pushout agnostic
./scripts/emit_mechanics_report.sh pullback-pushout agnostic
./scripts/emit_mechanics_report.sh double-pushout agnostic
bash ./scripts/check_pullback_pushout_mechanics.sh
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
Mechanics references elaborate Kan/Yoneda/Coyoneda/Freyd/pullback/pushout/codensity/CQL/sheafification only when needed.
```

Useful mechanics commands:

```bash
./scripts/emit_mechanics_report.sh index
./scripts/emit_mechanics_report.sh kan-lift typescript
./scripts/emit_mechanics_report.sh pullback typescript
./scripts/emit_mechanics_report.sh pushout agnostic
./scripts/emit_mechanics_report.sh double-pushout agnostic
./scripts/emit_mechanics_report.sh codensity-presentation agnostic
./scripts/emit_mechanics_report.sh cql-context agnostic
./scripts/emit_mechanics_report.sh sheafification typescript
./scripts/emit_mechanics_report.sh category-pivot agnostic
./scripts/emit_mechanics_report.sh syntax-semantics typescript
```

You can safely remove `codex/skills/kan`; this package is self-contained.

## Effective universal substrate and custom-agent workflow

This version adds Track I and a bundled categorical-substrate team. The target thesis is:

```text
I can implement any computable software on an effective universal computational substrate
while using category theory to define its architecture of composition, interpretation,
effects, state, boundaries, observations, and laws.
```

The package installs custom agents under `codex/agents/`. Codex subagents are explicitly gated: say `Use $universalist in categorical-substrate team mode and spawn the bundled custom agents` when you want delegation. Normal implicit `$universalist` routing remains single-agent.

Recommended command:

```bash
./scripts/emit_universalist_team_prompt.sh design
```

The root agent synthesizes specialist packets into one Effective Universal Architecture Certificate, chooses one witness seam, uses one writer, then verifies independently.

## Invocation metadata

The `SKILL.md` description is intentionally kept below 1024 characters and front-loads the boundary trigger because Codex initially sees the skill name, description, and file path before loading full instructions.

Implicit routing applies whenever implementation, review, or resolution considers how values, effects, state, evidence, authority, or behavior cross a code boundary. Activation is deliberately broader than architectural escalation: preserving an already exact boundary is a valid result.
