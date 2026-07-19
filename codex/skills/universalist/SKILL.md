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
  proof
```

Independent pressures become linked packets. Day convolution, Tambara framing, effect ordering, locality, data shape, and context preparation may coexist; they do not compete as one global winner.

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

A selected direction is not yet architecture. Lower it into one repository-native **Boundary Artifact Contract**. Complete every applicable field. When the artifact kind has no honest constructor, eliminator, composition, or interpreter surface, record `not applicable` with an artifact-specific rationale instead of inventing ceremonial structure:

```text
Context identifier / proof lease:
Boundary and owner:
Requirements discharged:
Representation / carrier:
Public constructors:
Public eliminators:
Legal compositions:
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

### Elimination surface

Eliminators must be total over representable cases, expose only sanctioned observations, and preserve information that compatibility or later interpretation requires. If elimination is intentionally partial, represent the partiality in the result type or named failure protocol.

### Composition surface

Legal composition must be explicit and closed over valid artifacts. Illegal composition should be unrepresentable where the host permits; otherwise the owner-controlled combinator rejects it with a typed or structured failure.

### Interpretation surface

One explicit interpreter, projection, serializer, compiler, handler, or renderer owns semantic lowering. It must preserve the current context's required observations, effect order, compatibility, and resource obligations.

## Enforcement allocation

Every requirement must have exactly one semantic owner and one primary disposition at the strongest honest locus the host permits: enforced, retained as a residual, or proved obstructed.

```text
representation / type
opaque constructor
composition API
interpreter / handler
persistence or schema constraint
runtime boundary validation
monitoring / invalidation
residual obligation
obstruction
```

Prefer structural enforcement. Additional guards are allowed when they are explicitly derived from the same semantic authority, preserve the same acceptance rule, have named failure behavior, and carry a conformance or drift witness. They provide defense in depth; they do not become competing owners. When static enforcement is impossible, centralize the primary runtime decision at the earliest boundary that owns the evidence needed to decide it.

An enforcement matrix is complete only when every current requirement maps to:

```text
semantic owner / authority
primary enforcement locus
derived guard loci, if any
positive witness
failure behavior
conformance / drift witness
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
7. **Enforcement completeness** — every requirement has one semantic owner and one primary disposition—enforced, residual, or obstructed; any derived guards trace to that authority and preserve its rule.
8. **Bypass exclusion** — unchecked construction, composition, or interpretation paths are absent or explicitly primitive.
9. **Effectivity** — construction, checking, normalization, interpretation, and invalidation fit the resource model.
10. **Context validity** — the proof lease remains valid under the recorded context and invalidation policy.

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
```

When an invalidation trigger fires, the artifact may remain executable but its architectural proof is stale. Re-establish the lease before claiming continued correctness.

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

A real obstruction requires attributed counterevidence, a reproducible counterexample, stability under the declared comparison maps, an effectivity account, a falsifier, and a reopening condition. Return obstruction rather than inventing evidence, authority, policy, representability, effect laws, host capability, or resource feasibility.

## Doctrine index

The operational kernel above is authoritative. Load detailed references only when the seam requires them:

- `references/universal-construction-registry.yaml` and `references/universal-constructions/`
- `references/structures-and-laws.md`
- `references/canonical-boundary-artifacts.md`
- `references/boundary-law-catalogue.md`
- `references/composition-geometry.md`
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

Before mutation, write the current-context contract, ordinary candidate, comparison universe, axis and typed hole, relevant card dispositions, Boundary Artifact Contract with explicit applicability rationales, enforcement matrix, residual obligations, invalidation triggers, proof lease, law, and falsifier into the plan.

After root adjudication emit exactly one receipt:

```bash
ledger --source universalist emit \
  --plan PLAN_PATH \
  --contract /path/to/universalist/references/decision-contract.yaml \
  --clause-ref UNI-DISPOSITION-001 \
  --clause-ref UNI-MINIMAL-001 \
  --clause-ref UNI-CONTEXT-001 \
  --clause-ref UNI-ARTIFACT-001 \
  --clause-ref UNI-ENFORCEMENT-001 \
  --clause-ref UNI-MECHANICS-001 \
  --clause-ref UNI-ROOT-001 \
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

Pass every applicable clause explicitly so receipt coverage does not depend on Ledger's compatibility defaults. `UNI-PRESERVE`, `UNI-ORDINARY`, and `UNI-CANONICAL` use the seven clauses above. `UNI-OBSTRUCT` replaces `UNI-ARTIFACT-001` with `UNI-OBSTRUCTION-001`.

Ledger owns plan identity, addressing, receipt construction, validation, and atomic append. Universalist owns architecture policy. `references/decision-contract.yaml` is the machine-readable authority for consequential triggers, routes, clauses, and required decision evidence; this file supplies their operational semantics. Change the skill, contract, and plan template together when that policy changes. Seq validates contract structure and fingerprinting, not prose-to-contract semantic equivalence. The root agent alone selects the route and authorizes mutation.

## Decision observability

A route is consequential only when at least two plausible routes materially differ in persistent behavior, authority, compatibility, migration, enforcement, invalidation, or proof obligations.

Consequential decisions require:

```text
current-context contract
ordinary candidate
comparison universe
one axis and typed hole
relevant cards and dispositions
Boundary Artifact Contract with applicability rationales
material delta
selected and rejected routes
law and falsifier
resource impact
enforcement matrix
residual obligations
invalidation triggers / proof lease
one root SDR-v1 receipt
applicable SKDC clause refs
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
- **Track E — Composition certification:** make legal construction and composition paths explicit.
- **Track F — Exact Context:** prepare certified context before semantic consumption.
- **Track G — Possibility Sheafification:** reconcile local meanings into an exact global abstraction.
- **Track H — Category Pivot:** move one hard operation to a world where it is explicit, then transport it back.
- **Track I — Effective universal substrate:** design a whole capability with concrete primitives, recursion/partiality, effects, state, observations, and resources.

Every track lowers to the applicable profile of the same Boundary Artifact Contract where a code boundary is changed; inapplicable surfaces require a concrete rationale rather than placeholder architecture.

## Team mode

Do not spawn Universalist subagents unless the user explicitly requests subagents, parallel agents, team mode, or the categorical-substrate team.

When authorized:

1. use the smallest sufficient read-only roster;
2. give each agent one axis and typed hole;
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

When expert explanation is requested, add the construction name, hypotheses, competitors, mediator, canonicality claim, effective lowering, claim strength, and obstruction boundary.

Stop after the first verified seam unless the user explicitly widens scope.
