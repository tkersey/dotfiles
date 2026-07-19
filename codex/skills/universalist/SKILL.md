---
name: universalist
description: "Use whenever implementing, reviewing, or resolving code that considers a boundary: creating, changing, preserving, validating, migrating, bypassing, or removing how values, effects, state, evidence, authority, or behavior cross modules, APIs, schemas/DTOs, serializers, storage/wire formats, parsers/validators, handlers, runtimes, protocols, plugins/tools/CLIs, processes, repositories, or public/internal contracts. Trigger even for ordinary feature work or PR/review resolution when boundary behavior is in scope; boundary consideration itself is the signal. Start with one boundary/seam; identify source/target worlds, carriers, operations, observations, laws/non-laws, interpreter/projection/handler, compatibility, falsifier, and resource impact, then choose the smallest honest construction. Keep implicit invocation enabled. Team mode only on explicit request. Use category theory as a hidden optimizer; expose expert names only on request."
---

# Universalist

Use this skill whenever implementation, refactoring, review, migration, or resolution considers a code boundary. A boundary is a seam where values, effects, state, evidence, authority, or observable behavior cross between owners or representations.

Default discipline:

```text
one signal
one seam
one smallest honest construction
one executable law
one falsifier
```

Activation is broad; escalation is narrow. The existing boundary may already be exact. In that case record it as preserved and continue ordinary delivery without inventing new structure.

## Trigger-to-evidence kernel

Record this compact disposition immediately:

```text
Boundary:
Disposition: preserved / introduced / changed / repaired / removed / bypass-justified
Owner:
Source / target:
Preserved / forgotten / generated / observed:
Compatibility:
Law:
Falsifier:
Resource impact:
```

For implementation, name the boundary and owner before mutation. For review or resolution, repair boundary liabilities at the owning seam rather than patching downstream symptoms.

## Universal problem compiler

Category theory is the hidden optimizer, not the default user-facing vocabulary. Every consequential seam uses a two-pass decision:

```text
repository facts
  -> smallest boring repository-native candidate
  -> universal-problem IR
  -> hidden categorical shadow
  -> material-delta gate
  -> selected effective presentation or obstruction
```

Use this protocol:

1. **Ordinary candidate** — first propose the smallest ordinary type, adapter, checked constructor, context parameter, state machine, operation IR, handler, graph, query, merge, or explicit loop that could own the seam.
2. **Comparison universe** — declare admissible alternatives, allowed transformations, required observations, equivalence/normalization, compatibility, authority, effects, and resources.
3. **Architectural hole** — identify whether the unknown is an object, map, extension, realizer, composition, representation, observation surface, local context, or local-to-global glue.
4. **Universal shadow** — search `references/universal-construction-registry.yaml` and its `references/universal-constructions/` theorem cards for a distinguished effective completion or obstruction. Never invent missing preconditions.
5. **Materiality gate** — retain the shadow only when it changes at least one of: owner, representable states, legal composition, information flow, interpreter/projection ownership, public construction paths, proof obligations, resources, existence, or migration strategy.
6. **Lowering** — compile the selected semantics into repository-native code using current language, framework, tests, compatibility, and cost constraints.
7. **Theory erasure** — ordinary output uses plain engineering language. Preserve the construction key in the plan/certificate; show expert categorical names only when explicitly requested.

A categorical name without a material architectural delta is discarded. Record `advanced mechanics: none` and retain the ordinary candidate.

Use `scripts/compile_universal_problem.py` for deterministic theorem-card selection. Read `references/universal-problem-ir.md` for the protocol and use `templates/universal-problem-certificate.md` for consequential decisions.

## Universal witness contract

A local equation or commuting square is not yet a universal architectural claim. A consequential universal claim requires:

```text
existence
commutation / observation preservation
admissible competitors
mediator / factorization
canonicality or uniqueness up to declared equivalence
finite or effective presentation
resource bound
nearest-route falsifier
```

A mathematically existing construction without an effective presentation is an obstruction, not an implementation.

## Domain algebra before architecture

When the local world is unclear, run a compact Domain Algebra Discovery pass:

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

Do not select a boundary artifact until carriers, operations, observations, laws, and non-laws are concrete enough to change code or tests.

## World and boundary inventory

For a non-trivial seam record:

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
Ordinary candidate:
Candidate universal artifact:
Law:
Falsifier:
```

A proposed world is too weak when it has nouns but no transformations, no sanctioned observations, no equality/coherence notion, or no law capable of changing implementation or failure behavior.

## Ordinary construction ladder

Prefer the smallest repository-native artifact first:

| Pressure | Ordinary artifact | First proof signal |
| --- | --- | --- |
| independent fields | record / product | projections recover fields |
| exclusive states | tagged union / coproduct | exhaustive handling; impossible mixtures rejected |
| stable predicate | checked wrapper / refinement | valid accepted; invalid rejected |
| shared observation agreement | owned compatibility object | mismatch rejected; projections preserved |
| explicit source overlap | canonical integration object | overlap agreement; provenance preserved |
| supplied behavior | strategy/function seam | parity with old branch fixtures |
| inspectable behavior | explicit syntax/IR | interpreter agrees with old behavior |
| ongoing behavior | transition system + observer | trace law; invalid transition rejected |
| multiple runtimes | operation syntax + handlers | handlers agree on declared observations |
| ordinary context | explicit parameter/adapter | same certified context reaches consumer |
| same-index descriptions | pointwise combination | same-index interpretation agrees |
| locality only | labelled graph / bounded context | required neighborhood preserved |

Escalate only when the hidden universal shadow produces a concrete artifact, interpreter/projection/handler/lowering, stronger law, and material delta.

## Composition geometry

A seam may carry three independent structural decisions. Do not collapse them into one concept menu.

### Stage 1 — Base composition

Select how values, effects, resources, components, contexts, or patches compose:

- sequential typed composition;
- lawful side-by-side composition;
- ordered pure/effectful composition;
- typed hierarchical substitution;
- many-input/many-output network composition;
- explicit feedback or ongoing interaction;
- resource-sensitive composition.

### Stage 2 — Indexed-description product

When artifacts are descriptions indexed by the base world, separately select:

- same-index pointwise combination;
- all-decomposition combination;
- witnessed partial/relational combination;
- recursive typed substitution;
- value-dependent sequencing.

Read `references/description-composition-doctrine.md` and `references/mechanics/day-convolution.md` only when an index world, tensor/kernel, legal decompositions, quotient/normal form, interpreter, and effectivity bound are concrete.

### Stage 3 — Context action

When one generalized capability must survive context extension, separately select:

- ordinary parameter/adapter;
- shared or mixed context framing;
- explicit residual/optic IR;
- generated all-frame closure;
- all-context observation;
- dependent typed context transport;
- representability or obstruction.

Read `references/contextual-morphism-doctrine.md` and `references/mechanics/tambara-modules.md` only when the ambient context world, endpoint actions, generalized capability, frame operation, coherence laws, effect owner, and effective representation are concrete.

### Runtime semantics

Description composition and context framing never grant effect commutativity, duplication, discard, parallelism, or resource independence. Execution order remains owned by explicit effect/resource/domain laws.

## Exact Context

A system reaches **Context Normal Form** when every semantic consumer receives a task-indexed, schema-shaped, provenance-preserving, freshness-valid, observationally minimal context instance through a certified publication boundary.

Use Exact Context when a semantic consumer—model, human, policy engine, compiler pass, scheduler, controller, planner, dashboard, auditor, test harness, or runtime—depends on evidence quality.

```text
candidate sources
  -> task schema
  -> mappings
  -> deterministic constraint closure
  -> provenance / freshness / missingness / contradiction
  -> observational core
  -> published snapshot
  -> rendering
  -> semantic consumer
```

Rules:

```text
Operational stores own mutation.
Verified context planes own semantic publication.
No semantic consumption without a task-shaped context appropriate to consequence.
No context claim without provenance, freshness, and explicit missingness.
```

Use CQL/categorical data tooling only when schemas, mappings, constraints, integration, provenance, and canonical publication dominate. Do not use it as the default live mutable store.

## Locality and exact abstraction

Use comonadic spatiality only when locality changes correctness, ownership, authority, evidence, or another required observation. Require named points and patches, local/global identity, effective halos, restriction, coherence, continuity, labels/provenance, resource law, and a locality falsifier. Prefer an ordinary labelled graph when it is sufficient.

Use Possibility Sheafification only for architecture-level abstractions whose local usage evidence shows:

- disagreement on overlaps;
- compatible locals with no global representation;
- several global representations with the same observations;
- global states unsupported by local behavior.

Do not call examples a basis without a reconstruction witness, or a wrapper a comonad without the relevant laws.

## Category pivots

Move a hard operation into another representation only when the new world makes inspection, proof, serialization, replay, authorization, minimization, integration, composition, or certification materially easier.

Typical pivots:

```text
opaque callback -> explicit syntax + interpreter
branchy policy -> poset/lattice
mutable protocol -> transitions + traces
raw context -> schema-shaped context instance
global dependency soup -> bounded locality model
indexed loops -> explicit index/decomposition world
repeated wrappers -> explicit context action
local meanings -> usage site + gluing
```

Every pivot requires an encoding, an interpretation back, a preservation law, information-loss statement, effectivity bound, and falsifier.

## Tracks

- **Track A0 — Domain Algebra Discovery:** clarify carriers, operations, observations, laws, and non-laws.
- **Track A — Diagnosis:** analyze one seam without mutation.
- **Track B — One-seam refactor:** implement the smallest reviewable artifact and stop.
- **Track C — Staged migration:** strengthen internals behind stable API, wire, or storage shapes.
- **Track D — Canonical boundary artifact:** select a universal artifact because the ordinary route is insufficient.
- **Track E — Composition certification:** certify one boundary and remove or justify bypasses.
- **Track F — Exact Context:** prepare and publish task-valid semantic context.
- **Track G — Possibility Sheafification:** repair an inexact architecture-level abstraction.
- **Track H — Category Pivot:** move a hard operation into an easier structured world and interpret back.
- **Track I — Effective Universal Software Synthesis:** design a whole capability over an effective substrate with explicit primitives, effects, state, observations, resources, and one witness seam.

## Consequential decision and plan

A route is consequential when it selects or preserves a construction for a changed seam by rejecting a nearby alternative. Ceremonial activation does not allocate a plan or receipt.

For Track B, C, D, F, G, H, or I with mutation, allocate one fresh plan before editing:

```bash
scripts/init_universalist_plan.sh [PROJECT_ROOT]
```

Consequential runs require Ledger `0.10.4` or newer and Skills Seq `0.3.51` or newer. The initializer checks both tools.

Plans live at:

```text
.ledger/universalist/plan-{plan-id}.md
```

Retain the exact plan ID. One changed seam admits one plan and one root decision receipt. Use `references/decision-contract.yaml` and native `ledger emit --source universalist ... --write-plan` before mutating a consequential seam. Workers reference the root decision ID and do not duplicate its receipt.

## Team mode

Spawn bundled subagents only when the current user explicitly requests subagents, parallel agents, team mode, or the categorical-substrate team.

When authorized:

```text
2-6 read-only specialists
  -> root synthesis
  -> proof auditor
  -> one root-selected witness seam
  -> one writer
  -> independent verifier
  -> root integration and stop
```

The root owns scope, comparison of the ordinary candidate and universal shadow, final architecture, mutation order, verification, and user-facing conclusions. Child agents never recursively delegate.

## Operator loop

1. Inspect repository reality: language, framework, ownership, tests, public/wire/storage boundaries, effects, resources.
2. Record the compact boundary disposition.
3. Produce the ordinary candidate.
4. Define the comparison universe and architectural hole.
5. Run the hidden theorem-card shadow.
6. Apply the materiality gate.
7. Allocate the plan and receipt when consequential mutation is in scope.
8. Lower the selected result idiomatically.
9. Verify existence, preservation, mediation/canonicality where claimed, falsifier, compatibility, and resources.
10. Stop after the first verified seam unless the user requested a sweep.

## Output contract

For a non-trivial response use these headings, adapting them to the host workflow rather than duplicating it:

1. **Track**
2. **Signal**
3. **Ordinary candidate**
4. **Universal shadow**
5. **Material architectural delta**
6. **Construction**
7. **Why this instead of nearby alternatives**
8. **Seam / files**
9. **Boundary and compatibility plan**
10. **Before -> After**
11. **Verification**
12. **Runtime-only leftovers**
13. **Next seam** (optional)

Ordinary output uses plain engineering language. When the user requests the mathematical derivation, include the construction key, expert name, comparison universe, competitors, mediator, canonicality, hypotheses, and effective lowering.

## Non-negotiables

- One signal, one seam, one smallest honest construction.
- Category theory must beat the boring architecture; otherwise discard the shadow.
- Do not claim a universal construction without competitors, mediator/factorization, canonicality, and effectivity.
- Prefer ordinary products, sums, refinements, checked agreement objects, adapters, explicit IRs, graphs, and pointwise operations first.
- Preserve wire, storage, and public shapes behind adapters unless a breaking change is requested.
- Do not grant symmetry, commutation, duplication, discard, feedback, parallelism, representability, reconstruction, or complete decomposition without witnesses.
- Do not feed raw retrieved material directly to a consequence-bearing semantic consumer.
- Do not hide external primitives, failure modes, authority, or resource costs behind abstract names.
- Do not introduce a generic categorical library merely to encode a single seam.
- Return obstruction instead of inventing missing evidence, policy, capability, or effective representation.
- Stop after one verified seam unless asked for more.

## Progressive disclosure

Primary references:

- `references/universal-problem-ir.md`
- `references/universal-construction-registry.yaml`
- `references/decision-contract.yaml`
- `references/universal-architecture-ecosystem.md`
- `references/artifact-selection-by-unknown-location.md`
- `references/canonical-boundary-artifacts.md`
- `references/composition-geometry.md`
- `references/presentation-strategies.md`
- `references/exact-context-doctrine.md`
- `references/possibility-sheafification.md`
- `references/category-pivot.md`

Load detailed mechanics only after the ordinary candidate and materiality gate justify them. Use `scripts/emit_mechanics_report.sh <topic> <language>` for expert mechanics and `scripts/check_universal_problem.sh` for the hidden-optimizer contract.
