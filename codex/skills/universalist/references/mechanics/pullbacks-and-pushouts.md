# Pullbacks and Pushouts

Pullbacks and pushouts are universal constructions for **agreement** and **gluing**.

```text
Pullback: select or construct the most general object whose two views agree.
Pushout:  construct the most general object obtained by gluing two objects along an explicit overlap.
```

Use this mechanics reference only after Universalist has named the worlds, maps, observations, witness slice, and falsifier. A pullback or pushout is justified only when its universal property changes code shape, proof obligations, or ownership.

## 1. Formal shapes

### Pullback

Given:

```text
f : A -> C
g : B -> C
```

a pullback is an object `P` with projections:

```text
pA : P -> A
pB : P -> B
```

such that:

```text
f . pA = g . pB
```

and universal among all such agreement objects: for every `X` with maps `xA : X -> A` and `xB : X -> B` satisfying `f . xA = g . xB`, there is a unique `u : X -> P` with:

```text
pA . u = xA
pB . u = xB
```

Diagram:

```text
        pB
    P ------> B
    |         |
 pA |         | g
    v         v
    A ------> C
        f
```

Software reading:

> `P` is the canonical witness object containing an `A`-side value and a `B`-side value that agree under their shared projection to `C`.

In `Set`:

```text
P = { (a,b) in A x B | f(a) = g(b) }
```

### Pushout

Given:

```text
i : O -> A
j : O -> B
```

a pushout is an object `Q` with injections:

```text
qA : A -> Q
qB : B -> Q
```

such that:

```text
qA . i = qB . j
```

and universal among all compatible gluings: for every `X` with maps `xA : A -> X` and `xB : B -> X` satisfying `xA . i = xB . j`, there is a unique `u : Q -> X` with:

```text
u . qA = xA
u . qB = xB
```

Diagram:

```text
        i
    O ------> A
    |         |
  j |         | qA
    v         v
    B ------> Q
        qB
```

Software reading:

> `Q` is the canonical integrated object obtained by keeping everything from `A` and `B` while identifying exactly the overlap specified by `O`.

In `Set`, construct it as the disjoint union `A + B` quotiented by the least equivalence relation identifying `i(o)` with `j(o)` for every `o in O`.

## 2. The core distinction

```text
Pullback = compatibility by shared observation.
Pushout  = integration by shared presentation.
```

Use a pullback when the unknown is an **input/witness that must satisfy two projections simultaneously**.

Use a pushout when the unknown is an **integrated output formed by gluing two sources along a declared interface or overlap**.

A useful mnemonic:

```text
Pull back requirements from a common target.
Push out sources through a common overlap.
```

## 3. Decision table

| Pressure | Construction | Software artifact | First law |
| --- | --- | --- | --- |
| Two values must agree on a shared key/view | Pullback | validated pair, dependent join, witness object | shared projections are equal |
| Two APIs/configurations must be jointly satisfiable | Pullback | compatibility context | any compatible candidate factors through it |
| Two source worlds must be integrated along known overlap | Pushout | canonical merged schema/model/context | injections agree on overlap |
| Two modules/extensions share a core contract | Pushout | combined extension | every compatible consumer factors through combined artifact |
| Two independent values need no agreement | Product | record/pair | projections only |
| Two alternatives remain disjoint | Coproduct | sum/variant | case analysis only |
| Two maps from one object must be equalized | Equalizer | refined subset | selected values make maps equal |
| Two representations must be identified | Coequalizer | quotient/normal form | parallel representations become equal |

## 4. Proven software uses of pullbacks

### 4.1 Relational joins and dependent records

A pullback in `Set` is an equijoin:

```text
Orders.customer_id -> CustomerId <- Customers.id
```

The pullback contains exactly `(order, customer)` pairs whose keys agree.

Use this reading for:

- typed joins;
- foreign-key witnesses;
- attaching evidence to the exact claim/source it belongs to;
- pairing an API request with the authenticated principal for the same tenant;
- combining configuration and runtime state that refer to the same deployment.

The law is stronger than “both values exist”: they must agree through the specified maps.

### 4.2 API and authorization contexts

Suppose:

```text
requestTenant : Request -> TenantId
principalTenant : Principal -> TenantId
```

The pullback is the type of authorized request contexts whose request and principal name the same tenant.

```text
AuthorizedContext = Request x_TenantId Principal
```

This makes tenant agreement a constructor invariant rather than a repeated runtime branch.

Falsifier: a request/principal pair with differing tenant IDs can be constructed or reaches the handler.

### 4.3 Refinements and dependent compatibility

Use a pullback when a new value must retain evidence that two representations describe the same semantic object:

```text
ParsedConfig -> ConfigIdentity <- DeployedConfig
```

The pullback carries both representations plus their agreement witness.

This is useful for:

- validated boundary decoders;
- wire/domain parity objects;
- synchronized model/view pairs;
- migration witnesses;
- version compatibility contexts.

### 4.4 Synchronous products of state machines

Given stateful systems that expose a shared synchronization label, a pullback-like construction selects pairs of transitions that agree on the shared event. Use cautiously: concurrency, time, fairness, and partiality may require richer categories than plain `Set`.

### 4.5 Exact Context relevance

A pullback expresses **joint relevance**:

```text
Evidence -> Claim <- ClaimsRequiredByTask
```

The pullback selects evidence that actually supports or contradicts a required claim, not merely data that is textually similar to a task.

## 5. Proven software uses of pushouts

### 5.1 Schema and data integration

Pushouts are a standard model for integrating schemas or instances with explicit overlap:

```text
SchemaA <- SharedSchema -> SchemaB
```

The overlap says which entities, attributes, paths, or equations truly correspond. The pushout produces an integrated target schema.

Use for:

- database integration;
- enterprise canonical models;
- CQL/functorial data migration;
- versioned schema evolution;
- context reconciliation;
- ontology or model integration.

The pushout does not discover overlap. Entity resolution, vocabulary alignment, and identity policy remain domain work.

### 5.2 API and module composition

Two modules may extend a shared core interface:

```text
PaymentsCore -> CardPayments
PaymentsCore -> BankTransfers
```

A pushout-shaped artifact combines the extensions while identifying the common core exactly once.

Use only when:

- the overlap contract is explicit;
- extension names and behaviors are compatible;
- conflicting definitions are rejected or resolved by named policy;
- downstream interpreters factor through the combined module.

Falsifier: the combined API contains two incompatible meanings for the same core operation, or identifies operations that only share a name.

### 5.3 Syntax and language extension

Pushouts can combine language fragments or signatures that share a base syntax. This is useful for modular DSLs, effect signatures, type systems, and compiler IR extensions.

The practical artifact is usually:

```text
BaseSyntax -> ExtensionA
BaseSyntax -> ExtensionB
CombinedSyntax
```

The universal law says any interpreter that consistently interprets both extensions and agrees on the base factors through `CombinedSyntax`.

### 5.4 Graph and model rewriting

Pushouts are foundational in algebraic graph transformation.

For a double-pushout rewrite rule:

```text
L <- K -> R
```

and a match `L -> G`:

1. compute a pushout complement to remove `L - K` from host graph `G`, producing context `D`;
2. compute a pushout of `K -> R` and `K -> D` to add `R - K`, producing rewritten graph `H`.

```text
L <- K -> R
|    |    |
v    v    v
G <- D -> H
```

Use DPO reasoning for:

- model-driven engineering;
- AST/IR graph rewrites;
- architecture graph evolution;
- refactoring dependency graphs;
- visual language tooling;
- rule-based transformations where deletion and preservation must be explicit.

A pushout complement may fail. Typical obstructions include dangling edges, forbidden identifications, or deletion of shared structure. That failure should become an obstruction report, not a guessed rewrite.

### 5.5 Adhesive categories

Adhesive categories provide well-behaved pushouts along monomorphisms and Van Kampen properties, making graph-like rewriting stable under pullback and composition.

Software guidance:

- if local graph/model rewrites must compose predictably, ask whether the modeling category is adhesive or has an adhesive-like fragment;
- prefer monic interface embeddings for preserved structure;
- treat failure of a pushout complement as a first-class invalid rewrite;
- do not assume arbitrary object categories have graph-like pushout behavior.

Common categories of typed graphs, many presheaf categories, and related model categories support adhesive rewriting patterns.

### 5.6 Multi-source context reconciliation

The existing Universalist Pushout Reconciliation pattern is one application:

```text
ContextA <- OverlapContext -> ContextB
```

The integrated context should preserve non-overlap facts, retain provenance from both sources, and expose conflict instead of silently collapsing it.

## 6. Effective implementation patterns

### Pullback in application code

Represent the universal object with an opaque constructor:

```text
class CompatiblePair<A,B> {
  private constructor(a, b)
  static create(a, b, projectA, projectB): Result<CompatiblePair<A,B>>
}
```

The constructor checks:

```text
projectA(a) == projectB(b)
```

Tests:

- matching projections construct successfully;
- mismatches fail;
- both projections are preserved;
- every alternate compatible representation normalizes through the same constructor/API.

### Pushout in application code

For finite sets/graphs/schemas:

1. tag all elements from `A` and `B`;
2. introduce identifications generated by `O`;
3. compute the quotient with union-find, canonical IDs, or a congruence closure;
4. preserve provenance from each equivalence class to original sources;
5. reject or report conflicts where the target category requires more than identification.

Tests:

- both source injections preserve source data;
- overlap images have one canonical representative;
- unrelated elements remain distinct;
- compatible downstream consumers factor through the canonical integrated artifact;
- different merge order does not change the canonical result, when the selected category/policy promises this.

## 7. Universal-property laws as software tests

### Pullback certificate

```text
Agreement:
  f(pA(p)) == g(pB(p))

Projection preservation:
  pA(makeCompatible(a,b)) == a
  pB(makeCompatible(a,b)) == b

Factorization:
  every alternate X carrying compatible A/B views maps through P

Uniqueness:
  two mediators preserving both projections are observationally equal
```

### Pushout certificate

```text
Overlap agreement:
  qA(i(o)) == qB(j(o))

Source preservation:
  qA and qB retain all non-identified source structure

Factorization:
  every compatible pair A -> X and B -> X induces Q -> X

Uniqueness:
  two induced maps agreeing on both injections are observationally equal
```

In ordinary languages, uniqueness is usually approximated through canonical constructors, normalization, property tests, and the absence of alternate public construction paths.

## 8. Pullback versus pushout selection

Ask these questions in order:

```text
1. Is the unknown a witness/input satisfying two views of one target?
   -> Pullback.

2. Is the unknown an integrated output gluing two sources along one overlap?
   -> Pushout.

3. Is there no shared target/overlap?
   -> Product or coproduct instead.

4. Are two maps from one source being forced equal?
   -> Equalizer.

5. Are two maps into one target generating identifications?
   -> Coequalizer.

6. Is the structure a graph rewrite with deletion/preservation/addition?
   -> Pushout complement + double pushout; check adhesive conditions.
```

## 9. Common misconceptions and falsifiers

### “Pushout means merge”

False. A pushout is a merge **along specified maps from an overlap**. No overlap map, no justified pushout.

### “Pullback means fetch both things”

False. A pullback enforces equality of shared projections. A product merely pairs values.

### “The universal property resolves business conflict”

False. It gives the least/general object satisfying declared identifications or agreements. It does not choose which identifiers, attributes, policies, or concepts should be identified.

### “Git merge is a pushout”

Only as an analogy unless a precise category, overlap/base object, morphisms, and universal property are modeled. Textual conflict resolution and history semantics usually require additional structure.

### “Pushouts always exist and behave like set union”

False. Existence and behavior depend on the category. Even when they exist, quotienting can collapse more structure than intended.

### “Pullbacks and pushouts preserve every operational property”

False. Latency, security, ordering, resource ownership, transactionality, and effect semantics require separate witnesses or richer categories.

## 10. Composition Certificate fields

When pullback/pushout mechanics are selected, add:

```text
Construction:
  pullback / pushout / DPO rewrite

Category/world:
  Set / types / schemas / graphs / presheaves / other

Span or cospan:
  maps and their meanings

Agreement/overlap:
  equality or identity policy

Universal mediator:
  constructor, adapter, integrated schema, normalizer, interpreter

Effective construction:
  validation / join / quotient / union-find / graph rewrite

Law:
  commutative square + factorization + uniqueness approximation

Falsifier:
  mismatch admitted / false identification / silent conflict / lost provenance /
  non-unique public construction / failed pushout complement
```

## 11. Sources and further reading

- Saunders Mac Lane, *Categories for the Working Mathematician* — limits, colimits, pullbacks, pushouts.
- Stephen Lack and Paweł Sobociński, *Adhesive Categories* — categorical foundations for compositional graph transformation.
- Hartmut Ehrig et al., *Fundamentals of Algebraic Graph Transformation* — double-pushout rewriting and applications.
- David Spivak, *Functorial Data Migration* and related categorical database work.
- Patrick Schultz and Ryan Wisnesky, *Algebraic Data Integration* — CQL, schema/instance colimits, pushout integration.
- Brendan Fong and David Spivak, *An Invitation to Applied Category Theory* — compositional systems and universal constructions.
