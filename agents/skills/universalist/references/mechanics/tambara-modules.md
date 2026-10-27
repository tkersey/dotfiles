# Tambara Modules and Context-Stable Profunctors

## Scope and terminology

This reference concerns Tambara modules in the sense used by Tambara, Pastro-Street, and profunctor optics:

```text
profunctors equipped with coherent action by an ambient monoidal category
```

It does not concern equivariant Tambara functors or Tambara-Yamagami categories.

Use this reference after Universalist has identified a real context action and a boundary capability that must survive framing.

## 1. Core data

Let:

```text
(M, tensor, I)    ambient context category
C                  source endpoint world
D                  target endpoint world
V                  semantic/enrichment world
```

Let the context category act on the endpoint worlds:

```text
L : M x C -> C
R : M x D -> D
```

Let:

```text
P : C^op x D -> V
```

be a profunctor.

A generalized Tambara module structure is a coherent family:

```text
alpha_m : P(a,b) -> P(L(m,a), R(m,b))
```

natural in `a,b` and coherent in `m`.

Software reading:

```text
P(a,b)       a generalized capability relating a to b
m            a residual/environment/scope/evidence/capability context
alpha_m      lift the capability so it works inside context m
```

## 2. Laws

### Unit

```text
alpha_I ~= id
```

Framing with the empty/identity context changes nothing.

### Associativity

```text
alpha_(m tensor n)
  ~=
alpha_m . alpha_n
```

Nested framing agrees with one combined frame, modulo action associators.

### Naturality in endpoints

Preprocessing the source and postprocessing the target commute with framing.

```text
dimap(f,g, alpha_m(p))
  ==
alpha_m(dimap(f,g,p))
```

up to the declared action/naturality coherence.

### Dinaturality / context reindexing

A coherent map between context presentations must not change the observable framed capability.

### Two-sided compatibility

For separate left and right actions, adding left and right context in either coherent order must agree.

### Interpretation preservation

```text
interpret(alpha_m(p))
  ==
frameSemantics(m, interpret(p))
```

under the declared observations.

### Resource/effect law

Framing does not grant commutativity, duplication, discard, parallelism, or resource reuse unless separately certified.

## 3. Why profunctors?

A function chooses one implementation:

```text
f : a -> b
```

A profunctor describes generalized transformations:

```text
P(a,b)
```

Examples include:

```text
functions
relations
predicates
parsers/printers
continuations
simulations
observations/updates
proof-relevant transformations
```

Profunctoriality changes endpoints. Tambara structure enlarges the common ambient context around those endpoints.

```text
profunctoriality:
  change a and b

Tambara strength:
  place a and b under the same admissible frame
```

## 4. Original two-sided form

For one monoidal category `A` and an endoprofunctor:

```text
T : A^op x A -> V
```

Pastro-Street use left and right actions:

```text
T(x,y) -> T(a tensor x, a tensor y)
T(x,y) -> T(x tensor b, y tensor b)
```

with unit, multiplication, naturality, and left/right compatibility.

When `A` is closed, strong and left-strong Tambara modules correspond to the center and lax center of the Day-convolution category `[A,V]`. When `A` is autonomous/rigid, every Tambara module is strong.

Architectural reading:

```text
Day center:
  a description moves coherently through convolution.

Tambara strength:
  a generalized morphism moves coherently through context action.
```

## 5. Mixed/generalized Tambara modules

Software boundaries often have different endpoint worlds.

Examples:

```text
domain -> wire
read model -> write model
plain value -> validated value
logical schema -> physical storage
pure representation -> effectful reconstruction
```

Use:

```text
L : M x C -> C
R : M x D -> D
P : C^op x D -> V
```

rather than forcing `C = D` or identical actions.

A mixed Tambara claim must name:

```text
common context world M
left/source action L
right/target action R
underlying profunctor P
unit/associativity/naturality laws
one context where the two actions differ materially
```

## 6. Optics as residual-context syntax

A mixed optic from `(a,b)` to `(s,t)` has the coend shape:

```text
Optic((a,b),(s,t))
  = coend_m C(s, L(m,a)) x D(R(m,b), t)
```

A representative consists of:

```text
m
extract/decompose : s -> L(m,a)
rebuild           : R(m,b) -> t
```

The coend quotient identifies coherent changes of residual context presentation.

Given `p : P(a,b)`:

```text
p
  -> alpha_m(p)
  -> dimap(decompose, rebuild, alpha_m(p))
  : P(s,t)
```

This is the operational core of lenses, prisms, traversals, mixed optics, and related accessors.

### Cartesian action / lenses

```text
L(m,a) = m x a
R(m,b) = m x b
```

The residual contains the rest of the product structure.

### Cocartesian action / prisms

```text
L(m,a) = m + a
R(m,b) = m + b
```

The residual contains alternatives that did not match.

### Traversal-like actions

The action records shape plus multiple focused elements. Use the action actually induced by the traversal representation; do not declare an arbitrary container action.

## 7. Profunctor representation theorem

Under the appropriate enriched/mixed assumptions, the residual/coend optic representation is equivalent to a polymorphic transformation over compatible Tambara modules:

```text
forall p. Tambara p => p a b -> p s t
```

Architectural consequence:

```text
existential representation
  exposes residual/context syntax

universal representation
  exposes only what every lawful context-aware interpreter can consume
```

This provides representation independence, but depends on the theorem's categorical and parametricity assumptions.

Do not claim the theorem from a language encoding that permits arbitrary reflection, unsafe casts, or observation of hidden implementation identity without qualification.

## 8. Optic lawfulness is separate

Tambara structure explains interpretation and composition of optics. It does not automatically prove:

```text
Get-Put
Put-Get
Put-Put
partial-match laws
validation invariants
business invariants
provenance preservation
```

Attach domain laws separately.

## 9. Free contextual closure

A free Tambara construction closes a bare profunctor under every admissible context.

Schematic coend:

```text
FreeTambara(Sigma)(f,g)
  = coend_{m,a,b}
      C(f, L(m,a))
      x Sigma(a,b)
      x D(R(m,b), g)
```

Software reading:

```text
bare local operation
  + every legal residual/context
  + decomposition/rebuild paths
  + quotient by coherent reindexing
  -> canonical context-closed capability language
```

Use when repeated wrappers are generated manually around one local operation.

Implementation obligations:

```text
finite/bounded context vocabulary
residual IR
normal form
reindexing quotient
interpreter
context-framing laws
resource bound
```

## 10. Cofree / all-context observation

An end-based construction has schematic form:

```text
Theta(P)(a,b)
  = end_m P(L(m,a), R(m,b))
```

A coalgebra:

```text
P -> Theta(P)
```

is coherent behavior under every context. This is the Pastro-Street-style comonadic view of Tambara structure.

Software reading:

```text
for each local capability,
expose a coherent family of framed capabilities for all supported contexts
```

Use when universal compatibility is the obligation. Do not attempt to enumerate all contexts unless an effective basis, query, or symbolic representation exists.

## 11. The double / optic category

Pastro-Street construct a promonoidal category `D(A)` whose copresheaves are Tambara modules:

```text
[D(A), V] ~= Tamb(A)
```

Its homs have the residual-context optic shape:

```text
D(A)((a,b),(s,t))
  = coend_m A(s, m tensor a) x A(m tensor b, t)
```

Universalist reading:

```text
optic/double category
  explicit residual-context syntax

Tambara module category
  semantic interpretations of that syntax
```

## 12. Day convolution and the monoidal center

The functor category `[A,V]` carries Day convolution. Under suitable closedness:

```text
strong Tambara modules
  ~=
monoidal center of ([A,V], Day)
```

A half-braiding says a description can move coherently through every other description under convolution. Tambara strength says a profunctor can move coherently through every ambient frame.

Use this relationship when:

```text
the base tensor and Day product are already explicit;
centrality changes the semantic artifact;
a Cayley/profunctor representation provides executable leverage;
strongness hypotheses are stated.
```

Do not claim center equivalence for arbitrary nonclosed/nonrigid settings.

## 13. Cayley representation

In a closed monoidal setting, a Cayley-style construction sends a description to a profunctor and converts Day convolution into profunctor composition.

Architectural use:

```text
Day-side presentation
  compose descriptions

Cayley/Tambara presentation
  compose context-stable generalized morphisms
```

This can support alternative implementations, but requires a concrete encoding and equivalence witness.

## 14. Representability diagnostic

Tambara modules are generalized morphisms between module categories. Some are represented by actual context-preserving functors; others are not.

Record:

```text
underlying generalized morphism:
right adjoint / representability witness:
concrete module functor or realizer:
nonrepresentability obstruction:
```

In suitable Cauchy-complete settings, right-adjoint Tambara modules characterize representable module functors.

Software reading:

```text
representable
  a real adapter/implementation map owns the behavior

nonrepresentable
  the architecture supports only a relation/specification/capability family
```

Do not silently generate a function from a lawful relation.

## 15. Dependent Tambara modules

When context changes indices or depends on the focus, use a double-category action and dependent Tambara structure.

Signals:

```text
state-indexed protocol steps
schema-indexed fields
capability-indexed operations
dependent records
context-sensitive syntax
read/write endpoints with changing indices
```

Required fields:

```text
double category of contexts
horizontal/vertical indices
left and right actions
horizontal naturality / dependent framing law
index transport
one nontrivial dependent counterexample
```

Do not erase the index change into `Any`, dynamic tags, or a fake total monoidal action merely to reuse an ordinary Tambara encoding.

## 16. Relationship to Freyd categories and effects

Tambara structure says:

```text
a capability may be framed by context
```

Freyd/premonoidal structure says:

```text
how effectful computations sequence and which operations are central
```

Therefore:

```text
Tambara framing != runtime commutativity
Tambara framing != parallelism
Tambara framing != duplication/discard permission
```

An effectful optic/interpreter may require both:

```text
Tambara laws for residual context
Freyd/resource laws for execution order
```

## 17. Relationship to comonads as spaces

Comonadic spatiality supplies:

```text
points
local patches
halos/germs
situated coalgebras
continuous boundaries
```

A spatial Tambara module can model a generalized transformation that survives a lawful halo/context extension.

Candidate action objects:

```text
dependency neighborhood
ownership region
capability/evidence halo
scope extension
policy environment
```

Required laws:

```text
framing preserves the center
restriction commutes with framing
required labels/provenance survive
context expansion is continuous or explicitly approximate
nested halo framing agrees with combined framing
resource/invalidation budget holds
```

Because halos may be partial, directional, or dependent, promonoidal or double-categorical actions may be more honest than an ordinary symmetric monoidal action.

## 18. Relationship to Exact Context

Separate:

```text
Context Certificate
  proves context m is valid for semantic consumption

Tambara structure
  proves a local capability can be transported through m coherently
```

Example:

```text
validate : P(Input, Result)
frame_m  : P(Input, Result) -> P(Contextual<Input>, Contextual<Result>)
```

Context framing must preserve:

```text
schema
provenance
freshness
authority
missingness/contradiction
required observations
```

Raw prompt concatenation, passing a context parameter, or wrapping values in a record is not enough.

## 19. Relationship to sheafification

Tambara structure and sheafification solve different problems.

```text
Tambara:
  local/generalized transformation remains valid under context action.

Sheafification:
  compatible local meanings glue to a global meaning.
```

A context-stable local operation may still disagree with another local operation on overlaps. Conversely, globally glued meaning may lack a canonical frame operation.

## 20. Software selection patterns

### Repeated wrapper lifting

Smell:

```text
each environment/tenant/evidence/capability wrapper reimplements the same local operation
```

Candidate:

```text
ambient context action + Tambara frame operation
```

### Bidirectional accessor with residual

Smell:

```text
extract focus, remember residual, update focus, rebuild whole
```

Candidate:

```text
optic residual IR + Tambara interpreter
```

### Domain/wire mixed boundary

Smell:

```text
source context acts on domain values differently from target context on wire/storage values
```

Candidate:

```text
mixed Tambara module with separate left/right actions
```

### All-context policy or validation

Smell:

```text
one rule must be valid under every certified environment/context shape
```

Candidate:

```text
cofree/all-context Tambara observation or finite context basis
```

### Generated contextual closure

Smell:

```text
manual generation of every legal wrapper around a local command/observer
```

Candidate:

```text
free Tambara closure
```

## 21. Effective representations

Possible encodings:

```text
interface ContextAction<M,A>
interface Tambara<P> { frame<M,A,B>(m, p): P<L(m,A), R(m,B)> }
sealed ResidualContext
Optic<S,T,A,B>
FramedCapability<M,A,B>
context-indexed map/table
symbolic action dictionary
generated first-order frame IR
```

Implementation strategies:

```text
finite context tags
bounded residual trees
normal-form residual records
dictionary passing / type classes
code generation
memoized context action
queryable context basis
partial action returning an explicit obstruction
```

Resource questions:

```text
How many frames are generated?
How large is the residual?
Can nested framing normalize incrementally?
Can contexts be cached safely?
Which labels/provenance survive?
Does framing duplicate effects or resources?
```

## 22. Certificate checklist

```text
Ambient context world:
Tensor / unit / partiality:
Source action:
Target action:
Underlying profunctor:
Tambara form: ordinary / mixed / two-sided / dependent
Frame operation:
Unit law:
Associativity law:
Naturality/dinaturality law:
Left/right compatibility:
Interpretation law:
Residual/optic representation:
Free/cofree presentation:
Representability status:
Effect-order owner:
Resource bound:
Positive witness:
Falsifier:
```

## 23. Strong falsifiers

Reject the Tambara route when any holds:

```text
no real context category/action exists;
context is merely an unstructured parameter bag;
framing changes local observations;
nested framing depends on grouping;
endpoint reindexing and framing disagree;
the supposed optic observes hidden residual identity;
the action silently duplicates or reorders effects;
a claimed concrete map is only a relation;
free/cofree closure is non-effective without an obstruction;
a plain adapter or explicit residual record already suffices;
the term Tambara actually refers to an equivariant Tambara functor.
```

## 24. First witness strategy

Implement one framed operation only:

```text
one local capability P(a,b)
one context constructor m
one frame_m implementation
one unit witness
one nested-context associativity witness
one endpoint-naturality witness
one interpretation test
one falsifier where an invalid context or effect reordering is rejected
```

Stop after the first verified seam.
