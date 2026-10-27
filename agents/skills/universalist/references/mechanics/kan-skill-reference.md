# Former Kan Skill Reference

This file preserves the former standalone Kan skill instructions as an internal mechanics reference. The unified `universalist` skill owns routing, certificates, and architecture decisions; these mechanics are used only after the universalist workflow identifies the relevant boundary/artifact.

---

---
name: kan
description: >
  Use when universalist or the user has identified a concrete world/boundary seam that needs detailed Kan mechanics: Kan extensions, Kan lifts, precomposition/postcomposition, Freyd/AFT free-builder diagnostics, Yoneda/Coyoneda boundary representations, defunctionalized boundary IRs, codensity/density, codensity presentations via dense probes and duality, Exact Context Doctrine, context compilation, task-indexed data exchange, Context Certificates, pointwise formulas, free/cofree completions, functorial data migration, compatibility facades, lifted implementations, residual obligations, Composition Certificates, Boundary Normal Form audits, or categorical law tests; and use when universalist identifies a Possibility Sheafification / exact-abstraction replacement that needs categorical repair mechanics. Do not use for generic architecture unless worlds, boundary kind, known side, unknown location, witness slice, proof signal, and—when applicable—a Composition Certificate or Sheafification Certificate are named or must be recovered.
---

# Kan

## Mission

Use this skill for the detailed categorical mechanics behind universal architecture boundaries.

`universalist` chooses whether a seam deserves a canonical artifact. `kan` elaborates the selected artifact: Kan extension, Kan lift, Freyd/AFT diagnostic, Yoneda/Coyoneda representation, defunctionalized IR, codensity, data migration, context compilation, or law tests.

Core rule:

```text
Primitives compute. Boundaries compose. Presentations compress. Contexts prepare. Witnesses certify.
```

Do not start with category labels.
Start with worlds, boundary kind, known side, unknown location, witness, and law.
```

## Required Handoff Contract

Do not begin detailed Kan mechanics unless the prompt or prior analysis provides, or you first recover:

- signal / smell;
- seam;
- source and target worlds;
- boundary kind;
- known side;
- unknown location;
- candidate artifact;
- witness slice;
- proof signal;
- falsifier;
- Composition Certificate fields if the seam is already certified or being certified;
- Context Certificate fields if the seam is a semantic-consumption/context-compilation boundary.
- Verified Context Plane fields if schemas, mappings, constraints, provenance, publication, or CQL-like tooling are relevant.

If these are absent, first produce a short world/boundary inventory and ask whether to proceed, unless the user requested a best-effort implementation.


## Possibility Sheafification Elaboration

Use this mode when `universalist` has identified an inexact architecture-level abstraction and produced, or asked for, a Sheafification Certificate. `kan` should elaborate the categorical repair; it should not invent Track G from vague code smell alone.

Required handoff:

- current abstraction and files;
- usage site and local contexts;
- local sections and overlaps;
- sheaf failure: local inconsistency, missing global glue, non-unique gluing, or hidden excess possibility;
- possibility envelope gap;
- candidate canonical repair;
- witness slice and falsifier.

Categorical repair selector:

| Sheaf failure | Likely categorical mechanics |
|---|---|
| Local inconsistency | equalizer, pullback witness, refined type, coherent observation |
| Missing global glue | free construction, initial algebra, algebraic effects, Kan lift, free builder, Exact Context artifact |
| Non-unique gluing | coequalizer, quotient, normalization, observational equivalence, canonical IR |
| Hidden excess possibility | coproduct, refined type, dependent invariant, state machine, behavioral coalgebra |
| Callback-shaped locals | defunctionalization, operation IR, handler algebra |
| Observation sprawl | Yoneda/Ran observation vocabulary |
| Generated/provenance drift | Coyoneda/Lan payload + path |

Output a **Sheafification Kan Report** with the construction mechanics, representation choice, comparison/unit/counit/factorization law when applicable, gluing law, falsifier, and migration notes.

## Composition Certificate Elaboration

Use this skill in two modes:

1. **Recover mode**: no certificate exists yet, so produce a compact world/boundary inventory and identify the missing certificate fields.
2. **Elaboration mode**: a certificate exists, so refine its categorical mechanics without changing the selected boundary artifact unless the mechanics expose an obstruction.

For any Kan output, preserve this mapping:

| Certificate field | Kan elaboration |
| --- | --- |
| Worlds | candidate categories / indexed structures / posets / syntactic worlds |
| Boundary kind | `K`, `P`, interpreter, handler, serializer, view, migration, observer |
| Unknown location | extension axis, lift axis, representation axis, control-flow axis |
| Canonical artifact | `Lan`, `Ran`, `Delta`, `Lft`, `Rft`, Yoneda, Coyoneda, explicit IR, free builder, obstruction |
| Interpreter/projection/lowering | unit, counit, comparison cell, handler, `runObservation`, `lowerGenerated`, `apply` |
| Law witness | naturality, factorization, projection law, lowering law, handler law, defunctionalization equivalence |
| Falsifier | no colimit/limit/residual, lossy projection, incoherent observations, invalid path, missing constructor, no exact lift |

If the prompt asks for code, emit the certificate-aware implementation plan: artifact, interpreter/projection, law test, falsifier, and bypass policy.

## Exact Context / Context Compilation Mode

Use this mode when the selected boundary is a semantic-consumption boundary: a model, human, policy engine, workflow, scheduler, planner, ranker, classifier, compiler pass, deployment controller, BI dashboard, auditor, tool selector, or agent runtime is about to consume prepared information.

Recover:

- Task `q` and semantic consumer.
- Source worlds and source schema `S`.
- Candidate source instance `I_candidate`.
- Task-specific context schema `T_q`.
- Required observables `Obs_q`.
- Source-to-context mapping `M_q : S -> T_q` or source-to-target dependencies.
- Migration mode: restriction/projection, left pushforward/merge, right pushforward/join, or practical analogue.
- Chase/closure steps: deterministic constraint enforcement, equality propagation, entity resolution, unit/date normalization.
- Provenance graph: `Claim -> Evidence -> Source`, `DerivedFact -> Derivation -> Inputs`.
- Missingness, contradiction, ambiguity, and unsupported-claim representation.
- Observational core/minimization relative to `Obs_q`.
- Rendering law for prompt/report/dashboard/tool-argument/decision-packet output.
- Freshness law and invalidation triggers.

Use this formula:

```text
Context(q) = core_Obs(chase(migrate_{M_q}(I_candidate)))
DecisionPacket(q) = render(Context(q))
```

Do not treat retrieval as context. Retrieval is candidate source-instance generation.

## Verified Context Plane / CQL Context Mode

Use this mode when context compilation requires verified canonicalization, integration, constraints, provenance, schema evolution, or source reconciliation.

Recover:

- Operational source plane: live stores, logs, tools, documents, APIs, event streams.
- Candidate source instance: stable snapshot or extracted/retrieved data.
- Verified context plane: schemas, mappings, constraints, reconciliation, provenance.
- Publication boundary: published context snapshot and Context Certificate.
- Rendering boundary: prompt, JSON, report, policy input, dashboard, tool arguments.
- Semantic consumer: model, human, policy engine, compiler pass, workflow scheduler, deployment controller, auditor, action selector, or agent runtime.

CQL/categorical databases are reference technologies when the hard problem is typed integration, schema mappings, constraints, colimits/pushouts, and provenance. Do not recommend CQL as the default primary live memory or low-latency mutable store. Pair verified context tooling with operational stores when mutation, concurrency, authorization, or streaming dominate.

Use this placement rule:

```text
Operational stores own mutation.
Verified context planes own semantic publication.
```

## Codensity Presentation Mode

Use this mode when a target monad/effect/behavior is too semantic, infinitary, observational, probabilistic, topological, or completion-like for a useful algebraic presentation by generators/equations.

Recover:

- Target behavior / monad / effect.
- Direct algebraic presentation attempt and why it is awkward.
- Small probe world: finite cases, approximants, observations, traces, expectations, policy probes, legacy views, or finitely presentable fragments.
- Density / coverage claim: how large objects are built or determined by probes.
- Duality / observation bridge: dualizing object, observation world, adjunction/equivalence, or semantic bridge.
- Reconstruction: right Kan/codensity formula or architecture-level reconstruction operation.
- Generic categorical part vs domain-specific theorem/assumption.
- Laws: probe coherence, reconstruction, monad/composition coherence, and falsifier.

Use this slogan:

```text
Algebraic presentations build by constructors.
Codensity presentations reconstruct from dense probes and dual observations.
```

Do not treat codensity only as optimization. It is also a presentation technology.

## Context Compilation Report Mode

Use when the requested Kan mechanics concern exact context, semantic consumption, or categorical data exchange for a task.

Deliver:

1. task `q` and semantic consumer;
2. source worlds/schema `S` and candidate source instance `I_candidate`;
3. task context schema `T_q`;
4. required observables `Obs_q`;
5. mapping `M_q`;
6. migration/closure/chase plan;
7. provenance, missingness, contradiction, and freshness structure;
8. observational core/minimization;
9. rendering/serialization law;
10. Context Certificate;
11. falsifiers.

## Step -1 — World Model Preamble

Before naming `Lan`, `Ran`, `Lft`, `Rft`, Yoneda, Coyoneda, or Freyd/AFT, record the worlds.

For each world:

```text
World:
Objects:
Transformations:
Invariants:
Observations:
Primitives:
Composition rules:
Equality/coherence notion:
```

A world is too weak for Kan mechanics if it has only nouns, no transformations, no equality/coherence notion, no observations, unstable invariants, or no law test.

## Boundary Kind to Kan Mapping

| Boundary kind | Software shape | Kan/categorical reading | First law |
| --- | --- | --- | --- |
| Embedding | old/core included in new/target | `Lan`, `Ran`, `Delta` | `new(embed(old)) == old(old)` |
| Projection | internals observed as public behavior | Kan lift, `P_*`, Freyd diagnostic | `observe(P(internal)) == required` |
| Forgetful map | rich structure erased to raw view | adjunction / free builder | `forget(free(raw))` satisfies raw behavior |
| Interpreter | syntax/effect/program -> behavior | algebra, fold, handler | interpreter agrees on fixtures |
| Compiler/lowering | source syntax/IR -> target IR/code | transported semantics, Coyoneda path | lowering preserves semantics |
| Serializer/codec | internal model -> wire/storage | projection/restriction, possible lift obstruction | round-trip or invariant preservation |
| View/query | model -> report/client view | `Ran`, Yoneda observation | overlapping observations commute |
| Handler | effect syntax -> runtime behavior | free effects, handler, defunctionalized operations | handler satisfies operation observations |
| Observer | subject -> observation result | Yoneda / `Ran` / `Rft` | representation change preserves observation |
| Migration | old schema -> new schema | `Delta`, `Lan`/Sigma, `Ran`/Pi | old reports pass through migration |
| Context compiler | source worlds -> task context schema | data exchange, migration/chase/core, context compilation | context satisfies schema, observables, provenance, freshness |
| Semantic consumer | context -> decision/action/inference | Exact Context, Context Certificate, rendering law | rendered packet preserves required observables |

## Core Heartbeat

### Extension axis: unknown after a boundary

Use when known source semantics must be transported or completed across `K`.

```text
C --K--> D
|        |
F        ?
v        v
E
```

Recover:

- `C`: source/core/legacy/specified world.
- `D`: target/ambient/expanded world.
- `E`: semantic/artifact/instance world.
- `K : C -> D`: embedding, schema map, API-version map, AST embedding, representation functor.
- `F : C -> E`: existing semantics, interpreter, instance, behavior, test oracle.
- Direction:
  - `Lan_K F`: free/generative/push-forward extension.
  - `Ran_K F`: coherent/conservative extension by observations.
  - `K*` / `Delta_K`: restriction/precomposition.
- Unit/counit:
  - `η : F -> Lan_K F · K`.
  - `ε : Ran_K F · K -> F`.
- Witness `d ∈ D` and one law test.

### Lift axis: unknown before a fixed boundary

Use when public behavior is known and the implementation-side artifact must be solved behind `P`.

```text
A --?--> B
|        |
F        P
v        v
C0
```

Recover:

- `A`: cases/contracts/tests/workflows/requirements.
- `B`: implementation/internal/runtime/resource world.
- `C0`: observable/public/external behavior world.
- `P : B -> C0`: projection, public API, view, handler, serializer, trace observer, compiler backend.
- `F : A -> C0`: required observable behavior.
- Direction:
  - `Lft_P F`: realization behind `P`, comparison `F -> P · Lft_P F`.
  - `Rft_P F`: residual/sound obligation behind `P`, comparison `P · Rft_P F -> F`.
  - `P_*`: direct projection/checking when implementation is already known.
- Witness `a ∈ A` and one projection law.

Use local notation `Lft_P` and `Rft_P` because Kan lift notation varies.

## Representation Passes

### Yoneda: observations first

Use when the boundary is observation-heavy: views, reports, public API projections, policy checks, contract assertions, test oracles, capability consumers, continuations.

Artifact:

```text
data Observation = ...
runObservation : Observation -> Subject -> Result
```

Law:

```text
runObservation(obs, repack(subject)) == runObservation(obs, subject)
```

### Coyoneda: deferred generation first

Use when the boundary is generation-heavy: generated DTOs, plugin operations, migrations, AST extensions, workflow steps, candidate realizers.

Artifact:

```text
data Generated = { payload, path }
lowerGenerated : Generated -> Target
```

Law:

```text
lowerGenerated(payload,path) == directInterpret(path,payload)
```

### Defunctionalization: first-order boundary IR

Use when functions cross architecture boundaries: callbacks, continuations, observers, selectors, handlers, predicates, builders, maps, resumptions.

Artifact:

```text
data BoundaryCase = ...captured fields...
apply/interpret/project : BoundaryCase -> Meaning
```

Law:

```text
apply(encode(oldFunction), input) == oldFunction(input)
```

## Freyd/AFT Boundary Diagnostic

Run this only after a lift-shaped boundary appears.

Question:

```text
Is P : B -> C0 disciplined enough to support a canonical free builder Free : C0 -> B?
```

Check:

1. `P` is concrete, not metaphorical.
2. `B` can combine constraints: products, pullbacks, equalizers, policy meets, workflow composition, validations.
3. `P` preserves those constraints enough to test.
4. There is a bounded solution-set-like family of implementation templates.
5. Candidate `Free` has a projection law:

```text
P(Free(required(case))) satisfies required(case)
```

If not, produce an obstruction report: lost evidence, vague projection, missing internal structure, unbounded templates, impossible observation, or required external dependency.

## Response Modes

### Certificate mechanics

Use when the user already has or wants a Composition Certificate.

1. Restate certificate fields.
2. Map the artifact to Kan/Yoneda/Coyoneda/defunctionalization mechanics.
3. Name the interpreter/projection/lowering/cell.
4. Name the law and falsifier.
5. State whether the certificate is verified, obstructed, approximate, or still only planned.

### Compact

1. Direct answer.
2. Worlds and boundary kind.
3. Extension or lift axis.
4. Representation pass: Yoneda, Coyoneda, defunctionalization, or none.
5. One witness.
6. One law/falsifier.

### Sheafification Kan report

Use when universalist has selected Track G / Possibility Sheafification.

1. Current abstraction and usage site.
2. Local sections and overlaps.
3. Sheaf failure classification.
4. Categorical repair.
5. Replacement artifact.
6. Interpreter/projection/lowering.
7. Gluing law and falsifier.
8. Migration/witness slice.

### Design memo

1. Problem frame.
2. World/boundary inventory.
3. Boundary kind to Kan mapping.
4. Extension/lift data.
5. Representation pass.
6. Proposed artifact and module shape.
7. Law tests and falsifier.
8. Failure modes.
9. Source/claim status.

### Implementation plan

1. Data structures.
2. Constructors / IR.
3. Interpreters/projections/lowerers.
4. Unit/counit/comparison functions.
5. Law tests.
6. Migration/rollback.

## Guardrails

- No Kan mechanics without worlds, boundary kind, known side, unknown location, witness, and law.
- No theorem claims for ordinary code unless categories/functors/natural transformations/comparison cells are explicit.
- No Yoneda/Coyoneda unless it changes representation, centralizes observations, defers generation, preserves provenance, or improves tests.
- No defunctionalization unless the higher-order value crosses a meaningful boundary.
- No Freyd/AFT unless `P : B -> C0` is concrete and there is a builder or obstruction report.
- Prefer plain engineering language when it conveys the same plan.
- No sheafification mechanics without local sections, overlaps, gluing failure, possibility-envelope gap, law, and falsifier.

## References

- `references/possibility-sheafification-mechanics.md`
- `references/abstraction-replacement-elaboration.md`

- `references/world-boundary-preamble.md references/composition-certificate-elaboration.md`
- `references/boundary-kind-to-kan.md`
- `references/foundations.md`
- `references/kan-lifts.md`
- `references/yoneda-coyoneda.md`
- `references/defunctionalization.md`
- `references/freyd-aft.md`
- `references/architecture-transformation.md`
- `references/law-tests.md`
- `references/claim-map.md`
- `references/sources.md`
- `references/sources.yml`
