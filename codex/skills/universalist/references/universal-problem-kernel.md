# Universal Problem Kernel

## Purpose

This reference is the internal architecture IR for `$universalist`.

Category theory remains the optimizer. The normal user-facing result is plain repository-native architecture. A categorical name is explanatory metadata unless its universal property changes the owner, representable states, legal composition, information flow, proof, resource model, migration, or existence result.

```text
plain boundary facts
  -> comparison universe
  -> boring candidate
  -> universal problem
  -> theorem-card completion or obstruction
  -> material-delta gate
  -> effective lowering
  -> proof-carrying code
```

## Core claim

A consequential architecture decision should be phrased as a missing universal problem:

> Given the existing partial architecture and a class of admissible competitors, find the distinguished effective completion through which every admissible competitor factors in the required direction, up to the declared observational equivalence—or report why no such completion is determined or implementable.

The word *universal* is always relative to:

- selected worlds;
- admissible transformations;
- sanctioned observations;
- compatibility equations;
- authority and effect policy;
- observational equivalence or normalization;
- resource and deployment bounds.

## Universal Problem IR

```yaml
problem:
  id: ""
  seam: ""
  owner: ""
  disposition: preserved | introduced | changed | repaired | removed | bypass-justified

comparison_universe:
  objects: []
  admissible_transformations: []
  observations: []
  equivalence: ""
  required_equations: []
  information_policy:
    preserved: []
    forgotten: []
    generated: []
    prohibited_loss: []
  authority_policy: []
  effect_policy: []
  resource_budget: []

hole:
  kind: object | map | composition | representation | equivalence | context | locality | proof
  polarity: receive | emit | extend | realize | observe | compose | frame | localize | glue
  known_side: ""
  missing_side: ""

ordinary_candidate:
  artifact: ""
  owner: ""
  law: ""
  falsifier: ""

universal_candidate:
  theorem_card: none
  bytecode: []
  expert_name: ""
  admissible_competitors: ""
  mediator: ""
  canonicality: ""
  status: preserved | ordinary | exact | approximate | underdetermined | obstructed | primitive-exception

proof:
  existence: ""
  commutation: ""
  mediation: ""
  canonicality: ""
  effectivity: ""
  falsifier: ""

lowering:
  repository_artifact: ""
  constructor_interpreter_projection: ""
  compatibility: ""
  migration: ""

materiality:
  changed_dimensions: []
  selected: ordinary | universal | obstruction
  rationale: ""
```

## Comparison universe

### Objects

Objects are candidate representations or architectural states relevant to one seam. Do not model the entire repository when one DTO/domain conversion is enough.

### Admissible transformations

These are the changes or translations allowed to count as contract-preserving. Examples:

- an adapter that preserves public observations;
- a migration that retains stable identifiers and provenance;
- a handler replacement that preserves declared operation observations;
- a normalization that forgets derivation order only when order is unobservable;
- a locality-preserving map that retains the required halo labels;
- an implementation projection that exposes exactly the public behavior.

Architectural policy lives here. Ask:

```text
May provenance be lost?
May effects reorder?
May authority widen?
May values duplicate or be discarded?
May two identities collapse?
May a representation be normalized?
May an approximation omit cases?
```

### Observations and equivalence

State what downstream consumers may distinguish. Structural equality is rarely the right default for migrations, generated IR, traces, context snapshots, normalized composites, or semantic compression.

Use:

```text
x ≈ y iff every sanctioned observation produces equivalent results
```

Name the observation set and any intentional approximation.

### Effects, authority, and resources

A universal construction in an idealized category may be unsuitable in production. Record:

- evaluation order and noncommuting operations;
- duplication, discard, retry, compensation, and failure behavior;
- authority and capability boundaries;
- time, memory, latency, throughput, persistence, invalidation, and deployment bounds;
- finite support, bounded search, laziness, symbolic representation, or approximation policy.

## Boring-candidate rule

Always construct the simplest plausible repository-native architecture before selecting an advanced theorem card.

The boring candidate is not a straw man. Give it:

- the correct owner;
- one construction or interpretation path;
- compatibility behavior;
- a positive law;
- a falsifier;
- the repository's normal types and tests.

The universal shadow must produce a material architectural delta. If it only changes the explanation, retain the boring candidate.

## Universal bytecode

### DECLARE

Define the comparison universe and architectural hole. No theorem card may run before this instruction.

### CONSTRAIN

Construct an artifact whose inhabitants satisfy simultaneous observations or equations.

Typical theorem cards:

- product;
- refinement/equalizer;
- pullback;
- verified context closure.

Generated questions:

```text
Which equations must hold?
Are the projections recoverable?
Can every compatible producer enter?
Is unchecked construction inaccessible?
```

### GLUE

Integrate contributors while identifying exactly the declared overlap.

Typical theorem cards:

- coproduct;
- quotient/coequalizer;
- pushout;
- schema/instance colimit;
- sheaf gluing.

Generated questions:

```text
What overlap is authorized?
What must remain distinct?
How are conflicts represented?
Does provenance survive?
Can every compatible consumer operate through the result?
```

### GENERATE

Create the least structure closed under declared primitives or frames.

Typical theorem cards:

- free syntax;
- free effects;
- free applicative;
- free Tambara/contextual closure;
- density-generated locality.

Generated questions:

```text
Which generators exist?
Which equations identify terms?
Are unsupported programs unrepresentable?
Is every legal generated case effective?
```

### OBSERVE

Characterize an artifact through sanctioned probes, traces, views, or contexts.

Typical theorem cards:

- Yoneda observation vocabulary;
- right Kan/coherent observation;
- final/behavioral coalgebra;
- codensity/dense-dual presentation;
- cofree all-context observation.

Generated questions:

```text
Are all sanctioned observations represented?
Do observations separate values that must remain distinct?
Can the artifact be reconstructed or compared from them?
```

### TRANSPORT

Move semantics along a boundary while preserving required structure.

Typical theorem cards:

- functorial adapter family;
- left or right Kan transport;
- Coyoneda generation path;
- schema migration;
- continuous locality-preserving boundary.

Generated questions:

```text
What is the source-to-target map?
What behavior is extended or restricted?
Which paths must commute?
What is intentionally forgotten or approximated?
```

### REALIZE

Construct an implementation behind a fixed observation or projection boundary.

Typical theorem cards:

- Kan lift;
- free builder behind projection;
- representability/module-functor diagnostic;
- residual obligations.

Generated questions:

```text
What exactly is P : B -> C?
Does P forget information needed for realization?
Is the realizer canonical, approximate, or underdetermined?
Which obligations repair the gap?
```

### COMPOSE

Make the legal geometry of transformations or indexed descriptions explicit.

Typical theorem cards:

- category and monoidal category;
- Freyd/premonoidal structure;
- operads, PROPs, properads, traces;
- pointwise, Day, promonoidal, substitutional, and monadic products;
- resource convolution.

Generated questions:

```text
What is the unit?
What is associative?
What may commute or interchange?
Which decompositions or substitutions are legal?
How are equivalent derivations normalized?
```

### FRAME

Preserve a generalized capability under legal context extension.

Typical theorem cards:

- Tambara module;
- mixed or dependent Tambara structure;
- optic/residual IR;
- free/cofree contextual closure;
- contextual representability.

Generated questions:

```text
What context world acts?
How does it act on source and target?
What is the generalized capability?
Does empty framing act as identity?
Does nested framing equal combined framing?
Is the relation representable by a concrete implementation?
```

### LOCALIZE

Represent objects together with coherent neighborhoods, restrictions, identity, and provenance.

Typical theorem cards:

- comonad as space;
- comonad coalgebra;
- density comonad;
- halo/germ;
- continuous comonadic map;
- spatial description composition.

Generated questions:

```text
What is the center?
How do neighborhoods nest?
How does restriction preserve meaning?
Can patches reconstruct situated objects?
How are local and global identities related?
```

### NORMALIZE

Quotient equivalent presentations while retaining observable distinctions and provenance.

Typical theorem cards:

- coequalizer/quotient;
- coend normal form;
- canonical IDs;
- IR normalization;
- sheafification uniqueness repair.

Generated questions:

```text
What equivalence relation is used?
Is it a congruence for all operations?
What information is forgotten?
Which provenance remains observable?
Is there one effective normal form?
```

### OBSTRUCT

Return a typed reason why no honest exact or effective solution follows.

Obstruction classes:

```text
missing evidence
missing authority or capability
inconsistent equations
underdetermined policy
nonfunctional generalized relation
incompatible context actions
missing basis or reconstruction
unbounded competitor or decomposition family
noneffective normalization
resource or deployment infeasibility
unsupported mathematical hypothesis
```

Obstruction is a successful architecture result when it prevents invented defaults.

## Universal proof dimensions

### Existence

Produce a constructor, interpreter, query, algorithm, finite representation, bounded approximation, or explicit witness.

### Commutation

Show that all required paths and observations agree. Examples:

- adapter round trip;
- projection preservation;
- migration parity;
- handler interpretation;
- restriction and continuity;
- framed interpretation;
- decomposition interpretation.

### Mediation

State how every admissible competitor reaches or is reached from the selected artifact.

Engineering proxies include:

- one opaque constructor;
- one public integration API;
- conversion from every supported legacy representation;
- one interpreter generated from constructors;
- one observer through which public views run;
- one normalizer for equivalent derivations.

### Canonicality

True mathematical uniqueness is often approximated in software. State the approximation:

```text
private constructor
canonical identifier
normalized representation
single owner module
no public bypass
one interpretation path
one migration path
uniqueness up to sanctioned observations
```

### Effectivity

The universal object must have a usable presentation. Record algorithms and budgets for:

- competitor mediation;
- decomposition enumeration;
- quotient normalization;
- context closure;
- basis reconstruction;
- provenance retention;
- cache invalidation;
- deployment and rollback.

### Falsifier

Generate a counterexample targeted at the selected universal obligation, not a generic invalid input.

## Materiality dimensions

The shadow result is consequential only when it changes at least one:

```text
owner
states/programs/morphisms representable
legal composition
information loss or provenance
authority or capability policy
effect order or resource accounting
interpreter/projection/handler ownership
number of public construction paths
proof strength or counterexample
existence/underdetermination/obstruction
migration and compatibility
```

Record the exact delta. `Expert name changed` is never a material delta.

## Status semantics

### preserved

The current boundary already satisfies the required law and has no material universal gap.

### ordinary

The boring candidate is selected; a theorem card either adds no material value or lacks preconditions.

### exact

The theorem card's existence, commutation, mediation, canonicality, effectivity, and falsifier are all witnessed for the seam.

### approximate

The selected artifact intentionally approximates an infinitary, global, or expensive construction. State the loss, bound, and observation-relative adequacy.

### underdetermined

Several observation-equivalent or observation-incomplete solutions exist and no canonical selection policy is supplied.

### obstructed

A required construction cannot exist or cannot be represented effectively under the current information, equations, hypotheses, or budget.

### primitive exception

The seam remains an explicit external primitive behind observations and handlers. Do not decorate it as a universal artifact.

## Plain-language emission

Default user-facing vocabulary:

| Internal concept | Plain emission |
| --- | --- |
| product | record containing independent fields |
| coproduct | explicit exclusive cases |
| equalizer/refinement | validated value with one trusted constructor |
| pullback | owned compatibility witness |
| pushout | canonical integration over explicit overlap |
| free object | generated operation language |
| Kan transport | behavior-preserving extension or migration |
| Kan lift | implementation realizer behind a projection |
| Yoneda | sanctioned observation vocabulary |
| Day convolution | composition over every legal index decomposition |
| Tambara module | context-stable generalized capability |
| density comonad | locality generated from a patch vocabulary |
| sheafification | canonical gluing of compatible local meanings |
| representability failure | no concrete implementation is determined |

Keep the expert name in the plan/certificate and make it available on request.

## Theorem-card protocol

The registry at `references/universal-construction-registry.yaml` is the source of truth for concept selection. Each card must state:

- one concept id and expert name;
- family and bytecode;
- hidden architectural question;
- preconditions;
- competitor class;
- mediator and canonicality;
- plain lowerings;
- positive witnesses;
- falsifiers;
- effectivity hazards;
- boring fallback;
- material-delta dimensions;
- claim boundary and references.

Use `scripts/validate_universal_registry.py` after every registry change.
