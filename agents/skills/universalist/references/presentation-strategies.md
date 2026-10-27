# Presentation Strategies

A canonical boundary artifact is not complete until its presentation strategy is clear.

## Modes

### Algebraic presentation

Use generators, operations, equations, free syntax, effect signatures, and handlers.

Use when:

- behavior is operational or command-like;
- constructors are finite and understandable;
- interpreters/handlers are natural;
- the artifact is an AST, workflow, effect language, or command DSL.

Proof signals:

- interpreter parity;
- handler agreement;
- equations respected;
- missing constructor fails exhaustiveness.

### Codensity / dense-dual presentation

Use a small dense world of probes plus a dual/observational bridge and reconstruction.

Use when:

- behavior is semantic, infinitary, probabilistic, topological, observational, or completion-like;
- generators/equations are awkward or infinitary;
- a small family of probes determines the large behavior;
- a representation theorem or domain assumption supports reconstruction.

Proof signals:

- probe coverage;
- probe coherence;
- reconstruction agrees with direct semantics on witnesses;
- missing probe or failed representation theorem gives falsifier.

### Density-comonadic spatial presentation

Use a small vocabulary of local patches:

```text
P : B -> Set
```

whose density comonad:

```text
<P> = Lan_P P
```

presents the world's locality. Coalgebras represent coherently situated objects; halos represent effective neighborhoods; continuous maps represent locality-preserving boundaries.

Use when:

- scope, dependency, ownership, evidence, capability, or context neighborhoods are semantic;
- local patches generate the world more naturally than command constructors;
- nested local views require counit/comultiplication coherence;
- local-to-global identity must remain explicit;
- a boundary must preserve neighborhoods and labels, not only points or values;
- a basis/canonical reconstruction claim can be tested.

Proof signals:

- center/counit law;
- nested-neighborhood/coassociativity law;
- restriction/germ preservation;
- basis-density or bounded reconstruction witness;
- continuity/halo-preservation law;
- labelled-halo and local/global provenance preservation;
- finite/effective halo and invalidation budget.

Do not call a fixture set or component catalog a basis merely because it covers examples. Do not call a dependency graph a comonadic space unless the additional laws and representation change architecture.

### Mixed presentation

Use the weakest combination that exposes each pressure honestly. Examples:

```text
Operation syntax       = algebraic presentation.
Semantic competence    = codensity probe presentation.
Local availability     = density-comonadic spatial presentation.
Runtime                 = handlers + behavioral coalgebra.
```

Agentic systems may stress this combination, but they are not the center of the doctrine.

### Primitive presentation

Use when the boundary is intentionally treated as an external primitive effect and contained by handlers/observations.

## Description composition is a separate decision

Presentation answers:

```text
How is one artifact represented?
```

Description composition answers:

```text
How do artifacts indexed by a composed world combine?
```

After selecting a presentation, choose the description product when needed:

```text
same index                         -> pointwise / Hadamard
all tensor decompositions          -> Day convolution
partial/relation-valued composition -> promonoidal convolution
recursive typed insertion          -> substitution / plethysm
value-dependent sequencing         -> endofunctor composition / monad
```

Examples:

```text
Algebraic operation syntax
  + Day/applicative product
  + Freyd runtime.

Density-comonadic spatial presentation
  + Day product of external-product patches
  + continuous projections.

Codensity probe presentation
  + pointwise product when probes share an index.
```

Do not add `Day` as a presentation mode. It is a tensor/product on indexed descriptions. A description family may be algebraically, densely, spatially, or primitively presented and still use pointwise, Day, promonoidal, substitutional, or sequential composition.

## Context action is a separate decision

Presentation also does not answer:

```text
How does a generalized transformation remain valid when context is added around its endpoints?
```

After selecting a presentation and any description product, choose the context-action structure when needed:

```text
plain parameter/adapter                 -> ordinary function/profunctor
same action on both endpoints           -> Tambara module
separate source and target actions       -> mixed/generalized Tambara module
residual context made explicit           -> optic/double/residual IR
bare capability closed under all frames  -> free Tambara construction
all-context coherent observation         -> cofree/end-based Tambara construction
index-changing context                   -> dependent Tambara/double-category action
concrete implementation required         -> representability/module-functor diagnostic
```

Examples:

```text
Algebraic validation rule
  + mixed Tambara framing through evidence and wire contexts
  + Freyd runtime for effectful checks.

Density-comonadic spatial presentation
  + Tambara action for halo extension
  + continuity and restriction laws.

Explicit optic residual IR
  + Tambara interpreter
  + separate lens/prism/business laws.
```

Do not add `Tambara` as a presentation mode. It is action structure on a profunctor/generalized morphism. An algebraically, densely, spatially, mixed, or primitively presented capability may be unframed, Tambara-framed, mixed, dependent, free/cofree, or representable.

## Rule

Do not accept a universal artifact merely because a canonical construction exists. Prefer a simple, testable presentation that reduces proof burden and separates generic mechanics from domain-specific assumptions.

For spatial presentations, require an effective subbasis/basis, halo representation, restriction/continuity law, and obstruction report when locality cannot be represented within the resource model.

For Day/promonoidal description composition, require an explicit index tensor/kernel, legal-decomposition and quotient policy, representable/interpretation laws, effect-order guardrail, and effective enumeration/normalization bound.

For Tambara/contextual-morphism structure, require a real ambient context action on both endpoint worlds, an underlying profunctor, unit/associativity/naturality/coherence, an interpretation law, representability status, effect/resource ownership, and an effective residual/context representation. A Reader parameter or wrapper is usually the smaller honest construction.
