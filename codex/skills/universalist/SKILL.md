---
name: universalist
description: "Use whenever implementing, reviewing, or resolving code that considers a boundary: creating, changing, preserving, validating, migrating, bypassing, or removing how values, effects, state, evidence, authority, or behavior cross modules, APIs, schemas/DTOs, serializers, storage/wire formats, parsers/validators, handlers, runtimes, protocols, plugins/tools/CLIs, processes, repositories, or public/internal contracts. Trigger even for ordinary feature work or PR/review resolution when boundary behavior is in scope; boundary consideration itself is the signal. Start with one boundary/seam; identify source/target worlds, carriers, operations, observations, laws/non-laws, interpreter/projection/handler, compatibility, falsifier, and resource impact, then choose the smallest honest construction. Keep implicit invocation enabled. Team mode only on explicit request. Includes ADD, Kan/Yoneda/Coyoneda/Freyd-AFT/Freyd-category/operad/codensity/CQL/sheafification mechanics."
---

# Universalist

Use this skill whenever a code boundary is considered. Its highest leverage comes from changing the **shape of truth** in a codebase, but it may conclude that an existing boundary is already exact and should be preserved.

Default operating discipline: one signal, one seam, one smallest honest construction.

## Boundary-trigger mandate

Use this skill whenever implementation, refactoring, review, migration, or resolution work considers a code boundary. Do not wait for category-theory language or a broad architecture request. Boundary consideration itself is the activation signal.

A code boundary is any seam where values, effects, state, evidence, authority, or observable behavior cross between owners or representations. This includes module/package APIs, public/internal contracts, DTOs/schemas/codecs, parsers/validators, storage/wire formats, syntax/interpreters/compilers, pure/effect handlers, state machines/protocols, plugins/tools/CLIs, processes, repositories, and deployment surfaces.

A boundary is considered whenever the task chooses, creates, changes, preserves, validates, migrates, bypasses, removes, or resolves that seam.

Apply the lens in both directions:

- **Implementation** — name the boundary and owner; state preserved, forgotten, generated, and observed information; name compatibility, law, and falsifier before mutation; then let the repo's normal implementation flow carry the change.
- **Resolution** — classify whether the finding or failure is a boundary liability; repair it at the owner boundary; reject symptom-only patches that leave boundary drift; verify the boundary disposition and law after repair.

Resolution includes PR/review findings, failing tests, regressions, migration defects, compatibility defects, and closeout decisions whose repair changes or relies on boundary behavior.

Activation is broad; escalation is narrow. If the existing boundary is already exact, record it as preserved and continue ordinary implementation or resolution. Do not invent categorical structure merely because the lens activated.

## Trigger-to-evidence kernel

When the boundary trigger fires, execute this kernel before entering the longer doctrine:

1. Record the compact boundary disposition immediately:

```text
Boundary:
Disposition: preserved / introduced / changed / repaired / removed / bypass-justified
Disposition rationale and evidence:
Owner:
Source / target:
Preserved / forgotten / generated / observed:
Law:
Falsifier:
```

2. Decide whether the route is consequential under **Decision observability**: at least two plausible routes materially differ in persistent behavior, authority, compatibility, migration, or proof obligations.
3. If the route is consequential, select the track, allocate one fresh ledger-addressed Universalist plan through **Step 0**, and emit exactly one root `SDR-v1`. When mutation is in scope, complete this gate before mutating the seam. A consequential `UNI-PRESERVE` decision follows the same gate.
4. If the route is not consequential, retain the compact disposition and continue the ordinary workflow. Do not allocate a plan or emit `SDR-v1` solely because the skill activated.

This kernel is the execution entrypoint. **Step -1**, **Step 0**, and **Decision observability** remain the detailed authorities for the receipt, plan, and decision contract.

This is an **inner lens** for choosing the right structural move. It may trigger during ordinary implementation or resolution when a boundary is considered, but it does not replace the repo's implementation, review, or closeout workflow.

This is now the single top-level skill for the Universal Architecture doctrine. The former `kan` skill has been folded into this skill as an internal mechanics layer under `references/mechanics/` and `templates/mechanics/`.

## Construction card decision table

For a consequential structural choice, state the **ordinary candidate** first, then consult `references/universal-construction-registry.yaml` and only the card fragments relevant to the seam's axis and evidenced signals. The 55 YAML cards are active architectural decision doctrine, not passive reference data and not executable commands.

For each relevant card, record one evidence-bound disposition: **selected**, **rejected**, **contradicted**, or **unresolved**. A selectable card may displace the ordinary candidate only when it materially changes persistent behavior, authority, compatibility, representable states, legal composition, effect semantics, locality, information flow, interpreter, construction paths, proof, resources, existence, or migration. Support-only cards may guard reasoning but never become implementation artifacts.

When one seam has independent pressures on several axes, evaluate each axis separately before root synthesis. Do not select one global card that silently drops effect order, description composition, context framing, locality, transport, or presentation obligations.

Repository evidence must establish a card's signals, prerequisites, laws, and required proof profile. The universal proof profile is existence, commutation or preservation, competitor mediation, canonicality or uniqueness-up-to, effectivity, and falsifier. The obstruction profile is nonexistence, counterexample, stability, effectivity, falsifier, and reopening condition. Card prose is guidance, not repository proof.

Do not let signal count, evidence count, `diagnostic_order`, or registry order manufacture a winner. Missing evidence leaves a card unresolved; it is not an obstruction. A complete constructive card and a complete obstruction remain an explicit evidence conflict until the root adjudicates them.

Ordinary routing follows boundary disposition. An ordinary solution for an introduced, changed, repaired, or removed seam is `UNI-ORDINARY`, not `UNI-PRESERVE`. `UNI-PRESERVE` is reserved for an already exact preserved seam. A justified primitive bypass uses `UNI-OBSTRUCT`.

The registry's `universal.role: emitter` names the categorical direction from a selected artifact to admissible consumers. It never denotes a shell or Python emitter.

Default user-facing output is plain repository language. Expose expert names and linked theorem references only when the user explicitly asks for the mathematical derivation.

## Doctrine index

Universalist includes Track A0, Track D, Track E, Track F, Track G, Track H, and Track I. It uses Universal architecture, Domain Algebra Discovery, Algebra before architecture, Universal Composition Doctrine, Composition Certificate, Boundary Normal Form, Presentation Strategy Doctrine, Dense-Dual Presentation, Exact Context Doctrine, Context Certificate, Context Normal Form, Verified Context Plane, Possibility Sheafification, Sheafification Certificate, Abstraction Normal Form, Syntax/Semantics Pivot, Easy-World Transfer, Category Pivot Certificate, World and Boundary Inventory, Boundary Kind Taxonomy, Boundary Law Catalogue, Unknown-location artifact selector, ADD carriers/operations/observations/laws, Freyd/AFT, Freyd categories, operads, composition geometry, free builder, obstruction report, Behavioral coalgebra, Effect signature, and the internal mechanics references for `P : B -> C`. Core guardrails include: Allow arbitrary domain primitives; Allow arbitrary sources; Forbid uncertified semantic consumption; Operational stores own mutation; Verified context planes own semantic publication; Presentations compress; Do not merely abstract. Sheafify possibility.
Do not force a hard problem to stay in the ordinary executable-program world when syntax, semantics, posets, relations, coalgebras, schemas, resources, or presheaves make the required operation explicit. For whole-system work, require an effective computational substrate, concrete primitive register, universal evaluator or equivalent, recursion/partiality, effect and state semantics, observations, resource model, and executable witnesses.

The enriched slogan is:

> Universal architecture is the practice of designing software around canonical boundary artifacts: **free syntax, coherent observations, transported semantics, lifted implementations, free builders behind projections, obstruction reports, behavioral coalgebras, effect signatures with handlers, explicit IRs, and law tests.**

Core discipline:

> Allow arbitrary domain primitives, but do not allow arbitrary composition across architecture boundaries.

> Do not merely abstract. Sheafify possibility.

Ordinary code may live inside a boundary: I/O, math, parsing, vendor APIs, database drivers, model calls, clocks, randomness, local algorithms, and low-level loops. Composition boundaries should be explicit artifacts: syntax, observations, projections, transports, lifts, handlers, state transitions, IRs, or law tests.



## Track A0 — Domain Algebra Discovery

Use Track A0 before universal-architecture escalation when the local world is not yet algebraically clear. This is the former Algebra-Driven Design kernel folded into `universalist`.

Core rule:

```text
Algebra before architecture.
```

Do not choose a universal boundary artifact until the local domain algebra has exposed the carriers, operations, observations, laws, and non-laws that make the world real.

A compact Domain Algebra pass produces:

```text
Domain:
Carriers:
Operations / constructors / eliminators:
Observations / equality criteria:
Laws:
Non-laws / counterexamples:
Interpreters / effect boundaries:
Property tests / falsifiers:
Architecture implications:
Escalation candidates:
```

Use Track A0 when:

- carriers or data domains are unclear;
- operations are named only by controllers, services, or helper functions;
- equality is implicit or observation-dependent;
- laws are suspected but untested;
- tempting algebraic laws may be false under stronger observations;
- pure and effectful operations are mixed;
- the system needs property-test-derived implementation guidance before a larger Track D/E/F/G/H move.

ADD mappings into Universalist:

| ADD term | Universalist role |
| --- | --- |
| Carrier | object/type/world inhabitant |
| Operation | morphism, constructor, eliminator, effect, transition |
| Observation | semantic consumer / equality probe / Yoneda-like observation |
| Law | invariant, interpreter law, boundary law, property test |
| Non-law | falsifier, obstruction, false equivalence, observation-strength warning |
| Interpreter | syntax/semantics boundary, handler, evaluator |
| Property test | executable witness |
| Architecture implication | Track B/D/E/F/G/H routing candidate |

The output of Track A0 should either stay local—types, operations, law tests—or justify escalation:

```text
law failure at a boundary      -> Track D / Track E
uncertified context            -> Track F
inexact abstraction            -> Track G
wrong representation category  -> Track H
whole-system substrate design  -> Track I
```


## Effective Universal Architecture Thesis

Thesis:

> I can implement any computable software on an effective universal computational substrate while using category theory to define its entire architecture of composition, interpretation, effects, state, boundaries, observations, and laws.

Treat this as an engineering thesis with proof obligations, not as permission to call every abstraction categorical. Category theory governs architecture; effective syntax, interpreters, concrete primitives, and runtime machinery make it executable.

A qualifying substrate must make these capabilities concrete:

```text
program/data representation
universal evaluation or equivalent interpretation
composition and identities
general recursion, iteration, partiality, or another universal-computation mechanism
external effects and concrete primitives
state and ongoing interaction
concurrency/distribution when the target requires them
observations and an equivalence notion
finite/effective presentations of categorical artifacts
resource semantics: time, space, latency, failure, capability, or cost
```

Use the **Substrate Reality Law**:

```text
No universality claim without an effective program representation.
No categorical artifact without an executable interpreter or compiler.
No external behavior without a named concrete primitive and handler.
No semantic-equivalence claim without observations.
No practical architecture without a resource model.
```

A system is in **Effective Categorical Normal Form** when:

- every architecture-level composition is governed by a named categorical artifact;
- every artifact has a finite or effective presentation;
- every presentation has an interpreter, compiler, handler, projection, or lowering;
- concrete primitives are isolated behind explicit effect/boundary interfaces;
- recursion/partiality and ongoing interaction are modeled honestly;
- required observations and laws are executable;
- resource and deployment constraints are part of the architecture rather than afterthoughts;
- unsupported constructions produce obstruction reports instead of decorative mathematics.

Use Track I when the task is to design, implement, or refactor an entire software capability under this thesis.

## Categorical Substrate Team Mode

Universalist is a workflow skill with bundled custom subagents. Subagent use is **explicitly gated**:

```text
Only spawn the team when the current user prompt explicitly asks for subagents,
parallel agents, team mode, the categorical substrate team, or equivalent delegation.
```

Otherwise run the same workflow in the root agent without spawning children.

When team mode is authorized, use the smallest sufficient roster from `codex/agents/`:

- `universalist-world-cartographer` — map worlds, boundaries, existing abstractions, primitives, observations, and evidence.
- `universalist-substrate-architect` — test computational universality, effective presentation, recursion/partiality, and concrete primitive support.
- `universalist-categorical-architect` — select canonical constructions, category pivots, and boundary artifacts.
- `universalist-semanticist` — separate syntax/semantics and model effects, state, interpretation, observations, and equivalence.
- `universalist-resource-realist` — pressure-test time, space, latency, concurrency, failure, security, deployment, and operational fit.
- `universalist-proof-auditor` — challenge effectivity, soundness, completeness, observational equivalence, laws, and falsifiers.
- `universalist-witness-implementer` — implement exactly one root-selected witness seam after architecture is synthesized.
- `universalist-verifier` — independently verify the implemented witness and certificate claims.

Workflow:

```text
explicit team request
  -> spawn 2-6 read-only specialists in parallel
  -> wait for all packets
  -> root synthesizes one Effective Universal Architecture Certificate
  -> proof auditor challenges it
  -> root selects one witness seam
  -> one writer implements it
  -> verifier checks the laws and resource claims
  -> root integrates, certifies, and stops
```

The root agent owns scope, synthesis, final decisions, write ordering, closure, and user-facing conclusions. Specialist packets are evidence, not truth. Read-only agents must not edit. Only one writer may mutate a seam at a time. Child agents must not recursively spawn more agents.

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

## Composition Geometry Selector

A universal artifact is not enough when the **geometry of composition** is itself the architectural decision. Before encoding a call graph, pipeline, service graph, effect runner, or subsystem assembly, select the weakest structure that makes legal composition explicit.

Use this selector:

| Composition pressure | Preferred structure | Architectural reading |
| --- | --- | --- |
| One transformation after another | Category | sequential typed composition |
| Independent context or parallel composition with lawful interchange | Monoidal category | components compose side-by-side |
| Pure values coexist with ordered call-by-value effects | Freyd / premonoidal category | pure transformations commute; effectful computations preserve sequencing |
| Typed many-input, one-output hierarchical assembly | Colored operad | legal component wiring and substitution grammar |
| Multiple inputs and outputs are fundamental | PROP or properad | network/process architecture without artificial product bundling |
| Feedback, recursion, or cyclic signal flow is fundamental | Traced monoidal category, temporal wiring, or coalgebra | explicit feedback and ongoing behavior |
| Inputs are consumable, affine, graded, permissioned, or costly | Linear / graded / resource-sensitive category | resource use and duplication are part of composition |

Core distinction:

```text
Categories describe transformations.
Operads describe legal hierarchical assembly.
Freyd categories describe ordered effectful execution under call-by-value.
Algebras/interpreters give these structures concrete semantics.
```

Use a **colored operad** when typed ports, hierarchical substitution, and several interpretations of the same wiring matter. Use a **nonsymmetric/planar operad** when order is semantic. Escalate to a PROP/properad for genuine multiple-output wiring, and to traced/coalgebraic structure for feedback.

Use a **Freyd category** when values and computations share types, pure code should remain freely compositional, effects make evaluation order observable, and only certified-central operations may commute or parallelize. Distinguish this from **Freyd's adjoint functor theorem**: use `freyd-category` for effectful call-by-value mechanics and `freyd-aft` for free-builder existence diagnostics.

Do not introduce these structures when ordinary composition is already exact, the grammar changes no code or tests, or a smaller sum/product/interface suffices.

## Comonadic Spatiality Selector

Use comonadic spatiality only when locality changes correctness, ownership, authority, evidence, or another required observation. Prefer an ordinary labelled graph or context object when it already makes the seam exact.

Before selecting this mechanics family, require:

- named points and local patches;
- explicit local-to-global identity and provenance;
- an effective finite, bounded, indexed, incremental, or queryable halo;
- center/counit and nested-neighborhood coherence;
- a basis/reconstruction witness or explicit non-basis status;
- restriction/germ behavior, locality-preserving transport, and a resource law;
- a falsifier where the point survives but required locality or labels do not.

When those obligations change the artifact and proof, read `references/comonadic-spatiality-doctrine.md` and `references/mechanics/comonads-as-spaces.md`. Distinguish comonad coalgebras from behavioral coalgebras and ordinary comonad maps from continuous locality-preserving maps.

## Do not trigger for

- Work wholly internal to one established boundary that does not choose, change, preserve, validate, migrate, bypass, remove, or resolve boundary behavior.
- Pure performance tuning, UI polish, formatting, or prose-only documentation that neither changes nor depends on a code boundary.
- Category-theory exposition that does not change or adjudicate a concrete code seam, construction, boundary, or proof signal.

Broad rewrites without a stable seam and domains with unstable rules still trigger the lens when boundaries are under consideration. Use Track A or Track A0 to name the obstruction and avoid freezing premature structure.

## Step -1 — World and Boundary Inventory

Use the compact boundary disposition from the **Trigger-to-evidence kernel** for every boundary-triggered implementation or resolution. For any non-trivial structural request, expand it into the full world and boundary inventory below. This prevents fake category labels and keeps the response anchored in repo reality.

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
| Pure/effect boundary | pure values enter ordered effectful call-by-value execution | Freyd/premonoidal category, centrality and order laws |
| Component assembly | typed ports and hierarchical subsystem wiring | colored operad; PROP/properad for multiple outputs |
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
- effect-order drift: computations are reordered, parallelized, duplicated, or discarded without a centrality/commutativity witness;
- assembly drift: typed components are wired through arbitrary call graphs rather than an explicit hierarchical composition grammar;
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
effect-order drift    -> Freyd/premonoidal effect geometry
assembly drift        -> colored operad / PROP / properad
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
| Freyd effect-order law | pure embedding preserves identity/composition; reordering is allowed only with observational commutativity |
| Operadic substitution law | `interpret(substitute(f,g1,...,gn)) == compose(interpret(f),interpret(g1),...,interpret(gn))` |
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

### Track A0 — Domain Algebra Discovery

Use when the local world is not yet algebraically clear.

Deliver:

- domain;
- carriers;
- operations / constructors / eliminators;
- observations / equality criteria;
- laws;
- non-laws / counterexamples;
- interpreters / effect boundaries;
- property tests / falsifiers;
- architecture implications;
- escalation candidates.

### Track A — Diagnosis only

Use when the user wants analysis, design review, refactor advice, or a structural reading of the current code.

Deliver:

- observed signal;
- chosen construction;
- why nearby alternatives are worse;
- first seam to attack;
- proof signal;
- compatibility notes;
- boundary disposition;
- whether this is ordinary universalist structure or universal-architecture territory.

### Track B — One-seam refactor

Use when the user wants code changes, but the right move is narrow and reviewable.

Deliver:

- one seam only;
- smallest honest construction;
- canonical boundary artifact if needed;
- adapter-first staging when a public boundary exists;
- boundary disposition and owner;
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
- current ledger-addressed Universalist plan update.

### Track D — Universal architecture boundary

Use when the smell is no longer just “choose a better type” but “choose the canonical artifact at a boundary.”

Deliver:

- worlds involved;
- boundary map, projection, embedding, interpreter, forgetful API, or observation map;
- known side and unknown artifact;
- canonical boundary artifact;
- composition geometry: category / monoidal / Freyd-premonoidal / operad / PROP-properad / traced-coalgebraic / resource-sensitive;
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
- typed component/service/dataflow wiring where legal hierarchical assembly should replace an accidental call graph;
- effectful call-by-value boundaries where sequencing, centrality, or claimed parallelism must be explicit;
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
11. **Freyd effect geometry** — pure values and ordered effectful computations share types without granting unjustified interchange.
12. **Operadic composition grammar** — typed ports and hierarchical substitution define which subsystems can be assembled.
13. **Explicit IR** — callbacks, handlers, continuations, predicates, mappers, and rules become data plus interpreter.
14. **Exact context** — task-indexed context instances prepared before semantic consumption.
15. **Context certificates** — schema, observables, provenance, freshness, missingness, contradiction, rendering, and falsifier for a context.
16. **Law tests** — executable witnesses that the boundary artifact does what it claims.

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
| In pure/effectful call-by-value composition | Freyd / premonoidal effect boundary | pure embedding laws plus an order-sensitive counterexample |
| In typed hierarchical component assembly | Colored operad / operadic wiring syntax | interpretation preserves substitution; illegal wiring rejected |
| After a source-to-target boundary `K` | Transported semantics / Lan-style | identity or embedding path preserves behavior |
| In coherent behavior under observations | Coherent observations / Ran/Yoneda-style | overlapping observations commute |
| In coherent local context around points | Comonadic spatiality | center and nested-neighborhood laws; locality falsifier |
| In patches intended to generate situated objects | Density comonad / basis | canonical reconstruction or explicit non-basis obstruction |
| Across a locality-sensitive boundary | Continuous comonadic map / spatial boundary | required halos, restrictions, identities, and labels are preserved |
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


## Freyd Category Diagnostic for Effectful Call-by-Value

Use this mechanics only when the architectural pressure is pure/effectful composition, not free-builder existence.

Model:

```text
C = pure values and pure transformations
K = effectful computations with explicit sequencing
J : C -> K = pure embedding, identity on shared objects/types
```

Require:

- pure morphisms are central and may commute with surrounding effects;
- effectful computations are not reordered unless an observational commutativity witness exists;
- context/threading of values through computations is explicit;
- claimed parallelism has an ordering, centrality, or commutation law;
- higher-order effectful functions use a representable/closed or strong-monad-like presentation when needed.

Certificate fields:

```text
pure world
computation world
pure embedding J
central operations
evaluation order
context action
noncommuting witness
observational law
```

Do not confuse this with Freyd/AFT. The mechanics commands are intentionally separate: `freyd-aft` and `freyd-category`.


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


### Track I — Effective Universal Software Synthesis

Use when the user wants to design, build, or substantially refactor a whole software capability so that category theory defines the architecture while an effective universal substrate and concrete primitives make it executable.

Typical triggers:

```text
implement any computable software
computationally universal categorical architecture
design the whole system from first principles
use the Universalist custom subagent team
make composition/effects/state/observations/laws categorical end to end
build a reusable substrate rather than a one-off feature
```

Deliver:

1. **System and observables** — user-visible behavior, external environment, equivalence notion, and non-goals.
2. **Effective substrate** — program representation, universal evaluator or equivalent, recursion/partiality, composition, state, interaction, and target runtime.
3. **Concrete primitive register** — I/O, storage, clocks, randomness, network, foreign APIs, numeric kernels, humans, models, hardware, and their handlers.
4. **World/boundary architecture** — categories/worlds, objects, transformations, boundaries, embeddings, projections, interpreters, migrations, and ownership.
5. **Syntax/semantics architecture** — editable syntax/IR, semantic domains, interpreters/handlers, observation functors, and adequacy/soundness laws.
6. **Effects/state/interaction** — effect signatures, handlers, state transitions, coalgebras/protocols, concurrency, failure, and compensation.
7. **Canonical construction map** — products, coproducts, refinements, free objects, Kan extensions/lifts, adjunctions, Freyd/premonoidal effect geometry, operads/PROPs/properads, observations, quotients, sheafification, or obstruction reports.
8. **Presentation/effectivity plan** — finite/effective representation, compilation/lowering, algorithms, termination/partiality boundary, and domain-specific assumptions.
9. **Resource model** — complexity, latency, memory, throughput, capability/security, persistence, deployment, and operational observability.
10. **Effective Universal Architecture Certificate** — laws, falsifiers, obstruction ledger, primitive exceptions, and proof commands.
11. **One witness seam** — the smallest end-to-end slice that proves the substrate can express, execute, observe, and verify real behavior.
12. **Accretive continuation** — next seam only after the witness is verified.

In explicit team mode, synthesize specialist packets before choosing the witness. Do not ask parallel writers to implement competing architectures. The root selects one architecture and one seam.

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
- If proposing Freyd/premonoidal structure, name pure and effectful worlds, the pure embedding, evaluation order, central operations, and one noncommuting witness.
- If proposing an operad, name colors/ports, primitive operations, substitution rules, symmetry/order, semantic algebra, forbidden wiring, and the substitution law.
- If proposing coalgebra/protocol structure, include transition, observation, trace law, and invalid-transition witness.

## Step 0 — Allocate a ledger-addressed plan

For every consequential route, including Track B, Track C, Track D, Track F, Track G, Track H, or Track I, create one fresh progress record through the native Ledger CLI before mutation:

Before allocation, load `$ledger` and complete `$ledger ensure` once. After
readiness, invoke native `ledger` directly. Consequential plans and receipts require
Ledger 0.10.6 or newer and Skills Seq 0.3.52 or newer.

```bash
ledger --source universalist create \
  --repo PROJECT_ROOT \
  --template /path/to/universalist/templates/universalist-plan.md
```

Ledger owns plan identity, collision-safe creation, and address resolution. Universalist owns the Markdown fields and subsequent updates. The returned `universalist-plan-address/v1` receipt contains the exact `plan_id`, `created_at`, and absolute `path` for the run.

Plans live at:

```text
.ledger/universalist/plan-{plan-id}.md
```

The plan id is `YYYYMMDDTHHMMSSnnnnnnnnnZ-NNNN`: a lexicographically sortable UTC nanosecond timestamp plus an atomic collision ordinal. Every create invocation must allocate a new file and must never reuse, truncate, or overwrite an earlier plan. Existing `.ledger/universalist-plan-{plan-id}.md` files remain read-only legacy addresses; `path` and `latest` may resolve them, but new plans must use the namespaced path. Do not create or update the legacy project-root `.universalist-plan.md`.

Retain the returned plan id for the entire run. Resolve that exact address with:

```bash
ledger --source universalist path --repo PROJECT_ROOT --id PLAN_ID
```

Use `latest` only when no run-specific address survives:

```bash
ledger --source universalist latest --repo PROJECT_ROOT
ledger --source universalist latest --repo PROJECT_ROOT --format path
```

`latest` scans valid plan ids and does not maintain a mutable pointer. Before resuming a recovered latest plan, verify that its Track, Signal, and Seam / files identify the current task; concurrent runs may have newer plans. If the required ledger source is unavailable, stop with the exact missing command/version rather than inventing an id or writing the file directly.

Minimum fields:

```md
# Universalist Plan

## Track:
## Boundary disposition:
## Disposition rationale and evidence:
## Signal and evidence:
## Ordinary candidate:
## Architectural axis:
## Relevant cards and dispositions:
## Alternatives considered:
## Material architectural delta:
## Evidence debt:
## Selected route:
## Construction:
## Canonical boundary artifact:
## Worlds / boundaries inventory:
## Boundary kind:
## Composition geometry:
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
## Root decision receipt: pending / emitted
## Status: planned / editing / verified / staged
## Next seam:
```

If context compacts, resolve the retained plan id and read that file first. If the id was lost, resolve `latest`, verify its task identity, then resume from its status line.

## Decision observability

Use [references/decision-contract.yaml](references/decision-contract.yaml) as the route authority for consequential Universalist decisions. A decision is consequential only when at least two plausible routes materially differ in persistent behavior, authority, compatibility, migration, or proof obligations. Routine seams, ceremonial activation, and uncontested choices do not allocate a plan or receipt.

After the root selects the route and before mutating the implementation seam, emit exactly one root-scoped receipt from the current ledger-addressed plan:

```bash
ledger --source universalist emit \
  --plan "$UNIVERSALIST_PLAN" \
  --contract /path/to/universalist/references/decision-contract.yaml \
  --question "Which construction owns this seam?" \
  --selected-route UNI-ORDINARY \
  --rejected-route UNI-CANONICAL \
  --expected-outcome "The owner boundary enforces one observable law." \
  --disposition changed \
  --construction "checked adapter at the owner boundary" \
  --law "required observations are preserved" \
  --falsifier "a mismatched source is accepted" \
  --advanced-mechanics none \
  --evidence-ref "code:path" \
  --write-plan
```

Ledger 0.10.6 or newer with Skills Seq 0.3.52 or newer derives the decision id, skill version, contract fingerprint, repository HEAD, plan id, and plan path. It consumes Seq's parsed receipt-binding projection from one immutable snapshot and validates the receipt through Seq before writing. Universalist owns the decision policy and contract; Ledger owns receipt construction and atomic plan mutation. Emit the command's JSON output once as a root assistant message so Seq can observe the decision. Keep the same concrete receipt at the end of the plan. Do not paste a static schema example.

One plan represents one changed seam and admits one receipt. Allocate a fresh plan for a distinct seam. In team mode, workers reference the root `decision_id`; they do not echo the receipt unless they own a genuinely distinct seam with its own plan. Keep route aliases empty and use exact route ids or structured receipts; generic prose aliases contaminate retrospective audits. Set `--advanced-mechanics` to `none` unless a named mechanics topic produces the concrete artifact, interpreter or projection, law, and falsifier.

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

11. **Update the current ledger-addressed plan**

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

For any non-trivial response, produce these headings in order, embedding them inside the repository's host workflow when that workflow already owns closeout:

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

For every boundary-triggered implementation or resolution, use **Boundary and compatibility plan** to record the compact boundary receipt: boundary, disposition, owner, source/target, preserved/forgotten/generated/observed information, law, and falsifier. Activation may conclude that the existing boundary is preserved and no new abstraction is required.

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


For Track I, also include:

- **Effective substrate and universality mechanism**
- **Concrete Primitive Register**
- **Universal evaluator / interpreter / compiler path**
- **Recursion / partiality / interaction model**
- **Effects / state / concurrency architecture**
- **Observation and equivalence model**
- **Resource model**
- **Team roster and specialist packets**, when explicitly authorized
- **Effective Universal Architecture Certificate**
- **One witness seam and stop point**
- **Obstruction ledger**

For Track B, Track C, Track D, Track F, Track G, Track H, or Track I, also update the exact ledger-addressed plan allocated for the current run.

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
- Do not claim computational universality without naming the effective program representation, evaluator or equivalent, recursion/partiality mechanism, and concrete runtime.
- Do not confuse categorical definability with implementability; require an effective presentation and executable lowering.
- Do not hide external reality behind abstract morphisms; maintain a Concrete Primitive Register with handlers and failure modes.
- Do not omit time/space/latency/concurrency/security/resource structure when it can change feasibility.
- Do not spawn subagents unless the user explicitly asks for subagents, parallel agents, or team mode.
- In team mode, parallelize read-heavy specialist analysis; use one root-selected writer only after synthesis and adversarial review.
- Child agents must not recursively delegate; the root owns synthesis, write ordering, verification, and closure.

## Internal mechanics and companion skills

Use **this skill** as the only top-level Universal Architecture workflow. Do not hand off to a separate `kan` skill; the former Kan material is now an internal mechanics layer.

Mechanics are used only after `universalist` has identified:

```text
attributed registry signal and repository evidence
ordinary repository-native candidate with law, falsifier, and resource impact
one seam and the architectural axis under pressure
relevant construction cards and their evidence-bound dispositions
seam/worlds, boundary disposition, and boundary kind
known side and unknown location
selected construction or explicit unresolved/obstructed result
proof obligations for any selected advanced construction
law/falsifier and effective presentation boundary
root-owned certificate and decision boundary
```

Then read the relevant internal mechanics reference and, when useful, its matching template.

Mechanics topics include Kan extensions/lifts, Freyd/AFT, Yoneda/Coyoneda, codensity presentations, comonadic spatiality, density comonads, halos, continuous comonadic maps, categorical-data/context compilation, CQL fit, pushout reconciliation, defunctionalization, possibility sheafification, category pivots, and syntax/semantics.


For Track I and team mode, read:

- `references/effective-universal-architecture-thesis.md`
- `references/effective-computational-substrate.md`
- `references/concrete-primitives.md`
- `references/effective-categorical-normal-form.md`
- `references/universal-software-synthesis-playbook.md`
- `references/workflow/subagent-orchestration.md`
- `references/workflow/team-routing.md`
- `references/workflow/subagent-packet-contract.md`

Use the workflow references and certificate templates to produce the explicit orchestration prompt and central artifacts.

- Use **`invariant-ace`** when the main job is discovering or pinning down invariants before choosing structure.
- Use **`accretive-implementer`** after the construction is chosen and the task becomes ordinary implementation.
- Use **`repeatedly-apply-skill`** when sweeping the repo for multiple seams or doing a multi-pass campaign.

## References

Core references:

- `references/universalist-overview.md`
- `references/discovery-signals.md`
- `references/decision-contract.yaml`
- `references/language-encoding-matrix.md`
- `references/framework-boundaries.md`
- `references/cost-model-and-false-positives.md`
- `references/structures-and-laws.md`
- `references/testing-playbook.md`
- `references/migration-playbooks.md`
- `references/case-studies.md`
- `references/sources.md`

Universal architecture references:

- `references/universal-construction-registry.yaml`
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
- `references/comonadic-spatiality-doctrine.md`
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

Effective substrate / workflow references:

- `references/effective-universal-architecture-thesis.md`
- `references/effective-computational-substrate.md`
- `references/concrete-primitives.md`
- `references/effective-categorical-normal-form.md`
- `references/universal-software-synthesis-playbook.md`
- `references/workflow/subagent-orchestration.md`
- `references/workflow/team-routing.md`
- `references/workflow/subagent-packet-contract.md`

Internal mechanics references from former `kan` skill:

- `references/mechanics/README.md`
- `references/mechanics/foundations.md`
- `references/mechanics/kan-lifts.md`
- `references/mechanics/freyd-aft.md`
- `references/mechanics/yoneda-coyoneda.md`
- `references/mechanics/codensity-presentations.md`
- `references/mechanics/comonads-as-spaces.md`
- `references/mechanics/defunctionalization.md`
- `references/mechanics/context-compilation.md`
- `references/mechanics/cql-context-management.md`
- `references/mechanics/possibility-sheafification-mechanics.md`
- `references/mechanics/category-pivot-mechanics.md`
- `references/mechanics/syntax-semantics-mechanics.md`

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
- `templates/effective-universal-architecture-certificate.md`
- `templates/computational-substrate-certificate.md`
- `templates/universal-synthesis-packet.md`
- `templates/syntax-semantics-certificate.md`
