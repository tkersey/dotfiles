# Contextual Morphism Doctrine

## Terminology boundary

This doctrine uses **Tambara module** in the Pastro-Street / profunctor-optics sense:

```text
a profunctor equipped with coherent action by an ambient monoidal context
```

It does **not** mean an equivariant Tambara functor, a Tambara-Yamagami category, or a module over a ring.

## Thesis

A software boundary often carries a local transformation, relation, proof, observation, or bidirectional capability that must remain valid after the same admissible context is added around both endpoints.

Do not duplicate that framing logic across wrappers, middleware, scopes, residual records, policies, evidence packets, capabilities, or environments. Model:

```text
context as an action;
local capability as a profunctor;
context-stable capability as a Tambara module.
```

Maxim:

```text
Contexts act.
Morphisms frame.
Tambara laws certify the framing.
```

Companion rule:

```text
Do not thread context ad hoc when context extension is itself algebraic.
```

## The formal shape

Let a monoidal category of admissible contexts be:

```text
(M, tensor, I)
```

Let it act on endpoint worlds:

```text
L : M x C -> C
R : M x D -> D
```

Let the boundary capability be a profunctor:

```text
P : C^op x D -> V
```

A generalized Tambara structure is a coherent family:

```text
frame_m : P(a,b) -> P(L(m,a), R(m,b))
```

Interpretation:

```text
P(a,b)       local/generalized capability between a and b
m            residual, environment, scope, evidence, capability, or other context
frame_m      reuse the capability inside context m
```

The minimum laws are:

```text
unit:
  frame_I ~= id

associativity:
  frame_(m tensor n) ~= frame_m . frame_n

naturality:
  endpoint reindexing commutes with framing

context coherence:
  coherent changes of context presentation do not change observations
```

For two-sided actions, add left/right compatibility. For dependent or index-changing context, use a double-category action and dependent Tambara structure rather than pretending one total monoidal action is sufficient.

## The three-layer distinction

Universalist should distinguish:

```text
Base composition geometry
  how context objects themselves compose.

Description composition
  how indexed descriptions combine: pointwise, Day, promonoidal, substitutional, or monadic.

Context action / contextual morphism
  how a generalized transformation remains valid when context is added around its endpoints.
```

Day convolution and Tambara modules are related but not identical:

```text
Day convolution:
  composes descriptions indexed by a monoidal world.

Tambara module:
  equips a profunctor with coherent transport through that world's action.
```

Under suitable closedness/rigidity hypotheses, strong Tambara modules correspond to central objects in the Day-convolution functor category. Architecturally:

```text
Day centrality      a description moves coherently through composition
Tambara strength    a generalized morphism moves coherently through context
```

## Contextual morphism selector

| Pressure | Structure | Software reading |
| --- | --- | --- |
| same context acts on both endpoint worlds | Tambara module | local capability survives shared framing |
| source and target receive different actions from one context world | generalized / mixed Tambara module | domain/wire, read/write, pure/effect, or other mixed endpoint framing |
| context changes indices or depends on the focused object | dependent Tambara module / double-category action | protocol-, schema-, state-, or capability-indexed framing |
| explicit residual context should be serializable or inspectable | optic / double / residual IR | `exists m. decompose + rebuild` |
| every compatible semantic interpreter should consume the boundary | profunctor optic representation | `forall p. Tambara p => p a b -> p s t` |
| a bare capability must be closed under every admissible frame | free Tambara construction | generated contextual closure |
| a capability must expose coherent behavior under every frame | cofree / end-based Tambara construction | all-context observation |
| generalized morphism is claimed to be an actual implementation map | representability / right-adjoint diagnostic | module functor or concrete realizer exists |

## Optic interpretation

An optic with residual context `m` has the conceptual shape:

```text
decompose : s -> L(m,a)
rebuild   : R(m,b) -> t
```

Given `p : P(a,b)`:

```text
p
  -> frame_m(p)
  -> dimap(decompose, rebuild, frame_m(p))
  : P(s,t)
```

This explains lenses, prisms, traversals, mixed optics, and other residual-context accessors.

Guardrail:

```text
optic representability and composition do not by themselves prove domain optic laws.
```

A lens-shaped value still needs the relevant Get-Put, Put-Get, Put-Put, validation, provenance, or business laws.

## Free and cofree contextual closure

Two useful constructions answer dual architecture questions.

### Free contextual closure

```text
Given a bare profunctorial capability,
generate every legal framed use and quotient coherent reindexings.
```

Use when code repeatedly wraps one operation in every environment/residual/context shape.

### Cofree all-context observation

```text
For each endpoint pair, record coherent behavior under every admissible context.
```

Use when the obligation is universal compatibility rather than syntax generation.

Both constructions require an effective presentation. A coend/end over all contexts is a specification, not automatically an executable algorithm.

## Representability

A Tambara module is a generalized morphism. It need not be the graph of a concrete function or module functor.

Record:

```text
representable:
  yes / no / unknown

realizer:
  concrete module functor, adapter, handler, or implementation map

obstruction:
  missing right adjoint, missing evidence, nonfunctional relation,
  incompatible endpoint actions, or non-effective context family
```

Do not invent an implementation merely because the generalized relation composes lawfully.

## Relation to existing Universalist mechanics

```text
Category / monoidal geometry
  defines the context world and its composition.

Day convolution
  lifts context/index composition to descriptions.

Tambara module
  makes profunctorial capabilities stable under context action.

Freyd category
  governs actual ordered effectful execution.

Comonadic spatiality
  describes the local world/halo surrounding a point.

Sheafification
  glues compatible local meanings.

Exact Context
  certifies that a semantic consumer receives a valid context instance.
```

A useful combined stack is:

```text
Density generates locality.
Day convolution composes descriptions of locality.
Tambara structure frames transformations through locality.
Sheafification glues compatible meaning.
Freyd/resource laws govern execution.
```

## Exact Context interpretation

Suppose:

```text
a              local payload/focus
b              local result
m              certified task/evidence/capability context
P(a,b)         local decision, validation, observation, or update capability
```

Then:

```text
frame_m : P(a,b) -> P(m act a, m act b)
```

means the local capability can run inside a certified context without reimplementing context threading for every consumer.

This is justified only when:

```text
contexts have a lawful unit and composition;
the action on endpoints is explicit;
framing preserves schema, provenance, authority, and observations;
execution order remains owned by the runtime/effect boundary.
```

Raw prompt concatenation, record wrapping, dependency injection, or passing a `Context` parameter is not sufficient evidence.

## Comonadic spatial interpretation

When contexts are halos or local patches, a context action may enlarge or translate the situated environment around both endpoints.

A spatial Tambara claim should state:

```text
context object / halo extension
source and target actions
restriction behavior
label/provenance transport
continuity relationship
framing law
resource/invalidation budget
```

Halos may compose partially, directionally, or dependently. In that case prefer promonoidal or double-categorical actions. Do not force them into a total symmetric tensor.

## Effective implementation forms

Possible code artifacts:

```text
ContextAction<M,A>
FramedCapability<M,A,B>
Tambara<P>
ResidualContext IR
Optic<S,T,A,B>
frame / first / choice / wander-like combinators
freeContextualize
observeAllContexts
representability witness
```

A practical implementation should identify:

```text
finite context vocabulary or bounded generator set
canonical residual/normal form
action interpreter
frame operation
unit and associativity tests
context-reindexing/coherence tests
resource bound
one counterexample
```

## Guardrails

1. A `Context<T>` wrapper is not a Tambara module.
2. Passing the same argument to two functions is not a context action.
3. A profunctor instance without framing laws is not Tambara structure.
4. Tambara strength does not imply effect commutativity, parallelism, duplication, or discard.
5. An optic representation theorem does not establish domain-specific lens/prism laws.
6. A free/cofree coend or end is not automatically finite or efficient.
7. Do not call a relation representable without a concrete realizer/right-adjoint witness.
8. Do not confuse these Tambara modules with equivariant Tambara functors.
9. Prefer a plain adapter, ordinary profunctor, reader/environment parameter, or explicit residual record when it already makes the boundary exact.

## Selection rule

Use Contextual Morphism Doctrine only when all are true:

```text
there is a real ambient context world;
that world acts meaningfully on both endpoint worlds;
the boundary is generalized/profunctorial or optic-like;
the same capability must survive multiple context extensions;
unit and associativity/coherence laws change code or tests;
an effective representation or obstruction can be supplied.
```

Otherwise use a smaller ordinary construction.
