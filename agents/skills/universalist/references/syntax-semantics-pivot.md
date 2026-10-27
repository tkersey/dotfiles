# Syntax / Semantics Pivot

## Core idea

Agentic and software systems often fail because they execute opaque behavior directly. The syntax/semantics pivot separates:

```text
Syntax world    = plans, operations, policies, memory queries, workflow steps, patches, context schemas.
Semantic world  = effects, traces, public behavior, policy outcomes, memory consequences, observations.
Interpreter     = handle / run / compile / lower / render / project.
Law             = accepted syntax denotes valid observed semantics.
```

Syntax gives agents handles. Semantics gives those handles meaning. Laws connect them.
The pivot is bidirectional: materialize structure when it must be observed,
retained, or changed; consider direct interpretation when that materialization
has no required role. Neither direction is a universal preference.

## Use when

- tool calls are raw `name + args` or arbitrary callbacks;
- plans are prose but need validation or replay;
- policies are embedded in prompts or scattered predicates;
- memory/context is raw text rather than typed context;
- workflow behavior is hidden in callbacks or branches;
- patches are produced without semantic intent;
- a syntax exists but no interpreter/law certifies its meaning;
- an already activated representation decision concerns a producer that builds
  temporary data only for a stable fold, with a material cost or proof dividend.

## Repairs

| Smell | Syntax artifact | Semantic artifact | Law |
|---|---|---|---|
| direct tool calls | `ToolOperation` | external effect + trace | allowed op produces allowed trace |
| prose plan | `Plan` IR | execution trace | trace satisfies proof obligations |
| policy in prompt | `PolicyRule` | `PolicyDecision` | evaluation matches allowed observations |
| raw memory chunks | context schema | certified context | rendering preserves observables |
| callbacks | operation/frame IR | interpreter effect | `apply(encoded,x) == oldCallback(x)` |
| patch without intent | `PatchIntent` | behavior/invariant delta | verification matches declared intent |

## Reverse pivot: choose representation by required elimination

Start with the native datatype and its fold. Multiple interpreters alone do not
favor Church encoding: both representations support them. Compare only the live
alternative; this table is a discriminator, not a menu to implement.

| Required capability | Baseline / relevant comparison | Discriminator |
|---|---|---|
| Whole-structure fold or interpretation | native fold; Church-style producer when materialization can disappear | representation laws and a concrete eliminated obligation/allocation |
| One constructor layer or repeated head/tail inspection | native pattern matching; Scott-style elimination | demand, repeated destruction, sharing, and total workload cost |
| Original substructures alongside recursive results | native recursion or paramorphism-style interface | required original structure survives without unjustified rebuilding |
| Inspection, persistence, identity, graph sharing, arbitrary rewrites | explicit datatype, graph, or IR | those capabilities remain available at the boundary that needs them |

These are workload comparisons, not impossibility claims: richer folds can
reconstruct data, and destruction can be encoded, but the cost and observation
contract must still hold. Do not equate Church, Scott, tagless-final, iterators,
or general continuation-passing style merely because all can use functions.

### Worked representation: expression as its fold

For finite immutable trees, in a pure total parametric model, use schematic types:

```text
Expr       = Literal(Int) | Add(Expr, Expr)
Algebra<R> = { literal: Int -> R, add: (R,R) -> R }
CExpr      = forall R. Algebra<R> -> R

encode(e)(a)          = foldExpr(a,e)
onePlusTwo(a)        = a.add(a.literal(1),a.literal(2))
decode(c)            = c({literal: Literal, add: Add})
```

An evaluation algebra yields `3`; a rendering algebra yields `(1+2)`; the
constructor algebra reconstructs `Add(Literal(1),Literal(2))`. The algebra is
chosen by the consumer; the encoded value must be uniform in its result carrier.
This is the typed Church-style / Boehm–Berarducci datatype-as-fold perspective,
not arbitrary untyped functions. See Kiselyov's
[Boehm–Berarducci derivation](https://okmij.org/ftp/tagless-final/course/Boehm-Berarducci.html).

The architectural opportunity is to delay commitment to a materialized tree,
not to mandate a public higher-rank interface. Lower to a native fold, a local
producer accepting an algebra, or a fused loop when that removes a real cost.
Keep ordinary data when it is already the smaller adequate construction.

### Claim boundaries

For an appropriate strictly positive datatype functor `F`, the schematic type
`C_F = forall R. (F R -> R) -> R` suggests an encoded fold. A universal claim also
needs the actual category/model, functor action, carrier, constructors, algebra
maps, and uniqueness argument. Parametricity assumptions supply equations not
provided by the type's reduction rules alone; see Wadler,
[Recursive Types for Free](https://homepages.inf.ed.ac.uk/wadler/papers/free-rectypes/free-rectypes.txt).
An iterator or passing round-trip samples do not by themselves establish
initiality or a dependent induction principle.

Distinguish theorem-backed terms in that model, a host implementation restricted
to justified constructors/operations, and unrestricted host callbacks. The last
may inspect runtime types, cast, throw, diverge, capture mutable state, or consume
resources. Restricting construction helps only when permitted operations and
captured values actually preserve the laws. Do not assert universal guarantees
because the API looks polymorphic. A lawful native implementation can still be
selected with the existing `structure` profile; lack of a universality proof is
not obstruction to ordinary code.

### Reconstruction is not confidentiality or authorization

The constructor algebra in `decode` is an executable falsifier for a proposal
that an unrestricted fold hides the represented information. A hidden concrete
type is not a secret value. Restricting interpreters can be a separate authority
boundary, but changes the admitted observation surface and any representation
claim; declare and justify that restriction. Domain validity, capability checks,
and authorized execution retain their own owners. A Church type alone enforces
none of them.

### Preserve the boundary that needs data

For a reviewed or durable operation plan, retain explicit versioned data at the
inspection, authorization, persistence, replay, and migration boundaries. A
hybrid may specialize its interpretation after those obligations are discharged,
but execution must remain bound to the exact approved plan and context. Do not
reconstruct a different plan from a mutable callback after approval. Never
replace serialization with a closure that cannot be replayed under the required
runtime/version, or assume reification alone preserves graph identity/sharing.

Translate one producer/consumer seam; compare required observations and all
sanctioned construction paths before retiring materialization. Keep any required
wire/storage representation and rollback path. When identity or resources are
observable, value-level round trips alone are insufficient.

### Whole-lifecycle cost

Separate semantic evidence from performance evidence. Inspect the lowered code
for eliminated intermediates, then measure construction plus all consumptions,
reification, repeated destruction, closure/dictionary allocation, stack use, and
lost sharing under the actual compiler/runtime and workload. Include empty,
large, repeated-consumption, and short-circuit/failure cases where admitted.
The finite pure fold law does not cover infinite inputs, lazy demand, cancellation,
or effect reordering automatically. A cheap builder or inlining hope is not a
speedup. See `domain-algebra/property-test-derivation.md` for the laws and falsifiers.

## Syntax/Semantics Certificate

When the receiving workflow needs an explicit certificate, reuse
`templates/syntax-semantics-certificate.md` for either direction. Carry applicable
evidence in the existing nomination when it already owns the same facts; do not
emit a duplicate certificate or a new durable record.

## Soundness / adequacy / preservation

- **Soundness**: every accepted syntax term denotes valid semantic behavior.
- **Adequacy**: required semantic distinctions are representable or observable.
- **Preservation**: syntax transformations preserve declared observations.
- **Falsifier**: accepted syntax with invalid semantics, or needed semantics not expressible in syntax.
