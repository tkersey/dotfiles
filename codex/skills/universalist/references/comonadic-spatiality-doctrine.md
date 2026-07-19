# Comonadic Spatiality Doctrine

Use this doctrine only when locality changes correctness, ownership, authority, evidence, provenance, scope, dependency, freshness, or another required observation. Prefer an ordinary labelled graph or context object when it already makes the seam exact.

## Core model

```text
points                 symbols, modules, endpoints, tasks, entities, states
local patches          scopes, dependency regions, evidence/capability contexts
situated objects       values equipped with coherent local context
halos                   effective neighborhoods around points
germs                   values or evidence valid on a sufficiently local patch
continuous boundaries  maps preserving required locality, not only point values
```

Maxims:

```text
Worlds have halos.
Context is a germ.
Boundaries preserve locality.
```

A literal comonadic model requires a context former `C`, center/counit, nested-neighborhood/comultiplication coherence, and situated-object/coalgebra laws. A software approximation must state exactly which of those observations it preserves.

## Density from patches

Given a patch vocabulary:

```text
P : B -> S
```

its density construction is written schematically as:

```text
<P> = Lan_P P
```

Treat a patch collection as:

- **coverage only** when it merely contains examples;
- **subbasis** when it generates candidate locality;
- **basis** only when situated objects reconstruct canonically, or when a bounded approximation and its loss are explicit.

Do not call fixture coverage a basis.

## Required spatial fields

```text
points
patch vocabulary / subbasis
local points and global identities
local-to-global identification and provenance
center/counit law
nested-neighborhood coherence
effective halo representation
restriction and germ rules
labelled relationships
basis/reconstruction or explicit non-basis
continuity law
resource and invalidation bound
locality falsifier
```

Labels may include target, kind, owner, capability, effect, provenance, trust, time, and cost. Preserve only those required by declared observations, but never drop them silently.

## Restriction and germs

A germ is meaningful only relative to a patch. Restriction must preserve local meaning:

```text
restrict identity = identity
restrict through nested patches = composed restriction
```

A context boundary can preserve a fact while invalidating the neighborhood that justified it. Such a boundary is value-preserving but locality-breaking.

## Continuous boundaries

Preserving points is weaker than preserving locality. A locality-sensitive boundary records:

```text
point map
halo-map direction
context/coalgebra transport
labels preserved / translated / forgotten
restriction law
continuity law
continuity falsifier
resource bound
```

An ordinary comonad map is not automatically a continuous locality-preserving map.

## External-product locality

For two patch vocabularies:

```text
P1 : B1 -> Set
P2 : B2 -> Set
```

the always-defined engineering starting point is the external-product patch vocabulary:

```text
P1 external-product P2 : B1 x B2 -> Set
(U,V) |-> P1(U) x P2(V)
```

and the density construction `<P1 external-product P2>`.

Do not write `<P1> star <P2>` until both spatial descriptions are placed in one specified monoidal description category. A literal or effective Day comparison requires:

```text
shared/product index world B
monoidal tensor and unit, or explicit promonoidal kernel, on B
reindexing of both spatial descriptions into [B,V]
Day_B(<P1>, <P2>)
density-Day comparison map Day_B(<P1>, <P2>) -> <P1 external-product P2>
proof that the comparison is an isomorphism, observational equivalence,
or explicitly bounded approximation
```

Without those data, call the result an external-product density construction rather than a Day product.

A spatial-composition certificate records:

```text
left and right subbases/bases
shared/product index world
tensor/unit or promonoidal kernel
external-product patch vocabulary
reindexing into one description category
density-Day comparison map
isomorphism / observational-equivalence / bounded-approximation status
combined point representation
combined halo representation
label product/translation
continuous projections
local/global identity policy
finite/indexed/incremental implementation
collision and resource falsifiers
```

## Context as a germ

Exact Context may use this refinement:

```text
semantic consumer / task = point q
relevant dependencies    = Halo(q)
prepared Context(q)       = certified section or germ over an effective halo
rendering                 = consumer-specific presentation of that germ
```

This changes the question from “which globally retrieved facts should be trimmed?” to “which local patch around the task supports the required observations, and how does validity survive restriction and transport?”

Retrieval output is not automatically a halo. A nearby-files list is not automatically a comonadic neighborhood.

## Context action through locality

When one local generalized capability must survive halo/context extension, a context-action framing layer may be added. Require an actual context action, endpoint actions, generalized capability, frame operation, unit/nested-frame/naturality/interpretation laws, authority/effect ownership, and an effective representation.

Framing does not establish overlap compatibility, global gluing, effect commutativity, duplication, discard, or safe parallelism.

## Relationship to sheafification

```text
Density generates locality.
Description composition combines indexed local descriptions.
Context framing preserves a local transformation under context extension.
Sheafification glues compatible local meaning within locality.
```

These are separate obligations. Day composition does not prove compatibility; framing does not prove gluing; sheafification does not supply an effect order.

## Anti-overreach

Do not use this doctrine when:

- a plain graph or context object already captures the required neighborhood;
- the patch vocabulary has no restriction or coherence law;
- local and global identity are conflated;
- the halo cannot be represented finitely, incrementally, symbolically, or within a stated bound;
- the category-theoretic shadow changes no code, tests, ownership, proof, or resource behavior.

Return an ordinary locality model or obstruction rather than decorative mathematics.
