# Description-Composition Doctrine

## Thesis

A Universalist world may already have a lawful composition:

```text
(C, tensor, I)
```

Software often manipulates not the objects of that world directly, but descriptions indexed by them:

```text
F, G : C -> V
```

Examples include graded program fragments, resource predicates, static plans, rule collections, weighted behaviors, context fragments, species, and local-space descriptions.

The composition of those descriptions is a second architectural decision. Do not invent it independently of the index world.

Maxim:

```text
Do not invent composition for descriptions.
Derive it from composition of their indices.
```

Compact form:

```text
Indices compose.
Descriptions convolve.
Interpreters execute.
Witnesses certify.
```

## Three distinct layers

Keep these layers separate:

```text
Base composition geometry
  how indices, resources, interfaces, grades, or patches compose.

Description composition
  how families indexed by that world compose.

Execution semantics
  how a description is interpreted, scheduled, handled, or lowered.
```

Examples:

```text
Base geometry      monoidal resource world
Description layer  predicates over resources
Convolution        separating conjunction
Execution          verification / capability checker
```

```text
Base geometry      product of result types
Description layer  static effect descriptions
Convolution        applicative/Day product
Execution          ordered effect runtime governed separately by Freyd laws
```

```text
Base geometry      local-patch product
Description layer  density-comonadic spaces
Convolution        Day product of spatial descriptions
Execution          indexed halo construction and continuous projections
```

Do not infer runtime commutativity, parallelism, or effect independence from a description-level convolution.

## Day convolution

Given a monoidal category `(C, tensor, I)` and a suitable cocomplete monoidal target `V`, the Day convolution of `F,G : C -> V` is:

```text
F star G = Lan_tensor(F external-product G)
```

Pointwise, schematically:

```text
(F star G)(c)
  = coend over a,b of
      C(a tensor b, c) x F(a) x G(b)
```

Software reading:

```text
To build a description at c:
  enumerate every legal decomposition a tensor b -> c;
  choose a description at a and one at b;
  combine their payloads;
  quotient presentations that differ only by coherent reindexing.
```

Day convolution is the canonical colimit-preserving extension of base composition to the functor/presheaf completion. Atomic descriptions should obey:

```text
represent(a) star represent(b) ~= represent(a tensor b)
```

## Promonoidal convolution

Not every software composition is total or represented by one tensor object. When legality is partial, relational, nondeterministic, or witnessed in several ways, use a promonoidal kernel:

```text
Compose(a, b; c)
```

and define convolution by ranging over witnesses in `Compose`.

Use this for:

- disjoint or compatible resource composition;
- partially composable grades;
- interface or rule matches;
- capability combinations with conflicts;
- weighted or nondeterministic assembly;
- composition whose witnesses carry provenance.

Do not totalize an invalid composition merely to obtain a monoidal category.

## Description-product selector

Choose the product at the description layer independently from the base composition geometry.

| Pressure | Description product | First proof obligation |
| --- | --- | --- |
| Combine descriptions at exactly the same index | Pointwise / Hadamard | same-index interpretation agrees |
| Combine over every `a tensor b -> c` | Day convolution | representables preserve base composition |
| Composition is partial or relation-valued | Promonoidal convolution | every emitted composite has an admissibility witness |
| Insert operations recursively into typed slots | Substitution / plethysm | interpretation preserves substitution |
| Later computation structure depends on an earlier result | Endofunctor composition / monadic sequencing | bind/interpreter law |
| Combine independent unindexed values | Product | projections recover inputs |
| Select values agreeing through one observation | Pullback | shared projections agree |
| Integrate sources along declared overlap | Pushout | injections agree on overlap |

A category, Freyd category, operad, PROP, or traced category selects the base geometry. Day convolution is usually a lift of that geometry into a category of descriptions, not a peer replacement for it.

## Selection rule

Use Day or promonoidal convolution only when all are true:

```text
there is a real index category/world;
there is a meaningful tensor or composition kernel;
the software artifacts are indexed descriptions of that world;
composition must account for all legal decompositions;
coherent reindexings should not produce distinct public composites;
an effective representation or explicit approximation exists.
```

Use a smaller construction when a pair, sequence, union, pullback, pushout, simple interface, or direct interpreter is already exact.

## Track A0 extension

Before escalating, Domain Algebra Discovery should record:

```text
Index carriers:
Index morphisms / refinements:
Index composition:
Index unit:
Partiality / admissibility:
Indexed description families:
Current description product:
Required description product:
Observation-relative laws:
Non-laws:
```

New rule:

```text
Algebra before architecture.
Index composition before description composition.
```

## Track D extension

Track D should choose both:

```text
Base composition geometry:
  category / monoidal / Freyd / operad / PROP / traced / resource-sensitive

Description product:
  none / pointwise / Day / promonoidal / substitution / endofunctor composition
```

The chosen product must change an artifact, interpreter, static analysis, law test, ownership boundary, or set of representable programs/states. Otherwise it is decorative.

## Track H extension

A standard Category Pivot is:

```text
Current world:
  maps, registries, callbacks, nested loops, or predicates indexed informally by grades.

Easy world:
  a functor or presheaf category over the explicit index world.

Operation made easy:
  canonical composition of indexed descriptions.

Transfer back:
  interpreter / evaluator / handler / lowering.
```

This is justified when the index algebra is hidden in executable code and becomes explicit in the description world.

## Effects and static structure

Distinguish:

```text
Applicative / Day-convolution structure:
  the shape of the computation is known before intermediate results.

Monad / endofunctor-composition structure:
  later computation shape may depend on an earlier result.

Freyd / premonoidal semantics:
  actual effect execution has observable order and restricted interchange.
```

A static description may enable batching, cost analysis, documentation, dependency extraction, and multiple interpreters. It does not prove that runtime effects commute or may execute in parallel.

## Resources and residuals

For resource-indexed predicates, promonoidal convolution has the shape:

```text
(P star Q)(r)
  iff exists r1,r2.
       Compose(r1,r2;r)
       and P(r1)
       and Q(r2)
```

When the convolution is closed or residuated, a residual asks:

```text
What additional description/resource/obligation G
is sufficient for F star G to satisfy H?
```

This may support residual obligations, capability requirements, context gaps, or planning deficits, but only after the underlying order and residual law are explicit.

## Exact Context extension

Use convolution for context only when requirements form a real compositional index world.

```text
Requirement = r1 tensor r2
ContextFragment : Requirement -> ContextData
```

Then convolution can range over lawful requirement decompositions. Do not call ordinary context concatenation, retrieval union, schema reconciliation, or evidence merging Day convolution without an index tensor/kernel and quotient law.

## Comonadic Spatiality extension

Density, indexed composition, and gluing solve different problems:

```text
Density generates locality.
A specified Day or promonoidal product composes indexed descriptions of locality.
Sheafification glues meaning within locality.
```

For patch vocabularies `P1 : B1 -> Set` and `P2 : B2 -> Set`, the always-defined starting point is the external-product vocabulary on `B1 x B2`:

```text
(U,V) |-> P1(U) x P2(V)
```

Do not call the induced density construction a Day product until both sides are reindexed into one specified monoidal/promonoidal description category. Name its shared/product index world, tensor/unit or kernel, density-Day comparison map, and whether that map is an isomorphism, observational equivalence, or bounded approximation. Also require an effective product of halos, label translation, continuous projections, and a resource bound.

## Possibility Sheafification extension

Day convolution composes local/indexed descriptions. Sheafification tests whether compatible local meanings glue exactly. A system may need:

```text
convolve local descriptions;
check compatibility on overlaps;
glue or normalize the result.
```

Do not conflate convolutional assembly with sheaf gluing.

## Core laws

### Representable / atomic preservation

```text
represent(a) star represent(b) ~= represent(a tensor b)
```

### Unit

```text
UnitDescription star F ~= F
F star UnitDescription ~= F
```

### Associativity

```text
(F star G) star H ~= F star (G star H)
```

### Decomposition soundness

Every emitted composite has a valid tensor/kernel witness.

### Decomposition completeness

Every supported legal decomposition is represented or explicitly excluded by the approximation policy.

### Coend / quotient coherence

Changing an intermediate presentation along an index morphism does not change the normalized public composite.

### Interpretation

```text
interpret(F star G)
  ==
combineSemantics(interpret(F), interpret(G))
```

The equality is relative to declared observations.

### Effect-order guardrail

```text
static composition shape != effect commutativity
```

Reordering or parallelization requires an independent Freyd/resource witness.

### Effectivity

```text
No convolutional artifact without an executable decomposition strategy,
normal form, complexity bound, or obstruction report.
```

## Effective implementation patterns

Use one or more of:

- finite support over grades;
- sparse maps keyed by indices;
- bounded decomposition enumeration;
- dynamic programming or memoization;
- semiring aggregation;
- canonical normal forms;
- union-find or quotient representatives where appropriate;
- symbolic constraints instead of enumeration;
- lazy streams with explicit termination/productivity conditions;
- incremental recomputation and invalidation indexes;
- an obstruction report when the decomposition space is too large or the quotient is unsafe.

Record:

```text
decomposition count / asymptotic bound
normalization cost
memory/index size
cache invalidation rule
collision policy
failure/partiality behavior
```

## Strongest falsifiers

Reject or narrow the construction when:

- no real index category or tensor can be named;
- pointwise product already expresses the intended behavior;
- a legal decomposition is omitted;
- an illegal decomposition is admitted;
- distinct semantic presentations collapse under the quotient;
- the selected convolution erases effect order;
- decomposition is non-effective or operationally explosive;
- applicative/static structure is claimed for a value-dependent workflow;
- an operadic substitution, pullback, pushout, or ordinary product is mislabeled as Day convolution;
- a numerical convolution kernel is being optimized and no architecture-level indexed semantics is involved.

## Doctrine outcome

The Universalist architecture stack becomes:

```text
Domain algebra determines the index world.
Composition geometry determines how indices compose.
Description composition lifts that law to indexed artifacts.
Interpreters give those artifacts executable semantics.
Freyd/resource laws govern effects and cost.
Certificates record laws, approximations, and falsifiers.
```
