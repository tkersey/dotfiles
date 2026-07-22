---
name: universalist
description: "Use whenever implementation, review, migration, or resolution creates, changes, preserves, validates, bypasses, or removes an owned code boundary. Universalist generates context-relative, correct-by-construction architecture: start with the smallest repository-native candidate, capture current requirements and host enforcement capabilities, consult construction cards only as evidence-bound theorem nominations, and synthesize the smallest effective artifact whose representation, constructors, eliminators, compositions, and interpretations enforce the contract. Make invalid states and illegal compositions unrepresentable where possible; centralize unavoidable runtime checks; preserve observations and compatibility; record residual obligations and invalidation triggers; return obstruction rather than invent correctness. Implicit invocation on; team mode only by explicit request."
---

# Universalist

Universalist generates **context-relative, correct-by-construction software architecture**.

It uses category theory as a hidden optimizer to derive the smallest effective boundary artifact whose representation, constructors, eliminators, compositions, and interpretations enforce the current context's requirements. It makes invalid states and illegal compositions unrepresentable where the host environment permits; centralizes unavoidable runtime validation at explicit owners; preserves required observations and compatibility; records residual obligations and invalidation triggers; and returns an obstruction rather than inventing correctness the context cannot justify.

Default discipline:

```text
one owned boundary
one current context
one architectural axis
one typed hole
one smallest effective artifact
one owner for every residual check
one law and one falsifier
```

Category theory must change what the architecture owns, permits, excludes, composes, observes, preserves, identifies, generates, interprets, proves, or refuses to invent. Otherwise it is explanatory metadata.

## Boundary-trigger mandate

Use this skill whenever implementation, refactoring, review, migration, or resolution considers a code boundary. A boundary is considered when work creates, changes, preserves, validates, migrates, bypasses, removes, or repairs how values, effects, state, evidence, authority, or behavior cross owners or representations.

Examples include module and package APIs, public/internal contracts, DTOs and schemas, parsers and validators, storage and wire formats, syntax and interpreters, effect handlers, protocols, plugins, tools, CLIs, processes, repositories, and deployment surfaces.

Activation is broad; escalation is narrow. An already exact boundary may be preserved. A local edit wholly inside one unchanged boundary does not trigger this skill.

## Trigger-to-evidence kernel

Record the compact boundary disposition immediately:

```text
Boundary:
Disposition: preserved / introduced / changed / repaired / removed / bypass-justified
Disposition rationale and evidence:
Owner:
Source / target:
Current requirements:
Required observations and compatibility:
Preserved / forgotten / generated / observed:
Law:
Falsifier:
Residual obligations:
Invalidation triggers:
```

Then:

1. Decide whether the route is consequential under **Decision observability**: at least two plausible routes materially differ in persistent behavior, authority, compatibility, migration, enforcement, invalidation, or proof obligations.
2. For a consequential route, allocate one fresh ledger-addressed Universalist plan through **Step 0**, complete this gate before mutating the seam, and emit exactly one root `SDR-v1`.
3. For a routine or uncontested seam, retain the compact disposition and continue the repository's ordinary workflow. Do not allocate a plan or emit `SDR-v1` solely because the skill activated.

## Current-context contract

Correctness is always relative to an attributed context `Γ`. Before claiming that an artifact is correct by construction, record:

```text
Context identifier or evidence fingerprint:
Requirement sources:
Required observations:
Equivalence / normalization:
Authority and policy:
Compatibility and migration constraints:
Effects and ordering:
Resource constraints:
Host enforcement capabilities:
Freshness / validity horizon:
```

The host capability inventory must say what can actually be enforced by:

```text
type or data representation
module opacity / private constructors
generated code or exhaustive matching
lawful composition API
interpreter / handler ownership
database or schema constraints
runtime validation
monitoring / audit / invalidation
```

Do not claim static enforcement where the language, module system, persistence layer, deployment topology, or external authority cannot provide it.

## Smallest effective artifact

State the **ordinary candidate** first: record, tagged union, checked constructor, adapter, explicit parameter, state machine, operation IR, handler, labelled graph, query, bounded loop, or canonical merge.

Define the comparison universe before calling anything smallest or canonical:

```text
admissible artifacts
admissible transformations
sanctioned observations
equivalence / normalization
compatibility
authority
effects and ordering
resources
host capabilities
```

“Smallest” means minimal in this declared universe relative to the requirements and resource model. It does not mean shortest code or most elementary category-theory name.

A candidate dominates another only with evidence that it preserves the required observations while reducing at least one of:

```text
invalid representable states
illegal public compositions
unchecked construction paths
duplicated authority
runtime proof burden
information loss
migration risk
resource cost
```

If several candidates are incomparable minima, the result is **underdetermined**. Do not manufacture a winner.

## One axis and one typed hole

Analyze one architectural axis and one compatible hole per packet:

```text
axes:
  data shape
  syntax-semantics
  behavior
  base composition
  two-dimensional composition
  description composition
  context action
  locality
  schema-context
  transport-realization
  presentation
  proof

holes:
  object
  map
  interpreter
  composition
  representation
  equivalence
  locality
  context action
  square
  proof
```

Independent pressures become linked packets. Double-category squares, Day convolution, Tambara framing, effect ordering, locality, data shape, and context preparation may coexist; they do not compete as one global winner.

## Double-category architecture

Use the `two_dimensional_composition` card when two semantically different arrow families both compose and correctness depends on typed squares relating them.

```text
horizontal arrows
  processes, open systems, queries, generalized interactions, executable behavior

vertical arrows
  migrations, refinements, strict maps, reindexings, deployments, architecture changes

squares
  compatibility witnesses whose four boundaries are explicit
```

The architectural maxim is:

```text
Processes compose horizontally.
Changes compose vertically.
Squares certify compatibility.
Interchange makes local change compositional.
```

Require:

```text
horizontal identities and composition
vertical identities and composition
square boundary typing
horizontal square pasting
vertical square pasting
interchange or explicit coherent comparison
one interpreter / double-functor lowering
effective normalization, resource, and invalidation policy
```

Select a pseudo double category when composition is coherent only up to a represented isomorphism or normal form. Select an equipment/framed bicategory only when strict maps admit effective companions, conjoints, or restrictions for generalized arrows. Select a virtual double category when generalized cells matter but horizontal composition is partial or intentionally unavailable.

Do not call a commutative-square fixture, a pair of categories, a PROP diagram, or double-pushout rewriting a double category by itself. Interchange never proves effect commutativity; preserve effect, authority, failure, provenance, and resource observations.

When selected, read `references/double-category-architecture.md` and `references/mechanics/double-categories.md`, then lower to the narrowest repository-native horizontal-arrow, vertical-arrow, square, pasting, and interpretation API needed by one witness seam.

## Construction card decision table

For a consequential structural choice, state the **ordinary candidate** first, then consult `references/universal-construction-registry.yaml` and only the card fragments relevant to the evidenced axis, typed hole, and requirements.

The construction cards are theorem nominations. They do not select a route or authorize mutation.

For each relevant card, record exactly one evidence-bound disposition: **selected**, **rejected**, **contradicted**, or **unresolved**.

- **selected** — prerequisites are evidenced, the card closes a real requirement gap, and its lowering is effective;
- **rejected** — it is admissible but a named alternative dominates it in the declared comparison universe;
- **contradicted** — an attributed prerequisite is false or a falsifier is witnessed;
- **unresolved** — required evidence is unknown, alternatives remain incomparable, or effectivity is not established.

The legacy card fields `route` and `diagnostic_order` are non-authoritative compatibility metadata. Never derive the final route from them. Signals are many-to-many pressure labels: one signal may nominate zero, one, or several cards, and a signal never proves a prerequisite.

Do not let signal count, evidence count, citation count, card order, categorical sophistication, or vocabulary manufacture a winner. Missing evidence remains unresolved; it is not an obstruction. Support-only cards may define or guard the comparison universe but never become implementation artifacts.

The registry's `universal.role: emitter` means that a selected artifact maps coherently into admissible consumers or interpretations. It never denotes an executable emitter.

## Boundary Artifact Contract

A selected direction is not yet architecture. Lower it into one repository-native **Boundary Artifact Contract**:

```text
Context identifier / proof lease:
Boundary and owner:
Requirements discharged:
Representation / carrier:
Public constructors:
Public eliminators:
Legal compositions:
Two-dimensional arrows / squares / pasting, if selected:
Interpreter / projection / handler:
Required observations:
Compatibility / migration:
Bypass prevention:
Enforcement allocation:
Residual obligations:
Invalidation triggers:
Resource bound:
Claim strength:
```

### Construction surface

Every public constructor must either make the invariant structurally unavoidable or perform the owner-controlled check before producing the artifact. Raw constructors and unchecked deserializers must not bypass the owner.

For a double-category artifact, square construction must require four matching boundaries. A strongly typed host should make mismatched edges unrepresentable; a weaker host should return one structured mismatch owned by the square constructor.

### Elimination surface

Eliminators must be total over representable cases, expose only sanctioned observations, and preserve information that compatibility or later interpretation requires. If elimination is intentionally partial, represent the partiality in the result type or named failure protocol.

### Composition surface

Legal composition must be explicit and closed over valid artifacts. Illegal composition should be unrepresentable where the host permits; otherwise the owner-controlled combinator rejects it with a typed or structured failure.

When two-dimensional composition is selected, expose separate horizontal and vertical composition plus horizontal and vertical square pasting. Internal shared boundaries may disappear only through an explicit equality, normalization, or compatibility witness. Require interchange up to the declared observations.

### Interpretation surface

One explicit interpreter, projection, serializer, compiler, handler, renderer, or double-functor lowering owns semantic lowering. It must preserve the current context's required observations, effect order, compatibility, resource obligations, and—when applicable—both arrow compositions, squares, pasting, and coherence.

## Enforcement allocation

Every requirement must be discharged exactly once at the strongest honest locus the host permits:

```text
representation / type
opaque constructor
composition API
square constructor / pasting API
interpreter / handler
persistence or schema constraint
runtime boundary validation
monitoring / invalidation
residual obligation
obstruction
```

Prefer structural enforcement, but do not duplicate the same authority across layers. When static enforcement is impossible, centralize the runtime check at the earliest boundary that owns the evidence needed to decide it.

An enforcement matrix is complete only when every current requirement maps to:

```text
owner
enforcement locus
positive witness
failure behavior
residual status
invalidation trigger
```

An orphan requirement is a correctness defect.

## Correct-by-construction laws

A context-relative boundary artifact must satisfy the laws applicable to its seam:

1. **Construction soundness** — every publicly constructible artifact satisfies all requirements allocated to construction.
2. **Representational adequacy** — every admissible state or operation required by the context is representable, residual, or explicitly obstructed.
3. **Elimination totality** — every representable case is handled, and sanctioned observations are preserved.
4. **Composition closure** — lawful composition stays inside the valid state space.
5. **Composition admissibility** — no illegal composition enters through a public path.
6. **Interpretation preservation** — lowering agrees with required semantics and observations.
7. **Enforcement completeness** — every requirement has one owner and one enforcement or residual locus.
8. **Bypass exclusion** — unchecked construction, composition, or interpretation paths are absent or explicitly primitive.
9. **Effectivity** — construction, checking, normalization, interpretation, and invalidation fit the resource model.
10. **Context validity** — the proof lease remains valid under the recorded context and invalidation policy.
11. **Two-dimensional coherence, when selected** — square boundaries match, both pasting operations close, interchange holds up to the declared equivalence, and interpretation preserves the entire square calculus.

## Universal witness contract

A consequential categorical nomination needs more than a local law or commuting square:

```text
Existence:
  the repository-native artifact or bounded approximation can be built.

Preservation:
  required observations, invariants, compatibility, and effects commute.

Mediation:
  every admissible competitor has the required comparison path.

Canonicality:
  the comparison is unique up to declared equivalence or normalization.

Effectivity:
  construction, comparison, validation, interpretation, and invalidation fit the budget.

Falsifier:
  a nearby weaker or illegal construction fails observably.
```

For a double-category claim, mediation additionally means that each admissible compatible change of a horizontal process is represented by a square and compatible local squares paste into a global square. Canonicality additionally requires the two pasting orders to agree by interchange up to the declared equivalence.

Engineering realizations may approximate mediation and uniqueness through opaque constructors, canonical identifiers, normalized IR, one public interpreter, one sanctioned projection, generated code, removal of bypasses, or bounded search. State the claim strength:

```text
literal
effective realization
bounded approximation
```

A bounded approximation must state what is included, excluded, possibly lost, and what evidence would refine it.

## Residual obligations

A residual obligation is a requirement the artifact cannot honestly discharge at construction time. Record:

```text
requirement
reason it remains residual
owner
check time
evidence needed
failure behavior
discharge condition
```

Residual obligations are first-class architecture, not TODO prose. They may become runtime validation, migration work, external authority checks, monitoring, or a later linked packet.

For a double-category artifact, unsupported arrow cases, unavailable square witnesses, partial companions/conjoints, or unbounded pseudo-coherence normalization remain explicit residuals rather than being silently totalized.

## Invalidation triggers and proof leases

A correct-by-construction claim is a **proof lease** over the current context, not an eternal property of source code.

Record the context identifier or evidence fingerprint and every change that requires revalidation, reconstruction, migration, or obstruction review, including changes to:

```text
requirements or policy
sanctioned observations or equivalence
schema / wire / storage version
external API semantics
authority or capability model
dependency or locality graph
effect ordering
host-language or module guarantees
resource budget
freshness horizon
horizontal or vertical arrow semantics
square boundary / pasting / coherence policy
```

When an invalidation trigger fires, the artifact may remain executable but its architectural proof is stale. Re-establish the lease before claiming continued correctness. Prefer incremental invalidation of squares whose boundaries changed over global recomputation.

## Evidence states and obstruction

Keep these states distinct:

```text
evidenced true
evidenced absent
unknown / not inspected
underdetermined
witnessed obstruction
```

Unknown or missing evidence means epistemically blocked. It does not prove nonexistence.

A real obstruction requires attributed counterevidence, a reproducible counterexample, stability under the declared comparison maps, an effectivity account, a falsifier, and a reopening condition. Return obstruction rather than inventing evidence, authority, policy, representability, effect laws, host capability, resource feasibility, square pasting, or interchange.

## Doctrine index

The operational kernel above is authoritative. Load detailed references only when the seam requires them:

- `references/universal-construction-registry.yaml` and `references/universal-constructions/`
- `references/structures-and-laws.md`
- `references/canonical-boundary-artifacts.md`
- `references/boundary-law-catalogue.md`
- `references/composition-geometry.md`
- `references/double-category-architecture.md`
- `references/mechanics/double-categories.md`
- `references/description-composition-doctrine.md`
- `references/effects-and-coalgebras.md`
- `references/comonadic-spatiality-doctrine.md`
- `references/exact-context-doctrine.md`
- `references/possibility-sheafification.md`
- `references/category-pivot.md`
- `references/mechanics/`

Use the theorem name in expert reasoning; emit repository-native architecture by default.

## Step -1 — World, boundary, and context inventory

For a non-trivial seam record:

```text
World:
  objects:
  transformations:
  invariants:
  observations:
  primitives:
  composition:
  equality / coherence:

Boundary:
  kind:
  source:
  target:
  owner:
  preserved:
  forgotten:
  generated:
  observed:

Context:
  requirements:
  authority:
  compatibility:
  effects:
  resources:
  host capabilities:
  validity horizon:

Typed hole:
  axis:
  kind:

Two-dimensional structure, when relevant:
  horizontal arrows and composition:
  vertical arrows and composition:
  square meaning:
  pasting and interchange:
```

Do not escalate when this inventory cannot be grounded in repository evidence.

## Step 0 — Allocate a ledger-addressed plan

For a consequential decision, first load `$ledger` and complete `$ledger ensure` once. Then allocate a fresh plan:

```bash
ledger --source universalist create \
  --repo PROJECT_ROOT \
  --template /path/to/universalist/templates/universalist-plan.md
```

Resolve it with:

```bash
ledger --source universalist path --repo PROJECT_ROOT --id PLAN_ID
ledger --source universalist latest --repo PROJECT_ROOT
```

Before mutation, write the ordinary candidate, comparison universe, axis and typed hole, relevant card dispositions, Boundary Artifact Contract, enforcement matrix, residual obligations, invalidation triggers, proof lease, law, falsifier, and any horizontal/vertical/square/pasting obligations into the plan.

After root adjudication emit exactly one receipt:

```bash
ledger --source universalist emit \
  --plan PLAN_PATH \
  --contract /path/to/universalist/references/decision-contract.yaml \
  --question "Which context-relative boundary artifact owns this seam?" \
  --selected-route UNI-ORDINARY \
  --rejected-route UNI-CANONICAL \
  --expected-outcome "One owner enforces the current requirements." \
  --disposition changed \
  --construction "checked owner-controlled boundary artifact" \
  --law "all public construction and composition paths preserve the required observations" \
  --falsifier "an invalid state or illegal composition crosses the owner boundary" \
  --advanced-mechanics none \
  --evidence-ref "code:path" \
  --write-plan
```

Ledger owns plan identity, addressing, receipt construction, validation, and atomic append. Universalist owns architecture policy. The root agent alone selects the route and authorizes mutation.

## Decision observability

A route is consequential only when at least two plausible routes materially differ in persistent behavior, authority, compatibility, migration, enforcement, invalidation, or proof obligations.

Consequential decisions require:

```text
ordinary candidate
comparison universe
one axis and typed hole
relevant cards and dispositions
Boundary Artifact Contract
material delta
selected and rejected routes
law and falsifier
resource impact
residual obligations
invalidation triggers / proof lease
one root SDR-v1 receipt
```

Routine seams, ceremonial activation, and uncontested implementation details use the compact boundary disposition only.

Routes are assigned after artifact lowering:

- `UNI-PRESERVE` — an already exact boundary remains unchanged.
- `UNI-ORDINARY` — the smallest repository-native artifact closes the seam without a material advanced-construction delta.
- `UNI-CANONICAL` — a theorem-card direction materially strengthens the ordinary candidate and has a complete effective witness.
- `UNI-OBSTRUCT` — no honest representable or effective artifact is currently justified, or a primitive bypass is explicitly contained.

A card's legacy route hint never determines this choice.

## Tracks

- **Track A0 — Domain Algebra Discovery:** carriers, operations, observations, laws, non-laws, and effect boundaries.
- **Track A — Diagnosis:** analyze one seam without mutation.
- **Track B — One-seam refactor:** implement one narrow owner-controlled artifact.
- **Track C — Staged migration:** strengthen internals behind stable wire, API, or storage shapes.
- **Track D — Canonical boundary artifact:** use theorem cards to strengthen one typed hole.
- **Track E — Composition certification:** make legal construction, one-dimensional composition, and—when selected—two-dimensional square/pasting paths explicit.
- **Track F — Exact Context:** prepare certified context before semantic consumption.
- **Track G — Possibility Sheafification:** reconcile local meanings into an exact global abstraction.
- **Track H — Category Pivot:** move one hard operation to a world where it is explicit, then transport it back.
- **Track I — Effective universal substrate:** design a whole capability with concrete primitives, recursion/partiality, effects, state, observations, and resources.

Every track lowers to the same Boundary Artifact Contract where a code boundary is changed.

## Team mode

Do not spawn Universalist subagents unless the user explicitly requests subagents, parallel agents, team mode, or the categorical-substrate team.

When authorized:

1. use the smallest sufficient read-only roster;
2. give each agent one axis and typed hole, including a `square` hole when two-dimensional composition is under review;
3. require evidence, candidate dispositions, residuals, and invalidators;
4. let the root synthesize one Boundary Artifact Contract;
5. have the proof auditor attack it;
6. use one writer for one witness seam;
7. use the verifier independently;
8. emit one root receipt for the consequential seam.

Child agents do not choose routes, authorize mutation, or recursively spawn agents.

## Output contract

Normal output uses repository and domain language:

```text
Introduce one authorization-owned compatibility object.
Expose only checked constructors.
Make tenant mismatch unrepresentable after construction.
Keep the external identity check at the authorization owner.
Preserve both source projections.
Invalidate the proof when tenant policy or identity semantics change.
```

For a double-category result, prefer language such as:

```text
Separate executable process composition from migration composition.
Introduce one typed compatibility-square witness.
Permit only boundary-matched horizontal and vertical pasting.
Verify that local migration witnesses paste into the same global result in either order.
Invalidate affected squares when an interface or process boundary changes.
```

When expert explanation is requested, add the construction name, hypotheses, competitors, mediator, canonicality claim, effective lowering, claim strength, and obstruction boundary.

Stop after the first verified seam unless the user explicitly widens scope.
