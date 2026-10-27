# Domain Algebra Discovery

Use to formulate and derive task-relevant operations, equations, carriers,
observations, algorithms, and proofs, including before a boundary problem or
candidate abstraction is named. A grounded required use is enough to begin.
Let mathematical knowledge suggest hypotheses and concrete evidence discriminate
them. Reuse the existing inquiry and adequate derivations; this is not another
stage, report, trigger identifier, or prerequisite for mechanical realization.

The techniques below adapt Sandy Maguire's *Algebra-Driven Design*, especially
"What Makes a Good Algebra?", "Tiles", "Scavenger Hunt", and "Deriving
Implementations". The authority, effect, migration, and proof qualifications are
Universalist's engineering application, not additional claims made by the book.

## Grow the algebra from required uses

```text
required uses -> useful operations -> interacting equations and observations
             -> revised vocabulary or carrier -> native realization
```

Start with the human-facing purpose and representative required uses, including
an awkward composition or boundary case when one is relevant. Do not begin by
assuming the incumbent container or a preferred categorical construction. For a
first-use boundary, use attributed requirements rather than invented historical
implementations. Examples expose missing behavior; they do not define the whole
admitted domain.

Propose the smallest useful constructors, combinators, and eliminators. Relate
each proposed operation to existing operations and required observations. An
identity, distributive law, or factoring may reveal missing functionality or
remove a special case. Awkward interactions can instead expose a conflated
operation, accidental constraint, or false law. Investigate the interactions
that decide this seam, not an exhaustive operation-pair matrix.

Keep the vocabulary compositional, task-relevant, parsimonious, and orthogonal.
Investigate task-grounded generalizations; retain them only where the equations
and a material dividend support their actual realization. A
convenient derived operation can stay when its relation to the smaller basis is
clear and it reduces caller knowledge; parsimony does not require forcing callers
to reconstruct every useful operation. Compare complete caller contracts and
source-supported changes under the existing law-preserving dominance rule.

Attribute equations to accepted requirements, justified derivations, or candidate
regularities. Names, existing code, and generated laws do not grant requirement
authority. Resolve a contradiction against that authority: either the proposed
law, the observation, or the representation may be wrong. Do not weaken an
accepted obligation merely to obtain a familiar algebra.

## Discharge derived obligations under their actual hypotheses

A required law may follow from a smaller law family instead of needing an
independent proof. When using that implication to remove repeated obligations,
keep the derivation and the hypotheses actually used with the existing proof
and invalidators. Generalizing a carrier, operation, or admissible map can break
the implication while the derived law remains required. Reprove the affected
implication or supply independent justification; reuse unaffected derivations.
Seek weaker sufficient hypotheses when they simplify the artifact without
weakening its contract.

For a multiplication-preserving map `f` from a monoid `A` to a monoid `B`:

```text
u = f(e_A)
u = f(e_A * e_A) = u * u
```

This proves that `u` is idempotent. If `u` is invertible, cancel it to obtain
`u = e_B`; a group target suffices but is stronger than that proof needs.
Another sufficient hypothesis is that `e_B` is the target's only idempotent.
For an arbitrary monoid target, multiplication preservation alone does not
establish identity preservation. Take Boolean conjunction, with identity `true`,
and `f(x) = false` for every source value:

```text
f(x * y) = false = false AND false = f(x) AND f(y)
f(e_A) = false != true
```

Thus a translation from reversible pipelines to a broader family admitting
projections cannot retain unit preservation merely because binary composition
still agrees. Mapping every pipeline to a fixed nonidentity idempotent normalizer
preserves binary composition while changing the empty pipeline's behavior.
Keep the required unit law and establish it under the new assumptions.

Likewise, comparability for every pair in a total order implies reflexivity by
taking both endpoints equal. Removing comparability removes that derivation;
reflexivity still needs justification. These are applications of Cheng,
[*The Joy of Abstraction*](https://doi.org/10.1017/9781108769389), sections 10.1–10.2
(printed pp. 118, 121–122) and 13.2 (pp. 150–152); the pipeline example is an
engineering application of the nonidentity-idempotent counterexample.

When a coherence theorem reduces a family of equations to generating laws,
retain its hypotheses and exact generated family. Samples satisfying the
generators do not themselves prove that entire family. Cheng's section 24.7
(printed pp. 383–384) explains the distinction between local axioms and their
global consequences. Judge removal of implementation checks separately: a
mathematically derived property may still supply distinct implementation
evidence.

## Let contradictions select the carrier

In the book's scavenger hunt, `both(a,b)` should combine rewards commutatively.
Returning a list exposes order that the intended reward observation does not
need. Replacing the list with a set removes order but also erases multiplicity:
two distinct awards of one point must still count twice.

For this observation, derive a bag (multiset) with additive counts:

```text
count(r, combine(a,b)) = count(r,a) + count(r,b)
combine(a,b) ~= combine(b,a)
combine(a,empty) ~= a
combine(combine(a,b),c) ~= combine(a,combine(b,c))
combine(singleton(r),singleton(r)) !~= singleton(r)
```

Here `~=` compares every reward count. Associativity, identity, and commutativity
follow pointwise from count addition; idempotence is a non-law. A native count map
or an equivalent representation can realize this without a public algebra
framework. A list behind an adequate observation boundary is not automatically
wrong; choose by the actual preserved observations and consumer obligations.

Ask both questions: **which distinctions does the representation introduce that
the domain does not require, and which would the simplification erase that the
domain does require?** Preserve the answer through public construction, permitted
operations, and future observations, not only current examples. An ordered audit
trace cannot be quotiented to a bag. Bounds, overflow, identity, provenance, and
failure behavior retain their actual contracts. Commutative reward accounting
neither permits reordering external effects nor proves effect-safe retries.

## Derive a unifying observation

When observations independently traverse or simulate the same structure, ask
whether a smaller observation with sufficient residual state can derive them.
The book replaces separately maintained reward and completion traversals with:

```text
step : Maybe Input -> Challenge -> (Multiset Reward, Challenge)
```

The result contains emitted rewards and the residual challenge. `Nothing` allows
immediate progress without another external event: after a gate consumes its
matching input, its reward can be emitted now, but the same input must not also
satisfy a second sequential gate. Derive reward accumulation and completion from
this semantics rather than coordinating two implementations of event dispatch.

For a pure, deterministic transition core, a native
`transition(state,event) -> (outputs,nextState)` is an analogous candidate, not
a mandated architecture. Show how each required observation is recovered and
how related residual states remain related under permitted continuations.
Today's equal status is insufficient when the next event distinguishes states.
Effectful, nondeterministic, partial, or resource-sensitive behavior needs its
actual observation and simulation argument; do not silently replace it with the
pure model. Output descriptions are not permission to execute effects.

Unify production meaning, not independent verification. Preserve an independent
oracle when it supplies distinct proof; do not consolidate it onto the very
transition being checked. Keep an adequate existing owner instead of adding a
second transition abstraction.

## Use a simple model to free the implementation

When useful for a consequential replacement, a compact initial encoding can
represent the algebra's operations as data and interpret them through the
accepted observations. It can be a reference model, not the required production
representation. Establish its connection to the accepted semantics before using
it to judge a successor; an incumbent implementation is not automatically an
oracle.

For a translation `T` between representations, the comparison is:

```text
Obs(optimized(T(program), inputs)) = Obs(reference(program, inputs))
```

Include required traces, failures, and residual behavior in `Obs`. A
structure-preserving or simulation argument may discharge more than samples;
keep its hypotheses and evidence strength explicit. The model is optional:
retain a sufficient initial implementation, direct proof, or existing oracle.
Do not require a second implementation, an IR, or an interpreter framework.
Performance claims need the actual host workload, not semantic agreement alone.

For law-adequacy countermodels, generator/observer coverage, and discovered-law
admission, use [property-test derivation](property-test-derivation.md) only when
that proof is live. Reuse the existing discriminator and required-valid control.

## Derive a compositional summary, not a framework

Consider an ordered integer trace of resource acquisitions and releases. Required
observations are final usage and whether any prefix violates the bounds `0..C`,
given initial usage `u`. Chunks must be summarized and recombined without rescanning
their elements. This is an engineering derivation, not an example from the book.

A chunk's net change alone loses intermediate violations. Derive the information
needed by concatenation: `S = (delta, low, high)`, where `low` and `high` are the
minimum and maximum prefix sums, including the empty prefix. Every prefix of
`a ++ b` is in `a`, or in `b` after adding `a.delta`; therefore derive:

```text
combine(a,b) = (
  a.delta + b.delta,
  min(a.low,  a.delta + b.low),
  max(a.high, a.delta + b.high)
)
empty = (0,0,0)
summarize(a ++ b) = combine(summarize(a), summarize(b))
valid(u,C,s) = (u + s.low >= 0) and (u + s.high <= C)
```

The carrier is summaries of finite traces, not arbitrary unchecked triples.
Concatenation supplies closure, identity, and associativity on that carrier;
the prefix decomposition proves the homomorphism. Native constructors should
produce valid summaries or validate imported summaries before trusting them.
For `[+3,-2]` and `[+4,-1]`, the summaries are `(1,0,3)` and `(3,0,4)`;
their combination is `(4,0,5)`. At `u=0, C=4`, the final usage is acceptable
but the trace is not. Prefix minima likewise preserve underflow detection.

Three fields and one native operation may suffice. Ordered chunk summaries can
be recombined or maintained incrementally; associativity does not license
permuting chunks. Use exact arithmetic or account for the host's overflow behavior.
The summary proves the supplied trace's accounting property, not that concurrent
external effects follow that trace. Keep per-event identity, audit, and failure
observations separately when required. Compare workload and storage costs before
claiming a speedup; a direct loop can remain better for a single scan.

The mathematical structure derives what must be retained and how to compose it.
No generic algebra interface, new public boundary, or construction card is required.

## Return to the existing decision

Algebra discovery supplies carriers, operations, observations, laws, non-laws,
interpreters, and falsifiers to the current nomination. It does not select a
route by itself. Keep `UNI-ORDINARY` available for a count map, local fold, or
transition function; preserve an adequate incumbent that resolves the question.
Use `UNI-CONSEQUENTIAL` before accepting materially different live candidates.
Focused theory may help discover the formulation; actual card prerequisites and
claim-appropriate evidence govern retention, not permission to inquire. Unlisted
constructions need the same proof, not registry expansion. Unknown evidence is
not `UNI-OBSTRUCT`.

A lawful structure requires its laws and interpretation. A claimed universal
construction additionally requires the relevant diagram, admissible maps and
competitors, factorization, and uniqueness argument. One interpreter, opacity,
or finite tests do not establish those claims. Inside Actuating, return only the
decision-changing derivation: Universalist nominates; Actuating selects.

The tile algebra's closure does not promise infallible external operations.
Admitted compositions need defined semantics, including required failures,
authority checks, partial effects, progress, and resource limits. None may be
removed merely to make the equations simpler.
