---
name: universalist
description: "Use when a code change needs a structural refactor, exact abstraction, certified context, or canonical boundary artifact instead of ordinary feature work: flag/state matrices, repeated validation, branchy policy logic, syntax mixed with execution, opaque callbacks/effects/tool calls, duplicated projections, generated artifacts losing provenance, unclear protocols/state machines, public contracts shaping internals, semantic consumers needing certified context, or abstractions that are too broad/narrow/redundant/inconsistent. Default to one signal, one seam, smallest honest construction; produce proof/falsifier and Composition, Context, Sheafification, Syntax/Semantics, or Category Pivot certificate. Includes internal mechanics for Kan/Yoneda/Coyoneda/Freyd/codensity/CQL/defunctionalization."
---

# Universalist

Use this skill when the highest leverage comes from changing the **shape of truth** in a codebase, not from adding another ordinary feature branch.

This is an **inner lens** for choosing the right structural move. It is not a generic implementation skill. Use it to decide and stage the structure, then let the repo's normal implementation flow carry the change.

This is now the single top-level skill for the Universal Architecture doctrine. The former `kan` skill has been folded into this skill as an internal mechanics layer under `references/mechanics/`, `templates/mechanics/`, and `scripts/emit_mechanics_report.sh`.

## Doctrine index

Universalist includes Track D, Track E, Track F, Track G, and Track H. It uses Universal architecture, Universal Composition Doctrine, Composition Certificate, Boundary Normal Form, Presentation Strategy Doctrine, Dense-Dual Presentation, Exact Context Doctrine, Context Certificate, Context Normal Form, Verified Context Plane, Possibility Sheafification, Sheafification Certificate, Abstraction Normal Form, Syntax/Semantics Pivot, Easy-World Transfer, Category Pivot Certificate, World and Boundary Inventory, Boundary Kind Taxonomy, Boundary Law Catalogue, Unknown-location artifact selector, Freyd/AFT, free builder, obstruction report, Behavioral coalgebra, Effect signature, and internal mechanics layer via `emit_mechanics_report.sh` for `P : B -> C`. Core guardrails include: Allow arbitrary domain primitives; Allow arbitrary sources; Forbid uncertified semantic consumption; Operational stores own mutation; Verified context planes own semantic publication; Presentations compress; Do not merely abstract. Sheafify possibility.
Do not force a hard problem to stay in the ordinary executable-program world when syntax, semantics, posets, relations, coalgebras, schemas, resources, or presheaves make the required operation explicit.

The enriched slogan is:

> Universal architecture is the practice of designing software around canonical boundary artifacts: **free syntax, coherent observations, transported semantics, lifted implementations, free builders behind projections, obstruction reports, behavioral coalgebras, effect signatures with handlers, explicit IRs, and law tests.**

Core discipline:

> Allow arbitrary domain primitives, but do not allow arbitrary composition across architecture boundaries.

> Do not merely abstract. Sheafify possibility.

Ordinary code may live inside a boundary: I/O, math, parsing, vendor APIs, database drivers, model calls, clocks, randomness, local algorithms, and low-level loops. Composition boundaries should be explicit artifacts: syntax, observations, projections, transports, lifts, handlers, state transitions, IRs, or law tests.


## Universal Composition Doctrine

Maxim:

```text
Allow arbitrary primitives. Forbid arbitrary composition.
```

A software system is universally architected when every meaningful composition boundary between worlds factors through a canonical boundary artifact, and every such artifact has an interpreter, projection, lowering, handler, or law-test witness.

Use this doctrine to separate two questions:

```text
Can the primitive compute?      Ordinary implementation question.
Can the boundary compose?      Universal architecture question.
```

A **Composition Certificate** is the unit of universal architecture. It records:

```text
worlds
boundary
unknown location
canonical artifact
interpreter / projection / lowering / handler
law witness
falsifier
bypass policy
```

A codebase is in **Boundary Normal Form** when all meaningful cross-world composition boundaries have Composition Certificates, and all bypasses are removed or explicitly justified as primitive effects.

Engineering law:

```text
No boundary without an artifact.
No artifact without an interpreter.
No interpreter without a law.
No law without a falsifier.
```

Use Track E when the user wants to move a codebase toward Boundary Normal Form, or when the main output should be a Composition Certificate rather than an immediate implementation.

## Presentation Strategy Doctrine

The codensity transcript adds one more architectural question: not only **what canonical artifact owns the boundary**, but **how that artifact is presented**. Complex artifacts need presentation strategies.

Use this extension of the engineering law stack:

```text
No boundary without an artifact.
No artifact without a presentation.
No presentation without an interpreter / projection / reconstruction.
No reconstruction without a law.
No law without a falsifier.
```

Presentation modes:

- **Algebraic presentation** — use generators, operations, equations, syntax, free objects, effect signatures, and handlers. Prefer when the artifact is operational, finitary, command-like, or naturally syntax-first.
- **Codensity / dense-dual presentation** — use a small dense world of probes plus a dual/observational bridge and reconstruction. Prefer when the artifact is semantic, infinitary, completion-like, probabilistic, topological, observational, or too large for a clean generators/equations presentation.
- **Mixed presentation** — use algebraic syntax for operations and dense probes for semantic competence, safety, policy, probability, traces, or compatibility. Agentic systems are a stress test, not the center of the doctrine.
- **Primitive presentation** — explicitly contain the boundary as a primitive effect when no useful artifact/presentation is available yet.

New doctrine sentence:

```text
Primitives compute. Boundaries compose. Presentations compress. Contexts prepare. Witnesses certify.
```

Dense-Dual Presentation principle:

> When a semantic artifact is too large, infinitary, observational, or completion-like to present by generators and equations, try to present it by a small dense world of probes plus a duality or observation bridge into the semantic world.

Reject canonical-but-useless presentations. Prefer small, testable, dense presentations that separate generic boundary machinery from domain-specific representation assumptions.

## Exact Context Doctrine

Maxim:

```text
Allow arbitrary sources. Forbid uncertified semantic consumption.
```

Exact Context Doctrine is the context-preparation layer of Universal Composition. It applies whenever a model, human, policy engine, planner, scheduler, workflow, tool selector, compiler pass, or other semantic consumer is about to decide, act, rank, classify, answer, approve, execute, or infer.

A semantic consumer should not receive raw retrieved material, raw tool output, stale memory, untyped chunks, or unconstrained summaries. It should receive a **task-indexed, schema-shaped, constraint-closed, provenance-preserving, freshness-valid, observationally minimal context instance**.

Use this pipeline:

```text
Task q
  -> task-specific context schema T_q
  -> task observables Obs_q
  -> candidate source instance I_candidate
  -> source-to-context mapping M_q
  -> migrated context instance
  -> chase / deterministic constraint closure
  -> provenance + missingness + contradiction structure
  -> observational core relative to Obs_q
  -> rendered decision packet
  -> semantic consumer
```

Compact formula:

```text
Context(q) = core_Obs(chase(migrate_{M_q}(I_candidate)))
DecisionPacket(q) = render(Context(q))
```

The prompt is not the context. A prompt, dashboard, JSON payload, tool argument, review packet, or decision brief is only a rendering of the semantic context.

Engineering law:

```text
No semantic consumption without certified context.
No context without a schema.
No schema without observables.
No observables without provenance and freshness.
```

Use Track F when the main issue is having just the right data at just the right time.

## Verified Context Plane Principle

Exact Context is universal, not agent-specific. The general boundary is:

```text
Prepared Context -> Semantic Consumer
```

A semantic consumer may be a model, human reviewer, policy engine, compiler pass, workflow scheduler, deployment controller, planner, ranker, classifier, BI dashboard, auditor, test harness, action selector, or agent runtime.

Use this plane split:

```text
Operational Source Plane
  mutable systems of record, logs, documents, APIs, event streams, tools, live stores

Candidate Plane
  retrieved / observed / sampled / extracted candidate source instances

Verified Context Plane
  schemas, mappings, constraints, provenance, normalization, reconciliation

Publication Plane
  stable task-indexed context snapshots and Context Certificates

Rendering Plane
  prompt, JSON packet, dashboard, report, tool args, policy input, review packet

Semantic Consumption Plane
  consumer decision, action, approval, execution, ranking, inference, or audit
```

Rule:

```text
Operational stores own mutation.
Verified context planes own semantic publication.
```

CQL and categorical databases are reference technologies for the verified context plane when schemas, mappings, constraints, integration, and provenance matter. Do not treat CQL as a default live-memory substrate. Pair it with operational stores when low-latency mutation, distributed writes, access control, or streaming are central.


## Possibility Sheafification Doctrine

Maxim:

```text
Do not merely abstract. Sheafify possibility.
```

A codebase already contains local evidence about what its abstractions mean: call sites, tests, controllers, serializers, database constraints, UI assumptions, policy checks, adapters, plugin hooks, event handlers, context schemas, and generated artifacts. Treat those local usages as a **site**. Treat each local meaning as a **section**. Treat shared identifiers, fields, traces, fixtures, and observations as **overlaps**.

An architecture-level abstraction is correct when compatible local meanings glue to one global meaning, and do so uniquely up to intended equivalence.

```text
compatible local meanings glue uniquely to global meaning
```

Possibility Sheafification is the abstraction manipulator that turns a messy presheaf of local meanings into a sheaf-like exact abstraction:

- local meanings agree on overlaps;
- every compatible family has a global representation;
- the global representation is unique up to intended quotient/canonicalization;
- impossible global states are excluded;
- missing valid global states become explicit obligations or extensions;
- redundant global states are quotiented or normalized.

Use Track G when the user wants the architecture to become inevitable: abstractions should admit exactly what is possible and no more. A codebase reaches **Abstraction Normal Form** when architecture-level abstractions behave like sheaves over their intended usage sites.

### Four sheaf failures

1. **Local inconsistency** — local meanings disagree on overlaps. Repair with split states, refined types, equalizers, pullbacks, observation coherence, or an obstruction report.
2. **Missing global glue** — local meanings are compatible but no global artifact represents them. Repair with free syntax, lifted implementation, effect signature, realizer, obligation ledger, context schema, or generated IR.
3. **Non-unique gluing** — multiple global representations produce the same local observations. Repair with quotient, normalization, canonical IR, coequalizer-like artifact, or single interpreter.
4. **Hidden excess possibility** — the global abstraction admits states no local behavior can justify. Repair with refined types, sum types, state machines, behavioral coalgebras, or exact context constraints.

New doctrine stack:

```text
Primitives compute.
Boundaries compose.
Presentations compress.
Contexts prepare.
Abstractions constrain possibility.
Easy worlds solve.
Witnesses certify.
```

## Easy-World Transfer / Category Pivot Doctrine

Maxim:

```text
Do not force a hard operation to stay in the ordinary executable-program world when another world makes it explicit.
```

Use Track H when a problem is hard because it is represented in the wrong category/world. In Universalist language, **Hask** means the ordinary executable-program world of computer science: functions, callbacks, services, branches, effects, IO, runtime behavior, and code-as-executed. That world is computationally expressive but often opaque to agents.

A category pivot asks:

```text
Current world: where are we trying to solve this?
Hard operation: inspect, compare, serialize, prove, minimize, merge, diff, totalize, authorize, explain, or replay?
Easy world: syntax, semantics, poset/lattice, relation, coalgebra, schema instance, resource model, presheaf/site, trace, or context schema?
Transfer: how do we encode into the easy world and interpret back?
Law: what observation is preserved?
Falsifier: when does the transfer fail?
```

The most important pivot for coding agents is **syntax/semantics**:

```text
Syntax gives handles: plans, operations, policies, memory queries, workflow steps, patches, certificates.
Semantics gives meaning: effects, traces, public behavior, policy outcomes, memory consequences.
Interpreters connect them: handle, run, compile, lower, render, project.
Laws certify them: accepted syntax denotes valid semantics; required semantic distinctions remain observable.
```

Use syntax when behavior needs inspection, replay, policy checks, serialization, diffing, total handling, simulation, provenance, or multiple interpreters. Use semantics when deciding what observations define correctness. Do not let agentic systems execute opaque intent; interpret certified syntax into observed semantics.

## Do not trigger for

- Routine feature work with no structural smell.
- Pure performance tuning, infra, UI polish, or docs work.
- Broad rewrites with no stable seam.
- Cases where the domain rules are still too unstable to freeze into a stronger model.
- Category-theory exposition that does not change a concrete seam, construction, boundary, or proof signal.

## Step -1 — World and Boundary Inventory

Before choosing Track A/B/C/D/E/F/G/H for any non-trivial structural request, inventory the worlds and boundaries. This prevents fake category labels and keeps the response anchored in repo reality.

A **world** is a structured domain where some objects, transformations, invariants, observations, primitives, and composition rules make sense.

A **boundary** is a map between worlds: embedding, projection, forgetful API, interpreter, compiler, serializer, view/query, handler, observer, migration, or adapter.

For each candidate world, record:

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

For each candidate boundary, record:

```text
Boundary:
Kind:
Source world:
Target world:
Preserved:
Forgotten:
Generated:
Observed:
Unknown location:
Candidate artifact:
Law test:
Falsifier:
```

If this inventory cannot be filled for the seam, do not escalate to Track D, Track F, Track G, or Track H.

## Boundary Kind Taxonomy

Classify boundary maps before choosing canonical artifacts.

| Boundary kind | Software shape | Usually suggests |
| --- | --- | --- |
| Embedding | old/core included in new/target | transported semantics, `Lan`, `Delta`, compatibility witness |
| Projection | internals observed as public behavior | lifted implementation, residual obligations, Freyd/AFT diagnostic |
| Forgetful map | rich structure erased to raw view | free builder / left adjoint question |
| Interpreter | syntax/program/effect -> behavior | free syntax, algebra/handler/fold |
| Compiler/lowering | source syntax/IR -> target IR/code | transported semantics, Coyoneda path, lowering law |
| Serializer/codec | internal model -> wire/storage | adapter, projection law, round-trip/invariant preservation |
| View/query | model -> read/report/client view | coherent observations, Yoneda observation vocabulary |
| Handler | effect syntax -> runtime behavior | effect signature, handler laws, defunctionalized operations |
| Observer | subject -> observation result | Yoneda vocabulary, law-test oracle |
| Migration | old schema/world -> new schema/world | `Delta`, `Lan`/Sigma, `Ran`/Pi, provenance path |
| Category pivot | hard operation in current world -> easier structured world | Syntax/Semantics Pivot, abstract domain, relation, coalgebra, schema, resource, presheaf |
| Context compiler | source worlds -> task context schema | Exact Context, data exchange, chase/closure, observational core |
| Semantic consumer | prepared context -> decision/action/inference | Context Certificate, rendering law, freshness law |

Do not skip this taxonomy. It decides whether the seam is an extension, a lift, a free-builder question, a coalgebra, an effect handler, or just an adapter.

## World Quality Diagnostic

A module or domain deserves to be treated as a world only if it has enough structure to support boundary laws.

A proposed world is too weak if:

- it has only nouns and no transformations;
- it cannot say what counts as equality, compatibility, or coherence;
- its invariants are unknown or still unstable;
- its primitives and composition rules are mixed together;
- it has no sanctioned observations;
- no law test can observe the boundary;
- calling it a world would not change code shape, tests, or failure modes.

When a world is too weak, use ordinary refactoring language and strengthen the model before applying universal architecture.

## Boundary Drift Smells

Boundary drift means two worlds communicate through uncoordinated paths or hidden assumptions.

Common drift signals:

- semantic drift: old/source semantics reimplemented differently in each target;
- observation drift: duplicated selectors, reports, queries, or public projections disagree;
- implementation drift: internals are invented without projecting to public behavior;
- generation drift: generated artifacts lose source/provenance/path information;
- control-flow drift: callbacks, closures, handlers, or continuations carry architecture semantics invisibly;
- behavioral drift: protocols, state machines, or distributed traces are tested by snapshots but not boundary laws;
- effect drift: operations are interpreted differently by test, production, audit, retry, or simulation handlers;
- context drift: raw retrieved chunks, stale memories, tool outputs, or summaries flow directly into a model/human/tool without schema, provenance, freshness, observables, or minimization;
- category drift: a hard operation is being forced to remain in executable code when syntax, semantics, a poset, relation, coalgebra, schema, resource model, or presheaf would make the structure inspectable.

Map drift to artifacts:

```text
semantic drift        -> transported semantics / Lan-style artifact
observation drift     -> coherent observations / Ran / Yoneda vocabulary
implementation drift  -> lifted implementation / Freyd diagnostic
creation drift        -> free builder behind projection or obstruction report
generation drift      -> Coyoneda-style generation path vocabulary
control-flow drift    -> defunctionalized explicit IR
behavioral drift      -> behavioral coalgebra / protocol observation law
effect drift          -> effect signature + handler laws
context drift         -> task-indexed context instance + Context Certificate
category drift        -> Category Pivot / Easy-World Transfer Certificate
```

## Boundary Law Catalogue

Use these named law shapes when designing proof signals:

| Boundary | Law shape |
| --- | --- |
| Embedding law | `new(embed(old)) == old(old)` |
| Projection law | `observe(project(internal)) == expectedPublicBehavior` |
| Forgetful law | `forget(combineRich(a,b)) == combineRaw(forget(a), forget(b))` |
| Interpreter law | `interpret(translate(syntax)) == oldBehavior(syntax)` |
| Serializer law | `decode(encode(internal))` preserves public invariants |
| Migration law | `oldReport(old) == oldReport(restrict(migrate(old)))` |
| Handler law | `run(handler(program))` satisfies operation observations |
| Coalgebra law | `observe(step(state,input))` satisfies protocol trace expectations |
| Generation law | `lowerGenerated(payload,path) == directInterpret(path,payload)` |
| Observation law | `runObservation(obs,repack(subject)) == runObservation(obs,subject)` |
| Defunctionalization law | `apply(encodedCase,x) == oldFunction(x)` |
| Context schema law | `Context(q)` satisfies task schema `T_q` |
| Observable preservation law | every required observable is answered, missing, contradicted, or unsupported explicitly |
| Provenance law | every evidence-bearing claim has a path to source or assumption marker |
| Freshness law | sources satisfy task freshness requirements at semantic consumption time |
| Rendering law | `render(Context(q))` preserves required observables under loss/token limits |

Every Track D artifact should have one positive law test and one falsifier/negative witness.

## Quick start: pick a track

### Track A — Diagnosis only

Use when the user wants analysis, design review, refactor advice, or a structural reading of the current code.

Deliver:

- observed signal;
- chosen construction;
- why nearby alternatives are worse;
- first seam to attack;
- proof signal;
- compatibility notes;
- whether this is ordinary universalist structure or universal-architecture territory.

### Track B — One-seam refactor

Use when the user wants code changes, but the right move is narrow and reviewable.

Deliver:

- one seam only;
- smallest honest construction;
- canonical boundary artifact if needed;
- adapter-first staging when a public boundary exists;
- fastest credible proof signal;
- explicit stop point after the first verified seam.

### Track C — Staged migration

Use when the internal model should improve while API, JSON, DB row, or message shapes stay stable for now.

Deliver:

- boundary decoder or adapter;
- internal stronger model;
- parity or differential tests;
- migration notes;
- clear cut line between legacy shape and internal shape;
- `.universalist-plan.md` update.

### Track D — Universal architecture boundary

Use when the smell is no longer just “choose a better type” but “choose the canonical artifact at a boundary.”

Deliver:

- worlds involved;
- boundary map, projection, embedding, interpreter, forgetful API, or observation map;
- known side and unknown artifact;
- canonical boundary artifact;
- presentation strategy: algebraic / codensity / mixed / primitive;
- dense probe family and dual/observation bridge when applicable;
- domain-specific theorem or assumption when reconstruction depends on it;
- one executable law test;
- one falsifier showing when the framing is overkill.

Use Track D for:

- duplicated projections or query/view sprawl;
- generated artifacts losing provenance;
- public contract determining internal implementation obligations;
- plugin, workflow, effect, rule-engine, or DSL boundaries;
- protocols, state machines, streams, actors, schedulers, or distributed processes whose behavior is best specified by observations over time;
- effect or workflow operations that need test, production, audit, explanation, simulation, and retry handlers;
- callback/closure/handler behavior that should become explicit IR;
- old semantics transported to a new target surface;
- compatibility facades where several old observations must agree;
- lifted-implementation refactors where `P : internals -> observable behavior` is vague, lossy, or intended to support a canonical implementation builder.

## Universal Architecture Kernel

Use this kernel for Track D decisions:

1. **Worlds** — source, target, implementation, observable behavior, syntax, runtime, API, DB, UI, policy, tests.
2. **Boundaries** — embedding `K`, projection `P`, interpreter, serializer, handler, report/view, compiler, observer.
3. **Free syntax** — AST/IR/effect/workflow syntax before interpretation.
4. **Coherent observations** — sanctioned observations/views that must agree.
5. **Transported semantics** — old/source semantics carried to a new target surface.
6. **Lifted implementations** — public behavior determines internal realizer/implementation.
7. **Free builders behind projections** — a disciplined `P : B -> C` supports canonical construction back into `B`.
8. **Obstruction reports** — a free/lifted implementation cannot exist because lost evidence, missing internal structure, or unbounded templates are named.
9. **Behavioral coalgebras** — state/process behavior specified by transitions and observations over time.
10. **Effect signatures and handlers** — operation syntax separated from runtime interpretation.
11. **Explicit IR** — callbacks, handlers, continuations, predicates, mappers, and rules become data plus interpreter.
12. **Exact context** — task-indexed context instances prepared before semantic consumption.
13. **Context certificates** — schema, observables, provenance, freshness, missingness, contradiction, rendering, and falsifier for a context.
14. **Law tests** — executable witnesses that the boundary artifact does what it claims.

## Unknown-location artifact selector

Choose by where the unknown lives:

| Unknown lives... | Default artifact | First proof signal |
| --- | --- | --- |
| In independent fields | Product | projections round-trip |
| In exclusive cases | Coproduct | exhaustive handling, invalid cases rejected |
| In a stable predicate | Refined type / equalizer | constructor accepts valid and rejects invalid |
| In shared projection agreement | Pullback witness | mismatches rejected, projections preserved |
| In configurable supplied behavior | Exponential / strategy | fixture parity with old branch |
| In structured syntax from generators | Free construction / initial algebra | interpreter agrees with old evaluator |
| In ongoing behavior over time | Behavioral coalgebra | traces/unfolds satisfy observations |
| In effectful operations with handlers | Effect signature / free effect syntax | test and production handlers agree on declared observations |
| After a source-to-target boundary `K` | Transported semantics / Lan-style | identity or embedding path preserves behavior |
| In coherent behavior under observations | Coherent observations / Ran/Yoneda-style | overlapping observations commute |
| Behind a projection `P` | Lifted implementation / Kan-lift-style | `project(realize(case)) == required(case)` |
| Behind `P`, but canonical construction is possible | Free builder behind projection | `project(free(required(case)))` satisfies required behavior |
| Behind `P`, but construction is impossible | Obstruction report | named loss of evidence/template/constraint |
| In internal checks implied by public behavior | Residual obligations | missing obligation fails projection |
| In generated payloads and deferred maps | Generation path vocabulary / Coyoneda-style | lowering equals direct interpretation |
| In duplicated selectors/projections | Observation vocabulary / Yoneda-style | representation change preserves observations |
| In callbacks/functions crossing boundaries | Explicit first-order IR / defunctionalization | `apply(encodedCase, x) == oldCallback(x)` |
| In data needed before semantic consumption | Task-indexed context instance / Context Certificate | schema constraints, observables, provenance, freshness, and rendering laws hold |
| In heterogeneous mutable sources needing semantic publication | Verified Context Snapshot / Publication Boundary | source snapshot, mapping, constraints, provenance, and publication law hold |
| In overlapping contexts from several systems | Pushout Reconciliation / explicit overlap | overlap identities are explicit, conflicts preserved, provenance survives |

### Track E — Composition certification

Use when the user wants to certify a boundary, audit uncertified composition, or move a codebase toward Boundary Normal Form one seam at a time.

Deliver:

- world inventory;
- boundary inventory;
- uncertified composition points;
- one Composition Certificate;
- canonical artifact and interpreter/projection/lowering;
- positive law witness;
- falsifier / negative witness;
- bypass removal plan;
- whether the seam is verified, obstructed, or still a primitive exception.

Use Track E for:

- architecture review where the question is “what boundary owns this composition?”;
- agent-written code that introduced new glue paths;
- APIs, handlers, migrations, plugins, tools, or policies that need certification;
- bringing an existing codebase incrementally into Boundary Normal Form;
- deciding whether a seam is genuinely universal-architecture territory or a justified primitive.

### Track F — Exact Context / semantic consumption boundary

Use when the main problem is whether a semantic consumer has exactly the right prepared data at exactly the right time. Semantic consumers include models, humans, policy engines, compilers, workflow schedulers, deployment controllers, planners, rankers, BI dashboards, auditors, test harnesses, approval gates, and agent runtimes.

Deliver:

- task `q` and consumer type;
- operational source plane and candidate source instance;
- verified context plane / context compilation mode;
- publication boundary and published snapshot shape;
- task-specific context schema `T_q`;
- required observables `Obs_q`;
- candidate source worlds and source instance `I_candidate`;
- source-to-context mapping `M_q`;
- deterministic closure/chase steps;
- provenance graph requirements;
- missingness, contradiction, ambiguity, and unsupported-claim representation;
- freshness requirements and invalidation triggers;
- observational-core/minimization plan;
- rendering/serialization plan;
- Context Certificate;
- CQL/categorical-database fit assessment when schemas, mappings, constraints, integration, or provenance dominate;
- Context Provenance Manifest when evidence lineage matters;
- law witnesses and falsifiers.

Use Track F for:

- RAG prompt stuffing or raw tool-output dumping;
- stale or temporally invalid context;
- missing evidence or unsupported claims;
- contradictions that are smoothed over;
- over-summarization that erases required distinctions;
- entity-resolution ambiguity;
- human review packets, policy-evaluation inputs, deployment decisions, debugging packets, planning packets, model prompts, compiler-pass inputs, scheduler contexts, audit packets, dashboards, or agent-runtime contexts that need exact context.

Do not frame this as only an inference problem. The general boundary is:

```text
Prepared Context -> Semantic Consumer
```

Inference is one semantic-consumption mode.

## Freyd/AFT boundary diagnostic for Track D

Use this sub-practice only after a lift-shaped boundary appears:

```text
A --?--> B
|        |
F        P
v        v
C        C
```

Software reading:

- `A`: public cases, contract tests, workflows, requirements, or obligations.
- `B`: internal implementation world.
- `C`: observable behavior world.
- `P : B -> C`: projection, serializer, public API runner, trace observer, report extractor, or forgetful/observational API.
- `F : A -> C`: required public behavior.
- `? : A -> B`: implementation realizer, implementation template, or residual obligation artifact.

The lift asks:

```text
Can we find L : A -> B such that P(L(a)) satisfies F(a)?
```

The Freyd/AFT diagnostic asks:

```text
Is P disciplined enough that required behavior in C has a canonical free builder Free : C -> B?
```

Use it to decide whether the seam needs:

- a concrete projection `P`, not vague “observable behavior”;
- internal constraint-combining structure in `B`;
- preservation of those constraints by `P`;
- a bounded solution-set-like family of implementation templates;
- a `Free` builder, realizer, or obligation artifact;
- an obstruction report when no exact/free lift exists.

Do **not** teach Freyd’s theorem in full inside ordinary responses. Translate it to this operational question:

> Does this observation boundary support a canonical implementation builder, or is it too lossy/ad hoc?


### Track G — Possibility Sheafification / inevitable architecture

Use when the codebase already has an abstraction, but the abstraction appears semantically inexact: too broad, too narrow, redundant, inconsistent, misplaced, callback-shaped, stringly typed, optional-field-heavy, or arbitrary.

Deliver:

- current abstraction and files;
- usage site: local contexts that cover the abstraction;
- local sections: what the abstraction means in each context;
- overlaps: shared fields, IDs, tests, observations, traces, or invariants;
- compatibility checks on overlaps;
- gluing analysis: existence, uniqueness, failures, and obstructions;
- possibility envelope: valid states, impossible states currently admitted, valid states currently omitted, redundant meanings;
- canonical repair: refined type, coproduct, pullback, quotient, free syntax, coherent observations, Kan lift, effect signature, behavioral coalgebra, Exact Context artifact, defunctionalized IR, or obstruction report;
- Sheafification Certificate;
- one law test and one falsifier;
- one witness-slice migration plan.

Use Track G for:

- `string`, `any`, `dict`, nullable/optional-field soup carrying domain state;
- interfaces/classes that mean different things at different call sites;
- callbacks that hide operation syntax;
- duplicated status/state representations;
- API DTOs whose observed meanings differ from domain meanings;
- tests that imply a global abstraction missing from code;
- context objects that are raw retrieved material rather than certified context;
- generated artifacts with multiple encodings of the same meaning;
- state/protocol objects that admit impossible traces.

Do not use Track G for local helper abstractions whose possible states are intentionally broad and do not cross architecture boundaries.

Track G question:

```text
Does this abstraction satisfy the sheaf condition over its real usage site?
```

Track G law shape:

```text
compatible local observations glue to a canonical global representation
```

Track G falsifiers:

```text
local disagreement, missing global representation, non-unique representation, or impossible global state.
```

### Track H — Category Pivot / Syntax-Semantics transfer

Use when the problem is hard because the current representation hides the relevant structure. The dominant case is ordinary executable behavior that should be reified as syntax and certified by semantics.

Deliver:

- current world/category and why the operation is hard there;
- candidate easy world/category and what becomes easy;
- transfer/encoding from current world into easy world;
- interpretation/transport back to executable behavior or required observations;
- Syntax/Semantics Certificate when the pivot is from opaque execution/prose/prompt/callbacks into explicit syntax plus interpreter;
- Category Pivot Certificate for other pivots;
- preservation law and falsifier;
- one witness extraction/refactor plan.

Use Track H for:

- agent/tool behavior represented as opaque `name + args`, callbacks, closures, or prose;
- plans, policies, workflows, memory operations, context requests, or patches that need inspection before execution;
- executable functions that need serialization, replay, diffing, validation, authorization, totality checks, simulation, or multiple interpreters;
- hard equality, minimization, merge, provenance, freshness, reachability, resource, or policy analysis that becomes easier in a poset, relation, schema, coalgebra, resource category, or presheaf/site;
- syntax present without certified semantics, or semantics claimed without observations.

Track H question:

```text
What world makes the hard operation easy, and what law transports the result back?
```

Syntax/semantics law shape:

```text
accepted syntax denotes valid observed semantics, and required semantic distinctions remain representable or observable.
```

Track H falsifiers:

```text
syntax accepted but semantics invalid; semantic behavior needed but not representable; easy-world result loses required observation when transported back.
```

## Non-negotiables

- One signal, one seam, one smallest honest construction.
- Prefer products, coproducts, refined types, pullbacks, exponentials, and free constructions before advanced machinery.
- Escalate to universal architecture only when the boundary artifact changes code shape or tests.
- Allow arbitrary domain primitives; require explicit universal artifacts at architecture boundaries.
- Allow arbitrary sources; forbid uncertified semantic consumption.
- Do not feed raw retrieved chunks, memories, or tool outputs directly to semantic consumers when the decision/action/inference depends on evidence quality.
- Keep wire and storage shapes stable behind adapters unless the user explicitly wants a breaking change.
- Use the repo's current language, framework, and test stack before proposing new libraries.
- Say what remains runtime-only in dynamic or weakly typed environments.
- Stop after the first verified seam unless the user asked for a sweep.
- For lift-shaped Track D work, make `P : B -> C` concrete before proposing implementation changes.
- If proposing a free builder behind `P`, include a Freyd/AFT-style obstruction check: constraint structure, preservation, and bounded templates.
- If proposing effects/handlers, include operation syntax, at least one handler, and a handler observation law.
- If proposing coalgebra/protocol structure, include transition, observation, trace law, and invalid-transition witness.

## Step 0 — Create or update `.universalist-plan.md`

This file is the progress record for the current run.

Create it in the project root for Track B, Track C, or Track D. Use `scripts/init_universalist_plan.sh` if helpful.

Minimum fields:

```md
# Universalist Plan

## Track:
## Signal:
## Construction:
## Canonical boundary artifact:
## Worlds / boundaries inventory:
## Boundary kind:
## Boundary law:
## Freyd/AFT boundary diagnostic:
## Composition Certificate:
## Boundary Normal Form status:
## Category pivot / Syntax-Semantics certificate:
## Why this construction:
## Seam / files:
## Public boundaries touched:
## Wire/storage compatibility plan:
## Verification command(s):
## Runtime-only leftovers:
## Status: planned / editing / verified / staged
## Next seam:
```

If context compacts, read this file first and resume from its status line.

## Operator loop

1. **Inspect repo reality**
   - language and type features;
   - framework conventions;
   - serializer, ORM, and API boundaries;
   - current test runner and proof tools.

2. **Find candidate signals**

   Start from code smells and pressure, not category labels:

   - flag, enum string, boolean, or nullable field matrices;
   - same predicate enforced in several places;
   - repeated shared-id or shared-version agreement checks;
   - branchy policy logic that really wants supplied behavior;
   - syntax mixed with execution, logging, or explanation;
   - duplicated projections or selectors;
   - generated artifacts with no provenance;
   - public contract/tests implying missing internal obligations;
   - callbacks/handlers crossing boundaries without explicit IR;
   - public behavior fixed while internals are underdetermined;
   - a projection/serializer/view loses evidence needed by required behavior;
   - protocols/state machines whose observations are duplicated or informal;
   - effect/workflow operations with multiple implicit handlers;
   - opaque executable behavior that should be syntax before semantics;
   - plans, policies, tool calls, context requests, patches, or memory operations whose semantics are implied but not certified;
   - hard analysis forced into runtime code when an abstract domain, relation, trace, schema, resource model, or presheaf would make it explicit.

3. **Pick one seam**

   Choose the smallest stable seam where the stronger shape can land with low blast radius.

   Good first seams:

   - DTO -> domain conversion;
   - controller or handler boundary;
   - constructor or factory;
   - one central service or evaluator;
   - one join helper or aggregate constructor;
   - one projection/query/read-model boundary;
   - one plugin or rule-family adapter;
   - one public contract case;
   - one observation/projection function `P` for a lift-shaped refactor;
   - one state transition plus observer;
   - one effect operation plus handler.

4. **Choose the smallest honest construction**

   Default ladder:

   - independent fields -> product;
   - exclusive states -> coproduct;
   - repeated stable predicate -> refined type / equalizer;
   - shared projection agreement -> pullback witness;
   - configurable behavior -> exponential;
   - syntax separate from execution -> free construction / initial algebra.

5. **Escalate to canonical boundary artifacts only when needed**

   Use the unknown-location selector and the canonical boundary artifact matrix. Escalate only when it produces:

   - an explicit artifact;
   - an interpreter/projection/handler/lowering function;
   - a proof signal;
   - a concrete reduction in drift, duplication, hidden behavior, or lossy projection.

5a. **Run a category pivot check when the current world hides the structure**

   Ask whether the hard part would be easier in another world:

   - executable function -> syntax/IR plus interpreter;
   - runtime state -> coalgebra/trace semantics;
   - scattered predicates -> policy/order lattice;
   - raw context/prompt -> schema-shaped context instance;
   - local call sites -> presheaf/site with gluing;
   - resource behavior -> capability/resource category;
   - nondeterministic/partial spec -> relation/profunctor world.

   If yes, create a Category Pivot or Syntax/Semantics Certificate before broad mutation.

6. **Plan the boundary**

   Decide whether the seam can change in place or needs:

   - decoder;
   - adapter;
   - DTO / row mapping;
   - persistence converter;
   - legacy-to-new translation layer;
   - observation vocabulary;
   - generation path;
   - explicit IR plus interpreter;
   - projection from implementation to public behavior;
   - state transition plus observer;
   - effect operation plus handler;
   - Freyd/AFT-style free-builder diagnostic for that projection.

6a. **Create the Composition Certificate**

   For Track D or Track E, write the certificate before broad edits:

   - worlds and boundary kind;
   - unknown location;
   - canonical artifact;
   - interpreter/projection/lowering/handler;
   - positive law witness;
   - falsifier;
   - bypass policy;
   - status: planned / implemented / verified / obstructed / primitive exception.

   The certificate is the reviewable unit. Do not let a categorical name substitute for the certificate.

7. **Run the Freyd/AFT diagnostic when appropriate**

   For a lift-shaped Track D refactor, answer:

   - What exactly is `P : B -> C` in code?
   - What does `P` forget, observe, serialize, erase, or project?
   - Can `B` express combined constraints, equalities, products, pullbacks, validations, or workflow composition?
   - Does `P` preserve those constraints when observed in `C`?
   - Is there a bounded family of implementation templates for each public behavior?
   - What `Free : C -> B`, realizer, or obligation artifact is suggested?
   - Is the unit/projection exact, covering, sound, or approximate?
   - What obstruction prevents a free/lifted implementation?

8. **Encode idiomatically**

   Use the strongest encoding the repo can actually support:

   - native ADT;
   - sealed hierarchy / enum with payload;
   - interface + tag;
   - checked constructor or wrapper;
   - witness type;
   - closure or strategy;
   - AST + interpreters;
   - observation enum + `runObservation`;
   - generated payload + path + `lowerGenerated`;
   - realizer/obligation + `project`/`satisfy`;
   - free-builder function + projection test;
   - state transition + `observe`;
   - operation signature + handlers.

9. **Verify with the fastest credible proof signal**

   Prefer:

   - compile or typecheck;
   - targeted unit tests;
   - exhaustive handling checks;
   - constructor-only entry;
   - decode / encode round-trip;
   - mismatch rejection;
   - parity or differential tests during migration;
   - observation coherence;
   - projection/lift realization test;
   - free-builder projection test;
   - obstruction report fixture;
   - defunctionalized interpreter equivalence;
   - trace law for coalgebra/protocol behavior;
   - handler parity/observation test for effects.

10. **Stop or name the next seam**

   Do not turn one structural insight into a repo-wide rewrite. Verify one seam, record it, and stop unless the user asked for a broader sweep.

11. **Update `.universalist-plan.md`**

   Record:

   - what changed;
   - which boundary stayed stable;
   - which proof passed;
   - what still remains runtime-only;
   - whether a Freyd/AFT diagnostic found a builder or an obstruction;
   - next seam, if any.

## Practical decision guide

| Repo smell | Default construction | Nearby alternative to reject first | First seam | Proof signal |
| --- | --- | --- | --- | --- |
| `status`, booleans, and nullable fields describe one lifecycle | Coproduct | Product with optional fields | Decoder + core state type | exhaustive handling + invalid legacy fixture tests |
| Same input predicate repeated at controllers, services, serializers | Refined type / equalizer | Raw primitive plus helper validation | Parse / constructor boundary | accept valid, reject invalid, normalization idempotence |
| `customer.accountId != subscription.accountId` appears repeatedly | Pullback witness | Plain pair + scattered assertions | checked constructor | mismatch rejection + preserved projections |
| Large branch decides pricing, rendering, or policy | Exponential | Bigger state machine | function / strategy seam | fixture parity against old branch |
| Rule syntax mixed with execute / explain / log | Free construction | More conditionals inside existing class | AST + one interpreter | interpreter consistency + differential tests |
| Several fields always travel together and are consumed independently | Product | Coproduct | record / struct / object | constructor and projection consistency |
| Several old views must agree on new internals | Coherent observations | Independent adapters | read-model/projection boundary | overlapping observation coherence |
| Generated artifacts lose provenance | Generation path vocabulary | anonymous callbacks | generation/lowering boundary | lowering equals direct interpretation |
| Public contract determines implementation | Lifted implementation | ad hoc service design | one contract case | projection matches required behavior |
| Public contract determines implementation but projection loses evidence | Free builder or obstruction report | pretending a lift exists | one projection function | project(free(required)) passes or obstruction named |
| Public policy implies internal checks | Residual obligations | ad hoc validators | one policy case | missing obligation fails projection |
| Callbacks carry architecture behavior | Explicit IR | hidden closure registry | plugin/handler seam | apply/interpreter equivalence |
| Stateful behavior is duplicated across handlers | Behavioral coalgebra | scattered mutation branches | one transition + observer | trace law and invalid transition rejection |
| Operation syntax needs multiple runtimes | Effect signature + handlers | callbacks embedded in workflow | one operation + test handler | handler observation parity |

## Output contract

For any non-trivial response, produce these headings in order:

1. **Track**
2. **Signal**
3. **Construction**
4. **Why this instead of nearby alternatives**
5. **Seam / files**
6. **Boundary and compatibility plan**
7. **Before -> After**
8. **Verification**
9. **Runtime-only leftovers**
10. **Next seam** (optional)

For Track D, also include:

- **World / boundary inventory**
- **Boundary kind**
- **Canonical boundary artifact**
- **Law / proof signal**
- **Falsifier**

For Track E, also include:

- **Composition Certificate**
- **Boundary Normal Form status**
- **Bypass policy**
- **Certification result**: verified / obstructed / primitive exception

For lift-shaped Track D or Track E, also include:

- **Projection `P : B -> C`**
- **Freyd/AFT boundary diagnostic** when `P` is vague, lossy, or intended to support a free builder
- **Builder or obstruction**

For behavioral Track D, also include:

- **State/transition shape**
- **Observation function**
- **Trace law**

For effect-handler Track D, also include:

- **Operation signature**
- **Handler(s)**
- **Handler observation law**

For Track F, also include:

- **Semantic consumer**
- **Task schema `T_q`**
- **Observables `Obs_q`**
- **Context Certificate**
- **Freshness / provenance / missingness / contradiction plan**
- **Rendering law**


For Track H, also include:

- **Current world and hard operation**
- **Easy world / category pivot**
- **Syntax world and semantic world**, when applicable
- **Interpreter / handler / compiler / renderer**
- **Soundness / adequacy / preservation law**
- **Category Pivot or Syntax/Semantics Certificate**
- **Falsifier**

For Track B, Track C, Track D, Track F, Track G, or Track H, also update `.universalist-plan.md`.

## Guardrails

- Prefer plain engineering language over category jargon when both say the same thing.
- Do not claim a universal construction without naming the constructor, eliminator, comparison, or factorization behavior it buys.
- Do not recommend HKT-heavy or typeclass-heavy patterns where the language cannot carry them cleanly.
- Do not propose new validation or property-test libraries without user approval.
- Do not widen the seam just because the larger design looks elegant.
- Call out persistence, serialization, and public API breakage explicitly.
- Say when a validator is only runtime protection.
- Do not use Kan/Yoneda/Coyoneda/Freyd vocabulary unless it produces a concrete artifact and law test.
- Defunctionalize only when higher-order behavior crosses a meaningful boundary.
- Treat Freyd/AFT as a projection diagnostic, not as a theorem recital.
- Treat opaque subsystems as primitives behind explicit observation/projection boundaries.
- Do not sheafify merely to decorate an abstraction; sheafify only when local usage evidence shows inconsistency, missing glue, non-unique glue, or excess possibility.
- Do not pivot categories merely to sound profound; pivot only when the easy world makes inspection, proof, synthesis, minimization, replay, or certification materially easier and the transfer law is stated.
- Do not claim an abstraction is exact without a usage site, local sections, overlap checks, gluing law, and falsifier.
- Do not claim syntax/semantics separation without constructors/formation rules, interpreter, observations, soundness/adequacy law, and falsifier.

## Internal mechanics and companion skills

Use **this skill** as the only top-level Universal Architecture workflow. Do not hand off to a separate `kan` skill; the former Kan material is now an internal mechanics layer.

Mechanics are used only after `universalist` has identified:

```text
signal
seam/worlds
boundary kind
known side
unknown location
canonical artifact
witness slice
law/falsifier
certificate type
```

Then read the relevant internal mechanics reference or run:

```bash
./scripts/emit_mechanics_report.sh <topic> <language>
```

Mechanics topics include Kan extensions/lifts, Freyd/AFT, Yoneda/Coyoneda, codensity presentations, categorical-data/context compilation, CQL fit, pushout reconciliation, defunctionalization, possibility sheafification, category pivots, and syntax/semantics.

- Use **`invariant-ace`** when the main job is discovering or pinning down invariants before choosing structure.
- Use **`accretive-implementer`** after the construction is chosen and the task becomes ordinary implementation.
- Use **`repeatedly-apply-skill`** when sweeping the repo for multiple seams or doing a multi-pass campaign.

## References

Core references:

- `references/universalist-overview.md`
- `references/discovery-signals.md`
- `references/language-encoding-matrix.md`
- `references/framework-boundaries.md`
- `references/cost-model-and-false-positives.md`
- `references/structures-and-laws.md`
- `references/testing-playbook.md`
- `references/migration-playbooks.md`
- `references/case-studies.md`
- `references/sources.md`

Universal architecture references:

- `references/universal-architecture-kernel.md`
- `references/universal-architecture-ecosystem.md`
- `references/artifact-selection-by-unknown-location.md`
- `references/canonical-boundary-artifacts.md`
- `references/kan-boundaries-for-universalist.md`
- `references/freyd-aft-boundary-diagnostic.md`
- `references/effects-and-coalgebras.md`
- `references/yoneda-coyoneda-defunctionalization.md`
- `references/universal-architecture-law-tests.md`
- `references/universal-composition-doctrine.md`
- `references/composition-certificates.md`
- `references/boundary-normal-form.md references/presentation-strategies.md references/dense-dual-presentation.md references/semantic-compression.md`


Sheafification / exact-abstraction references:

- `references/possibility-sheafification.md`
- `references/sheafification-certificates.md`
- `references/abstraction-normal-form.md`
- `references/abstraction-manipulator-playbook.md`

Category pivot / syntax-semantics references:

- `references/category-pivot.md`
- `references/syntax-semantics-pivot.md`
- `references/category-pivot-certificate.md`
- `references/syntax-semantics-certificate.md`

Internal mechanics references from former `kan` skill:

- `references/mechanics/README.md`
- `references/mechanics/foundations.md`
- `references/mechanics/kan-lifts.md`
- `references/mechanics/freyd-aft.md`
- `references/mechanics/yoneda-coyoneda.md`
- `references/mechanics/codensity-presentations.md`
- `references/mechanics/defunctionalization.md`
- `references/mechanics/context-compilation.md`
- `references/mechanics/cql-context-management.md`
- `references/mechanics/possibility-sheafification-mechanics.md`
- `references/mechanics/category-pivot-mechanics.md`
- `references/mechanics/syntax-semantics-mechanics.md`

## Scripts

- `scripts/init_universalist_plan.sh`
- `scripts/detect_signals.py`
- `scripts/emit_scaffold.py`
- `scripts/emit_boundary_adapter.py`
- `scripts/emit_verification_plan.py`
- `scripts/emit_law_test_stub.sh`
- `scripts/emit_universal_artifact_matrix.sh`
- `scripts/emit_canonical_artifact_plan.sh`
- `scripts/emit_universal_architecture_prompt.sh`
- `scripts/emit_freyd_boundary_diagnostic.sh`
- `scripts/emit_composition_certificate.sh`
- `scripts/emit_boundary_normal_form_plan.sh scripts/emit_presentation_diagnostic.sh`
- `scripts/emit_context_certificate.sh`
- `scripts/emit_context_compiler_plan.sh`
- `scripts/emit_exact_context_prompt.sh`
- `scripts/check_universalist.sh`


- `scripts/emit_possibility_sheafifier.sh`
- `scripts/emit_sheafification_certificate.sh`
- `scripts/emit_abstraction_normal_form_plan.sh`
- `scripts/emit_category_pivot.sh`
- `scripts/emit_syntax_semantics_certificate.sh`
- `scripts/emit_mechanics_report.sh`
- `scripts/emit_kan_stub.sh`
- `scripts/emit_codensity_presentation.sh`
- `scripts/emit_context_compilation_report.sh`
- `scripts/emit_cql_context_report.sh`
- `scripts/emit_sheafification_kan.sh`

## Templates

- `templates/universalist-plan.md`
- `templates/universalist-report.md`
- `templates/universal-architecture-report.md`
- `templates/freyd-boundary-diagnostic.md`
- `templates/composition-certificate.md`
- `templates/boundary-normal-form-report.md`


- `templates/sheafification-certificate.md`
- `templates/abstraction-normal-form-report.md`
- `templates/category-pivot-certificate.md`
- `templates/syntax-semantics-certificate.md`
