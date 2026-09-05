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

## Evidence strength

Distinguish a general derivation, exhaustive checking of a declared finite model,
and sampled property tests. A sample cannot establish universal mediation,
uniqueness, behavioral equivalence, or a resource bound. Test required-valid
counterparts as well as prohibited cases; a reject-everything implementation
must not pass the architecture discriminator.

## Skill rule

Do not accept a law merely because the operation names resemble a familiar algebra. Laws are relative to observations, effects, ordering, resources, and public contracts.
