# Architectonic Doctrine

Use this reference when the task asks for rearchitecture, better abstractions, organizing boundaries, canonical ownership, composition laws, or language intended to activate those behaviors.

## Governing operator

## `architectonic`

`ARCHITECTONIC` means:

> Seek the organizing abstractions, boundaries, owners, and composition laws that make the system coherent as a whole.

Architectonic doctrine does not mean “add more architecture.” It asks which structure makes the live obligations fit naturally, exposes only consequential distinctions, and makes invalid states or compositions unrepresentable where the host permits.

An architectonic candidate should improve the system’s conceptual compression:

```text
conceptual compression =
  live obligations and observations explained
  / independent concepts, owners, exceptions, and repair paths required
```

A larger abstraction surface is not architectonic merely because it is systematic. The selected organization must earn its factors, owners, and laws.

## Runtime activation

Canonical high-amplitude form:

```text
OPERATE ARCHITECTONICALLY
```

Normal sentence form:

```text
Operate architectonically.
```

Plain-language alternative:

```text
Find the governing abstraction.
```

Use the exact uppercase fragment when a consuming skill or repository contract requires it. Treat the formal and plain forms as behavioral-upgrade candidates rather than assuming the denser term always performs better.

## Internal decode

```text
live obligations
  -> required observations
  -> current factors and owners
  -> abstraction leaks and accidental distinctions
  -> candidate organizing principle
  -> lawful constructors, eliminators, and compositions
  -> canonical ownership
  -> reconstitution path
  -> preservation or refinement proof
```

## Prompt-ready doctrine

```md
Operate ARCHITECTONICALLY.

Do not assume the current abstractions, files, services, classes, boundaries, or
owners are the right decomposition.

Recover the live obligations and required observations. Then seek the smallest
coherent organization whose:

- factors own distinct obligations;
- truth has canonical owners;
- constructors and eliminators expose the real state space;
- compositions are lawful and explicit;
- accidental distinctions disappear;
- invalid states or compositions are unrepresentable where possible;
- unavoidable validation has one explicit owner;
- implementation follows from the selected structure rather than reconstructing
  forgotten information through validators, caches, correlation, or bypasses.

Prefer conceptual compression over abstraction proliferation.
Name the preservation or refinement relation and the evidence that the new
organization dominates the incumbent.
```

## Architectonic Map

Use only when correctness, handoff, adjudication, or publication requires an inspectable architecture-language artifact:

```md
Architectonic Map:
- live obligations:
- required observations:
- incumbent abstractions and owners:
- abstraction leaks:
- accidental distinctions:
- duplicated or shadow truth:
- candidate organizing principle:
- governing factors:
- constructors / eliminators:
- canonical owners:
- lawful compositions:
- invalid states excluded:
- unavoidable validation owner:
- conceptual compression:
- reconstitution path:
- preservation / refinement relation:
- proof path:
- falsifier:
- disposition: retain | strengthen | split | replace | obstruct
```

The map is explanatory, not an authority artifact. When another workflow already owns an architecture decision record, sharpen that record instead of creating a competing source of truth.

## Adjacent operators

### `principal`

Find the most general solution satisfying the constraints, from which valid special cases arise by instantiation.

- Governs: generality under constraints.
- Cash-out: Principal Solution and Instantiation Map.
- Distinction: a principal solution may be local; `architectonic` organizes the whole relevant system or boundary.

### `factorizing`

Decompose the whole into factors with distinct obligations and an explicit recomposition rule.

- Governs: decomposition and recomposition.
- Cash-out: Factorization Map.
- Distinction: factorization exposes candidate parts; it does not decide which organization should govern.

### `representation-shifting`

Change the representation so invariants, operations, or ownership become natural rather than reconstructed procedurally.

- Governs: representation change.
- Cash-out: before/after representation map and observation-preservation proof.
- Distinction: narrower than `architectonic`; the owner and composition structure may remain unchanged.

### `canonicalizing`

Select one normal form, truth owner, or primary route and make other surfaces projections or derived views.

- Governs: singular ownership and normal form.
- Cash-out: Canonical Owner Map or normal-form gate.
- Distinction: canonicalization may repair one axis without discovering the governing organization of the whole.

### `reconstitutive`

Rebuild the implementation around a newly selected organization instead of layering the new concept over the old one.

- Governs: structural realization after selection.
- Cash-out: reconstitution path, retired surfaces, and preservation proof.
- Distinction: `architectonic` selects the organization; `reconstitutive` realizes it.

### `morphogenetic`

Generate a genuinely new organizing form rather than selecting only among inherited decompositions.

- Governs: formation of new structure.
- Cash-out when needed: candidate form, formation mechanism, and comparison with inherited forms.
- Distinction: higher-variance and generative; a morphogenetic idea must still survive architectonic and adjudicative selection.

### `universalizing`

Seek an abstraction characterized by a universal property: the canonical object or morphism through which all relevant alternatives uniquely factor.

- Governs: universal characterization.
- Cash-out: objects, morphisms, factorization condition, uniqueness condition, and contextual obstruction.
- Distinction: stronger and narrower than generic reuse or generality. Do not use it when no universal property can be stated.

### `algebraic`

Represent behavior through carriers, operations, observations, and laws.

- Governs: explicit behavioral structure.
- Cash-out: behavior algebra or law catalog.
- Distinction: algebraic structure may be one factor inside an architectonic organization; it is not automatically the whole architecture.

### `modular`

Separate components behind interfaces.

- Governs: substitutability and local reasoning.
- Warning: too broad as a primary doctrine word. Modules can preserve the wrong factors and ownership boundaries.

### `architectural`

Concerns architecture.

- Warning: topical adjective, not a strong operator. Prefer `architectonic` when the instruction must discover or impose governing organization.

## Core distinctions

```text
ARCHITECTONIC          -> discover the governing organization of the whole
PRINCIPAL              -> find the most general solution under constraints
FACTORIZING            -> expose factors and recomposition
REPRESENTATION-SHIFTING -> change the representation
CANONICALIZING         -> choose one owner or normal form
UNIVERSALIZING         -> characterize an abstraction by a universal property
MORPHOGENETIC          -> generate a new organizing form
RECONSTITUTIVE         -> rebuild around the selected form
```

The transformation is:

```text
architecture concern -> ARCHITECTONIC selection -> RECONSTITUTIVE realization
```

## Strong stacks

### General rearchitecture

```text
ARCHITECTONIC -> PRINCIPAL -> FACTORIZING -> RECONSTITUTIVE
```

Discover the governing organization, choose the most general adequate abstraction, expose its factors, and rebuild around it.

### Correct-by-construction architecture

```text
EXCAVATORY -> ARCHITECTONIC -> CANONICALIZING -> RECONSTITUTIVE
```

Descend to the governing layer, select the organization, establish canonical owners, and realize the structure.

### Category-theoretic architecture

```text
ARCHITECTONIC -> UNIVERSALIZING -> CANONICALIZING -> RECONSTITUTIVE
```

Use only when a universal construction is contextually justified. Return an obstruction rather than inventing a universal property.

### Technical-debt rearchitecture

```text
STRATIGRAPHIC -> ARCHITECTONIC -> FACTORIZING -> ABLATIVE -> NORMALIZING
```

Recover the historical layers and their obligations, find the governing factors, remove residue, and recompose the survivors into normal form.

### Generative architecture search

```text
POIETIC -> MORPHOGENETIC -> ARCHITECTONIC -> ADJUDICATIVE
```

Create candidate forms, generate new organizations, test them against the governing obligations, and issue a criteria-backed disposition.

## Selection rules

Use `architectonic` when:

- the current abstractions or ownership boundaries are themselves suspect;
- repeated local fixes reconstruct information the model should retain directly;
- special cases indicate the governing decomposition is wrong;
- several abstractions overlap without distinct obligations;
- valid behavior depends on discipline rather than constructors, types, or one explicit validation owner;
- a rearchitecture decision must compare organization, ownership, composition, and proof together;
- the user asks for the better abstraction rather than another implementation tactic.

Use another operator when:

- only the most general local solution is needed: `principal`;
- the factors are known but need separation: `factorizing`;
- the representation alone is wrong: `representation-shifting`;
- ownership or normal form alone is duplicated: `canonicalizing`;
- the architecture is already selected and must be implemented: `reconstitutive`;
- a genuinely new structural form must be generated: `morphogenetic`;
- a universal property can be stated and justified: `universalizing`;
- hidden higher-order behavior should become explicit data: `reifying`.

Do not use `architectonic` merely because the task touches architecture. A local repair can remain local when the current abstraction still owns the obligation cleanly.

## Stopping rule

Stop architectonic search when one candidate:

- covers every live obligation and required observation;
- gives each semantic truth a canonical owner;
- exposes lawful construction, elimination, and composition;
- eliminates accidental distinctions or justifies every retained distinction;
- excludes invalid states where possible and centralizes unavoidable validation;
- has a credible preservation or refinement proof;
- has a realizable reconstitution path;
- is not dominated by a simpler organization with equal or stronger proof;
- has an explicit falsifier or obstruction.

If the context cannot justify a coherent candidate, return an obstruction rather than naming an aesthetically pleasing abstraction.

## Failure modes

Reject:

- architecture theater: more diagrams, layers, or nouns without better ownership or laws;
- abstraction proliferation: every local concern becomes an independent interface or service;
- file-shaped factorization: current files or classes are assumed to be the real semantic factors;
- universal-property cosplay: `universalizing` without factorization and uniqueness obligations;
- elegance without migration: no credible path from incumbent to selected structure;
- generality without task fit: a more abstract API that weakens the actual contract;
- reconstitution before selection: rewriting the system before the governing organization is adjudicated;
- local-fix denial: forcing rearchitecture when one owner-local correction is sufficient;
- authority drift: `$logophile` wording presented as though it selected the architecture.

## Composition boundaries

`$logophile` owns terminology, distinction, prompt wording, and human-facing articulation. It does not nominate, select, implement, or verify architecture.

When composing with repository workflows:

- `$universalist` may nominate the essential boundary shape and return an obstruction;
- `$reduce` may challenge factors, quotients, ablations, and recomposition;
- `$actuating` owns Construction selection, orchestration, and the next legal action;
- `$glaze` may generate one bounded reframe when the owning workflow requests it;
- `$logophile` sharpens the doctrine and resulting human-facing language only.

When `$actuating` is the consumer, preserve its exact activation:

```text
OPERATE ARCHITECTONICALLY
```

Preserve its existing `Architectonic Escalation` and Construction Contract surfaces. Do not create a competing authority artifact merely because this reference defines an optional `Architectonic Map`.

## Behavioral-upgrade discipline

Formal doctrine and runtime activation are separate:

```text
Formal doctrine:    ARCHITECTONIC
Exact activation:   OPERATE ARCHITECTONICALLY
Plain activation:   Find the governing abstraction.
```

When replacing an established plain phrase, use Behavioral Upgrade mode. Compare familiarity, cadence, decoding cost, task coverage, predicted median, ceiling, variance, and shadow risk. `retain`, `specialize`, or `benchmark` are valid outcomes.

## Output shape

For an architectonic doctrine request, return:

```md
Task Pressure
Recommended Mode
Adjacent Operators
Key Distinctions
Strongest Stack
Runtime Activation
Cash-Out Artifact (only when needed)
Shadow Risks
Use This:
[copy-pasteable doctrine block]
```

Keep the runtime activation terse. Do not append the full unpacking unless the user requests it or the decision boundary requires it.
