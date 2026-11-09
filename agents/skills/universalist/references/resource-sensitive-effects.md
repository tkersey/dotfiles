# Resource-sensitive effects

Use when a live question concerns effects on separately owned resources, what a
specification actually guarantees, or whether a guarantee survives a change of
context. Lower the useful argument to native operations; no categorical runtime,
new workflow, or enumeration of every possible context is required.

- [Computation and specifications](#separate-computation-from-its-specifications)
- [Resource preservation and information dependencies](#preserve-resources-and-check-information-dependencies)
- [Specification refinement](#a-core-refines-specifications)
- [Assertion contexts](#keep-assertions-attached-to-their-contexts)
- [Small countermodels](#small-countermodels-distinguish-stronger-claims)
- [Sources and application limits](#source-and-application-boundary)

## Separate computation from its specifications

A computation monad `T` describes effects; an assertion lifting `W` describes
specifications about them. For a posetal fibration `p: E -> B`, the paper requires
a fibered monad lifting: `p W = T p`, unit and multiplication over those of `T`,
and preservation of cartesian morphisms, which gives substitution compatibility.
The same computation semantics can have different specification liftings.

Ordinary strength `T A × B -> T(A × B)` threads a passive value. Resource framing
needs a compatible lifted strength under the assertion tensor. For assertions
`Q` over `A` and `F` over `B`, its condition is:

```text
W Q tensor F <= strength* W(Q tensor F)
```

Here `strength*` is predicate reindexing. Base strength alone does not establish
this law. See the paper's §§5.2–5.3 for the full coherence requirements.

## Preserve resources and check information dependencies

In a heap model, `P * F` describes a legal split into resources satisfying `P`
and `F`. A frame rule carries `{P} c {Q}` to `{P * F} c {Q * F}`. The legal
splits, observations, and applicable specifications determine what this means.
Do not infer information independence from a preservation specification alone.

Consider `inspect(h) = (contains_key(h,k), h)`. Every heap cell survives, and a
postcondition ignoring the Boolean result can survive extension by other cells.
Nevertheless, adding `k` changes the returned information. This example refutes
the inference from unchanged resources to result independence; it does not prove
a frame rule for every result-sensitive specification of `inspect`.

For a transaction rollback, derive the owned entries, permitted deletions, and
required outcomes on success and failure. A handle whose operations can delete
only that transaction's entries can preserve a separately owned complement.
Establish that actual aliases, captured handles, callbacks, and recovery paths
cannot bypass the claimed boundary. Merely renaming handles supplies no proof.

Use the source's observation to distinguish the claims: add another transaction's
entry and require it to survive rollback; retain the required ability to roll
back while that entry exists. If rollback's result must also ignore that entry,
vary its contents while holding the deciding inputs fixed. Shared immutable
configuration may be admissible, while a shared mutable budget or policy can be a
real dependency. Derive the allowed variation instead of assuming that different
owners make all observations independent.

Rejecting every rollback with a populated surrounding context preserves that
context vacuously but loses required-valid operations. Compare the native repair
against that counterexample and an already adequate scoped implementation.
Reuse adequate native ownership and operations rather than adding a framework.

## A core refines specifications

The paper's §6.1 assumes a higher-order bunched fibration, a fibered monad lifting `W`,
and a chosen strength for `T`. Schematically, suppressing context maps:

```text
wp_frame(c,Q) = forall F. F -* wp(c,Q * F)
```

`-*` is separating implication. Frames range over every relevant base type,
not just closed assertions or a sampled test set.
With that fibration, `T`, and strength fixed, order liftings by pointwise
entailment. Theorem 6.11 supplies the coreflection:

```text
Core(W) <= W
W strong => Core(W) = W
Core(Core(W)) = Core(W)
V strong => (V <= W iff V <= Core(W))
Inclusion |- Core
```

Equality here is equality in the entailment order, not textual identity.
The core is the greatest strong lifting below `W`: its preconditions may be
stronger, admitting fewer justified specifications. It does not change `T`.

For engineering, keep four possible changes distinct: repair execution, restrict
admission, narrow a claim, or change the resource boundary. A restriction that
drops an accepted valid case leaves that requirement unmet. A claim correction
can remove an unjustified guarantee without fixing the program. The theorem
does not select the smallest code change or prove cost, termination, or adequacy
for the source's required behavior. Use the existing
[universal witness contract](claim-appropriate-proof.md#universal-witness-contract)
for the claim actually made.

## Keep assertions attached to their contexts

For `u: A -> B`, pulling back assertion `Q` gives `u* Q` over `A`.
A specification-preserving map from `(A,P)` to `(B,Q)` needs `P <= u* Q`.
This is an obligation about the actual map and predicates, not permission to
relabel evidence. For the paper's fibered liftings, substitution satisfies
`W(u* Q) = (T u)* W(Q)` in the entailment order. The commuting square `p W = T p`
alone would not establish this compatibility.

For example, evidence about one immutable revision remains a fact about that
revision. Reuse for a changed revision needs the relevant preservation argument.
A record containing subject tags is not thereby a fibration, and durable storage
does not establish transport. Reuse
[transport across interpretations](claim-appropriate-proof.md#transport-across-interpretations).

## Small countermodels distinguish stronger claims

**Rule satisfaction versus adequacy.** The transformer `wp_bad(c,Q) = true`
satisfies the one-way Return, Bind, Frame, and Monotonicity implications, even
with `Q = false`. Those rules alone therefore cannot establish a meaningful
success guarantee. A model of partial correctness may allow divergence; choose
a terminating computation and impossible postcondition when challenging its
claimed operational adequacy. Reuse
[claim-directed correspondence](claim-appropriate-proof.md#claim-directed-correspondence).

**Mediator direction.** In an arrow category, let `J(x) = id_x` and let `cod`
return an arrow's codomain. Then `Hom(f,J(x)) = Hom(cod(f),x)`, so `cod |- J`.
The reverse is not automatic: in `0 < 1`, take `f: 0 -> 1` and `x = 1`.
A square `J(1) -> f` needs the nonexistent map `1 -> 0`, although
`Hom(1,cod(f))` contains an identity. Check the comparison direction on such a
small instance when it can decide a live universal claim.

## Source and application boundary

Li, Doenges, and Azevedo de Amorim,
[*Fibered Separation Logic: Weakest Preconditions, Universal Constructions,
and Local Independence*](https://arxiv.org/html/2611.08685v1), §§5.2–5.3 and §6.1,
supply the lifting and frame-core results. The native boundary examples and small
countermodels above are engineering applications and independent mathematical
checks. They are not a formal verification of this paper or measured skill efficacy.
