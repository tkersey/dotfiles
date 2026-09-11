# Property-test derivation

Every Domain Algebra pass should map at least one meaningful law or non-law to an executable check.

## Property-test plan

```text
Property name:
Carrier generators:
Operation sequence:
Observation function:
Law expected:
Counterexample shape:
Shrinking / minimal witness:
Architecture implication if false:
```

## Positive laws

Positive laws should test preserved structure:

```text
observe(op(identity, x)) == observe(x)
observe(compose(compose(a,b),c)) == observe(compose(a,compose(b,c)))
```

## Non-laws

False laws should have explicit counterexamples. A non-law is often more valuable than a law because it prevents over-general architecture.

```text
refund(capture(p)) != p under audit-trace observation
```

## Test whether the laws specify the intended behavior

Conformance to equations and adequacy of those equations are different claims.
When adequacy is uncertain, construct one cheap wrong model that satisfies the
candidate equations but violates a required observation. Reject it with the
existing discriminator; this is not a universal mutation-testing quota.

Maguire's *Algebra-Driven Design*, "Tiles", exposes the distinction: structural
rotation equations do not determine which direction is clockwise, and comparing
only zero-sized rasterizations makes every tile appear equal. For a concrete
row-major observation, rotating `[[1,2],[3,4]]` clockwise must produce
`[[3,1],[4,2]]`, not the counterclockwise `[[2,4],[1,3]]` or the original tile.
Setting both rotations to identity passes four-turn and inverse equations;
exchanging clockwise and counterclockwise passes those equations too. The
asymmetric observation rejects both wrong models. Include non-square and
nontrivial inputs where dimensions or other interactions matter; one example
does not establish equality at every size.

Use the same technique for a silent interpreter, a dropped reward multiplicity,
or a state quotient that loses the next transition. Keep required-valid controls
so that reject-all is not an adequate model. A surviving wrong model calls for a
better observation or law, not automatically a production-code patch.

## Discovered equations are candidates, not authority

The book's QuickSpec technique can propose equations from an implementation:

```text
observed regularity -> candidate equation -> authority/observation adjudication
                    -> accepted regression property
```

A discovery run may capture an implementation bug or a deficient generator.
Resolve surprising or contradictory equations against accepted requirements,
independent observations, and generator coverage before retaining them. A law
supported only by current behavior stays a hypothesis, not a compatibility duty.
Fresh samples can challenge a candidate but cannot supply missing source authority.
Do not require QuickSpec, Haskell, or new discovery tooling for an adequate native
property or model test.

## Generator, observer, and shrinker adequacy

When generated tests materially support the claim, inspect their effective domain:

- Generate valid terms through the supported public algebra, covering relevant
  operations and their law-sensitive compositions. Check the observed distribution
  of constructors, depth, boundary values, and interaction cases; an operation
  present in generator source but never exercised gives no coverage. Keep generator
  coverage aligned when the public operation vocabulary changes. A sample shows
  sampled coverage, not exhaustiveness over all compositions.
- Separately exercise malformed inputs and sanctioned ingress, alias, mutation,
  or deserialization paths at their actual admission owners. Public-constructor
  tests do not replace boundary tests, and invalid internal terms do not by
  themselves falsify the public algebra's law.
- Make the comparator cover every observation relevant to the claim, including
  parameters and permitted continuations that distinguish values. Identity,
  multiplicity, ordering, failures, effects, and resources cannot disappear merely
  because the default equality function ignores them.
- Shrink toward a smaller witness while retaining the law's preconditions and
  relevant failure stage. Recheck that the result still refutes the same claim;
  an earlier fixture/setup failure is a different witness. Report timeouts,
  discarded cases, and generator bias as coverage limits. Discarding expensive
  cases cannot establish termination, latency, or resource safety.

These adapt the book's "Property-Based Testing" and "Effective QuickSpec" into
the existing property-test plan. Adequate native evidence can discharge the
questions without an additional report or testing subsystem. Finite-model tests
of these techniques are not evidence of coding-agent efficacy.

## Worked transformation: fold–map fusion

For finite lists and pure total `g` and `f`, derive:

```text
foldr f z (map g xs) = foldr (lambda x acc: f(g(x),acc)) z xs
```

The empty case is `z = z`. For `x :: xs`, expand `map` and `foldr`, apply the
inductive hypothesis to `xs`, and obtain the fused step. No associativity of `f`
is needed: the transformation preserves the existing nesting. See Gibbons,
[Unifying Theories of Programming with Monads, section 2.2](https://www.cs.ox.ac.uk/people/jeremy.gibbons/publications/utp-monads.pdf).

Lower to one native loop when that removes a material intermediate structure;
do not introduce a recursion-scheme framework just to express the proof.
Generate empty, singleton, and longer lists and use a nonassociative `f` as a
control against accidental reassociation. Check overflow and numeric semantics
in the actual host rather than substituting mathematical integers silently.

Nearest false friend: moving an effectful eager map into a right fold. With
`xs = [1,2]`, logging `g` and `f` can change `g1,g2,f2,f1` into
`g2,f2,g1,f1`. Exceptions, divergence, evaluation order, and consumption of a
single-use resource likewise require additional laws. A value-only equality
must not authorize the effectful rewrite.

For an operation-language transformation `T` and interpreters, the analogous
obligation is `Obs(H_new(T(p))) = Obs(H_old(p))` under explicit hypotheses.
Use structural induction or the appropriate homomorphism argument when possible;
retain one minimal counterexample that breaks an omitted hypothesis. Performance
is a separate claim: show the eliminated allocation/traversal in the lowering
and measure the relevant runtime cost. Semantic equality alone proves no speedup.

## Representation laws: native data and its fold

Use only when representation or producer/consumer fusion is the live alternative.
In the finite, pure, total, parametric setting described in
`../syntax-semantics-pivot.md`, let `D` be the native datatype with constructor
algebra `in`, and define:

```text
encode(d)(alpha) = fold(alpha,d)
decode(c)        = c(in)

decode(encode(d)) ~= d
encode(decode(c)) ~= c
```

The first law follows by structural induction on native values. The second
requires uniformity of admitted encoded values: it is not established by hiding
a constructor or observing one interpreter. Declare `~=` over the required
observations and permitted future operations. State excluded partial, effectful,
infinite, identity-sensitive, or resource-sensitive cases instead of importing a
pure theorem into them. Test every sanctioned construction route, not only the
helper constructors that generated friendly examples.

For an algebra morphism `h` with `h . alpha = beta . F(h)`, require:

```text
h(c(alpha)) = c(beta)
```

This is a reusable preservation argument under the model's hypotheses, not a
claim that every function `h` is an algebra morphism. For lists, a concrete
witness is `h = length`, `alpha = (Cons,Nil)`, and
`beta = (lambda x n: 1+n,0)`. For the expression example, test numeric and
rendering algebras and constructor reconstruction. Keep computation rules,
representation equivalence, universal uniqueness, and dependent induction as
separate claims. The same finite tests cannot establish all four.

## Worked transformation: fold/build fusion

For an admitted pure parametric producer of finite lists:

```text
Producer<A> = forall R. (A -> R -> R) -> R -> R
build(g)    = g(Cons,Nil)
foldr(k,z,build(g)) = g(k,z)
```

Derive the equality from the producer's uniformity using `foldr(k,z)` as the
algebra morphism from `(Cons,Nil)` to `(k,z)`. This eliminates the *intermediate*
list, not necessarily the final result or every allocation. Preserve right-fold
nesting; a left-fold rewrite additionally needs its own law. No associativity of
`k` is assumed. A native loop may be the best lowering; a callback framework is
not part of the proof. GHC's
[foldr/build documentation](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/rewrite_rules.html)
describes compiler-specific fusion conditions; do not assume a different host
implements them or that every polymorphic producer satisfies the required law.

### Falsifier: an ignored algebra call becomes an effect

In an eager host, consider the following deliberately unrestricted callback:

```text
g(k,z):
    k(99,z)                 # discard this result
    return k(1,z)
```

With pure list constructors, `build(g)` is `[1]`; the discarded node is not in
the result. With a logging sum algebra, folding that list returns `1` with trace
`[1]`, while direct `g(k,0)` returns `1` with trace `[99,1]`. An algebra that
throws at `99` also makes only the direct path fail. Even a term harmless under
pure interpretations can fail the transferred law under effectful ones. Do not
label value parity a successful fusion. Reject the rewrite or prove the actual
effect-aware law; keep the valid pure constructor-generated producer as a control.

A second falsifier is a builder closing over a mutable list: materialize while
it is `[1]`, mutate it to `[1,2]`, then compare the stored value with delayed
interpretation. They differ. Snapshot ownership or a genuinely replayable
producer is required when the contract promises a stable value. One-shot
iterators, cancellation, and resource lifetimes need their actual protocol, not
an invented parametricity argument. Reification must not rerun unapproved effects.

Use empty/singleton/deeper cases, nonassociative algebras, constructor
reconstruction, and multiple observations as controls. Check invalid domain
inputs and required-valid counterparts at their existing owners; the encoding
does not add validation. Count eliminated nodes only in a declared cost model,
and benchmark the full host workload separately from the semantic law.

## Evidence strength

Distinguish a general derivation, exhaustive checking of a declared finite model,
and sampled property tests. A sample cannot establish universal mediation,
uniqueness, behavioral equivalence, or a resource bound. Test required-valid
counterparts as well as prohibited cases; a reject-everything implementation
must not pass the architecture discriminator.

## Skill rule

Do not accept a law merely because the operation names resemble a familiar algebra. Laws are relative to observations, effects, ordering, resources, and public contracts.
