---
name: universalist
description: >
  Use when code smells point to a structural refactor that should ship: flag or state matrices, repeated boundary validation, shared-key agreement checks, branchy policy logic, syntax mixed with execution, duplicated projections, generated artifacts losing provenance, callbacks crossing architecture boundaries, protocols or state machines with unclear observations, effect/workflow operations needing multiple handlers, public contracts determining internals, forgetful or observational projections that may need a canonical free builder, or any need for canonical boundary artifacts, Composition Certificates, Boundary Normal Form, presentation strategies, semantic compression, dense probe presentations, or codensity-style presentation diagnostics. Default to one signal, one seam, one smallest honest construction, adapter-first staging, one explicit boundary artifact, one proof signal, and—when the seam crosses worlds—one Composition Certificate.
---

# Universalist

Use this skill when the highest leverage comes from changing the **shape of truth** in a codebase, not from adding another ordinary feature branch.

This is an **inner lens** for choosing the right structural move. It is not a generic implementation skill. Use it to decide and stage the structure, then let the repo's normal implementation flow carry the change.

The enriched slogan is:

> Universal architecture is the practice of designing software around canonical boundary artifacts: **free syntax, coherent observations, transported semantics, lifted implementations, free builders behind projections, obstruction reports, behavioral coalgebras, effect signatures with handlers, explicit IRs, and law tests.**

Core discipline:

> Allow arbitrary domain primitives, but do not allow arbitrary composition across architecture boundaries.

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
- **Mixed presentation** — use algebraic syntax for operations and dense probes for semantic competence, safety, policy, probability, traces, or compatibility. Agentic systems often need this.
- **Primitive presentation** — explicitly contain the boundary as a primitive effect when no useful artifact/presentation is available yet.

New doctrine sentence:

```text
Primitives compute. Boundaries compose. Presentations compress. Witnesses certify.
```

Dense-Dual Presentation principle:

> When a semantic artifact is too large, infinitary, observational, or completion-like to present by generators and equations, try to present it by a small dense world of probes plus a duality or observation bridge into the semantic world.

Reject canonical-but-useless presentations. Prefer small, testable, dense presentations that separate generic boundary machinery from domain-specific representation assumptions.


## Do not trigger for

- Routine feature work with no structural smell.
- Pure performance tuning, infra, UI polish, or docs work.
- Broad rewrites with no stable seam.
- Cases where the domain rules are still too unstable to freeze into a stronger model.
- Category-theory exposition that does not change a concrete seam, construction, boundary, or proof signal.

## Step -1 — World and Boundary Inventory

Before choosing Track A/B/C/D for any non-trivial structural request, inventory the worlds and boundaries. This prevents fake category labels and keeps the response anchored in repo reality.

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

If this inventory cannot be filled for the seam, do not escalate to Track D.

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
- effect drift: operations are interpreted differently by test, production, audit, retry, or simulation handlers.

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
12. **Law tests** — executable witnesses that the boundary artifact does what it claims.

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

## Non-negotiables

- One signal, one seam, one smallest honest construction.
- Prefer products, coproducts, refined types, pullbacks, exponentials, and free constructions before advanced machinery.
- Escalate to universal architecture only when the boundary artifact changes code shape or tests.
- Allow arbitrary domain primitives; require explicit universal artifacts at architecture boundaries.
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
   - effect/workflow operations with multiple implicit handlers.

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

For Track B, Track C, or Track D, also update `.universalist-plan.md`.

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

## Hand-offs and companion skills

- Use **`kan`** only after `universalist` has identified the signal, seam, worlds, boundary kind, candidate artifact, witness slice, and proof signal; then use `kan` for detailed Kan extension/lift, Freyd/AFT, Yoneda/Coyoneda, codensity, or defunctionalization mechanics.
- Do not hand off to `kan` until `universalist` has identified the signal, seam, candidate artifact, witness slice, and proof signal.
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
- `scripts/check_universalist.sh`

## Templates

- `templates/universalist-plan.md`
- `templates/universalist-report.md`
- `templates/universal-architecture-report.md`
- `templates/freyd-boundary-diagnostic.md`
- `templates/composition-certificate.md`
- `templates/boundary-normal-form-report.md`
