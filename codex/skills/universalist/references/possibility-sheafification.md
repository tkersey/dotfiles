# Possibility Sheafification

## Core idea

A codebase already contains local evidence about what an abstraction means. The evidence is distributed across call sites, tests, controllers, serializers, database constraints, UI assumptions, adapters, policy checks, event handlers, context compilers, and generated artifacts.

Possibility Sheafification treats that evidence as a site:

```text
patches        = local usage contexts
local sections = local meanings of the abstraction
overlaps       = shared fields, IDs, traces, fixtures, observations, constraints
global section = the intended abstraction
```

An architecture-level abstraction is exact when compatible local meanings glue to one global meaning, and that gluing is unique up to intended equivalence.

```text
compatible local meanings glue uniquely to global meaning
```

## Density, convolution, framing, and sheafification

When the usage site's locality is itself unclear, first use Comonadic Spatiality:

```text
local patch vocabulary P
  -> density comonad <P> = Lan_P P
  -> coherent situated objects / coalgebras
  -> halos and restriction structure
  -> sheafification of compatible local meanings
```

When local or indexed descriptions themselves have a composition law, insert the description-composition layer:

```text
base patch/index composition
  -> Day or promonoidal convolution of descriptions
  -> compatibility checks on overlaps
  -> sheafification / canonical gluing
```

When one local generalized transformation must survive the addition of ambient context, insert the context-action layer:

```text
ambient context action
  -> Tambara framing of the local profunctor/capability
  -> restriction/overlap compatibility checks
  -> sheafification of framed local meanings
```

The roles differ:

```text
Density generates locality.
Convolution composes indexed descriptions.
Day convolution composes locality when patch products are the index tensor.
Tambara framing preserves a local transformation under context action.
Sheafification glues compatible meaning within locality.
```

A collection of call sites, fixtures, or examples is not automatically a basis. A basis claim requires canonical reconstruction of situated objects from basic patches, or a clearly bounded engineering approximation. If the patch family only generates a subbasis, record that and do not claim complete local-to-global reconstruction.

The local point/global point distinction also matters: several representations inside different patches may map to one coarse global identity while retaining distinct scope, provenance, capability, or dependency meaning.

Day convolution does not establish compatibility or global glue. It aggregates over legal decompositions. The resulting sections may still disagree on overlaps, lack a global representative, or admit non-unique/global excess states.

Tambara framing also does not establish compatibility or global glue. It says one generalized transformation survives a context action. Two framed local transformations may still disagree on overlaps, and a globally glued meaning may still lack a canonical frame operation.

## What it manipulates

Possibility Sheafification manipulates abstractions by comparing their **possibility envelope** to their real usage site.

- Too broad: admits impossible global states.
- Too narrow: cannot represent compatible local meanings.
- Redundant: several global states have the same local observations.
- Inconsistent: local sections disagree on overlaps.
- Misplaced: the global meaning is hidden in a callback, serializer, test, or adapter.
- Discontinuous: a refactor preserves global values while destroying the neighborhoods that justify local meaning.
- Miscomposed: indexed local descriptions use pointwise, Day, substitutional, or sequential composition inconsistently.
- Misframed: one local capability is reimplemented under each environment/context, or the frame changes its observations.

## Four sheaf failures

### Local inconsistency

Local meanings disagree on an overlap. Repair with refined states, split abstractions, equalizers, pullbacks, coherent observations, or obstruction reports.

### Missing global glue

Local meanings are compatible but no global artifact represents them. Repair with free syntax, effect signature, lifted implementation, context schema, realizer, or obligation artifact.

### Non-unique gluing

Multiple global representations produce the same local behavior. Repair with quotient, canonicalization, normal form, coequalizer-like artifact, or a single interpreter/projection.

### Hidden excess possibility

The global abstraction admits states that no local behavior can justify. Repair with coproducts, refined types, state machines, behavioral coalgebras, exact context constraints, or defunctionalized IR.

## Workflow

1. Name the abstraction and files.
2. Build the usage site: local contexts that cover the abstraction.
3. If locality is semantic, name points, patches, local/global identity, and an effective halo representation.
4. Decide whether the patch vocabulary is merely a subbasis or supports a basis/canonical reconstruction claim.
5. If indexed descriptions compose, name the index tensor/kernel and select pointwise, Day, promonoidal, substitution, or sequential composition.
6. If one local capability is repeatedly wrapped, name the context world, endpoint actions, underlying profunctor, and candidate Tambara frame.
7. Extract local sections: what each context believes the abstraction means.
8. Identify overlaps: shared keys, observations, traces, fields, tests, invariants.
9. Check compatibility on overlaps.
10. Check existence of global glue.
11. Check uniqueness of global glue.
12. Check whether the proposed refactor is continuous with respect to required halos/labels.
13. Check that convolutional decomposition/quotient choices preserve required local observations and provenance.
14. Check that context framing preserves local observations, restrictions, and endpoint naturality.
15. Classify the sheaf/framing failure.
16. Select the canonical repair.
17. Emit a Sheafification Certificate, with a linked Day or Tambara report when composition/framing is consequential.
18. Add one gluing law and one falsifier.
19. Refactor one witness slice and stop.

## Canonical repairs

| Failure | Architecture smell | Canonical repair |
|---|---|---|
| Local disagreement | semantic drift | split/refine/equalize |
| Compatible locals lack global | missing artifact | free syntax, Kan lift, effect signature, context schema |
| Multiple globals same locals | redundant representation | quotient, canonicalization, normal form |
| Global admits invisible states | overbroad abstraction | refined type, sum type, state machine |
| Local callbacks cannot be compared | hidden behavior | defunctionalized IR |
| Local observations scattered | projection sprawl | Yoneda observation vocabulary |
| Generated locals lack provenance | arbitrary generation | Coyoneda payload + path |
| Public behavior determines internals | outside-in pressure | Kan lift / residual obligations |
| Ongoing behavior over time | trace/protocol pressure | behavioral coalgebra |
| Consumer sees raw source data | uncertified context | Exact Context / Context Certificate |
| Locality changes but boundary preserves only points | locality drift | comonadic spatial presentation + continuous/labelled-halo law |
| Indexed descriptions compose ad hoc | composition drift | explicit index world + Day/promonoidal/pointwise/substitution selector |
| Same local capability is reimplemented under every context | framing drift | ambient action + Tambara module + framing laws |
| Source/target contexts differ | mixed framing drift | mixed Tambara module with separate endpoint actions |
| Residual focus/rebuild logic is scattered | optic drift | residual IR / optic double + Tambara interpreter + domain laws |
| Claimed context-stable relation needs a real map | representability gap | concrete module functor/realizer or obstruction |

## Guardrail

Do not sheafify local helpers or intentionally open extension points. Use Possibility Sheafification when the abstraction is architecture-level and local usage evidence shows an exactness gap.

Do not call every usage map a topology, every dependency list a halo, or every fixture catalog a basis. Use the density-comonadic layer only when its center, neighborhood coherence, restriction, reconstruction, continuity, and resource laws are meaningful.

Do not call every local combination Day convolution. Require a real index tensor/kernel, legal-decomposition policy, quotient coherence, interpretation law, and effective representation. Convolution composes descriptions; it does not by itself prove overlap compatibility or unique global gluing.

Do not call every wrapper, Reader parameter, middleware layer, or residual record a Tambara module. Require a real ambient context action on both endpoint worlds, an underlying profunctor, framing laws, an interpreter, representability status, and an effective witness. Tambara framing preserves a transformation under context action; it does not by itself prove overlap compatibility, global gluing, effect commutativity, or domain optic laws.
